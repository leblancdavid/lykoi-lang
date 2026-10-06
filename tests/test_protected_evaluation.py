"""R5.94 synthetic-only engineering challenges. No actual held-out identities."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from lykoi_controller import Failure, canonical
from lykoi_pipeline.controller import digest
from lykoi_pipeline.example import PRINCIPALS as BASE, CREDENTIALS as TOKENS
from lykoi_rehearsal.public_freeze_r5_91 import configurations, integrity as public_integrity
from lykoi_rehearsal.service import public_author_seed
from lykoi_workspace.example import obligation
from lykoi_protected import CLASSIFICATION, PURPOSE
from lykoi_protected.adapter import ProtectedAIAdapter
from lykoi_protected.compatibility import frc, contracts, mappings, service
from lykoi_protected.controller import ProtectedController
from lykoi_protected.freeze import seal_snapshot, integrity
from lykoi_protected.pipeline import ProtectedPipeline
from lykoi_protected.policy import POLICY
from lykoi_protected.workspace import ProtectedWorkspace, ProvenanceWorkspace
from test_public_rehearsal import transport, rows, source_model

PRINCIPALS = copy.deepcopy(BASE)
PRINCIPALS["custodian"] = {"credential": "synthetic-custodian", "roles": ["admission", "owner"], "projects": ["public"]}
CREDENTIALS = {**TOKENS, "admission": "synthetic-custodian"}
TEXT = "Create tasks with titles. Omitted priority uses NORMAL."
IDENTITY = "HELDOUT-SYNTH-001"
RUN = "R5.94.synthetic-success"


def producers(config, classification=CLASSIFICATION, unsupported=False, questions=False):
    def obligations(text):
        result = rows(text, "NORMAL")
        if unsupported:
            result.append(obligation("ORDER", text, "Task listing order is unconstrained.", "filter_order",
                                     {"domain": "task lists", "ordering": "unconstrained"}))
        return result
    def formal(req):
        obs = obligations(req["source"]["text"])
        return {"obligations": obs, "authority": {o["id"]: [req["evidence"][0]["identity"]] for o in obs},
                "questions": [{"id": "Q", "text": "Which priority?", "priority": "BLOCKING", "affects": ["DEFAULT"]}] if questions else [],
                "issues": []}
    def review(req):
        assert "candidate" not in req and "obligations" not in req
        text = req["source"]["text"]
        obs = obligations(text)
        return {"inventory": {"version": "SourceObligationInventory-0.1", "source_commitment": req["source_commitment"],
                "extractor": "synthetic-independent-fixture", "context_class": "SYNTHETIC_ENGINEERING", "items": [
                    {"id": o["id"], "spans": [{"start": 0, "end": len(text), "quote": text}], "meaning": o["statement"],
                     "category": "BEHAVIOR", "material": True, "dependencies": []} for o in obs], "questions": [], "limitations": ["Not live AI"]},
                "interpretations": {o["id"]: {k: o[k] for k in ("statement", "relation")} for o in obs},
                "authority": {o["id"]: [req["evidence"][0]["identity"]] for o in obs}}
    return (ProtectedAIAdapter("formalizer", config["roles"]["formalizer"], classification=classification, transport=transport(formal)),
            ProtectedAIAdapter("reviewer", config["roles"]["reviewer"], classification=classification, transport=transport(review)))


class ProtectedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "protected.sqlite"
        self.candidate = seal_snapshot()
        self.config = configurations()
        self.c = self.open()

    def open(self, candidate=None):
        return ProtectedController(self.path, PRINCIPALS, candidate=candidate or self.candidate,
                                   model_configurations=self.config, author_seed=public_author_seed())

    def tearDown(self):
        self.c.close()
        self.tmp.cleanup()

    def call(self, role, command, **args):
        return self.c.execute(CREDENTIALS[role], "public", command, expected_revision=self.c.revision, **args)

    def activate(self, purpose=PURPOSE):
        return self.call("owner", "protected_activate", purpose=purpose, candidate_identity=self.candidate["identity"])

    def authorize(self, identity=IDENTITY, run=RUN, mode="UNAVAILABLE_TERMINATE"):
        return self.call("owner", "protected_authorize", source_identity=identity, run=run,
                         policy_identity=digest(POLICY), clarification={"mode": mode, "principal": None if mode == "UNAVAILABLE_TERMINATE" else "human"})

    def workspace(self, *, unsupported=False, questions=False, mode="UNAVAILABLE_TERMINATE"):
        self.activate()
        auth = self.authorize(mode=mode)
        w = ProtectedWorkspace(self.c, "public", RUN, CREDENTIALS, authorization=auth, source_identity=IDENTITY)
        text = TEXT + (" Task listing order is unconstrained." if unsupported else "")
        w.admit(lambda: text)
        f, r = producers(self.config, unsupported=unsupported, questions=questions)
        fid = w.formalize(f)
        soi = w.commit_inventory(r)
        coverage = w.reconcile(soi)
        return w, fid, soi, coverage, auth

    def pipeline(self, auth):
        def author(req):
            self.assertEqual(set(req), {"version", "run", "v1", "toolchain", "fixture"})
            self.assertNotIn(TEXT, canonical(req).decode())
            self.assertNotIn(IDENTITY, canonical(req).decode())
            return {"source": source_model()}
        a = ProtectedAIAdapter("author", self.config["roles"]["author"], transport=transport(author))
        return ProtectedPipeline(self.c, "public", CREDENTIALS, a, authorization=auth, source_identity=IDENTITY, run=RUN)

    def test_synthetic_success_and_exact_roles(self):
        w, fid, soi, coverage, auth = self.workspace()
        self.assertEqual(self.c.artifact(fid)["content"]["contract"]["source"]["classification"], CLASSIFICATION)
        w.approve(CREDENTIALS["owner"], fid)
        seal = w.seal(fid)
        p = self.pipeline(auth)
        ready = p.prepare(seal, RUN, review_rationale="Synthetic exact authority review")
        self.assertEqual(ready["outcome"], "IMPLEMENTATION_AUTHORIZED", ready)
        result = p.execute(ready)
        self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)
        ledger = self.c.ledger(IDENTITY)
        self.assertEqual({k: ledger["counters"][k] for k in ("authorizations", "source_opens", "source_admissions", "formalizer_exposures", "reviewer_exposures", "author_exposures")},
                         dict.fromkeys(("authorizations", "source_opens", "source_admissions", "formalizer_exposures", "reviewer_exposures", "author_exposures"), 1))
        self.assertEqual(ledger["counters"]["verifier_exposures"], 3)
        self.assertEqual(ledger["counters"]["development_exposures"], 0)
        self.assertFalse(ledger["pristine"])
        self.assertEqual(ledger["development_knowledge"], "AUTHORIZED_DERIVED_EXPOSURE")
        for key in ("structural", "bdi", "adequacy", "v1", "plan_seal", "grant", "model", "target", "verification"):
            self.assertEqual(self.c.protected_origin(result[key]), auth)
        self.c.check_integrity()
        self.c.close()
        self.c = self.open()
        self.assertEqual(self.c.ledger(IDENTITY), ledger)

    def test_unsupported_mapping_halts_without_grant(self):
        w, fid, _, _, auth = self.workspace(unsupported=True)
        w.approve(CREDENTIALS["owner"], fid)
        seal = w.seal(fid)
        result = self.pipeline(auth).prepare(seal, RUN, review_rationale="Synthetic unsupported complete source")
        self.assertEqual(result["outcome"], "UNREPRESENTABLE_SOURCE", result)
        self.assertIn("adequacy", result)
        self.assertNotIn("grant", result)
        self.assertFalse(any(e["type"] == "GRANT_ISSUED" for e in self.c.events()))
        self.assertEqual(self.c.ledger(IDENTITY)["counters"]["author_exposures"], 0)

    def test_authorization_is_opaque_and_not_access(self):
        self.activate()
        auth = self.authorize()
        c = self.c.artifact(auth)["content"]
        self.assertNotIn("text", c)
        self.assertNotIn("sha256", c)
        ledger = self.c.ledger(IDENTITY)
        self.assertTrue(ledger["pristine"])
        self.assertEqual(ledger["observed_states"], ["PRISTINE", "AUTHORIZED_NOT_ACCESSED"])
        self.assertEqual(ledger["counters"]["source_opens"], 0)

    def deny_open(self, auth, identity=IDENTITY, run=RUN):
        called = []
        w = ProtectedWorkspace(self.c, "public", run, CREDENTIALS, authorization=auth, source_identity=identity)
        with self.assertRaises(Failure):
            w.admit(lambda: called.append(True) or TEXT)
        self.assertFalse(called)
        self.assertEqual(self.c.events()[-1]["type"], "PROTECTED_DENIED")

    def test_without_activation_no_open(self):
        self.deny_open("not-authorized")

    def test_without_source_authorization_no_open(self):
        self.activate()
        self.deny_open("not-authorized")

    def test_wrong_identity_and_cross_source_authorization(self):
        self.activate()
        auth = self.authorize()
        self.deny_open(auth, "HELDOUT-SYNTH-002")

    def test_wrong_run_denied(self):
        self.activate()
        self.deny_open(self.authorize(), run="other-run")

    def test_stale_authorization_denied(self):
        self.activate()
        auth = self.authorize()
        self.call("owner", "invalidate", subject=auth, reason="Synthetic stale authority")
        self.deny_open(auth)

    def test_public_scope_cannot_activate_protected(self):
        with self.assertRaises(Failure):
            self.activate("FUTURE_PUBLIC_REHEARSAL_ONLY")
        self.assertEqual(self.c.events()[-1]["type"], "PROTECTED_DENIED")

    def test_scope_rejects_unmediated_public_workflow(self):
        self.activate()
        with self.assertRaises(Failure):
            self.call("owner", "register", kind="message", content={"text": TEXT})
        self.assertEqual(self.c.events()[-1]["type"], "TRANSITION_DENIED")

    def test_author_original_source_denied_and_audited(self):
        w, _, _, _, auth = self.workspace()
        with self.assertRaises(Failure):
            self.call("author", "protected_deliver", subject=w.source, authorization=auth,
                      source_identity=IDENTITY, run=RUN, recipient_role="author", session="synthetic-author")
        self.assertEqual(self.c.ledger(IDENTITY)["counters"]["author_exposures"], 0)
        self.assertEqual(self.c.ledger(IDENTITY)["counters"]["denials"], 1)

    def test_reviewer_candidate_before_commitment_denied(self):
        self.activate()
        auth = self.authorize()
        w = ProtectedWorkspace(self.c, "public", RUN, CREDENTIALS, authorization=auth, source_identity=IDENTITY)
        w.admit(lambda: TEXT)
        fid = w.formalize(producers(self.config)[0])
        with self.assertRaises(Failure) as error:
            self.call("reviewer", "protected_deliver", subject=fid, authorization=auth,
                      source_identity=IDENTITY, run=RUN, recipient_role="reviewer", session="blind-review")
        self.assertEqual(error.exception.code, "PROTECTED_SOI_COMMITMENT_REQUIRED")

    def test_single_open_and_authorization(self):
        w, _, _, _, _ = self.workspace()
        with self.assertRaises(Failure):
            self.authorize(run="another-run")
        called = []
        with self.assertRaises(Failure):
            w.admit(lambda: called.append(True) or TEXT)
        self.assertFalse(called)
        self.assertEqual(self.c.ledger(IDENTITY)["counters"]["source_opens"], 1)

    def test_failed_delivery_is_still_exposure(self):
        self.activate()
        auth = self.authorize()
        w = ProtectedWorkspace(self.c, "public", RUN, CREDENTIALS, authorization=auth, source_identity=IDENTITY)
        w.admit(lambda: TEXT)
        f, _ = producers(self.config)
        f.transport = lambda _: (_ for _ in ()).throw(Failure("SYNTHETIC_PRODUCER_FAILURE"))
        with self.assertRaises(Failure):
            w.formalize(f)
        ledger = self.c.ledger(IDENTITY)
        self.assertEqual(ledger["counters"]["formalizer_exposures"], 1)
        self.assertEqual(ledger["counters"]["reviewer_exposures"], 0)
        self.assertNotIn("AUTHOR_EXPOSED", ledger["observed_states"])

    def test_incomplete_open_is_durable_and_not_retryable(self):
        self.activate()
        auth = self.authorize()
        w = ProtectedWorkspace(self.c, "public", RUN, CREDENTIALS, authorization=auth, source_identity=IDENTITY)
        with self.assertRaises(OSError):
            w.admit(lambda: (_ for _ in ()).throw(OSError("synthetic failure")))
        self.deny_open(auth)
        ledger = self.c.ledger(IDENTITY)
        self.assertEqual(ledger["counters"]["open_attempts"], 1)
        self.assertEqual(ledger["counters"]["source_opens"], 0)
        self.assertIn("INCOMPLETE", ledger["observed_states"])

    def test_clarification_unavailable_terminates(self):
        w, fid, _, _, auth = self.workspace(questions=True)
        with self.assertRaises(Failure) as error:
            w.ask("Q")
        self.assertEqual(error.exception.code, "PROTECTED_CLARIFICATION_UNAVAILABLE")
        self.assertIn("CLARIFICATION_UNAVAILABLE", self.c.ledger(IDENTITY)["observed_states"])
        self.assertFalse(any(e["type"] == "CLARIFICATION_ANSWERED" for e in self.c.events()))

    def test_clarification_available_preserves_protected_revision(self):
        w, _, _, _, auth = self.workspace(questions=True, mode="HUMAN_AVAILABLE")
        q = w.ask("Q")
        fresh = w.answer(CREDENTIALS["owner"], q, "Omitted priority uses NORMAL.")
        self.assertEqual(w.source, fresh)
        self.assertEqual(self.c.artifact(fresh)["content"]["classification"], CLASSIFICATION)
        self.assertEqual(self.c.protected_origin(fresh), auth)
        self.assertTrue(any(e["type"] == "CLARIFICATION_ANSWERED" for e in self.c.events()))

    def test_provenance_invariance(self):
        w, fid, _, _, _ = self.workspace()
        protected = self.c.artifact(fid)["content"]["contract"]
        other = service.RehearsalController(Path(self.tmp.name) / "public.sqlite", BASE,
                    model_configurations=self.config, author_seed=public_author_seed())
        try:
            public_w = ProvenanceWorkspace(other, "public", RUN, TOKENS, classification="PUBLIC")
            public_w.ingest(TOKENS["owner"], TEXT)
            f, r = producers(self.config, "PUBLIC")
            public_id = public_w.formalize(f)
            soi = public_w.commit_inventory(r)
            public_w.reconcile(soi)
            public_w.approve(TOKENS["owner"], public_id)
            public_w.seal(public_id)
            public = other.artifact(public_id)["content"]["contract"]
            for key in ("context", "obligations", "issues", "unspecified", "implementation_choices", "lineage"):
                self.assertEqual(public[key], protected[key])
            pp, sp = contracts.structural(public, "frc"), contracts.structural(protected, "frc")
            self.assertEqual(pp, sp)
            self.assertEqual(mappings.project(public)["normalized"], mappings.project(protected)["normalized"])
            self.assertEqual(contracts.bdi(public, pp)["result"]["decisions"], contracts.bdi(protected, sp)["result"]["decisions"])
            self.assertEqual(contracts.adequate(public, contracts.bdi(public, pp))["outcome"], contracts.adequate(protected, contracts.bdi(protected, sp))["outcome"])
            self.invariance_evidence = {"synthetic_only": True, "public_source_class": public["source"]["classification"],
                "protected_source_class": protected["source"]["classification"], "same_content_sha256": public["source"]["sha256"] == protected["source"]["sha256"],
                "formal_semantics_equal": True, "structural_projection_equal": True,
                "V1_normalized_equal": True, "BDI_decisions_equal": True, "adequacy_outcome_equal": True,
                "public_contract_identity": digest(public), "protected_contract_identity": digest(protected),
                "semantic_projection_identity": digest(mappings.project(protected)["normalized"])}
        finally:
            other.close()

    def test_validator_does_not_weaken_contract_checks(self):
        w, fid, _, _, _ = self.workspace()
        contract = self.c.artifact(fid)["content"]["contract"]
        for mutate in (lambda c: c["source"].update(sha256="wrong"),
                       lambda c: c["obligations"].append(copy.deepcopy(c["obligations"][0])),
                       lambda c: c["source"].update(classification="PROTECTED"),
                       lambda c: c.update(extra="unknown")):
            changed = copy.deepcopy(contract)
            mutate(changed)
            with self.assertRaises(frc.ContractError):
                frc.validate(changed)
        from benchmark.evaluation.formal_requirements_r5_80 import validate, ContractError
        with self.assertRaises(ContractError):
            validate(contract)

    def test_freeze_integrity_and_historical_identity(self):
        self.assertTrue(integrity(self.candidate))
        changed = copy.deepcopy(self.candidate)
        changed["role_policy"]["raw"].append("author")
        changed["identity"] = digest({k: v for k, v in changed.items() if k != "identity"})
        self.assertFalse(integrity(changed))
        from lykoi_pipeline.controller import ROOT
        self.assertTrue(public_integrity(json.loads((ROOT / "benchmark/results/phase5c/r5_91/public-freeze-final.json").read_text())))

    def test_restart_rejects_new_freeze(self):
        self.activate()
        self.c.close()
        changed = copy.deepcopy(self.candidate)
        changed["identity"] = "substitution"
        with self.assertRaises(Failure):
            self.open(changed)
        self.c = self.open()

    def test_public_active_controller_cannot_reserve_protected_source(self):
        from lykoi_rehearsal.public_service_r5_91 import PublicController, ACTIVATION
        from lykoi_rehearsal.public_freeze_r5_91 import seal_snapshot as public_candidate, PURPOSE as PUBLIC
        candidate = public_candidate()
        other = PublicController(Path(self.tmp.name) / "public.sqlite", BASE, candidate=candidate,
                                 model_configurations=self.config, author_seed=public_author_seed())
        try:
            def call(command, **args):
                return other.execute(TOKENS["owner"], "public", command, expected_revision=other.revision, **args)
            active = call("register", kind="context", content={"version": ACTIVATION, "purpose": PUBLIC,
                           "candidate_identity": candidate["identity"], "active": True})
            call("adopt", subject=active)
            with self.assertRaises(Failure):
                call("protected_reserve", authorization="synthetic-no-authority", source_identity=IDENTITY, run=RUN)
            self.assertEqual(other.events()[-1]["type"], "TRANSITION_DENIED")
        finally:
            other.close()

    def test_verifier_original_source_and_inventory_denied(self):
        w, fid, soi, _, auth = self.workspace()
        for aid in (w.source, soi):
            with self.assertRaises(Failure):
                self.call("verifier", "protected_deliver", subject=aid, authorization=auth,
                          source_identity=IDENTITY, run=RUN, recipient_role="verifier", session="synthetic-verifier")
        delivered = self.call("verifier", "protected_deliver", subject=fid, authorization=auth,
                    source_identity=IDENTITY, run=RUN, recipient_role="verifier", session="synthetic-verifier")
        self.assertNotIn(TEXT, canonical(delivered).decode())
        self.assertNotIn("source_quote", canonical(delivered).decode())

    def test_author_role_escalation_denied(self):
        w, _, _, _, auth = self.workspace()
        with self.assertRaises(Failure):
            self.call("author", "protected_deliver", subject=w.source, authorization=auth,
                      source_identity=IDENTITY, run=RUN, recipient_role="formalizer", session="synthetic-author")
        self.assertEqual(self.c.events()[-1]["reason"]["code"], "ROLE_DENIED")

    def test_reviewer_structural_candidate_side_channel_denied(self):
        self.activate()
        auth = self.authorize()
        w = ProtectedWorkspace(self.c, "public", RUN, CREDENTIALS, authorization=auth, source_identity=IDENTITY)
        w.admit(lambda: TEXT)
        fid = w.formalize(producers(self.config)[0])
        structural = w._reg("formalizer", "structural", {"proposal": "candidate-derived"}, frc=fid)
        with self.assertRaises(Failure):
            self.call("reviewer", "protected_deliver", subject=structural, authorization=auth,
                      source_identity=IDENTITY, run=RUN, recipient_role="reviewer", session="synthetic-blind-review")

    def test_read_before_failed_admission_remains_exposed(self):
        self.activate()
        auth = self.authorize()
        w = ProtectedWorkspace(self.c, "public", RUN, CREDENTIALS, authorization=auth, source_identity=IDENTITY)
        with self.assertRaises(Failure):
            w.admit(lambda: "")
        ledger = self.c.ledger(IDENTITY)
        self.assertEqual(ledger["counters"]["source_reads"], 1)
        self.assertEqual(ledger["counters"]["source_admissions"], 0)
        self.assertFalse(ledger["pristine"])

    def test_pre_authorized_clarification_authority(self):
        w, _, _, _, _ = self.workspace(questions=True, mode="PREAUTHORIZED_AUTHORITY")
        q = w.ask("Q")
        with self.assertRaises(Failure):
            w.answer(CREDENTIALS["admission"], q, "Synthetic unauthorized answer")
        fresh = w.answer(CREDENTIALS["owner"], q, "Omitted priority uses NORMAL.")
        self.assertEqual(self.c.artifact(fresh)["content"]["classification"], CLASSIFICATION)

    def test_candidate_source_substitution_and_relabeling_denied(self):
        w, fid, _, _, _ = self.workspace()
        for classification in ("PUBLIC", "SYNTHETIC"):
            content = copy.deepcopy(self.c.artifact(fid)["content"])
            content["contract"]["source"]["classification"] = classification
            with self.assertRaises(Failure):
                w._reg("formalizer", "frc", content, source=w.source)
        content = copy.deepcopy(self.c.artifact(fid)["content"])
        content["contract"]["source"]["id"] = "synthetic-substitution"
        with self.assertRaises(Failure):
            w._reg("formalizer", "frc", content, source=w.source)

    def test_append_only_ledger_cannot_erase_exposures(self):
        import sqlite3
        self.workspace()
        before = self.c.ledger(IDENTITY)
        with self.assertRaises(sqlite3.IntegrityError):
            self.c.db.execute("DELETE FROM journal")
        self.assertEqual(before, self.c.ledger(IDENTITY))

    def test_protected_workspace_requires_protected_controller(self):
        other = service.RehearsalController(Path(self.tmp.name) / "public.sqlite", BASE,
                    model_configurations=self.config, author_seed=public_author_seed())
        try:
            with self.assertRaises(Failure):
                ProvenanceWorkspace(other, "public", RUN, TOKENS, classification=CLASSIFICATION)
            with self.assertRaises(Failure):
                ProtectedWorkspace(other, "public", RUN, TOKENS, authorization="synthetic-none", source_identity=IDENTITY)
        finally:
            other.close()

    def test_protected_schema_only_extends_provenance(self):
        from lykoi_pipeline.controller import ROOT
        schema = json.loads((ROOT / "schema/formal-requirement-contract-protected-v0.1.schema.json").read_text())
        original = json.loads((ROOT / "schema/formal-requirement-contract-v0.1.schema.json").read_text())
        self.assertEqual(schema["required"], original["required"])
        self.assertFalse(schema["additionalProperties"])
        self.assertEqual(schema["properties"]["source"]["properties"]["classification"]["enum"], ["SYNTHETIC", "PUBLIC", CLASSIFICATION])
        from benchmark.evaluation.formal_requirements_r5_80 import KINDS
        self.assertEqual(frc.KINDS, KINDS)

    def test_wrong_worker_configuration_denies_before_exposure(self):
        self.activate()
        auth = self.authorize()
        w = ProtectedWorkspace(self.c, "public", RUN, CREDENTIALS, authorization=auth, source_identity=IDENTITY)
        w.admit(lambda: TEXT)
        f, _ = producers(self.config)
        f.config["model"] = "unfrozen-synthetic-model"
        with self.assertRaises(Failure):
            w.formalize(f)
        self.assertEqual(self.c.ledger(IDENTITY)["counters"]["formalizer_exposures"], 0)


if __name__ == "__main__":
    unittest.main()
