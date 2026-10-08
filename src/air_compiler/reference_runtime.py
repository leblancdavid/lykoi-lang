"""Bounded single-store reference backend, inserted only in the normal profile.

All cooperative CLI operations hold one exclusive store-operation reservation.
Atomic replacement commits one record's change and the observed integrity checks.
No cross-file transaction or crash-recovery/serializability claim is made.
"""
REFERENCE = {}  # inserted by normal compiler
_reference_read = read_state
_reference_decode = decode_state
_reference_execute = execute
_reference_mutation = execute_mutation
_reference_touched = set()


class ReferenceInputs(dict):
    def __init__(self, values, supplied=None):
        super().__init__(values)
        self.supplied = set(values) if supplied is None else set(supplied)


def reference_defaults(op, inputs):
    inputs = ReferenceInputs(copy.deepcopy(inputs), getattr(inputs, "supplied", set(inputs)))
    for n, p in op["parameters"].items():
        if n not in inputs and "default" in p: inputs[n] = copy.deepcopy(p["default"])
    return inputs


def reference_entities(payload):
    declared = {e["name"]: e for e in REFERENCE["facts"]["entities"]}
    entities = copy.deepcopy(payload.get("entities", {n: e["initial"] for n, e in declared.items()})) if type(payload) is dict else {n: copy.deepcopy(e["initial"]) for n, e in declared.items()}
    if set(entities) != set(declared):
        raise Failure("invalid_state")
    for n, rows in entities.items():
        fields = REFERENCE["types"][n]
        key = REFERENCE["identities"][n]
        if type(rows) is not list or any(type(r) is not dict or set(r) != set(fields) or any(not mutable_value_valid(r[f], t) for f, t in fields.items()) for r in rows):
            raise Failure("invalid_state")
        ids = [r[key] for r in rows]
        if any(type(i) is not str or not i.strip() for i in ids) or len(set(ids)) != len(ids):
            raise Failure("invalid_state")
        # Initial rows are explicit persistent semantic constants, not ambient users.
        if any(r not in rows for r in declared[n]["initial"]):
            raise Failure("invalid_state")
    return entities


def decode_state(payload, state):
    reference_entities(payload)
    if type(payload) is dict and "entities" in payload:
        payload = {k: v for k, v in payload.items() if k != "entities"}
    return _reference_decode(payload, state)


def reference_payload():
    state = SPEC["state"][0]
    rt, path = state_layout(state)
    try:
        payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (ValueError, UnicodeError):
        raise Failure("invalid_state")
    return payload


def reference_rows():
    state = SPEC["state"][0]
    rt, path = state_layout(state)
    return {REFERENCE["facts"]["primary"]: read_state(state, rt, path), **reference_entities(reference_payload())}


def reference_fields(bindings):
    return {a + "." + n: v for a, row in bindings.items() for n, v in row.items()}


def reference_condition(tree, rows, bindings, inputs):
    k = tree["kind"]
    if k in ("and", "or", "not"):
        values = [reference_condition(c, rows, bindings, inputs) for c in ([tree["child"]] if k == "not" else tree["children"])]
        return not values[0] if k == "not" else all(values) if k == "and" else any(values)
    if k == "extent":
        s = tree["selection"]
        count = sum(predicate_eval(s["predicate"], reference_fields({**bindings, s["binding"]: r}), inputs) for r in rows[s["entity"]])
        return count == tree["value"] if tree["relation"] == "eq" else count >= tree["value"]
    if k == "reachable":
        fields = reference_fields(bindings)
        source = predicate_value(tree["source"], fields, inputs, {}, {})
        target = predicate_value(tree["target"], fields, inputs, {}, {})
        key = REFERENCE["identities"][tree["entity"]]
        domain = {r[key]: r for r in rows[tree["entity"]]}
        # Nonempty path semantics: source==target alone is not reachability.
        visited, pending = set(), [source]
        while pending:
            node = pending.pop()
            if node in visited or node not in domain:
                continue
            visited.add(node)
            edges = domain[node][tree["field"]]
            edges = edges if type(edges) is list else [edges]
            if any(x == target and x in domain for x in edges):
                return True
            pending.extend(x for x in edges if x in domain and x not in visited)
        return False
    return predicate_eval(tree, reference_fields(bindings), inputs)


