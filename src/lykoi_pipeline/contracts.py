"""Bounded WHAT-side adapters. No author output enters these transformations."""
from __future__ import annotations

import copy

from benchmark.evaluation import behavioral_discovery_r5_82 as discovery
from benchmark.evaluation import implementation_adequacy_r5_81 as adequacy
from benchmark.evaluation import formal_requirements_r5_80 as frc
from benchmark.evaluation import benchmark_documents_v1 as v1
from lykoi_controller import Failure

VERSION = "sealed-pipeline-1"


def structural(contract, frc_id):
    from . import mutable_profile
    if mutable_profile.applies(contract):
        return mutable_profile.structural(contract, frc_id)
    from . import model_profile
    if model_profile.applies(contract):
        return model_profile.structural(contract, frc_id)
    from . import composition_profile
    if composition_profile.applies(contract):
        return composition_profile.structural(contract, frc_id)
    from . import scalar_profile
    if scalar_profile.applies(contract):
        return scalar_profile.structural(contract, frc_id)
    from . import query_profile
    if query_profile.applies(contract):
        return query_profile.structural(contract, frc_id)
    rows, operations, unsupported = [], [], []
    for o in contract["obligations"]:
        oid, relation = o["id"], o["relation"]
        kind, p = relation["kind"], relation["parameters"]
        facts, channels, authority = {}, {}, {}
        def fact(name, value):
            facts[name] = {"value": value, "origin": [oid], "evidence": "SEALED_RELATION"}
        def clause(family, allowed, mode="DETERMINED"):
            authority[family] = {"allowed": allowed, "authority": mode, "source_quote": o["source_quote"]}
        supported = True
        if kind == "priority_create" and p.get("condition") == "priority omitted":
            fact("optional_input", True)
            channels["return"] = "MEANINGFUL"
            if p.get("result") in ("LOW", "NORMAL", "HIGH"):
                clause("optional", ["default"])
        elif kind == "priority_filter" and p.get("multiplicity") == "all":
            fact("selection", True)
            fact("exactly_one", False)
            # Plural task collection admits multiple selected records. Supplying
            # this traced fact avoids treating the inapplicable exactly-one tie
            # rule's missing annotation as supported analysis.
            fact("multiple_matches", True)
            channels["return"] = "MEANINGFUL"
            if p.get("predicate") in ("LOW", "NORMAL", "HIGH"):
                clause("selection", ["matching"])
        elif kind == "filter_order" and p.get("ordering") == "unconstrained":
            fact("collection", True)
            fact("max_results", "many")
            fact("order_varies", True)
            channels["order"] = "DELEGATED"
            clause("ordering", ["forward", "reverse"], "UNCONSTRAINED")
        elif kind == "crud" and p == {"domain": "task creation", "result": "supplied title"}:
            channels["return"] = "MEANINGFUL"
        elif kind in ("public_state_alternatives", "durable_content_constraints"):
            # Explicit component contracts are preserved, not reverse inferred.
            channels["later"] = "MEANINGFUL"
        elif kind == "effects":
            # Externally visible event/timing effects have no R5.82 rule.
            channels["external_effect"] = "MEANINGFUL"
        else:
            supported = False
        rows.append({"obligation": oid, "classification": "REPRESENTED" if supported else "UNSUPPORTED",
                     "relation": copy.deepcopy(relation), "operation": oid if supported else None,
                     "justification": "Exact bounded relation adapter" if supported else "No qualified structural mapping"})
        if supported:
            operations.append({"id": oid, "facts": facts, "channels": channels, "authority": authority})
        else:
            unsupported.append(oid)
    component = contract["context"]["component_authority"]
    if component is not None:
        rows.append({"obligation": "@component-context", "classification": "REPRESENTED",
                     "relation": copy.deepcopy(component), "operation": "@component-context",
                     "justification": "Complete source-selected exact component relation retained as normative authority; no new component choice delegated"})
        operations.append({"id": "@component-context", "facts": {},
                           "channels": {"return": "MEANINGFUL", "error": "MEANINGFUL", "later": "MEANINGFUL"},
                           "authority": {}, "exact_component_authority": copy.deepcopy(component)})
    return {"version": VERSION, "source_frc": frc_id, "rows": rows,
            "interface": {"version": discovery.VERSION_BDI, "operations": operations},
            "unsupported": unsupported, "exclusions": [],
            "observation_scope": "Only sealed relations and explicitly declared channels",
            "reachability": "Declared possible; no general reachability/completeness proof; exact component context is preserved, not independently rediscovered"}


