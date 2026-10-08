"""Closed historical authority projection, separate from creation bindings."""
from .query_schema import obj, array, TEXT
from .reference_schema import TYPE, SOURCE
from .predicate_schema import VALUE
from .computation_schema import graph


def schema():
    source = {"anyOf": [SOURCE, obj({"kind": {"enum": ["before"]}, "name": TEXT, "type": TYPE})]}
    return obj({"steps": array(obj({"from": {"type": "integer"}, "to": {"type": "integer"}, "entities": array(obj({"entity": TEXT, "add_fields": array(obj({"field": TEXT, "source": source})), "computations": {"anyOf": [{"type": "null"}, graph(TYPE, VALUE)]}}))})), "invalid": {"enum": ["invalid_state"]}, "rejection": {"enum": ["unchanged"]}, "preservation": {"enum": ["unrelated_fields"]}})
