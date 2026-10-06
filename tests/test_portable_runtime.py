"""Prospective runtime tests reuse synthetic protected challenges unchanged."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import test_protected_evaluation as fixtures
from lykoi_controller import Failure
from lykoi_pipeline.controller import ROOT, digest
from lykoi_protected.portable_controller import PortableProtectedController
from lykoi_protected.portable_freeze import seal_snapshot, integrity
from lykoi_rehearsal.service import public_author_seed
from lykoi_rehearsal.public_freeze_r5_91 import configurations
from lykoi_runtime.verify import contract_pin, provenance, selected, verify_selected
from lykoi_protected import portable_freeze
from lykoi_runtime.verify import sha

PRODUCTION_SNAPSHOT = portable_freeze.snapshot


def calibration_snapshot():
    """Exact local synthetic pins; never a production/historical substitution.

    Positive controller tests require a locally intact synthetic freeze, just as
    historical tests snapshot their current installation. Actual inherited freeze
    drift is tested independently without this fixture. Mock workers never invoke
    the differently installed OpenCode executable.
    """
    body = PRODUCTION_SNAPSHOT()
    body["candidate"] = "SYNTHETIC_PORTABLE_RUNTIME_CALIBRATION_NOT_A_PROTECTED_FREEZE"
    body["files"] = {path: sha(ROOT / path) for path in body["files"]}
    executable = Path(body["models"]["roles"]["author"]["executable"])
    body["runtime"]["opencode"]["executable_sha256"] = sha(executable)
    body["runtime"]["opencode"]["version"] = "SYNTHETIC_MOCK_WORKERS_NO_LIVE_EXECUTION"
    return body


class PortableTests(fixtures.ProtectedTests):
    def setUp(self):
        self.calibration = patch("lykoi_protected.portable_freeze.snapshot", side_effect=calibration_snapshot)
        self.calibration.start()
        self.addCleanup(self.calibration.stop)
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "portable.sqlite"
        self.candidate = seal_snapshot()
        self.config = configurations()
        self.c = self.open()

    def open(self, candidate=None):
        return PortableProtectedController(self.path, fixtures.PRINCIPALS, candidate=candidate or self.candidate,
                     model_configurations=self.config, author_seed=public_author_seed())

    def test_freeze_integrity_and_historical_identity(self):
        self.assertTrue(integrity(self.candidate))
        changed = copy.deepcopy(self.candidate)
        changed["role_policy"]["raw"].append("author")
        changed["identity"] = digest({k: v for k, v in changed.items() if k != "identity"})
        self.assertFalse(integrity(changed))
        historical = json.loads((ROOT / "benchmark/results/phase5c/r5_94/protected-freeze-candidate.json").read_text())
        self.assertEqual(self.candidate["supersedes"], historical["identity"])
        production = PRODUCTION_SNAPSHOT()
        for path, pin in historical["files"].items():
            self.assertEqual(production["files"][path], pin)

    def test_exact_file_drift_rejected_even_with_resealed_body(self):
        changed = copy.deepcopy(self.candidate)
        changed["files"]["src/air_compiler/validator.py"] = "0" * 64
        changed["identity"] = digest({k: v for k, v in changed.items() if k != "identity"})
        self.assertFalse(integrity(changed))

    def test_contract_substitution_denied(self):
        changed = copy.deepcopy(self.candidate)
        changed["runtime"]["python_contract"]["version"] = "UNQUALIFIED_CONTRACT"
        changed["identity"] = digest({k: v for k, v in changed.items() if k != "identity"})
        self.assertFalse(integrity(changed))

    def test_runtime_provenance_not_component_identity(self):
        before = self.c.components()
        self.assertEqual(before["tools"], {"python_contract": contract_pin()})
        self.c.runtime_provenance = {"synthetic_different_runtime": True}
        self.assertEqual(before, self.c.components())
        self.c.runtime_provenance = provenance()
        self.activate()
        event = self.c.events()[-1]
        receipt = self.c.events()[-2]
        self.assertEqual(receipt["type"], "RUNTIME_EXECUTION_PROVENANCE")
        self.assertEqual(receipt["evidence"]["provenance"], provenance())
        self.assertEqual(receipt["evidence"]["operation_revision"], event["revision"])
        self.assertNotIn("execution_runtime", self.c.artifact(event["subject"])["content"])

    def test_incompatible_runtime_denies_before_activation(self):
        with patch("lykoi_protected.portable_controller.verify_selected", return_value={"status": "RUNTIME_INCOMPATIBLE"}):
            with self.assertRaises(Failure) as caught:
                self.open()
        self.assertEqual(caught.exception.code, "RUNTIME_INCOMPATIBLE")
        self.assertFalse(self.c.events())

    def test_changed_runtime_must_requalify_before_dispatch(self):
        self.c.runtime_provenance = {"stale": True}
        with patch("lykoi_protected.portable_controller.verify_selected", return_value={"status": "RUNTIME_INCOMPATIBLE"}) as probe:
            with self.assertRaises(Failure):
                self.activate()
        probe.assert_called_once()
        self.assertFalse(self.c.events())


class SelectionTests(unittest.TestCase):
    def test_unavailable_interpreter_structured_failure(self):
        result = verify_selected(str(ROOT / "nonexistent-runtime-contract-interpreter.exe"))
        self.assertEqual(result["status"], "RUNTIME_INCOMPATIBLE")
        self.assertEqual(result["failures"][0]["requirement"], "qualification_process")
        self.assertFalse(result["provenance"]["executed"])

    def test_explicit_environment_current_selection(self):
        import sys
        with patch.dict("os.environ", {"LYKOI_PYTHON": "configured interpreter"}):
            self.assertEqual(selected(), "configured interpreter")
            self.assertEqual(selected("explicit interpreter"), "explicit interpreter")
        with patch.dict("os.environ", {}, clear=True):
            self.assertEqual(selected(), sys.executable)
