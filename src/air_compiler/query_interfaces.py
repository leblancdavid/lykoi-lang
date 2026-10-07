"""Existing listing normalization and declared capability authority, R5.107."""
import copy

from .mutable_values import require


def listing(model, types, command):
    """Normalize supported scalar listing semantics, without application dispatch."""
    c = next(c for c in model["commands"] if c["token"] == command)
    b = next(b for b in model["behaviors"] if b["id"] == c["behavior"])
    require(b["kind"] == "list" and not b["inputs"] and not b["writes"] and not b["conditions"], "Supported read-only no-input listing")
    names = {f["id"]: f["name"] for t in model["types"] if t["kind"] == "record" for f in t["fields"]}
    state = next(s for s in model["state"] if s["id"] == b["state"])
    policy = dict(case="sensitive", normalization="none")
    resources = {}
    def operand(kind, name=None, value=None, typ=None):
        return dict(kind=kind, type=copy.deepcopy(typ or types[name]), **({"value": value} if kind == "literal" else {"name": name}))
    def comparison(left, right, op="eq"):
        return dict(kind="compare", result_type="boolean", operator=op, left=left, right=right, policy=policy, nulls="false")
    def tree(f):
        if f["kind"] == "all":
            return dict(kind="and", result_type="boolean", children=[tree(x) for x in f["predicates"]])
        n = names[f["field"]]
        if f["kind"] == "field_before_clock":
            cid = f["clock"]
            require(next(c for c in model["capabilities"] if c["id"] == cid)["kind"] == "utc_clock" and cid in b["requires"], "Existing listing declares clock authority")
            clock_type = dict(type="timestamp", domain=[], nullable=False)
            resources[cid] = dict(name=cid, type=clock_type, capability=cid, sampling="once_per_query")
            return comparison(operand("field", n), operand("resource", cid, typ=clock_type), "lt")
        require(f["kind"] == "field_equals", "Clock listing needs an explicitly resource-bound query, not an implicit amendment")
        return comparison(operand("field", n), operand("literal", n, f["value"]))
    boolean = dict(type="boolean", domain=[], nullable=False)
    true = operand("literal", value=True, typ=boolean)
    predicate = tree(b["filter"]) if "filter" in b else comparison(true, true)
    query = dict(id=command, source=dict(collection=state["id"], fields=copy.deepcopy(types), unique_key=names[state["key_field"]]), parameters={}, predicate=predicate, comparison=dict(scope="predicate_nodes"), ordering=[dict(field=names[f], direction="ASC") for f in b["order_by"]], validation=[], inclusion=[], effect=dict(state="read_only", persistence="unchanged"), result=dict(shape="collection", cardinality="zero_or_more", no_match="empty"))
    if resources:
        query["resources"] = list(resources.values())
    return query


def bind(model, types, query):
    commands = {c["token"] for c in model["commands"]}
    if query["id"] in commands:
        require("amendment" in query and query["amendment"]["base"] == listing(model, types, query["id"]), "Existing listing amendment must bind exact preserved behavior")
    capabilities = {c["id"]: c for c in model["capabilities"]}
    for r in query.get("resources", []):
        require(capabilities.get(r["capability"], {}).get("kind") == "utc_clock", "Query operand binds declared UTC clock capability only")
