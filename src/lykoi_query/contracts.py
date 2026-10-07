"""Formal semantic adapters, coverage and bounded decision discovery for queries."""
from __future__ import annotations

import copy

from air_compiler.collection_query import FACETS, INTERFACES, POLICIES, VERSION, QueryError, canonical, validate
from benchmark.evaluation import behavioral_discovery_r5_82 as discovery
from benchmark.evaluation import implementation_adequacy_r5_81 as adequacy
from benchmark.evaluation import formal_requirements_r5_80 as frc
from lykoi_controller import Failure

RELATION = "filter_order"
PROFILE = "collection-query-1"


def structural(contract, frc_id):
    """No source-word/identity dispatch. FRC facet values are semantic authority.

    Prose-only historical relations remain unsupported; extraction is a separate,
    inspectable formalization step, never a permissive adapter fallback.
    """
    groups, rows, unsupported = {}, [], []
    for o in contract["obligations"]:
        p = o["relation"]["parameters"]
        supported = (o["relation"]["kind"] == RELATION and set(p) == {"query", "facet", "value"}
                     and type(p["query"]) is str and p["query"].strip() and p["facet"] in FACETS + INTERFACES)
        rows.append({"obligation": o["id"], "relation": copy.deepcopy(o["relation"]),
                     "classification": "REPRESENTED" if supported else "UNSUPPORTED"})
        if supported:
            group = groups.setdefault(p["query"], {"id": p["query"], "origins": {}})
            if p["facet"] in group:
                unsupported.extend([o["id"], group["origins"][p["facet"]]])
            else:
                group[p["facet"]] = copy.deepcopy(p["value"])
                group["origins"][p["facet"]] = o["id"]
        else:
            unsupported.append(o["id"])
    queries = []
    for group in groups.values():
        try:
            validate({k: v for k, v in group.items() if k != "origins"})
            queries.append(group)
        except (QueryError, KeyError, TypeError, ValueError):
            unsupported.extend(group["origins"].values())
    if contract["context"]["component_authority"] is not None:
        unsupported.append("@component-context")
    unsupported = sorted(set(unsupported))
    for row in rows:
        if row["obligation"] in unsupported:
            row["classification"] = "UNSUPPORTED"
    return {"version": PROFILE, "source_frc": frc_id, "rows": rows,
            "queries": queries, "unsupported": unsupported}


def coverage(contract, projection):
    expected = structural(contract, frc.digest(contract))
    if expected != projection or projection["unsupported"]:
        raise Failure("STRUCTURAL_COVERAGE_FAILURE", unsupported=expected["unsupported"],
                      reason="Unsupported, incomplete or stale query projection")
    if not projection["queries"]:
        raise Failure("STRUCTURAL_COVERAGE_FAILURE", reason="Empty query inventory")
    return {"outcome": "SUPPORTED", "scope": PROFILE, "obligations": len(projection["rows"])}


def token(value):
    return canonical(value)


def alternatives(query, facet):
    """Finite synthetic-profile decisions, not universal behavioral completeness."""
    value = query[facet]
    if type(value) is dict and "freedom" in value:
        return value["freedom"]
    if facet == "comparison":
        if query["predicate"].get("result_type") == "boolean":
            return [value, {"scope": "invented_global_policy"}]
        return [{"case": c, "normalization": n} for c in ("sensitive", "casefold") for n in ("none", "strip")]
    if facet == "effect":
        return [{"state": "read_only", "persistence": "unchanged"}, {"state": "mutating", "persistence": "write"}]
    if facet == "result":
        choices = [{"shape": "collection", "cardinality": "zero_or_more", "no_match": m} for m in ("empty", "null")]
        return choices + [value if value is not None and value.get("no_match") == "error" else
                          {"shape": "collection", "cardinality": "zero_or_more", "no_match": "error", "error": "no_match"}]
    if facet == "ordering":
        keys = value or [{"field": query["source"]["unique_key"], "direction": "ASC"}]
        reverse = [{**k, "direction": "DESC" if k["direction"] == "ASC" else "ASC"} for k in keys]
        choices = [keys, reverse]
        if len(keys) > 1:
            choices.extend([list(reversed(keys)), [next(k for k in keys if k["field"] == query["source"]["unique_key"])]])
        return list({token(c): c for c in choices}.values())
    if facet == "validation":
        if not query["parameters"]:
            return [[], [{"invented_parameter_validation": True}]]
        values = value or [{"parameter": next(iter(query["parameters"])), "rule": "nonblank", "error": "invalid_query"}]
        return [values, []]
    if facet == "inclusion":
        values = value or []
        if values:
            altered = copy.deepcopy(values)
            rule = altered[0]
            if rule["mode"] == "equals":
                altered[0] = {"field": rule["field"], "mode": "all"}
            else:
                kind = query["source"]["fields"][rule["field"]]
                rule.update(mode="equals", value={"boolean": False, "integer": 0, "string": "active", "strings": []}[kind])
            return [values, altered]
        # With no named other dimension the selection-only policy still matters.
        return [[], [{"implicit_exclusion": True}]]
    raise QueryError("Unknown decision facet")


