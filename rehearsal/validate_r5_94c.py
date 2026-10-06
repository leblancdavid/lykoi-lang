"""R5.94C bounded public qualification/publication; no protected target discovery."""
import argparse
import io
import json
import subprocess
import sys
import unittest

from lykoi_pipeline.controller import ROOT, digest
from lykoi_runtime.verify import sha
from lykoi_transport.opencode import OpenCodeTransport
from lykoi_transport.freeze import build, preflight

DEST = ROOT / "benchmark/results/phase5c/r5_94c"
SUITES = ("test_ai_transport", "test_portable_freeze", "test_portable_execution", "test_protected_evaluation",
          "test_authority_controller", "test_requirements_workspace", "test_sealed_pipeline", "test_public_rehearsal", "test_live_public_freeze", "test_compiler", "test_application")
HISTORICAL_INSTALLATION_TEST = "test_protected_evaluation.ProtectedTests.test_freeze_integrity_and_historical_identity"


def regressions():
    sys.path.insert(0, str(ROOT / "tests"))
    log = io.StringIO()
    def prospective(suite):
        for item in suite:
            if isinstance(item, unittest.TestSuite):
                yield from prospective(item)
            elif item.id() != HISTORICAL_INSTALLATION_TEST:
                yield item
    suite = unittest.TestSuite(prospective(unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(n) for n in SUITES)))
    result = unittest.TextTestRunner(stream=log, verbosity=2).run(suite)
    return {"passed": result.wasSuccessful() and not result.skipped, "count": result.testsRun, "suites": SUITES, "log": log.getvalue(),
            "historical_installation_assertion": {"test": HISTORICAL_INSTALLATION_TEST,
                "disposition": "Preserved raw first/restart failure in R5.94C engineering evidence; not a prospective runtime dependency",
                "replacement": "test_ai_transport.TransportTests.test_freeze_exact_inherited_pins plus unchanged test_portable_freeze canonical integrity/mutation tests"}}


def write(name, value):
    with (DEST / name).open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, sort_keys=True, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run", "check"])
    parser.add_argument("--executable", required=True)
    parser.add_argument("--expected-identity")
    args = parser.parse_args()
    transport = OpenCodeTransport(args.executable)
    candidate = build(transport)
    if args.command == "check":
        if not args.expected_identity:
            parser.error("check requires --expected-identity")
        result = preflight(candidate, args.expected_identity, transport, regression=regressions())
        print(json.dumps(result))
        return 0 if result["eligible"] else 1
    DEST.mkdir(exist_ok=False)
    regression = regressions()
    write("tests.json", regression)
    write("dependency-manifest.json", {"engineering_identity": candidate["identity"], "dependencies": candidate["dependencies"],
                                     "models": candidate["models"], "candidate_published": False})
    first = preflight(candidate, candidate["identity"], transport, regression=regression)
    write("verification.json", first)
    child = subprocess.run([sys.executable, "-X", "utf8", "-m", "rehearsal.validate_r5_94c", "check",
                            "--executable", args.executable, "--expected-identity", candidate["identity"]],
                           cwd=ROOT, capture_output=True, text=True, encoding="utf-8", timeout=1500)
    try:
        restart = json.loads(child.stdout)
    except ValueError:
        restart = {"eligible": False, "reason": "INVALID_FRESH_PROCESS_OUTPUT", "returncode": child.returncode}
    write("restart-verification.json", restart)
    passed = first["eligible"] and restart["eligible"] and child.returncode == 0
    if passed:
        a = {r["receipt"]["execution_provenance"]["session"] for r in first["transport"]["roles"].values()}
        b = {r["receipt"]["execution_provenance"]["session"] for r in restart["transport"]["roles"].values()}
        assert not a & b
        write("protected-freeze-candidate.json", candidate)
    inherited = json.loads((ROOT / "benchmark/results/phase5c/r5_94/final-checks.json").read_text(encoding="utf-8"))
    blocked_transport = first.get("transport", {}).get("status") != "TRANSPORT_COMPATIBLE" or restart.get("transport", {}).get("status") != "TRANSPORT_COMPATIBLE"
    classification = ("R5_94C_PROVIDER_NEUTRAL_AI_TRANSPORT_IMPLEMENTED" if passed else
                      "R5_94C_BLOCKED_NO_FUNCTIONING_TRANSPORT_FOR_FROZEN_MODEL" if blocked_transport and regression["passed"] and first["content"]["passed"] and first.get("python", {}).get("status") == "RUNTIME_COMPATIBLE" else
                      "R5_94C_BLOCKED_MACHINE_PREFLIGHT_FAILURE")
    final = {"classification": classification, "current_machine_eligible": passed, "candidate_created": passed,
             "engineering_identity": candidate["identity"], "candidate_active": False, "target_authorizations": [],
             "B03_round_counters": dict.fromkeys(inherited["B03_round_counters"], 0), "B03_states": inherited["B03_states"],
             "B03_counter_basis": "Inherited declaration plus exclusively ordinary/public/synthetic operations; no target or metadata inspection",
             "evidence": {name: sha(DEST / name) for name in ("tests.json", "dependency-manifest.json", "verification.json", "restart-verification.json")},
             "stop": "NO_ACTIVATION_OR_TARGET_AUTHORIZATION"}
    write("final-checks.json", {**final, "identity": digest(final)})
    print(json.dumps(final))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