def reference_integrity(before, after, *, migration=False, touched=None):
    touched = _reference_touched if touched is None else touched
    for check in REFERENCE["checks"]:
        r = check["reference"]
        source, target = r["entity"], r["target"]
        sk, tk = REFERENCE["identities"][source], REFERENCE["identities"][target]
        old = {x[sk]: x for x in before[source]}
        target_ids = {x[tk] for x in after[target]}
        removed = {x[tk] for x in before[target]} - target_ids
        # Restrict is reverse selection + cardinality zero over candidate state.
        if r["deletion"]["policy"] == "restrict":
            for deleted in removed:
                if not reference_condition(check["reverse"]["predicate"], after, {}, {"deleted_identity": deleted}):
                    raise Failure(r["deletion"]["error"])
        # Required existence checks new/replaced values, or every migration row.
        # Explicit permit can leave old references dangling after authorized delete.
        if r["existence"]["policy"] == "required":
            for row in after[source]:
                if not migration and row[sk] in old and row == old[row[sk]] and (source, row[sk]) not in touched:
                    continue
                ids = row[r["field"]] if type(row[r["field"]]) is list else [row[r["field"]]]
                if any(not reference_condition(check["existence"]["predicate"], after, {}, {"candidate_identity": i}) for i in ids):
                    raise Failure(r["existence"]["error"])


def reference_commit(before, after, *, migration=False):
    state = SPEC["state"][0]
    rt, path = state_layout(state)
    primary = REFERENCE["facts"]["primary"]
    if not valid_state(after[primary], state, rt):
        raise Failure("invalid_state")
    entities = {n: rows for n, rows in after.items() if n != primary}
    reference_entities({"entities": entities})
    reference_integrity(before, after, migration=migration)
    payload = dict(schema_version=state["schema_version"], records=after[primary], entities=entities)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False) as f:
            temporary = Path(f.name)
            json.dump(payload, f, sort_keys=True, ensure_ascii=False)
            f.write("\n")
        os.replace(temporary, path)
    except OSError:
        raise Failure("persistence_failure")
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def write_state(records, state, record_type, path):
    before = reference_rows()
    after = copy.deepcopy(before)
    after[REFERENCE["facts"]["primary"]] = records
    reference_commit(before, after)


def reference_existing_guards(command, named):
    guards = [g for g in REFERENCE["facts"]["guards"] if g["command"] == command]
    if not guards:
        return
    rows = reference_rows()
    primary = REFERENCE["facts"]["primary"]
    key = REFERENCE["identities"][primary]
    row = next((r for r in rows[primary] if r[key] == named.get(key)), None)
    if row is None:
        return  # Existing declared lookup error has precedence.
    for g in guards:
        if not reference_condition(g["predicate"], rows, {"primary": row}, named):
            raise Failure(g["error"])


def execute(behavior, inputs, clock=None, *, providers=None):
    global _reference_touched
    command = next(c["token"] for c in SPEC["commands"] if c.get("behavior") == behavior["id"])
    named = {i["name"]: inputs[i["id"]] for i in behavior["inputs"] if i["id"] in inputs}
    reference_existing_guards(command, named)
    primary = REFERENCE["facts"]["primary"]
    _reference_touched = {(primary, named.get(REFERENCE["identities"][primary]))}
    try:
        return _reference_execute(behavior, inputs, clock, providers=providers)
    finally:
        _reference_touched = set()


def execute_mutation(mutation, inputs):
    global _reference_touched
    reference_existing_guards(mutation["command"], inputs)
    _reference_touched = {(REFERENCE["facts"]["primary"], inputs.get(mutation["lookup"]))}
    try:
        return _reference_mutation(mutation, inputs)
    finally:
        _reference_touched = set()


def migrate():
    if "historical" in REFERENCE:
        return historical_migrate()
    state = SPEC["state"][0]
    rt, path = state_layout(state)
    payload = reference_payload()
    if not payload:
        return {"migrated": 0}
    version = 1 if type(payload) is list else payload.get("schema_version")
    records = copy.deepcopy(payload if type(payload) is list else payload.get("records"))
    if type(records) is not list:
        raise Failure("invalid_state")
    entities = reference_entities(payload)
    original = copy.deepcopy(records)
    for m in sorted(SPEC["migrations"], key=lambda x: x["from_version"]):
        if m["from_version"] != version:
            continue
        remaining = {field_name(rt, a["field"]) for step in SPEC["migrations"] if step["from_version"] >= version for a in step["add_fields"]}
        names = {f["name"] for f in rt["fields"]} - remaining
        if any(type(r) is not dict or set(r) != names for r in records):
            raise Failure("invalid_state")
        added = {field_name(rt, a["field"]): copy.deepcopy(a["value"]) for a in m["add_fields"]}
        records = [{**r, **copy.deepcopy(added)} for r in records]
        version = m["to_version"]
    if version != state["schema_version"]:
        raise Failure("invalid_state")
    primary = REFERENCE["facts"]["primary"]
    after = {primary: records, **entities}
    for r in REFERENCE["facts"]["references"]:
        if r["migration"]:
            for row in after[r["entity"]]:
                if r["field"] not in row or row[r["field"]] in ("", []):
                    row[r["field"]] = copy.deepcopy(r["migration"]["value"])
    # Before image with current field projections; migration is explicit authority.
    before = copy.deepcopy(after)
    reference_integrity(before, after, migration=True)
    changed = original != records or type(payload) is not dict or "entities" not in payload
    if changed:
        reference_commit(before, after, migration=True)
    return {"migrated": len(records) if changed else 0}


