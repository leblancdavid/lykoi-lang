"""Normal FRC/V1 CollectionQuery profile. No natural-language interpretation.

The formalizer owns interpretation; this module validates the resulting facts.
R5.98 semantic machinery and historical envelopes remain unchanged.
"""
import copy
import re

from air_compiler.collection_query import FACETS, QueryError, validate as query_validate
from benchmark.evaluation import formal_requirements_r5_80 as frc
from lykoi_controller import Failure
from lykoi_query import contracts as query

PROFILE = query.PROFILE
V1 = "LykoiContractV1"


def typed(relation):
    p = relation.get("parameters", {})
    return relation.get("kind") == "filter_order" and bool(set(p) & {"query", "facet", "value"})


def applies(contract):
    return any(typed(o["relation"]) for o in contract["obligations"])


def selected(contract):
    """Explicit normal V1 selection preserves older prospective FRC routing."""
    return applies(contract) and contract["context"]["domains"].get("capability_profile") == PROFILE


def validate_relations(contract):
    """Validate the profile's complete groups; omissions are explicit null policies.

    Nonquery obligations remain in the FRC and are refused by structural coverage.
    Missing/duplicate query facets are invalid formalizer output, never defaults.
    """
    frc.validate(contract)
    groups = {}
    for o in contract["obligations"]:
        r = o["relation"]
        if not typed(r):
            continue
        p = r["parameters"]
        if (set(p) != {"query", "facet", "value"} or type(p["query"]) is not str
                or not re.fullmatch(r"[a-z][a-z0-9_-]*", p["query"]) or p["facet"] not in FACETS):
            raise Failure("INVALID_TYPED_QUERY_RELATION", obligation=o["id"])
        group = groups.setdefault(p["query"], {"id": p["query"]})
        if p["facet"] in group:
            raise Failure("DUPLICATE_QUERY_FACET", obligation=o["id"])
        group[p["facet"]] = copy.deepcopy(p["value"])
    for group in groups.values():
        try:
            query_validate(group)
        except (QueryError, TypeError, KeyError, ValueError) as exc:
            raise Failure("INVALID_TYPED_QUERY_RELATION", reason=str(exc)) from exc
    return groups


def meaning_equal(candidate, interpretation):
    """Only closed typed relations can disregard a display description difference."""
    if typed(candidate["relation"]):
        return (type(interpretation) is dict and set(interpretation) == {"statement", "relation"}
                and type(interpretation["statement"]) is str and bool(interpretation["statement"].strip())
                and candidate["relation"] == interpretation["relation"])
    return interpretation == {k: candidate[k] for k in ("statement", "relation")}


def storage(contract):
    """Storage authority is normal FRC context, reviewed by source-side domains.

    No automatic task-model inference. Model state reads use the existing model's
    validator; a typed query view can expose only supported nonnullable fields.
    """
    value = copy.deepcopy(contract["context"]["domains"].get("collection_store", {"kind": "json_array"}))
    if value == {"kind": "json_array"}:
        return value
    if type(value) is not dict or set(value) != {"kind", "model", "state"} or value["kind"] != "model_state":
        raise Failure("UNSUPPORTED_COLLECTION_STORE")
    from air_compiler.profiles import validate_storage
    validate_storage(value, list(validate_relations(contract).values()))
    return value


def structural(contract, fid):
    # Native query projection consumes semantic values only. Never source text.
    try:
        validate_relations(contract)
        storage(contract)
    except Failure as exc:
        p = query.structural(contract, frc.digest(contract))
        p["source_frc"] = fid
        p["unsupported"] = sorted(set(p["unsupported"] + ["@query-profile"]))
        p["profile_failure"] = exc.as_dict()
        return p
    p = query.structural(contract, frc.digest(contract))
    p["source_frc"] = fid
    return p


def coverage(contract, projection):
    expected = structural(contract, projection["source_frc"])
    if projection != expected or expected["unsupported"]:
        raise Failure("STRUCTURAL_COVERAGE_FAILURE", unsupported=expected["unsupported"],
                      reason=expected.get("profile_failure", "Incomplete/stale query projection"))
    canonical_projection = copy.deepcopy(projection)
    canonical_projection["source_frc"] = frc.digest(contract)
    return query.coverage(contract, canonical_projection)


def bdi(contract, projection):
    coverage(contract, projection)
    p = copy.deepcopy(projection)
    p["source_frc"] = frc.digest(contract)
    return query.bdi(contract, p)


def adequate(contract, discovered):
    result = query.adequate(contract, discovered)
    result["outcome"] = "ADEQUATE" if result["outcome"] == "IMPLEMENTATION_ADEQUATE" else result["outcome"]
    return result


def faithful_v1(contract):
    if not selected(contract):
        raise Failure("UNREPRESENTABLE_SOURCE", gap="QUERY_PROFILE_NOT_SELECTED")
    validate_relations(contract)
    p = structural(contract, frc.digest(contract))
    coverage(contract, p)
    doc = query.document(contract, p)
    normal = {"schema_version": V1, "profile": PROFILE, "document": doc, "storage": storage(contract)}
    return {"version": V1, "profile": PROFILE, "outcome": "FAITHFUL_COMPLETE", "document": normal,
            "normalized": copy.deepcopy(normal),
            "coverage": [{"frc_id": o["id"], "v1_id": o["id"]} for o in contract["obligations"]]}


def recover(normal):
    if (type(normal) is not dict or set(normal) != {"schema_version", "profile", "document", "storage"}
            or normal["schema_version"] != V1 or normal["profile"] != PROFILE):
        raise QueryError("Unsupported normal V1 profile")
    contract = query.recover(normal["document"])
    if faithful_v1(contract)["normalized"] != normal:
        raise QueryError("Unfaithful normal V1 profile")
    return contract


def formalizer_guidance():
    return ("CollectionQuery profile collection-query-1: emit normal filter_order obligations with "
            "parameters exactly {query,facet,value}, one per facet: " + ", ".join(FACETS) + ". "
            "Select context domains capability_profile=collection-query-1 for the normal V1 extension. "
            "Typed values are semantic authority; statement is display prose. Interpret source once. "
            "Use string equals or string-collection contains with parameter/constant references; "
            "explicit sensitive/casefold and none/strip; ordered ASC/DESC keys including unique identity; "
            "nonempty/nonblank validation with declared error; inclusion all/equals; read_only/unchanged "
            "or distinguishable mutating/write frame; collection zero_or_more result empty/null/error. "
            "Do not guess policies: unresolved material policy is null plus blocking question/issue. "
            "Explicit finite policy freedom uses {freedom:[alternatives]}. Retain unsupported obligations. "
            "Only source, clarification or approved project policy can authorize a fact. Source inventory "
            "independently extracts typed relations; its descriptions need not match candidate prose.")
