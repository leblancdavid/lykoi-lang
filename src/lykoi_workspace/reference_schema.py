"""Closed typed reference facets for FRC producers; no downstream prose parsing."""
from .query_schema import obj, array, TEXT
from .predicate_schema import VALUE, POLICY, TYPE as OLD_TYPE
from functools import lru_cache

IDENTITY = obj({"type": {"enum": ["identifier"]}, "domain": array(TEXT), "entity": TEXT})
TYPE = {"anyOf": [OLD_TYPE, IDENTITY, obj({"type": {"enum": ["collection"]}, "element": IDENTITY, "ordering": {"enum": ["insertion"]}, "duplicates": {"enum": ["allow", "unique"]}, "equality": {"enum": ["exact"]}})]}
OPERAND = {"anyOf": [obj({"kind": {"enum": ["field", "parameter"]}, "name": TEXT, "type": TYPE}), obj({"kind": {"enum": ["literal"]}, "type": TYPE, "value": VALUE})]}
SOURCE = OPERAND
ERROR = {"anyOf": [TEXT, {"type": "null"}]}


@lru_cache(maxsize=None)
def condition(selection=True):
    alternatives = [obj({"kind": {"enum": ["compare", "member"]}, "result_type": {"enum": ["boolean"]}, "operator": {"enum": ["eq", "lt", "le", "gt", "ge", "in"]}, "left": OPERAND, "right": OPERAND, "policy": POLICY, "nulls": {"enum": ["false"]}}), obj({"kind": {"enum": ["is_null", "present"]}, "result_type": {"enum": ["boolean"]}, "operand": OPERAND})]
    if selection:
        alternatives += [obj({"kind": {"enum": ["extent"]}, "result_type": {"enum": ["boolean"]}, "selection": obj({"entity": TEXT, "binding": TEXT, "predicate": {"type": "object"}}), "relation": {"enum": ["eq", "ge"]}, "value": {"type": "integer"}}), obj({"kind": {"enum": ["reachable"]}, "result_type": {"enum": ["boolean"]}, "entity": TEXT, "field": TEXT, "source": OPERAND, "target": OPERAND, "paths": {"enum": ["nonempty"]}})]
    # Native validation below visits every closed node, without exponentially
    # unrolling the schema into the existing nonrecursive schema-checking API.
    child = {"type": "object"}
    alternatives += [obj({"kind": {"enum": ["and", "or"]}, "result_type": {"enum": ["boolean"]}, "children": array(child)}), obj({"kind": {"enum": ["not"]}, "result_type": {"enum": ["boolean"]}, "child": child})]
    return {"anyOf": alternatives}


@lru_cache(maxsize=1)
def schema():
    fields = {"type": "object", "additionalProperties": TYPE}
    parameter = obj({"type": TYPE, "flag": TEXT, "encoding": {"enum": ["text", "json"]}, "missing_error": TEXT, "invalid_error": TEXT})
    policy = obj({"policy": {"enum": ["required", "unchecked", "restrict", "permit", "unavailable"]}, "error": ERROR})
    guard = obj({"predicate": condition(), "error": TEXT})
    return obj({"primary": TEXT,
        "entities": array(obj({"name": TEXT, "key": TEXT, "fields": fields, "initial": array({"type": "object", "additionalProperties": VALUE})})),
        "references": array(obj({"entity": TEXT, "field": TEXT, "target": TEXT, "existence": policy, "deletion": policy, "migration": {"anyOf": [{"type": "null"}, obj({"when": {"enum": ["missing_or_empty"]}, "value": VALUE})]}})),
        "operations": array(obj({"command": TEXT, "entity": TEXT, "kind": {"enum": ["create", "update", "delete", "list"]}, "parameters": {"type": "object", "additionalProperties": parameter}, "lookup": ERROR, "missing_error": ERROR, "duplicate_error": ERROR, "changes": array(obj({"field": TEXT, "source": SOURCE, "operation": {"enum": ["replace", "append", "add_unique", "remove"]}, "invalid_error": TEXT})), "guards": array(guard), "order": array(TEXT)})),
        "guards": array(obj({"command": TEXT, "parameters": fields, "predicate": condition(), "error": TEXT})),
        "commit": obj({"scope": {"enum": ["one_store"]}, "mutation": {"enum": ["one_record"]}, "isolation": {"enum": ["exclusive_operation"]}, "rejection": {"enum": ["unchanged"]}})})


def validate_value(value):
    from lykoi_rehearsal.adapters import check_schema
    from air_compiler.references import require
    check_schema(value, schema())
    def tree(t, selection=True, depth=0):
        require(depth < 24, "Bounded producer condition depth")
        check_schema(t, condition(selection))
        if t["kind"] in ("and", "or"):
            for c in t["children"]: tree(c, selection, depth + 1)
        elif t["kind"] == "not": tree(t["child"], selection, depth + 1)
        elif t["kind"] == "extent": tree(t["selection"]["predicate"], False, depth + 1)
    for g in value["guards"]: tree(g["predicate"])
    for op in value["operations"]:
        for g in op["guards"]: tree(g["predicate"])
