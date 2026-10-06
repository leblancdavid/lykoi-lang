"""Public/synthetic interface challenges; fixtures never qualify a live transport."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from lykoi_controller import Failure
from lykoi_pipeline.controller import digest
from lykoi_rehearsal.adapters import obj
from lykoi_freeze.opencode import requests, negative_controls
from lykoi_transport.adapter import WorkerAdapter, ProtectedWorkerAdapter, Result
from lykoi_transport.verify import frozen_models, qualify
from lykoi_transport.freeze import build, verify_content
from lykoi_transport.execution import ExecutionGuard, NeutralProtectedController


class SyntheticTransport:
    def __init__(self):
        self.calls = []
        self.failure = None
        self.route = "github-copilot/claude-sonnet-4.6"
        self.version = "synthetic-not-live"

    def identity(self):
        return {"implementation": "synthetic-test-only", "version": self.version}

    def provenance(self):
        return self.identity()

    def invoke(self, invocation):
        self.calls.append(invocation)
        output = {k: s["enum"][0] for k, s in invocation.schema["properties"]["output"].get("properties", {}).items() if "enum" in s}
        return Result(None if self.failure else {"binding": invocation.inputs["binding"], "output": output}, self.failure,
                      {"session": invocation.request_id, "request_id": invocation.request_id, "actual_model_route": self.route,
                       "fresh_context_verified": True, "effective_instructions_tools_context_verified": True, "session_input_verified": True})


class TransportTests(unittest.TestCase):
    def setUp(self):
        self.transport = SyntheticTransport()
        self.models = frozen_models()

    def adapter(self, role):
        return WorkerAdapter(role, self.models["roles"][role], self.transport)

    def test_all_four_role_allowlists(self):
        for role, forbidden in (("formalizer", "repository"), ("reviewer", "candidate_frc"),
                                ("author", "hidden_verification"), ("author", "original_prose"), ("verifier", "implementation")):
            with self.subTest(role=role, forbidden=forbidden):
                adapter = self.adapter(role)
                request = requests(role, adapter, "synthetic-boundary")
                request[forbidden] = {"canary": "NOT_DELIVERED"}
                with self.assertRaises(Failure):
                    adapter.produce(request)
                self.assertFalse(self.transport.calls)
                self.assertEqual(adapter.receipts[-1]["status"], "FAILURE")

    def test_exact_inputs_and_instructions(self):
        from lykoi_rehearsal.opencode_adapter import role_prompt
        adapter = self.adapter("formalizer")
        request = requests("formalizer", adapter, "synthetic-exact")
        adapter.invoke(request, obj({"role": {"enum": ["formalizer"]}}))
        invocation = self.transport.calls[0]
        self.assertEqual(invocation.inputs["input"], request)
        self.assertEqual(invocation.instructions, role_prompt("formalizer"))
        self.assertEqual(invocation.configuration, self.models["roles"]["formalizer"])

    def test_failure_never_returns_candidate_and_records_provenance(self):
        self.transport.failure = {"reason": "SYNTHETIC_PROVIDER_DOWN"}
        adapter = self.adapter("formalizer")
        with self.assertRaises(Failure):
            adapter.produce(requests("formalizer", adapter, "synthetic-failure"))
        self.assertEqual(adapter.receipts[-1]["status"], "FAILURE")
        self.assertNotIn("output_identity", adapter.receipts[-1])
        self.assertIn("execution_provenance", adapter.receipts[-1])

    def test_transport_exception_explicit_failure(self):
        adapter = self.adapter("formalizer")
        with patch.object(self.transport, "invoke", side_effect=TimeoutError("not persisted")), self.assertRaises(Failure):
            adapter.produce(requests("formalizer", adapter, "synthetic-timeout"))
        self.assertEqual(adapter.receipts[-1]["status"], "FAILURE")
        self.assertNotIn("output_identity", adapter.receipts[-1])

    def test_failure_with_fabricated_candidate_rejected(self):
        adapter = self.adapter("formalizer")
        with patch.object(self.transport, "invoke", return_value=Result({}, {"reason": "down"}, {})), self.assertRaises(Failure) as caught:
            adapter.produce(requests("formalizer", adapter, "synthetic-fabrication"))
        self.assertEqual(caught.exception.code, "AI_TRANSPORT_CONTRACT_VIOLATION")

    def test_structured_binding_and_schema_reject(self):
        for envelope in ({"binding": "WRONG", "output": {}}, {"binding": "correct", "output": []}):
            adapter = self.adapter("formalizer")
            def invoke(call):
                value = copy.deepcopy(envelope)
                if value["binding"] == "correct":
                    value["binding"] = call.inputs["binding"]
                return Result(value, None, {})
            with patch.object(self.transport, "invoke", side_effect=invoke), self.assertRaises(Failure):
                adapter.produce(requests("formalizer", adapter, "synthetic-malformed"))

    def test_model_substitution_fails(self):
        self.transport.route = "another/model"
        adapter = self.adapter("formalizer")
        with self.assertRaises(Failure) as caught:
            adapter.invoke(requests("formalizer", adapter, "synthetic-route"), obj({}))
        self.assertEqual(caught.exception.code, "AI_MODEL_ROUTE_MISMATCH")

    def test_success_provenance_and_untrusted_output(self):
        adapter = self.adapter("verifier")
        adapter.invoke(requests("verifier", adapter, "synthetic-provenance"), obj({}))
        receipt = adapter.receipts[-1]
        for key in ("transport", "configured_model", "instruction_identity", "schema_identity", "configuration_identity",
                    "input_identity", "input_artifacts", "request_id", "execution_provenance", "output_identity"):
            self.assertIn(key, receipt)
        self.assertEqual(receipt["authority"], "UNTRUSTED_CANDIDATE")

    def test_protected_commitment_classification_preserved(self):
        adapter = ProtectedWorkerAdapter("reviewer", self.models["roles"]["reviewer"], self.transport, classification="SYNTHETIC")
        request = requests("reviewer", adapter, "synthetic-commitment")
        self.assertEqual(adapter._request(request), self.adapter_with_session(adapter)._request(request))

    def adapter_with_session(self, other):
        adapter = self.adapter(other.role)
        adapter.session = other.session
        return adapter

    def test_opencode_execution_failure_controls(self):
        with patch("lykoi_rehearsal.opencode_adapter.Path.is_file", return_value=True):
            self.assertEqual(len(negative_controls({**self.models["roles"]["formalizer"], "executable": "synthetic"})), 8)

    def test_qualification_bounded_failure_all_roles(self):
        self.transport.failure = {"reason": "synthetic-down"}
        result = qualify(self.transport, self.models)
        self.assertEqual(len(self.transport.calls), 4)
        self.assertEqual(len(result["failures"]), 4)
        self.assertEqual(result["status"], "TRANSPORT_INCOMPATIBLE")

    def test_frozen_config_change_blocks_without_invocation(self):
        self.models["roles"]["author"]["model"] = "different"
        self.assertEqual(qualify(self.transport, self.models)["status"], "TRANSPORT_INCOMPATIBLE")
        self.assertFalse(self.transport.calls)

    def test_optional_implementation_interface(self):
        result = qualify(self.transport, self.models)
        self.assertEqual(result["status"], "TRANSPORT_COMPATIBLE")
        self.assertEqual(len(result["roles"]), 4)

    def test_freeze_exact_inherited_pins(self):
        candidate = build(self.transport)
        self.assertTrue(verify_content(candidate, candidate["identity"])["passed"])
        candidate["dependencies"][0]["content_sha256"] = "0" * 64
        from lykoi_freeze.freeze import semantic_body
        candidate["identity"] = digest(semantic_body(candidate))
        self.assertFalse(verify_content(candidate, candidate["identity"])["passed"])

    def test_transport_drift_requires_requalification(self):
        candidate = build(self.transport)
        from lykoi_runtime.verify import provenance
        check = {"eligible": True, "python": {"provenance": provenance()}, "transport": {"provenance": self.transport.provenance()}}
        with patch("lykoi_transport.execution.preflight", return_value=check) as mocked:
            guard = ExecutionGuard(candidate, candidate["identity"], self.transport, {"passed": True})
            self.transport.version = "changed"
            mocked.return_value = {"eligible": False}
            with self.assertRaises(Failure):
                guard.ensure()
            self.assertEqual(mocked.call_count, 2)


class NeutralPipelineTests(unittest.TestCase):
    def test_unchanged_protected_pipeline_and_boundaries(self):
        import test_protected_evaluation as fixtures
        from lykoi_rehearsal.service import public_author_seed
        from lykoi_runtime.verify import provenance
        transport = SyntheticTransport()
        candidate = build(transport)
        class Fixture(fixtures.ProtectedTests):
            def open(inner, candidate=None):
                return NeutralProtectedController(inner.path, fixtures.PRINCIPALS, candidate=candidate or inner.candidate,
                    expected_identity=inner.candidate["identity"], transport=transport, regression={"passed": True},
                    model_configurations=inner.config, author_seed=public_author_seed())
        with patch("lykoi_transport.execution.preflight", return_value={"eligible": True, "python": {"provenance": provenance()},
                                                                     "transport": {"provenance": transport.provenance()}}):
            for name in ("test_synthetic_success_and_exact_roles", "test_unsupported_mapping_halts_without_grant",
                         "test_reviewer_candidate_before_commitment_denied", "test_author_original_source_denied_and_audited", "test_provenance_invariance"):
                with self.subTest(check=name), tempfile.TemporaryDirectory() as directory:
                    case = Fixture()
                    case.tmp = SimpleNamespace(name=directory)
                    case.path = Path(directory) / "synthetic.sqlite"
                    case.candidate, case.config = candidate, candidate["models"]
                    case.c = case.open()
                    try:
                        getattr(case, name)()
                    finally:
                        case.c.close()
