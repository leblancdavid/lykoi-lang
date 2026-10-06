"""Bounded live qualification: one public/synthetic attempt per role, no retries."""
import argparse
import json
import io
import sys
import unittest

from lykoi_controller import Failure
from lykoi_pipeline.controller import ROOT, digest
from lykoi_freeze.opencode import requests, semantic_models
from lykoi_rehearsal.adapters import obj
from . import CONTRACT
from .adapter import WorkerAdapter
from .opencode import OpenCodeTransport

BASE = "benchmark/results/phase5c/r5_94b/final/protected-freeze-candidate.json"


def frozen_models():
    return json.loads((ROOT / BASE).read_text(encoding="utf-8"))["models"]


def qualify(transport, models):
    result = {"contract": CONTRACT, "status": "TRANSPORT_INCOMPATIBLE", "roles": {}, "failures": [],
              "scope": "PUBLIC_SYNTHETIC_ONLY", "protected_access": False,
              "model_configuration_identity": digest(models), "transport": transport.identity()}
    if models != frozen_models():
        result["failures"].append({"code": "FROZEN_MODEL_CONFIGURATION_DRIFT"})
        return result
    try:
        before = transport.provenance()
        result["provenance"] = before
    except (OSError, ValueError) as exc:
        result["failures"].append({"code": "TRANSPORT_IMPLEMENTATION_UNAVAILABLE", "reason": type(exc).__name__})
        return result
    sessions = set()
    for role, config in models["roles"].items():
        adapter = WorkerAdapter(role, config, transport)
        marker = "R5.94C-PUBLIC-" + role
        request = requests(role, adapter, marker)
        try:
            output = adapter.invoke(request, obj({"role": {"enum": [role]}, "marker": {"enum": [marker]}}))
            provenance = adapter.receipts[-1]["execution_provenance"]
            if not all(provenance.get(key) is True for key in
                       ("fresh_context_verified", "effective_instructions_tools_context_verified", "session_input_verified")):
                raise Failure("AI_BOUNDARY_EVIDENCE_UNAVAILABLE")
            session = provenance.get("session") or provenance.get("request_id")
            if not session or session in sessions:
                raise Failure("AI_NONFRESH_SESSION")
            sessions.add(session)
            result["roles"][role] = {"passed": True, "output": output, "receipt": adapter.receipts[-1]}
        except Failure as exc:
            result["roles"][role] = {"passed": False, "failure": exc.as_dict(), "receipts": adapter.receipts}
            result["failures"].append({"role": role, "failure": exc.as_dict()})
    try:
        if transport.provenance() != before:
            result["failures"].append({"code": "IMPLEMENTATION_DRIFT_DURING_QUALIFICATION"})
    except (OSError, ValueError) as exc:
        result["failures"].append({"code": "TRANSPORT_IMPLEMENTATION_UNAVAILABLE", "reason": type(exc).__name__})
    if not result["failures"] and len(sessions) == 4:
        result["status"] = "TRANSPORT_COMPATIBLE"
    return result


def contract_tests():
    sys.path.insert(0, str(ROOT / "tests"))
    stream = io.StringIO()
    suite = unittest.defaultTestLoader.loadTestsFromName("test_ai_transport")
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return {"passed": result.wasSuccessful() and not result.skipped, "count": result.testsRun, "log": stream.getvalue()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["verify"])
    parser.add_argument("--implementation", choices=["opencode"], required=True)
    parser.add_argument("--executable", required=True)
    args = parser.parse_args()
    tests = contract_tests()
    result = qualify(OpenCodeTransport(args.executable), frozen_models())
    result["contract_tests"] = tests
    if not tests["passed"]:
        result["status"] = "TRANSPORT_INCOMPATIBLE"
        result["failures"].append({"code": "CONTRACT_TESTS_FAILED"})
    print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "TRANSPORT_COMPATIBLE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
