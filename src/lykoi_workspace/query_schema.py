"""Closed typed formalizer relation schema, consumed at the normal AI interface."""

TEXT = {"type": "string"}


def obj(properties):
    return {"type": "object", "properties": properties, "required": list(properties), "additionalProperties": False}


def array(items):
    return {"type": "array", "items": items}


SOURCE = obj({"collection": TEXT, "fields": {"type": "object", "additionalProperties": {"enum": ["string", "integer", "boolean", "strings"]}}, "unique_key": TEXT})
PARAMETERS = {"type": "object", "additionalProperties": {"enum": ["string"]}}
OPERAND = {"anyOf": [obj({"parameter": TEXT}), obj({"constant": TEXT})]}
PREDICATE = obj({"field": TEXT, "operator": {"enum": ["equals", "contains"]}, "operand": OPERAND})
VALUES = {
    "source": SOURCE,
    "parameters": PARAMETERS,
    "predicate": PREDICATE,
    "comparison": obj({"case": {"enum": ["sensitive", "casefold"]}, "normalization": {"enum": ["none", "strip"]}}),
    "ordering": array(obj({"field": TEXT, "direction": {"enum": ["ASC", "DESC"]}})),
    "validation": array(obj({"parameter": TEXT, "rule": {"enum": ["nonempty", "nonblank"]}, "error": TEXT})),
    "inclusion": array({"anyOf": [obj({"field": TEXT, "mode": {"enum": ["all"]}}),
                                     obj({"field": TEXT, "mode": {"enum": ["equals"]}, "value": {}})]}),
    "effect": {"anyOf": [obj({"state": {"enum": ["read_only"]}, "persistence": {"enum": ["unchanged"]}}),
                           obj({"state": {"enum": ["mutating"]}, "persistence": {"enum": ["write"]}})]},
    "result": {"anyOf": [obj({"shape": {"enum": ["collection"]}, "cardinality": {"enum": ["zero_or_more"]}, "no_match": {"enum": ["empty", "null"]}}),
                           obj({"shape": {"enum": ["collection"]}, "cardinality": {"enum": ["zero_or_more"]}, "no_match": {"enum": ["error"]}, "error": TEXT})]},
}


def relation_schema():
    from air_compiler.collection_query import POLICIES
    alternatives = []
    for facet, schema in VALUES.items():
        value = {"anyOf": [schema, {"type": "null"}, obj({"freedom": array(schema)})]} if facet in POLICIES else schema
        alternatives.append(obj({"kind": {"enum": ["filter_order"]}, "parameters": obj({
            "query": TEXT, "facet": {"enum": [facet]}, "value": value})}))
    return {"anyOf": alternatives}


def validate_output(output):
    from .scalar_schema import validate_output as validate_scalar
    from .mutable_schema import validate_output as validate_mutable
    validate_mutable(output)
    validate_scalar(output)
    from lykoi_rehearsal.adapters import check_schema
    from lykoi_pipeline.query_profile import typed
    for obligation in output["obligations"]:
        if typed(obligation["relation"]):
            check_schema(obligation["relation"], relation_schema())
