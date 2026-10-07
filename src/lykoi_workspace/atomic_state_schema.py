"""Closed producer schema for ordinary coupled typed record creation."""
from .query_schema import obj, array, TEXT, VALUES
from .predicate_schema import tree, TYPE as QUERY_TYPE
from .reference_schema import TYPE
from .predicate_schema import VALUE


def schema():
    source = {"anyOf": [obj({"kind": {"enum": ["literal"]}, "type": TYPE, "value": VALUE}), obj({"kind": {"enum": ["parameter", "before", "after", "resource"]}, "type": TYPE, "name": TEXT})]}
    q = obj({"id": TEXT, **VALUES})
    q["properties"].update(source=obj({"collection": TEXT, "fields": {"type": "object", "additionalProperties": QUERY_TYPE}, "unique_key": TEXT}), parameters={"type": "object", "additionalProperties": QUERY_TYPE}, predicate=tree(), comparison=obj({"scope": {"enum": ["predicate_nodes"]}}))
    return obj({"operations": array(obj({"command": TEXT, "entity": TEXT, "parameters": {"type": "object", "additionalProperties": TYPE}, "resources": array(obj({"name": TEXT, "type": TYPE, "capability": TEXT})), "on": {"enum": ["success"]}, "sampling": {"enum": ["once_per_operation"]}, "ordering": {"enum": ["declared_creation_occurrence"]}, "creations": array(obj({"entity": TEXT, "bindings": {"type": "object", "additionalProperties": obj({"source": source, "invalid_error": TEXT})}, "duplicate_error": TEXT}))})), "queries": array(q), "append_only": array(TEXT), "commit": obj({"scope": {"enum": ["one_store"]}, "mutation": {"enum": ["bounded_records"]}, "isolation": {"enum": ["exclusive_operation"]}, "rejection": {"enum": ["unchanged"]}})})
