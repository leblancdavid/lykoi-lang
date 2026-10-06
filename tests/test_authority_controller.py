"""Public synthetic authority challenges; no benchmark/protected inputs."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

from lykoi_controller import Controller, Failure, canonical, identity
from lykoi_controller.controller import parse_json


PRINCIPALS = {
    "human": {"credential": "synthetic-owner", "roles": ["owner"], "projects": ["public"]},
    "wizard": {"credential": "synthetic-wizard", "roles": ["formalizer"], "projects": ["public"]},
    "review": {"credential": "synthetic-review", "roles": ["reviewer"], "projects": ["public"]},
    "service": {"credential": "synthetic-controller", "roles": ["controller"], "projects": ["public"]},
    "checker": {"credential": "synthetic-checker", "roles": ["mechanical"], "projects": ["public"]},
    "writer": {"credential": "synthetic-author", "roles": ["author"], "projects": ["public"]},
    "external": {"credential": "synthetic-verifier", "roles": ["verifier"], "projects": ["public"]},
    "verification-owner": {"credential": "synthetic-verification-owner", "roles": ["verification_authority"], "projects": ["public"]},
    "dual": {"credential": "synthetic-dual", "roles": ["author", "verifier"], "projects": ["public"]},
}


class Case:
    """Reusable executable demonstration, with synthetic semantic receipts."""

    def __init__(self, controller):
        self.c = controller

    def call(self, actor, command, **args):
        return self.c.execute(PRINCIPALS[actor]["credential"], "public", command,
                              expected_revision=self.c.revision, **args)

    def reg(self, actor, kind, content, **deps):
        return self.call(actor, "register", kind=kind, content=content, dependencies=deps)

    def validate(self, aid, access=None):
        self.call("checker", "validate", subject=aid, check="synthetic-producer-receipt", access=access)

    def review(self, aid, outcome="ACCEPTED"):
        self.call("review", "review", subject=aid, outcome=outcome,
                  rationale="Synthetic public premise; not semantic qualification",
                  access=list(self.c.artifact(aid)["dependencies"].values()))

    def policy(self, rule="Stable list order", waivable=True):
        aid = self.reg("wizard", "policy", {"rule": rule, "scope": "task list", "waivable": waivable})
        self.validate(aid)
        self.review(aid)
        self.call("human", "adopt", subject=aid)
        return aid

    def source(self, text=b"Tasks have optional priority.", policy=None):
        message = self.reg("human", "message", text)
        self.call("human", "adopt", subject=message)
        deps = {"message": message}
        if policy:
            deps["policy:list-order"] = policy
        root = self.reg("wizard", "source", {"provenance": "human-authorized-requirement", "revision": 1}, **deps)
        self.call("human", "adopt", subject=root)
        return root

    def candidate(self, source, revision=1, applications=None):
        frc = self.reg("wizard", "frc", {"obligations": ["priority"], "revision": revision,
                                        "policy_applications": applications or []}, source=source)
        soi = self.reg("review", "soi", {"items": ["priority"], "synthetic_blind_receipt": True}, source=source)
        self.validate(soi, [source])
        self.validate(frc)
        self.call("service", "begin_review", subject=frc, soi=soi)
        return frc, soi

    def seal(self, frc, soi, structural_outcome="ACCEPTED"):
        coverage = self.reg("review", "coverage", {"mappings": [["priority", "priority"]]}, frc=frc, soi=soi)
        self.validate(coverage)
        self.review(coverage)
        structural = self.reg("wizard", "structural", {"channel": "priority"}, frc=frc)
        self.validate(structural)
        self.review(structural, structural_outcome)
        approval = self.call("human", "approve", subject=frc, coverage=coverage, structural=structural)
        seal = self.call("service", "seal_frc", subject=frc)
        return {"frc": frc, "soi": soi, "coverage": coverage, "structural": structural,
                "approval": approval, "seal": seal}

    def downstream(self, base):
        seal, structural = base["seal"], base["structural"]
        freeze = self.reg("service", "freeze", {"controller": "authority-1", "tools": "synthetic-1",
                                               "language": "unchanged", "V1": "unchanged"})
        self.validate(freeze)
        receipt = self.reg("review", "structural_receipt", {"outcome": "SUPPORTED"}, seal=seal, structural=structural)
        self.validate(receipt)
        self.review(receipt)
        bdi = self.reg("checker", "bdi", {"outcome": "SUPPORTED", "synthetic": True},
                       seal=seal, structural_receipt=receipt, freeze=freeze)
        self.validate(bdi)
        adequacy = self.reg("checker", "adequacy", {"outcome": "ADEQUATE", "synthetic": True},
                            seal=seal, bdi=bdi, structural_receipt=receipt, freeze=freeze)
        self.validate(adequacy)
        self.review(adequacy)
        v1 = self.reg("wizard", "v1", {"outcome": "FAITHFUL_COMPLETE", "synthetic": True}, seal=seal, adequacy=adequacy)
        self.validate(v1)
        self.review(v1)
        plan = self.reg("external", "plan", {"outcome": "READY", "cases": ["missing priority -> NORMAL"], "synthetic": True},
                        seal=seal, freeze=freeze)
        self.validate(plan)
        self.review(plan)
        plan_seal = self.call("verification-owner", "seal_plan", subject=plan)
        bundle = self.reg("wizard", "bundle", {"interface": "public synthetic", "baseline": "none"},
                          v1=v1, adequacy=adequacy, plan_seal=plan_seal, freeze=freeze)
        grant = self.call("service", "grant", subject=bundle)
        return dict(base, structural_receipt=receipt, bdi=bdi, adequacy=adequacy, v1=v1,
                    plan=plan, plan_seal=plan_seal, bundle=bundle, grant=grant, freeze=freeze)

    def full(self, clarification=True, policy=True):
        p = self.policy() if policy else None
        source = self.source(policy=p)
        apps = [{"policy": p, "mode": "DEFAULT"}] if p else []
        initial, inventory = self.candidate(source, applications=apps)
        if clarification:
            question = self.reg("wizard", "question", {"id": "Q1", "question": "What happens when priority is missing?"}, source=source)
            self.call("wizard", "clarify", subject=initial, question=question)
            answer = self.reg("human", "answer", b"Missing priority defaults to NORMAL.", question=question, source=source)
            revised = self.call("human", "answer", subject=answer)
            frc, soi = self.candidate(revised, 2, apps)
        else:
            frc, soi, revised = initial, inventory, source
        return dict(self.downstream(self.seal(frc, soi)), source=revised, old_source=source,
                    old_frc=initial, policy=p)


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "controller.sqlite"
        self.c = Controller(self.path, PRINCIPALS)
        self.case = Case(self.c)

    def tearDown(self):
        self.c.close()
        self.tmp.cleanup()

    def assertDenied(self, code, actor, command, **args):
        with self.assertRaises(Failure) as caught:
            self.case.call(actor, command, **args)
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(self.c.events()[-1]["reason"]["code"], code)

    def test_positive_synthetic_clarification_policy_chain(self):
        b = self.case.full()
        self.assertTrue(self.c.applicable(b["grant"], b["bundle"], b["freeze"])["applicable"])
        self.assertEqual(self.c.state(b["frc"])["lifecycle"], "SEALED")
        self.assertEqual(self.c.state(b["old_frc"])["lifecycle"], "CLARIFICATION")
        self.assertFalse(self.c.state(b["old_frc"])["eligible_for_new_use"])
        self.assertTrue(self.c.state(b["bundle"])["implementation_authorized"])
        revision = self.c.revision
        audit = self.c.audit(b["bundle"])
        self.assertIn(b["source"], audit["sources"])
        self.assertIn(b["old_source"], audit["sources"])
        self.assertEqual(audit["grants"], [b["grant"]])
        self.assertTrue(any(e["actor"] == "human" and e["type"] == "APPROVAL_GRANTED" for e in audit["authority_evidence"]))
        # Change authoritative source; old grant is retained but new use denies.
        new_source = self.case.source(b"Tasks have optional priority; default HIGH.", b["policy"])
        self.case.call("human", "supersede", subject=b["source"], replacement=new_source)
        self.assertFalse(self.c.applicable(b["grant"], b["bundle"], b["freeze"])["applicable"])
        self.assertGreater(self.c.revision, revision)
        self.assertEqual(self.c.artifact(b["grant"])["type"], "grant")

    def test_false_ai_assertions_have_no_authority(self):
        source = self.case.source()
        for assertion in ({"approved": True}, {"coverage_complete": True}, {"status": "APPROVED"},
                          {"outcome": "IMPLEMENTATION_ADEQUATE"}, {"verified": True}, {"human_confirmed": True}):
            with self.subTest(assertion=assertion):
                candidate = self.case.reg("wizard", "frc", assertion, source=source)
                state = self.c.state(candidate)
                for key in ("human_authorized", "sealed", "implementation_authorized", "mechanically_validated", "reviewed"):
                    self.assertFalse(state[key])
                self.assertDenied("INVALID_TRANSITION", "service", "seal_frc", subject=candidate)
                self.assertDenied("TYPE_MISMATCH", "service", "grant", subject=candidate)

    def test_role_spoof_self_escalation_and_scope(self):
        source = self.case.source()
        candidate = self.case.reg("wizard", "frc", {}, source=source)
        self.assertDenied("ROLE_DENIED", "wizard", "adopt", subject=source)
        self.assertDenied("ROLE_DENIED", "review", "approve", subject=candidate, coverage=candidate, structural=candidate)
        self.assertDenied("ROLE_DENIED", "writer", "bind_verification", subject=candidate)
        self.assertDenied("ROLE_DENIED", "writer", "grant", subject=candidate)
        with self.assertRaises(Failure) as caught:
            self.c.execute("pretend-human", "public", "adopt", expected_revision=self.c.revision, subject=source)
        self.assertEqual(caught.exception.code, "UNAUTHENTICATED")
        with self.assertRaises(Failure) as caught:
            self.c.execute("synthetic-owner", "different-project", "adopt", expected_revision=self.c.revision, subject=source)
        self.assertEqual(caught.exception.code, "SCOPE_DENIED")
        self.assertDenied("RESERVED_OR_UNKNOWN_TYPE", "wizard", "register", kind="frc_seal", content={})

    def test_wrong_human_version_and_artifact_substitution(self):
        b = self.case.full(clarification=False)
        frc2 = self.case.reg("wizard", "frc", {"display_path": "same.json", "approved": True}, source=b["source"])
        self.assertNotEqual(frc2, b["frc"])
        self.assertDenied("INVALID_TRANSITION", "service", "seal_frc", subject=frc2)
        changed = self.case.reg("wizard", "bundle", {"interface": "different authoritative content", "baseline": "none"},
                                **self.c.artifact(b["bundle"])["dependencies"])
        result = self.c.applicable(b["grant"], changed, b["freeze"])
        self.assertFalse(result["applicable"])
        self.assertEqual(result["failure"]["code"], "GRANT_IDENTITY_MISMATCH")
        self.assertFalse(self.c.applicable(b["grant"], b["bundle"], b["freeze"], "release")["applicable"])
        self.assertDenied("GRANT_IDENTITY_MISMATCH", "writer", "reserve", subject=changed, grant=b["grant"], freeze=b["freeze"])

    def test_unresolved_clarification_and_wrong_answer(self):
        source = self.case.source()
        frc, soi = self.case.candidate(source)
        question = self.case.reg("wizard", "question", {"id": "Q"}, source=source)
        self.case.call("wizard", "clarify", subject=frc, question=question)
        self.assertDenied("INVALID_TRANSITION", "service", "seal_frc", subject=frc)
        a = self.case.reg("human", "answer", b"NORMAL", question=question, source=source)
        revised = self.case.call("human", "answer", subject=a)
        self.assertFalse(self.c.state(frc)["eligible_for_new_use"])
        frc2, soi2 = self.case.candidate(revised)
        # Same stable IDs do not let old inventory cross the new root.
        self.assertDenied("STALE_DEPENDENCY", "service", "begin_review", subject=frc2, soi=soi)
        deps = self.c.artifact(frc2)["dependencies"]
        self.assertEqual(deps["source"], revised)
        self.assertNotEqual(revised, source)

    def test_clarification_mismatch_across_sealed_graph(self):
        b = self.case.full()
        other_source = self.case.source(b"Missing priority defaults to HIGH.", b["policy"])
        other_frc, other_soi = self.case.candidate(other_source, applications=[{"policy": b["policy"], "mode": "DEFAULT"}])
        other = self.case.seal(other_frc, other_soi)
        self.assertDenied("DEPENDENCY_MISMATCH", "wizard", "register", kind="v1", content={"outcome": "FAITHFUL_COMPLETE"},
                          dependencies={"seal": other["seal"], "adequacy": b["adequacy"]})

    def test_disputed_coverage_and_unsupported_what_only(self):
        source = self.case.source()
        frc, soi = self.case.candidate(source)
        coverage = self.case.reg("review", "coverage", {}, frc=frc, soi=soi)
        structural = self.case.reg("wizard", "structural", {}, frc=frc)
        self.case.validate(coverage)
        self.case.review(coverage, "DISPUTED")
        self.case.validate(structural)
        self.case.review(structural)
        self.assertDenied("MISSING_EVIDENCE", "human", "approve", subject=frc, coverage=coverage, structural=structural)
        # Unsupported structural scope can seal WHAT, but cannot authorize HOW.
        source2 = self.case.source(b"Synthetic unsupported timing requirement.")
        frc2, soi2 = self.case.candidate(source2)
        base = self.case.seal(frc2, soi2, "UNSUPPORTED")
        self.assertTrue(self.c.state(frc2)["sealed"])
        with self.assertRaises(Failure):
            self.case.downstream(base)
        self.assertEqual(self.c.events()[-1]["type"], "GRANT_DENIED")

    def test_post_seal_dispute_denies_grant_and_dispatch(self):
        b = self.case.full(clarification=False)
        self.case.review(b["v1"], "DISPUTED")
        self.assertFalse(self.c.applicable(b["grant"], b["bundle"], b["freeze"])["applicable"])
        self.assertFalse(self.c.state(b["bundle"])["implementation_authorized"])
        self.assertDenied("GRANT_ALREADY_ISSUED", "service", "grant", subject=b["bundle"])

    def test_policy_adoption_and_precedence(self):
        policy = self.case.reg("wizard", "policy", {"rule": "default NORMAL", "waivable": True})
        self.assertDenied("MISSING_EVIDENCE", "human", "adopt", subject=policy)
        self.case.validate(policy)
        self.case.review(policy)
        self.case.review(policy, "DISPUTED")
        self.assertDenied("POLICY_DISPUTED", "human", "adopt", subject=policy)
        policy = self.case.policy("default NORMAL")
        source = self.case.source(b"Explicit feature default HIGH.", policy)
        for mode, feature, expected in (("DEFAULT", "HIGH", "POLICY_CANNOT_OVERRIDE_FEATURE"),
                                        ("CONFLICT", "HIGH", "POLICY_CONFLICT")):
            frc, soi = self.case.candidate(source, applications=[{"policy": policy, "mode": mode, "feature_decision": feature}])
            with self.assertRaises(Failure) as caught:
                self.case.seal(frc, soi)
            self.assertEqual(caught.exception.code, expected)
        frc, soi = self.case.candidate(source, applications=[{"policy": policy, "mode": "FEATURE_EXCEPTION", "feature_decision": "HIGH"}])
        self.case.seal(frc, soi)
        self.assertTrue(self.c.state(frc)["sealed"])

    def test_invalidation_all_authoritative_dependency_classes(self):
        # Every stage replacement conservatively invalidates descendant authority.
        for kind in ("source", "policy", "frc", "structural", "adequacy", "v1", "plan"):
            with self.subTest(kind=kind):
                with tempfile.TemporaryDirectory() as tmp:
                    c = Controller(Path(tmp) / "state.sqlite", PRINCIPALS)
                    case = Case(c)
                    b = case.full(clarification=False)
                    old = b[kind]
                    a = c.artifact(old)
                    actor = {"source": "wizard", "policy": "wizard", "frc": "wizard", "structural": "wizard",
                             "adequacy": "checker", "v1": "wizard", "plan": "external"}[kind]
                    content = dict(a["content"], authoritative_revision=2)
                    new = case.reg(actor, kind, content, **a["dependencies"])
                    if kind == "source":
                        case.call("human", "adopt", subject=new)
                    elif kind == "policy":
                        case.validate(new)
                        case.review(new)
                        case.call("human", "adopt", subject=new)
                    case.call("human", "supersede", subject=old, replacement=new)
                    result = c.applicable(b["grant"], b["bundle"], b["freeze"])
                    self.assertEqual(result["failure"]["code"], "STALE_DEPENDENCY")
                    self.assertFalse(c.state(b["bundle"])["eligible_for_new_use"])
                    self.assertIn(b["grant"], c.audit(b["bundle"])["grants"])
                    c.close()

    def test_clarification_answer_replacement_invalidates_descendants(self):
        b = self.case.full()
        answer = self.c.artifact(b["source"])["dependencies"]["answer"]
        # Explicit revocation of the answer invalidates its new-root descendants.
        self.case.call("human", "invalidate", subject=answer, reason="Human retracts NORMAL answer")
        self.assertFalse(self.c.applicable(b["grant"], b["bundle"], b["freeze"])["applicable"])

    def test_revocation_after_reservation_prevents_completion(self):
        b = self.case.full(clarification=False)
        reservation = self.case.call("writer", "reserve", subject=b["bundle"], grant=b["grant"], freeze=b["freeze"])
        model = self.case.reg("writer", "model", b"synthetic model", bundle=b["bundle"], grant=b["grant"])
        self.case.call("human", "invalidate", subject=b["source"], reason="withdrawn")
        self.assertDenied("STALE_DEPENDENCY", "writer", "complete", subject=reservation, output=model)

    def test_durable_reservation_crash_replay_and_completion(self):
        b = self.case.full(clarification=False)
        reservation = self.case.call("writer", "reserve", subject=b["bundle"], grant=b["grant"], freeze=b["freeze"])
        self.c.close()
        self.c = Controller(self.path, PRINCIPALS)
        self.case = Case(self.c)
        self.assertIn(reservation, self.c.audit(b["bundle"])["incomplete_reservations"])
        self.assertDenied("DISPATCH_REPLAY", "writer", "reserve", subject=b["bundle"], grant=b["grant"], freeze=b["freeze"])
        model = self.case.reg("writer", "model", b"synthetic model", bundle=b["bundle"], grant=b["grant"])
        self.case.call("writer", "complete", subject=reservation, output=model)
        self.assertDenied("DISPATCH_REPLAY", "writer", "complete", subject=reservation, output=model)

    def test_grant_reissue_cannot_bypass_single_use_dispatch(self):
        b = self.case.full(clarification=False)
        self.case.call("writer", "reserve", subject=b["bundle"], grant=b["grant"], freeze=b["freeze"])
        self.assertDenied("GRANT_ALREADY_ISSUED", "service", "grant", subject=b["bundle"])
        self.assertEqual(self.c.audit(b["bundle"])["grants"], [b["grant"]])

    def test_external_verification_and_author_self_verification(self):
        b = self.case.full(clarification=False)
        reservation = self.case.call("dual", "reserve", subject=b["bundle"], grant=b["grant"], freeze=b["freeze"])
        model = self.case.reg("dual", "model", b"synthetic model", bundle=b["bundle"], grant=b["grant"])
        self.case.call("dual", "complete", subject=reservation, output=model)
        target = self.case.reg("checker", "target", b"synthetic generated bytes", model=model, freeze=b["freeze"])
        self.case.validate(target)
        result = self.case.reg("external", "verification", {"outcome": "SCOPED_PASS", "synthetic": True},
                               target=target, plan_seal=b["plan_seal"], freeze=b["freeze"])
        self.case.validate(result)
        self.assertDenied("SELF_VERIFICATION", "dual", "bind_verification", subject=result)
        self.case.call("external", "bind_verification", subject=result)
        self.assertEqual(self.c.events()[-1]["type"], "VERIFICATION_BOUND")

    def test_revision_race_rollback_and_no_partial_authority(self):
        rev = self.c.revision
        other = Controller(self.path, PRINCIPALS)
        self.case.source()
        with self.assertRaises(Failure) as caught:
            other.execute("synthetic-owner", "public", "register", expected_revision=rev,
                          kind="message", content="racing message")
        self.assertEqual(caught.exception.code, "REVISION_RACE")
        other.close()
        self.assertFalse(any(a[0].startswith("message:") and "racing message" in a[1]
                             for a in self.c.db.execute("SELECT * FROM artifacts")))

    def test_append_only_store_and_journal(self):
        self.case.full(clarification=False)
        for sql in ("UPDATE journal SET event='{}'", "DELETE FROM journal", "DELETE FROM artifacts",
                    "UPDATE artifacts SET envelope='{}'", "UPDATE config SET value='{}'"):
            with self.assertRaises(sqlite3.IntegrityError):
                self.c.db.execute(sql)
        self.c.check_integrity()

    def test_registry_cannot_be_spoofed_on_restart(self):
        changed = copy.deepcopy(PRINCIPALS)
        changed["wizard"]["roles"].append("owner")
        with self.assertRaises(Failure) as caught:
            Controller(self.path, changed)
        self.assertEqual(caught.exception.code, "REGISTRY_MISMATCH")

    def test_persistence_actual_process_restart(self):
        b = self.case.full()
        before = self.c.audit(b["bundle"])
        self.c.close()
        script = (
            "import json,sys;sys.path[:0]=[sys.argv[1],sys.argv[2]];"
            "from lykoi_controller import Controller;"
            "from test_authority_controller import PRINCIPALS;"
            "c=Controller(sys.argv[3],PRINCIPALS);"
            "print(json.dumps(c.audit(sys.argv[4]),sort_keys=True));c.close()"
        )
        root = Path(__file__).resolve().parents[1]
        process = subprocess.run([sys.executable, "-c", script, str(root / "src"), str(root / "tests"),
                                  str(self.path), b["bundle"]], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(process.stdout), before)
        self.c = Controller(self.path, PRINCIPALS)
        self.assertTrue(self.c.applicable(b["grant"], b["bundle"], b["freeze"])["applicable"])

    def test_same_artifacts_events_reproduce_identity_and_decisions(self):
        b = self.case.full()
        with tempfile.TemporaryDirectory() as tmp:
            other = Controller(Path(tmp) / "state.sqlite", PRINCIPALS)
            b2 = Case(other).full()
            self.assertEqual(b, b2)
            self.assertEqual(self.c.events(), other.events())
            self.assertEqual(self.c.applicable(b["grant"], b["bundle"], b["freeze"]),
                             other.applicable(b2["grant"], b2["bundle"], b2["freeze"]))
            other.close()

    def test_source_recovery_provenance_is_not_implicit_human_authority(self):
        message = self.case.reg("human", "message", b"public observed implementation behavior")
        root = self.case.reg("wizard", "source", {"provenance": "observed-implementation-behavior"}, message=message)
        self.assertFalse(self.c.state(root)["human_authorized"])
        self.assertDenied("MISSING_EVIDENCE", "human", "adopt", subject=root)

    def test_unsupported_adequacy_and_missing_evidence_do_not_grant(self):
        b = self.case.full(clarification=False)
        deps = self.c.artifact(b["adequacy"])["dependencies"]
        unsupported = self.case.reg("checker", "adequacy", {"outcome": "OUTSIDE_SCOPE"}, **deps)
        self.case.validate(unsupported)
        self.case.review(unsupported)
        v1 = self.case.reg("wizard", "v1", {"outcome": "FAITHFUL_COMPLETE"}, seal=b["seal"], adequacy=unsupported)
        self.case.validate(v1)
        self.case.review(v1)
        bundle = self.case.reg("wizard", "bundle", {}, v1=v1, adequacy=unsupported, plan_seal=b["plan_seal"], freeze=b["freeze"])
        self.assertDenied("UNSUPPORTED_OUTCOME", "service", "grant", subject=bundle)
        unreviewed = self.case.reg("wizard", "v1", {"outcome": "FAITHFUL_COMPLETE", "approved": True}, seal=b["seal"], adequacy=b["adequacy"])
        bundle = self.case.reg("wizard", "bundle", {}, v1=unreviewed, adequacy=b["adequacy"], plan_seal=b["plan_seal"], freeze=b["freeze"])
        self.assertDenied("MISSING_EVIDENCE", "service", "grant", subject=bundle)

    def test_unsealed_plan_and_freeze_substitution_deny(self):
        b = self.case.full(clarification=False)
        plan = self.case.reg("external", "plan", {"outcome": "READY", "verified": True}, seal=b["seal"], freeze=b["freeze"])
        self.assertDenied("MISSING_EVIDENCE", "verification-owner", "seal_plan", subject=plan)
        self.assertDenied("ROLE_DENIED", "external", "seal_plan", subject=b["plan"])
        freeze = self.case.reg("service", "freeze", {"tools": "different version"})
        self.assertFalse(self.c.applicable(b["grant"], b["bundle"], freeze)["applicable"])
        self.assertDenied("DEPENDENCY_MISMATCH", "wizard", "register", kind="bundle", content={},
                          dependencies=dict(self.c.artifact(b["bundle"])["dependencies"], freeze=freeze))

    def test_rejected_and_revision_required_lifecycle(self):
        for outcome in ("REJECTED", "REVISION_REQUIRED"):
            source = self.case.source(outcome.encode())
            frc, soi = self.case.candidate(source)
            coverage = self.case.reg("review", "coverage", {}, frc=frc, soi=soi)
            self.case.validate(coverage)
            self.case.review(coverage, outcome)
            self.assertEqual(self.c.state(frc)["lifecycle"], outcome)
            self.assertDenied("INVALID_TRANSITION", "service", "seal_frc", subject=frc)

    def test_input_access_and_no_candidate_self_review(self):
        source = self.case.source()
        soi = self.case.reg("review", "soi", {}, source=source)
        self.assertDenied("BLIND_INPUT_VIOLATION", "checker", "validate", subject=soi,
                          check="synthetic-producer-receipt", access=[])
        self.assertFalse(self.c.state(soi)["mechanically_validated"])
        # Failed multi-event operations roll back every event and artifact.
        self.assertFalse(self.c._has(soi, "SOI_COMMITTED"))
        policy = self.case.reg("wizard", "policy", {"waivable": True})
        self.assertDenied("ROLE_DENIED", "wizard", "review", subject=policy,
                          outcome="ACCEPTED", rationale="self", access=[])

    def test_same_display_path_and_immutable_returned_content(self):
        source = self.case.source()
        first = self.case.reg("wizard", "frc", {"path": "contract.json", "behavior": "NORMAL"}, source=source)
        second = self.case.reg("wizard", "frc", {"path": "contract.json", "behavior": "HIGH"}, source=source)
        self.assertNotEqual(first, second)
        returned = self.c.artifact(first)
        returned["content"]["behavior"] = "HIGH"
        self.assertEqual(self.c.artifact(first)["content"]["behavior"], "NORMAL")
        self.assertDenied("INVALID_TRANSITION", "service", "seal_frc", subject=second)

    def test_conflicting_answer_needs_explicit_resolution(self):
        source = self.case.source()
        frc, soi = self.case.candidate(source)
        question = self.case.reg("wizard", "question", {"id": "Q"}, source=source)
        self.case.call("wizard", "clarify", subject=frc, question=question)
        a = self.case.reg("human", "answer", b"NORMAL", question=question, source=source)
        other = self.case.reg("human", "answer", b"HIGH", question=question, source=source)
        self.case.call("human", "answer", subject=a)
        self.assertDenied("CONFLICTING_ANSWER", "human", "answer", subject=other)

    def test_malformed_request_structured_and_audit_event_identity(self):
        self.assertDenied("MALFORMED_REQUEST", "wizard", "register", kind="frc")
        b = self.case.full(clarification=False)
        seal = self.c.artifact(b["seal"])
        events = {e["event_identity"] for e in self.c.events()}
        self.assertTrue(set(seal["content"]["authority_events"]).issubset(events))
        self.assertTrue(any(e["type"] == "APPROVAL_GRANTED" and e["event_identity"] in seal["content"]["authority_events"]
                            for e in self.c.events()))
        self.assertTrue(self.c.audit(b["bundle"])["journal_times"])

    def test_prior_clarifications_remain_normative_in_later_roots(self):
        b = self.case.full()
        first_answer = self.c.artifact(b["source"])["dependencies"]["answer"]
        candidate, inventory = self.case.candidate(b["source"], 3,
            [{"policy": b["policy"], "mode": "DEFAULT"}])
        question = self.case.reg("wizard", "question", {"id": "Q2", "question": "Allowed priorities?"}, source=b["source"])
        self.case.call("wizard", "clarify", subject=candidate, question=question)
        answer = self.case.reg("human", "answer", b"LOW, NORMAL, HIGH", question=question, source=b["source"])
        root = self.case.call("human", "answer", subject=answer)
        normative = self.c.closure(root, authoritative=True)
        self.assertIn(first_answer, normative)
        self.assertIn(answer, normative)
        self.assertNotIn(b["source"], normative)
        self.assertTrue(self.c.state(root)["eligible_for_new_use"])
        self.case.call("human", "invalidate", subject=first_answer, reason="retracted")
        self.assertFalse(self.c.state(root)["eligible_for_new_use"])

    def test_restart_detects_corrupt_artifact_and_journal(self):
        for target in ("artifacts", "journal"):
            with self.subTest(target=target), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "corrupt.sqlite"
                c = Controller(path, PRINCIPALS)
                Case(c).source()
                c.close()
                db = sqlite3.connect(path)
                db.execute(f"DROP TRIGGER {target}_no_update")
                if target == "artifacts":
                    db.execute("UPDATE artifacts SET envelope=replace(envelope, 'human-authorized-requirement', 'forged') WHERE id LIKE 'source:%'")
                else:
                    db.execute("UPDATE journal SET digest='tampered' WHERE revision=1")
                db.commit()
                db.close()
                with self.assertRaises(Failure) as caught:
                    Controller(path, PRINCIPALS)
                self.assertIn(caught.exception.code, {"CONTENT_MISMATCH", "JOURNAL_DIGEST_MISMATCH"})


class IdentityTests(unittest.TestCase):
    def test_canonical_conformance_vector(self):
        expected = b'{"a":[true,null,-1],"z":"\xc3\xa9"}'
        self.assertEqual(canonical({"z": "é", "a": [True, None, -1]}), expected)
        envelope = {"type": "frc", "schema": "authority-1", "content": {"a": [True, None, -1], "z": "é"}}
        self.assertEqual(identity(envelope).split(":")[-1], hashlib.sha256(canonical(envelope)).hexdigest())

    def test_reformatting_not_content_and_order_is_authoritative(self):
        self.assertEqual(canonical(parse_json('{"b":2,"a":1}')),
                         canonical(parse_json('{\n "a": 1, "b": 2\n}')))
        self.assertNotEqual(canonical([1, 2]), canonical([2, 1]))
        self.assertNotEqual(canonical("a\r\nb"), canonical("a\nb"))

    def test_duplicate_keys_float_nonfinite_large_integer_reject(self):
        for text in ('{"a":1,"a":2}', '{"a":1e0}', '{"a":1.0}', '{"a":NaN}',
                     '{"a":Infinity}', '{"a":9007199254740992}', '{"a":-0}'):
            with self.subTest(text=text), self.assertRaises(Failure):
                parse_json(text)
        for value in (1.0, float("nan"), 9007199254740992, {1: "bad"}, (1, 2)):
            with self.subTest(value=value), self.assertRaises(Failure):
                canonical(value)

    def test_type_schema_content_and_dependencies_bound(self):
        envelope = {"type": "frc", "schema": "authority-1", "content": {"x": 1}, "dependencies": {"source": "v1"}}
        original = identity(envelope)
        for key, value in (("type", "soi"), ("schema", "authority-2"), ("content", {"x": 2}),
                           ("dependencies", {"source": "v2"})):
            self.assertNotEqual(original, identity(dict(envelope, **{key: value})))


if __name__ == "__main__":
    unittest.main()
