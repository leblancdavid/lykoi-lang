"""Bounded scalar-write + read-only CollectionQuery composition, R5.103.

The authority selects one scalar state, not independent models silently unioned.
Interactions are validated against the actual lowered store and command namespace.
"""
import copy

from . import scalar_profile as scalar, query_profile as query
from lykoi_controller import Failure

PROFILE = "existing-composed-1"


def applies(contract):
    return scalar.applies(contract) and query.applies(contract)


def split(contract):
    scalar.require(contract["context"]["domains"].get("capability_profile") == PROFILE, "Explicit bounded composition selection")
    binding = contract["context"]["domains"].get("collection_store")
    scalar.keys(binding, ("kind", "state"))
    scalar.require(binding["kind"] == "composed_scalar", "UNSUPPORTED_COMPOSITION: query must select the authorized scalar state")
    sc, qc = copy.deepcopy(contract), copy.deepcopy(contract)
    sc["obligations"] = [o for o in sc["obligations"] if scalar.typed(o["relation"])]
    qc["obligations"] = [o for o in qc["obligations"] if query.typed(o["relation"])]
    sc["context"]["domains"]["capability_profile"] = scalar.PROFILE
    qc["context"]["domains"]["capability_profile"] = query.PROFILE
    f = scalar.facts(sc)
    model = scalar.lower(f, sc["context"]["domains"].get("scalar_base_model"))
    if binding["state"] not in {s["id"] for s in model["state"]}:
        raise Failure("PROFILE_COMPOSITION_CONFLICT", reason="Selected state does not exist in the authorized scalar model")
    qc["context"]["domains"]["collection_store"] = {"kind": "model_state", "model": model, "state": binding["state"]}
    groups = query.validate_relations(qc)
    if set(groups) & {c["token"] for c in model["commands"]}:
        raise Failure("PROFILE_COMPOSITION_CONFLICT", reason="Query command contradicts an existing command authority")
    scalar.require(all(q["effect"] == {"state": "read_only", "persistence": "unchanged"} for q in groups.values()), "UNSUPPORTED_COMPOSITION: mutating query/write interaction")
    # Enforce model/view field kinds, nonnullable projection, uniqueness and no
    # command collision using the existing store adapter, not profile membership.
    store = query.storage(qc)
    return sc, qc, f, groups, store


def structural(contract, fid):
    try:
        sc, qc, f, groups, store = split(contract)
        sp, qp = scalar.structural(sc, fid), query.structural(qc, fid)
        scalar.coverage(sc, sp); query.coverage(qc, qp)
        rows = sp["rows"] + qp["rows"]
        unsupported = [o["id"] for o in contract["obligations"] if not (scalar.typed(o["relation"]) or query.typed(o["relation"]))]
        rows += [{"obligation": o["id"], "classification": "UNSUPPORTED", "relation": copy.deepcopy(o["relation"]), "operation": None, "justification": "Outside bounded composition"} for o in contract["obligations"] if o["id"] in unsupported]
        operations = sp["interface"]["operations"]
        facts = {"scalar": f, "queries": groups, "storage": store}
        reason = None
        classification = "UNSUPPORTED_COMPOSITION" if unsupported else "COMPATIBLE_COMPOSITION"
    except (Failure, ValueError, KeyError, TypeError) as exc:
        unsupported = [o["id"] for o in contract["obligations"]]
        rows = [{"obligation": o["id"], "classification": "UNSUPPORTED", "relation": copy.deepcopy(o["relation"]), "operation": None, "justification": "Composition has no qualified mapping"} for o in contract["obligations"]]
        operations, facts, reason = [], None, str(exc)
        classification = "CONFLICT" if isinstance(exc, Failure) and exc.code == "PROFILE_COMPOSITION_CONFLICT" else "UNSUPPORTED_COMPOSITION"
    return {"version": PROFILE, "source_frc": fid, "rows": rows, "facts": facts,
            "interface": {"version": scalar.discovery.VERSION_BDI, "operations": operations}, "unsupported": unsupported, "profile_failure": reason, "composition_class": classification,
            "observation_scope": "One authorized scalar state with disjoint read-only query commands", "reachability": "Bounded field/effect/identity/namespace checks; not arbitrary interactions"}


def coverage(contract, projection):
    expected = structural(contract, projection["source_frc"])
    if expected != projection or expected["unsupported"]:
        raise Failure("STRUCTURAL_COVERAGE_FAILURE", unsupported=expected["unsupported"], reason=expected["profile_failure"])
    return {"outcome": "SUPPORTED", "version": PROFILE, "rows": copy.deepcopy(expected["rows"]), "scope": expected["observation_scope"], "limitations": [expected["reachability"]]}


def bdi(contract, projection):
    coverage(contract, projection)
    result = scalar.discovery.discover(contract, projection["interface"])
    _, qc, _, _, _ = split(contract)
    qp = query.structural(qc, scalar.frc.digest(qc))
    qb = query.bdi(qc, qp)["result"]
    for key in ("decisions", "exclusions", "unknown"):
        result[key] += copy.deepcopy(qb[key])
    scalar.require(len({d["id"] for d in result["decisions"]}) == len(result["decisions"]), "CONFLICT: decision identity collision")
    result["extension"] = PROFILE
    return {"version": scalar.discovery.VERSION_BDI, "outcome": "SUPPORTED" if not result["unknown"] else "UNSUPPORTED", "result": result}


def adequate(contract, discovered):
    return scalar.adequate(contract, discovered)


def faithful_v1(contract):
    p = structural(contract, scalar.frc.digest(contract)); coverage(contract, p)
    normal = {"schema_version": scalar.V1, "profile": PROFILE, "contract": copy.deepcopy(contract), "facts": p["facts"]}
    return {"version": scalar.V1, "profile": PROFILE, "outcome": "FAITHFUL_COMPLETE", "document": normal, "normalized": copy.deepcopy(normal),
            "coverage": [{"frc_id": o["id"], "v1_id": o["id"]} for o in contract["obligations"]]}


def recover(normal):
    scalar.keys(normal, ("schema_version", "profile", "contract", "facts"))
    scalar.require(normal["schema_version"] == scalar.V1 and normal["profile"] == PROFILE, "Versioned composed V1")
    scalar.require(faithful_v1(normal["contract"])["normalized"] == normal, "Faithful composed V1 recovery")
    return copy.deepcopy(normal["contract"])


def formalizer_guidance():
    return ("Bounded compatible scalar plus query contracts select existing-composed-1 and "
            "collection_store={kind:composed_scalar,state:declared_state_id}. Emit full existing-scalar-1 "
            "facets and complete CollectionQuery groups. Query commands must be disjoint, read-only, "
            "and type/identity-compatible with the same scalar state. Mutating queries, nullable "
            "query fields and cross-state interactions remain unsupported; contradictory authorities "
            "are conflicts. Optional scalar guards carry command/field/value/error/rejection unchanged; "
            "clock_queries carry command/predicates/order/result whole_records/effect read_only. "
            "Predicates are only field_equals or field_before_clock with declared utc_clock, "
            "or their existing conjunction. Standalone amendments may select existing-model-1, "
            "existing_base_model context, and crud/profile existing-model-1 guards/clock_queries facets. "
            "Boolean guard facts may be recorded but cannot execute against absent or unsupported "
            "writable field types. No OR, ranges, in-set, temporal arithmetic or relations.")
