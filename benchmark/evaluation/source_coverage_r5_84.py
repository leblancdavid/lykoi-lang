"""SCCA-0.1: pure, prospective evidence checks, not a natural-language oracle.

Only the experiment wrapper supplies R5.82's old coverage flag. No IO or grants.
Caller-pinned reviews are cooperative evidence, not authenticated credentials.
"""
from benchmark.evaluation import formal_requirements_r5_80 as frc
from benchmark.evaluation.behavioral_discovery_r5_82 import (
    RULES, discover, adequacy_sidecar,
)
from benchmark.evaluation.implementation_adequacy_r5_81 import analyze, authorization

VERSION = "SourceContractInterfaceCoverageAttestation-0.1"
SOI_VERSION = "SourceObligationInventory-0.1"


def evidence_content(bundle):
    """Display metadata and an injected legacy boolean have no evidential meaning."""
    return {k: v for k, v in bundle.items() if k not in ("metadata", "coverage_complete")}


def evidence_hash(bundle):
    return frc.digest(evidence_content(bundle))


def _ids(rows):
    result = {r["id"]: r for r in rows}
    if len(result) != len(rows) or any(not k for k in result):
        raise ValueError("DUPLICATE_OR_EMPTY_ID")
    return result


def _at(value, path):
    if not path:
        raise ValueError("EMPTY_STRUCTURAL_PATH")
    for key in path:
        value = value[key]
    return value


