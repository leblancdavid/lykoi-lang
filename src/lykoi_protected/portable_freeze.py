"""Prospective R5.94A freeze. Historical snapshots are never rewritten."""
import copy
import json
from pathlib import Path

from lykoi_pipeline.controller import ROOT, digest
from lykoi_runtime.verify import contract_pin, sha, verify_selected

HISTORICAL = "benchmark/results/phase5c/r5_94/protected-freeze-candidate.json"
EXTRA = ("src/lykoi_runtime/__init__.py", "src/lykoi_runtime/verify.py",
         "src/lykoi_protected/portable_freeze.py", "src/lykoi_protected/portable_controller.py",
         "rehearsal/python-runtime-contract-v1.json", "docs/python-runtime-contract-v1.md",
         "tests/test_portable_runtime.py", "rehearsal/validate_r5_94a.py",
         "tests/test_authority_controller.py", "tests/test_requirements_workspace.py",
         "tests/test_compiler.py", "tests/test_application.py",
         "generated/task_manager.py", "generated/task_manager.manifest.json")


def snapshot():
    original = json.loads((ROOT / HISTORICAL).read_text(encoding="utf-8"))
    assert original["identity"] == digest({k: v for k, v in original.items() if k != "identity"})
    body = copy.deepcopy(original)
    body.pop("identity")
    body.update(version="protected-portable-freeze-r5.94a-1", candidate="R5.94A-GENERIC-PROTECTED-CANDIDATE-2",
                supersedes=original["identity"])
    # Python eligibility is the contract. OpenCode remains exact: it executes
    # frozen role/configuration behavior and has no qualified replacement contract.
    body["runtime"] = {"python_contract": contract_pin(), "opencode": original["runtime"]["opencode"]}
    body["files"][HISTORICAL] = sha(ROOT / HISTORICAL)
    body["files"].update({path: sha(ROOT / path) for path in EXTRA})
    return body


def seal_snapshot():
    body = snapshot()
    return {**body, "identity": digest(body)}


def integrity(candidate):
    """Semantic integrity only; eligibility additionally requires qualification."""
    try:
        body = {k: v for k, v in candidate.items() if k != "identity"}
        if candidate["identity"] != digest(body) or body != snapshot():
            return False
        if any(sha(ROOT / path) != pin for path, pin in body["files"].items()):
            return False
        executable = Path(body["models"]["roles"]["author"]["executable"])
        return sha(executable) == body["runtime"]["opencode"]["executable_sha256"]
    except (KeyError, OSError, ValueError, TypeError, AssertionError):
        return False


def verify(candidate, interpreter=None):
    runtime = verify_selected(interpreter)
    intact = integrity(candidate)
    return {"eligible": intact and runtime["status"] == "RUNTIME_COMPATIBLE",
            "freeze_integrity": intact, "candidate_identity": candidate.get("identity"),
            "runtime_qualification": runtime, "active": False, "target_authorizations": []}
