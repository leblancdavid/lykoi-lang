"""TypedMutableValues-1 semantic validation and deterministic IR composition.

The legacy scalar algebra is a component, not a substitute for these types.
No requirement text or application command names are interpreted here.
"""
import copy

from lykoi_controller import Failure

VERSION = "typed-mutable-values-1"


def require(ok, reason):
    if not ok:
        raise Failure("INVALID_TYPED_MUTATION", reason=reason)


def keys(value, names):
    require(type(value) is dict and set(value) == set(names), "Closed mutation object: " + str(names))


def valid_value(value, typ):
    if typ["type"] == "collection":
        if type(value) is not list or not all(valid_value(x, typ["element"]) for x in value):
            return False
        return typ["duplicates"] == "allow" or stable_unique(value) == value
    if value is None:
        return typ.get("nullable", False)
    if type(value) is not str:
        return False
    if typ["type"] == "enum":
        return value in typ["domain"]
    if typ["type"] == "timestamp":
        from .runtime_template import utc_timestamp
        return utc_timestamp(value)
    return typ["type"] in ("string", "identifier")


def stable_unique(values):
    result = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def pipeline(steps, typ):
    require(type(steps) is list, "Explicit ordered pipeline, including empty verbatim pipeline")
    for step in steps:
        if step.get("kind") == "map_elements":
            keys(step, ("kind", "pipeline"))
            require(typ["type"] == "collection", "Element pipelines require a typed collection")
            pipeline(step["pipeline"], typ["element"])
        elif step.get("kind") == "transform":
            keys(step, ("kind", "operation"))
            op = step["operation"]
            require(op in ("verbatim", "trim", "stable_deduplicate"), "Authorized bounded transformation")
            require(op != "trim" or typ["type"] in ("string", "identifier", "enum"), "Trim scalar string-like values only")
            require(op != "stable_deduplicate" or typ["type"] == "collection", "Dedup collection only")
        else:
            keys(step, ("kind", "rule", "error"))
            require(step["kind"] == "validate" and step["rule"] in ("nonempty", "nonblank", "typed"), "Explicit validation stage")
            require(step["rule"] == "typed" or typ["type"] in ("string", "identifier", "enum"), "String validation only")
            require(type(step["error"]) is str and bool(step["error"]), "Declared stage error")


