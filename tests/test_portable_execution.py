"""Meaningful negative controls for process-local qualification and transport drift."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lykoi_controller import Failure
from lykoi_freeze.execution import ExecutionGuard, QualifiedOpenCodeAdapter
from lykoi_freeze.opencode import semantic_models, negative_controls
from lykoi_rehearsal.public_freeze_r5_91 import configurations
from lykoi_pipeline.controller import ROOT, digest
from lykoi_runtime.verify import provenance
from lykoi_freeze.freeze import build
from lykoi_freeze.execution import CrossMachineProtectedController
from lykoi_freeze.execution import QualifiedProtectedOpenCodeAdapter
from lykoi_rehearsal.opencode_adapter import OpenCodeAdapter
from lykoi_freeze.opencode import requests
from lykoi_rehearsal.service import public_author_seed
import test_protected_evaluation as fixtures


class ExecutionTests(unittest.TestCase):
    def setUp(self):
        self.models = semantic_models(configurations())
        self.actual = {"python": {"runtime": "synthetic-a"}, "opencode": {"artifact": "synthetic-a"}}
        self.check = {"eligible": True, "python": {"provenance": self.actual["python"]}, "opencode": {"provenance": self.actual["opencode"]}}
        self.patches = [patch("lykoi_freeze.execution.preflight", return_value=self.check),
                        patch("lykoi_freeze.execution.provenance", return_value=self.actual["python"]),
                        patch("lykoi_freeze.execution.tool_provenance", return_value=self.actual["opencode"]),
                        patch("lykoi_freeze.execution.verify_content", return_value={"passed": True})]
        self.mocks = [p.start() for p in self.patches]
        for p in self.patches:
            self.addCleanup(p.stop)
        self.guard = ExecutionGuard({"models": self.models}, "synthetic-id", "synthetic-artifact")

    def test_unchanged_machine_does_not_requalify(self):
        self.guard.ensure()
        self.assertEqual(self.mocks[0].call_count, 1)

    def test_tool_change_requalifies_and_failed_contract_blocks(self):
        self.mocks[2].return_value = {"artifact": "replacement"}
        self.mocks[0].return_value = {"eligible": False}
        with self.assertRaises(Failure) as caught:
            self.guard.ensure()
        self.assertEqual(caught.exception.code, "MACHINE_INELIGIBLE")
        self.assertEqual(self.mocks[0].call_count, 2)

    def test_runtime_change_requalifies(self):
        new = {"runtime": "replacement"}
        self.mocks[1].return_value = new
        self.mocks[0].return_value = {**self.check, "python": {"provenance": new}}
        self.assertEqual(self.guard.ensure()["python"], new)
        self.assertEqual(self.mocks[0].call_count, 2)

    def test_new_process_guard_does_not_reuse_qualification(self):
        ExecutionGuard({"models": self.models}, "synthetic-id", "synthetic-artifact")
        self.assertEqual(self.mocks[0].call_count, 2)

    def test_content_drift_blocks_before_worker(self):
        self.mocks[3].return_value = {"passed": False}
        with self.assertRaises(Failure) as caught:
            self.guard.ensure()
        self.assertEqual(caught.exception.code, "PROTECTED_FREEZE_DRIFT")

    def test_model_substitution_rejected(self):
        changed = copy.deepcopy(self.models["roles"]["author"])
        changed["model"] = "different-model"
        with self.assertRaises(Failure):
            QualifiedOpenCodeAdapter("author", changed, self.guard)

    def test_transport_path_not_semantic_configuration(self):
        role = "author"
        adapter = QualifiedOpenCodeAdapter(role, self.models["roles"][role], self.guard)
        self.assertNotIn("executable", adapter.config)
        self.assertNotIn("cli_version", adapter.config)
        self.assertEqual(adapter.config["model"], "claude-sonnet-4.6")

    def test_invocation_and_receipt_bind_semantic_config_separately(self):
        adapter = QualifiedOpenCodeAdapter("author", self.models["roles"]["author"], self.guard)
        request = requests("author", adapter, "synthetic-receipt")
        def invoke(payload):
            self.assertEqual(adapter.config["executable"], str(Path("synthetic-artifact").resolve()))
            bound = json.loads(payload["messages"][1]["content"])
            adapter.cli_session = "synthetic-fresh-session"
            return {"choices": [{"message": {"content": json.dumps({"binding": bound["binding"], "output": {"source": {}}})}}]}
        with patch.object(OpenCodeAdapter, "_invoke", side_effect=invoke):
            adapter.produce(request)
        self.assertEqual(adapter.config, self.models["roles"]["author"])
        self.assertEqual(adapter.receipts[-1]["configuration_identity"], digest(adapter.config))
        self.assertEqual(adapter.receipts[-1]["machine_provenance"], self.actual)

    def test_transport_error_restores_semantic_configuration(self):
        adapter = QualifiedOpenCodeAdapter("author", self.models["roles"]["author"], self.guard)
        with patch.object(OpenCodeAdapter, "_invoke", side_effect=Failure("AI_EXECUTION_FAILURE")):
            with self.assertRaises(Failure):
                adapter._invoke({})
        self.assertEqual(adapter.config, self.models["roles"]["author"])

    def test_protected_reviewer_commitment_preserves_classification(self):
        adapter = QualifiedProtectedOpenCodeAdapter("reviewer", self.models["roles"]["reviewer"], self.guard,
                                                   classification="SYNTHETIC")
        request = requests("reviewer", adapter, "synthetic-reviewer")
        bound = adapter._request(request)
        self.assertNotIn("candidate_frc", bound)
        baseline = OpenCodeAdapter("reviewer", self.models["roles"]["reviewer"])
        baseline.session = adapter.session
        self.assertEqual(bound["source_commitment"], baseline._request(request)["source_commitment"])


class SyntheticPipelineTests(unittest.TestCase):
    """Actual unchanged pipeline, synthetic workers; not a live eligibility receipt."""
    def setUp(self):
        actual = {"python": provenance(), "opencode": {"version": "SYNTHETIC_MOCK_NOT_ELIGIBILITY", "path": "synthetic", "sha256": "0" * 64}}
        qualified = {"eligible": True, "python": {"provenance": actual["python"]}, "opencode": {"provenance": actual["opencode"]}}
        for target, value in (("lykoi_freeze.freeze.tool_provenance", actual["opencode"]),
                              ("lykoi_freeze.execution.tool_provenance", actual["opencode"]),
                              ("lykoi_freeze.execution.preflight", qualified)):
            p = patch(target, return_value=value)
            p.start()
            self.addCleanup(p.stop)
        candidate = build("synthetic")
        config = candidate["models"]

        class Fixture(fixtures.ProtectedTests):
            def setUp(inner):
                inner.tmp = tempfile.TemporaryDirectory()
                inner.path = Path(inner.tmp.name) / "cross-machine-synthetic.sqlite"
                inner.candidate, inner.config = candidate, config
                inner.c = inner.open()

            def open(inner, candidate=None):
                return CrossMachineProtectedController(inner.path, fixtures.PRINCIPALS, candidate=candidate or inner.candidate,
                            expected_identity=inner.candidate["identity"], executable="synthetic",
                            model_configurations=inner.config, author_seed=public_author_seed())

        self.case = Fixture()
        self.case.setUp()
        self.addCleanup(self.case.tearDown)

    def test_supported_pipeline_and_restart(self):
        self.case.test_synthetic_success_and_exact_roles()

    def test_unsupported_scope_unchanged(self):
        self.case.test_unsupported_mapping_halts_without_grant()

    def test_source_blind_reviewer_before_commitment(self):
        self.case.test_reviewer_candidate_before_commitment_denied()

    def test_author_raw_source_denied(self):
        self.case.test_author_original_source_denied_and_audited()

    def test_controller_copy_cannot_reseal_a_changed_candidate(self):
        from lykoi_freeze.freeze import semantic_body
        self.case.c.candidate["semantics"]["role_policy"]["raw"].append("author")
        self.case.c.candidate["identity"] = digest(semantic_body(self.case.c.candidate))
        with self.assertRaises(Failure) as caught:
            self.case.activate()
        self.assertEqual(caught.exception.code, "PROTECTED_FREEZE_DRIFT")
        self.assertFalse(self.case.c.events())

    def test_provenance_does_not_change_semantics(self):
        self.case.test_provenance_invariance()

    def test_semantic_outcomes_match_preserved_previous_runtime(self):
        # Compare generated bytes and normalized semantics, not envelope IDs,
        # timing, installation facts or mock qualification.
        from rehearsal.validate_r5_94a import stable
        for unsupported in (False, True):
            if unsupported:
                # Independent synthetic controller/session, never rerun a source.
                self.case.c.close()
                self.case.path = Path(self.case.tmp.name) / "unsupported.sqlite"
                self.case.c = self.case.open()
            w, fid, _, _, auth = self.case.workspace(unsupported=unsupported)
            w.approve(fixtures.CREDENTIALS["owner"], fid)
            seal = w.seal(fid)
            pipeline = self.case.pipeline(auth)
            prepared = pipeline.prepare(seal, fixtures.RUN, review_rationale="Synthetic portability comparison")
            outcome = prepared if unsupported else pipeline.execute(prepared)
            record = {"result": outcome, "artifacts": pipeline.audit(outcome)["artifacts"]}
            name = "unsupported.json" if unsupported else "success.json"
            historical = json.loads((ROOT / "benchmark/results/phase5c/r5_94" / name).read_text(encoding="utf-8"))
            self.assertEqual(stable(record), stable(historical))
