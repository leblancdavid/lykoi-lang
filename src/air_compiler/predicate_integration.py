"""Bounded normal model integration, independent of legacy serialization."""
import copy

from .mutable_values import keys, require
from .predicates import validate, same_type


def add_booleans(model, semantics, fields, types, record, create):
    from lykoi_pipeline.scalar_profile import name
    keys(semantics, ("booleans", "guards", "invariants"))
    require(type(semantics["booleans"]) is list, "Explicit boolean declarations")
    for b in semantics["booleans"]:
        keys(b, ("name", "creation", "migration")); name(b["name"])
        require(b["name"] not in fields, "Fresh generic boolean field")
        keys(b["creation"], ("source", "value"))
        require(b["creation"]["source"] == "literal" and type(b["creation"]["value"]) is bool, "Typed literal boolean creation")
        fid = "field:predicate:" + b["name"]
        field = dict(id=fid, name=b["name"], type="prim:boolean")
        fields[b["name"]] = field; record["fields"].append(field)
        types[b["name"]] = dict(type="boolean", domain=[], nullable=False)
        create["assignments"].append(dict(field=fid, source="literal", value=b["creation"]["value"]))
        require(type(b["migration"]) is list, "Explicit historical boolean authority")
        for m in b["migration"]:
            keys(m, ("from", "to", "value"))
            require(type(m["from"]) is int and m["from"] >= 1 and m["to"] == m["from"] + 1 and type(m["value"]) is bool, "Additive typed boolean migration")
            state = model["state"][0]
            state["schema_version"] = max(state["schema_version"], m["to"])
            prior = next((x for x in model["migrations"] if x["from_version"] == m["from"]), None)
            if prior is None:
                access = [x["id"] for x in model["capabilities"] if x["kind"] == "resource_access" and x["resource"] == state["storage"]]
                prior = dict(id="migration:predicate:" + str(m["from"]), state=state["id"], from_version=m["from"], to_version=m["to"], add_fields=[], requires=access, effects=["state_read", "state_write", "file_read", "file_write"])
                model["migrations"].append(prior)
            prior["add_fields"].append(dict(field=fid, value=m["value"]))
        require(model["state"][0]["schema_version"] == 1 or len(b["migration"]) == 1, "Historical boolean introduction must be authorized")


def validate_semantics(model, semantics, types, facts):
    from lykoi_pipeline.scalar_profile import name
    commands = {c["token"]: c for c in model["commands"] if "behavior" in c}
    require(type(semantics["guards"]) is list and type(semantics["invariants"]) is list, "Explicit guards and record-local invariants")
    for g in semantics["guards"]:
        keys(g, ("command", "predicate", "error", "rejection"))
        require(g["command"] in commands and g["rejection"] == "unchanged", "Precondition on existing lookup operation, rejection unchanged")
        b = next(b for b in model["behaviors"] if b["id"] == commands[g["command"]]["behavior"])
        require(b["kind"] in ("update", "delete") and "lookup" in b, "No cross-entity/create preconditions")
        names = {f["id"]: f["name"] for t in model["types"] if t["kind"] == "record" for f in t["fields"]}
        params = {i["name"]: types[names[b["lookup"]["field"]]] for i in b["inputs"]}
        validate(g["predicate"], fields=types, parameters=params); name(g["error"])
    for inv in semantics["invariants"]:
        keys(inv, ("predicate", "error"))
        validate(inv["predicate"], fields=types)
        require(inv["error"] == "invalid_state", "Record-local invariant uses existing invalid-state rejection at read/write boundaries")


