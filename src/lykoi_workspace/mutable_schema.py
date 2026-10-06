"""Closed typed producer relations for normal mutable-value composition."""
from .query_schema import obj, array, TEXT

SCALAR = {"anyOf": [TEXT, {"type": "null"}]}
VALUE = {"anyOf": [TEXT, {"type": "null"}, array(TEXT)]}
ELEMENT_PIPELINE = array({"anyOf": [
    obj({"kind": {"enum": ["transform"]}, "operation": {"enum": ["verbatim", "trim", "stable_deduplicate"]}}),
    obj({"kind": {"enum": ["validate"]}, "rule": {"enum": ["nonempty", "nonblank", "typed"]}, "error": TEXT})]})
PIPELINE = array({"anyOf": ELEMENT_PIPELINE["items"]["anyOf"] + [obj({"kind": {"enum": ["map_elements"]}, "pipeline": ELEMENT_PIPELINE})]})
VALUES = {
    "collections": array(obj({"name": TEXT, "element": obj({"type": {"enum": ["string", "identifier", "enum", "timestamp"]}, "domain": array(TEXT)}),
        "ordering": {"enum": ["insertion"]}, "duplicates": {"enum": ["allow", "unique"]}, "equality": {"enum": ["exact"]},
        "creation": obj({"input": TEXT, "encoding": {"enum": ["json", "repeated"]}, "default": array(TEXT), "pipeline": PIPELINE, "error": TEXT}),
        "migration": array(obj({"from": {"type": "integer"}, "to": {"type": "integer"}, "value": array(TEXT)}))})),
    "mutations": array(obj({"command": TEXT, "lookup": TEXT, "missing_error": TEXT,
        "changes": array(obj({"field": TEXT, "input": TEXT, "operation": {"enum": ["replace", "append", "add_unique"]},
            "omitted": {"enum": ["unchanged", "reject"]}, "missing_error": SCALAR, "pipeline": PIPELINE, "invalid_error": TEXT})),
        "guards": array(obj({"field": TEXT, "value": VALUE, "error": TEXT})),
        "effect": obj({"atomicity": {"enum": ["single_record"]}, "persistence": {"enum": ["atomic"]}, "rejection": {"enum": ["unchanged"]}})})),
    "creation_pipelines": array(obj({"field": TEXT, "pipeline": PIPELINE, "error": TEXT})),
}


def relation_schema():
    from lykoi_pipeline.mutable_profile import PROFILE
    return {"anyOf": [obj({"kind": {"enum": ["crud"]}, "parameters": obj({"profile": {"enum": [PROFILE]}, "facet": {"enum": [facet]}, "value": schema})}) for facet, schema in VALUES.items()]}


def validate_output(output):
    from lykoi_pipeline.mutable_profile import typed
    from lykoi_rehearsal.adapters import check_schema
    for o in output["obligations"]:
        if typed(o["relation"]):
            check_schema(o["relation"], relation_schema())
