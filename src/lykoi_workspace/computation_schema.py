"""Closed computation producer schema; semantic validation checks all bindings."""
from .query_schema import obj, array, TEXT


def graph(typ, value):
    operand = {"anyOf": [obj({"kind": {"enum": ["literal"]}, "type": typ, "value": value}), obj({"kind": {"enum": ["parameter", "before", "after", "resource", "computed"]}, "type": typ, "name": TEXT}), obj({"kind": {"enum": ["cardinality"]}, "type": typ, "selection": obj({"entity": TEXT, "binding": TEXT, "predicate": {"type": "object"}})})]}
    node = obj({"binding": TEXT, "operator": {"enum": ["value", "add", "shift_utc_seconds", "refine_integer", "refine_instant", "days_to_seconds"]}, "type": typ, "operands": array(operand), "depends_on": array(TEXT), "error": TEXT})
    node["properties"].update(null={"anyOf": [obj({"policy": {"enum": ["reject"]}}), obj({"policy": {"enum": ["literal"]}, "value": value})]}, conversion=obj({"source": {"enum": ["elapsed_days"]}, "target": {"enum": ["elapsed_seconds"]}, "seconds_per_day": {"enum": [86400]}, "negative": {"enum": ["preserve"]}, "overflow": {"enum": ["reject"]}}))
    return obj({"nodes": array(node), "policy": obj({"integer_domain": {"enum": ["signed_64"]}, "overflow": {"enum": ["reject"]}, "snapshot": {"enum": ["operation_before"]}, "rejection": {"enum": ["unchanged"]}})})