def validate_query(q, complete=False, *, occurrence_order=False):
    from .collection_query import keys as qkeys, validate as old_validate
    from .predicates import scalar_type
    from .collection_query import FACETS, INTERFACES
    qkeys(q, ("id", *FACETS, *(n for n in INTERFACES if n in q)))
    qkeys(q["source"], ("collection", "fields", "unique_key"))
    fields, params = q["source"]["fields"], q["parameters"]
    require(type(fields) is dict and bool(fields) and type(params) is dict, "Typed query fields/parameters")
    for t in list(fields.values()) + list(params.values()):
        scalar_type(t)
    resources = {}
    for binding in q.get("resources", []):
        qkeys(binding, ("name", "type", "capability", "sampling"))
        require(binding["name"] not in resources and type(binding["name"]) is str and bool(binding["name"]), "Unique declared resource operand")
        require(binding["type"] == dict(type="timestamp", domain=[], nullable=False) and binding["sampling"] == "once_per_query" and type(binding["capability"]) is str and bool(binding["capability"]), "Explicit existing UTC clock resource binding and sampling")
        resources[binding["name"]] = binding["type"]
    validate(q["predicate"], fields=fields, parameters=params, resources=resources)
    for pre in q.get("preconditions", []):
        qkeys(pre, ("predicate", "error", "stage", "rejection"))
        require(pre["stage"] == "before_selection" and pre["rejection"] == "unchanged" and type(pre["error"]) is str and bool(pre["error"]), "Declared query precondition error, stage and no write")
        validate(pre["predicate"], parameters=params, resources=resources)
    errors = q.get("parameter_errors", {})
    require(type(errors) is dict and set(errors) <= set(params), "Parameter error binding")
    for n, e in errors.items():
        qkeys(e, ("missing", "invalid"))
        require(type(e["invalid"]) is str and bool(e["invalid"]), "Declared type error distinct from preconditions")
        require((type(e["missing"]) is str and bool(e["missing"])) or e["missing"] == {"kind": "cli_rejection"}, "Existing application missing error or explicit required-CLI rejection")
    if "amendment" in q:
        a = q["amendment"]
        qkeys(a, ("base", "composition", "predicate"))
        require(a["composition"] in ("and", "or", "replace"), "Source must determine amendment composition")
        require("amendment" not in a["base"], "Bounded amendment of one complete existing query; flatten successive amendments explicitly")
        old_validate(a["base"], complete=True)
        require(a["base"]["predicate"].get("result_type") == "boolean", "Existing query selection normalized to common tree")
        validate(a["predicate"], fields=fields, parameters=params, resources=resources)
        tree = a["predicate"] if a["composition"] == "replace" else dict(kind=a["composition"], result_type="boolean", children=[a["base"]["predicate"], a["predicate"]])
        require(q["predicate"] == tree, "Amendment must preserve explicit composition")
        require(all(q[n] == a["base"][n] for n in FACETS if n != "predicate"), "Selection-only amendment preserves all unrelated query facets")
        require(all(q.get(n) == a["base"][n] for n in INTERFACES if n != "amendment" and n in a["base"]), "Existing query validation/resource interfaces preserved")
    require(q["comparison"] == {"scope": "predicate_nodes"} and q["inclusion"] == [], "All selection in one common tree; policy belongs to atomic node")
    key = q["source"]["unique_key"]
    require(key in fields and fields[key]["type"] in ("string", "identifier") and not fields[key].get("nullable", False), "Stable nonnullable query identity")
    for order in q["ordering"] or []:
        require(order["field"] in fields and fields[order["field"]]["type"] != "collection" and not fields[order["field"]].get("nullable", False), "No new nullable/collection ordering")
    for rule in q["validation"] or []:
        require(rule["parameter"] in params and params[rule["parameter"]]["type"] in ("string", "identifier", "enum"), "Existing string input validation")
    # Reuse the bounded result/effect/order/validation policies without adding a
    # second selection representation. The proxy is validation-only, never IR.
    proxy = copy.deepcopy(q)
    for n in INTERFACES:
        proxy.pop(n, None)
    proxy["source"]["fields"] = {n: "string" for n in fields}
    proxy["parameters"] = {n: "string" for n in params} or {"unused": "string"}
    proxy["predicate"] = dict(field=key, operator="equals", operand={"constant": ""})
    proxy["comparison"] = dict(case="sensitive", normalization="none")
    old_validate(proxy, complete=complete, occurrence_order=occurrence_order)
    return copy.deepcopy(q)
