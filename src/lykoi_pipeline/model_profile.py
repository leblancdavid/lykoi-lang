"""Typed amendments of existing guard/clock-selection semantics, not new writes."""
import copy
import json

from air_compiler.parser import parse
from air_compiler.validator import validate
from lykoi_controller import Failure
from . import scalar_profile as scalar

PROFILE = "existing-model-1"
FACETS = ("guards", "clock_queries")


def typed(relation):
    return relation.get("parameters", {}).get("profile") == PROFILE


def applies(contract):
    return any(typed(o["relation"]) for o in contract["obligations"])


def facts(contract):
    scalar.frc.validate(contract)
    result = {}
    for o in contract["obligations"]:
        if not typed(o["relation"]): continue
        p = o["relation"]["parameters"]
        scalar.keys(p, ("profile", "facet", "value"))
        scalar.require(o["relation"]["kind"] == "crud" and p["facet"] in FACETS and p["facet"] not in result, "Closed existing-model amendment")
        result[p["facet"]] = copy.deepcopy(p["value"])
    scalar.require(bool(result) and any(result.values()), "Nonempty explicit amendment")
    # Producer schema validates closed facet objects. Lowering validates all
    # executable values/field types against the prior model's existing algebra.
    from lykoi_rehearsal.adapters import check_schema
    from lykoi_workspace.scalar_schema import MODEL_VALUES
    for facet, value in result.items(): check_schema(value, MODEL_VALUES[facet])
    return result


def lower(contract):
    scalar.require(contract["context"]["domains"].get("capability_profile") == PROFILE, "Explicit existing-model profile selection")
    base = copy.deepcopy(contract["context"]["domains"].get("existing_base_model"))
    validate(parse(json.dumps(base)))
    return scalar.integrate_facets(base, facts(contract))


def structural(contract, fid):
    unsupported = [o["id"] for o in contract["obligations"] if not typed(o["relation"])]
    if contract["context"]["component_authority"] is not None: unsupported.append("@component-context")
    try:
        f = facts(contract); model = lower(contract); reason = None
    except (Failure, ValueError, KeyError, TypeError, StopIteration) as exc:
        unsupported += [o["id"] for o in contract["obligations"] if typed(o["relation"])]
        f, model, reason = None, None, str(exc)
    rows, operations = [], []
    for o in contract["obligations"]:
        oid = o["id"]; supported = oid not in unsupported
        rows.append({"obligation": oid, "classification": "REPRESENTED" if supported else "UNSUPPORTED", "relation": copy.deepcopy(o["relation"]), "operation": oid if supported else None, "justification": "Existing-model typed amendment" if supported else "No executable amendment/prerequisite"})
        if not supported: continue
        fact, authority = {}, {}
        if o["relation"]["parameters"]["facet"] == "guards":
            fact["invalid_admitted"] = {"value": True, "origin": [oid], "evidence": "SEALED_TYPED_RELATION"}
            authority["invalid_input"] = {"allowed": ["reject"], "authority": "DETERMINED", "source_quote": o["source_quote"]}
        else:
            for k, value in (("collection", True), ("max_results", "many"), ("order_varies", False)):
                fact[k] = {"value": value, "origin": [oid], "evidence": "SEALED_TYPED_RELATION"}
        operations.append({"id": oid, "facts": fact, "channels": {"return": "MEANINGFUL", "error": "MEANINGFUL", "later": "MEANINGFUL", "order": "MEANINGFUL"}, "authority": authority})
    return {"version": PROFILE, "source_frc": fid, "rows": rows, "facts": f, "model": model, "unsupported": sorted(set(unsupported)), "profile_failure": reason,
            "interface": {"version": scalar.discovery.VERSION_BDI, "operations": operations}, "observation_scope": "Existing base authority preserved with explicit lookup guards/read-only selections", "reachability": "Bounded v0.3 amendment, not new predicate semantics"}


def coverage(contract, projection):
    p = structural(contract, projection["source_frc"])
    if p != projection or p["unsupported"]:
        raise Failure("STRUCTURAL_COVERAGE_FAILURE", unsupported=p["unsupported"], reason=p["profile_failure"])
    return {"outcome": "SUPPORTED", "version": PROFILE, "rows": copy.deepcopy(p["rows"]), "scope": p["observation_scope"], "limitations": [p["reachability"]]}


def bdi(contract, projection):
    coverage(contract, projection)
    result = scalar.discovery.discover(contract, projection["interface"])
    return {"version": scalar.discovery.VERSION_BDI, "outcome": "SUPPORTED" if not result["unknown"] else "UNSUPPORTED", "result": result}


def adequate(contract, discovered): return scalar.adequate(contract, discovered)


def faithful_v1(contract):
    p = structural(contract, scalar.frc.digest(contract)); coverage(contract, p)
    normal = {"schema_version": scalar.V1, "profile": PROFILE, "contract": copy.deepcopy(contract), "facts": p["facts"]}
    return {"version": scalar.V1, "profile": PROFILE, "outcome": "FAITHFUL_COMPLETE", "document": normal, "normalized": copy.deepcopy(normal), "coverage": [{"frc_id": o["id"], "v1_id": o["id"]} for o in contract["obligations"]]}


def recover(normal):
    scalar.keys(normal, ("schema_version", "profile", "contract", "facts"))
    scalar.require(normal["schema_version"] == scalar.V1 and normal["profile"] == PROFILE and faithful_v1(normal["contract"])["normalized"] == normal, "Faithful existing-model V1")
    return copy.deepcopy(normal["contract"])
