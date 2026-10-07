"""Persistent-reference-1: nominal identity, finite selection and commit composition.

The one new core candidate is explicit nonempty-path reachability. Reference
policies lower to inspectable selections; neither SQL nor prose enters lowering.
"""
import copy

from .predicates import validate as predicate_validate, scalar_type, same_type
from .mutable_values import valid_value
from lykoi_controller import Failure

VERSION = "persistent-references-1"
FACET = "reference_semantics"


def require(ok, reason):
    if not ok:
        raise Failure("INVALID_REFERENCE_COMPOSITION", reason=reason)


def keys(v, names):
    require(type(v) is dict and set(v) == set(names), "Closed reference object: " + str(names))


def identity(entity):
    return dict(type="identifier", domain=[], entity=entity)


def operand(kind, typ, name):
    return dict(kind=kind, type=copy.deepcopy(typ), name=name)


def match(left, right, member=False):
    return dict(kind="member" if member else "compare", result_type="boolean", operator="in" if member else "eq", left=left, right=right, policy=dict(case="sensitive", normalization="none"), nulls="false")


def count_selection(entity, predicate, value):
    return dict(kind="extent", result_type="boolean", selection=dict(entity=entity, binding="related", predicate=predicate), relation="eq", value=value)


def erase(t):
    t = copy.deepcopy(t)
    if t.get("type") == "collection":
        t["element"] = erase(t["element"])
    t.pop("entity", None)
    return t


def value_type(t, entities):
    scalar_type(erase(t))
    atom = t["element"] if t["type"] == "collection" else t
    if "entity" in atom:
        keys(atom, ("type", "domain", "entity"))
        require(atom == identity(atom["entity"]) and atom["entity"] in entities, "Nominal entity identity")
    return t


def flat_types(bindings, types):
    return {a + "." + n: t for a, entity in bindings.items() for n, t in types[entity].items()}


def validate_condition(tree, types, bindings, parameters, depth=0, computed=None):
    require(depth < 24, "Bounded condition depth")
    require(type(tree) is dict and tree.get("result_type") == "boolean", "Explicit boolean condition")
    kind = tree.get("kind")
    if kind in ("and", "or", "not"):
        keys(tree, ("kind", "result_type", "child") if kind == "not" else ("kind", "result_type", "children"))
        children = [tree["child"]] if kind == "not" else tree["children"]
        require(type(children) is list and 1 <= len(children) <= 64 and (kind == "not" or len(children) >= 2), "Explicit grouping")
        for c in children:
            validate_condition(c, types, bindings, parameters, depth + 1, computed)
    elif kind == "extent":
        keys(tree, ("kind", "result_type", "selection", "relation", "value"))
        require(tree["relation"] in ("eq", "ge") and type(tree["value"]) is int and tree["value"] >= 0, "Nonnegative cardinality relation; no arithmetic")
        s = tree["selection"]
        keys(s, ("entity", "binding", "predicate"))
        require(s["entity"] in types and s["binding"] not in bindings, "Explicit finite entity domain and fresh binding")
        # No recursive selection/query nesting in a selection predicate.
        validate_atom(s["predicate"], types, {**bindings, s["binding"]: s["entity"]}, parameters, computed)
    elif kind == "reachable":
        keys(tree, ("kind", "result_type", "entity", "field", "source", "target", "paths"))
        require(tree["entity"] in types and tree["field"] in types[tree["entity"]], "Declared relation projection")
        t = types[tree["entity"]][tree["field"]]
        atom = t["element"] if t["type"] == "collection" else t
        require(atom == identity(tree["entity"]) and tree["paths"] == "nonempty", "Same-entity nominal edges; nonempty finite paths")
        synthetic = dict(kind="compare", result_type="boolean", operator="eq", left=tree["source"], right=tree["target"], policy=dict(case="sensitive", normalization="none"), nulls="false")
        validate_atom(synthetic, types, bindings, parameters, computed)
        require(tree["source"]["type"] == tree["target"]["type"] == identity(tree["entity"]), "Reachability endpoint type")
    else:
        validate_atom(tree, types, bindings, parameters, computed)
    return copy.deepcopy(tree)


