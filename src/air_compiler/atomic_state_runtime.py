"""One private candidate and one existing store replacement; ordinary typed rows."""
ATOMIC_STATE = {}  # inserted by normal compiler
_atomic_context = ContextVar("lykoi_atomic_state", default=None)
_atomic_value_of = value_of
_atomic_commit = reference_commit
_atomic_execute = execute
_atomic_mutation = execute_mutation
_atomic_related = reference_operation
_atomic_entities = reference_entities
_atomic_migrate = migrate


def reference_entities(payload):
    if type(payload) is dict and "entities" in payload and type(payload["entities"]) is dict:
        payload = copy.deepcopy(payload)
        for e in REFERENCE["facts"]["entities"]:
            if e["name"] in ATOMIC_STATE["facts"]["append_only"] and e["initial"] == []:
                payload["entities"].setdefault(e["name"], [])
    return _atomic_entities(payload)


def migrate():
    payload = reference_payload()
    missing = type(payload) is dict and "entities" in payload and any(e not in payload["entities"] for e in ATOMIC_STATE["facts"]["append_only"])
    result = _atomic_migrate()
    if missing and result["migrated"] == 0:
        rows = reference_rows()
        _atomic_commit(rows, rows, migration=True)
        return {"migrated": len(rows[REFERENCE["facts"]["primary"]])}
    return result


def value_of(assignment, inputs):
    context = _atomic_context.get()
    if context is None or assignment["source"] != "capability":
        return _atomic_value_of(assignment, inputs)
    cid = assignment["id"]
    if cid not in context["sampled"]:
        provider = context["providers"].get(cid)
        context["sampled"][cid] = provider() if provider else _atomic_value_of(assignment, inputs)
    return context["sampled"][cid]


def atomic_call(command, inputs, call, providers=None):
    op = next((o for o in ATOMIC_STATE["facts"]["operations"] if o["command"] == command), None)
    if op is None or _atomic_context.get() is not None:
        return call()
    providers = {} if providers is None else providers
    allowed = {r["capability"] for r in op["resources"]}
    if type(providers) is not dict or not set(providers) <= allowed or not all(callable(p) for p in providers.values()):
        raise ValueError("Providers bind declared atomic operation capabilities only")
    token = _atomic_context.set(dict(op=op, inputs=inputs, providers=providers, sampled={}, commits=0))
    try:
        return call()
    finally:
        _atomic_context.reset(token)


def reference_commit(before, after, *, migration=False):
    context = _atomic_context.get()
    if context is None or migration:
        return _atomic_commit(before, after, migration=migration)
    if context["commits"]:
        raise Failure("invalid_state")
    context["commits"] += 1
    op = context["op"]
    entity = op["entity"]
    key = REFERENCE["identities"][entity]
    old = {r[key]: r for r in before[entity]}
    new = {r[key]: r for r in after[entity]}
    touched = {i for e, i in _reference_touched if e == entity and i is not None}
    changed = {i for i in set(old) | set(new) if old.get(i) != new.get(i)} | touched
    if len(changed) != 1:
        raise Failure("invalid_state")
    rid = next(iter(changed))
    images = dict(before=old.get(rid), after=new.get(rid))
    resources = {}
    for r in op["resources"]:
        v = value_of(dict(source="capability", id=r["capability"]), {})
        if not mutable_value_valid(v, r["type"]):
            raise Failure("invalid_state")
        if by_id("capabilities", r["capability"])["kind"] == "uuid_v4":
            try:
                if UUID(v).version != 4: raise ValueError()
            except (ValueError, AttributeError): raise Failure("invalid_state")
        resources[r["name"]] = v
    candidate = copy.deepcopy(after)
    computed = computation_evaluate(op["computations"], before, images, context["inputs"], resources) if "computations" in op else {}
    for creation in op["creations"]:
        e = creation["entity"]
        row = {}
        for n, b in creation["bindings"].items():
            s = b["source"]
            v = s["value"] if s["kind"] == "literal" else (computed if s["kind"] == "computed" else context["inputs"] if s["kind"] == "parameter" else resources if s["kind"] == "resource" else images[s["kind"]])[s["name"]]
            if not mutable_value_valid(v, REFERENCE["types"][e][n]):
                raise Failure(b["invalid_error"])
            row[n] = copy.deepcopy(v)
        k = REFERENCE["identities"][e]
        if not row[k].strip():
            raise Failure(creation["bindings"][k]["invalid_error"])
        if any(r[k] == row[k] for r in candidate[e]):
            raise Failure(creation["duplicate_error"])
        candidate[e].append(row)
    return _atomic_commit(before, candidate)


def execute(behavior, inputs, clock=None, *, providers=None):
    command = next(c["token"] for c in SPEC["commands"] if c.get("behavior") == behavior["id"])
    named = {i["name"]: inputs[i["id"]] for i in behavior["inputs"] if i["id"] in inputs}
    op = next((o for o in ATOMIC_STATE["facts"]["operations"] if o["command"] == command), None)
    if op is None:
        return _atomic_execute(behavior, inputs, clock, providers=providers)
    # Atomic context owns provider sampling; existing creation adapter receives no
    # undeclared secondary capabilities.
    return atomic_call(command, named, lambda: _atomic_execute(behavior, inputs, clock), providers)


def execute_mutation(mutation, inputs, *, providers=None):
    return atomic_call(mutation["command"], inputs, lambda: _atomic_mutation(mutation, inputs), providers)


def reference_operation(op, inputs, *, providers=None):
    return atomic_call(op["command"], inputs, lambda: _atomic_related(op, inputs), providers)


def atomic_state_main(base_main):
    q = next((q for q in ATOMIC_STATE["facts"]["queries"] if sys.argv[1:2] == [q["id"]]), None)
    if q is None:
        return base_main()
    parser = argparse.ArgumentParser(prog=q["id"])
    for n in q["parameters"]: parser.add_argument("--" + n, dest=n, default=argparse.SUPPRESS)
    inputs = vars(parser.parse_args(sys.argv[2:]))
    try:
        for n, t in q["parameters"].items():
            if n in inputs and t["type"] in ("boolean", "collection", "integer", "duration"):
                try: inputs[n] = json.loads(inputs[n])
                except ValueError: raise ApplicationError("invalid_input")
        result = execute_query(q, reference_rows()[q["source"]["collection"]], inputs)
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0
    except ApplicationError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
