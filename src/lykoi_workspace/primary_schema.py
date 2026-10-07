"""Closed normal producer relation for primary numeric and actor interfaces."""
from .query_schema import obj, array, TEXT
from .predicate_schema import TYPE, VALUE
from .reference_schema import TYPE as NOMINAL
from .mutable_schema import PIPELINE


def schema():
    creation = {"anyOf": [obj({"source": {"enum": ["literal"]}, "value": VALUE}), obj({"source": {"enum": ["input"]}, "input": TEXT, "pipeline": PIPELINE, "error": TEXT}), obj({"source": {"enum": ["input_default"]}, "input": TEXT, "pipeline": PIPELINE, "error": TEXT, "default": VALUE})]}
    return obj({"integers": array(obj({"name": TEXT, "type": TYPE, "creation": creation, "migration": array(obj({"from": {"type": "integer"}, "to": {"type": "integer"}, "value": VALUE}))})), "context_inputs": array(obj({"command": TEXT, "name": TEXT, "type": NOMINAL, "role": {"enum": ["actor"]}, "authority": {"enum": ["explicit_parameter"]}, "missing_error": TEXT, "invalid_error": TEXT}))})
