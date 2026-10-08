"""Exact-bound local experiments. No controller, credentials, seals or grants.

Human decision/provenance is supplied by the caller, not authenticated here.
The separately retained approval is the trust input; receipts cannot approve
themselves. This API is for cooperative local research, not hostile-code isolation.
"""
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
from pathlib import Path
import subprocess
import sys
import tempfile

from air_compiler.parser import AirError
from air_compiler.profiles import author, generate
from lykoi_controller import Failure, canonical
from lykoi_pipeline import contracts, plans
from lykoi_pipeline.pipeline import external_execute


VERSION = "local-research-receipt-1"
PURPOSE = "local-research-only"
ROOT = Path(__file__).resolve().parents[2]
STAGES = ("frc", "structural_coverage", "bdi", "adequacy", "faithful_v1",
          "acceptance_coverage", "authoring", "compilation", "external_verification")
APPROVAL_FIELDS = {"requirement_id", "source_identity", "frc_identity",
                   "acceptance_identity", "human_statement", "provenance",
                   "evaluator", "purpose"}


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def implementation_snapshot():
    """Content provenance, not an environment qualification or runtime freeze."""
    paths = sorted((ROOT / "src").rglob("*.py"))
    paths += [ROOT / p for p in (
        "benchmark/evaluation/formal_requirements_r5_80.py",
        "benchmark/evaluation/behavioral_discovery_r5_82.py",
        "benchmark/evaluation/implementation_adequacy_r5_81.py",
        "benchmark/evaluation/benchmark_documents_v1.py",
        "air/task_manager.json", "benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json",
        "tests/test_local_research.py", "tests/test_scalar_normal_path.py",
        "tests/test_sealed_pipeline.py")]
    return {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in paths}


def receipt(approval):
    """Record an already supplied human approval; never creates human authority."""
    return {"version": VERSION, "approval": copy.deepcopy(approval),
            "implementation_snapshot": digest(implementation_snapshot()),
            "recorded_at_utc": datetime.now(timezone.utc).isoformat()}


def verify_receipt(record, approved, source, contract, plan, evaluator):
    if (type(record) is not dict or set(record) != {
            "version", "approval", "implementation_snapshot", "recorded_at_utc"}
            or record["version"] != VERSION):
        raise Failure("RESEARCH_RECEIPT_INVALID")
    if (type(approved) is not dict or set(approved) != APPROVAL_FIELDS
            or any(type(v) is not str or not v.strip() for v in approved.values())):
        raise Failure("RESEARCH_APPROVAL_INVALID")
    if record["approval"] != approved:
        raise Failure("RESEARCH_APPROVAL_MISMATCH")
    if approved["purpose"] != PURPOSE:
        raise Failure("RESEARCH_SCOPE_DENIED")
    if evaluator != approved["evaluator"]:
        raise Failure("RESEARCH_EVALUATOR_MISMATCH")
    for key, value in (("source_identity", source), ("frc_identity", contract),
                       ("acceptance_identity", plan)):
        if approved[key] != digest(value):
            raise Failure("RESEARCH_IDENTITY_MISMATCH", artifact=key)
    if source != contract.get("source"):
        raise Failure("RESEARCH_IDENTITY_MISMATCH", artifact="frc-source")
    if record["implementation_snapshot"] != digest(implementation_snapshot()):
        raise Failure("RESEARCH_SNAPSHOT_MISMATCH")
    try:
        stamp = datetime.fromisoformat(record["recorded_at_utc"])
        if stamp.utcoffset() is None or stamp.utcoffset().total_seconds() != 0:
            raise ValueError("UTC required")
    except (TypeError, ValueError):
        raise Failure("RESEARCH_RECEIPT_INVALID", field="recorded_at_utc") from None


def _author(normal, run, fixture):
    request = {"version": contracts.VERSION, "run": run, "v1": normal,
               "toolchain": {"compiler": "0.3.0", "semantics": "axiom-0.3"},
               "fixture": fixture}
    worker = ROOT / "src/lykoi_pipeline/author_worker.py"
    with tempfile.TemporaryDirectory(prefix="lykoi-local-author-") as tmp:
        try:
            result = subprocess.run([sys.executable, "-I", "-S", str(worker)],
                                    input=canonical(request).decode(), cwd=tmp,
                                    env={}, text=True, capture_output=True, timeout=10)
            if result.returncode:
                raise Failure("AUTHORING_FAILURE", stderr=result.stderr)
            from lykoi_controller.controller import parse_json
            output = parse_json(result.stdout)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise Failure("AUTHORING_FAILURE", reason=type(exc).__name__) from exc
    if "failure" in output:
        raise Failure(output["failure"], reason=output.get("reason"))
    if (set(output) != {"source", "run", "author_adapter", "isolation"}
            or output["run"] != run or output["author_adapter"] != "restricted-fixture-1"):
        raise Failure("AUTHORING_FAILURE")
    if normal.get("schema_version") == "LykoiContractV1" and output["source"] != author(normal):
        raise Failure("AUTHORING_FAILURE", reason="Unfaithful authorized profile")
    return output