def assess(bundle, receipt, admission):
    """Check explicit evidence graphs under an external experimental admission.

    Missing inventory meaning is not recoverable from arbitrary prose here.
    Nonapproval is sticky: unresolved/disputed/material unsupported always halts.
    """
    findings, states, required_reviews = [], set(), set()

    def fail(code, state="COVERAGE_INCOMPLETE"):
        findings.append(code)
        states.add(state)

    def reviewed(key):
        required_reviews.add(key)

    try:
        if not all(isinstance(x, dict) for x in (bundle, receipt, admission)):
            raise ValueError("MISSING_EVIDENCE_OR_REVIEW")
        content_hash = evidence_hash(bundle)
        if bundle["version"] != VERSION:
            raise ValueError("UNKNOWN_ATTESTATION_VERSION")
        source, soi, contract = bundle["source"], bundle["soi"], bundle["contract"]
        interface = bundle["interface"]
        frc.validate(contract)
        if (source["record"] != contract["source"] or source["revision"] < 1
                or soi["version"] != SOI_VERSION
                or soi["source_commitment"] != frc.digest(source)):
            raise ValueError("SOURCE_OR_INVENTORY_BINDING")
        if soi["questions"] or bundle["questions"]:
            fail("UNRESOLVED_COVERAGE_QUESTIONS", "SOURCE_AMBIGUOUS")
        if bundle["disagreements"]:
            fail("UNRESOLVED_INVENTORY_DISAGREEMENT", "COVERAGE_DISPUTED")
        text = source["record"]["text"]
        items = _ids(soi["items"])
        covered = set()
        for iid, item in items.items():
            for span in item["spans"]:
                a, b = span["start"], span["end"]
                if (type(a) is not int or type(b) is not int or not 0 <= a < b <= len(text)
                        or text[a:b] != span["quote"]):
                    raise ValueError("INVALID_SOURCE_SPAN:" + iid)
                covered.update(range(a, b))
            if not item["spans"] or not item["meaning"]:
                raise ValueError("EMPTY_SOURCE_ITEM:" + iid)
            if type(item["material"]) is not bool:
                raise ValueError("INVALID_MATERIALITY")
            if any(x not in items for x in item["dependencies"]):
                raise ValueError("UNBOUND_SOURCE_DEPENDENCY")
            reviewed("inventory:" + iid)
        if any(not ch.isspace() and n not in covered for n, ch in enumerate(text)):
            fail("UNACCOUNTED_SOURCE_TEXT")
        obligations = _ids(contract["obligations"])
        issues = _ids(contract["issues"])
        maps = _ids(bundle["source_map"])
        mapped_items, justified = set(), set()
        for mid, row in maps.items():
            reviewed("mapping:" + mid)
            if not row["source_ids"] or any(i not in items for i in row["source_ids"]):
                raise ValueError("UNBOUND_SOURCE_MAPPING")
            if any(o not in obligations for o in row["obligation_ids"]):
                fail("MISSING_FRC_TARGET:" + mid)
            mapped_items.update(row["source_ids"])
            justified.update(row["obligation_ids"])
            kind = row["disposition"]
            if kind == "REPRESENTED":
                if not row["obligation_ids"]:
                    fail("OMITTED_MATERIAL_OBLIGATION:" + mid)
                if any(items[i]["category"] in ("AMBIGUITY", "CONFLICT", "UNSPECIFIED")
                       for i in row["source_ids"]):
                    fail("UNCERTAINTY_CONVERTED_TO_BEHAVIOR:" + mid, "SOURCE_AMBIGUOUS")
            elif kind in ("AMBIGUITY", "CONFLICT"):
                if row["issue_id"] not in issues or issues[row["issue_id"]]["category"] != kind:
                    fail("UNPRESERVED_SOURCE_ISSUE:" + mid)
                fail("ACTIVE_SOURCE_ISSUE:" + mid,
                     "SOURCE_CONFLICTING" if kind == "CONFLICT" else "SOURCE_AMBIGUOUS")
            elif kind == "UNSPECIFIED":
                if (row["preserved_text"] not in contract["unspecified"]
                        or any(items[i]["category"] != "UNSPECIFIED" for i in row["source_ids"])):
                    fail("UNPRESERVED_EXPLICIT_UNSPECIFIED:" + mid)
            elif kind == "NONBEHAVIORAL":
                if any(items[i]["material"] for i in row["source_ids"]) or not row["rationale"]:
                    fail("MATERIAL_MISCLASSIFIED_NONBEHAVIORAL:" + mid)
            elif kind == "EXCLUDED":
                exclusion = row["exclusion"]
                reviewed("exclusion:" + mid)
                if not exclusion["rationale"] or not exclusion["premises"]:
                    fail("UNSUPPORTED_EXCLUSION:" + mid)
                if any(i not in items for i in exclusion["premises"]):
                    fail("UNBOUND_EXCLUSION_PREMISE:" + mid)
                cls = exclusion["class"]
                if cls == "EXPLICIT_NON_SEMANTIC":
                    if not any(items[i]["category"] == "CONSUMER_RESTRICTION"
                               for i in exclusion["premises"]):
                        fail("NO_EXPLICIT_NONSEMANTIC_AUTHORITY:" + mid)
                elif cls == "MECHANICALLY_IRRELEVANT":
                    # Narrow exhaustive proof, conditional on independently reviewed domain.
                    domain = exclusion["domain"]
                    if (domain["exhaustive"] is not True or not domain["collections"]
                            or any(len(c) > 1 for c in domain["collections"])
                            or not any(items[i]["category"] == "CARDINALITY_BOUND"
                                       for i in exclusion["premises"])):
                        fail("INVALID_FINITE_ORDER_EXCLUSION:" + mid)
                elif cls != "REVIEWER_CLASSIFIED_IRRELEVANT":
                    fail("UNSUPPORTED_EXCLUSION_CLASS:" + mid)
            elif kind == "UNSUPPORTED":
                fail("UNSUPPORTED_SOURCE_CONTENT:" + mid, "STRUCTURAL_SCOPE_UNSUPPORTED")
            else:
                fail("UNKNOWN_SOURCE_DISPOSITION:" + mid)
        for iid in items.keys() - mapped_items:
            fail("UNMAPPED_SOURCE_ITEM:" + iid)
        implications = _ids(bundle["implications"])
        implied = set()
        for impid, imp in implications.items():
            reviewed("implication:" + impid)
            target = imp["result"]
            if (target not in obligations or not imp["premises"]
                    or any(i not in items for i in imp["premises"])
                    or not imp["rationale"] or imp["review_status"] != "APPROVED"):
                fail("UNSUPPORTED_IMPLICATION:" + impid)
                continue
            if obligations[target]["basis"] != "NECESSARY_IMPLICATION":
                fail("IMPLICATION_BASIS_MISMATCH:" + impid)
            if imp["inference_class"] == "CONJUNCTION_ELIMINATION":
                if (imp["mode"] != "MECHANICAL_CONDITIONAL_ON_REVIEWED_PREMISES"
                        or imp["conclusion"] not in imp["premise_atoms"]):
                    fail("INVALID_CONJUNCTION_IMPLICATION:" + impid)
            elif imp["inference_class"] == "REVIEWER_NECESSITY":
                if imp["mode"] != "REVIEWER_DERIVED" or not imp["denial_witness"]:
                    fail("NO_NECESSITY_WITNESS:" + impid)
            else:
                fail("UNSUPPORTED_INFERENCE_CLASS:" + impid)
            implied.add(target)
        for oid in obligations:
            if oid not in justified and oid not in implied:
                fail("INVENTED_OR_UNJUSTIFIED_FRC_OBLIGATION:" + oid)
            if obligations[oid]["basis"] == "NECESSARY_IMPLICATION" and oid not in implied:
                fail("MISSING_IMPLICATION_PROVENANCE:" + oid)
        projections = _ids(bundle["structural_map"])
        projected, accounted_paths = set(), set()
        for pid, row in projections.items():
            reviewed("projection:" + pid)
            oid = row["obligation_id"]
            if oid not in obligations:
                fail("UNBOUND_PROJECTION:" + pid)
                continue
            projected.add(oid)
            if row["status"] != "REPRESENTED":
                fail("MATERIAL_STRUCTURAL_" + row["status"] + ":" + oid,
                     "STRUCTURAL_SCOPE_UNSUPPORTED")
            elif row["family"] not in RULES:
                fail("UNSUPPORTED_STRUCTURAL_FAMILY:" + row["family"], "STRUCTURAL_SCOPE_UNSUPPORTED")
            if not row["entries"] or not any(e["role"] == "OBSERVATION" for e in row["entries"]):
                fail("MISSING_STRUCTURAL_OBSERVATION:" + oid)
            for entry in row["entries"]:
                path = entry["path"]
                try:
                    if _at(interface, path) != entry["value"]:
                        fail("STRUCTURAL_VALUE_MISMATCH:" + pid)
                except (KeyError, IndexError, TypeError):
                    fail("MISSING_STRUCTURAL_FACT:" + pid)
                accounted_paths.add(tuple(path))
        for oid in obligations.keys() - projected:
            fail("MISSING_STRUCTURAL_PROJECTION:" + oid, "STRUCTURAL_SCOPE_UNSUPPORTED")
        # Prevent unreviewed inhibitors/channels/authority from changing discovery.
        for n, op in enumerate(interface["operations"]):
            for group in ("facts", "channels", "authority"):
                for key in op.get(group, {}):
                    if ("operations", n, group, key) not in accounted_paths:
                        fail("UNREVIEWED_INTERFACE_ENTRY:" + op["id"] + ":" + key)
            if "finite_domain" in op and ("operations", n, "finite_domain") not in accounted_paths:
                fail("UNREVIEWED_FINITE_DOMAIN:" + op["id"])
        if any(i["category"] == "CONFLICT" for i in issues.values()):
            fail("ACTIVE_FRC_CONFLICT", "SOURCE_CONFLICTING")
        elif issues:
            fail("ACTIVE_FRC_ISSUE", "SOURCE_AMBIGUOUS")
        if (receipt.get("version") != VERSION
                or admission.get("mode") != "PUBLIC_SYNTHETIC_EXPERIMENT"
                or admission.get("review_commitment") != frc.digest(receipt)
                or admission.get("inventory_commitment") != frc.digest(soi)
                or receipt.get("evidence_commitment") != content_hash
                or receipt.get("reviewer") != admission.get("reviewer")
                or not receipt.get("reviewer")
                or receipt["reviewer"] in (contract["formalizer"], soi["extractor"])
                or not receipt.get("context_class")):
            fail("UNQUALIFIED_OR_UNBOUND_REVIEW", "COVERAGE_UNREVIEWED")
        judgments = receipt.get("judgments", {})
        for key in required_reviews:
            judgment = judgments.get(key, {})
            if judgment.get("result") != "PASS" or not judgment.get("rationale"):
                fail("UNAPPROVED_EVIDENCE:" + key, "COVERAGE_DISPUTED")
        if receipt.get("result") != "COVERAGE_APPROVED":
            fail("REVIEW_NOT_APPROVED", "COVERAGE_UNREVIEWED")
    except (KeyError, IndexError, TypeError, ValueError, frc.ContractError) as exc:
        content_hash = None
        fail("INVALID_COVERAGE_EVIDENCE:" + str(exc))
    precedence = ("SOURCE_CONFLICTING", "SOURCE_AMBIGUOUS", "COVERAGE_DISPUTED",
                  "COVERAGE_INCOMPLETE", "STRUCTURAL_SCOPE_UNSUPPORTED", "COVERAGE_UNREVIEWED")
    status = next((s for s in precedence if s in states), "COVERAGE_APPROVED")
    source_ok = not states.intersection(set(precedence) - {"STRUCTURAL_SCOPE_UNSUPPORTED"})
    return {"version": VERSION, "status": status, "findings": findings,
            "evidence_commitment": content_hash, "source_coverage_approved": source_ok,
            "structural_coverage_approved": not states,
            "mechanical_scope": "GRAPH_BINDING_AND_REVIEW_CONSISTENCY_NOT_PROSE_COMPLETENESS",
            "production_authority": False}


