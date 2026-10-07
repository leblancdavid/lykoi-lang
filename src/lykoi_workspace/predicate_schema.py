"""Closed bounded producer schema for typed conditions, not executable prose."""
from .query_schema import obj, array, TEXT

SCALAR = obj({"type": {"enum": ["string", "identifier", "enum", "boolean", "timestamp"]}, "domain": array(TEXT), "nullable": {"type": "boolean"}})
ELEMENT = obj({"type": {"enum": ["string", "identifier", "enum", "timestamp", "integer"]}, "domain": array(TEXT)})
TYPE = {"anyOf": [SCALAR, ELEMENT, obj({"type": {"enum": ["duration"]}, "domain": array(TEXT), "unit": {"enum": ["seconds"]}}), obj({"type": {"enum": ["collection"]}, "element": ELEMENT, "ordering": {"enum": ["insertion"]}, "duplicates": {"enum": ["allow", "unique"]}, "equality": {"enum": ["exact"]}})]}
VALUE = {"anyOf": [TEXT, {"type": "boolean"}, {"type": "integer"}, {"type": "null"}, array(TEXT)]}
OPERAND = {"anyOf": [obj({"kind": {"enum": ["field", "parameter", "resource"]}, "name": TEXT, "type": TYPE}), obj({"kind": {"enum": ["literal"]}, "type": TYPE, "value": VALUE}), obj({"kind": {"enum": ["value"]}, "type": TYPE, "stage": {"enum": ["RAW", "TRANSFORMED", "PERSISTED"]}})]}
POLICY = obj({"case": {"enum": ["sensitive", "casefold"]}, "normalization": {"enum": ["none", "strip"]}})


def tree(depth=4):
    atoms = [obj({"kind": {"enum": ["compare", "member"]}, "result_type": {"enum": ["boolean"]}, "operator": {"enum": ["eq", "lt", "le", "gt", "ge", "in"]}, "left": OPERAND, "right": OPERAND, "policy": POLICY, "nulls": {"enum": ["false"]}}), obj({"kind": {"enum": ["is_null", "present"]}, "result_type": {"enum": ["boolean"]}, "operand": OPERAND})]
    if depth:
        child = tree(depth - 1)
        atoms += [obj({"kind": {"enum": ["and", "or"]}, "result_type": {"enum": ["boolean"]}, "children": array(child)}), obj({"kind": {"enum": ["not"]}, "result_type": {"enum": ["boolean"]}, "child": child})]
    return {"anyOf": atoms}


def semantics():
    return obj({"booleans": array(obj({"name": TEXT, "creation": obj({"source": {"enum": ["literal"]}, "value": {"type": "boolean"}}), "migration": array(obj({"from": {"type": "integer"}, "to": {"type": "integer"}, "value": {"type": "boolean"}}))})), "guards": array(obj({"command": TEXT, "predicate": tree(), "error": TEXT, "rejection": {"enum": ["unchanged"]}})), "invariants": array(obj({"predicate": tree(), "error": TEXT}))})
