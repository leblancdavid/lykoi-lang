"""Closed producer authority for prewrite predicates and trusted host sources."""
from .query_schema import obj, array, TEXT
from .reference_schema import TYPE, ERROR, condition


def schema():
    actor = obj({"name": TEXT, "type": TYPE, "source": {"enum": ["explicit_parameter", "trusted_context"]}, "context": ERROR, "missing_error": TEXT, "invalid_error": TEXT})
    operation = obj({"command": TEXT, "entity": TEXT, "lookup": ERROR, "actor": actor, "parameters": {"type": "object", "additionalProperties": TYPE}, "predicate": condition(), "error": TEXT, "observation": {"enum": ["committed_operation_before"]}, "rejection": {"enum": ["unchanged"]}})
    operation["properties"]["checks"] = array(obj({"predicate": condition(), "error": TEXT}))
    return obj({"operations": array(operation)})
