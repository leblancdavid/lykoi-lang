"""Closed normal producer schema for already-existing writable scalar semantics."""
from .query_schema import obj, array, TEXT

VALUE = {"anyOf": [TEXT, {"type": "null"}]}
DEFAULT = {"anyOf": [{"type": "null"}, obj({"value": VALUE, "trigger": {"enum": ["omitted"]}, "boundary": {"enum": ["creation"]}})]}
VALUES = {
    "storage": obj({"path": TEXT, "version": {"type": "integer"}, "missing": {"enum": ["empty_collection"]}, "write": {"enum": ["atomic"]}, "rejection": {"enum": ["unchanged"]}}),
    "fields": array(obj({"name": TEXT, "type": {"enum": ["string", "identifier", "enum", "timestamp"]}, "domain": array(TEXT), "nullable": {"type": "boolean"}, "preservation": {"enum": ["verbatim"]}})),
    "creation": obj({"command": TEXT, "bindings": array(obj({"field": TEXT, "source": {"enum": ["input", "literal", "uuid_v4", "utc_clock"]}, "value": VALUE, "default": DEFAULT})),
                     "validation": array(obj({"field": TEXT, "rule": {"enum": ["nonblank", "timestamp_utc"]}, "error": TEXT}))}),
    "listing": obj({"command": TEXT, "order": array(TEXT), "result": {"enum": ["whole_records"]}}),
    "lifecycle": array(obj({"field": TEXT, "initial": VALUE, "source": VALUE, "target": VALUE, "command": TEXT, "missing_error": TEXT, "transition_error": TEXT, "rejection": {"enum": ["unchanged"]}})),
    "evolution": array(obj({"from": {"type": "integer"}, "to": {"type": "integer"}, "defaults": {"type": "object", "additionalProperties": VALUE}, "boundary": {"enum": ["explicit_migration"]}, "preservation": {"enum": ["unrelated_fields"]}})),
}


def relation_schema():
    from lykoi_pipeline.scalar_profile import PROFILE
    return {"anyOf": [obj({"kind": {"enum": ["crud"]}, "parameters": obj({"profile": {"enum": [PROFILE]}, "facet": {"enum": [facet]}, "value": schema})}) for facet, schema in VALUES.items()]}


def validate_output(output):
    from lykoi_rehearsal.adapters import check_schema
    from lykoi_pipeline.scalar_profile import typed
    for o in output["obligations"]:
        if typed(o["relation"]):
            check_schema(o["relation"], relation_schema())
