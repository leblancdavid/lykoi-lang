"""Trusted session orchestration, immutable evidence, finite source-only review.

Authority is exclusively Controller.execute. Session cursors and review budgets
are reconstructed from its journal, rather than persisted approval booleans.
FRC/SOI records use the existing research contracts inside authority-1 wrappers.
"""
from __future__ import annotations

import copy
import hashlib

from benchmark.evaluation.formal_requirements_r5_80 import ContractError, validate, check_revision
from lykoi_controller import Failure, canonical


PRIORITIES = {"BLOCKING", "IMPORTANT", "INFORMATIONAL"}
PROVENANCE = {"human_statement", "clarification_answer", "approved_policy",
              "observed_legacy_behavior", "test_supported_behavior", "documentation_claim"}


class Workspace:
    MAX_REVIEWS = 2  # first review + one human/candidate correction re-review

    def __init__(self, controller, project, session, service_credentials):
        self.c, self.project, self.session = controller, project, session
        # Trusted service credentials only; human credential is supplied per action.
        self.credentials = dict(service_credentials)

    def _call(self, role, command, **args):
        return self.c.execute(self.credentials[role], self.project, command,
                              expected_revision=self.c.revision, **args)

    def _human(self, credential, command, **args):
        return self.c.execute(credential, self.project, command,
                              expected_revision=self.c.revision, **args)

    def _reg(self, role, kind, content, **dependencies):
        return self._call(role, "register", kind=kind, content=content, dependencies=dependencies)

    def _validate(self, aid, access=None):
        self._call("mechanical", "validate", subject=aid, check="identity-closure", access=access)

    def _review(self, aid, outcome, rationale):
        self._call("reviewer", "review", subject=aid, outcome=outcome, rationale=rationale,
                   access=list(self.c.artifact(aid)["dependencies"].values()))

    def _records(self, kind):
        result = []
        for e in self.c.events():
            if e["type"] != "ARTIFACT_REGISTERED" or not e["subject"]:
                continue
            a = self.c.artifact(e["subject"])
            if (a["project"] == self.project and a["type"] == kind
                    and a["content"].get("workspace") == self.session):
                result.append((e["subject"], a))
        return result

    def _source_belongs(self, aid):
        a = self.c.artifact(aid)
        if a["project"] != self.project or a["type"] != "source":
            return False
        message = self.c.artifact(a["dependencies"]["message"])
        return message["content"].get("workspace") == self.session

    @property
    def sources(self):
        return list(dict.fromkeys(e["subject"] for e in self.c.events()
                    if e["type"] == "HUMAN_AUTHORIZED" and e["subject"]
                    and self._source_belongs(e["subject"])))

    @property
    def source(self):
        if not self.sources:
            raise Failure("SOURCE_REQUIRED")
        return self.sources[-1]

    @property
    def candidate(self):
        candidates = [(aid, a) for aid, a in self._records("frc")
                      if a["dependencies"]["source"] == self.source]
        if not candidates:
            raise Failure("CANDIDATE_REQUIRED")
        return candidates[-1][0]

    def ingest(self, credential, text, policies=()):
        if type(text) is not str or not text.strip():
            raise Failure("TEXT_REQUIRED")
        old = self.sources[-1] if self.sources else None
        message = self._human(credential, "register", kind="message",
                              content={"workspace": self.session, "text": text,
                                       "provenance": "human_statement", "version": len(self.sources) + 1})
        self._human(credential, "adopt", subject=message)
        deps = {"message": message}
        for policy in policies:
            p = self.c.artifact(policy)
            if p["type"] != "policy" or p["content"].get("scope") not in {"*", self.session}:
                raise Failure("POLICY_NOT_APPLICABLE")
            deps["policy:" + policy] = policy
        source = self._reg("formalizer", "source", {"workspace": self.session,
                           "provenance": "human_statement"}, **deps)
        self._human(credential, "adopt", subject=source)
        if old and self.c.state(old)["eligible_for_new_use"]:
            self._human(credential, "supersede", subject=old, replacement=source)
        return source

    def define_policy(self, rule, *, scope, waivable=True):
        return self._reg("formalizer", "policy", {"workspace": self.session,
                         "version": "ProjectPolicyContract-0.1", "rule": rule,
                         "scope": scope, "waivable": waivable})

    def adopt_policy(self, credential, policy, *, rationale, replaces=None):
        self._validate(policy)
        self._review(policy, "ACCEPTED", rationale)
        self._human(credential, "adopt", subject=policy)
        if replaces:
            self._human(credential, "supersede", subject=replaces, replacement=policy)
        return policy

    def inputs(self):
        source = self.source
        root = self.c.artifact(source)
        evidence = []
        for aid in sorted(self.c.closure(source, authoritative=True)):
            a = self.c.artifact(aid)
            if a["type"] == "message":
                evidence.append({"identity": aid, "text": a["content"]["text"],
                                 "provenance": "human_statement"})
            elif a["type"] == "answer":
                evidence.append({"identity": aid, "text": a["content"]["text"],
                                 "question": a["content"]["question_id"],
                                 "provenance": "clarification_answer"})
            elif a["type"] == "policy":
                evidence.append({"identity": aid, "text": a["content"]["rule"],
                                 "provenance": "approved_policy", "waivable": a["content"]["waivable"]})
        text = self.c.artifact(root["dependencies"]["message"])["content"]["text"]
        return {"identity": source, "text": text, "revision": len(self.sources)}, evidence

    def _produce(self, producer, role):
        if producer.role != role or not producer.session:
            raise Failure("PRODUCER_ROLE_MISMATCH")
        source, evidence = self.inputs()
        request = {"role": role, "session": producer.session, "source": source,
                   "evidence": evidence, "output_schema": "WorkspaceAnalysis-1" if role == "formalizer" else "WorkspaceSOI-1",
                   "instructions": "Propose WHAT only. Retain material uncertainty; conventions are not authority. "
                    + ("Extract source inventory without candidate access." if role == "reviewer" else "Propose obligations and product questions.")}
        from lykoi_pipeline.query_profile import formalizer_guidance
        request["instructions"] += " " + formalizer_guidance()
        from lykoi_pipeline.scalar_profile import formalizer_guidance as scalar_guidance
        from lykoi_pipeline.composition_profile import formalizer_guidance as composition_guidance
        request["instructions"] += " " + composition_guidance()
        request["instructions"] += " " + scalar_guidance()
        result = producer.produce(copy.deepcopy(request))
        canonical(result)
        if type(result) is not dict:
            raise Failure("INVALID_PRODUCER_OUTPUT")
        return copy.deepcopy(result), {"session": producer.session, "role": role,
                                      "provenance": copy.deepcopy(producer.provenance), "isolation": producer.isolation}

    def formalize(self, producer):
        if not self.c.state(self.source)["eligible_for_new_use"]:
            raise Failure("STALE_SOURCE")
        result, attribution = self._produce(producer, "formalizer")
        if any(a["content"]["producer"]["session"] == producer.session for _, a in self._records("soi")):
            raise Failure("SHARED_PRODUCER_CONTEXT")
        obligations = result["obligations"]
        from .query_schema import validate_output
        validate_output(result)
        questions = result.get("questions", [])
        for q in questions:
            if q["priority"] not in PRIORITIES or not q["text"]:
                raise Failure("INVALID_QUESTION")
        prior = self._records("frc")
        previous = prior[-1][1]["content"]["contract"] if prior else None
        retired = {oid for _, a in prior for row in a["content"]["contract"]["lineage"]
                   if row["change"] == "retire" for oid in row["previous"]}
        if retired & {o["id"] for o in obligations}:
            raise Failure("RETIRED_OBLIGATION_ID")
        # Conservative meaning equality, independent of artifact/revision identity.
        for _, a in prior:
            for old in a["content"]["contract"]["obligations"]:
                for new in obligations:
                    if (old["relation"], old["statement"]) == (new["relation"], new["statement"]) and old["id"] != new["id"]:
                        raise Failure("UNSTABLE_OBLIGATION_ID", previous=old["id"], proposed=new["id"])
        source, evidence = self.inputs()
        contract = {"schema_version": "FormalRequirementContract-0.1", "contract_id": self.session,
                    "revision": len(prior) + 1,
                    "source": {"id": source["identity"], "text": source["text"], "classification": "SYNTHETIC",
                               "sha256": hashlib.sha256(source["text"].encode("utf-8")).hexdigest()},
                    "context": {"scope": "Public synthetic requirements session " + self.session,
                                "domains": result.get("domains", {}), "assumptions": [], "component_authority": None},
                    "obligations": obligations, "issues": result.get("issues", []),
                    "unspecified": result.get("unspecified", []), "implementation_choices": [],
                    "lineage": result.get("lineage", []), "formalizer": attribution["session"], "review": None}
        try:
            validate(contract)
            from lykoi_pipeline.query_profile import validate_relations
            validate_relations(contract)
            from lykoi_pipeline.scalar_profile import applies, facts
            if applies(contract):
                facts(contract)
            if previous:
                check_revision(previous, contract)
        except ContractError as exc:
            raise Failure("INVALID_FRC", reason=str(exc)) from exc
        content = {"workspace": self.session, "contract": contract, "producer": attribution,
                   "authority": result.get("authority", {}), "questions": questions,
                   "policy_applications": result.get("policy_applications", []),
                   "unsupported": result.get("unsupported", []),
                   "necessary_implications": result.get("necessary_implications", []),
                   "exclusions": result.get("exclusions", []), "structure": result.get("structure", {})}
        frc = self._reg("formalizer", "frc", content, source=self.source)
        self._validate(frc)
        return frc

    def ask(self, question_id):
        frc = self.candidate
        q = next((q for q in self.c.artifact(frc)["content"]["questions"] if q["id"] == question_id), None)
        if q is None:
            raise Failure("UNKNOWN_QUESTION")
        aid = self._reg("formalizer", "question", dict(q, workspace=self.session), source=self.source)
        if q["priority"] != "INFORMATIONAL":
            self._call("formalizer", "clarify", subject=frc, question=aid)
        return aid

    def answer(self, credential, question, text):
        q = self.c.artifact(question)
        if q["dependencies"]["source"] != self.source or q["content"].get("workspace") != self.session:
            raise Failure("STALE_QUESTION")
        if not text.strip():
            raise Failure("ANSWER_REQUIRED")
        aid = self._human(credential, "register", kind="answer",
                          content={"workspace": self.session, "text": text, "question_id": q["content"]["id"],
                                   "provenance": "clarification_answer"},
                          dependencies={"question": question, "source": self.source})
        return self._human(credential, "answer", subject=aid)

    def revise_answer(self, credential, answer, text):
        # Explicit human withdrawal, fresh root retaining all OTHER answers, fresh
        # question and answer. No controller redesign or conflicting-answer override.
        old_source = self.source
        root = self.c.artifact(old_source)
        if answer not in root["dependencies"].values():
            raise Failure("ANSWER_NOT_CURRENT")
        old = self.c.artifact(answer)
        deps = {k: v for k, v in root["dependencies"].items() if v != answer and k != "predecessor"}
        fresh = self._reg("formalizer", "source", {"workspace": self.session, "revision_reason": "human answer replacement",
                          "replaces_answer": answer}, **deps)
        self._human(credential, "adopt", subject=fresh)
        self._human(credential, "supersede", subject=old_source, replacement=fresh)
        self._human(credential, "invalidate", subject=answer, reason="Human explicitly replaced clarification")
        text = self.c.artifact(deps["message"])["content"]["text"]
        resolution_contract = {"schema_version": "FormalRequirementContract-0.1",
                               "contract_id": self.session + ":resolution", "revision": 1,
                               "source": {"id": fresh, "text": text, "classification": "SYNTHETIC",
                                          "sha256": hashlib.sha256(text.encode()).hexdigest()},
                               "context": {"scope": "Explicit human clarification replacement", "domains": {},
                                           "assumptions": [], "component_authority": None},
                               "obligations": [], "issues": [{"id": "REPLACEMENT", "category": "QUESTION",
                                   "description": "Human must confirm replacement behavior", "affects": [],
                                   "alternatives": [], "witness": None, "resolved": False}],
                               "unspecified": [], "implementation_choices": [], "lineage": [],
                               "formalizer": "requirements-service", "review": None}
        validate(resolution_contract)
        placeholder = self._reg("formalizer", "frc", {"workspace": self.session + ":resolution",
                                "contract": resolution_contract}, source=fresh)
        question = self._reg("formalizer", "question", {"workspace": self.session,
                             "id": old["content"]["question_id"], "text": "Please confirm the revised behavior.",
                             "priority": "BLOCKING"}, source=fresh)
        self._call("formalizer", "clarify", subject=placeholder, question=question)
        return self.answer(credential, question, text)

    def _committed_reviews(self):
        ids = {aid for aid, _ in self._records("soi")}
        return [e for e in self.c.events() if e["type"] == "SOI_COMMITTED" and e["subject"] in ids]

    def commit_inventory(self, producer):
        if len(self._committed_reviews()) >= self.MAX_REVIEWS:
            raise Failure("FINITE_REVIEW_EXHAUSTED", permitted=self.MAX_REVIEWS)
        frc = self.candidate
        formalizer_sessions = {a["content"]["producer"]["session"] for _, a in self._records("frc")}
        if producer.session in formalizer_sessions:
            raise Failure("SHARED_PRODUCER_CONTEXT")
        result, attribution = self._produce(producer, "reviewer")
        soi = result["inventory"]
        source, evidence = self.inputs()
        record = self.c.artifact(frc)["content"]["contract"]["source"]
        expected = hashlib.sha256(canonical({"revision": len(self.sources), "record": record})).hexdigest()
        if soi["version"] != "SourceObligationInventory-0.1" or soi["source_commitment"] != expected:
            raise Failure("SOI_SOURCE_MISMATCH")
        ids, covered = set(), set()
        for item in soi["items"]:
            if set(item) != {"id", "spans", "meaning", "category", "material", "dependencies"}:
                raise Failure("MALFORMED_SOI_ITEM")
            if not item["id"] or item["id"] in ids or not item["meaning"] or type(item["material"]) is not bool:
                raise Failure("MALFORMED_SOI_ITEM")
            ids.add(item["id"])
            if not item["spans"]:
                raise Failure("SOI_SPAN_REQUIRED")
            for span in item["spans"]:
                start, end = span["start"], span["end"]
                if not (type(start) is int and type(end) is int and 0 <= start < end <= len(source["text"])
                        and source["text"][start:end] == span["quote"]):
                    raise Failure("SOI_SPAN_MISMATCH")
                covered.update(range(start, end))
        if any(i not in covered for i, ch in enumerate(source["text"]) if not ch.isspace()):
            raise Failure("SOI_TEXT_UNACCOUNTED")
        if any(set(item["dependencies"]) - ids for item in soi["items"]):
            raise Failure("SOI_UNBOUND_DEPENDENCY")
        content = {"workspace": self.session, "inventory": soi, "producer": attribution,
                   "interpretations": result.get("interpretations", {}),
                   "domains": result.get("domains", {}), "unspecified": result.get("unspecified", []),
                   "authority": result.get("authority", {}), "round": len(self._committed_reviews()) + 1}
        aid = self._reg("reviewer", "soi", content, source=self.source)
        self._validate(aid, [self.source])  # Controller creates SOI_COMMITTED here.
        self._call("controller", "begin_review", subject=frc, soi=aid)
        return aid

    def reconciliation_inputs(self, inventory):
        if not any(e["subject"] == inventory for e in self._committed_reviews()):
            raise Failure("INVENTORY_NOT_COMMITTED")
        frc = self.candidate
        if not any(e["subject"] == frc and e["type"] == "REVIEW_STARTED" and e["evidence"] == inventory
                   for e in self.c.events()):
            raise Failure("REVIEW_NOT_STARTED")
        if self.c.artifact(inventory)["dependencies"] != self.c.artifact(frc)["dependencies"]:
            raise Failure("SOURCE_SET_MISMATCH")
        return self.c.artifact(frc), self.c.artifact(inventory)

    def reconcile(self, inventory):
        f, s = self.reconciliation_inputs(inventory)
        fc, sc = f["content"], s["content"]
        source, evidence = self.inputs()
        allowed = {e["identity"] for e in evidence}
        obligations = {o["id"]: o for o in fc["contract"]["obligations"]}
        rows, matched = [], set()
        for item in sc["inventory"]["items"]:
            oid = item["id"]
            status = "MATCHED"
            if item["category"] == "NONBEHAVIORAL" and not item["material"]:
                status = "NONBEHAVIORAL"
            elif item["category"] in {"AMBIGUITY", "CONFLICT", "UNSPECIFIED"}:
                status = "AMBIGUITY"
            elif item["category"] not in {"BEHAVIOR", "FREEDOM", "CONSUMER_RESTRICTION", "CARDINALITY_BOUND"}:
                status = "UNSUPPORTED_SCOPE"
            elif oid not in obligations:
                status = "SOURCE_OBLIGATION_MISSING"
            elif oid not in sc["interpretations"]:
                status = "UNRESOLVED_MAPPING"
            elif not self._meaning_equal(obligations[oid], sc["interpretations"][oid]):
                status = "MATERIALLY_DIVERGENT"
            elif not sc["authority"].get(oid) or set(sc["authority"][oid]) - allowed:
                status = "LACKING_AUTHORITY"
            elif set(fc["authority"].get(oid, [])) != set(sc["authority"][oid]):
                status = "LACKING_AUTHORITY"
            else:
                matched.add(oid)
            rows.append({"item": oid, "status": status, "meaning": item["meaning"]})
        for oid in obligations.keys() - matched:
            if not any(r["item"] == oid and r["status"] != "NONBEHAVIORAL" for r in rows):
                rows.append({"item": oid, "status": "FRC_OBLIGATION_LACKING_AUTHORITY", "meaning": obligations[oid]["statement"]})
        policy_evidence = {e["identity"]: e for e in evidence if e["provenance"] == "approved_policy"}
        applications = fc["policy_applications"]
        if {b["policy"] for b in applications} != set(policy_evidence):
            rows.append({"item": "policies", "status": "POLICY_CONFLICT", "meaning": "Please confirm which project policies apply."})
        for binding in applications:
            policy = policy_evidence.get(binding["policy"])
            mode, feature = binding.get("mode"), binding.get("feature_decision")
            valid = policy and ((mode == "DEFAULT" and not feature) or
                                (mode == "FEATURE_EXCEPTION" and feature and policy["waivable"]))
            if not valid:
                rows.append({"item": "policy", "status": "POLICY_CONFLICT",
                             "meaning": "The feature request and project policy conflict. Which behavior should apply?"})
            elif mode == "FEATURE_EXCEPTION":
                rows.append({"item": "policy", "status": "FEATURE_OVERRIDES_POLICY", "meaning": feature,
                             "policy": binding["policy"]})
        if fc["contract"]["context"]["domains"] != sc["domains"] or fc["contract"]["unspecified"] != sc["unspecified"]:
            rows.append({"item": "context", "status": "MATERIALLY_DIVERGENT",
                         "meaning": "Please clarify which inputs and behavioral freedoms should apply."})
        if fc["unsupported"] or fc["structure"]:
            rows.append({"item": "scope", "status": "UNSUPPORTED_SCOPE", "meaning": str(fc["unsupported"])})
        if fc["contract"]["issues"] or sc["inventory"]["questions"] or any(q["priority"] != "INFORMATIONAL" for q in fc["questions"]):
            rows.append({"item": "questions", "status": "AMBIGUITY", "meaning": "Unresolved product questions"})
        # No unreviewed implications, exclusions or inferred structural scope.
        if fc["necessary_implications"] or fc["exclusions"] or any(o["basis"] != "STATED" for o in obligations.values()):
            rows.append({"item": "derivation", "status": "UNSUPPORTED_SCOPE", "meaning": "Requires separately qualified implication/exclusion review"})
        acceptable = bool(obligations) and all(r["status"] in {"MATCHED", "NONBEHAVIORAL", "FEATURE_OVERRIDES_POLICY"} for r in rows)
        aid = self._reg("reviewer", "coverage", {"workspace": self.session, "rows": rows,
                        "outcome": "ACCEPTABLE" if acceptable else "DISPUTED",
                        "limitation": "Exact structured clause comparison; no natural-language completeness proof"},
                        frc=self.candidate, soi=inventory)
        self._validate(aid)
        self._review(aid, "ACCEPTED" if acceptable else "DISPUTED", "Deterministic item-level bidirectional reconciliation")
        structural = self._reg("formalizer", "structural", {"workspace": self.session,
                               "scope": "requirements-only; no V1/BDI support asserted", "proposal": fc["structure"]}, frc=self.candidate)
        self._validate(structural)
        self._review(structural, "UNSUPPORTED", "Authoring projection deferred; WHAT-only requirements seal")
        return aid

    @staticmethod
    def _meaning_equal(candidate, interpretation):
        from lykoi_pipeline.query_profile import meaning_equal
        return meaning_equal(candidate, interpretation)

    def route_disagreement(self, coverage):
        a = self.c.artifact(coverage)
        if a["dependencies"]["frc"] != self.candidate or a["content"]["outcome"] != "DISPUTED":
            raise Failure("NO_CURRENT_DISPUTE")
        row = next(r for r in a["content"]["rows"] if r["status"] not in {"MATCHED", "NONBEHAVIORAL", "FEATURE_OVERRIDES_POLICY"})
        question = self._reg("reviewer", "question", {"workspace": self.session, "id": "RESOLVE." + row["item"],
                             "priority": "BLOCKING", "text": "Please clarify what you want: " + row["meaning"],
                             "dispute_evidence": coverage}, source=self.source)
        self._call("reviewer", "clarify", subject=self.candidate, question=question)
        return question

    def approval_summary(self, exact_frc):
        if exact_frc != self.candidate:
            raise Failure("WRONG_CANDIDATE_VERSION")
        a = self.c.artifact(exact_frc)["content"]
        return {"candidate": exact_frc, "commitments": [o["statement"] for o in a["contract"]["obligations"]],
                "freedoms": a["contract"]["unspecified"], "questions": a["questions"], "issues": a["contract"]["issues"]}

    def approve(self, credential, exact_frc):
        self.approval_summary(exact_frc)
        coverages = [(aid, a) for aid, a in self._records("coverage") if a["dependencies"]["frc"] == exact_frc]
        structures = [(aid, a) for aid, a in self._records("structural") if a["dependencies"]["frc"] == exact_frc]
        if not coverages or not structures:
            raise Failure("RECONCILIATION_REQUIRED")
        return self._human(credential, "approve", subject=exact_frc, coverage=coverages[-1][0], structural=structures[-1][0])

    def seal(self, exact_frc):
        if exact_frc != self.candidate:
            raise Failure("WRONG_CANDIDATE_VERSION")
        return self._call("controller", "seal_frc", subject=exact_frc)

    def status(self):
        try:
            candidate = self.candidate
        except Failure:
            candidate = None
        authority = self.c.state(candidate) if candidate else None
        coverages = [a for _, a in self._records("coverage") if a["dependencies"]["frc"] == candidate]
        needs_review = candidate and (not coverages or coverages[-1]["content"]["outcome"] != "ACCEPTABLE")
        return {"source_versions": self.sources, "candidate": candidate, "authority": authority,
                "reviews_used": len(self._committed_reviews()), "reviews_limit": self.MAX_REVIEWS,
                "halt": "FINITE_REVIEW_EXHAUSTED" if len(self._committed_reviews()) >= self.MAX_REVIEWS
                and needs_review else None}
