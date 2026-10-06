"""Prepare real smoke evidence, then separately activate one public freeze."""
import json
import hashlib
from pathlib import Path

from lykoi_controller import Failure
from lykoi_pipeline.controller import ROOT, digest
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_rehearsal import verification
from lykoi_rehearsal.public_freeze_r5_91 import DIRECTORY, PURPOSE, configurations, seal_snapshot, eligibility
from lykoi_rehearsal.public_service_r5_91 import PublicController, ACTIVATION
from lykoi_rehearsal.service import public_author_seed


def write_new(path, value):
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def evidence():
    attempt = DIRECTORY / "attempt-3"
    result = json.loads((attempt / "results.json").read_text())
    assert result["roles"]["formalizer"]["status"] == "NATIVE_CANDIDATE_REGISTERED"
    assert result["roles"]["reviewer"]["status"] == "NATIVE_CANDIDATE_REGISTERED"
    assert result["roles"]["author"]["outcome"] == "BEHAVIORALLY_VERIFIED"
    assert result["roles"]["verifier"]["status"] == "CANDIDATE_REVIEWED_NOT_AUTHORITY"
    events = result["source_events"]
    committed = next(e["revision"] for e in events if e["type"] == "SOI_COMMITTED")
    reviewed = next(e["revision"] for e in events if e["type"] == "REVIEW_STARTED")
    assert committed < reviewed
    record = {"version": "live-role-smoke-r5.91-1", "status": "ROLE_INTEGRATION_SMOKE_ESTABLISHED",
              "scope": "PUBLIC_NON_SCORED_ADAPTER_INTEGRATION_NOT_MODEL_CERTIFICATION", "roles": {},
              "soi_commit_revision": committed, "review_start_revision": reviewed,
              "semantic_agreement_required": False, "future_requirement_selected": False,
              "development_attempts": ["attempt-1", "attempt-2", "attempt-3"],
              "same_model_correlated_errors_possible": True,
              "owner_freeze_authorization": "R5.91 user instruction to activate when infrastructure prerequisites satisfied"}
    for role in ("formalizer", "reviewer", "author", "verifier"):
        invocation = json.loads((attempt / (role + "-invocation.json")).read_text())
        assert len(invocation["receipts"]) == 1
        record["roles"][role] = {"receipt": invocation["receipts"][0],
                                 "result": result["roles"][role].get("status", result["roles"][role].get("outcome")),
                                 "evidence": "attempt-3/" + role + "-invocation.json"}
    reviewer_input = json.loads((attempt / "reviewer-invocation.json").read_text())["allowed_input"]
    assert set(reviewer_input) == {"role", "session", "source", "evidence", "output_schema", "instructions", "source_commitment", "source_span"}
    assert "candidate" not in reviewer_input
    author_input = json.loads((attempt / "author-input.json").read_text())
    assert set(author_input) == {"version", "run", "v1", "toolchain", "fixture"}
    verifier_input = json.loads((attempt / "verifier-input.json").read_text())
    assert set(verifier_input) == {"what", "what_seal", "profile_identity"}
    record["role_input_separation"] = "MECHANICALLY_CHECKED_ALLOWLISTS_NO_CANDIDATE_REVIEWER_NO_PLAN_AUTHOR_NO_IMPLEMENTATION_VERIFIER"
    record["reconciliation"] = result["reconciliation"]
    write_new(DIRECTORY / "smoke-integration.json", record)


def activate():
    checks = json.loads((DIRECTORY / "verification.json").read_text())
    if not checks["checks_passed_with_known_crlf_failures"]:
        raise Failure("FREEZE_FAILURE", reason="Required verification not passed")
    candidate = seal_snapshot()
    # The first activation's receipt publication failed on decimal test timings.
    # Retain that exact controller/freeze; never reuse or rewrite its identity.
    first_db = DIRECTORY / "public-controller.sqlite"
    if first_db.exists() and not (DIRECTORY / "activation-attempt-1.json").exists():
        first = json.loads((DIRECTORY / "public-freeze.json").read_text())
        old = PublicController(first_db, PRINCIPALS, candidate=first, model_configurations=configurations(), author_seed=public_author_seed())
        try:
            write_new(DIRECTORY / "activation-attempt-1.json", {"candidate_identity": first["identity"],
                      "activation": old.activation(), "events": old.events(), "future_requirement_selected": False,
                      "status": "ACTIVATED_RECEIPT_PUBLICATION_FAILED_NON_CANONICAL_DECIMAL_TIMINGS",
                      "retired_for_this_preparation": True, "requirement_admissions": 0,
                      "current_integrity": "STALE_AFTER_PROSPECTIVE_PUBLICATION_FIX_NEW_FREEZE_REQUIRED"})
        finally:
            old.close()
    db = DIRECTORY / "public-controller-final.sqlite"
    if db.exists():
        raise Failure("FREEZE_FAILURE", reason="Activation controller already exists")
    c = PublicController(db, PRINCIPALS, candidate=candidate, model_configurations=configurations(), author_seed=public_author_seed())
    try:
        check = eligibility(candidate, c)
        if not check["eligible"]:
            raise Failure("PUBLIC_REHEARSAL_INELIGIBLE", evidence=check)
        aid = c.execute(CREDENTIALS["owner"], "public", "register", expected_revision=c.revision,
                        kind="context", content={"version": ACTIVATION, "purpose": PURPOSE,
                                                  "candidate_identity": candidate["identity"], "active": True})
        c.execute(CREDENTIALS["owner"], "public", "adopt", expected_revision=c.revision, subject=aid)
        proof = c.prove_admission_order()
        assert proof["no_requirement_admitted"]
        write_new(DIRECTORY / "public-freeze-final.json", candidate)
        write_new(DIRECTORY / "activation.json", {"classification": "R5_91_PUBLIC_REHEARSAL_FROZEN",
                  "candidate": candidate["candidate"], "candidate_identity": candidate["identity"],
                  "activation": c.activation(), "order_proof": proof, "eligibility": check,
                  "verification_file_sha256": hashlib.sha256((DIRECTORY / "verification.json").read_bytes()).hexdigest(), "controller_events": c.events(),
                  "principal_scope": "Existing public prototype principals/role credentials; trusted local operator boundary",
                  "protected_authorization": False, "future_requirement_selected": False})
        print(json.dumps({"classification": "R5_91_PUBLIC_REHEARSAL_FROZEN", "freeze_identity": candidate["identity"], "activation": c.activation()}))
    finally:
        c.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["evidence", "activate"])
    args = parser.parse_args()
    evidence() if args.command == "evidence" else activate()