def compose(base, facts):
    """Validate the new algebra and lower to a typed model plus atomic-write nodes."""
    from lykoi_pipeline.scalar_profile import name, command_name
    keys(facts, ("collections", "mutations", "creation_pipelines"))
    d = copy.deepcopy(base)
    require(len(d["state"]) == 1, "Single-record, single-store profile")
    state = d["state"][0]
    collection_versions = [m["to"] for c in facts["collections"] for m in c.get("migration", [])]
    state["schema_version"] = max([state["schema_version"]] + collection_versions)
    types = {t["id"]: t for t in d["types"]}
    record = types[types[state["type"]]["item_type"]]
    fields = {f["name"]: f for f in record["fields"]}
    def scalar_type(f):
        t = f["type"]
        return dict(type="timestamp" if t == "prim:timestamp" else "string" if t == "prim:string" else "enum", domain=types[t]["values"] if t in types else [], nullable=f.get("nullable", False))
    value_types = {n: scalar_type(f) for n, f in fields.items()}
    identity = next(n for n, f in fields.items() if f["id"] == state["key_field"])
    create = next(b for b in d["behaviors"] if b["kind"] == "create")
    create_command = next(c for c in d["commands"] if c.get("behavior") == create["id"])
    require(type(facts["collections"]) is list, "Collection declarations")
    for c in facts["collections"]:
        keys(c, ("name", "element", "ordering", "duplicates", "equality", "creation", "migration"))
        name(c["name"])
        require(c["name"] not in fields, "Collection field must be explicitly introduced")
        keys(c["element"], ("type", "domain"))
        e = c["element"]
        require(e["type"] in ("string", "identifier", "enum", "timestamp"), "Bounded nonnullable scalar elements")
        require((e["type"] == "enum" and type(e["domain"]) is list and bool(e["domain"]) and all(type(x) is str for x in e["domain"]) and len(set(e["domain"])) == len(e["domain"])) or (e["type"] != "enum" and e["domain"] == []), "Exact element domain")
        require(c["ordering"] == "insertion" and c["duplicates"] in ("allow", "unique") and c["equality"] == "exact", "Independent explicit order/duplicate/exact case-sensitive equality policies")
        typ = dict(type="collection", element=e, ordering=c["ordering"], duplicates=c["duplicates"], equality=c["equality"])
        value_types[c["name"]] = typ
        keys(c["creation"], ("input", "encoding", "default", "pipeline", "error"))
        name(c["creation"]["input"])
        require(c["creation"]["input"] not in {i["name"] for i in create["inputs"]} and c["creation"]["encoding"] in ("json", "repeated"), "Distinct declared collection input and encoding")
        require(valid_value(c["creation"]["default"], typ), "Explicit typed creation default; never migration authority")
        pipeline(c["creation"]["pipeline"], typ)
        name(c["creation"]["error"])
        fid, tid, iid = "field:mutable:" + c["name"], "type:mutable:" + c["name"], "input:mutable:create:" + c["name"]
        field = dict(id=fid, name=c["name"], type=tid)
        fields[c["name"]] = field; record["fields"].append(field)
        d["types"].append(dict(id=tid, name=c["name"], kind="value_collection", **{k: v for k, v in typ.items() if k != "type"}))
        create["inputs"].append(dict(id=iid, name=c["creation"]["input"], type=tid))
        create_command["arguments"].append(dict(flag="--" + c["creation"]["input"].replace("_", "-"), input=iid, required=False))
        create["assignments"].append(dict(field=fid, source="input_default", id=iid, value=copy.deepcopy(c["creation"]["default"])))
        create["guarantees"].append(dict(id="guarantee:mutable:" + c["name"], kind="result_field_equals_assignment", field=fid))
        require(type(c["migration"]) is list, "Explicit collection migration authority, including no history")
        for m in c["migration"]:
            keys(m, ("from", "to", "value"))
            require(type(m["from"]) is int and m["from"] >= 1 and m["to"] == m["from"] + 1 and m["to"] <= state["schema_version"], "Additive collection migration boundary")
            require(valid_value(m["value"], typ), "Typed historical default")
            prior = next((x for x in d["migrations"] if x["from_version"] == m["from"]), None)
            if prior is None:
                access = [x["id"] for x in d["capabilities"] if x["kind"] == "resource_access" and x["resource"] == state["storage"]]
                prior = dict(id="migration:mutable:" + str(m["from"]), state=state["id"], from_version=m["from"], to_version=m["to"], add_fields=[], requires=access, effects=["state_read", "state_write", "file_read", "file_write"])
                d["migrations"].append(prior)
            prior["add_fields"].append(dict(field=fid, value=copy.deepcopy(m["value"])))
        require(state["schema_version"] == 1 or len(c["migration"]) == 1, "One explicit historical introduction per added collection")
    if d["migrations"] and not any("migration" in c for c in d["commands"]):
        d["commands"].append(dict(id="command:mutable:migrate", token="migrate", migration=max(d["migrations"], key=lambda x: x["to_version"])["id"], arguments=[]))
    require(sorted(m["to_version"] for m in d["migrations"]) == list(range(2, state["schema_version"] + 1)), "Complete additive migration chain")
    for c in d["commands"]:
        if "migration" in c:
            c["migration"] = max(d["migrations"], key=lambda x: x["to_version"])["id"]
    if state["schema_version"] > 1:
        if not any(e["code"] == "migration_required" for e in d["errors"]):
            d["errors"].append(dict(id="error:mutable:migration_required", code="migration_required"))
        eid = next(e["id"] for e in d["errors"] if e["code"] == "migration_required")
        for b in d["behaviors"]:
            b["failures"] = sorted(set(b["failures"] + [eid]))
    require(type(facts["creation_pipelines"]) is list, "Explicit scalar creation pipelines")
    seen = set()
    for c in facts["creation_pipelines"]:
        keys(c, ("field", "pipeline", "error"))
        require(c["field"] in fields and c["field"] not in seen and value_types[c["field"]]["type"] != "collection", "Unique existing scalar creation input")
        seen.add(c["field"])
        require(any(a["field"] == fields[c["field"]]["id"] and a["source"] in ("input", "input_default") for a in create["assignments"]), "Creation pipeline requires supplied input binding")
        pipeline(c["pipeline"], value_types[c["field"]]); name(c["error"])
    lifecycle = {m["field"] for m in d["state_machines"]}
    commands = {c["token"] for c in d["commands"]}
    require(type(facts["mutations"]) is list, "Explicit atomic mutations")
    for m in facts["mutations"]:
        keys(m, ("command", "lookup", "missing_error", "changes", "guards", "effect"))
        command_name(m["command"]); name(m["missing_error"])
        require(m["command"] not in commands and m["lookup"] == identity, "Disjoint command and immutable identity lookup")
        commands.add(m["command"])
        require(m["effect"] == {"atomicity": "single_record", "persistence": "atomic", "rejection": "unchanged"}, "Complete atomic write effect")
        require(type(m["changes"]) is list and bool(m["changes"]), "Nonempty simultaneous field changes")
        changed, inputs = set(), {identity}
        for w in m["changes"]:
            keys(w, ("field", "input", "operation", "omitted", "missing_error", "pipeline", "invalid_error"))
            name(w["input"]); name(w["invalid_error"])
            require(w["field"] in fields and w["field"] != identity and fields[w["field"]]["id"] not in lifecycle and w["field"] not in changed and w["input"] not in inputs, "Distinct writable nonidentity/nonlifecycle fields and inputs")
            changed.add(w["field"]); inputs.add(w["input"])
            typ = value_types[w["field"]]
            require(w["operation"] in ("replace", "append", "add_unique"), "Distinct mutation operations")
            require(w["operation"] == "replace" or typ["type"] == "collection", "Append/add collection only")
            require(w["operation"] != "append" or typ["duplicates"] == "allow", "Append cannot violate unique policy")
            require(w["omitted"] in ("unchanged", "reject"), "Explicit input presence semantics")
            require((w["omitted"] == "unchanged" and w["missing_error"] is None) or (w["omitted"] == "reject" and type(w["missing_error"]) is str and bool(w["missing_error"])), "Distinct missing-input authority")
            pipeline(w["pipeline"], typ["element"] if w["operation"] != "replace" else typ)
        require(type(m["guards"]) is list, "Explicit prewrite guards")
        for g in m["guards"]:
            keys(g, ("field", "value", "error"))
            require(g["field"] in fields and valid_value(g["value"], value_types[g["field"]]), "Typed equality guard")
            name(g["error"])
    return dict(version=VERSION, base=copy.deepcopy(base), model=d, value_types=value_types, facts=copy.deepcopy(facts))
