"""Public, pure BDI-0.1 structural discovery. No IO, prose inference or grants."""
import copy
from benchmark.evaluation.implementation_adequacy_r5_81 import commitment, VERSION

VERSION_BDI = "BehavioralDecisionInventory-0.1"
# Each predicate is a conjunction over reviewed interface facts, not word matching.
# required values, inhibiting invariants, observation channel, finite probe choices
RULES = {
    "ordering": ({"collection": True, "max_results": "many", "order_varies": True}, {}, "order", ["forward", "reverse"]),
    "selection": ({"selection": True}, {}, "return", ["matching", "nonmatching"]),
    "cardinality": ({"selection": True, "exactly_one": True}, {}, "return", ["one", "all"]),
    "tie": ({"selection": True, "exactly_one": True, "multiple_matches": True}, {"unique_match": True}, "return", ["first", "last"]),
    "optional": ({"optional_input": True}, {}, "return", ["default", "reject"]),
    "nullable_predicate": ({"nullable": True, "predicate": True}, {"nonnull_precondition": True}, "return", ["exclude", "include"]),
    "default_trigger_domain": ({"creation_default": True, "historical_absence": True}, {"historical_complete": True}, "later", ["creation_only", "also_historical"]),
    "normalization": ({"normalize": True}, {"normalization_identity": True}, "return", ["normalized", "raw"]),
    "collision": ({"normalize": True, "unique": True, "collision_possible": True}, {"injective_on_domain": True}, "error", ["reject", "merge"]),
    "invalid_input": ({"invalid_admitted": True}, {}, "error", ["reject", "coerce"]),
    "duplicates": ({"duplicates_admitted": True, "collection": True}, {}, "return", ["preserve", "deduplicate"]),
    "persistence": ({"persist": True}, {}, "later", ["durable", "volatile"]),
    "transition": ({"transition": True}, {}, "later", ["change", "unchanged"]),
    "retry": ({"transition": True, "repeat": True, "poststate_admitted": True}, {"single_invocation": True}, "later", ["idempotent", "reject"]),
    "failure_atomicity": ({"persist": True, "failure_after_write": True}, {"failure_before_write_only": True}, "later", ["rollback", "retain"]),
}


def finite_facts(operation):
    """Enumerate only explicitly exhaustive finite domains; no general SMT claim.

    Score states list every admitted eligible-record score multiset (nonempty).
    Normalization enumerates every admitted string with the exact lower transform.
    These domains are reviewer-supplied scope, not inferred from English.
    """
    op = copy.deepcopy(operation)
    domain = op.get("finite_domain")
    if domain is None:
        return op
    if domain.get("exhaustive") is not True or not domain.get("origin"):
        raise ValueError("finite domain must be exhaustive and traced")
    def put(name, value, witness):
        prior = op["facts"].get(name)
        if prior and prior["value"] != value:
            raise ValueError("contradictory finite domain: " + name)
        op["facts"][name] = {"value": value, "origin": domain["origin"],
                             "evidence": "FINITE_ENUMERATION", "witness": witness}
    if "score_states" in domain:
        states = domain["score_states"]
        if not states or any(not s or any(type(x) not in (int, float) for x in s) for s in states):
            raise ValueError("nonempty numeric eligible states required")
        # commitment rejects nonfinite numeric values before this function is called.
        tied = next((s for s in states if s.count(max(s)) > 1), None)
        put("multiple_matches", tied is not None, tied)
        put("unique_match", tied is None, {"enumerated_states": len(states)})
    if "normalization_values" in domain:
        values = domain["normalization_values"]
        if domain.get("transform") != "lower" or not values or any(not isinstance(v, str) for v in values):
            raise ValueError("only nonempty finite string/lower domain supported")
        pair = next(([a, b] for n, a in enumerate(values) for b in values[n+1:]
                     if a != b and a.lower() == b.lower()), None)
        put("collision_possible", pair is not None, pair)
        put("injective_on_domain", pair is None, {"enumerated_values": len(values)})
        put("normalization_identity", all(v.lower() == v for v in values), {"enumerated_values": len(values)})
    return op


