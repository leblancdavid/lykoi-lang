"""Prospective Lykoi CollectionQuery-0.1 validation and deterministic backend.

Independent of the compatibility v0.3 task application. No executable predicates.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

VERSION = "CollectionQuery-0.1"
FACETS = ("source", "parameters", "predicate", "comparison", "ordering",
          "validation", "inclusion", "effect", "result")
INTERFACES = ("amendment", "preconditions", "resources", "parameter_errors")
POLICIES = ("comparison", "ordering", "validation", "inclusion", "effect", "result")


class QueryError(ValueError):
    pass


def require(value, reason):
    if not value:
        raise QueryError(reason)


def keys(value, names):
    require(type(value) is dict and set(value) == set(names), "Unknown/missing query fields: " + str(names))


def text(value):
    return type(value) is str and bool(value.strip())


def validate(query, *, complete=False, occurrence_order=False):
    """None = omission; {freedom: [...]} = explicit finite policy freedom.

    Structures with omission are representable but not executable. Mutating frames
    are representable for analysis but this read-only backend refuses them.
    """
    if type(query) is dict and query.get("predicate", {}).get("result_type") == "boolean":
        from .predicate_integration import validate_query
        return validate_query(query, complete, occurrence_order=occurrence_order)
    keys(query, ("id", *FACETS))
    require(text(query["id"]), "Empty query identity")
    keys(query["source"], ("collection", "fields", "unique_key"))
    source = query["source"]
    fields = source["fields"]
    require(text(source["collection"]) and type(fields) is dict and fields, "Invalid collection")
    require(all(text(k) and v in ("string", "integer", "boolean", "strings")
                for k, v in fields.items()), "Unsupported record field type")
    require(source["unique_key"] in fields and fields[source["unique_key"]] in ("string", "integer"),
            "Scalar unique identity required")
    params = query["parameters"]
    require(type(params) is dict and params and all(type(k) is str and re.fullmatch(r"[a-z][a-z0-9_]*", k)
                and k != "store" and v == "string" for k, v in params.items()),
            "Only declared string parameters supported")
    pred = query["predicate"]
    keys(pred, ("field", "operator", "operand"))
    require(pred["field"] in fields and pred["operator"] in ("equals", "contains"), "Unsupported predicate")
    require(fields[pred["field"]] == ("strings" if pred["operator"] == "contains" else "string"),
            "Predicate/field type mismatch")
    operand = pred["operand"]
    require(type(operand) is dict and len(operand) == 1, "Invalid operand")
    require((set(operand) == {"parameter"} and operand["parameter"] in params) or
            (set(operand) == {"constant"} and type(operand["constant"]) is str), "Unbound operand")

    def policy(name, value):
        if name == "comparison":
            keys(value, ("case", "normalization"))
            require(value["case"] in ("sensitive", "casefold") and value["normalization"] in ("none", "strip"),
                    "Unsupported comparison policy")
        elif name == "ordering":
            if occurrence_order and value == []:
                return
            require(type(value) is list and bool(value), "Nonempty key sequence required")
            seen = set()
            for key in value:
                keys(key, ("field", "direction"))
                require(key["field"] in fields and fields[key["field"]] != "strings" and
                        key["direction"] in ("ASC", "DESC") and key["field"] not in seen,
                        "Invalid ordering key")
                seen.add(key["field"])
            require(source["unique_key"] in seen, "Deterministic ordering needs unique tie-break key")
        elif name == "validation":
            require(type(value) is list, "Invalid validation rules")
            seen = set()
            for rule in value:
                keys(rule, ("parameter", "rule", "error"))
                require(rule["parameter"] in params and rule["rule"] in ("nonempty", "nonblank") and
                        text(rule["error"]) and rule["parameter"] not in seen, "Invalid validation rule")
                seen.add(rule["parameter"])
        elif name == "inclusion":
            require(type(value) is list, "Invalid inclusion policy")
            seen = set()
            for rule in value:
                require(type(rule) is dict and rule.get("mode") in ("all", "equals"), "Unsupported inclusion")
                keys(rule, ("field", "mode") if rule["mode"] == "all" else ("field", "mode", "value"))
                require(rule["field"] in fields and rule["field"] != pred["field"] and
                        rule["field"] not in seen, "Invalid inclusion dimension")
                seen.add(rule["field"])
                if rule["mode"] == "equals":
                    require(valid_value(rule["value"], fields[rule["field"]]), "Inclusion value type mismatch")
        elif name == "effect":
            keys(value, ("state", "persistence"))
            require(value in ({"state": "read_only", "persistence": "unchanged"},
                              {"state": "mutating", "persistence": "write"}), "Inconsistent effect frame")
        elif name == "result":
            require(type(value) is dict and value.get("no_match") in ("empty", "null", "error"), "Invalid no-match result")
            keys(value, ("shape", "cardinality", "no_match", "error") if value["no_match"] == "error"
                 else ("shape", "cardinality", "no_match"))
            require(value["shape"] == "collection" and value["cardinality"] == "zero_or_more", "Unsupported result shape")
            require(value["no_match"] != "error" or text(value["error"]), "Missing no-match error")

    for name in POLICIES:
        value = query[name]
        if value is None:
            require(not complete, "Omitted policy: " + name)
        elif type(value) is dict and "freedom" in value:
            keys(value, ("freedom",))
            require(not complete, "Unresolved explicit freedom: " + name)
            values = value["freedom"]
            require(type(values) is list and len(values) > 1, "Finite freedom requires alternatives")
            require(len({canonical(v) for v in values}) == len(values), "Duplicate freedom alternative")
            for choice in values:
                policy(name, choice)
        else:
            policy(name, value)
    if complete:
        require(query["effect"] == {"state": "read_only", "persistence": "unchanged"},
                "Read-only backend cannot lower mutating frame")
    return copy.deepcopy(query)


def valid_value(value, kind):
    return ((kind == "string" and type(value) is str) or
            (kind == "integer" and type(value) is int) or
            (kind == "boolean" and type(value) is bool) or
            (kind == "strings" and type(value) is list and all(type(x) is str for x in value)))


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def generate(query):
    model = validate(query, complete=True)
    runtime = Path(__file__).with_name("collection_query_runtime.py").read_text(encoding="utf-8")
    runtime = Path(__file__).with_name("predicate_runtime.py").read_text(encoding="utf-8") + "\n" + runtime
    return "# Generated by Lykoi CollectionQuery-0.1; do not edit.\n" + runtime + (
        "\nif __name__ == '__main__':\n    main(" + repr(model) + ")\n")