def validate_atom(tree, types, bindings, parameters, computed=None):
    fields = flat_types(bindings, types)
    def nominal(node):
        if type(node) is dict:
            if node.get("kind") in ("compare", "member"):
                l, r = node["left"]["type"], node["right"]["type"]
                require(same_type(l, r["element"] if node["kind"] == "member" else r), "No cross-entity identity substitution")
                atom = l.get("element", l)
                if "entity" in atom:
                    require(node["policy"] == dict(case="sensitive", normalization="none"), "Identity comparison is exact")
            if node.get("kind") in ("field", "parameter", "computed"):
                env = fields if node["kind"] == "field" else (computed or {}) if node["kind"] == "computed" else parameters
                require(node["name"] in env and same_type(node["type"], env[node["name"]]), "Explicit nominal binding and field namespace")
            for v in node.values(): nominal(v)
        elif type(node) is list:
            for v in node: nominal(v)
    nominal(tree)
    def lower(node):
        if type(node) is dict:
            return {k: "parameter" if k == "kind" and v == "computed" else erase(v) if k == "type" and type(v) is dict else lower(v) for k, v in node.items()}
        return [lower(x) for x in node] if type(node) is list else node
    predicate_validate(lower(tree), fields={n: erase(t) for n, t in fields.items()}, parameters={n: erase(t) for n, t in {**parameters, **(computed or {})}.items()})