def downstream(bundle, receipt, admission, fidelity_receipt):
    """Mandatory experimental entrypoint; never consume a supplied complete boolean."""
    coverage = assess(bundle, receipt, admission)
    result = {"coverage": coverage, "discovery": "NOT_RUN", "adequacy": "OUTSIDE_ANALYSIS_SCOPE",
              "experimental_authorization": False, "production_authorization": False}
    if coverage["status"] != "COVERAGE_APPROVED":
        if coverage["status"] == "SOURCE_AMBIGUOUS":
            result["adequacy"] = "NEEDS_CLARIFICATION"
        elif coverage["status"] == "SOURCE_CONFLICTING":
            result["adequacy"] = "CONFLICTING_REQUIREMENT"
        return result
    try:
        contract = bundle["contract"]
        if frc.review_gate(contract, fidelity_receipt) != "APPROVED":
            result["adequacy"] = "FIDELITY_NOT_APPROVED"
            return result
        bdi = discover(contract, bundle["interface"])
        sidecar = adequacy_sidecar(contract, bdi, coverage_reviewed=True)
        result.update(discovery=bdi, adequacy=analyze(contract, sidecar)["status"],
                      experimental_authorization=authorization(contract, fidelity_receipt, sidecar))
    except (KeyError, TypeError, ValueError, frc.ContractError) as exc:
        result["error"] = str(exc)
    return result
