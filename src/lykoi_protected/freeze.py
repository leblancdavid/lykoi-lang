"""Requirement-blind protected candidate; exact ordinary file allowlist only."""
import copy
import hashlib
import json

from lykoi_pipeline.controller import ROOT, digest
from lykoi_rehearsal.public_freeze_r5_91 import snapshot as public_snapshot
from . import VERSION, PURPOSE
from .policy import POLICY

EXTRA = (
    "src/lykoi_protected/__init__.py", "src/lykoi_protected/compatibility.py",
    "src/lykoi_protected/policy.py", "src/lykoi_protected/freeze.py",
    "src/lykoi_protected/controller.py", "src/lykoi_protected/workspace.py",
    "src/lykoi_protected/pipeline.py", "src/lykoi_protected/adapter.py",
    "schema/protected-evaluation-r5.94.schema.json", "docs/protected-evaluation-r5.94.md",
    "schema/formal-requirement-contract-protected-v0.1.schema.json",
    "tests/test_protected_evaluation.py", "rehearsal/validate_r5_94.py",
)


def snapshot():
    body = public_snapshot()
    body.update(version=VERSION, candidate="R5.94-GENERIC-PROTECTED-CANDIDATE-1", purpose=PURPOSE,
                active=False, protected_authorization=False, role_policy=copy.deepcopy(POLICY),
                validation_scope="SYNTHETIC_ENGINEERING_NOT_HELD_OUT_EVIDENCE")
    body["versions"].update(controller=VERSION, workspace=VERSION, pipeline=VERSION,
                            provenance="FormalRequirementContract-protected-0.1",
                            source_commitment_adapter=VERSION)
    body["schemas"]["protected_provenance"] = json.loads((ROOT / "schema/formal-requirement-contract-protected-v0.1.schema.json").read_text())
    body["schemas"]["protected_policy"] = json.loads((ROOT / "schema/protected-evaluation-r5.94.schema.json").read_text())
    for path in EXTRA:
        body["files"][path] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
    return body


def seal_snapshot():
    body = snapshot()
    return {**body, "identity": digest(body)}


def integrity(candidate):
    try:
        body = {k: v for k, v in candidate.items() if k != "identity"}
        return candidate["identity"] == digest(body) and body == snapshot()
    except (KeyError, OSError, ValueError, TypeError):
        return False
