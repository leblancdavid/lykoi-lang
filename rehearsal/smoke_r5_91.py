"""Small public non-scored real-role probes; never selects a rehearsal requirement."""
import copy
import json
from pathlib import Path
import sys
import tempfile

from lykoi_controller import Failure
from lykoi_pipeline.controller import ROOT, digest
from lykoi_pipeline.example import CREDENTIALS, PRINCIPALS
from lykoi_rehearsal.opencode_adapter import OpenCodeAdapter, normalize_plan
from lykoi_rehearsal.service import RehearsalController, RehearsalPipeline, public_author_seed
from lykoi_rehearsal import verification
from lykoi_workspace import Workspace


def write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def main(attempt):
    destination = ROOT / "benchmark/results/phase5c/r5_91" / attempt
    destination.mkdir(parents=True, exist_ok=False)
    config = json.loads((ROOT / "rehearsal/model-configurations-r5.91.json").read_text())
    roles = {r: OpenCodeAdapter(r, v) for r, v in config["roles"].items()}
    results = {"scope": "PUBLIC_NON_SCORED_ROLE_SMOKE_ONLY", "attempt": attempt, "roles": {},
               "future_requirement_selected": False, "protected_access": False}
    # Existing R5.89 title-only source; no new rehearsal requirement.
    with tempfile.TemporaryDirectory() as tmp:
        c = RehearsalController(Path(tmp) / "smoke.sqlite", PRINCIPALS,
                                model_configurations=config, author_seed=public_author_seed())
        try:
            w = Workspace(c, "public", "R5.91.public-smoke", CREDENTIALS)
            w.ingest(CREDENTIALS["owner"], "Create tasks with titles.")
            for role, action in (("formalizer", lambda: w.formalize(roles["formalizer"])),
                                 ("reviewer", lambda: w.commit_inventory(roles["reviewer"]))):
                try:
                    aid = action()
                    results["roles"][role] = {"status": "NATIVE_CANDIDATE_REGISTERED", "artifact": aid,
                                              "content": c.artifact(aid)["content"]}
                except Failure as exc:
                    results["roles"][role] = {"status": "REFUSED", "failure": exc.as_dict()}
            if results["roles"]["reviewer"]["status"] == "NATIVE_CANDIDATE_REGISTERED" and results["roles"]["formalizer"]["status"] == "NATIVE_CANDIDATE_REGISTERED":
                try:
                    results["reconciliation"] = w.reconcile(results["roles"]["reviewer"]["artifact"])
                except Failure as exc:
                    results["reconciliation"] = exc.as_dict()
            results["source_events"] = c.events()
        finally:
            c.close()
    # Reuse the already-authorized R5.89 public synthetic calibration helper.
    # Its fixture formalization/approval is explicitly not live AI evidence.
    sys.path.insert(0, str(ROOT / "tests"))
    from test_public_rehearsal import EndToEndTests
    case = EndToEndTests()
    case.setUp()
    case.c.close()
    case.config = config
    case.c = RehearsalController(Path(case.tmp.name) / "live-smoke.sqlite", PRINCIPALS,
                                 model_configurations=config, author_seed=public_author_seed())
    try:
        seal = case.workspace()
        p = RehearsalPipeline(case.c, "public", CREDENTIALS, roles["author"], mode="CALIBRATION")
        prepared = p.prepare(seal, "R5.91.author-smoke", review_rationale="Existing authorized public title-only calibration, not future rehearsal")
        results["authorized_calibration"] = prepared
        if prepared["outcome"] == "IMPLEMENTATION_AUTHORIZED":
            write(destination / "author-input.json", case.c.artifact(prepared["bundle"])["content"]["author_input"])
            result = p.execute(prepared)
            results["roles"]["author"] = result
        else:
            results["roles"]["author"] = {"status": "BUNDLE_UNAVAILABLE"}
        _, contract = case.c.what(seal)
        plan_request = {"what": contract, "what_seal": seal,
                        "profile_identity": digest(json.loads((ROOT / "rehearsal/public-capability-profile-1.json").read_text()))}
        write(destination / "verifier-input.json", plan_request)
        try:
            output = roles["verifier"].produce(plan_request)
            write(destination / "verifier-candidate.json", output)
            plan = normalize_plan(output["plan"])
            verification.review(contract, plan)
            results["roles"]["verifier"] = {"status": "CANDIDATE_REVIEWED_NOT_AUTHORITY", "plan": plan}
        except (Failure, KeyError, TypeError) as exc:
            results["roles"]["verifier"] = {"status": "REFUSED", "failure": exc.as_dict() if isinstance(exc, Failure) else type(exc).__name__}
        results["calibration_events"] = case.c.events()
    finally:
        case.tearDown()
    for role, adapter in roles.items():
        write(destination / (role + "-invocation.json"), {"attempts": adapter.attempts, "receipts": adapter.receipts,
              "candidate_text": adapter.last_output, "provenance": adapter.provenance, "allowed_input": adapter.last_input})
    write(destination / "results.json", results)
    print(json.dumps({"attempt": attempt, "roles": {r: x.get("status", x.get("outcome")) for r, x in results["roles"].items()}}))


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("attempt")
    main(parser.parse_args().attempt)