def execute(record, approved, source, contract, plan, *, evaluator, run,
            author_fixture=None):
    """One experiment; stop at first native blocker. Return research data only.

    Plan and approved artifacts are copied before any worker runs. The author
    receives only V1/toolchain/explicit fixture, never the acceptance expectations.
    No callback can supply a purported successful semantic or verifier result.
    """
    record, approved, source, contract, plan = copy.deepcopy(
        (record, approved, source, contract, plan))
    result = {"version": "local-research-result-1", "purpose": PURPOSE,
              "production_authorized": False, "receipt_identity": digest(record),
              "run": run, "stages": {s: "NOT_REACHED" for s in STAGES},
              "evidence": {}}
    stage = "approval_integrity"
    try:
        verify_receipt(record, approved, source, contract, plan, evaluator)
        for stage in STAGES:
            result["stages"][stage] = "RUNNING"
            evidence = result["evidence"]
            if stage == "frc":
                evidence[stage] = contracts.frc.validate(contract)
                from lykoi_pipeline.query_profile import validate_relations
                validate_relations(contract)
                if contract["issues"]:
                    raise Failure("NEEDS_CLARIFICATION", issues=contract["issues"])
            elif stage == "structural_coverage":
                projection = contracts.structural(contract, approved["frc_identity"])
                evidence["structural"] = projection
                evidence[stage] = contracts.coverage(contract, projection)
            elif stage == "bdi":
                evidence[stage] = contracts.bdi(contract, evidence["structural"])
                if evidence[stage]["outcome"] != "SUPPORTED":
                    raise Failure("UNSUPPORTED_BDI_SCOPE", evidence=evidence[stage])
            elif stage == "adequacy":
                evidence[stage] = contracts.adequate(contract, evidence["bdi"])
                if evidence[stage]["outcome"] != "ADEQUATE":
                    raise Failure(evidence[stage]["result"]["status"], evidence=evidence[stage])
            elif stage == "faithful_v1":
                evidence[stage] = contracts.faithful_v1(contract)
                if evidence[stage]["outcome"] != "FAITHFUL_COMPLETE":
                    raise Failure("UNREPRESENTABLE_SOURCE")
            elif stage == "acceptance_coverage":
                # No fallback/generated plan, no change to approved expectations.
                if (type(plan) is not dict or plan.get("version") != plans.VERSION
                        or not {"cases", "coverage", "limitations"} <= set(plan)):
                    raise Failure("RESEARCH_ACCEPTANCE_BINDING_REQUIRED",
                                  reason="Exact approved native execution payload unavailable")
                from lykoi_pipeline import query_profile, scalar_profile, model_profile
                if any(p.applies(contract) for p in (query_profile, scalar_profile, model_profile)):
                    if plan.get("source_sha256") != source["sha256"]:
                        raise Failure("RESEARCH_IDENTITY_MISMATCH", artifact="plan-source")
                evidence[stage] = plans.review_coverage(contract, plan)
            elif stage == "authoring":
                verify_receipt(record, approved, source, contract, plan, evaluator)
                evidence[stage] = _author(evidence["faithful_v1"]["normalized"], run,
                                          copy.deepcopy(author_fixture))
            elif stage == "compilation":
                try:
                    target = generate(evidence["authoring"]["source"])
                except (AirError, ValueError, KeyError, TypeError) as exc:
                    raise Failure("COMPILATION_FAILURE", reason=str(exc)) from exc
                evidence[stage] = {"source_identity": digest(evidence["authoring"]["source"]),
                                   "target_sha256": hashlib.sha256(target.encode()).hexdigest()}
            else:
                verify_receipt(record, approved, source, contract, plan, evaluator)
                outcome, observations = external_execute(target, plan)
                evidence[stage] = {"outcome": outcome, "cases": observations,
                                   "acceptance_identity": digest(plan)}
                if outcome != "BEHAVIORALLY_VERIFIED":
                    raise Failure(outcome)
            result["stages"][stage] = "PASS"
        result["outcome"] = "BEHAVIORALLY_VERIFIED"
    except contracts.frc.ContractError as exc:
        result.update(outcome=exc.code, failure={"code": exc.code})
    except Failure as exc:
        result.update(outcome=exc.code, failure=exc.as_dict())
    if "failure" in result:
        result["first_blocker_stage"] = stage
        if stage in result["stages"]:
            result["stages"][stage] = "HALTED"
    result["completed_at_utc"] = datetime.now(timezone.utc).isoformat()
    return result
