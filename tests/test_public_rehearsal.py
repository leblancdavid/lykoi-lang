"""Public calibration only. Mock HTTP transport is never reported as real AI."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from air_compiler.generator import generate
from air_compiler.parser import parse
from lykoi_controller import Failure, canonical
from lykoi_pipeline import contracts
from lykoi_pipeline.controller import ROOT, digest
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS, wizard
from lykoi_workspace import Workspace
from lykoi_workspace.example import obligation
from lykoi_rehearsal.adapters import AIAdapter, PROMPTS
from lykoi_rehearsal.freeze import configurations, seal_snapshot, integrity, eligibility
from lykoi_rehearsal.mappings import TITLE, select, project
from lykoi_rehearsal.service import RehearsalController, RehearsalPipeline, public_author_seed
from lykoi_rehearsal import verification


def source_model():
    return json.loads((ROOT / "air/task_manager.json").read_text(encoding="utf-8"))


def change_default(source, value):
    def walk(x):
        if isinstance(x, dict):
            if x.get("source") == "input_default" and x.get("field") == "field_priority":
                x["value"] = value
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(source)
    return source


def rows(text, default=None):
    result = [obligation("TITLE", text, "Create tasks with the supplied title.", "crud", copy.deepcopy(TITLE["parameters"]))]
    if default is not None:
        result.append(obligation("DEFAULT", text, "Omitted priority uses " + default + ".", "priority_create",
                                 {"condition": "priority omitted", "result": default}))
    return result


def contract(default=None):
    text = "Create tasks with titles." + (" Omitted priority uses " + default + "." if default else "")
    import hashlib
    return {"schema_version": "FormalRequirementContract-0.1", "contract_id": "public-calibration", "revision": 1,
            "source": {"id": "public", "text": text, "classification": "SYNTHETIC", "sha256": hashlib.sha256(text.encode()).hexdigest()},
            "context": {"scope": "public calibration", "domains": {}, "assumptions": [], "component_authority": None},
            "obligations": rows(text, default), "issues": [], "unspecified": [], "implementation_choices": [],
            "lineage": [], "formalizer": "public", "review": None}


def transport(output):
    def invoke(payload):
        sent = json.loads(payload["messages"][1]["content"])
        result = output(sent["input"]) if callable(output) else copy.deepcopy(output)
        return {"model": "mock-not-real-ai", "id": "test", "choices": [{"message": {
            "content": json.dumps({"binding": sent["binding"], "output": result})}}]}
    return invoke


class MappingTests(unittest.TestCase):
    def test_profile_declares_small_scope(self):
        profile = json.loads((ROOT / "rehearsal/public-capability-profile-1.json").read_text())
        self.assertEqual(profile["supported_patterns"], ["task-title-create-1", "task-title-default-create-1"])
        self.assertFalse(profile["future_requirement_selected"])
        self.assertIn("persistence obligations", profile["unsupported"])

    def test_all_mapping_boundaries_and_preservation(self):
        for default in (None, "LOW", "NORMAL", "HIGH"):
            c = contract(default)
            p = project(c)
            self.assertEqual(len(p["coverage"]), len(c["obligations"]))
            self.assertEqual({o["id"]: o["relation"] for o in c["obligations"]}, p["normalized"]["application"]["operations"])
            self.assertEqual(p["normalized"]["obligations"], sorted(p["document"]["payload"]["obligations"], key=lambda o: o["id"]))
            structural = contracts.structural(c, "frc")
            contracts.coverage(c, structural)
            bdi = contracts.bdi(c, structural)
            self.assertEqual(bdi["outcome"], "SUPPORTED")
            self.assertEqual(contracts.adequate(c, bdi)["outcome"], "ADEQUATE")

    def test_extra_obligation_never_dropped(self):
        for relation in ({"kind": "persist", "parameters": {"durable": True}},
                         {"kind": "filter_order", "parameters": {"domain": "task lists", "ordering": "unconstrained"}},
                         {"kind": "priority_filter", "parameters": {"domain": "tasks", "multiplicity": "all", "predicate": "HIGH"}}):
            c = contract("NORMAL")
            c["obligations"].append(obligation("EXTRA", c["source"]["text"], "Extra behavioral obligation", relation["kind"], relation["parameters"]))
            with self.assertRaises(Failure) as error:
                project(c)
            self.assertEqual(error.exception.code, "UNREPRESENTABLE_SOURCE")

    def test_near_miss_mutations_reject(self):
        for key, value in (("cardinality", "exactly one"), ("ordering", "ascending"), ("state", "completed"), ("validation", "trim")):
            c = contract()
            c["obligations"][0]["relation"]["parameters"][key] = value
            with self.assertRaises(Failure):
                project(c)
        for condition, result in (("null or omitted", "NORMAL"), ("priority omitted", "URGENT"), ("priority omitted", "UNRESOLVED")):
            c = contract("NORMAL")
            c["obligations"][1]["relation"]["parameters"] = {"condition": condition, "result": result}
            with self.assertRaises(Failure):
                project(c)

    def test_duplicate_context_and_domains_reject(self):
        for field, value in (("component_authority", {}), ("domains", {"title": "at most 20"}), ("assumptions", ["unique titles"])):
            c = contract()
            c["context"][field] = value
            with self.assertRaises(Failure):
                project(c)
        c = contract()
        extra = copy.deepcopy(c["obligations"][0])
        extra["id"] = "duplicate-semantic"
        c["obligations"].append(extra)
        with self.assertRaises(Failure):
            select(c)

    def test_inadequacy_preserved(self):
        c = contract("UNRESOLVED")
        bdi = contracts.bdi(c, contracts.structural(c, "frc"))
        self.assertNotEqual(contracts.adequate(c, bdi)["outcome"], "ADEQUATE")


class AdapterTests(unittest.TestCase):
    def request(self, a):
        return {"role": a.role, "session": a.session, "source": {"identity": "source", "text": "Create tasks with titles.", "revision": 1},
                "evidence": [{"identity": "message", "text": "Create tasks with titles.", "provenance": "human_statement"}],
                "output_schema": "WorkspaceAnalysis-1", "instructions": "WHAT"}

    def test_unavailable_configuration_is_not_live_success(self):
        a = AIAdapter("formalizer", configurations()["roles"]["formalizer"])
        with self.assertRaises(Failure) as error:
            a.produce(self.request(a))
        self.assertEqual(error.exception.code, "AI_CONFIGURATION_UNAVAILABLE")
        self.assertEqual(a.receipts, [])

    def test_allowlist_and_schema(self):
        a = AIAdapter("formalizer", {}, transport=transport({"obligations": [], "authority": {}, "questions": [], "issues": []}))
        r = self.request(a)
        r["candidate"] = "forbidden"
        with self.assertRaises(Failure):
            a.produce(r)
        a = AIAdapter("formalizer", {}, transport=transport({"obligations": "invalid"}))
        with self.assertRaises(Failure):
            a.produce(self.request(a))

    def test_binding_substitution_rejects(self):
        a = AIAdapter("formalizer", {}, transport=lambda _: {"choices": [{"message": {"content": '{"binding":"wrong","output":{}}'}}]})
        with self.assertRaises(Failure):
            a.produce(self.request(a))

    def test_provenance_and_instruction_identity(self):
        a = AIAdapter("formalizer", {}, transport=transport({"obligations": [], "authority": {}, "questions": [], "issues": []}))
        a.produce(self.request(a))
        receipt = a.receipts[-1]
        self.assertEqual(receipt["instruction_identity"], digest(PROMPTS["formalizer"]))
        self.assertEqual(receipt["authority"], "UNTRUSTED_CANDIDATE")
        self.assertEqual(receipt["execution"], "TEST_TRANSPORT_NOT_REAL_AI")
        self.assertEqual(receipt["source_identity"], "source")

    def test_credential_not_persisted_and_live_protocol(self):
        config = {**configurations()["roles"]["formalizer"], "model": "public-test-model"}
        a = AIAdapter("formalizer", config)
        def urlopen(req, timeout):
            self.assertEqual(timeout, 90)
            self.assertIn("json_schema", req.data.decode())
            sent = json.loads(json.loads(req.data)["messages"][1]["content"])
            response = {"model": "returned-model", "choices": [{"message": {"content": json.dumps({"binding": sent["binding"], "output": {"obligations": [], "authority": {}, "questions": [], "issues": []}})}}]}
            ctx = unittest.mock.MagicMock()
            ctx.__enter__.return_value.read.return_value = canonical(response)
            return ctx
        with patch.dict("os.environ", {"LYKOI_REHEARSAL_API_KEY": "test-secret"}), patch("urllib.request.urlopen", side_effect=urlopen):
            a.produce(self.request(a))
        self.assertNotIn("test-secret", canonical(a.receipts).decode())


class EndToEndTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.config = configurations()
        self.c = RehearsalController(Path(self.tmp.name) / "public.sqlite", PRINCIPALS, model_configurations=self.config,
                                     author_seed=public_author_seed())

    def tearDown(self):
        self.c.close()
        self.tmp.cleanup()

    def workspace(self, default=None, disagreement=False, ambiguous=False):
        c = contract(default)
        w = Workspace(self.c, "public", "calibration", CREDENTIALS)
        w.ingest(CREDENTIALS["owner"], c["source"]["text"])
        def formal(req):
            refs = [req["evidence"][0]["identity"]]
            return {"obligations": c["obligations"], "authority": {o["id"]: refs for o in c["obligations"]},
                    "questions": [], "issues": c["issues"]}
        f = AIAdapter("formalizer", self.config["roles"]["formalizer"], transport=transport(formal))
        fid = w.formalize(f)
        def review(req):
            self.assertNotIn("candidate", req)
            self.assertNotIn("obligations", req)
            text = req["source"]["text"]
            interpretations = {o["id"]: {k: o[k] for k in ("statement", "relation")} for o in c["obligations"]}
            if disagreement:
                interpretations["TITLE"]["statement"] = "Different requirement"
            return {"inventory": {"version": "SourceObligationInventory-0.1", "source_commitment": req["source_commitment"],
                    "extractor": "mock-reviewer", "context_class": "TEST_TRANSPORT", "items": [
                        {"id": o["id"], "spans": [{"start": 0, "end": len(text), "quote": text}], "meaning": o["statement"],
                         "category": "AMBIGUITY" if ambiguous else "BEHAVIOR", "material": True, "dependencies": []} for o in c["obligations"]],
                    "questions": [], "limitations": ["Calibration, not real AI"]}, "interpretations": interpretations,
                    "authority": {o["id"]: [req["evidence"][0]["identity"]] for o in c["obligations"]}}
        reviewer = AIAdapter("reviewer", self.config["roles"]["reviewer"], transport=transport(review))
        soi = w.commit_inventory(reviewer)
        events = self.c.events()
        self.assertLess(next(e["revision"] for e in events if e["type"] == "SOI_COMMITTED"),
                        next(e["revision"] for e in events if e["type"] == "REVIEW_STARTED"))
        self.assertNotEqual(f.session, reviewer.session)
        w.reconcile(soi)
        w.approve(CREDENTIALS["owner"], fid)
        return w.seal(fid)

    def pipeline(self, model=None):
        def author(req):
            self.assertEqual(set(req), {"version", "run", "v1", "toolchain", "fixture"})
            self.assertNotIn("public title", canonical(req).decode())
            self.assertNotIn("coverage", req)
            return {"source": model if model is not None else source_model()}
        return RehearsalPipeline(self.c, "public", CREDENTIALS, AIAdapter("author", self.config["roles"]["author"], transport=transport(author)), mode="CALIBRATION")

    def test_authorized_title_end_to_end(self):
        p = self.pipeline()
        ready = p.prepare(self.workspace(), "title", review_rationale="Independent synthetic authority coverage review")
        self.assertEqual(ready["outcome"], "IMPLEMENTATION_AUTHORIZED", ready)
        result = p.execute(ready)
        self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)
        self.assertEqual(self.c.artifact(result["model"])["content"]["receipt"]["execution"], "TEST_TRANSPORT_NOT_REAL_AI")
        self.assertEqual(p.audit_run("title")["run"]["outcome"], "BEHAVIORALLY_VERIFIED")

    def test_default_success_and_wrong_author_behavior(self):
        p = self.pipeline()
        result = p.execute(p.prepare(self.workspace("NORMAL"), "default", review_rationale="Public calibration coverage"))
        self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)

    def test_low_default_authorized_calibration(self):
        p = self.pipeline(change_default(source_model(), "LOW"))
        result = p.execute(p.prepare(self.workspace("LOW"), "low", review_rationale="Public calibration coverage"))
        self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)

    def test_high_default_authorized_calibration(self):
        p = self.pipeline(change_default(source_model(), "HIGH"))
        result = p.execute(p.prepare(self.workspace("HIGH"), "high", review_rationale="Public calibration coverage"))
        self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)

    def test_compilable_wrong_default_fails(self):
        p = self.pipeline()
        result = p.execute(p.prepare(self.workspace("HIGH"), "wrong", review_rationale="Public calibration coverage"))
        self.assertEqual(result["outcome"], "BEHAVIORAL_VERIFICATION_FAILURE", result)

    def test_author_capability_failure(self):
        p = self.pipeline({"axiom_version": "9", "unsupported": True})
        result = p.execute(p.prepare(self.workspace(), "bad-author", review_rationale="Public calibration coverage"))
        self.assertEqual(result["outcome"], "AUTHOR_CAPABILITY_FAILURE", result)
        self.assertNotIn("target", result)

    def test_blind_disagreement_and_ambiguity_block_approval(self):
        with self.assertRaises(Failure):
            self.workspace(disagreement=True)

    def test_ambiguity_blocks_approval(self):
        with self.assertRaises(Failure):
            self.workspace(ambiguous=True)

    def test_exact_wizard_still_halts_before_author(self):
        p = self.pipeline()
        result = p.prepare(wizard(self.c), "old-wizard", review_rationale="Preserve public example")
        self.assertEqual(result["outcome"], "UNREPRESENTABLE_SOURCE", result)
        self.assertEqual(result["failure"]["details"]["gap"], "NO_QUALIFIED_COMPLETE_MAPPING")
        self.assertNotIn("grant", result)
        self.assertFalse(p.author_adapter.receipts)

    def test_plan_sealed_before_bundle_and_no_grant_no_author(self):
        p = self.pipeline()
        ready = p.prepare(self.workspace(), "ordering", review_rationale="Public coverage")
        events = self.c.events()
        self.assertLess(next(e["revision"] for e in events if e["type"] == "PLAN_SEALED"),
                        next(e["revision"] for e in events if e["type"] == "ARTIFACT_REGISTERED" and e["subject"] == ready["bundle"]))
        with self.assertRaises(Failure):
            p.author(ready["bundle"], ready["plan_seal"], ready["freeze"])
        self.assertFalse(p.author_adapter.receipts)

    def test_restart_configuration_substitution_denied(self):
        self.c.close()
        config = copy.deepcopy(self.config)
        config["roles"]["author"]["model"] = "substituted"
        with self.assertRaises(Failure):
            RehearsalController(Path(self.tmp.name) / "public.sqlite", PRINCIPALS, model_configurations=config,
                                author_seed=public_author_seed())

    def test_public_mode_blocks_before_any_requirement_or_author(self):
        with self.assertRaises(Failure) as error:
            RehearsalPipeline(self.c, "public", CREDENTIALS, AIAdapter("author", self.config["roles"]["author"]))
        self.assertEqual(error.exception.code, "PUBLIC_REHEARSAL_INELIGIBLE")
        self.assertFalse(self.c.events())

    def test_unsupported_structure_visibly_fails(self):
        p = self.pipeline()
        original = contracts.structural
        def unsupported(c, fid):
            result = original(c, fid)
            result["unsupported"] = ["TITLE"]
            result["rows"][0]["classification"] = "UNSUPPORTED"
            return result
        with patch.object(contracts, "structural", side_effect=unsupported):
            result = p.prepare(self.workspace(), "unsupported-structure", review_rationale="Public coverage")
        self.assertEqual(result["outcome"], "STRUCTURAL_COVERAGE_FAILURE")
        self.assertNotIn("grant", result)

    def test_author_receipt_substitution_denied(self):
        p = self.pipeline()
        ready = p.prepare(self.workspace(), "receipt", review_rationale="Public coverage")
        model = p.author(ready["bundle"], ready["grant"], ready["freeze"])
        a = self.c.artifact(model)
        a["content"]["receipt"]["input_identity"] = "wrong"
        replacement = p.reg("author", "model", a["content"], **a["dependencies"])
        with self.assertRaises(Failure):
            p.check(replacement)


class VerificationFreezeTests(unittest.TestCase):
    def test_all_supported_external_calibrations(self):
        for default in (None, "LOW", "NORMAL", "HIGH"):
            c = contract(default)
            plan = verification.produce(c)
            verification.review(c, plan)
            model = change_default(source_model(), default or "NORMAL")
            result = verification.execute(generate(parse(canonical(model).decode())), plan)
            self.assertEqual(result[0], "BEHAVIORALLY_VERIFIED", result)

    def test_coverage_assertion_without_observation_rejects(self):
        c = contract()
        plan = verification.produce(c)
        plan["cases"][0]["steps"][0]["contains"] = []
        old = plan["cases"][0].pop("identity")
        new = digest(plan["cases"][0])
        plan["cases"][0]["identity"] = new
        plan["coverage"][0]["cases"] = [new]
        with self.assertRaises(Failure):
            verification.review(c, plan)

    def test_ai_verifier_candidate_remains_untrusted(self):
        c = contract()
        a = AIAdapter("verifier", {}, transport=transport({"plan": verification.produce(c)}))
        result = verification.candidate_plan(a, c, "seal", "profile")
        self.assertEqual(result["outcome"], "READY")
        self.assertEqual(a.receipts[-1]["authority"], "UNTRUSTED_CANDIDATE")

    def test_containment_filesystem_and_network(self):
        plan = verification.produce(contract())
        for code in ('open("C:/dev/lykoi-lang/README.md").read()', 'import socket; socket.socket()', 'import subprocess; subprocess.run(["cmd"])'):
            with self.assertRaises(Failure) as error:
                verification.execute(code, plan)
            self.assertEqual(error.exception.code, "CONTAINMENT_FAILURE")

    def test_runtime_failure_distinct(self):
        with patch("lykoi_rehearsal.verification.subprocess.run", side_effect=OSError("unavailable")):
            self.assertEqual(verification.execute("", verification.produce(contract()))[0], "RUNTIME_FAILURE")

    def test_timeout_is_containment_failure(self):
        import subprocess
        with patch("lykoi_rehearsal.verification.subprocess.run", side_effect=subprocess.TimeoutExpired("worker", 10)):
            with self.assertRaises(Failure) as error:
                verification.execute("", verification.produce(contract()))
            self.assertEqual(error.exception.code, "CONTAINMENT_FAILURE")

    def test_freeze_drift_and_requirement_blind_eligibility(self):
        candidate = seal_snapshot()
        self.assertTrue(integrity(candidate))
        result = eligibility(candidate)
        self.assertFalse(result["eligible"])
        self.assertIn("PUBLIC_FREEZE_NOT_ACTIVE", result["blockers"])
        self.assertIn("REAL_AI_CALIBRATION_NOT_EXERCISED", result["blockers"])
        candidate["instructions"]["author"] += " drift"
        self.assertFalse(integrity(candidate))
        self.assertIn("COMPONENT_OR_CONFIGURATION_DRIFT", eligibility(candidate)["blockers"])

    def test_activation_does_not_override_model_qualification(self):
        candidate = seal_snapshot()
        activation = {"active": True, "purpose": "FUTURE_PUBLIC_REHEARSAL_ONLY", "candidate_identity": candidate["identity"]}
        result = eligibility(candidate, activation=activation)
        self.assertFalse(result["eligible"])
        self.assertNotIn("PUBLIC_FREEZE_NOT_ACTIVE", result["blockers"])
        self.assertIn("SEMANTIC_AUTHOR_MODELS_NOT_CONFIGURED", result["blockers"])


if __name__ == "__main__":
    unittest.main()
