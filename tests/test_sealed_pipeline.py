"""R5.88 public fault injections; explicit public fixtures only."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from lykoi_controller import Failure, canonical
from lykoi_pipeline import PipelineController, Pipeline
from lykoi_pipeline import contracts, plans
from lykoi_pipeline.controller import digest, ROOT
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS, wizard
from lykoi_pipeline.pipeline import external_execute


def calibration():
    # Explicit public calibration, not any protected resource or metadata.
    return json.loads((ROOT / "benchmark/results/phase5c/r5_80/candidates.json").read_text(encoding="utf-8"))["P01"]


def verification_fixture(contract):
    """Separately authored WHAT-side fixture, before an author model exists.

    Exercises the calibrated public store route. Task CLI is deliberately wrong
    for it; compilation is expected to succeed and external behavior to fail.
    This is coverage review evidence, not exhaustive semantic equivalence proof.
    """
    ids = [o["id"] for o in contract["obligations"]] + ["@component-context"]
    case = {"id": "public-store", "obligations": ids, "initial_state": "fresh_directory",
            "steps": [{"argv": ["store", "--code", "public", "--value", "17"], "returncode": 0, "contains": ["17"],
                       "files": [{"path": "measurements.json", "json": {"revision": 1, "samples": [{"code": "public", "value": 17}]}}]}],
            "invariants": ["V1 revision remains 1; optional values obey the declared domain"],
            "transitions": "store inserts a sample in declared persisted state", "rejections": "Unspecified cases are not invented"}
    case["identity"] = digest(case)
    return {"version": plans.VERSION, "outcome": "READY", "producer": plans.ISOLATION,
            "cases": [case], "coverage": [{"obligation": oid, "classification": "EXERCISED",
                      "justification": "Separately authored public calibration fixture; bounded coverage review",
                      "cases": [case["identity"]]} for oid in ids],
            "limitations": ["Single positive sample does not prove exhaustive equivalence"]}


def author_fixture(mode="identity"):
    return {"identity": "public-existing-task-model-fixture-1:" + mode,
            "source": json.loads((ROOT / "air/task_manager.json").read_text(encoding="utf-8")), "mode": mode}


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "controller.sqlite"
        self.contract = calibration()
        self.fixtures = {digest(self.contract): verification_fixture(self.contract)}
        self.fixture = author_fixture()
        self.c = PipelineController(self.path, PRINCIPALS, verification_fixtures=self.fixtures, author_fixture=self.fixture)
        self.p = Pipeline(self.c, "public", CREDENTIALS)

    def tearDown(self):
        self.c.close()
        self.tmp.cleanup()

    def denied(self, code, fn, *args, **kwargs):
        with self.assertRaises(Failure) as caught:
            fn(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def seal(self, contract=None):
        contract = contract or self.contract
        def reg(role, kind, content, **deps):
            return self.p.call(role, "register", kind=kind, content=content, dependencies=deps)
        def validate(aid, access=None):
            self.p.call("mechanical", "validate", subject=aid, check="identity-closure", access=access)
        message = reg("owner", "message", {"text": contract["source"]["text"]})
        self.p.call("owner", "adopt", subject=message)
        source = reg("formalizer", "source", {"provenance": "human_statement"}, message=message)
        self.p.call("owner", "adopt", subject=source)
        frc = reg("formalizer", "frc", {"contract": contract, "policy_applications": []}, source=source)
        soi = reg("reviewer", "soi", {"items": [o["id"] for o in contract["obligations"]]}, source=source)
        validate(frc)
        validate(soi, [source])
        self.p.call("controller", "begin_review", subject=frc, soi=soi)
        cov = reg("reviewer", "coverage", {"fixture": "public-calibration"}, frc=frc, soi=soi)
        structural = reg("formalizer", "structural", {"scope": "requirements-only; no V1/BDI support asserted"}, frc=frc)
        validate(cov)
        validate(structural)
        self.p.review(cov, "Public synthetic independent fixture coverage")
        self.p.call("reviewer", "review", subject=structural, outcome="UNSUPPORTED",
                    rationale="WHAT-only approval; back-half projection remains separate", access=[frc])
        self.p.call("owner", "approve", subject=frc, coverage=cov, structural=structural)
        return self.p.call("controller", "seal_frc", subject=frc)

    def ready(self):
        result = self.p.prepare(self.seal(), "public-run-1", review_rationale="Separately authored synthetic calibration evidence")
        self.assertEqual(result["outcome"], "IMPLEMENTATION_AUTHORIZED", result)
        return result

    def test_public_workspace_exact_seal_halts_at_v1(self):
        result = self.p.prepare(wizard(self.c), "wizard-1", review_rationale="Independent bounded synthetic item review")
        self.assertEqual(result["outcome"], "UNREPRESENTABLE_SOURCE")
        self.assertIn("adequacy", result)
        self.assertNotIn("grant", result)
        self.assertNotIn("plan", result)
        self.assertFalse(any(e["type"] == "DISPATCH_RESERVED" for e in self.c.events()))

    def test_structural_omission_before_bdi(self):
        seal = self.seal()
        original = contracts.structural
        def omit(contract, fid):
            projection = original(contract, fid)
            projection["rows"].pop()
            return projection
        with patch.object(contracts, "structural", side_effect=omit):
            result = self.p.prepare(seal, "omitted", review_rationale="Omission challenge")
        self.assertEqual(result["outcome"], "STRUCTURAL_COVERAGE_FAILURE")
        self.assertNotIn("bdi", result)

    def test_structural_forged_complete_bool_rejects(self):
        fid, contract = self.c.what(self.seal())
        projection = contracts.structural(contract, fid)
        projection["rows"].pop()
        projection["projection_complete"] = True
        self.denied("STRUCTURAL_COVERAGE_FAILURE", contracts.coverage, contract, projection)

    def test_unsupported_structural_relation_halts(self):
        contract = copy.deepcopy(self.contract)
        contract["obligations"][0]["relation"] = {"kind": "sum", "parameters": {"inputs": "integers"}}
        result = self.p.prepare(self.seal(contract), "unsupported", review_rationale="Unsupported relation")
        self.assertEqual(result["outcome"], "STRUCTURAL_COVERAGE_FAILURE")
        self.assertNotIn("bdi", result)

    def test_unsupported_bdi_observation_halts(self):
        contract = copy.deepcopy(self.contract)
        contract["obligations"][0]["relation"] = {"kind": "effects", "parameters": {"events": True}}
        result = self.p.prepare(self.seal(contract), "event", review_rationale="Declared unsupported observation")
        self.assertEqual(result["outcome"], "UNSUPPORTED_BDI_SCOPE")
        self.assertNotIn("grant", result)

    def test_inadequate_contract_cannot_grant(self):
        contract = copy.deepcopy(self.contract)
        contract["obligations"][0]["relation"] = {"kind": "priority_create", "parameters": {"condition": "priority omitted", "result": "UNRESOLVED"}}
        result = self.p.prepare(self.seal(contract), "inadequate", review_rationale="No default authority")
        self.assertEqual(result["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")
        self.assertNotIn("grant", result)

    def test_missing_plan_obligation_no_seal(self):
        plan = self.fixtures[digest(self.contract)]
        plan["coverage"].pop()
        # Fixture service setup is immutable; use a fresh DB with this declared
        # bad candidate to test native coverage, not mutate authorized criteria.
        self.c.close()
        self.c = PipelineController(Path(self.tmp.name) / "bad-plan.sqlite", PRINCIPALS,
                                    verification_fixtures=self.fixtures, author_fixture=self.fixture)
        self.p = Pipeline(self.c, "public", CREDENTIALS)
        result = self.p.prepare(self.seal(), "missing-plan", review_rationale="Fault fixture")
        self.assertEqual(result["outcome"], "VERIFICATION_PLAN_COVERAGE_GAP")
        self.assertNotIn("plan_seal", result)
        self.assertNotIn("grant", result)

    def test_default_plan_cannot_verify_component_context(self):
        self.denied("VERIFICATION_PLAN_COVERAGE_GAP", plans.review_coverage, self.contract, plans.produce(self.contract))

    def test_native_evidence_cannot_be_text_claim(self):
        ready = self.ready()
        d = self.c.artifact(ready["adequacy"])["dependencies"]
        fake = self.p.reg("mechanical", "adequacy", {"outcome": "ADEQUATE"}, **d)
        self.denied("NATIVE_EVIDENCE_MISMATCH", self.p.check, fake)
        self.denied("NATIVE_PIPELINE_EVIDENCE_REQUIRED", self.p.call, "mechanical", "validate", subject=fake, check="identity-closure")

    def test_no_grant_no_author(self):
        ready = self.ready()
        self.denied("GRANT_DENIAL", self.p.author, ready["bundle"], ready["plan_seal"], ready["freeze"])
        self.assertFalse(any(e["type"] == "DISPATCH_RESERVED" for e in self.c.events()))

    def test_plan_is_sealed_before_author_bundle(self):
        ready = self.ready()
        events = self.c.events()
        seal_rev = next(e["revision"] for e in events if e["type"] == "PLAN_SEALED")
        bundle_rev = next(e["revision"] for e in events if e["subject"] == ready["bundle"] and e["type"] == "ARTIFACT_REGISTERED")
        self.assertLess(seal_rev, bundle_rev)
        request = self.c.artifact(ready["bundle"])["content"]["author_input"]
        self.assertEqual(set(request), {"version", "run", "v1", "toolchain", "fixture"})
        self.assertNotIn("public-store", canonical(request).decode())
        self.assertNotIn("source_quote", canonical(request).decode())

    def test_component_substitution_before_author_rejects(self):
        ready = self.ready()
        components = self.c.components()
        components["compiler"] = "substituted"
        with patch.object(self.c, "components", return_value=components):
            self.denied("GRANT_DENIAL", self.p.author, ready["bundle"], ready["grant"], ready["freeze"])

    def test_component_substitution_before_grant_rejects(self):
        ready = self.ready()
        components = self.c.components()
        components["verifier_adapter"] = "different"
        with patch.object(self.c, "components", return_value=components):
            self.denied("FREEZE_FAILURE", self.p.call, "controller", "grant", subject=ready["bundle"])

    def test_manifest_substitution_rejects(self):
        ready = self.ready()
        a = self.c.artifact(ready["bundle"])
        a["content"]["manifest"]["v1"] = ready["adequacy"]
        replacement = self.p.reg("formalizer", "bundle", a["content"], **a["dependencies"])
        self.denied("FREEZE_FAILURE", self.p.call, "controller", "grant", subject=replacement)

    def test_wrong_but_compilable_target_fails_behavior(self):
        result = self.p.execute(self.ready())
        self.assertIn("target", result, result)
        self.assertEqual(result["outcome"], "BEHAVIORAL_VERIFICATION_FAILURE", result)
        verification = self.c.artifact(result["verification"])["content"]
        self.assertFalse(verification["cases"][0]["steps"][0]["passed"])
        self.assertTrue(any(e["type"] == "VERIFICATION_BOUND" for e in self.c.events()))

    def test_author_cannot_issue_external_authority(self):
        result = self.p.execute(self.ready())
        self.denied("SELF_VERIFICATION", self.p.call, "author", "bind_verification", subject=result["verification"])
        self.denied("AUTHOR_VERIFICATION_ROLE_CONFLICT", self.p.call, "author", "seal_plan", subject=result["plan"])

    def test_hidden_plan_normal_file_api_denied(self):
        self.fixture["mode"] = "hidden_read_probe"
        self.c.close()
        self.c = PipelineController(Path(self.tmp.name) / "hidden.sqlite", PRINCIPALS,
                                    verification_fixtures=self.fixtures, author_fixture=self.fixture)
        self.p = Pipeline(self.c, "public", CREDENTIALS)
        result = self.p.execute(self.ready())
        self.assertEqual(result["outcome"], "AUTHOR_RESOURCE_DENIED")
        self.assertNotIn("model", result)

    def test_compilation_failure_is_distinct(self):
        self.fixture["mode"] = "malformed"
        self.c.close()
        self.c = PipelineController(Path(self.tmp.name) / "malformed.sqlite", PRINCIPALS,
                                    verification_fixtures=self.fixtures, author_fixture=self.fixture)
        self.p = Pipeline(self.c, "public", CREDENTIALS)
        result = self.p.execute(self.ready())
        self.assertEqual(result["outcome"], "COMPILATION_FAILURE", result)
        self.assertNotIn("target", result)

    def test_author_adapter_capability_gap(self):
        self.c.close()
        self.fixture = None
        self.c = PipelineController(Path(self.tmp.name) / "gap.sqlite", PRINCIPALS,
                                    verification_fixtures=self.fixtures)
        self.p = Pipeline(self.c, "public", CREDENTIALS)
        result = self.p.execute(self.ready())
        self.assertEqual(result["outcome"], "LYKOI_CAPABILITY_GAP")

    def test_restart_audit_and_fixture_substitution(self):
        result = self.p.execute(self.ready())
        before = self.p.audit(result)
        self.c.close()
        self.c = PipelineController(self.path, PRINCIPALS, verification_fixtures=self.fixtures, author_fixture=self.fixture)
        self.p = Pipeline(self.c, "public", CREDENTIALS)
        self.assertEqual(before, self.p.audit(result))
        self.assertEqual(self.p.audit_run(result["run"])["run"]["verification"], result["verification"])
        self.denied("FREEZE_FAILURE", PipelineController, self.path, PRINCIPALS, verification_fixtures={}, author_fixture=self.fixture)

    def test_upstream_invalidation_makes_grant_stale(self):
        ready = self.ready()
        self.p.call("owner", "invalidate", subject=ready["frc"], reason="Authoritative WHAT changed")
        self.assertFalse(self.c.applicable(ready["grant"], ready["bundle"], ready["freeze"])["applicable"])
        self.denied("GRANT_DENIAL", self.p.author, ready["bundle"], ready["grant"], ready["freeze"])

    def test_plan_replacement_does_not_preserve_run(self):
        ready = self.ready()
        a = self.c.artifact(ready["plan"])
        a["content"]["limitations"].append("new plan version")
        replacement = self.p.reg("verifier", "plan", a["content"], **a["dependencies"])
        self.p.call("owner", "supersede", subject=ready["plan"], replacement=replacement)
        self.denied("GRANT_DENIAL", self.p.author, ready["bundle"], ready["grant"], ready["freeze"])

    def test_replay_denies_second_author(self):
        ready = self.ready()
        self.p.author(ready["bundle"], ready["grant"], ready["freeze"])
        self.denied("DISPATCH_REPLAY", self.p.author, ready["bundle"], ready["grant"], ready["freeze"])

    def test_external_behavior_not_code_identity(self):
        # Public wizard fixture plan independently exercises title/default/filter;
        # two compiler inputs differ only in internal declaration ordering.
        from air_compiler.generator import generate
        from air_compiler.parser import parse
        from lykoi_workspace.example import formalizer_fixture
        evidence = [{"identity": "human", "provenance": "human_statement"},
                    {"identity": "default", "provenance": "clarification_answer", "question": "PRIORITY.DEFAULT", "text": "NORMAL"},
                    {"identity": "important", "provenance": "clarification_answer", "question": "IMPORTANT.MEANING", "text": "HIGH"}]
        c = {"obligations": formalizer_fixture({}, evidence)["obligations"], "context": {"component_authority": None}}
        plan = plans.produce(c)
        plans.review_coverage(c, plan)
        source1 = self.fixture["source"]
        source2 = copy.deepcopy(source1)
        source2["commands"].reverse()
        targets = [generate(parse(canonical(x).decode())) for x in (source1, source2)]
        self.assertNotEqual(targets[0], targets[1])
        for target in targets:
            self.assertEqual(external_execute(target, plan)[0], "BEHAVIORALLY_VERIFIED")
        wrong = copy.deepcopy(source1)
        def change(node):
            if isinstance(node, dict):
                if node.get("field") == "field_priority" and node.get("source") == "input_default":
                    node["value"] = "LOW"
                for child in node.values():
                    change(child)
            elif isinstance(node, list):
                for child in node:
                    change(child)
        change(wrong)
        # Same supported language and same acceptance plan; lowering still works.
        self.assertEqual(external_execute(generate(parse(canonical(wrong).decode())), plan)[0], "BEHAVIORAL_VERIFICATION_FAILURE")

    def test_runtime_failure_is_not_success(self):
        plan = self.fixtures[digest(self.contract)]
        with patch("lykoi_pipeline.pipeline.subprocess.run", side_effect=OSError("unavailable")):
            outcome, observations = external_execute("print('17')", plan)
        self.assertEqual(outcome, "RUNTIME_FAILURE")
        self.assertFalse(observations[0]["steps"][0]["passed"])

    def test_actual_process_restart_audit_by_run(self):
        result = self.p.execute(self.ready())
        code = ("import sys,json; sys.path[:0]=" + repr([str(ROOT), str(ROOT / 'src')]) + "; "
                "from lykoi_pipeline import PipelineController,Pipeline; "
                "d=json.load(sys.stdin); c=PipelineController(d['path'],d['principals'],verification_fixtures=d['plans'],author_fixture=d['author']); "
                "a=Pipeline(c,'public',d['credentials']).audit_run(d['run']); "
                "print(json.dumps({'outcome':a['run']['outcome'],'verification':a['run']['verification']})); c.close()")
        child = subprocess.run([sys.executable, "-I", "-S", "-c", code], text=True, capture_output=True, timeout=30,
                               input=json.dumps({"path": str(self.path), "principals": PRINCIPALS,
                                    "plans": self.fixtures, "author": self.fixture, "credentials": CREDENTIALS, "run": result["run"]}))
        self.assertEqual(child.returncode, 0, child.stderr)
        self.assertEqual(json.loads(child.stdout), {"outcome": result["outcome"], "verification": result["verification"]})

    def test_changed_target_cannot_keep_build_binding(self):
        result = self.p.execute(self.ready())
        a = self.c.artifact(result["target"])
        a["content"]["target_source"] += "\nprint('substitution')\n"
        changed = self.p.reg("mechanical", "target", a["content"], **a["dependencies"])
        self.assertNotEqual(changed, result["target"])
        self.denied("NATIVE_EVIDENCE_MISMATCH", self.p.check, changed)

    def test_invalid_fixture_authoring_failure_is_distinct(self):
        self.fixture["mode"] = "invalid"
        self.c.close()
        self.c = PipelineController(Path(self.tmp.name) / "invalid.sqlite", PRINCIPALS,
                                    verification_fixtures=self.fixtures, author_fixture=self.fixture)
        self.p = Pipeline(self.c, "public", CREDENTIALS)
        result = self.p.execute(self.ready())
        self.assertEqual(result["outcome"], "AUTHORING_FAILURE")

    def test_missing_executed_case_cannot_bind_success(self):
        result = self.p.execute(self.ready())
        a = self.c.artifact(result["verification"])
        a["content"]["cases"] = []
        a["content"]["outcome"] = "BEHAVIORALLY_VERIFIED"
        forged = self.p.reg("verifier", "verification", a["content"], **a["dependencies"])
        self.denied("VERIFICATION_PLAN_COVERAGE_GAP", self.p.check, forged)

    def test_unjustified_plan_exclusion_is_not_coverage(self):
        plan = copy.deepcopy(self.fixtures[digest(self.contract)])
        plan["coverage"][0]["classification"] = "AUTHORIZED_FREEDOM"
        plan["coverage"][0]["cases"] = []
        self.denied("VERIFICATION_PLAN_COVERAGE_GAP", plans.review_coverage, self.contract, plan)


if __name__ == "__main__":
    unittest.main()
