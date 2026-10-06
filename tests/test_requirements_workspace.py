"""R5.87 executable public-only workspace challenges; no protected discovery."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from lykoi_controller import Controller, Failure
from lykoi_workspace import Workspace, SubprocessFixture, ModelAdapter
from lykoi_workspace.example import (SOURCE, PRINCIPALS, CREDENTIALS, obligation,
                                     formalizer_fixture, reviewer_fixture, formalize, review, demonstrate, render_transcript)


class WorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "workspace.sqlite"
        self.c = Controller(self.path, PRINCIPALS)
        self.w = Workspace(self.c, "public", "test-session", CREDENTIALS)

    def tearDown(self):
        self.c.close()
        self.tmp.cleanup()

    def clarified(self, policy=None):
        self.w.ingest("public-human", SOURCE, [policy] if policy else [])
        initial = formalize(self.w)
        q = self.w.ask("PRIORITY.DEFAULT")
        self.w.answer("public-human", q, "NORMAL")
        formalize(self.w)
        q = self.w.ask("IMPORTANT.MEANING")
        self.w.answer("public-human", q, "HIGH")
        return initial, formalize(self.w)

    def draft(self):
        source, evidence = self.w.inputs()
        prior = self.w._records("frc")
        return formalizer_fixture(source, evidence, previous=prior[-1][1]["content"]["contract"] if prior else None)

    def submit(self, output):
        return self.w.formalize(SubprocessFixture("formalizer", "formal-context", output))

    def inventory_output(self):
        source, evidence = self.w.inputs()
        return reviewer_fixture(source, evidence, len(self.w.sources))

    def commit(self, output):
        return self.w.commit_inventory(SubprocessFixture("reviewer", "review-context", output))

    def seal_current(self):
        frc = self.w.candidate
        inv = review(self.w)
        coverage = self.w.reconcile(inv)
        approval = self.w.approve("public-human", frc)
        return frc, coverage, approval, self.w.seal(frc)

    def denied(self, code, callback, *args, **kwargs):
        with self.assertRaises(Failure) as caught:
            callback(*args, **kwargs)
        self.assertEqual(caught.exception.code, code)

    def test_public_end_to_end_controller_seal(self):
        result = demonstrate(Path(self.tmp.name) / "public.sqlite")
        self.assertTrue(result["status"]["authority"]["sealed"])
        self.assertFalse(result["status"]["authority"]["implementation_authorized"])
        self.assertEqual(len(result["summary"]["commitments"]), 4)
        transcript = render_transcript(result)
        self.assertIn("Human: Approve.", transcript)
        self.assertNotIn("sha256", transcript)

    def test_ingestion_exact_version_and_immutable_source(self):
        first = self.w.ingest("public-human", "First\r\nrequirement.")
        second = self.w.ingest("public-human", "First\nrequirement.")
        self.assertNotEqual(first, second)
        self.assertFalse(self.c.state(first)["eligible_for_new_use"])
        message = self.c.artifact(first)["dependencies"]["message"]
        self.assertEqual(self.c.artifact(message)["content"]["text"], "First\r\nrequirement.")

    def test_stable_logical_id_and_new_artifact_after_clarification(self):
        initial, final = self.clarified()
        before = self.c.artifact(initial)["content"]["contract"]
        after = self.c.artifact(final)["content"]["contract"]
        self.assertEqual(before["obligations"][0], after["obligations"][0])
        self.assertNotEqual(initial, final)
        draft = self.draft()
        draft["obligations"][0]["id"] = "UNRELATED.NEW.ID"
        self.denied("UNSTABLE_OBLIGATION_ID", self.submit, draft)

    def test_question_priorities_and_required_human_answer(self):
        self.w.ingest("public-human", SOURCE)
        output = self.draft()
        output["questions"][0]["priority"] = "IMPORTANT"
        output["questions"].append({"id": "INFO", "text": "Display hint", "priority": "INFORMATIONAL"})
        frc = self.submit(output)
        info = self.w.ask("INFO")
        self.assertEqual(self.c.state(frc)["lifecycle"], "DRAFT")
        question = self.w.ask("PRIORITY.DEFAULT")
        self.assertEqual(self.c.state(frc)["lifecycle"], "CLARIFICATION")
        self.denied("ROLE_DENIED", self.w.answer, "public-formalizer", question, "NORMAL")
        self.w.answer("public-human", question, "Human explicitly delegates this choice to the adopted policy.")
        self.assertFalse(self.c.state(frc)["eligible_for_new_use"])
        self.assertEqual(self.c.artifact(info)["content"]["priority"], "INFORMATIONAL")

    def test_ai_status_strings_and_role_escalation_are_inert(self):
        self.w.ingest("public-human", SOURCE)
        output = self.draft()
        output.update(status="APPROVED", approved=True, human_confirmed="HUMAN_CONFIRMED", complete="COMPLETE", ambiguity="NO_AMBIGUITY")
        frc = self.submit(output)
        self.assertFalse(self.c.state(frc)["human_authorized"])
        self.denied("INVALID_TRANSITION", self.w.seal, frc)
        self.denied("ROLE_DENIED", self.w._call, "formalizer", "seal_frc", subject=frc)
        self.denied("ROLE_DENIED", self.w._call, "reviewer", "approve", subject=frc, coverage=frc, structural=frc)

    def test_blind_request_has_no_candidate_or_controller(self):
        self.clarified()
        seen = []
        output = self.inventory_output()
        adapter = ModelAdapter("reviewer", "fresh-review", lambda req: seen.append(req) or output,
                               provider="mock", model="mock-model")
        inventory = self.w.commit_inventory(adapter)
        self.assertEqual(set(seen[0]), {"role", "instructions", "session", "source", "evidence", "output_schema"})
        serialized = json.dumps(seen)
        self.assertNotIn(self.w.candidate, serialized)
        self.assertNotIn("public-controller", serialized)
        self.assertEqual(self.w.reconciliation_inputs(inventory)[0]["type"], "frc")
        events = self.c.events()
        commit = next(e["revision"] for e in events if e["type"] == "SOI_COMMITTED")
        start = next(e["revision"] for e in events if e["type"] == "REVIEW_STARTED")
        self.assertLess(commit, start)

    def test_uncommitted_inventory_cannot_expose_candidate(self):
        self.clarified()
        raw = self.w._reg("reviewer", "soi", {"workspace": self.w.session}, source=self.w.source)
        self.denied("INVENTORY_NOT_COMMITTED", self.w.reconciliation_inputs, raw)

    def test_shared_session_is_rejected(self):
        self.clarified()
        producer = SubprocessFixture("reviewer", "formal-context", self.inventory_output())
        self.denied("SHARED_PRODUCER_CONTEXT", self.w.commit_inventory, producer)

    def test_producer_exact_unicode_roundtrip(self):
        expected = {"statement": "Créer une tâche — priorité élevée."}
        producer = SubprocessFixture("formalizer", "unicode-context", expected)
        request = {"role": "formalizer", "instructions": "Preserve exact text", "session": "unicode-context",
                   "source": {"text": "Créer une tâche — priorité élevée."}, "evidence": [], "output_schema": "WorkspaceAnalysis-1"}
        self.assertEqual(producer.produce(request), expected)

    def test_omission_detected_cannot_seal_then_corrected(self):
        self.w.ingest("public-human", SOURCE)
        # Omit listing from the lineage from its first draft, while preserving
        # its product question. This is an omission, not an explicit retirement.
        def omitted():
            output = self.draft()
            output["obligations"] = output["obligations"][:2]
            output["lineage"] = [r for r in output["lineage"] if r["current"] != ["TASK.LIST.IMPORTANT"]]
            for issue in output["issues"]:
                if issue["affects"] == ["TASK.LIST.IMPORTANT"]:
                    issue["affects"] = []
            return self.submit(output)
        omitted()
        self.w.answer("public-human", self.w.ask("PRIORITY.DEFAULT"), "NORMAL")
        omitted()
        self.w.answer("public-human", self.w.ask("IMPORTANT.MEANING"), "HIGH")
        frc = omitted()
        coverage = self.w.reconcile(review(self.w))
        rows = self.c.artifact(coverage)["content"]["rows"]
        self.assertIn("SOURCE_OBLIGATION_MISSING", [r["status"] for r in rows])
        self.denied("MISSING_EVIDENCE", self.w.approve, "public-human", frc)
        self.denied("INVALID_TRANSITION", self.w.seal, frc)
        question = self.w.route_disagreement(coverage)
        self.assertIn("List all tasks", self.c.artifact(question)["content"]["text"])
        self.w.answer("public-human", question, "Yes, include the important-task listing.")
        formalize(self.w)
        self.seal_current()
        self.assertTrue(self.c.state(self.w.candidate)["sealed"])

    def test_invention_with_plausible_source_quote_denied(self):
        self.clarified()
        output = self.draft()
        output["obligations"].append(obligation("TASK.SORT.TITLE", "List important tasks.", "Sort by title alphabetically.",
                                                "filter_order", {"ordering": "alphabetical"}))
        # Even a real source identity plus real quote cannot supply invented meaning.
        output["authority"]["TASK.SORT.TITLE"] = output["authority"]["TASK.LIST.IMPORTANT"]
        frc = self.submit(output)
        coverage = self.w.reconcile(review(self.w))
        self.assertIn("FRC_OBLIGATION_LACKING_AUTHORITY", [r["status"] for r in self.c.artifact(coverage)["content"]["rows"]])
        self.denied("MISSING_EVIDENCE", self.w.approve, "public-human", frc)
        self.denied("INVALID_TRANSITION", self.w.seal, frc)

    def test_material_divergence_returns_product_question_to_human(self):
        self.clarified()
        output = self.inventory_output()
        output["interpretations"]["TASK.LIST.IMPORTANT"]["statement"] = "List one highest-priority task."
        output["inventory"]["items"][2]["meaning"] = "Should the list show one highest-priority task or all matching tasks?"
        coverage = self.w.reconcile(self.commit(output))
        self.assertIn("MATERIALLY_DIVERGENT", [r["status"] for r in self.c.artifact(coverage)["content"]["rows"]])
        q = self.w.route_disagreement(coverage)
        self.assertIn("one highest-priority task or all", self.c.artifact(q)["content"]["text"])
        self.w.answer("public-human", q, "All matching tasks.")
        formalize(self.w)
        self.seal_current()

    def test_unresolved_mapping_and_umbrella_are_insufficient(self):
        self.clarified()
        output = self.inventory_output()
        output["interpretations"].pop("TASK.CREATE.TITLE")
        coverage = self.w.reconcile(self.commit(output))
        self.assertIn("UNRESOLVED_MAPPING", [r["status"] for r in self.c.artifact(coverage)["content"]["rows"]])
        formalize(self.w)
        output = self.inventory_output()
        output["inventory"]["items"] = [{"id": "ALL", "spans": [{"start": 0, "end": len(SOURCE), "quote": SOURCE}],
                                          "meaning": "Everything covered", "category": "BEHAVIOR", "material": True, "dependencies": []}]
        coverage = self.w.reconcile(self.commit(output))
        self.assertEqual(self.c.artifact(coverage)["content"]["outcome"], "DISPUTED")

    def test_inventory_span_and_text_accountability_checks(self):
        self.clarified()
        output = self.inventory_output()
        output["inventory"]["items"][0]["spans"][0]["quote"] = "invented quote"
        self.denied("SOI_SPAN_MISMATCH", self.commit, output)
        output = self.inventory_output()
        output["inventory"]["items"].pop()
        self.denied("SOI_TEXT_UNACCOUNTED", self.commit, output)

    def test_unsupported_scope_halts(self):
        self.clarified()
        output = self.draft()
        output["unsupported"] = ["Unqualified structural temporal scope"]
        frc = self.submit(output)
        coverage = self.w.reconcile(review(self.w))
        self.assertIn("UNSUPPORTED_SCOPE", [r["status"] for r in self.c.artifact(coverage)["content"]["rows"]])
        self.denied("MISSING_EVIDENCE", self.w.approve, "public-human", frc)

    def test_invented_domain_or_freedom_is_divergent(self):
        self.clarified()
        output = self.draft()
        output["domains"] = {"titles": "ASCII only"}
        output["unspecified"] = ["Task creation may lose unrelated tasks."]
        frc = self.submit(output)
        coverage = self.w.reconcile(review(self.w))
        self.assertIn("MATERIALLY_DIVERGENT", [r["status"] for r in self.c.artifact(coverage)["content"]["rows"]])
        self.denied("MISSING_EVIDENCE", self.w.approve, "public-human", frc)

    def test_nonbehavioral_inventory_cannot_authorize_an_frc_obligation(self):
        self.clarified()
        output = self.inventory_output()
        output["inventory"]["items"][0].update(category="NONBEHAVIORAL", material=False)
        coverage = self.w.reconcile(self.commit(output))
        self.assertIn("FRC_OBLIGATION_LACKING_AUTHORITY", [r["status"] for r in self.c.artifact(coverage)["content"]["rows"]])

    def test_exact_version_approval_cannot_approve_next_frc(self):
        self.clarified()
        frc, _, approval, seal = self.seal_current()
        new = formalize(self.w)
        self.assertNotEqual(frc, new)
        self.assertEqual(self.c.artifact(approval)["dependencies"]["frc"], frc)
        self.denied("WRONG_CANDIDATE_VERSION", self.w.approve, "public-human", frc)
        self.denied("INVALID_TRANSITION", self.w.seal, new)
        self.assertEqual(self.c.artifact(seal)["type"], "frc_seal")

    def test_clarification_replacement_invalidates_old_seal(self):
        initial, frc = self.clarified()
        _, _, approval, seal = self.seal_current()
        answers = [(aid, self.c.artifact(aid)) for aid in self.c.closure(self.w.source, authoritative=True)
                   if self.c.artifact(aid)["type"] == "answer"]
        answer = next(aid for aid, a in answers if a["content"]["question_id"] == "PRIORITY.DEFAULT")
        old_source = self.w.source
        self.w.revise_answer("public-human", answer, "LOW")
        self.assertNotEqual(old_source, self.w.source)
        for aid in (frc, approval, seal, answer):
            self.assertFalse(self.c.state(aid)["eligible_for_new_use"])
        new = formalize(self.w)
        self.assertNotEqual(new, frc)
        self.denied("INVALID_TRANSITION", self.w.seal, new)
        _, _, _, new_seal = self.seal_current()
        self.assertNotEqual(new_seal, seal)
        self.assertTrue(self.c.state(new)["sealed"])

    def test_policy_exact_provenance_and_supersession(self):
        policy = self.w.define_policy("Collection ordering is unconstrained.", scope="*")
        self.w.adopt_policy("public-human", policy, rationale="Human-selected synthetic policy")
        self.clarified(policy)
        frc, _, approval, seal = self.seal_current()
        self.assertEqual(self.c.artifact(frc)["content"]["authority"]["TASK.LIST.ORDER"], [policy])
        new = self.w.define_policy("Collection ordering is newest first.", scope="*")
        self.w.adopt_policy("public-human", new, rationale="Human policy revision", replaces=policy)
        for aid in (frc, approval, seal):
            self.assertFalse(self.c.state(aid)["eligible_for_new_use"])

    def test_unadopted_or_inapplicable_policy_rejects(self):
        policy = self.w.define_policy("No policy default", scope="*")
        self.denied("MISSING_EVIDENCE", self.w.ingest, "public-human", SOURCE, [policy])
        other = self.w.define_policy("Other feature only", scope="other-session")
        self.w.adopt_policy("public-human", other, rationale="Synthetic other scope")
        self.denied("POLICY_NOT_APPLICABLE", self.w.ingest, "public-human", SOURCE, [other])

    def test_feature_requirement_overrides_waivable_policy(self):
        self.policy_feature_case(waivable=True, mode="FEATURE_EXCEPTION", seals=True)

    def test_unresolved_nonwaivable_policy_conflict_blocks(self):
        self.policy_feature_case(waivable=False, mode="FEATURE_EXCEPTION", seals=False)

    def policy_feature_case(self, *, waivable, mode, seals):
        policy = self.w.define_policy("Collection ordering is unconstrained.", scope="*", waivable=waivable)
        self.w.adopt_policy("public-human", policy, rationale="Synthetic policy adoption")
        text = "Show tasks newest first."
        self.w.ingest("public-human", text, [policy])
        source, evidence = self.w.inputs()
        human = next(e["identity"] for e in evidence if e["provenance"] == "human_statement")
        row = obligation("TASK.ORDER", text, "Show tasks newest first.", "filter_order", {"ordering": "newest first"})
        output = {"obligations": [row], "authority": {row["id"]: [human]},
                  "policy_applications": [{"policy": policy, "mode": mode, "feature_decision": "newest first"}]}
        frc = self.submit(output)
        # Independent inventory authored from this source/policy, without FRC input.
        import hashlib
        from lykoi_controller import canonical
        record = {"id": source["identity"], "text": text, "classification": "SYNTHETIC", "sha256": hashlib.sha256(text.encode()).hexdigest()}
        inventory = {"version": "SourceObligationInventory-0.1", "source_commitment": hashlib.sha256(canonical({"revision": 1, "record": record})).hexdigest(),
                     "extractor": "review-context", "context_class": SubprocessFixture.isolation,
                     "items": [{"id": "TASK.ORDER", "spans": [{"start": 0, "end": len(text), "quote": text}],
                                "meaning": "Show tasks newest first.", "category": "BEHAVIOR", "material": True, "dependencies": []}],
                     "questions": [], "limitations": ["Synthetic"]}
        soi = self.commit({"inventory": inventory, "authority": {"TASK.ORDER": [human]},
                           "interpretations": {"TASK.ORDER": {"statement": "Show tasks newest first.", "relation": {"kind": "filter_order", "parameters": {"ordering": "newest first"}}}}})
        self.w.reconcile(soi)
        if seals:
            self.w.approve("public-human", frc)
            self.w.seal(frc)
            self.assertIn("newest first", self.w.approval_summary(frc)["commitments"][0])
        else:
            coverage = self.w._records("coverage")[-1][1]["content"]
            self.assertIn("POLICY_CONFLICT", [r["status"] for r in coverage["rows"]])
            self.denied("MISSING_EVIDENCE", self.w.approve, "public-human", frc)
            self.denied("INVALID_TRANSITION", self.w.seal, frc)

    def test_correlated_agreement_can_be_wrong(self):
        self.clarified()
        output = self.draft()
        output["obligations"].pop()
        output["lineage"].append({"change": "retire", "previous": ["TASK.LIST.IMPORTANT"], "current": [], "reason": "Incorrect producer judgment"})
        frc = self.submit(output)
        inventory = self.inventory_output()
        lost = inventory["inventory"]["items"].pop()
        # Both producers incorrectly classify listing as nonbehavioral/context.
        lost.update(category="NONBEHAVIORAL", material=False, meaning="Context only (incorrect)")
        inventory["inventory"]["items"].append(lost)
        self.w.reconcile(self.commit(inventory))
        self.w.approve("public-human", frc)
        self.w.seal(frc)
        expected = {"TASK.CREATE.TITLE", "TASK.CREATE.PRIORITY", "TASK.LIST.IMPORTANT"}
        actual = {o["id"] for o in self.c.artifact(frc)["content"]["contract"]["obligations"]}
        self.assertNotEqual(expected, actual)
        self.assertTrue(self.c.state(frc)["sealed"])

    def test_finite_review_budget_survives_restart(self):
        self.clarified()
        for _ in range(2):
            output = self.inventory_output()
            output["inventory"]["questions"] = ["Persisting disagreement"]
            self.w.reconcile(self.commit(output))
            formalize(self.w)
        self.c.close()
        self.c = Controller(self.path, PRINCIPALS)
        self.w = Workspace(self.c, "public", "test-session", CREDENTIALS)
        self.assertEqual(self.w.status()["halt"], "FINITE_REVIEW_EXHAUSTED")
        self.denied("FINITE_REVIEW_EXHAUSTED", review, self.w)

    def test_sealed_workspace_actual_process_restart(self):
        self.clarified()
        self.seal_current()
        before = self.w.status()
        self.c.close()
        script = ("import sys,json;sys.path[:0]=[sys.argv[1],sys.argv[2]];"
                  "from lykoi_controller import Controller;from lykoi_workspace import Workspace;"
                  "from lykoi_workspace.example import PRINCIPALS,CREDENTIALS;"
                  "c=Controller(sys.argv[3],PRINCIPALS);w=Workspace(c,'public','test-session',CREDENTIALS);"
                  "print(json.dumps(w.status()));c.close()")
        root = Path(__file__).resolve().parents[1]
        process = subprocess.run([sys.executable, "-c", script, str(root / "src"), str(root), str(self.path)],
                                 capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(process.stdout), before)
        self.c = Controller(self.path, PRINCIPALS)


if __name__ == "__main__":
    unittest.main()
