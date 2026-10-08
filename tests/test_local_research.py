"""R5.120A public/synthetic qualification; no Phase 6 source access."""
import ast
import copy
import hashlib
import inspect
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lykoi_controller import Controller, Failure, canonical
from lykoi_research import local
from lykoi_workspace.scalar_corpus import captures, obligations
from lykoi_pipeline.scalar_profile import PROFILE
from test_scalar_normal_path import independent_plan
from test_sealed_pipeline import calibration, verification_fixture, author_fixture


def positive_contract():
    record = captures()[0]
    contract = {"schema_version": local.contracts.frc.VERSION,
                "contract_id": "R5.120A/public-library", "revision": 1,
                "source": {"id": "public-synthetic-library/R5.102",
                           "text": record["source"], "classification": "SYNTHETIC",
                           "sha256": hashlib.sha256(record["source"].encode()).hexdigest()},
                "context": {"scope": "Public synthetic scalar registry",
                            "domains": {"capability_profile": PROFILE},
                            "assumptions": [], "component_authority": None},
                "obligations": obligations(record), "issues": [], "unspecified": [],
                "implementation_choices": [], "lineage": [],
                "formalizer": "R5.120A/same-agent-synthetic", "review": None}
    return contract, independent_plan(record)


def inputs(contract=None, plan=None):
    if contract is None:
        contract, plan = positive_contract()
    source = copy.deepcopy(contract["source"])
    approved = {"requirement_id": "R5.120A-SYNTHETIC",
                "source_identity": local.digest(source),
                "frc_identity": local.digest(contract),
                "acceptance_identity": local.digest(plan),
                "human_statement": "Synthetic qualification approval: execute this exact public contract and plan for local research only.",
                "provenance": "R5.120A user instruction authorizes synthetic qualification; test statement is role simulation, not a real source approval or authentication.",
                "evaluator": "R5.120A-local-synthetic-evaluator", "purpose": local.PURPOSE}
    return local.receipt(approved), approved, source, contract, plan


def run(args, **kwargs):
    return local.execute(*args, evaluator=args[1]["evaluator"], run="r5-120a-synthetic", **kwargs)