def coverage(contract, projection):
    from . import mutable_profile
    if mutable_profile.applies(contract):
        return mutable_profile.coverage(contract, projection)
    from . import model_profile
    if model_profile.applies(contract):
        return model_profile.coverage(contract, projection)
    from . import composition_profile
    if composition_profile.applies(contract):
        return composition_profile.coverage(contract, projection)
    from . import scalar_profile
    if scalar_profile.applies(contract):
        return scalar_profile.coverage(contract, projection)
    from . import query_profile
    if query_profile.applies(contract):
        return query_profile.coverage(contract, projection)
    ids = [o["id"] for o in contract["obligations"]]
    if contract["context"]["component_authority"] is not None:
        ids.append("@component-context")
    rows = projection["rows"]
    if sorted(r["obligation"] for r in rows) != sorted(ids):
        raise Failure("STRUCTURAL_COVERAGE_FAILURE", reason="Omitted, extra or duplicate obligation")
    if projection["unsupported"] or any(r["classification"] != "REPRESENTED" for r in rows):
        raise Failure("STRUCTURAL_COVERAGE_FAILURE", unsupported=projection["unsupported"])
    operations = projection["interface"]["operations"]
    if {o["id"] for o in operations} != set(ids):
        raise Failure("STRUCTURAL_COVERAGE_FAILURE", reason="Unmapped operation")
    return {"outcome": "SUPPORTED", "version": VERSION, "rows": copy.deepcopy(rows),
            "scope": projection["observation_scope"], "limitations": [projection["reachability"]]}


def bdi(contract, projection):
    from . import mutable_profile
    if mutable_profile.applies(contract):
        return mutable_profile.bdi(contract, projection)
    from . import model_profile
    if model_profile.applies(contract):
        return model_profile.bdi(contract, projection)
    from . import composition_profile
    if composition_profile.applies(contract):
        return composition_profile.bdi(contract, projection)
    from . import scalar_profile
    if scalar_profile.applies(contract):
        return scalar_profile.bdi(contract, projection)
    from . import query_profile
    if query_profile.applies(contract):
        return query_profile.bdi(contract, projection)
    result = discovery.discover(contract, projection["interface"])
    return {"version": discovery.VERSION_BDI, "outcome": "SUPPORTED" if not result["unknown"] else "UNSUPPORTED",
            "result": result}


def adequate(contract, discovered):
    from . import mutable_profile
    if mutable_profile.applies(contract):
        return mutable_profile.adequate(contract, discovered)
    from . import model_profile
    if model_profile.applies(contract):
        return model_profile.adequate(contract, discovered)
    from . import composition_profile
    if composition_profile.applies(contract):
        return composition_profile.adequate(contract, discovered)
    from . import scalar_profile
    if scalar_profile.applies(contract):
        return scalar_profile.adequate(contract, discovered)
    from . import query_profile
    if query_profile.applies(contract):
        return query_profile.adequate(contract, discovered)
    sidecar = discovery.adequacy_sidecar(contract, discovered["result"], coverage_reviewed=True)
    # The unchanged adequacy engine requires a nonempty inventory. A component
    # with no discovered choice has an explicit INTERNAL record, not a new family.
    if not sidecar["decisions"] and sidecar["supported"]:
        sidecar["decisions"] = [{"id": "inventory:no-supported-open-choice", "relevance": "INTERNAL",
                                "reason": "Reviewed structural scope fires no supported decision rule"}]
    result = adequacy.analyze(contract, sidecar)
    return {"version": adequacy.VERSION, "outcome": "ADEQUATE" if result["status"] == "IMPLEMENTATION_ADEQUATE" else result["status"],
            "sidecar": sidecar, "result": result}


def faithful_v1(contract):
    """Same positive domain as R5.80; exact sealed authority replaces its receipt.

    Does not expand V1 or invent a mapping for generic behavioral relations.
    """
    from . import query_profile, scalar_profile, composition_profile, model_profile, mutable_profile
    if mutable_profile.applies(contract):
        return mutable_profile.faithful_v1(contract)
    if model_profile.applies(contract):
        return model_profile.faithful_v1(contract)
    if composition_profile.applies(contract):
        return composition_profile.faithful_v1(contract)
    if scalar_profile.applies(contract):
        return scalar_profile.faithful_v1(contract)
    if query_profile.selected(contract):
        return query_profile.faithful_v1(contract)
    context = contract["context"]["component_authority"]
    missing = [o["id"] for o in contract["obligations"] if o["relation"]["kind"] not in
               ("public_state_alternatives", "durable_content_constraints")]
    if context is None or missing:
        raise Failure("UNREPRESENTABLE_SOURCE", gap="NO_QUALIFIED_COMPLETE_MAPPING",
                      obligations_without_mapping=missing, missing_component_authority=context is None)
    try:
        document = {"schema_version": v1.VERSION, "document_id": "sealed-" + frc.validate(contract),
                    "role": "behavioral", "payload": {**copy.deepcopy(context), "obligations": [
                        {"id": o["id"], "requirement": {"kind": o["relation"]["kind"], **o["relation"]["parameters"]}}
                        for o in contract["obligations"]]}}
        normalized = v1.assemble([document])
        recovered = frc.recover(normalized, contract)
        if frc.compare_relations(contract, recovered)["classification"] not in ("STRUCTURALLY_IDENTICAL", "EXACT_CLAUSE_EQUIVALENT"):
            raise Failure("UNREPRESENTABLE_SOURCE", gap="PRESERVATION_FAILURE")
    except (frc.ContractError, v1.DocumentError) as exc:
        raise Failure("UNREPRESENTABLE_SOURCE", gap=str(exc)) from exc
    return {"version": v1.VERSION, "outcome": "FAITHFUL_COMPLETE", "document": document,
            "normalized": normalized, "coverage": [{"frc_id": o["id"], "v1_id": o["id"]} for o in contract["obligations"]]}
