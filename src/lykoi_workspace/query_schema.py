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
    from .predicate_schema import tree, TYPE
    values = dict(VALUES)
    values["source"] = {"anyOf": [SOURCE, obj({"collection": TEXT, "fields": {"type": "object", "additionalProperties": TYPE}, "unique_key": TEXT})]}
    values["parameters"] = {"anyOf": [PARAMETERS, {"type": "object", "additionalProperties": TYPE}]}
    values["predicate"] = {"anyOf": [PREDICATE, tree()]}
    values["comparison"] = {"anyOf": [VALUES["comparison"], obj({"scope": {"enum": ["predicate_nodes"]}})]}
    base_values = dict(values)
    values["preconditions"] = array(obj({"predicate": tree(), "error": TEXT, "stage": {"enum": ["before_selection"]}, "rejection": {"enum": ["unchanged"]}}))
    values["resources"] = array(obj({"name": TEXT, "type": TYPE, "capability": TEXT, "sampling": {"enum": ["once_per_query"]}}))
    values["parameter_errors"] = {"type": "object", "additionalProperties": obj({"missing": {"anyOf": [TEXT, obj({"kind": {"enum": ["cli_rejection"]}})]}, "invalid": TEXT})}
    base = obj({"id": TEXT, **values})
    base["required"] = ["id", *base_values]
    values["amendment"] = obj({"base": base, "composition": {"enum": ["and", "or", "replace"]}, "predicate": tree()})
    alternatives = []
    for facet, schema in values.items():
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