class LocalResearchTests(unittest.TestCase):
    def test_valid_receipt_and_positive_external_execution(self):
        args = inputs()
        local.verify_receipt(*args, evaluator=args[1]["evaluator"])
        before = copy.deepcopy(args)
        result = run(args)
        self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)
        self.assertTrue(all(v == "PASS" for v in result["stages"].values()))
        self.assertEqual(args, before)
        self.assertFalse(result["production_authorized"])
        self.assertNotIn("grant", result)
        self.assertEqual(len(result["evidence"]["external_verification"]["cases"]), 5)

    def test_exact_bindings_and_approval_statement(self):
        for index, field in ((2, "id"), (3, "contract_id"), (4, "limitations")):
            with self.subTest(index=index):
                args = list(inputs())
                args[index][field] = "modified" if index != 4 else ["modified"]
                result = run(args)
                self.assertEqual(result["outcome"], "RESEARCH_IDENTITY_MISMATCH")
                self.assertTrue(all(v == "NOT_REACHED" for v in result["stages"].values()))
        args = inputs()
        args[0]["approval"]["human_statement"] += " substituted"
        self.assertEqual(run(args)["outcome"], "RESEARCH_APPROVAL_MISMATCH")
        args = inputs()
        args[0]["approval"]["provenance"] = "pretend authenticated"
        self.assertEqual(run(args)["outcome"], "RESEARCH_APPROVAL_MISMATCH")

    def test_modified_acceptance_expectation_rejected_before_authoring(self):
        args = inputs()
        args[4]["cases"][0]["steps"][0]["returncode"] = 7
        with patch.object(local, "_author") as author:
            self.assertEqual(run(args)["outcome"], "RESEARCH_IDENTITY_MISMATCH")
            author.assert_not_called()

    def test_scope_evaluator_snapshot_and_timestamp(self):
        args = inputs()
        args[1]["purpose"] = "production"
        args[0]["approval"] = copy.deepcopy(args[1])
        self.assertEqual(run(args)["outcome"], "RESEARCH_SCOPE_DENIED")
        args = inputs()
        result = local.execute(*args, evaluator="other", run="wrong-evaluator")
        self.assertEqual(result["outcome"], "RESEARCH_EVALUATOR_MISMATCH")
        args = inputs()
        args[0]["implementation_snapshot"] = {}
        self.assertEqual(run(args)["outcome"], "RESEARCH_SNAPSHOT_MISMATCH")
        for timestamp in ("bad", "2026-10-08T12:00:00", "2026-10-08T12:00:00+01:00"):
            args = inputs()
            args[0]["recorded_at_utc"] = timestamp
            self.assertEqual(run(args)["outcome"], "RESEARCH_RECEIPT_INVALID")

    def test_legitimate_structural_and_bdi_halts(self):
        for kind, params, outcome, stage in (
                ("sum", {"inputs": "integers"}, "STRUCTURAL_COVERAGE_FAILURE", "structural_coverage"),
                ("effects", {"events": True}, "UNSUPPORTED_BDI_SCOPE", "bdi")):
            contract = calibration()
            contract["obligations"][0]["relation"] = {"kind": kind, "parameters": params}
            args = inputs(contract, verification_fixture(contract))
            with patch.object(local, "_author") as author:
                result = run(args)
                self.assertEqual(result["outcome"], outcome, result)
                self.assertEqual(result["first_blocker_stage"], stage)
                self.assertEqual(result["stages"]["authoring"], "NOT_REACHED")
                author.assert_not_called()

    def test_adequacy_and_v1_halts(self):
        contract = calibration()
        contract["obligations"][0]["relation"] = {
            "kind": "priority_create", "parameters": {"condition": "priority omitted", "result": "UNRESOLVED"}}
        result = run(inputs(contract, verification_fixture(contract)))
        self.assertEqual(result["outcome"], "IMPLEMENTATION_UNDERSPECIFIED", result)
        self.assertEqual(result["first_blocker_stage"], "adequacy")
        contract["obligations"][0]["relation"]["parameters"]["result"] = "NORMAL"
        result = run(inputs(contract, verification_fixture(contract)))
        self.assertEqual(result["outcome"], "UNREPRESENTABLE_SOURCE", result)
        self.assertEqual(result["first_blocker_stage"], "faithful_v1")

    def test_frc_issues_and_malformed_frc_not_waived(self):
        args = inputs()
        args[3]["issues"] = [{"id": "question", "category": "QUESTION", "description": "Unresolved",
                              "affects": [], "alternatives": [], "witness": None, "resolved": False}]
        args[1]["frc_identity"] = local.digest(args[3])
        args[0]["approval"] = copy.deepcopy(args[1])
        self.assertEqual(run(args)["outcome"], "NEEDS_CLARIFICATION")
        args[3]["revision"] = 0
        args[1]["frc_identity"] = local.digest(args[3])
        args[0]["approval"] = copy.deepcopy(args[1])
        self.assertEqual(run(args)["outcome"], "MALFORMED_FRC")

    def test_wrong_but_compilable_external_failure(self):
        contract = calibration()
        result = run(inputs(contract, verification_fixture(contract)), author_fixture=author_fixture())
        self.assertEqual(result["outcome"], "BEHAVIORAL_VERIFICATION_FAILURE", result)
        self.assertEqual(result["stages"]["compilation"], "PASS")
        self.assertEqual(result["first_blocker_stage"], "external_verification")
        self.assertFalse(result["evidence"]["external_verification"]["cases"][0]["steps"][0]["passed"])

    def test_missing_or_inadequate_acceptance_cannot_author(self):
        args = inputs()
        args[4]["coverage"].pop()
        args[1]["acceptance_identity"] = local.digest(args[4])
        args[0]["approval"] = copy.deepcopy(args[1])
        with patch.object(local, "_author") as author:
            result = run(args)
            self.assertEqual(result["outcome"], "VERIFICATION_PLAN_COVERAGE_GAP")
            author.assert_not_called()

    def test_missing_native_payload_is_a_blocker_not_generated(self):
        contract = calibration()
        result = run(inputs(contract, {"native_plan": None}))
        self.assertEqual(result["outcome"], "RESEARCH_ACCEPTANCE_BINDING_REQUIRED")
        self.assertEqual(result["stages"]["authoring"], "NOT_REACHED")

    def test_compilation_failure_keeps_verification_unreached(self):
        contract = calibration()
        result = run(inputs(contract, verification_fixture(contract)),
                     author_fixture=author_fixture("malformed"))
        self.assertEqual(result["outcome"], "COMPILATION_FAILURE", result)
        self.assertEqual(result["stages"]["external_verification"], "NOT_REACHED")

    def test_production_rejects_receipts_and_no_journal_changes(self):
        principals = {"service": {"credential": "synthetic-production-controller",
                                  "roles": ["controller", "owner"], "projects": ["public"]}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "production.sqlite"
            c = Controller(path, principals)
            try:
                args = inputs()
                for command in ("approve_research", "grant", "seal_frc"):
                    with self.assertRaises(Failure) as caught:
                        c.execute(canonical(args[0]).decode(), "public", command,
                                  expected_revision=c.revision, subject=local.digest(args[0]))
                    self.assertEqual(caught.exception.code, "UNAUTHENTICATED")
                for command in ("grant", "seal_frc"):
                    with self.assertRaises(Failure):
                        c.execute("synthetic-production-controller", "public", command,
                                  expected_revision=c.revision, subject=local.digest(args[0]))
                for kind in (local.VERSION, "approval", "research_approval", "grant", "frc_seal"):
                    with self.assertRaises(Failure) as caught:
                        c.execute("synthetic-production-controller", "public", "register",
                                  expected_revision=c.revision, kind=kind, content=args[0])
                    self.assertEqual(caught.exception.code, "RESERVED_OR_UNKNOWN_TYPE")
                context = c.execute("synthetic-production-controller", "public", "register",
                                    expected_revision=c.revision, kind="context", content=args[0])
                with self.assertRaises(Failure) as caught:
                    c.execute("synthetic-production-controller", "public", "grant",
                              expected_revision=c.revision, subject=context)
                self.assertEqual(caught.exception.code, "TYPE_MISMATCH")
                self.assertFalse(c.applicable(local.digest(args[0]), "subject", "freeze")["applicable"])
                # Production itself journals refusals. Measure research execution
                # separately, after those intentionally attempted production calls.
                before = (path.read_bytes(), c.revision, c.events())
                self.assertEqual(run(args)["outcome"], "BEHAVIORALLY_VERIFIED")
                self.assertEqual((path.read_bytes(), c.revision, c.events()), before)
            finally:
                c.close()

    def test_no_controller_or_grant_dispatch_surface(self):
        tree = ast.parse(inspect.getsource(local))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                self.assertFalse(any(n.name in {"Controller", "PipelineController", "Pipeline"} for n in node.names))
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                self.assertNotIn(node.func.attr, {"execute", "grant", "_put", "_register"})
        self.assertEqual(set(inspect.signature(local.execute).parameters), {
            "record", "approved", "source", "contract", "plan", "evaluator", "run", "author_fixture"})


if __name__ == "__main__":
    unittest.main()