def reference_inputs(op, inputs):
    inputs = reference_defaults(op, inputs)
    for n, p in op["parameters"].items():
        if n not in inputs:
            if "default" not in p: raise Failure(p["missing_error"])
            inputs[n] = copy.deepcopy(p["default"])
        if p["encoding"] == "utc_day":
            try:
                day = inputs[n]
                if type(day) is not str or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", day):
                    raise ValueError()
                datetime.strptime(day, "%Y-%m-%d")
                inputs[n] = day + "T00:00:00Z"
            except (ValueError, TypeError):
                raise Failure(p["invalid_error"])
        if not mutable_value_valid(inputs[n], p["type"]):
            raise Failure(p["invalid_error"])
    return inputs


def reference_operation(op, inputs):
    global _reference_touched
    inputs = reference_inputs(op, inputs)
    before = reference_rows()
    rows = before[op["entity"]]
    key = REFERENCE["identities"][op["entity"]]
    target = next((r for r in rows if r[key] == inputs.get(op["lookup"])), None) if op["lookup"] else None
    if op["kind"] in ("update", "delete") and target is None:
        raise Failure(op["missing_error"])
    computed = computation_evaluate(op["computations"], before, {"before": target}, inputs) if "computations" in op else {}
    for g in op["guards"]:
        if not reference_condition(g["predicate"], before, {"primary": target} if target else {}, ReferenceInputs({**inputs, **computed}, inputs.supplied | set(computed))):
            raise Failure(g["error"])
    if op["kind"] == "list":
        return sorted(copy.deepcopy(rows), key=lambda r: tuple(r[n] for n in op["order"]))
    candidate = copy.deepcopy(target) if target else {}
    for w in op["changes"]:
        if "when" in w and not reference_condition(w["when"], before, {"primary": target}, inputs): continue
        s = w["source"]
        value = copy.deepcopy(computed[s["name"]] if s["kind"] == "computed" else inputs[s["name"]] if s["kind"] == "parameter" else s["value"])
        n = w["field"]
        if w["operation"] == "replace": candidate[n] = value
        elif w["operation"] == "remove": candidate[n] = [x for x in candidate[n] if x != value]
        elif w["operation"] == "append" or value not in candidate[n]: candidate[n].append(value)
        if not mutable_value_valid(candidate[n], REFERENCE["types"][op["entity"]][n]):
            raise Failure(w["invalid_error"])
    if op["kind"] == "create":
        if not candidate[key].strip():
            raise Failure(next(w["invalid_error"] for w in op["changes"] if w["field"] == key))
        if any(r[key] == candidate[key] for r in rows):
            raise Failure(op["duplicate_error"])
    after = copy.deepcopy(before)
    if op["kind"] == "create": after[op["entity"]].append(candidate)
    elif op["kind"] == "delete": after[op["entity"]] = [r for r in after[op["entity"]] if r[key] != target[key]]
    else: after[op["entity"]] = [candidate if r[key] == target[key] else r for r in after[op["entity"]]]
    _reference_touched = {(op["entity"], candidate.get(key))} if op["kind"] != "delete" else set()
    try:
        reference_commit(before, after)
    finally:
        _reference_touched = set()
    return copy.deepcopy(target if op["kind"] == "delete" else candidate)


def reference_main(base_main):
    state = SPEC["state"][0]
    rt, path = state_layout(state)
    lock = Path(str(path) + ".operation-lock")
    reserved = False
    try:
        try:
            fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            os.close(fd)
            reserved = True
        except FileExistsError:
            raise Failure("store_busy")
        if sys.argv[1:] == ["migrate"]:
            print(json.dumps(migrate(), sort_keys=True))
            return 0
        op = next((o for o in REFERENCE["facts"]["operations"] if sys.argv[1:2] == [o["command"]]), None)
        if op is None:
            return base_main()
        parser = argparse.ArgumentParser(prog=op["command"])
        for n, p in op["parameters"].items(): parser.add_argument(p["flag"], dest=n, default=argparse.SUPPRESS)
        inputs = ReferenceInputs(vars(parser.parse_args(sys.argv[2:])))
        for n, p in op["parameters"].items():
            if n not in inputs:
                if "default" not in p: raise Failure(p["missing_error"])
                inputs[n] = copy.deepcopy(p["default"])
                continue
            if p["encoding"] == "json":
                try: inputs[n] = json.loads(inputs[n])
                except ValueError: raise Failure(p["invalid_error"])
            if p["encoding"] != "utc_day" and not mutable_value_valid(inputs[n], p["type"]): raise Failure(p["invalid_error"])
        result = reference_operation(op, inputs)
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0
    except Failure as exc:
        print(json.dumps({"error": exc.code}), file=sys.stderr)
        return 1
    except OSError:
        print(json.dumps({"error": "persistence_failure"}), file=sys.stderr)
        return 1
    finally:
        if reserved: lock.unlink()
