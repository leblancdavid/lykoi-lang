"""Exclusive prospective publication; only explicit ordinary public inputs."""
import argparse
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from lykoi_pipeline.controller import ROOT, digest
from lykoi_freeze.freeze import build, preflight, verify_content
from lykoi_freeze.content import canonical_text, sha_bytes
from lykoi_runtime.verify import sha

DESTINATION = ROOT / "benchmark/results/phase5c/r5_94b/final"


def write(name, value):
    with (DESTINATION / name).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, sort_keys=True, indent=2) + "\n")


def run(executable):
    DESTINATION.mkdir(parents=True, exist_ok=False)
    sys.path.insert(0, str(ROOT / "tests"))
    stream = io.StringIO()
    suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(name) for name in ("test_portable_freeze", "test_portable_execution"))
    tests = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    write("tests.json", {"passed": tests.wasSuccessful() and not tests.skipped, "count": tests.testsRun, "log": stream.getvalue()})
    assert tests.wasSuccessful() and not tests.skipped, stream.getvalue()
    candidate = build(executable)
    write("protected-freeze-candidate.json", candidate)
    write("dependency-manifest.json", {"candidate_identity": candidate["identity"], "dependencies": candidate["dependencies"], "ambiguous": []})
    mirrors = {}
    # Copy only the audited ordinary manifest, never discover any target input.
    for representation in ("LF", "CRLF"):
        with tempfile.TemporaryDirectory(prefix="lykoi freeze mirror é ") as directory:
            root = Path(directory)
            for entry in candidate["dependencies"]:
                if entry["freeze_class"] != "CANONICAL_CONTENT_PIN" or "embedded_field" in entry:
                    continue
                relative = entry.get("locator", entry["dependency"])
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                data = canonical_text((ROOT / relative).read_bytes())
                target.write_bytes(data if representation == "LF" else data.replace(b"\n", b"\r\n"))
            check = verify_content(candidate, candidate["identity"], root)
            assert check["passed"], check
            mirrors[representation] = check
    comparison_path = "benchmark/results/phase5c/r5_94a/comparison-final/historical-comparison.json"
    previous = json.loads((ROOT / comparison_path).read_text(encoding="utf-8"))
    write("cross-machine-comparison.json", {"files": candidate["provenance"]["cross_machine_comparison"],
                                           "relocated_representation_mirrors": mirrors,
                                           "historical_python_evidence": {"path": comparison_path, "physical_sha256": sha(ROOT / comparison_path), "record": previous},
                                           "current_pipeline_comparison": "tests.json:test_semantic_outcomes_match_preserved_previous_runtime",
                                           "limits": "Mirrors are relocation/representation tests on the current computer, not execution on a second physical machine. Historical 3.12.10 outcomes are preserved evidence, not a new contract qualification.",
                                           "opencode_1_1_25_contract_equivalence": "NOT_ESTABLISHED_NOT_EXECUTED"})
    first = preflight(candidate, candidate["identity"], executable)
    write("verification.json", first)
    child = subprocess.run([sys.executable, "-X", "utf8", "-m", "rehearsal.validate_r5_94b", "check", "--opencode", executable,
                            "--expected-identity", candidate["identity"], "--destination", str(DESTINATION)],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=1200)
    try:
        restart = json.loads(child.stdout)
    except ValueError:
        restart = {"eligible": False, "error": "RESTART_INVALID_RESPONSE", "returncode": child.returncode, "stderr": child.stderr}
    write("restart-verification.json", restart)
    if first["eligible"] and restart["eligible"]:
        first_sessions = {r["session"] for r in first["opencode"]["roles"].values()}
        restart_sessions = {r["session"] for r in restart["opencode"]["roles"].values()}
        assert not first_sessions & restart_sessions, "Restart reused role sessions"
    inherited = json.loads((ROOT / "benchmark/results/phase5c/r5_94/final-checks.json").read_text(encoding="utf-8"))
    passed = first["eligible"] and restart["eligible"] and child.returncode == 0
    if passed:
        classification = "R5_94B_CROSS_MACHINE_PROTECTED_FREEZE_IMPLEMENTED"
    elif not first["content"]["passed"]:
        classification = "R5_94B_CANONICAL_OR_BINARY_PIN_VERIFICATION_FAILED"
    elif first.get("python", {}).get("status") != "RUNTIME_COMPATIBLE":
        classification = "R5_94B_PYTHON_RUNTIME_CONTRACT_FAILED"
    elif first.get("opencode", {}).get("status") != "OPENCODE_COMPATIBLE":
        classification = "R5_94B_OPENCODE_ADAPTER_CONTRACT_FAILED"
    else:
        classification = "R5_94B_FRESH_PROCESS_REVERIFICATION_FAILED"
    final = {"classification": classification,
             "candidate_identity": candidate["identity"], "candidate_active": False, "target_authorizations": [],
             "current_machine_eligible": passed, "B03_round_counters": dict.fromkeys(inherited["B03_round_counters"], 0),
             "B03_states": inherited["B03_states"],
             "B03_counter_basis": "Inherited pristine declaration plus exclusively ordinary/public/synthetic operations; no target or protected metadata inspected",
             "evidence": {p: sha(DESTINATION / p) for p in ("tests.json", "protected-freeze-candidate.json", "dependency-manifest.json", "cross-machine-comparison.json", "verification.json", "restart-verification.json")},
             "stop": "INACTIVE_GENERIC_FREEZE_ONLY_NO_TARGET_AUTHORIZATION"}
    write("final-checks.json", {**final, "identity": digest(final)})
    print(json.dumps(final))


def check(executable, expected):
    candidate = json.loads((DESTINATION / "protected-freeze-candidate.json").read_text(encoding="utf-8"))
    result = preflight(candidate, expected, executable)
    if (DESTINATION / "final-checks.json").is_file():
        final = json.loads((DESTINATION / "final-checks.json").read_text(encoding="utf-8"))
        assert final["identity"] == digest({k: v for k, v in final.items() if k != "identity"})
        assert all(sha(DESTINATION / name) == value for name, value in final["evidence"].items())
        assert not final["target_authorizations"] and all(v == 0 for v in final["B03_round_counters"].values())
        result["published_evidence_integrity"] = True
    print(json.dumps(result))
    return 0 if result["eligible"] else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run", "check"])
    parser.add_argument("--opencode", required=True)
    parser.add_argument("--expected-identity")
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    if args.destination:
        DESTINATION = args.destination.resolve()
    if args.command == "check" and not args.expected_identity:
        parser.error("check requires the externally approved --expected-identity")
    raise SystemExit(check(args.opencode, args.expected_identity) if args.command == "check" else run(args.opencode))
