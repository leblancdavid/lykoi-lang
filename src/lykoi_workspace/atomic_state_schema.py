"""Closed producer schema for ordinary coupled typed record creation."""
from .query_schema import obj, array, TEXT, VALUES
from .predicate_schema import tree, TYPE as QUERY_TYPE
from .reference_schema import TYPE
from .predicate_schema import VALUE


def schema():
    source = {"anyOf": [obj({"kind": {"enum": ["literal"]}, "type": TYPE, "value": VALUE}), obj({"kind": {"enum": ["parameter", "before", "after", "resource", "computed"]}, "type": TYPE, "name": TEXT})]}
    source["anyOf"].append(obj({"kind": {"enum": ["created"]}, "type": TYPE, "effect": TEXT, "entity": TEXT, "field": TEXT, "alternative": {"anyOf": [{"type": "null"}, obj({"kind": {"enum": ["literal"]}, "type": TYPE, "value": VALUE})]}}))
    q = obj({"id": TEXT, **VALUES})
    q["properties"].update(source=obj({"collection": TEXT, "fields": {"type": "object", "additionalProperties": QUERY_TYPE}, "unique_key": TEXT}), parameters={"type": "object", "additionalProperties": QUERY_TYPE}, predicate=tree(), comparison=obj({"scope": {"enum": ["predicate_nodes"]}}))
    result = obj({"operations": array(obj({"command": TEXT, "entity": TEXT, "parameters": {"type": "object", "additionalProperties": TYPE}, "resources": array(obj({"name": TEXT, "type": TYPE, "capability": TEXT})), "on": {"enum": ["success"]}, "sampling": {"enum": ["once_per_operation"]}, "ordering": {"enum": ["declared_creation_occurrence"]}, "creations": array(obj({"entity": TEXT, "bindings": {"type": "object", "additionalProperties": obj({"source": source, "invalid_error": TEXT})}, "duplicate_error": TEXT}))})), "queries": array(q), "append_only": array(TEXT), "commit": obj({"scope": {"enum": ["one_store"]}, "mutation": {"enum": ["bounded_records"]}, "isolation": {"enum": ["exclusive_operation"]}, "rejection": {"enum": ["unchanged"]}})})
    from .computation_schema import graph
    result["properties"]["operations"]["items"]["properties"]["computations"] = graph(TYPE, VALUE)
    result["properties"]["operations"]["items"]["properties"]["resources"]["items"]["properties"]["observation"] = {"enum": ["operation", "binding"]}
    from .reference_schema import condition
    creation = result["properties"]["operations"]["items"]["properties"]["creations"]["items"]
    creation["properties"].update(binding=TEXT, when={"anyOf": [{"type": "null"}, condition()]}, depends_on=array(TEXT), computations=graph(TYPE, VALUE))
    return result