def compose(ir, f):
    keys(f, ("primary", "entities", "references", "operations", "guards", "commit"))
    require(f["commit"] == dict(scope="one_store", mutation="one_record", isolation="exclusive_operation", rejection="unchanged"), "Bounded coherent store commit")
    primary = f["primary"]
    require(type(primary) is str and bool(primary), "Named primary entity")
    types = {primary: copy.deepcopy(ir["value_types"])}
    model = ir["model"]
    state = model["state"][0]
    rec = next(t for t in model["types"] if t["kind"] == "record")
    key = next(x["name"] for x in rec["fields"] if x["id"] == state["key_field"])
    types[primary][key] = identity(primary)
    identities = {primary: key}
    require(type(f["entities"]) is list, "Explicit related schemas")
    for e in f["entities"]:
        keys(e, ("name", "key", "fields", "initial"))
        require(e["name"] not in types and type(e["fields"]) is dict and e["key"] in e["fields"], "Unique entity and identity projection")
        types[e["name"]] = copy.deepcopy(e["fields"])
        identities[e["name"]] = e["key"]
    for e, fields in types.items():
        require(fields[identities[e]] == identity(e), "Reuse identifier value with nominal entity type")
        for t in fields.values(): value_type(t, types)
    seen = set()
    checks = []
    for r in f["references"]:
        keys(r, ("entity", "field", "target", "existence", "deletion", "migration"))
        require(r["entity"] in types and r["target"] in types and r["field"] in types[r["entity"]], "Reference field/target domain")
        require((r["entity"], r["field"]) not in seen, "Unique field target authority")
        seen.add((r["entity"], r["field"]))
        t = types[r["entity"]][r["field"]]
        atom = t["element"] if t["type"] == "collection" else t
        stored_atom = erase(atom)
        if stored_atom.get("nullable") is False: stored_atom.pop("nullable")
        require(stored_atom in (dict(type="identifier", domain=[]), dict(type="string", domain=[])), "References reuse stored identity values")
        if "entity" in atom: require(atom["entity"] == r["target"], "Field target type cannot be substituted")
        if t["type"] == "collection": t["element"] = identity(r["target"])
        else: types[r["entity"]][r["field"]] = identity(r["target"])
        if r["migration"] is not None:
            keys(r["migration"], ("when", "value"))
            require(r["migration"]["when"] == "missing_or_empty" and valid_value(r["migration"]["value"], erase(types[r["entity"]][r["field"]])), "Explicit reference migration value")
        for policy, choices in (("existence", ("required", "unchecked")), ("deletion", ("restrict", "permit", "unavailable"))):
            keys(r[policy], ("policy", "error"))
            require(r[policy]["policy"] in choices, "Explicit " + policy + " authority; no cascade")
            required = r[policy]["policy"] in ("required", "restrict")
            require((type(r[policy]["error"]) is str and bool(r[policy]["error"])) if required else r[policy]["error"] is None, "Declared material error; no conventional default")
        ti = identity(r["target"])
        exists = count_selection(r["target"], match(operand("field", ti, "related." + identities[r["target"]]), operand("parameter", ti, "candidate_identity")), 1)
        reverse_field = types[r["entity"]][r["field"]]
        left = operand("parameter", ti, "deleted_identity") if t["type"] == "collection" else operand("field", ti, "related." + r["field"])
        right = operand("field", reverse_field, "related." + r["field"]) if t["type"] == "collection" else operand("parameter", ti, "deleted_identity")
        reverse = count_selection(r["entity"], match(left, right, t["type"] == "collection"), 0)
        checks.append(dict(reference=copy.deepcopy(r), existence=dict(iterator="each_reference_value", predicate=exists, observation="candidate_before_commit"), reverse=dict(predicate=reverse, observation="candidate_without_deleted_record")))
    # Related nominal fields must not lose their existence/deletion authority.
    for e, fields in types.items():
        for n, t in fields.items():
            atom = t.get("element", t)
            require("entity" not in atom or n == identities[e] or (e, n) in seen, "Every nominal reference field needs explicit integrity policy")
    for check in checks:
        ti = identity(check["reference"]["target"])
        validate_condition(check["existence"]["predicate"], types, {}, {"candidate_identity": ti})
        validate_condition(check["reverse"]["predicate"], types, {}, {"deleted_identity": ti})
    for e in f["entities"]:
        ids = []
        for row in e["initial"]:
            require(type(row) is dict and set(row) == set(types[e["name"]]) and all(valid_value(v, erase(types[e["name"]][n])) for n, v in row.items()), "Typed initial entity state")
            value = row[e["key"]]
            require(type(value) is str and bool(value.strip()) and value not in ids, "Nonblank unique initial identity")
            ids.append(value)
    commands = {"migrate"} | {c["token"] for c in model["commands"]} | {m["command"] for m in ir["facts"]["mutations"]}
    for op in f["operations"]:
        keys(op, ("command", "entity", "kind", "parameters", "lookup", "missing_error", "duplicate_error", "changes", "guards", "order") + (("computations",) if "computations" in op else ()))
        require(op["command"] not in commands and op["entity"] in types, "Explicit unique operation/entity scope")
        commands.add(op["command"])
        require(op["kind"] in ("create", "update", "delete", "list"), "Bounded one-record effects")
        e = op["entity"]
        for n, p in op["parameters"].items():
            keys(p, ("type", "flag", "encoding", "missing_error", "invalid_error") + (("conversion",) if "conversion" in p else ()))
            value_type(p["type"], types)
            require(p["flag"].startswith("--") and p["encoding"] in ("text", "json", "utc_day") and all(type(p[k]) is str and bool(p[k]) for k in ("missing_error", "invalid_error")), "Explicit parameter transport/errors")
            if p["encoding"] == "utc_day":
                require(same_type(p["type"], dict(type="timestamp", domain=[])) and p.get("conversion") == dict(source="gregorian_utc_day", target="instant", boundary="start_of_day", timezone="UTC", precision="seconds", invalid="reject"), "Exact date-to-instant representation authority")
            else:
                require("conversion" not in p, "No undeclared transport conversion")
        require(len({p["flag"] for p in op["parameters"].values()}) == len(op["parameters"]), "Unique parameter flags")
        params = {n: p["type"] for n, p in op["parameters"].items()}
        computed = {}
        if "computations" in op:
            from .computation import validate as validate_computation
            require(op["kind"] in ("create", "update"), "Computation on write operations only")
            computed = validate_computation(op["computations"], types, e, params, images=("before",) if op["kind"] == "update" else ())
        if op["kind"] in ("update", "delete"):
            require(op["lookup"] in params and params[op["lookup"]] == identity(e) and type(op["missing_error"]) is str and bool(op["missing_error"]), "Typed primary lookup and missing authority")
        else: require(op["lookup"] is None and op["missing_error"] is None, "No implicit lookup")
        require((type(op["duplicate_error"]) is str and bool(op["duplicate_error"])) if op["kind"] == "create" else op["duplicate_error"] is None, "Creation duplicate authority")
        require(not op["changes"] if op["kind"] in ("list", "delete") else bool(op["changes"]), "Bounded effects")
        require(op["entity"] != primary or op["kind"] != "create", "Primary creation retains existing resource/lifecycle authority")
        require(set(op["order"]) <= set(types[e]) and len(set(op["order"])) == len(op["order"]), "Declared listing key projection")
        fields = []
        for w in op["changes"]:
            keys(w, ("field", "source", "operation", "invalid_error"))
            require(w["field"] in types[e] and w["field"] not in fields, "Unique typed write target")
            fields.append(w["field"])
            require(op["kind"] == "create" or w["field"] != identities[e], "Identity is immutable")
            if e == primary:
                lifecycle = {next(x["name"] for x in rec["fields"] if x["id"] == sm["field"]) for sm in model["state_machines"]}
                require(w["field"] not in lifecycle, "Primary lifecycle retains transition authority")
            require(w["operation"] in ("replace", "append", "add_unique", "remove"), "Existing insertion/replacement plus stable membership removal composition")
            target = types[e][w["field"]]
            if w["operation"] != "replace":
                require(target["type"] == "collection", "Element mutation needs finite sequence")
                target = target["element"]
            s = w["source"]
            if s.get("kind") == "computed":
                from .computation import bound
                bound(s, computed, target)
                require(type(w["invalid_error"]) is str and bool(w["invalid_error"]), "Declared invalid candidate error")
                continue
            require(s.get("kind") in ("parameter", "literal"), "Typed write source")
            keys(s, ("kind", "type", "name") if s["kind"] == "parameter" else ("kind", "type", "value"))
            require(same_type(s["type"], target), "Exact nominal write type")
            require((s["name"] in params and same_type(params[s["name"]], target)) if s["kind"] == "parameter" else valid_value(s["value"], erase(target)), "Bound write source")
            require(type(w["invalid_error"]) is str and bool(w["invalid_error"]), "Declared invalid candidate error")
        if op["kind"] == "create": require(set(fields) == set(types[e]), "Complete typed creation")
        for g in op["guards"]:
            keys(g, ("predicate", "error"))
            require(type(g["error"]) is str and bool(g["error"]), "Declared guard error")
            validate_condition(g["predicate"], types, {"primary": e} if op["kind"] in ("update", "delete") else {}, params, computed=computed)
        require(not set(params) & set(computed), "Computed bindings cannot shadow inputs")
    for g in f["guards"]:
        keys(g, ("command", "parameters", "predicate", "error"))
        require(g["command"] in {c["token"] for c in model["commands"]} | {m["command"] for m in ir["facts"]["mutations"]}, "Guard binds existing primary operation")
        require(type(g["error"]) is str and bool(g["error"]), "Guard missing behavior requires clarification")
        params = g["parameters"]
        # Only existing supplied inputs may bind; do not invent ambient names.
        b = next((b for b in model["behaviors"] if any(c.get("behavior") == b["id"] and c["token"] == g["command"] for c in model["commands"])), None)
        allowed = {i["name"] for i in b["inputs"]} if b else {m["lookup"] for m in ir["facts"]["mutations"] if m["command"] == g["command"]} | {w["input"] for m in ir["facts"]["mutations"] if m["command"] == g["command"] for w in m["changes"] if "input" in w}
        require(set(params) <= allowed, "No implicit global input lookup")
        declared = {p["parameter"]: p["type"] for p in ir["facts"].get("input_contracts", []) if p["operation"] == g["command"]}
        for n, t in params.items():
            value_type(t, types)
            expected = types[primary].get(n, declared.get(n))
            require(expected is not None and same_type(t, expected), "Existing guard input nominal authority")
        validate_condition(g["predicate"], types, {"primary": primary}, params)
    deletable = {o["entity"] for o in f["operations"] if o["kind"] == "delete"}
    if any(b["kind"] == "delete" for b in model["behaviors"]): deletable.add(primary)
    require(all(r["target"] not in deletable for r in f["references"] if r["deletion"]["policy"] == "unavailable"), "Deletion unavailable only when no target delete effect is exposed; do not invent a policy")
    return dict(version=VERSION, facts=copy.deepcopy(f), types=types, identities=identities, checks=checks, storage=copy.deepcopy(state))
