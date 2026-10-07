"""Self-contained backend for the validated typed mutable-value algebra."""
import copy

MUTABLE = {}  # inserted by normal compiler
_scalar_valid_state = valid_state
_scalar_execute = execute
_scalar_value_of = value_of


class MissingExternalInput(ValueError):
    """CLI-only rejection has no fabricated application error identity."""


def value_of(assignment, inputs):
    return copy.deepcopy(_scalar_value_of(assignment, inputs))


def mutable_value_valid(value, typ):
    if typ["type"] == "collection":
        return (type(value) is list and all(mutable_value_valid(x, typ["element"]) for x in value)
                and (typ["duplicates"] == "allow" or mutable_unique(value) == value))
    if value is None:
        return typ.get("nullable", False)
    if typ["type"] == "boolean":
        return type(value) is bool
    if typ["type"] in ("integer", "duration"):
        return type(value) is int and -(2 ** 63) <= value < 2 ** 63
    if type(value) is not str:
        return False
    if typ["type"] == "enum":
        return value in typ["domain"]
    return utc_timestamp(value) if typ["type"] == "timestamp" else typ["type"] in ("string", "identifier")


def mutable_unique(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def valid_state(records, state, record_type):
    if type(records) is not list:
        return False
    names = {f["name"] for f in record_type["fields"]}
    if any(type(r) is not dict or set(r) != names or any(not mutable_value_valid(r[n], t) for n, t in MUTABLE["value_types"].items()) for r in records):
        return False
    collection_names = {c["name"] for c in MUTABLE["facts"]["collections"]} | {b["name"] for b in MUTABLE["facts"].get("predicate_semantics", {}).get("booleans", [])} | {n["name"] for n in MUTABLE["facts"].get("primary_interfaces", {}).get("integers", [])}
    scalar_type = {**record_type, "fields": [f for f in record_type["fields"] if f["name"] not in collection_names]}
    if not _scalar_valid_state([{k: v for k, v in r.items() if k not in collection_names} for r in records], state, scalar_type):
        return False
    return all(predicate_eval(inv["predicate"], record=r) for inv in MUTABLE["facts"].get("predicate_semantics", {}).get("invariants", []) for r in records)


def mutable_pipeline(value, steps, typ, error):
    raw = copy.deepcopy(value)
    value = copy.deepcopy(value)
    # Raw shape must be safe for transformations. Uniqueness is validated at the
    # final/stated typed stage, so explicitly authorized dedup can repair it.
    shape_ok = (type(value) is list and all(type(x) is str for x in value)) if typ["type"] == "collection" else mutable_value_valid(value, typ) if typ["type"] in ("boolean", "integer", "duration") else (type(value) is str or (value is None and typ.get("nullable", False)))
    if not shape_ok:
        raise Failure(error)
    for step in steps:
        if step["kind"] == "map_elements":
            value = [mutable_pipeline(x, step["pipeline"], typ["element"], error) for x in value]
        elif step["kind"] == "transform":
            if step["operation"] == "trim":
                if value is None:
                    raise Failure(error)
                value = value.strip()
            elif step["operation"] == "stable_deduplicate":
                value = mutable_unique(value)
        else:
            rule = step["rule"]
            when = step.get("when")
            if when and "result_type" in when:
                if not predicate_eval(when, stages={"RAW": raw, "TRANSFORMED": value, "PERSISTED": value}):
                    continue
            elif when:
                observed = raw if when["stage"] == "RAW" else value
                predicate = when["predicate"]
                active = {"present": True, "absent": False, "empty": observed == "", "nonempty": observed != "", "whitespace": type(observed) is str and bool(observed) and observed.isspace()}[predicate]
                if not active:
                    continue
            observed = raw if step.get("stage") == "RAW" else value
            ok = mutable_value_valid(observed, typ) if rule == "typed" else bool(observed) if rule == "nonempty" else (type(observed) is str and bool(observed.strip()))
            if not ok:
                raise Failure(step["error"])
    if not mutable_value_valid(value, typ):
        raise Failure(error)
    return value


def execute_mutation(mutation, inputs):
    primary_context_validate(mutation["command"], inputs)
    state = SPEC["state"][0]
    record_type, path = state_layout(state)
    records = read_state(state, record_type, path)
    key = mutation["lookup"]
    target = next((r for r in records if r[key] == inputs.get(key)), None)
    if target is None:
        raise Failure(mutation["missing_error"])
    for guard in mutation["guards"]:
        ok = predicate_eval(guard["predicate"], target, inputs) if "predicate" in guard else target[guard["field"]] == guard["value"]
        if not ok:
            raise Failure(guard["error"])
    candidate = copy.deepcopy(target)
    changed = False
    for change in mutation["changes"]:
        if "source" in change:
            candidate[change["field"]] = copy.deepcopy(change["source"]["value"])
            changed = True
            continue
        supplied = change["input"] in inputs
        if not supplied:
            if change["omitted"] == "reject":
                if change["missing_error"] is None:
                    raise MissingExternalInput(change["input"])
                raise Failure(change["missing_error"])
            continue
        typ = MUTABLE["value_types"][change["field"]]
        changed = True
        value = mutable_pipeline(inputs[change["input"]], change["pipeline"], typ if change["operation"] == "replace" else typ["element"], change["invalid_error"])
        if change["operation"] == "replace":
            candidate[change["field"]] = value
        elif change["operation"] == "append" or value not in candidate[change["field"]]:
            candidate[change["field"]].append(value)
        if not mutable_value_valid(candidate[change["field"]], typ):
            raise Failure(change["invalid_error"])
    if not changed:
        return copy.deepcopy(target)
    staged = [candidate if r is target else copy.deepcopy(r) for r in records]
    for inv in MUTABLE["facts"].get("predicate_semantics", {}).get("invariants", []):
        if not predicate_eval(inv["predicate"], candidate):
            raise Failure(inv["error"])
    write_state(staged, state, record_type, path)
    return copy.deepcopy(candidate)


def execute(behavior, inputs, clock=None, *, providers=None):
    inputs = copy.deepcopy(inputs)
    command = next(c["token"] for c in SPEC["commands"] if c.get("behavior") == behavior["id"])
    primary_context_validate(command, {i["name"]: inputs[i["id"]] for i in behavior["inputs"] if i["id"] in inputs})
    guards = [g for g in MUTABLE["facts"].get("predicate_semantics", {}).get("guards", []) if g["command"] == command]
    if guards:
        state = SPEC["state"][0]
        record_type, path = state_layout(state)
        records = read_state(state, record_type, path)
        lookup = behavior["lookup"]
        target = next((r for r in records if r[field_name(record_type, lookup["field"])] == inputs.get(lookup["input"])), None)
        if target is not None:  # existing declared lookup error retains precedence
            named = {i["name"]: inputs[i["id"]] for i in behavior["inputs"] if i["id"] in inputs}
            for g in guards:
                if not predicate_eval(g["predicate"], target, named):
                    raise Failure(g["error"])
    if behavior["kind"] == "create":
        command = next(c["token"] for c in SPEC["commands"] if c.get("behavior") == behavior["id"])
        for p in MUTABLE["facts"].get("input_contracts", []):
            if p["operation"] == command and p["presence"] == "required":
                iid = next(i["id"] for i in behavior["inputs"] if i["name"] == p["parameter"])
                if iid not in inputs:
                    if p["missing"]["kind"] == "cli_rejection":
                        raise MissingExternalInput(p["parameter"])
                    raise Failure(p["missing"]["error"])
        pipelines = MUTABLE["facts"]["creation_pipelines"] + [dict(field=c["name"], pipeline=c["creation"]["pipeline"], error=c["creation"]["error"]) for c in MUTABLE["facts"]["collections"] if c["creation"].get("source") != "literal"] + [dict(field=c["name"], pipeline=c["creation"]["pipeline"], error=c["creation"]["error"]) for c in MUTABLE["facts"].get("primary_interfaces", {}).get("integers", []) if c["creation"]["source"] != "literal"]
        for p in pipelines:
            field = next(f for f in MUTABLE["model"]["types"] if f["kind"] == "record")["fields"]
            fid = next(f["id"] for f in field if f["name"] == p["field"])
            assignment = next(a for a in behavior["assignments"] if a["field"] == fid)
            iid = assignment["id"]
            if iid in inputs:
                inputs[iid] = mutable_pipeline(inputs[iid], p["pipeline"], MUTABLE["value_types"][p["field"]], p["error"])
    return _scalar_execute(behavior, inputs, clock, providers=providers)


def mutable_main(argv=None):
    parser = argparse.ArgumentParser(prog=SPEC["application"]["name"])
    commands = parser.add_subparsers(dest="command", required=True)
    mutations = {m["command"]: m for m in MUTABLE["facts"]["mutations"]}
    for c in SPEC["commands"]:
        sub = commands.add_parser(c["token"])
        if "migration" not in c:
            b = by_id("behaviors", c["behavior"])
            for arg in c["arguments"]:
                decl = next((x for x in MUTABLE["facts"]["collections"] if x["creation"].get("input") == arg["flag"][2:].replace("-", "_") and b["kind"] == "create"), None)
                sub.add_argument(arg["flag"], required=arg["required"], default=argparse.SUPPRESS, **({"action": "append"} if decl and decl["creation"]["encoding"] == "repeated" else {}))
    for token, m in mutations.items():
        sub = commands.add_parser(token)
        sub.add_argument("--" + m["lookup"].replace("_", "-"), required=True)
        for w in m["changes"]:
            if "source" in w:
                continue
            sub.add_argument("--" + w["input"].replace("_", "-"), default=argparse.SUPPRESS)
    parsed = vars(parser.parse_args(argv)); token = parsed.pop("command")
    try:
        if token in mutations:
            m = mutations[token]
            for w in m["changes"]:
                if "source" in w:
                    continue
                if w["input"] in parsed and w["operation"] == "replace" and MUTABLE["value_types"][w["field"]]["type"] == "collection":
                    try:
                        parsed[w["input"]] = json.loads(parsed[w["input"]])
                    except ValueError:
                        raise Failure(w["invalid_error"])
            result = execute_mutation(m, parsed)
        else:
            c = next(c for c in SPEC["commands"] if c["token"] == token)
            if "migration" in c:
                result = migrate()
            else:
                b = by_id("behaviors", c["behavior"]); inputs = {}
                for arg in c["arguments"]:
                    n = arg["flag"][2:].replace("-", "_")
                    if n not in parsed:
                        continue
                    value = parsed[n]
                    decl = next((x for x in MUTABLE["facts"]["collections"] if x["creation"].get("input") == n and b["kind"] == "create"), None)
                    if decl and decl["creation"]["encoding"] == "json":
                        try:
                            value = json.loads(value)
                        except ValueError:
                            raise Failure(decl["creation"]["error"])
                    inp = next(i for i in b["inputs"] if i["id"] == arg["input"])
                    if inp["type"] not in ("prim:string", "prim:timestamp", "prim:integer") and by_id("types", inp["type"])["kind"] == "enum" and value not in by_id("types", inp["type"])["values"]:
                        parser.error("invalid choice: " + value)
                    inputs[arg["input"]] = value
                result = execute(b, inputs)
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0
    except Failure as exc:
        print(json.dumps({"error": exc.code}), file=sys.stderr)
        return 1


def input_main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    declarations = MUTABLE["facts"].get("input_contracts", [])
    token = argv[0] if argv else None
    parameters = [p for p in declarations if p["operation"] == token]
    if not parameters:
        return mutable_main(argv)
    parser = argparse.ArgumentParser(prog=SPEC["application"]["name"] + " " + token)
    for p in parameters:
        parser.add_argument(p["binding"]["flag"], dest=p["parameter"], default=argparse.SUPPRESS,
                            **({"action": "append"} if p["binding"]["encoding"] == "repeated" else {}))
    parsed = vars(parser.parse_args(argv[1:]))
    for p in parameters:
        if p["presence"] == "required" and p["parameter"] not in parsed:
            if p["missing"]["kind"] == "cli_rejection":
                print("missing required input: " + p["binding"]["flag"], file=sys.stderr)
                return 2
            print(json.dumps({"error": p["missing"]["error"]}), file=sys.stderr)
            return 1
    try:
        mutation = next((m for m in MUTABLE["facts"]["mutations"] if m["command"] == token), None)
        behavior = None if mutation else by_id("behaviors", next(c["behavior"] for c in SPEC["commands"] if c["token"] == token))
        for p in parameters:
            n = p["parameter"]
            if n in parsed and p["binding"]["encoding"] == "json":
                error = next(w["invalid_error"] for w in mutation["changes"] if w.get("input") == n) if mutation else next(c["creation"]["error"] for c in MUTABLE["facts"]["collections"] + MUTABLE["facts"].get("primary_interfaces", {}).get("integers", []) if c["creation"].get("input") == n)
                try:
                    parsed[n] = json.loads(parsed[n])
                except ValueError:
                    raise Failure(error)
        if mutation:
            result = execute_mutation(mutation, parsed)
        else:
            inputs = {i["id"]: parsed[i["name"]] for i in behavior["inputs"] if i["name"] in parsed}
            result = execute(behavior, inputs)
        print(json.dumps(result, sort_keys=True, ensure_ascii=False))
        return 0
    except Failure as exc:
        print(json.dumps({"error": exc.code}), file=sys.stderr)
        return 1


main = input_main


def primary_context_validate(command, inputs):
    for p in MUTABLE["facts"].get("primary_interfaces", {}).get("context_inputs", []):
        if p["command"] != command:
            continue
        if p["name"] not in inputs:
            raise Failure(p["missing_error"])
        v = inputs[p["name"]]
        if not mutable_value_valid(v, p["type"]) or not v.strip():
            raise Failure(p["invalid_error"])
