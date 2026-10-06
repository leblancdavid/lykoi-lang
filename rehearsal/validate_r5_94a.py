"""Explicit non-held-out engineering evidence; exclusive creation, no activation of candidate."""
import argparse
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest

from lykoi_pipeline.controller import ROOT, digest
from lykoi_protected.portable_freeze import seal_snapshot, integrity, verify
from lykoi_runtime.verify import sha, verify_selected

DESTINATION = ROOT / "benchmark/results/phase5c/r5_94a"


def write(name, value):
    with (DESTINATION / name).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, sort_keys=True, indent=2) + "\n")


def stable(record):
    artifacts = list(record["artifacts"].values())
    def content(kind):
        return next(a["content"] for a in artifacts if a["type"] == kind)
    result = {"outcome": record["result"]["outcome"],
              "bdi_decisions": content("bdi")["result"]["decisions"],
              "adequacy_outcome": content("adequacy")["outcome"]}
    if record["result"]["outcome"] == "BEHAVIORALLY_VERIFIED":
        result.update(model_source_identity=content("model")["source_identity"],
                      target_sha256=content("target")["target_sha256"],
                      normalized_v1_identity=digest(content("v1")["normalized"]))
    return result


def run():
    DESTINATION.mkdir(parents=True, exist_ok=True)
    runtime = verify_selected(sys.executable)
    write("qualification.json", runtime)
    assert runtime["status"] == "RUNTIME_COMPATIBLE", runtime
    candidate = seal_snapshot()
    classification = {"EXACT_SEMANTIC_PIN": {"files": candidate["files"],
                         "body_fields": [key for key in candidate if key not in {"identity", "files", "runtime"}],
                         "opencode": candidate["runtime"]["opencode"]},
                      "COMPATIBILITY_CONTRACT": {"python": candidate["runtime"]["python_contract"]},
                      "PROVENANCE_ONLY": ["Python exact version", "Python executable path/SHA-256", "Python DLL/ZIP identities",
                                          "SQLite version", "platform/architecture particulars within contract scope"],
                      "note": "Exact executable OpenCode pin is retained; no replacement runtime behavior contract established for it"}
    write("dependency-classification.json", classification)
    write("protected-freeze-candidate.json", candidate)
    first = verify(candidate, sys.executable)
    write("verification.json", first)
    if not first["eligible"]:
        # Qualification is not permission to weaken unrelated exact dependencies.
        mismatches = []
        for path, pin in candidate["files"].items():
            actual = sha(ROOT / path)
            if actual != pin:
                data = (ROOT / path).read_bytes()
                import hashlib
                lf = data.replace(b"\r\n", b"\n")
                normalized = hashlib.sha256(lf).hexdigest()
                crlf = hashlib.sha256(lf.replace(b"\n", b"\r\n")).hexdigest()
                mismatches.append({"path": path, "expected_sha256": pin, "actual_sha256": actual,
                                   "LF_sha256": normalized, "LF_matches_historical": normalized == pin,
                                   "CRLF_sha256": crlf, "CRLF_matches_historical": crlf == pin,
                                   "representation_only": pin in (normalized, crlf)})
        executable = Path(candidate["models"]["roles"]["author"]["executable"])
        audit = {"file_mismatches": mismatches, "mismatch_count": len(mismatches),
                 "all_file_mismatches_explained_by_LF_CRLF": all(m["representation_only"] for m in mismatches),
                 "opencode": {
                 "path": str(executable), "expected": candidate["runtime"]["opencode"],
                 "actual_sha256": sha(executable),
                 "actual_version": subprocess.run([str(executable), "--version"], capture_output=True,
                                                  text=True, check=True).stdout.strip()}}
        write("exact-dependency-audit.json", audit)
        child = subprocess.run([sys.executable, "-X", "utf8", "-m", "rehearsal.validate_r5_94a", "check", "--destination", str(DESTINATION)],
                               cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=240)
        assert child.returncode == 1, child.stderr
        restart = json.loads(child.stdout)
        assert not restart["eligible"] and restart["runtime_qualification"]["status"] == "RUNTIME_COMPATIBLE"
        write("restart-verification.json", restart)
        inherited = json.loads((ROOT / "benchmark/results/phase5c/r5_94/final-checks.json").read_text())
        final = {"classification": "R5_94A_GENERIC_FREEZE_BLOCKED_EXACT_NON_PYTHON_DEPENDENCY_DRIFT",
                 "runtime_contract_implemented": True, "current_runtime_qualified": True,
                 "candidate_identity": candidate["identity"], "freeze_integrity": False,
                 "candidate_active": False, "target_authorizations": [],
                 "B03_round_counters": dict.fromkeys(inherited["B03_round_counters"], 0),
                 "B03_states": inherited["B03_states"],
                 "B03_counter_basis": "Inherited declaration plus this round's synthetic/public operations; no protected target or metadata inspected",
                 "evidence": {name: sha(DESTINATION / name) for name in ("qualification.json", "protected-freeze-candidate.json",
                              "verification.json", "exact-dependency-audit.json", "restart-verification.json", "dependency-classification.json")},
                 "stop": "CANDIDATE_CREATED_BUT_NOT_VERIFIED_EXACT_DEPENDENCIES_NOT_SUBSTITUTED"}
        write("final-checks.json", {**final, "identity": digest(final)})
        print(json.dumps(final))
        return
    sys.path.insert(0, str(ROOT / "tests"))
    import test_portable_runtime
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_portable_runtime)
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    with (DESTINATION / "portable-tests.txt").open("x", encoding="utf-8", newline="\n") as log:
        log.write(stream.getvalue())
    write("tests.json", {"tests": result.testsRun, "failures": [t.id() for t, _ in result.failures],
                         "errors": [t.id() for t, _ in result.errors], "skipped": len(result.skipped),
                         "log_sha256": sha(DESTINATION / "portable-tests.txt")})
    assert result.wasSuccessful() and not result.skipped, stream.getvalue()
    comparison = {"historical_runtime": "CPython 3.12.10 (preserved R5.94 evidence, NOT reexecuted)",
                  "current_runtime": runtime["provenance"], "comparisons": {}}
    for unsupported in (False, True):
        test = test_portable_runtime.PortableTests("test_synthetic_success_and_exact_roles")
        test.setUp()
        try:
            w, fid, _, _, auth = test.workspace(unsupported=unsupported)
            w.approve(test_portable_runtime.fixtures.CREDENTIALS["owner"], fid)
            seal = w.seal(fid)
            pipeline = test.pipeline(auth)
            prepared = pipeline.prepare(seal, test_portable_runtime.fixtures.RUN, review_rationale="Synthetic engineering calibration")
            outcome = prepared if unsupported else pipeline.execute(prepared)
            record = {"synthetic_only": True, "result": outcome, "artifacts": pipeline.audit(outcome)["artifacts"],
                      "journal": test.c.events(), "ledger": test.c.ledger(test_portable_runtime.fixtures.IDENTITY)}
            name = "unsupported.json" if unsupported else "success.json"
            write(name, record)
            historical_path = ROOT / "benchmark/results/phase5c/r5_94" / name
            historical = json.loads(historical_path.read_text(encoding="utf-8"))
            old, new = stable(historical), stable(record)
            assert old == new, (old, new)
            comparison["comparisons"][name] = {"historical_sha256": sha(historical_path), "old": old, "new": new, "equal": True}
        finally:
            test.tearDown()
    test = test_portable_runtime.PortableTests("test_provenance_invariance")
    test.setUp()
    try:
        test.test_provenance_invariance()
        invariant = test.invariance_evidence
        write("provenance-invariance.json", invariant)
        historical_path = ROOT / "benchmark/results/phase5c/r5_94/provenance-invariance.json"
        historical = json.loads(historical_path.read_text(encoding="utf-8"))
        keys = [k for k in invariant if k not in {"public_contract_identity", "protected_contract_identity"}]
        assert all(invariant[k] == historical[k] for k in keys)
        comparison["comparisons"]["provenance-invariance"] = {"historical_sha256": sha(historical_path),
                 "equal_fields": keys, "equal": True}
    finally:
        test.tearDown()
    comparison["limits"] = ["No second runtime available/executed; old runtime not retroactively contract-qualified",
                            "Envelope identities differ with new freeze dependencies; semantic normalized identity remains exact",
                            "Journal provenance, paths, runtime bytes, clocks and process timings are intentionally environment-dependent"]
    write("historical-comparison.json", comparison)
    assert integrity(candidate)
    assert first["eligible"]
    child = subprocess.run([sys.executable, "-X", "utf8", "-m", "rehearsal.validate_r5_94a", "check", "--destination", str(DESTINATION)],
                           cwd=ROOT, text=True, encoding="utf-8", capture_output=True, timeout=240)
    assert child.returncode == 0, child.stderr
    restart = json.loads(child.stdout)
    assert restart["eligible"] and restart["candidate_identity"] == candidate["identity"]
    write("restart-verification.json", restart)
    inherited = json.loads((ROOT / "benchmark/results/phase5c/r5_94/final-checks.json").read_text())
    final = {"classification": "R5_94A_PORTABLE_RUNTIME_CONTRACT_IMPLEMENTED", "candidate_identity": candidate["identity"],
             "candidate_active": False, "target_authorizations": [], "B03_round_counters": dict.fromkeys(inherited["B03_round_counters"], 0),
             "B03_states": inherited["B03_states"],
             "B03_counter_basis": "Inherited declaration plus exclusively synthetic/public operations; no target or protected metadata inspected",
             "evidence": {name: sha(DESTINATION / name) for name in ("qualification.json", "tests.json", "portable-tests.txt",
                         "success.json", "unsupported.json", "provenance-invariance.json", "historical-comparison.json",
                         "protected-freeze-candidate.json", "verification.json", "restart-verification.json")},
             "stop": "GENERIC_PORTABLE_FREEZE_VERIFIED_NO_TARGET_ACTIVATION_OR_AUTHORIZATION"}
    write("final-checks.json", {**final, "identity": digest(final)})
    print(json.dumps(final))


def check():
    candidate = json.loads((DESTINATION / "protected-freeze-candidate.json").read_text(encoding="utf-8"))
    result = verify(candidate, sys.executable)
    if (DESTINATION / "final-checks.json").is_file():
        final = json.loads((DESTINATION / "final-checks.json").read_text(encoding="utf-8"))
        assert final["identity"] == digest({k: v for k, v in final.items() if k != "identity"})
        assert all(sha(DESTINATION / path) == pin for path, pin in final["evidence"].items())
        assert not final["candidate_active"] and not final["target_authorizations"]
        assert all(v == 0 for v in final["B03_round_counters"].values())
        result["evidence_integrity"] = True
    print(json.dumps(result))
    return 0 if result["eligible"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run", "check"])
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    if args.destination:
        DESTINATION = args.destination.resolve()
    raise SystemExit(check() if args.command == "check" else run())
