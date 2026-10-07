"""Closed computation producer schema; semantic validation checks all bindings."""
from .query_schema import obj, array, TEXT


def graph(typ, value):
    operand = {"anyOf": [obj({"kind": {"enum": ["literal"]}, "type": typ, "value": value}), obj({"kind": {"enum": ["parameter", "before", "after", "resource", "computed"]}, "type": typ, "name": TEXT}), obj({"kind": {"enum": ["cardinality"]}, "type": typ, "selection": obj({"entity": TEXT, "binding": TEXT, "predicate": {"type": "object"}})})]}
    return obj({"nodes": array(obj({"binding": TEXT, "operator": {"enum": ["value", "add", "shift_utc_seconds"]}, "type": typ, "operands": array(operand), "depends_on": array(TEXT), "error": TEXT})), "policy": obj({"integer_domain": {"enum": ["signed_64"]}, "overflow": {"enum": ["reject"]}, "snapshot": {"enum": ["operation_before"]}, "rejection": {"enum": ["unchanged"]}})})