def discover(contract, interface):
    """Missing facts are UNKNOWN, never invented invariants or negative facts."""
    # Reject noncanonical evidence, including NaN in enumerated domains.
    contract_hash, interface_hash = commitment(contract), commitment(interface)
    decisions, exclusions, unknown = [], [], []
    ids = set()
    for operation in interface["operations"]:
        op = finite_facts(operation)
        if not op["id"] or op["id"] in ids:
            raise ValueError("duplicate/empty operation identity")
        ids.add(op["id"])
        facts = op["facts"]
        for channel, scope in op["channels"].items():
            if scope not in ("MEANINGFUL", "DELEGATED", "EXCLUDED"):
                raise ValueError("unknown observation scope")
            if channel not in ("return", "order", "error", "later") and scope != "EXCLUDED":
                unknown.append({"operation": op["id"], "family": "unsupported_observation",
                                "missing": ["rule_for:" + channel]})
        for name, fact in facts.items():
            if not fact["origin"] or not fact["evidence"]:
                raise ValueError("untraceable fact: " + name)
        for family, (needs, inhibits, channel, options) in RULES.items():
            # Applicability is relevance-sensitive: first structural fact must hold.
            first = next(iter(needs))
            if first not in facts or facts[first]["value"] != needs[first]:
                continue
            missing = [k for k in needs if k not in facts]
            if missing:
                unknown.append({"operation": op["id"], "family": family, "missing": missing})
                continue
            if any(facts[k]["value"] != v for k, v in needs.items()):
                continue
            fired_inhibitors = [k for k, v in inhibits.items() if k in facts and facts[k]["value"] == v]
            basis = list(needs) + fired_inhibitors
            origins = sorted({x for k in basis for x in facts[k]["origin"]})
            identity = op["id"] + ":" + family
            scope = op["channels"].get(channel)
            if scope not in (None, "MEANINGFUL", "DELEGATED", "EXCLUDED"):
                raise ValueError("unknown observation scope")
            if fired_inhibitors or scope == "EXCLUDED":
                exclusions.append({"id": identity, "origins": origins,
                                   "reason": "invariant:" + ",".join(fired_inhibitors) if fired_inhibitors else "nonsemantic_channel"})
                continue
            if scope is None:
                unknown.append({"operation": op["id"], "family": family, "missing": ["channel:" + channel]})
                continue
            decisions.append({"id": identity, "family": family, "operation": op["id"],
                              "origins": origins, "trigger": copy.deepcopy(needs), "facts": basis,
                              "alternatives": list(options), "channel": channel, "observation_scope": scope,
                              "consequence": "Choices differ through declared " + channel + " observation",
                              "rule": "BDI-0.1/" + family,
                              "evidence": "MECHANICALLY_DERIVED_FINITE" if any(facts[k]["evidence"] == "FINITE_ENUMERATION" for k in basis) else "BOUNDED_STRUCTURAL",
                              "witnesses": [facts[k]["witness"] for k in basis if "witness" in facts[k]],
                              "reachability": "FINITE_DECLARED_DOMAIN" if "finite_domain" in op else "DECLARED_POSSIBLE_UNLESS_SUPPORTED_INVARIANT",
                              "authority": op.get("authority", {}).get(family),
                              "dependency": [op["id"] + ":transition"] if family == "retry" else []})
    return {"version": VERSION_BDI, "contract_commitment": contract_hash,
            "interface_commitment": interface_hash, "decisions": decisions,
            "exclusions": exclusions, "unknown": unknown,
            "coverage": "SUPPORTED_RULES_ONLY_NOT_GENERAL_COMPLETENESS"}


def adequacy_sidecar(contract, bdi, coverage_reviewed=False):
    """Adapter does not certify completeness or issue authoring authority."""
    if bdi["version"] != VERSION_BDI or bdi["contract_commitment"] != commitment(contract):
        raise ValueError("stale BDI")
    decisions = []
    for d in bdi["decisions"]:
        decisions.append({"id": d["id"], "relevance": "REQUIRED", "reason": d["consequence"],
                          "options": d["alternatives"], "clauses": [d["authority"]] if d["authority"] else []})
    return {"version": VERSION, "contract_commitment": commitment(contract),
            "scope": contract.get("scope", contract.get("context", {}).get("scope")),
            "coverage_reviewed": coverage_reviewed, "supported": not bdi["unknown"],
            "issues": [], "decisions": decisions}
