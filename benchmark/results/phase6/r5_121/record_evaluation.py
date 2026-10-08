"""R5.121 evidence recorder; exact retained inputs, one terminal local attempt.

No semantic mappings, acceptance substitutions, controller calls or repair logic.
Run baseline first, then evaluate. Existing evidence is never overwritten.
"""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys

from lykoi_research import local

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
PHASE = HERE.parent
EXPECTED = {
    "frc": "69d32178bb065e1fa80ac6bb319a1147e3ac7c699a99bb0f56a6db52129ce0f8",
    "acceptance": "6d0551086fffacc52ce9c35f1d87b127ec181c06120f67b177eefe5f6a1406b3",
    "original_source": "90132320ad5aa7e7c3996ed97096a798a9ecceea76927a9f9c1948bda58d9970",
    "composite_source": "61f939652d67777081306ee0c9d3caeca47872f49af155bab9f2723838f3819a",
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    with (HERE / name).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def command(args):
    run = subprocess.run(args, cwd=ROOT, text=True, capture_output=True)
    return {"command": args, "exit_code": run.returncode,
            "stdout": run.stdout, "stderr": run.stderr}


def git(*args):
    result = command(["git", *args])
    assert result["exit_code"] == 0, result
    return result["stdout"].strip()


def retained_hashes():
    # Only authorized round evidence; no P6-A04/P6-A05 content access.
    paths = []
    for round_name in ("r5_119", "r5_119a", "r5_120", "r5_120a"):
        paths.extend(p for p in (PHASE / round_name).rglob("*")
                     if p.is_file() and "__pycache__" not in p.parts)
    paths.extend(PHASE / name for name in (
        "R5_119-REPORT.md", "R5_119A-REPORT.md", "R5_120-REPORT.md", "R5_120A-REPORT.md"))
    return {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(paths)}


def baseline():
    assert not (HERE / "SNAPSHOT.json").exists(), "Snapshot already recorded"
    checks = [command([sys.executable, "-m",
                       "benchmark.results.phase6.r5_119a.verify_revision"])]
    for folder, pattern in (
        ("tests", "test_local_research.py"),
        ("tests", "test_research_authority.py"),
        ("tests", "test_sealed_pipeline.py"),
        ("tests", "test_authority_controller.py"),
        ("tests", "test_compiler.py"),
        ("tests", "test_application.py"),
        ("tests", "test_scalar_normal_path.py"),
        ("benchmark/harness", "test_baseline.py"),
    ):
        checks.append(command([sys.executable, "-m", "unittest", "discover",
                               "-s", folder, "-p", pattern, "-v"]))
    for check in ("validate", "safety"):
        checks.append(command([sys.executable, "-m", "air_compiler.cli",
                               check, "air/task_manager.json"]))
    save("BASELINE-CHECKS.json", checks)
    assert all(c["exit_code"] == 0 for c in checks), "Baseline failed; stop"
    manifest = local.implementation_snapshot()
    accounting = ROOT / "benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json"
    assert load(accounting)["final_count"] == 26
    snapshot = {
        "round": "R5.121", "observed_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git("rev-parse", "HEAD"),
        "git_root_tree": git("rev-parse", "HEAD^{tree}"),
        "initial_working_tree": "CLEAN: initial git status --short empty",
        "working_tree_at_snapshot": git("status", "--porcelain=v1", "--untracked-files=all"),
        "git_objects": {p: git("rev-parse", "HEAD:" + p) for p in (
            "src", "src/air_compiler", "src/lykoi_pipeline", "src/lykoi_research",
            "src/lykoi_controller", "schema", "air", "generated", "tests",
            "benchmark/evaluation")},
        "implementation_manifest": manifest, "implementation_identity": local.digest(manifest),
        "kernel_concepts": 26, "kernel_accounting_path": accounting.relative_to(ROOT).as_posix(),
        "kernel_accounting_sha256": sha(accounting),
        "kernel_accounting_blob": git("rev-parse", "HEAD:" + accounting.relative_to(ROOT).as_posix()),
        "versions": {"compiler_backend": "0.3.0", "canonical_model": "0.3",
                     "normal_dispatcher": "LykoiProgram-1", "frc": "FormalRequirementContract-0.1",
                     "bdi": "BehavioralDecisionInventory-0.1", "adequacy": "ImplementationAdequacy-0.1",
                     "v1": "LykoiContractV1", "pipeline": "sealed-pipeline-1",
                     "local_receipt": local.VERSION, "external_plan": "external-cli-plan-1"},
        "model_provider": "OpenAI / openai/gpt-6.1-sol via OpenCode, session-reported",
        "python": sys.version, "platform": sys.platform,
        "baseline_checks": "BASELINE-CHECKS.json",
        "exposure": "Linked post-first-result, previously exposed in R5.116A/R5.119/R5.119A/R5.120; not blinded",
        "preserved_artifact_file_hashes": retained_hashes(), "production_authorized": False,
    }
    save("SNAPSHOT.json", snapshot)
    print(json.dumps({"baseline": "PASS", "snapshot": snapshot["implementation_identity"]}))


def evaluate():
    assert not (HERE / "LOCAL-EXECUTION-RECEIPT.json").exists(), "Attempt already started; no retry"
    snapshot = load(HERE / "SNAPSHOT.json")
    assert local.digest(local.implementation_snapshot()) == snapshot["implementation_identity"]
    assert retained_hashes() == snapshot["preserved_artifact_file_hashes"]
    contract = load(PHASE / "r5_119a/FRC-CANDIDATE-R2.json")
    plan = load(PHASE / "r5_119a/ACCEPTANCE-PLAN-R2.json")
    old_receipt = load(PHASE / "r5_120/APPROVAL-RECEIPT.json")
    original = PHASE / "r5_120/P6_A03_FIRST_RESULT.json"
    first = load(original)
    assert first["result"] == "NEEDS_CLARIFICATION"
    assert first["first_blocker"] == "RESEARCH_APPROVER_UNAVAILABLE"
    provenance = load(PHASE / "r5_116a/P6-A03-provenance.json")
    observed = {"frc": local.digest(contract), "acceptance": local.digest(plan),
                "original_source": sha(PHASE / "r5_116a" / provenance["source"]["path"]),
                "composite_source": hashlib.sha256(contract["source"]["text"].encode()).hexdigest()}
    assert observed == EXPECTED
    assert old_receipt["frc"]["canonical_sha256"] == observed["frc"]
    assert old_receipt["acceptance_plan"]["canonical_sha256"] == observed["acceptance"]
    approval = {
        "requirement_id": "P6-A03", "source_identity": local.digest(contract["source"]),
        "frc_identity": observed["frc"], "acceptance_identity": observed["acceptance"],
        "human_statement": old_receipt["explicit_statement"],
        "provenance": "Retained project-owner statement in r5_120/APPROVAL-RECEIPT.json; separately reauthorized by current user message R5.121 — P6-A03 Post-First-Result Semantic Evaluation, sections 1-2; current OpenCode session, conversation attribution only",
        "evaluator": "Current OpenCode coding-agent session / OpenAI openai/gpt-6.1-sol / R5.121",
        "purpose": local.PURPOSE,
    }
    save("APPROVAL-VERIFICATION.json", {
        "round": "R5.121", "status": "PASS", "expected": EXPECTED, "observed": observed,
        "source_record_canonical_sha256": approval["source_identity"],
        "source_record_identity_note": "Full FRC source record, distinct from composite text hash",
        "frc_file_sha256": sha(PHASE / "r5_119a/FRC-CANDIDATE-R2.json"),
        "acceptance_file_sha256": sha(PHASE / "r5_119a/ACCEPTANCE-PLAN-R2.json"),
        "retained_human_statement_receipt_sha256": sha(PHASE / "r5_120/APPROVAL-RECEIPT.json"),
        "approved": approval,
        "separate_attempt_authorization": {
            "provenance": "Current user message, R5.121 — P6-A03 Post-First-Result Semantic Evaluation",
            "exact_excerpts": ["Proceed with **R5.121 only**.",
                               "This is a **linked post-first-result evaluation**.",
                               "Use the existing recorded human approval and the R5.120A local research runner.",
                               "Record a new research-only execution receipt explicitly linked to the preserved P6-A03 first result."],
            "scope": "R5.121 only; exact unchanged revision-2 artifacts; stop at first terminal result",
        },
        "conversation_attribution_not_cryptographic_authentication": True,
        "original_first_result": {"path": original.relative_to(ROOT).as_posix(), "file_sha256": sha(original)},
        "artifact_regeneration": False, "production_authorized": False,
    })
    receipt = local.receipt(approval)
    local.verify_receipt(receipt, approval, contract["source"], contract, plan, approval["evaluator"])
    save("LOCAL-EXECUTION-RECEIPT.json", receipt)
    result = local.execute(receipt, approval, contract["source"], contract, plan,
                           evaluator=approval["evaluator"], run="R5.121/P6-A03/post-first-result/1")
    save("SEMANTIC-STAGE-EVIDENCE.json", result)
    record = {
        "record": "P6_A03_POST_FIRST_RESULT", "round": "R5.121",
        "round_classification": "R5_121_P6_A03_POST_FIRST_EVALUATION_COMPLETE",
        "attempt": "linked-post-first-result/1", "requirement": "P6-A03",
        "result": result["outcome"], "first_current_blocker": result.get("failure"),
        "first_current_blocker_stage": result.get("first_blocker_stage"),
        "blocker_kind": "STRUCTURAL_SEMANTIC_INTEGRATION" if result.get("first_blocker_stage") == "structural_coverage" else "SEE_NATIVE_EVIDENCE",
        "recorded_at_utc": result["completed_at_utc"],
        "original_first_result": {"path": original.relative_to(ROOT).as_posix(), "file_sha256": sha(original),
                                  "canonical_sha256": local.digest(first), "result": first["result"],
                                  "first_blocker": first["first_blocker"], "preserved": True},
        "approved_artifacts": observed,
        "implementation_snapshot": {"path": "SNAPSHOT.json", "file_sha256": sha(HERE / "SNAPSHOT.json"),
                                    "identity": snapshot["implementation_identity"], "git_commit": snapshot["git_commit"],
                                    "kernel_concepts": 26, "kernel_accounting_sha256": snapshot["kernel_accounting_sha256"]},
        "local_receipt": {"path": "LOCAL-EXECUTION-RECEIPT.json", "identity": local.digest(receipt),
                          "valid": True, "first_result_link": "APPROVAL-VERIFICATION.json"},
        "stages": result["stages"],
        "reached_stages": [s for s, status in result["stages"].items() if status != "NOT_REACHED"],
        "downstream_stages": {s: status for s, status in result["stages"].items() if status == "NOT_REACHED"},
        "semantic_evidence": {"path": "SEMANTIC-STAGE-EVIDENCE.json", "canonical_sha256": local.digest(result)},
        "executable_identity": result["evidence"].get("compilation"),
        "executable_software_produced": "compilation" in result["evidence"],
        "acceptance_results": result["evidence"].get("external_verification", {"status": "NOT_REACHED", "executions": 0, "observations": []}),
        "redis_compatible_acceptance": "NOT_REACHED; exact approved plan native_plan is null; no replacement payload",
        "behavioral_verification_performed": "external_verification" in result["evidence"],
        "exposure_provenance": snapshot["exposure"],
        "review_context": "Same-agent/model source interpretation; native code owns stage classification; no independent cognitive review claimed",
        "production_authorized": False,
        "immutability_policy": "Exclusive-create terminal publication; no repair/retry. File hash pinned in PUBLICATION-IDENTITIES.json; later attempts need separate authorization and linkage",
    }
    save("P6_A03_POST_FIRST_RESULT.json", record)
    assert local.digest(local.implementation_snapshot()) == snapshot["implementation_identity"]
    assert retained_hashes() == snapshot["preserved_artifact_file_hashes"]
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    {"baseline": baseline, "evaluate": evaluate}[sys.argv[1]]()
