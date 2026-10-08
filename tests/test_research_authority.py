"""R5.118A synthetic-only authority controls. No external requirement access."""
from __future__ import annotations

import copy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from lykoi_controller import Controller, Failure
from lykoi_pipeline.controller import PipelineController
from lykoi_workspace import Workspace
from lykoi_pipeline import Pipeline
from lykoi_pipeline.example import PRINCIPALS as PIPELINE_PRINCIPALS, CREDENTIALS
from test_sealed_pipeline import calibration, verification_fixture, author_fixture


PRINCIPALS = {
    name: {"credential": "synthetic-" + name, "roles": roles, "projects": ["public"]}
    for name, roles in {
        "owner": ["owner"], "producer": ["formalizer"], "reviewer": ["reviewer"],
        "verifier": ["verifier"], "checker": ["mechanical"], "service": ["controller"],
        "approver": ["research_approver"], "evaluator": ["research_evaluator"],
        "other": ["research_evaluator"], "dual": ["formalizer", "research_approver"],
        "writer": ["author"],
    }.items()
}


class ResearchAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "research.sqlite"
        self.c = Controller(self.path, PRINCIPALS)
        self.w = Workspace(self.c, "public", "synthetic-research", {"formalizer": "synthetic-producer"})
        self.source = self.w.ingest("synthetic-owner", "For input ping, return pong on stdout.")
        self.frc = self.reg("producer", "frc", {
            "workspace": self.w.session, "contract": {"obligations": [
                {"id": "R1", "statement": "ping -> pong on stdout"}], "issues": [], "unspecified": []},
            "questions": [], "approved": True, "status": "RESEARCH_EVALUATION_APPROVED"}, source=self.source)
        self.call("checker", "validate", subject=self.frc, check="identity-closure")
        self.plan_content = {
            "purpose": "research-evaluation-only", "fixed_before_authoring": True,
            "expectation_basis": "preserved-source", "coverage_limitations": ["Only the stated ping fixture"],
            "checks": [{"id": "C1", "obligations": ["R1"], "input": "ping",
                        "observable": "stdout text", "expected": "pong"}],
        }
        self.plan = self.reg("verifier", "research_plan", self.plan_content, source=self.source, frc=self.frc)
        self.review_content = {
            "material_questions": [], "source_contradictions": [], "requested_scope_determined": True,
            "assumptions": ["The test compares stdout text without transport newline"],
            "nonblocking_uncertainties": ["No behavior outside ping is specified"],
            "review_context": "SAME_AGENT", "limitations": "Synthetic roles; same-agent cognition, not independent review",
            "traceability": [{"obligation": "R1", "source": self.source,
                              "evidence": "For input ping, return pong on stdout."}],
        }
        self.review = self.reg("reviewer", "research_review", self.review_content,
                               source=self.source, frc=self.frc, plan=self.plan)

    def tearDown(self):
        self.c.close()
        self.tmp.cleanup()

    def call(self, actor, command, **args):
        return self.c.execute("synthetic-" + actor, "public", command,
                              expected_revision=self.c.revision, **args)

    def reg(self, actor, kind, content, **dependencies):
        return self.call(actor, "register", kind=kind, content=content, dependencies=dependencies)

    def approve(self, actor="approver", review=None, plan=None, frc=None, source=None):
        return self.call(actor, "approve_research", subject=frc or self.frc, source=source or self.source,
                         plan=plan or self.plan, review=review or self.review, evaluation_actor="evaluator")

    def begin(self, approval, **overrides):
        args = dict(subject=approval, source=self.source, frc=self.frc, plan=self.plan)
        args.update(overrides)
        return self.call("evaluator", "begin_research_evaluation", **args)

    def denied(self, code, callback, *args, **kwargs):
        with self.assertRaises(Failure) as caught:
            callback(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def revised_review(self, **updates):
        content = copy.deepcopy(self.review_content)
        content.update(updates)
        return self.reg("reviewer", "research_review", content, source=self.source, frc=self.frc, plan=self.plan)

    def test_source_bound_synthetic_approval_and_external_observation(self):
        approval = self.approve()
        a = self.c.artifact(approval)
        self.assertEqual(a["dependencies"], {"source": self.source, "frc": self.frc,
                                           "plan": self.plan, "review": self.review})
        self.assertEqual(a["content"]["evaluation_actor"], "evaluator")
        self.assertEqual(a["content"]["assumptions"], self.review_content["assumptions"])
        attempt = self.begin(approval)
        # Public synthetic target, not Lykoi generated software or an external
        # requirement. The expected observation was fixed in the plan above.
        observed = subprocess.run([sys.executable, "-c", "import sys; print('pong' if sys.argv[1] == 'ping' else '')", "ping"],
                                  capture_output=True, text=True, check=True).stdout.strip()
        expected = self.c.artifact(self.plan)["content"]["checks"][0]["expected"]
        self.assertEqual(observed, expected)
        self.assertFalse(self.c.artifact(attempt)["content"]["behaviorally_verified"])
        self.assertFalse(self.c.state(self.frc)["human_authorized"])
        self.assertFalse(self.c.state(self.frc)["sealed"])
        self.assertFalse(self.c.state(self.frc)["implementation_authorized"])
        self.assertFalse(any(e["type"] == "APPROVAL_GRANTED" for e in self.c.events()))

    def test_production_deployment_and_what_seal_remain_protected(self):
        approval = self.approve()
        for purpose in ("release", "production", "deploy", "WHAT", "author"):
            self.denied("RESEARCH_SCOPE_DENIED", self.begin, approval, purpose=purpose)
            self.assertFalse(self.c.applicable(approval, self.frc, self.source, purpose)["applicable"])
        self.denied("INVALID_TRANSITION", self.call, "service", "seal_frc", subject=self.frc)
        self.denied("TYPE_MISMATCH", self.call, "service", "grant", subject=approval)

    def test_source_a_cannot_authorize_source_b(self):
        approval = self.approve()
        message = self.reg("owner", "message", {"text": "Source B: ping -> pang"})
        other = self.reg("producer", "source", {"origin": "synthetic-B"}, message=message)
        self.denied("RESEARCH_IDENTITY_MISMATCH", self.begin, approval, source=other)

    def test_altered_frc_is_not_authorized(self):
        approval = self.approve()
        content = copy.deepcopy(self.c.artifact(self.frc)["content"])
        content["contract"]["obligations"][0]["statement"] = "ping -> pang"
        other = self.reg("producer", "frc", content, source=self.source)
        self.denied("RESEARCH_IDENTITY_MISMATCH", self.begin, approval, frc=other)

    def test_acceptance_plan_identity_and_expectations_are_fixed(self):
        approval = self.approve()
        content = copy.deepcopy(self.plan_content)
        content["checks"][0]["expected"] = "pang"
        other = self.reg("verifier", "research_plan", content, source=self.source, frc=self.frc)
        self.denied("RESEARCH_IDENTITY_MISMATCH", self.begin, approval, plan=other)
        self.assertEqual(self.c.artifact(self.plan)["content"]["checks"][0]["expected"], "pong")

    def test_material_ambiguity_and_source_contradiction_still_halt(self):
        for field in ("material_questions", "source_contradictions"):
            review = self.revised_review(**{field: ["Unresolved material decision"]})
            self.denied("NEEDS_CLARIFICATION", self.approve, review=review)
        question = self.reg("producer", "question", {"text": "Which output?"}, source=self.source)
        self.call("producer", "clarify", subject=self.frc, question=question)
        self.denied("NEEDS_CLARIFICATION", self.approve)

    def test_new_clarification_invalidates_earlier_research_approval(self):
        approval = self.approve()
        question = self.reg("reviewer", "question", {"text": "Output ambiguity discovered"}, source=self.source)
        self.call("reviewer", "clarify", subject=self.frc, question=question)
        self.denied("NEEDS_CLARIFICATION", self.begin, approval)

    def test_stale_dependencies_reject_approval_and_consumption(self):
        approval = self.approve()
        self.call("service", "invalidate", subject=self.plan, reason="Plan withdrawn")
        self.denied("STALE_DEPENDENCY", self.begin, approval)
        self.denied("STALE_DEPENDENCY", self.approve)
        self.assertEqual(self.c.artifact(approval)["type"], "research_approval")

    def test_producer_cannot_manufacture_approval_or_reserved_artifact(self):
        for actor in ("producer", "reviewer", "writer", "owner"):
            self.denied("ROLE_DENIED", self.approve, actor=actor)
        self.denied("RESERVED_OR_UNKNOWN_TYPE", self.reg, "producer", "research_approval", {"approved": True})
        self.denied("TYPE_MISMATCH", self.begin, self.frc)
        self.assertFalse(any(e["type"] == "RESEARCH_EVALUATION_APPROVED" for e in self.c.events()))

    def test_explicit_dual_role_producer_cannot_self_approve(self):
        frc = self.reg("dual", "frc", self.c.artifact(self.frc)["content"], source=self.source)
        # Identity is content-addressed; make it a genuinely new dual-produced candidate.
        content = copy.deepcopy(self.c.artifact(frc)["content"])
        content["producer"] = "dual"
        frc = self.reg("dual", "frc", content, source=self.source)
        self.call("checker", "validate", subject=frc, check="identity-closure")
        plan = self.reg("verifier", "research_plan", self.plan_content, source=self.source, frc=frc)
        review = self.reg("reviewer", "research_review", self.review_content, source=self.source, frc=frc, plan=plan)
        self.denied("RESEARCH_SELF_APPROVAL", self.approve, actor="dual", frc=frc, plan=plan, review=review)

    def test_scope_actor_and_replay_rejection(self):
        approval = self.approve()
        self.denied("RESEARCH_ACTOR_MISMATCH", self.call, "other", "begin_research_evaluation",
                    subject=approval, source=self.source, frc=self.frc, plan=self.plan)
        self.denied("SCOPE_DENIED", self.c.execute, "synthetic-evaluator", "other-project",
                    "begin_research_evaluation", expected_revision=self.c.revision, subject=approval,
                    source=self.source, frc=self.frc, plan=self.plan)
        self.begin(approval)
        self.denied("RESEARCH_EVALUATION_REPLAY", self.begin, approval)

    def test_plan_cannot_derive_expectations_from_generated_code(self):
        content = copy.deepcopy(self.plan_content)
        content["expectation_basis"] = "generated-code"
        plan = self.reg("verifier", "research_plan", content, source=self.source, frc=self.frc)
        review = self.reg("reviewer", "research_review", self.review_content, source=self.source, frc=self.frc, plan=plan)
        self.denied("RESEARCH_PLAN_NOT_READY", self.approve, plan=plan, review=review)

    def test_missing_source_traceability_and_acceptance_coverage_halt(self):
        review = self.revised_review(traceability=[])
        self.denied("RESEARCH_TRACEABILITY_REQUIRED", self.approve, review=review)
        content = copy.deepcopy(self.plan_content)
        content["checks"][0]["obligations"] = ["invented"]
        plan = self.reg("verifier", "research_plan", content, source=self.source, frc=self.frc)
        review = self.reg("reviewer", "research_review", self.review_content, source=self.source, frc=self.frc, plan=plan)
        self.denied("RESEARCH_ACCEPTANCE_BINDING_REQUIRED", self.approve, plan=plan, review=review)

    def test_workspace_compatibility_and_restart(self):
        approval = self.w.approve_research("synthetic-approver", self.frc, plan=self.plan,
                                          review=self.review, evaluation_actor="evaluator")
        self.c.close()
        self.c = Controller(self.path, PRINCIPALS)
        self.w = Workspace(self.c, "public", "synthetic-research", {})
        attempt = self.w.begin_research_evaluation("synthetic-evaluator", approval,
                                                   exact_frc=self.frc, plan=self.plan)
        self.assertEqual(self.c.artifact(attempt)["dependencies"], {"approval": approval})
        self.c.check_integrity()

    def test_review_budget_and_new_review_reject_old_approval(self):
        approval = self.approve()
        self.revised_review(limitations="Second disclosed pass, still same-agent")
        self.denied("STALE_RESEARCH_REVIEW", self.begin, approval)
        self.revised_review(limitations="Third and final disclosed pass, still same-agent")
        self.denied("FINITE_RESEARCH_REVIEW_EXHAUSTED", self.revised_review,
                    limitations="Unbounded fourth pass is refused")

    def test_malformed_review_does_not_create_authority(self):
        review = self.revised_review(material_questions=False)
        self.denied("MALFORMED_REQUEST", self.approve, review=review)
        self.assertFalse(any(e["type"] == "RESEARCH_EVALUATION_APPROVED" for e in self.c.events()))

    def test_research_approval_cannot_bypass_native_v1_or_certify_generated_success(self):
        approval = self.approve()
        attempt = self.begin(approval)
        native = PipelineController(Path(self.tmp.name) / "native.sqlite", PRINCIPALS)
        try:
            # Native WHAT/V1 path accepts only its own product seal; research
            # preflight does not weaken or skip native projection validation.
            message = native.execute("synthetic-owner", "public", "register",
                                     expected_revision=native.revision, kind="message", content={"text": "public synthetic"})
            self.denied("MISSING_WHAT_SEAL", native.what, message)
        finally:
            native.close()
        self.assertFalse(self.c.state(attempt)["implementation_authorized"])
        self.assertFalse(self.c.artifact(attempt)["content"]["behaviorally_verified"])
        self.denied("TYPE_MISMATCH", self.call, "verifier", "bind_verification", subject=attempt)

    def test_historical_evidence_and_semantic_scope_preserved(self):
        root = Path(__file__).resolve().parents[1]
        # Compare Git metadata only. Do not read curation sources or acceptance
        # bodies (especially P6-A03--A05) to assert byte preservation.
        paths = ["benchmark/results/phase6/r5_116a", "benchmark/results/phase6/r5_117",
                 "benchmark/results/phase6/r5_118", "src/air_compiler", "schema", "air", "generated",
                 "src/lykoi_query"]
        result = subprocess.run(["git", "diff", "--exit-code", "HEAD", "--", *paths],
                                cwd=root, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, "Historical/semantic scope changed: " + result.stderr)


class NativeResearchTests(unittest.TestCase):
    """The real existing stage/author/compiler/verifier path, public fixtures only."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        principals = copy.deepcopy(PIPELINE_PRINCIPALS)
        principals.update({k: PRINCIPALS[k] for k in ("approver", "evaluator")})
        self.contract = calibration()
        # Establish source-side expected observations before any target/model.
        self.native_plan = verification_fixture(self.contract)
        from lykoi_pipeline.controller import digest
        self.c = PipelineController(Path(self.tmp.name) / "native.sqlite", principals,
            verification_fixtures={digest(self.contract): self.native_plan}, author_fixture=author_fixture())
        self.p = Pipeline(self.c, "public", CREDENTIALS)

    def tearDown(self):
        self.c.close()
        self.tmp.cleanup()

    def research_seal(self, contract=None):
        contract = contract or self.contract
        def reg(role, kind, content, **deps):
            return self.p.call(role, "register", kind=kind, content=content, dependencies=deps)
        # The public source is attributed and retained without product adoption
        # or product WHAT approval. No upstream owner is needed here.
        message = reg("owner", "message", {"text": contract["source"]["text"], "origin": "public synthetic calibration"})
        source = reg("formalizer", "source", {"origin": "synthetic", "revision": "R5.80/P01"}, message=message)
        frc = reg("formalizer", "frc", {"contract": contract, "policy_applications": []}, source=source)
        self.p.call("mechanical", "validate", subject=frc, check="identity-closure")
        plan = reg("verifier", "research_plan", {
            "purpose": "research-evaluation-only", "fixed_before_authoring": True,
            "expectation_basis": "preserved-source", "coverage_limitations": self.native_plan["limitations"],
            "checks": [{"id": "public-store", "obligations": [o["id"] for o in contract["obligations"]],
                        "observable": "exit, stdout, persisted measurements.json", "expected": self.native_plan["cases"]}],
            "native_plan": self.c.expected_plan(contract)}, source=source, frc=frc)
        review = reg("reviewer", "research_review", {
            "material_questions": [], "source_contradictions": [], "requested_scope_determined": True,
            "assumptions": [], "nonblocking_uncertainties": contract["unspecified"],
            "review_context": "SAME_AGENT", "limitations": "Public known-answer role fixtures; same-agent cognition",
            "traceability": [{"obligation": o["id"], "source": source, "evidence": o["source_quote"]}
                             for o in contract["obligations"]]}, source=source, frc=frc, plan=plan)
        approval = self.c.execute("synthetic-approver", "public", "approve_research",
            expected_revision=self.c.revision, subject=frc, source=source, plan=plan, review=review, evaluation_actor="evaluator")
        attempt = self.c.execute("synthetic-evaluator", "public", "begin_research_evaluation",
            expected_revision=self.c.revision, subject=approval, source=source, frc=frc, plan=plan)
        return self.p.call("controller", "seal_research_frc", subject=attempt)

    def test_native_research_evaluation_without_product_approval(self):
        seal = self.research_seal()
        ready = self.p.prepare(seal, "synthetic-research-native", review_rationale="Disclosed synthetic source-side stage review")
        self.assertEqual(ready["outcome"], "IMPLEMENTATION_AUTHORIZED", ready)
        grant = self.c.artifact(ready["grant"])
        self.assertEqual(grant["content"]["purpose"], "research-implementation")
        self.assertFalse(self.c.applicable(ready["grant"], ready["bundle"], ready["freeze"], "deploy")["applicable"])
        result = self.p.execute(ready)
        self.assertEqual(result["outcome"], "BEHAVIORAL_VERIFICATION_FAILURE", result)
        self.assertIn("target", result)
        self.assertFalse(any(e["type"] in {"APPROVAL_GRANTED", "HUMAN_AUTHORIZED", "ARTIFACT_SEALED"}
                             for e in self.c.events()))
        # Deliberately wrong but compilable existing fixture cannot self-certify.
        with self.assertRaises(Failure) as caught:
            self.p.call("author", "bind_verification", subject=result["verification"])
        self.assertEqual(caught.exception.code, "SELF_VERIFICATION")

    def test_unsupported_v1_halts_with_research_approval(self):
        contract = copy.deepcopy(self.contract)
        contract["context"]["component_authority"] = None
        result = self.p.prepare(self.research_seal(contract), "synthetic-unsupported-v1",
                                review_rationale="Disclosed synthetic review")
        self.assertEqual(result["outcome"], "UNREPRESENTABLE_SOURCE", result)
        self.assertNotIn("grant", result)
        self.assertNotIn("model", result)

    def test_native_acceptance_payload_cannot_change_after_approval(self):
        seal = self.research_seal()
        changed = copy.deepcopy(self.native_plan)
        changed["cases"][0]["steps"][0]["returncode"] = 2
        with patch.object(self.c, "expected_plan", return_value=changed):
            with self.assertRaises(Failure) as caught:
                self.c.what(seal)
        self.assertEqual(caught.exception.code, "RESEARCH_ACCEPTANCE_BINDING_REQUIRED")
        self.assertFalse(any(e["type"] == "DISPATCH_RESERVED" for e in self.c.events()))

    def test_structural_bdi_adequacy_halts_with_research_approval(self):
        cases = [({"kind": "sum", "parameters": {"inputs": "integers"}}, "STRUCTURAL_COVERAGE_FAILURE"),
                 ({"kind": "effects", "parameters": {"events": True}}, "UNSUPPORTED_BDI_SCOPE"),
                 ({"kind": "priority_create", "parameters": {"condition": "priority omitted", "result": "UNRESOLVED"}},
                  "IMPLEMENTATION_UNDERSPECIFIED")]
        for i, (relation, expected) in enumerate(cases):
            contract = copy.deepcopy(self.contract)
            contract["obligations"][0]["relation"] = relation
            # Deliberately malformed mapping: source trace is only a review
            # premise; native stages must still reject unsupported candidates.
            result = self.p.prepare(self.research_seal(contract), "synthetic-stage-refusal-" + str(i),
                                    review_rationale="Synthetic fault injection, not faithful-source certification")
            self.assertEqual(result["outcome"], expected, result)
            self.assertNotIn("grant", result)


if __name__ == "__main__":
    unittest.main()
