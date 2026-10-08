"""Research evaluation authority 1; never a product WHAT seal or author grant.

Semantic stage execution and external behavioral verification retain their own
existing gates. A review is a disclosed attestation,
not mechanically proven natural-language entailment or independent cognition.
"""
from __future__ import annotations


class ResearchAuthority:
    MAX_RESEARCH_REVIEWS = 3  # initial source review + at most two corrections

    def _research_binding(self, project, source, frc, plan, review):
        from .controller import Failure

        s = self._subject(source, project, "source")
        f = self._subject(frc, project, "frc")
        p = self._subject(plan, project, "research_plan")
        r = self._subject(review, project, "research_review")
        if f["dependencies"]["source"] != source or p["dependencies"] != {"source": source, "frc": frc}:
            raise Failure("RESEARCH_IDENTITY_MISMATCH")
        if r["dependencies"] != {"source": source, "frc": frc, "plan": plan}:
            raise Failure("RESEARCH_IDENTITY_MISMATCH")
        self._need(frc, "CANDIDATE_COMMITTED")
        # Source attribution is not source-project authorization. The approval
        # binds exact preserved message bytes and source provenance, not HUMAN_AUTHORIZED.
        message = self.artifact(s["dependencies"]["message"])["content"]
        text = message.get("text")
        if not isinstance(text, str) or not text:
            raise Failure("RESEARCH_SOURCE_TEXT_REQUIRED")
        if self.state(frc)["lifecycle"] == "CLARIFICATION":
            raise Failure("NEEDS_CLARIFICATION", reason="MATERIAL_DECISION_UNRESOLVED")
        for aid in self.closure(review, authoritative=True):
            if self._blocked(aid):
                raise Failure("NEEDS_CLARIFICATION", reason="DISPUTED_REVIEW", artifact=aid)
        contract = f["content"].get("contract", {})
        if contract.get("source") and contract["source"].get("text") != text:
            raise Failure("RESEARCH_IDENTITY_MISMATCH", reason="FRC source text differs from preserved source")
        if (contract.get("issues") or any(q.get("priority") != "INFORMATIONAL"
                for q in f["content"].get("questions", []))):
            raise Failure("NEEDS_CLARIFICATION", reason="MATERIAL_DECISION_UNRESOLVED")
        pc, rc = p["content"], r["content"]
        if not isinstance(pc, dict) or not isinstance(rc, dict):
            raise Failure("MALFORMED_REQUEST", command="research-review")
        list_fields = ("material_questions", "source_contradictions", "assumptions",
                       "nonblocking_uncertainties", "traceability")
        if any(not isinstance(rc.get(key), list) for key in list_fields):
            raise Failure("MALFORMED_REQUEST", command="research-review")
        if not isinstance(pc.get("checks"), list):
            raise Failure("RESEARCH_PLAN_NOT_READY")
        reviews = [e["subject"] for e in self.events() if e["type"] == "ARTIFACT_REGISTERED"
                   and e["subject"] and self.artifact(e["subject"])["type"] == "research_review"
                   and self.artifact(e["subject"])["dependencies"]["frc"] == frc]
        latest = self.artifact(reviews[-1])["content"]
        if latest["material_questions"] or latest["source_contradictions"]:
            raise Failure("NEEDS_CLARIFICATION", reason="MATERIAL_DECISION_UNRESOLVED")
        if reviews[-1] != review:
            raise Failure("STALE_RESEARCH_REVIEW")
        obligations = contract.get("obligations", f["content"].get("obligations", []))
        ids = [o["id"] for o in obligations]
        if not ids or len(ids) != len(set(ids)):
            raise Failure("RESEARCH_OBLIGATIONS_REQUIRED")
        if (rc["material_questions"] or rc["source_contradictions"]
                or rc["requested_scope_determined"] is not True):
            raise Failure("NEEDS_CLARIFICATION", reason="MATERIAL_DECISION_UNRESOLVED")
        if rc["review_context"] not in {"SEPARATE_CONTEXT", "SAME_AGENT", "SAME_MODEL"} or not rc["limitations"]:
            raise Failure("RESEARCH_REVIEW_DISCLOSURE_REQUIRED")
        rows = rc["traceability"]
        if (len(rows) != len(ids) or {row["obligation"] for row in rows} != set(ids)
                or any(row["source"] != source or not isinstance(row["evidence"], str)
                       or not row["evidence"] or row["evidence"] not in text for row in rows)):
            raise Failure("RESEARCH_TRACEABILITY_REQUIRED")
        if (pc["purpose"] != "research-evaluation-only" or pc["fixed_before_authoring"] is not True
                or pc["expectation_basis"] != "preserved-source"
                or not isinstance(pc["coverage_limitations"], list)):
            raise Failure("RESEARCH_PLAN_NOT_READY")
        checks = pc["checks"]
        if (not checks or len({c["id"] for c in checks}) != len(checks)
                or {oid for c in checks for oid in c["obligations"]} != set(ids)
                or any(not c["obligations"] or not c["observable"] or "expected" not in c for c in checks)):
            raise Failure("RESEARCH_ACCEPTANCE_BINDING_REQUIRED")
        if (not isinstance(rc["assumptions"], list)
                or not isinstance(rc["nonblocking_uncertainties"], list)):
            raise Failure("RESEARCH_ASSUMPTIONS_REQUIRED")
        # These are explicit source-only review premises. They do not substitute
        # for structural coverage, BDI, adequacy, faithful V1 or external checking.
        if self._producer(plan) == self._producer(frc):
            raise Failure("AUTHOR_VERIFICATION_ROLE_CONFLICT")
        return rc

    def _approve_research(self, actor, project, subject, source, plan, review, evaluation_actor):
        from .controller import Failure

        self._role(actor, {"research_approver"})
        rc = self._research_binding(project, source, subject, plan, review)
        principal = self.principals.get(evaluation_actor)
        if not principal or project not in principal["projects"] or "research_evaluator" not in principal["roles"]:
            raise Failure("RESEARCH_EVALUATOR_REQUIRED")
        if actor == self._producer(subject):
            raise Failure("RESEARCH_SELF_APPROVAL")
        approval = self._put("research_approval", project,
            {"purpose": "research-evaluation-only", "action": "evaluate", "principal": actor,
             "evaluation_actor": evaluation_actor, "assumptions": rc["assumptions"],
             "nonblocking_uncertainties": rc["nonblocking_uncertainties"],
             "review_context": rc["review_context"], "limitations": rc["limitations"],
             "authority_events": self._evidence_ids(review)},
            {"source": source, "frc": subject, "plan": plan, "review": review}, actor)
        self._event("RESEARCH_EVALUATION_APPROVED", approval, actor, "research_approver",
                    "RESEARCH_EVALUATION_APPROVED", evidence=approval)
        return approval

    def _begin_research_evaluation(self, actor, project, subject, source, frc, plan,
                                   purpose="research-evaluation-only"):
        from .controller import Failure

        self._role(actor, {"research_evaluator"})
        a = self._subject(subject, project, "research_approval")
        self._need(subject, "RESEARCH_EVALUATION_APPROVED")
        if purpose != "research-evaluation-only":
            raise Failure("RESEARCH_SCOPE_DENIED")
        if a["content"]["evaluation_actor"] != actor:
            raise Failure("RESEARCH_ACTOR_MISMATCH")
        d = a["dependencies"]
        if {"source": source, "frc": frc, "plan": plan} != {k: d[k] for k in ("source", "frc", "plan")}:
            raise Failure("RESEARCH_IDENTITY_MISMATCH")
        self._research_binding(project, source, frc, plan, d["review"])
        if self._has(subject, "RESEARCH_EVALUATION_STARTED"):
            raise Failure("RESEARCH_EVALUATION_REPLAY")
        attempt = self._put("research_evaluation", project,
            {"purpose": purpose, "actor": actor, "authoring_authorized": False,
             "production_authorized": False, "behaviorally_verified": False},
            {"approval": subject}, actor)
        self._event("RESEARCH_EVALUATION_STARTED", subject, actor, "research_evaluator",
                    "EVALUATION_STARTED", evidence=attempt)
        return attempt

    def _seal_research_frc(self, actor, project, subject):
        """Reuse the exact seal edge, with a distinct purpose and authority event."""
        self._role(actor, {"controller"})
        attempt = self._subject(subject, project, "research_evaluation")
        approval = attempt["dependencies"]["approval"]
        a = self._subject(approval, project, "research_approval")
        self._need(approval, "RESEARCH_EVALUATION_STARTED")
        d = a["dependencies"]
        self._research_binding(project, d["source"], d["frc"], d["plan"], d["review"])
        seal = self._put("frc_seal", project,
            {"purpose": "research-evaluation-only", "evaluation": subject,
             "authority_events": self._evidence_ids(approval)}, {"approval": approval}, actor)
        self._event("RESEARCH_FRC_SEALED", d["frc"], actor, "controller",
                    "RESEARCH_SEALED", evidence=seal)
        return seal
