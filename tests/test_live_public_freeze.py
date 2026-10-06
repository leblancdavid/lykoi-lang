"""Prospective public-only admission/isolation tests; never protected inputs."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from lykoi_controller import Failure, canonical
from lykoi_pipeline.controller import digest
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_rehearsal.opencode_adapter import OpenCodeAdapter, cli_configuration, normalize_plan
from lykoi_rehearsal.public_freeze_r5_91 import configurations, seal_snapshot, integrity, eligibility, PURPOSE
from lykoi_rehearsal.public_service_r5_91 import PublicController, PublicPipeline, ACTIVATION
from lykoi_rehearsal.service import public_author_seed
from lykoi_rehearsal.verification import produce, review
from lykoi_workspace import Workspace
from test_public_rehearsal import contract
from test_public_rehearsal import rows


class LiveAdapterTests(unittest.TestCase):
    def adapter_request(self):
        a = OpenCodeAdapter("reviewer", configurations()["roles"]["reviewer"])
        request = {"role": "reviewer", "session": a.session,
                   "source": {"identity": "source", "text": "Create tasks with titles.", "revision": 1},
                   "evidence": [], "output_schema": "WorkspaceSOI-1", "instructions": "source only"}
        return a, request

    def test_candidate_rejected_before_cli_dispatch(self):
        a, request = self.adapter_request()
        request["candidate"] = "forbidden"
        with self.assertRaises(Failure), patch("subprocess.run") as invoke:
            a.produce(request)
        invoke.assert_not_called()

    def test_scoped_source_metadata_and_no_tools(self):
        a, request = self.adapter_request()
        bound = a._request(request)
        self.assertEqual(bound["source_span"], {"start": 0, "end": 25, "quote": request["source"]["text"]})
        self.assertNotIn("candidate", bound)
        config = cli_configuration("reviewer", "github-copilot/claude-sonnet-4.6")
        self.assertEqual(config["tools"], {"*": False})
        self.assertEqual(config["permission"], "deny")
        self.assertFalse(config["compaction"]["auto"])

    def test_cli_error_does_not_publish_secret_headers(self):
        a, request = self.adapter_request()
        result = type("Result", (), {"returncode": 0, "stdout": json.dumps({"type": "error", "error": {
            "data": {"statusCode": 401, "responseHeaders": {"Authorization": "test-secret"}}}}).encode(), "stderr": b"test-secret"})()
        with patch("subprocess.run", return_value=result):
            with self.assertRaises(Failure) as caught:
                a.produce(request)
        self.assertNotIn("test-secret", canonical({"failure": caught.exception.as_dict(), "attempts": a.attempts}).decode())
        self.assertFalse(a.receipts)

    def test_cli_fresh_session_stdin_and_instruction_isolation(self):
        a = OpenCodeAdapter("formalizer", configurations()["roles"]["formalizer"])
        request = {"role": a.role, "session": a.session, "source": {"identity": "source", "text": "Create tasks with titles.", "revision": 1},
                   "evidence": [], "output_schema": "WorkspaceAnalysis-1", "instructions": "WHAT"}
        def invoke(argv, **kwargs):
            self.assertNotIn("--session", argv)
            self.assertNotIn("--continue", argv)
            self.assertNotIn("--attach", argv)
            self.assertNotIn("OPENCODE_SERVER_PASSWORD", kwargs["env"])
            self.assertNotEqual(Path(kwargs["cwd"]), Path.cwd())
            sent = json.loads(kwargs["input"])
            text = json.dumps({"binding": sent["binding"], "output": {"obligations": [], "authority": {}, "questions": [], "issues": []}})
            event = {"type": "text", "sessionID": "fresh-public-session", "part": {"text": text}}
            return type("Result", (), {"returncode": 0, "stdout": json.dumps(event).encode(), "stderr": b""})()
        with patch("subprocess.run", side_effect=invoke):
            a.produce(request)
        self.assertEqual(a.receipts[-1]["authority"], "UNTRUSTED_CANDIDATE")
        self.assertIsNone(a.receipts[-1]["returned_model"])

    def test_plan_identity_assignment_preserves_expectations(self):
        c = contract()
        plan = produce(c)
        case = plan["cases"][0]
        old_steps = copy.deepcopy(case["steps"])
        plan["coverage"][0]["cases"] = [case["id"]]
        case.pop("identity")
        normalized = normalize_plan(plan)
        review(c, normalized)
        self.assertEqual(old_steps, normalized["cases"][0]["steps"])


class PublicFreezeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.candidate = seal_snapshot()
        self.db = Path(self.tmp.name) / "public.sqlite"
        self.c = self.open()

    def open(self, candidate=None):
        return PublicController(self.db, PRINCIPALS, candidate=candidate or self.candidate,
                                model_configurations=configurations(), author_seed=public_author_seed())

    def tearDown(self):
        self.c.close()
        self.tmp.cleanup()

    def activate(self):
        aid = self.c.execute(CREDENTIALS["owner"], "public", "register", expected_revision=self.c.revision,
                             kind="context", content={"version": ACTIVATION, "purpose": PURPOSE,
                                                       "candidate_identity": self.candidate["identity"], "active": True})
        self.c.execute(CREDENTIALS["owner"], "public", "adopt", expected_revision=self.c.revision, subject=aid)
        return self.c.activation()

    def test_requirement_refused_before_activation_and_not_stored(self):
        w = Workspace(self.c, "public", "public-test", CREDENTIALS)
        with self.assertRaises(Failure) as caught:
            w.ingest(CREDENTIALS["owner"], "Create tasks with titles.")
        self.assertEqual(caught.exception.code, "PUBLIC_REHEARSAL_INELIGIBLE")
        self.assertEqual(self.c.db.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0], 0)
        self.assertEqual(self.c.events()[-1]["type"], "TRANSITION_DENIED")

    def test_activation_predates_admission_and_survives_restart(self):
        active = self.activate()
        Workspace(self.c, "public", "old-public-calibration-only", CREDENTIALS).ingest(CREDENTIALS["owner"], "Create tasks with titles.")
        proof = self.c.prove_admission_order()
        self.assertTrue(proof["freeze_predates_every_admission"])
        self.assertLess(active["revision"], min(proof["admission_revisions"]))
        self.c.close()
        self.c = self.open()
        self.assertEqual(self.c.activation(), active)
        self.assertTrue(self.c.prove_admission_order()["freeze_predates_every_admission"])

    def test_model_prompt_schema_adapter_and_mapping_drift_change_identity(self):
        self.assertTrue(integrity(self.candidate))
        for field in ("models", "instructions", "schemas", "versions", "mapping_registry"):
            changed = copy.deepcopy(self.candidate)
            changed[field]["drift"] = "changed"
            changed["identity"] = digest({k: v for k, v in changed.items() if k != "identity"})
            self.assertNotEqual(changed["identity"], self.candidate["identity"])
            self.assertFalse(integrity(changed))

    def test_worker_cannot_activate_or_grant(self):
        with self.assertRaises(Failure):
            self.c.execute(CREDENTIALS["author"], "public", "register", expected_revision=self.c.revision,
                           kind="context", content={"version": ACTIVATION, "purpose": PURPOSE,
                                                     "candidate_identity": self.candidate["identity"], "active": True})
        self.assertIsNone(self.c.activation())
        self.activate()
        self.assertTrue(eligibility(self.candidate, self.c)["eligible"])

    def test_missing_live_smoke_blocks_even_self_rehashed_freeze(self):
        changed = copy.deepcopy(self.candidate)
        changed["smoke"]["roles"]["author"]["receipt"]["execution"] = "TEST_TRANSPORT_NOT_REAL_AI"
        self.assertFalse(eligibility(changed, self.c)["eligible"])

    def test_restart_rejects_freeze_substitution(self):
        self.activate()
        self.c.close()
        changed = copy.deepcopy(self.candidate)
        changed["identity"] = "substitution"
        with self.assertRaises(Failure):
            self.open(changed)
        self.c = self.open()

    def test_pipeline_rejects_inactive_freeze_before_consuming_what(self):
        with self.assertRaises(Failure):
            PublicPipeline(self.c, "public", CREDENTIALS, OpenCodeAdapter("author", configurations()["roles"]["author"]))
        self.assertFalse(self.c.events())

    def test_repeat_activation_denied(self):
        self.activate()
        with self.assertRaises(Failure):
            self.activate()

    def test_public_native_chain_with_mock_cli_remains_controller_gated(self):
        # Public development source already used in R5.89, never a future task.
        # Mocked CLI events test wiring only; not counted as live smoke evidence.
        import subprocess
        original_run = subprocess.run
        self.activate()
        def invoke(argv, **kwargs):
            if Path(argv[0]) != Path(configurations()["roles"]["author"]["executable"]):
                return original_run(argv, **kwargs)
            sent = json.loads(kwargs["input"])
            request = sent["input"]
            role = argv[argv.index("--agent") + 1].removeprefix("lykoi-")
            if role == "author":
                self.assertEqual(set(request), {"version", "run", "v1", "toolchain", "fixture"})
                output = {"source": request["fixture"]["source"]}
            else:
                text = request["source"]["text"]
                obligations = rows(text)
                authority = {o["id"]: [request["evidence"][0]["identity"]] for o in obligations}
                if role == "formalizer":
                    output = {"obligations": obligations, "authority": authority, "questions": [], "issues": []}
                else:
                    self.assertNotIn("candidate", request)
                    output = {"inventory": {"version": "SourceObligationInventory-0.1",
                              "source_commitment": request["source_commitment"], "extractor": "test-only",
                              "context_class": "MOCK_CLI_NOT_LIVE", "items": [{"id": "TITLE",
                              "spans": [request["source_span"]], "meaning": obligations[0]["statement"],
                              "category": "BEHAVIOR", "material": True, "dependencies": []}], "questions": [], "limitations": []},
                              "authority": authority, "interpretations": {o["id"]: {k: o[k] for k in ("statement", "relation")} for o in obligations}}
            event = {"type": "text", "sessionID": "mock-cli-session-" + role,
                     "part": {"text": json.dumps({"binding": sent["binding"], "output": output})}}
            return type("Result", (), {"returncode": 0, "stdout": json.dumps(event).encode(), "stderr": b""})()
        with patch("subprocess.run", side_effect=invoke):
            w = Workspace(self.c, "public", "old-public-title-only", CREDENTIALS)
            w.ingest(CREDENTIALS["owner"], "Create tasks with titles.")
            f = OpenCodeAdapter("formalizer", configurations()["roles"]["formalizer"])
            fid = w.formalize(f)
            r = OpenCodeAdapter("reviewer", configurations()["roles"]["reviewer"])
            soi = w.commit_inventory(r)
            w.reconcile(soi)
            w.approve(CREDENTIALS["owner"], fid)
            seal = w.seal(fid)
            p = PublicPipeline(self.c, "public", CREDENTIALS, OpenCodeAdapter("author", configurations()["roles"]["author"]))
            ready = p.prepare(seal, "R5.91.unit-public-wiring", review_rationale="Explicit public synthetic unit review")
            self.assertEqual(ready["outcome"], "IMPLEMENTATION_AUTHORIZED", ready)
            result = p.execute(ready)
            self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)
            self.assertEqual(result["mode"], "PUBLIC_REHEARSAL")
            self.assertTrue(self.c.prove_admission_order()["freeze_predates_every_admission"])


if __name__ == "__main__":
    unittest.main()