def bdi(contract, projection):
    coverage(contract, projection)
    obligations = {o["id"]: o for o in contract["obligations"]}
    operations = []
    for q in projection["queries"]:
        oid = q["origins"]["predicate"]
        operations.append({"id": q["id"], "facts": {
            "selection": {"value": True, "origin": [oid], "evidence": "FORMAL_QUERY"},
            "exactly_one": {"value": False, "origin": [q["origins"]["result"]], "evidence": "FORMAL_QUERY"},
            "multiple_matches": {"value": True, "origin": [q["origins"]["result"]], "evidence": "FORMAL_QUERY"}},
            "channels": {"return": "MEANINGFUL"}, "authority": {
                "selection": {"allowed": ["matching"], "authority": "DETERMINED", "source_quote": obligations[oid]["source_quote"]}}})
    result = discovery.discover(contract, {"version": discovery.VERSION_BDI, "operations": operations})
    for q in projection["queries"]:
        # Runtime binding is a distinct decision from matching versus nonmatching.
        oid = q["origins"]["predicate"]
        runtime = "parameter" in q["predicate"].get("operand", {}) or ('"kind":"parameter"' in token(q["predicate"]))
        decisions = [("runtime_binding", ["runtime_parameter", "constant"],
                       "runtime_parameter" if runtime else "constant", oid, "return", "DETERMINED")]
        if q["predicate"].get("result_type") == "boolean":
            from air_compiler.predicates import decisions as predicate_decisions
            for path, meaning in predicate_decisions(q["predicate"]):
                decisions.append(("condition/" + path, [meaning, "altered_or_missing_condition"], meaning, oid, "return", "DETERMINED"))
        for facet in POLICIES:
            value = q[facet]
            free = type(value) is dict and "freedom" in value
            options = [token(c) for c in alternatives(q, facet)]
            decisions.append((facet, options, options if free else token(value) if value is not None else None,
                              q["origins"][facet], "later" if facet == "effect" else "error" if facet == "validation" else
                               "order" if facet == "ordering" else "return", "UNCONSTRAINED" if free else "DETERMINED"))
        for facet in INTERFACES:
            if facet in q:
                meaning = token(q[facet])
                decisions.append((facet, [meaning, "omitted_or_altered_interface"], meaning, q["origins"][facet], "error" if facet in ("preconditions", "parameter_errors") else "return", "DETERMINED"))
        for family, options, selected, origin, channel, mode in decisions:
            authority = None if selected is None else {"allowed": selected if type(selected) is list else [selected],
                "authority": mode, "source_quote": obligations[origin]["source_quote"]}
            result["decisions"].append({"id": q["id"] + ":query_" + family, "family": "query_" + family,
                "operation": q["id"], "origins": [origin], "alternatives": options, "channel": channel,
                "observation_scope": "MEANINGFUL", "authority": authority,
                "consequence": "Observable query policy: " + family, "rule": PROFILE + "/" + family,
                "reachability": "DECLARED_SYNTHETIC_PROFILE_NOT_GENERAL_PROOF"})
    result["extension"] = PROFILE
    return {"outcome": "SUPPORTED" if not result["unknown"] else "UNSUPPORTED", "result": result}


def adequate(contract, discovered):
    sidecar = discovery.adequacy_sidecar(contract, discovered["result"], coverage_reviewed=True)
    result = adequacy.analyze(contract, sidecar)
    return {"outcome": result["status"], "result": result, "sidecar": sidecar}


def document(contract, projection):
    """Prospective CollectionQueryDocumentV1, not historical BehavioralContractV1.

    The old V1 envelope accepts opaque operations but does not assign executable
    query meaning. This explicit versioned semantic profile closes that gap only.
    """
    coverage(contract, projection)
    return {"schema_version": "CollectionQueryDocumentV1", "contract": copy.deepcopy(contract),
            "source_frc": frc.digest(contract), "queries": copy.deepcopy(projection["queries"])}


def recover(doc):
    if set(doc) != {"schema_version", "contract", "source_frc", "queries"} or doc["schema_version"] != "CollectionQueryDocumentV1":
        raise QueryError("Unsupported query document")
    contract = doc["contract"]
    if doc["source_frc"] != frc.digest(contract):
        raise QueryError("Stale query document")
    projection = structural(contract, doc["source_frc"])
    coverage(contract, projection)
    if doc["queries"] != projection["queries"]:
        raise QueryError("Unfaithful query document")
    return copy.deepcopy(contract)
