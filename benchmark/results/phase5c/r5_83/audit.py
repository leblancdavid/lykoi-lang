"""R5.83 read-only public audit: no grants, static consumers or protected IO.

Synthetic false coverage attestations are negative controls, never approvals.
Print evidence to stdout; do not write or repair upstream artifacts.
"""
import copy
import hashlib
import json
from pathlib import Path

from benchmark.evaluation import formal_requirements_r5_80 as frc
from benchmark.evaluation.behavioral_discovery_r5_82 import discover, adequacy_sidecar
from benchmark.evaluation.implementation_adequacy_r5_81 import analyze, authorization

ROOT = Path(__file__).resolve().parents[4]
# Exact ordinary-file allowlist. No requirements, protected ledgers or discovery.
PINS = (
    "docs/requirement-formalization-boundary-v1.md",
    "docs/formal-requirement-contract-v0.1.md",
    "docs/behavioral-decision-inventory-v0.1.md",
    "docs/implementation-adequacy-v0.1.md",
    "docs/benchmark-document-contract-v1.md",
    "docs/axiom-v0.3.md",
    "schema/axiom-v0.3.schema.json",
    "schema/formal-requirement-contract-v0.1.schema.json",
    "schema/benchmark-document-contract-v1.schema.json",
    "benchmark/evaluation/formal_requirements_r5_80.py",
    "benchmark/evaluation/behavioral_discovery_r5_82.py",
    "benchmark/evaluation/implementation_adequacy_r5_81.py",
    "benchmark/evaluation/benchmark_documents_v1.py",
    "benchmark/evaluation/phase5_runner_v2.py",
    "benchmark/semantic/profile_audit_r5_41.py",
    "src/air_compiler/__init__.py",
    "src/air_compiler/cli.py",
    "src/air_compiler/generator.py",
    "src/air_compiler/model.py",
    "src/air_compiler/parser.py",
    "src/air_compiler/planning.py",
    "src/air_compiler/runtime_template.py",
    "src/air_compiler/semantics.py",
    "src/air_compiler/validator.py",
    "benchmark/results/phase5c/r5_80/candidates.json",
    "benchmark/results/phase5c/r5_80/reviews.json",
    "benchmark/results/phase5c/R5_83-HELD-OUT-EXPOSURE-READINESS.md",
    "benchmark/results/phase5c/r5_83/PRECOMMITMENT.md",
    "benchmark/results/phase5c/r5_83/audit.py",
)


def synthetic_probe():
    store = "Store the supplied value durably."
    event = "Emit exactly one public event per successful call."
    source = store + " " + event
    contract = {
        "schema_version": frc.VERSION, "contract_id": "R5.83-SYNTHETIC-EVENT",
        "revision": 1,
        "source": {"id": "R5.83-SYNTHETIC-EVENT", "text": source,
                   "sha256": hashlib.sha256(source.encode()).hexdigest(),
                   "classification": "SYNTHETIC"},
        "context": {"scope": "Sequential successful-call diagnostic only; durable value and public event count",
                    "domains": {"value": "integer"}, "assumptions": [],
                    "component_authority": None},
        "obligations": [
            {"id": "S.O1", "basis": "STATED", "source_quote": store,
             "derived_from": [], "relation": {"kind": "persist", "parameters": {"result": "durable value"}},
             "statement": store},
            {"id": "S.O2", "basis": "STATED", "source_quote": event,
             "derived_from": [], "relation": {"kind": "effects", "parameters": {"event_count": 1}},
             "statement": event},
        ],
        "issues": [], "unspecified": [], "implementation_choices": [],
        "lineage": [], "formalizer": "synthetic-negative-control-author", "review": None,
    }
    receipt = {"contract_commitment": frc.digest(contract),
               "reviewer": "synthetic-bookkeeping-reviewer", "outcome": "APPROVED",
               "checks": {k: True for k in frc.CHECKS}, "findings": []}
    interface = {"operations": [{"id": "store",
        "facts": {"persist": {"value": True, "origin": ["S.O1"], "evidence": store},
                  "failure_after_write": {"value": False, "origin": ["synthetic.context.scope"],
                                          "evidence": "Successful-call-only diagnostic domain; not full failure coverage"}},
        "channels": {"later": "MEANINGFUL"},
        "authority": {"persistence": {"authority": "DETERMINED", "allowed": ["durable"],
                                     "source_quote": store}}}]}

    def result(value, reviewed):
        bdi = discover(contract, value)
        sidecar = adequacy_sidecar(contract, bdi, reviewed)
        return {"unknown": bdi["unknown"],
                "decisions": [d["family"] for d in bdi["decisions"]],
                "adequacy": analyze(contract, sidecar)["status"],
                "authorization_helper": authorization(contract, receipt, sidecar)}

    declared = copy.deepcopy(interface)
    declared["operations"][0]["channels"]["events"] = "MEANINGFUL"
    excluded = copy.deepcopy(interface)
    excluded["operations"][0]["channels"]["events"] = "EXCLUDED"
    records = {
        "frc_bookkeeping": frc.review_gate(contract, receipt),
        "declared_events": result(declared, True),
        "omitted_events_default_coverage": result(interface, False),
        "omitted_events_false_coverage_attestation": result(interface, True),
        "excluded_events_false_scope_attestation": result(excluded, True),
    }
    assert records["frc_bookkeeping"] == "APPROVED"
    assert records["declared_events"]["adequacy"] == "OUTSIDE_ANALYSIS_SCOPE"
    assert not records["declared_events"]["authorization_helper"]
    assert records["omitted_events_default_coverage"]["adequacy"] == "OUTSIDE_ANALYSIS_SCOPE"
    for key in ("omitted_events_false_coverage_attestation", "excluded_events_false_scope_attestation"):
        assert records[key]["unknown"] == []
        assert records[key]["adequacy"] == "IMPLEMENTATION_ADEQUATE"
        assert records[key]["authorization_helper"]
    records["interpretation"] = (
        "False attestations are intentionally invalid under the review protocol. "
        "These are helper outputs, not real approvals/grants or implementation success. "
        "The mechanics cannot establish source-to-interface completeness or truthful exclusions."
    )
    return records


