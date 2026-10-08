"""Bounded typed computation graph: explicit dependencies, no embedded expressions."""
import copy

from .references import keys, require, validate_atom, erase
from .predicates import same_type
from .mutable_values import valid_value

INTEGER = dict(type="integer", domain=[])
TIME = dict(type="timestamp", domain=[])
DURATION = dict(type="duration", domain=[], unit="seconds")
POLICY = dict(integer_domain="signed_64", overflow="reject", snapshot="operation_before", rejection="unchanged")


def validate(graph, types, entity, parameters, resources=None, images=("before",)):
    keys(graph, ("nodes", "policy"))
    require(graph["policy"] == POLICY, "Explicit signed-64/overflow/snapshot/atomic policy")
    nodes = graph["nodes"]
    require(type(nodes) is list and 1 <= len(nodes) <= 16, "1..16 local computations")
    env = {}
    for node in nodes:
        require(type(node) is dict and type(node.get("binding")) is str and bool(node["binding"]) and node["binding"] not in env, "Unique explicit result binding")
        require(node.get("operator") in ("value", "add", "shift_utc_seconds", "refine_integer", "refine_instant", "days_to_seconds"), "Closed deterministic operators")
        op = node["operator"]
        keys(node, ("binding", "operator", "type", "operands", "depends_on", "error") + (("null",) if op in ("refine_integer", "refine_instant") else ()) + (("conversion",) if op == "days_to_seconds" else ()))
        require(type(node["error"]) is str and bool(node["error"]), "Declared computation failure")
        args = node["operands"]
        require(type(args) is list and len(args) == (1 if op in ("value", "refine_integer", "refine_instant", "days_to_seconds") else 2), "Exact operand arity")
        deps = []
        for s in args:
            k = s.get("kind")
            if k == "cardinality":
                keys(s, ("kind", "type", "selection"))
                require(s["type"] == INTEGER, "Cardinality is signed-64 integer; overflow rejects")
                sel = s["selection"]
                keys(sel, ("entity", "binding", "predicate"))
                require(sel["entity"] in types and sel["binding"] != "primary", "Explicit finite cardinality domain")
                validate_atom(sel["predicate"], types, {"primary": entity, sel["binding"]: sel["entity"]} if "before" in images else {sel["binding"]: sel["entity"]}, parameters)
            else:
                require(k in ("literal", "parameter", "before", "after", "resource", "computed"), "No ambient or executable operands")
                keys(s, ("kind", "type", "value") if k == "literal" else ("kind", "type", "name"))
                if k == "literal":
                    require(valid_value(s["value"], erase(s["type"])), "Typed literal operand")
                else:
                    require(k not in ("before", "after") or k in images, "Available declared image")
                    source = parameters if k == "parameter" else (resources or {}) if k == "resource" else env if k == "computed" else types[entity]
                    require(s["name"] in source and same_type(source[s["name"]], s["type"]), "Explicit typed operand binding; acyclic graph")
                    if k == "computed" and s["name"] not in deps: deps.append(s["name"])
        require(type(node["depends_on"]) is list and len(set(node["depends_on"])) == len(node["depends_on"]) and set(node["depends_on"]) == set(deps), "Exact dependencies, topologically declared; no imperative sequencing")
        expected = [TIME, DURATION] if op == "shift_utc_seconds" else [dict(type="integer", domain=[], nullable=True)] if op == "refine_integer" else [{**TIME, "nullable": True}] if op == "refine_instant" else [INTEGER] * len(args)
        result_type = TIME if op in ("shift_utc_seconds", "refine_instant") else DURATION if op == "days_to_seconds" else INTEGER
        require(all(same_type(a["type"], t) for a, t in zip(args, expected)) and same_type(node["type"], result_type), "Exact operator operand/result types; no coercion")
        if op in ("refine_integer", "refine_instant"):
            policy = node["null"]
            require(policy == dict(policy="reject") or (type(policy) is dict and set(policy) == {"policy", "value"} and policy["policy"] == "literal" and valid_value(policy["value"], result_type)), "Source-authorized null rejection or literal fallback")
        if op == "days_to_seconds":
            require(node["conversion"] == dict(source="elapsed_days", target="elapsed_seconds", seconds_per_day=86400, negative="preserve", overflow="reject"), "Exact dimensioned conversion, no general multiplication")
        env[node["binding"]] = copy.deepcopy(node["type"])
    return env


def bound(source, env, target):
    keys(source, ("kind", "type", "name"))
    widened = target.get("nullable") is True and not source["type"].get("nullable", False) and same_type(source["type"], {**target, "nullable": False})
    require(source["kind"] == "computed" and source["name"] in env and same_type(env[source["name"]], source["type"]) and (same_type(source["type"], target) or widened), "Bound computed consumption; only nonnull-to-nullable target widening")
