"""Closed typed producer relations for normal mutable-value composition."""
from .query_schema import obj, array, TEXT

SCALAR = {"anyOf": [TEXT, {"type": "null"}]}
VALUE = {"anyOf": [TEXT, {"type": "null"}, array(TEXT)]}
STAGE = {"enum": ["RAW", "TRANSFORMED", "PERSISTED"]}
WHEN = {"anyOf": [{"type": "null"}, obj({"stage": STAGE, "predicate": {"enum": ["present", "absent", "empty", "nonempty", "whitespace"]}})]}
from .predicate_schema import tree, semantics, TYPE as PREDICATE_TYPE
WHEN["anyOf"].append(tree())
ELEMENT_PIPELINE = array({"anyOf": [
    obj({"kind": {"enum": ["transform"]}, "operation": {"enum": ["verbatim", "trim", "stable_deduplicate"]}}),
    obj({"kind": {"enum": ["validate"]}, "rule": {"enum": ["nonempty", "nonblank", "typed"]}, "error": TEXT}),
    obj({"kind": {"enum": ["validate"]}, "rule": {"enum": ["nonempty", "nonblank", "typed"]}, "error": TEXT, "stage": STAGE, "when": WHEN})]})
PIPELINE = array({"anyOf": ELEMENT_PIPELINE["items"]["anyOf"] + [obj({"kind": {"enum": ["map_elements"]}, "pipeline": ELEMENT_PIPELINE})]})
VALUES = {
    "collections": array(obj({"name": TEXT, "element": obj({"type": {"enum": ["string", "identifier", "enum", "timestamp"]}, "domain": array(TEXT)}),
        "ordering": {"enum": ["insertion"]}, "duplicates": {"enum": ["allow", "unique"]}, "equality": {"enum": ["exact"]},
        "creation": {"anyOf": [obj({"input": TEXT, "encoding": {"enum": ["json", "repeated"]}, "default": array(TEXT), "pipeline": PIPELINE, "error": TEXT}), obj({"source": {"enum": ["input"]}, "input": TEXT, "encoding": {"enum": ["json", "repeated"]}, "pipeline": PIPELINE, "error": TEXT}), obj({"source": {"enum": ["literal"]}, "value": array(TEXT)})]},
        "migration": array(obj({"from": {"type": "integer"}, "to": {"type": "integer"}, "value": array(TEXT)}))})),
    "mutations": array(obj({"command": TEXT, "lookup": TEXT, "missing_error": TEXT,
        "changes": array({"anyOf": [obj({"field": TEXT, "input": TEXT, "operation": {"enum": ["replace", "append", "add_unique"]},
            "omitted": {"enum": ["unchanged", "reject"]}, "missing_error": SCALAR, "pipeline": PIPELINE, "invalid_error": TEXT}),
            obj({"field": TEXT, "source": obj({"kind": {"enum": ["literal"]}, "type": PREDICATE_TYPE, "value": {"anyOf": [VALUE, {"type": "boolean"}]}}), "operation": {"enum": ["replace"]}, "pipeline": PIPELINE, "invalid_error": TEXT})]}),
        "guards": array({"anyOf": [obj({"field": TEXT, "value": VALUE, "error": TEXT}), obj({"predicate": tree(), "error": TEXT})]}),
        "effect": obj({"atomicity": {"enum": ["single_record"]}, "persistence": {"enum": ["atomic"]}, "rejection": {"enum": ["unchanged"]}})})),
    "creation_pipelines": array(obj({"field": TEXT, "pipeline": PIPELINE, "error": TEXT})),
}
TYPE = obj({"type": {"enum": ["string", "identifier", "enum", "timestamp"]}, "domain": array(TEXT)})
NULLABLE_TYPE = obj({"type": {"enum": ["string", "identifier", "enum", "timestamp"]}, "domain": array(TEXT), "nullable": {"type": "boolean"}})
COLLECTION_TYPE = obj({"type": {"enum": ["collection"]}, "element": TYPE, "ordering": {"enum": ["insertion"]}, "duplicates": {"enum": ["allow", "unique"]}, "equality": {"enum": ["exact"]}})
VALUES["input_contracts"] = array(obj({"operation": TEXT, "parameter": TEXT,
    "type": {"anyOf": [TYPE, NULLABLE_TYPE, COLLECTION_TYPE, PREDICATE_TYPE]}, "presence": {"enum": ["required", "optional"]},
    "binding": obj({"source": {"enum": ["cli_flag"]}, "flag": TEXT, "encoding": {"enum": ["text", "json", "repeated"]}}),
    "missing": {"anyOf": [{"type": "null"}, obj({"kind": {"enum": ["application_error"]}, "error": TEXT}), obj({"kind": {"enum": ["cli_rejection"]}})]}}))
VALUES["predicate_semantics"] = semantics()


def relation_schema():
    from lykoi_pipeline.mutable_profile import PROFILE
    from .reference_schema import schema as reference_schema
    values = {**VALUES, "reference_semantics": reference_schema()}
    return {"anyOf": [obj({"kind": {"enum": ["crud"]}, "parameters": obj({"profile": {"enum": [PROFILE]}, "facet": {"enum": [facet]}, "value": schema})}) for facet, schema in values.items()]}


def validate_output(output):
    from lykoi_pipeline.mutable_profile import typed
    from lykoi_rehearsal.adapters import check_schema
    for o in output["obligations"]:
        if typed(o["relation"]):
            check_schema(o["relation"], relation_schema())
            if o["relation"]["parameters"]["facet"] == "reference_semantics":
                from .reference_schema import validate_value
                validate_value(o["relation"]["parameters"]["value"])
