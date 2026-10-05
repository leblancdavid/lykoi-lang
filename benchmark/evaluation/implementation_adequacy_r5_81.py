"""Pure experimental finite-decision analysis; no protected IO or authoring."""

import hashlib
import json


VERSION = "ImplementationAdequacy-0.1"


def commitment(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def analyze(contract, analysis):
    try:
        contract_hash, analysis_hash = commitment(contract), commitment(analysis)
    except (TypeError, ValueError):
        return {"status": "OUTSIDE_ANALYSIS_SCOPE", "missing_decisions": [],
                "findings": ["NON_CANONICAL_JSON"], "next_action": "NEEDS_CLARIFICATION",
                "contract_commitment": None, "analysis_commitment": None}
    findings = []
    missing = []
    conflict = False
    ambiguity = False
    outside = False
    try:
        source = contract["source"]
        if isinstance(source, dict):
            source = source["text"]
        if analysis["version"] != VERSION or analysis["contract_commitment"] != contract_hash:
            raise ValueError("STALE_OR_UNKNOWN_ANALYSIS")
        scope = contract.get("scope", contract.get("context", {}).get("scope"))
        if analysis["scope"] != scope:
            raise ValueError("SCOPE_MISMATCH")
        if analysis["supported"] is True and not analysis["decisions"]:
            raise ValueError("EMPTY_SUPPORTED_INVENTORY")
        if not analysis["scope"] or analysis["coverage_reviewed"] is not True or analysis["supported"] is not True:
            outside = True
            findings.append("UNQUALIFIED_COVERAGE_OR_PROFILE")
        for issue in analysis["issues"]:
            if issue["kind"] == "CONFLICT":
                conflict = True
            elif issue["kind"] == "AMBIGUITY":
                ambiguity = True
            else:
                outside = True
            findings.append(issue["reason"])
        seen = set()
        for d in analysis["decisions"]:
            if d["id"] in seen or not d["reason"]:
                raise ValueError("INVALID_DECISION_ID_OR_RELEVANCE")
            seen.add(d["id"])
            if d["relevance"] in ("INTERNAL", "EXCLUDED"):
                continue
            if d["relevance"] != "REQUIRED":
                raise ValueError("UNKNOWN_RELEVANCE")
            options = set(d["options"])
            if not options or len(options) != len(d["options"]):
                raise ValueError("INVALID_FINITE_DOMAIN")
            allowed = options.copy()
            for clause in d["clauses"]:
                selected = set(clause["allowed"])
                if (clause["authority"] not in ("DETERMINED", "DELEGATED", "UNCONSTRAINED")
                        or not clause["source_quote"] or clause["source_quote"] not in source
                        or not selected <= options):
                    raise ValueError("INVALID_AUTHORITY")
                if clause["authority"] == "DETERMINED" and len(selected) != 1:
                    raise ValueError("INVALID_DETERMINATION")
                if clause["authority"] == "UNCONSTRAINED" and selected != options:
                    raise ValueError("INVALID_UNCONSTRAINED_DOMAIN")
                allowed &= selected
            if not d["clauses"]:
                missing.append(d["id"])
                findings.append("MISSING_AUTHORITY:" + d["id"])
            elif not allowed:
                conflict = True
                findings.append("EMPTY_INTERSECTION:" + d["id"])
    except (KeyError, TypeError, ValueError) as exc:
        outside = True
        findings.append("INVALID_ANALYSIS:" + str(exc))
    status = ("CONFLICTING_REQUIREMENT" if conflict else
              "NEEDS_CLARIFICATION" if ambiguity else
              "OUTSIDE_ANALYSIS_SCOPE" if outside else
              "IMPLEMENTATION_UNDERSPECIFIED" if missing else
              "IMPLEMENTATION_ADEQUATE")
    return {"status": status, "missing_decisions": missing, "findings": findings,
            "next_action": "NONE" if status == "IMPLEMENTATION_ADEQUATE" else "NEEDS_CLARIFICATION",
            "contract_commitment": contract_hash, "analysis_commitment": analysis_hash}


def authorization(contract, fidelity_receipt, analysis):
    result = analyze(contract, analysis)
    return (isinstance(fidelity_receipt, dict)
            and fidelity_receipt.get("outcome") == "APPROVED"
            and fidelity_receipt.get("contract_commitment") == result["contract_commitment"]
            and result["status"] == "IMPLEMENTATION_ADEQUATE")