def b01_probe():
    # Only already-public candidate/receipt. No B01 implementation or oracle.
    base = ROOT / "benchmark/results/phase5c/r5_80"
    contract = json.loads((base / "candidates.json").read_text(encoding="utf-8"))["B01"]
    reviews = json.loads((base / "reviews.json").read_text(encoding="utf-8"))
    receipt = reviews["receipts"]["B01"]
    interface = {"operations": [{"id": "priority-lifecycle", "facts": {
        "creation_default": {"value": True, "origin": ["B01.O08"], "evidence": "Conditional creation context"},
        "historical_absence": {"value": True, "origin": ["B01.O07", "B01.I1"], "evidence": "Unresolved historical admission; conditional only"}},
        "channels": {"later": "MEANINGFUL"}}]}
    bdi = discover(contract, interface)
    sidecar = adequacy_sidecar(contract, bdi)
    sidecar["issues"] = [{"kind": "AMBIGUITY", "reason": "B01.I1 default trigger domain unresolved"}]
    fidelity = frc.review_gate(contract, receipt)
    status = analyze(contract, sidecar)["status"]
    authorized = authorization(contract, receipt, sidecar)
    assert fidelity == status == "NEEDS_CLARIFICATION" and not authorized
    assert [d["family"] for d in bdi["decisions"]] == ["default_trigger_domain"]
    return {"fidelity": fidelity, "conditional_decision": "default_trigger_domain",
            "adequacy_diagnostic": status, "authorization_helper": authorized,
            "downstream_authoring": "NOT_RUN", "qualification": "KNOWN_PUBLIC_CONDITIONAL_CALIBRATION"}


def run():
    return {
        "pipeline_version": "R5.83-CANDIDATE-1",
        "classification": "R5_83_B03_EXPOSURE_NOT_READY",
        "pins_exact_physical_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in PINS},
        "unsupported_scope_probe": synthetic_probe(),
        "B01": b01_probe(),
        "limits": "Coordinating public audit; no isolated independent review, end-to-end implementation or acceptance run. Pins are an audited component snapshot, not a complete executable-run closure.",
        "B03": {"status": ["B03_PRISTINE", "B03_NOT_EVALUATED", "B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT"],
                "accounting_basis": "Scoped session activity plus inherited status; no protected ledger or metadata inspection",
                "source_access_attempts": 0, "source_reads": 0, "content_revealing_metadata": 0,
                "formalization": 0, "discovery": 0, "adequacy": 0, "authorization": 0,
                "reservations": 0, "packaging": 0, "opening": 0, "consumer_observation": 0,
                "generation": 0, "execution": 0, "acceptance": 0, "repair": 0},
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
