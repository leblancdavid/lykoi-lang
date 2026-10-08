"""Content-bound, event-sourced authority controller (production envelope 1).

The embedding authority service owns credentials and the principal registry.
Workers submit candidates, never events. SQLite is the trusted persistence boundary.
Semantic producers and operating-system job isolation are deliberately separate.
"""
from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
from datetime import datetime, timezone

from .research import ResearchAuthority


class Failure(Exception):
    """Stable structured refusal; does not coerce a failed transition."""

    def __init__(self, code, **details):
        self.code = code
        self.details = details
        super().__init__(code)

    def as_dict(self):
        return {"code": self.code, "details": self.details}


def _value(value):
    if value is None or type(value) is bool:
        return
    if type(value) is int and abs(value) <= 9007199254740991:
        return
    if type(value) is str:
        try:
            value.encode("utf-8", errors="strict")
        except UnicodeEncodeError as exc:
            raise Failure("INVALID_UNICODE") from exc
        return
    if type(value) is list:
        for item in value:
            _value(item)
        return
    if type(value) is dict and all(type(k) is str for k in value):
        for k, v in value.items():
            _value(k)
            _value(v)
        return
    raise Failure("NON_CANONICAL_VALUE", type=type(value).__name__)


def canonical(value):
    """CJ-1: sorted keys, ordered arrays, compact UTF-8, safe integers only."""
    _value(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def parse_json(text):
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise Failure("DUPLICATE_KEY", key=k)
            result[k] = v
        return result

    def numeric(text):
        raise Failure("UNSUPPORTED_NUMBER", value=text)

    def integer(text):
        if text == "-0":
            raise Failure("UNSUPPORTED_NUMBER", value=text)
        return int(text)

    try:
        result = json.loads(text, object_pairs_hook=pairs, parse_int=integer, parse_float=numeric,
                            parse_constant=numeric)
    except json.JSONDecodeError as exc:
        raise Failure("MALFORMED_JSON", position=exc.pos) from exc
    canonical(result)
    return result


def identity(envelope):
    digest = hashlib.sha256(canonical(envelope)).hexdigest()
    return f"{envelope['type']}:{envelope['schema']}:CJ-1:sha256:{digest}"


# Named edges are part of identity. Producer envelopes are intentionally not
# historical FRC/BDI/V1 schemas; these are authority wrappers around exact content.
EDGES = {
    "message": {}, "context": {}, "policy": {}, "freeze": {},
    "source": {"message": "message"},
    "question": {"source": "source"},
    "answer": {"question": "question", "source": "source"},
    "frc": {"source": "source"},
    "soi": {"source": "source"},
    "coverage": {"frc": "frc", "soi": "soi"},
    "structural": {"frc": "frc"},
    "structural_receipt": {"seal": "frc_seal", "structural": "structural"},
    "bdi": {"seal": "frc_seal", "structural_receipt": "structural_receipt", "freeze": "freeze"},
    "adequacy": {"seal": "frc_seal", "bdi": "bdi", "structural_receipt": "structural_receipt", "freeze": "freeze"},
    "v1": {"seal": "frc_seal", "adequacy": "adequacy"},
    "plan": {"seal": "frc_seal", "freeze": "freeze"},
    "bundle": {"v1": "v1", "adequacy": "adequacy", "plan_seal": "plan_seal", "freeze": "freeze"},
    "model": {"bundle": "bundle", "grant": "grant"},
    "target": {"model": "model", "freeze": "freeze"},
    "verification": {"target": "target", "plan_seal": "plan_seal", "freeze": "freeze"},
    "research_plan": {"source": "source", "frc": "frc"},
    "research_review": {"source": "source", "frc": "frc", "plan": "research_plan"},
}
INTERNAL = {"approval", "frc_seal", "plan_seal", "policy_seal", "grant", "reservation",
            "research_approval", "research_evaluation"}
PRODUCERS = {
    "message": {"owner"}, "policy": {"owner", "formalizer"},
    "source": {"owner", "formalizer"}, "question": {"formalizer", "reviewer"},
    "answer": {"owner"}, "frc": {"formalizer"}, "soi": {"reviewer"},
    "coverage": {"reviewer"}, "structural": {"formalizer"},
    "structural_receipt": {"reviewer"}, "bdi": {"mechanical"},
    "adequacy": {"mechanical"}, "v1": {"formalizer"}, "plan": {"verifier"},
    "bundle": {"formalizer"}, "model": {"author"}, "target": {"mechanical"},
    "verification": {"verifier"}, "freeze": {"controller"}, "context": {"owner"},
    "research_plan": {"verifier"}, "research_review": {"reviewer"},
}


class Controller(ResearchAuthority):
    """One trusted service instance per connection; concurrent instances use CAS.

    Principals: {name: {credential: secret, roles: [...], projects: [...]}}.
    Provisioning is an administrator operation, not an AI-callable API. On restart
    the supplied registry must match the stored credential digests/roles/scopes.
    """

    def __init__(self, path, principals):
        self.db = sqlite3.connect(str(path), isolation_level=None, timeout=10)
        self.db.execute("PRAGMA foreign_keys=ON")
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS config (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS artifacts
                (id TEXT PRIMARY KEY, envelope TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS journal
                (revision INTEGER PRIMARY KEY, event TEXT NOT NULL, digest TEXT NOT NULL, recorded_at TEXT NOT NULL);
            CREATE TRIGGER IF NOT EXISTS artifacts_no_update BEFORE UPDATE ON artifacts
                BEGIN SELECT RAISE(ABORT, 'immutable artifact'); END;
            CREATE TRIGGER IF NOT EXISTS artifacts_no_delete BEFORE DELETE ON artifacts
                BEGIN SELECT RAISE(ABORT, 'immutable artifact'); END;
            CREATE TRIGGER IF NOT EXISTS journal_no_update BEFORE UPDATE ON journal
                BEGIN SELECT RAISE(ABORT, 'append-only journal'); END;
            CREATE TRIGGER IF NOT EXISTS journal_no_delete BEFORE DELETE ON journal
                BEGIN SELECT RAISE(ABORT, 'append-only journal'); END;
            CREATE TRIGGER IF NOT EXISTS config_no_update BEFORE UPDATE ON config
                BEGIN SELECT RAISE(ABORT, 'immutable registry'); END;
            CREATE TRIGGER IF NOT EXISTS config_no_delete BEFORE DELETE ON config
                BEGIN SELECT RAISE(ABORT, 'immutable registry'); END;
        """)
        self.principals = {
            name: {"credential_digest": hashlib.sha256(p["credential"].encode()).hexdigest(),
                   "roles": sorted(p["roles"]), "projects": sorted(p["projects"])}
            for name, p in principals.items()
        }
        tokens = [p["credential_digest"] for p in self.principals.values()]
        if len(tokens) != len(set(tokens)):
            self.db.close()
            raise Failure("DUPLICATE_CREDENTIAL")
        self.db.execute("INSERT OR IGNORE INTO config VALUES ('principals', ?)",
                        (canonical(self.principals).decode(),))
        stored = self.db.execute("SELECT value FROM config WHERE key='principals'").fetchone()[0]
        if stored != canonical(self.principals).decode():
            self.db.close()
            raise Failure("REGISTRY_MISMATCH")
        try:
            self.check_integrity()
        except Exception:
            self.db.close()
            raise

    def close(self):
        self.db.close()

    @property
    def revision(self):
        return self.db.execute("SELECT COALESCE(MAX(revision), 0) FROM journal").fetchone()[0]

    def events(self):
        return [dict(parse_json(text), event_identity="event:CJ-1:sha256:" + digest)
                for text, digest in self.db.execute("SELECT event,digest FROM journal ORDER BY revision")]

    def _evidence_ids(self, aid):
        graph = self.closure(aid, authoritative=True)
        return [e["event_identity"] for e in self.events() if e["subject"] in graph
                and e["type"] not in {"ARTIFACT_REGISTERED", "TRANSITION_DENIED", "GRANT_DENIED"}]

    def artifact(self, aid):
        row = self.db.execute("SELECT envelope FROM artifacts WHERE id=?", (aid,)).fetchone()
        if not row:
            raise Failure("UNKNOWN_ARTIFACT", artifact=aid)
        envelope = parse_json(row[0])
        if identity(envelope) != aid:
            raise Failure("CONTENT_MISMATCH", artifact=aid)
        return envelope

    def closure(self, aid, *, authoritative=False):
        result = set()

        def visit(current):
            if current in result:
                return
            result.add(current)
            a = self.artifact(current)
            for edge, dep in a["dependencies"].items():
                # Historical transcript anchors remain inspectable, but a new
                # root does not inherit its predecessor's execution authority.
                if authoritative and ((a["type"] == "source" and edge == "predecessor")
                                      or a["type"] in {"answer", "question"}):
                    continue
                visit(dep)

        visit(aid)
        return result

    def check_integrity(self):
        previous = None
        for revision, text, digest in self.db.execute("SELECT revision,event,digest FROM journal ORDER BY revision"):
            event = parse_json(text)
            if event["revision"] != revision or event["previous"] != previous:
                raise Failure("JOURNAL_CHAIN_MISMATCH")
            if hashlib.sha256(canonical(event)).hexdigest() != digest:
                raise Failure("JOURNAL_DIGEST_MISMATCH")
            if revision != event["expected_revision"] + 1:
                raise Failure("JOURNAL_REVISION_MISMATCH")
            previous = digest
        for (aid,) in self.db.execute("SELECT id FROM artifacts"):
            self.closure(aid)

    def _event(self, kind, subject, actor, role, state, evidence=None, reason=None):
        rev = self.revision
        prev = self.db.execute("SELECT digest FROM journal WHERE revision=?", (rev,)).fetchone()
        deps = self.artifact(subject)["dependencies"] if subject else {}
        evidence_identity = None
        if evidence is not None or reason is not None:
            if type(evidence) is str and self.db.execute("SELECT 1 FROM artifacts WHERE id=?", (evidence,)).fetchone():
                evidence_identity = evidence
            else:
                evidence_identity = "evidence:CJ-1:sha256:" + hashlib.sha256(
                    canonical({"evidence": evidence, "reason": reason})).hexdigest()
        event = {"revision": rev + 1, "expected_revision": rev,
                 "previous": prev[0] if prev else None, "type": kind,
                 "subject": subject, "identity": subject, "prerequisites": deps,
                 "actor": actor, "role": role, "state": state,
                 "evidence": evidence, "evidence_identity": evidence_identity, "reason": reason}
        data = canonical(event)
        self.db.execute("INSERT INTO journal VALUES (?, ?, ?, ?)",
                        (rev + 1, data.decode(), hashlib.sha256(data).hexdigest(),
                         datetime.now(timezone.utc).isoformat()))

    def _actor(self, credential, project):
        digest = hashlib.sha256(credential.encode()).hexdigest()
        for name, principal in self.principals.items():
            if principal["credential_digest"] == digest:
                if project not in principal["projects"]:
                    raise Failure("SCOPE_DENIED", project=project)
                return name
        raise Failure("UNAUTHENTICATED")

    def _role(self, actor, allowed):
        roles = set(self.principals[actor]["roles"]) & set(allowed)
        if not roles:
            raise Failure("ROLE_DENIED", actor=actor, required=sorted(allowed))
        return sorted(roles)[0]

    def _has(self, aid, kind, outcome=None):
        return any(e["subject"] == aid and e["type"] == kind
                   and (outcome is None or e["reason"] == outcome) for e in self.events())

    def _producer(self, aid):
        return next(e["actor"] for e in self.events()
                    if e["type"] == "ARTIFACT_REGISTERED" and e["subject"] == aid)

    def _fresh(self, aid):
        graph = self.closure(aid, authoritative=True)
        stale = [e["subject"] for e in self.events()
                 if e["type"] in {"ARTIFACT_SUPERSEDED", "DEPENDENCY_INVALIDATED"}
                 and e["subject"] in graph]
        if stale:
            raise Failure("STALE_DEPENDENCY", artifacts=sorted(set(stale)))

    def _need(self, aid, kind, outcome=None):
        if not self._has(aid, kind, outcome):
            raise Failure("MISSING_EVIDENCE", artifact=aid, event=kind, outcome=outcome)

    def _coherent(self, aid):
        # All normative paths must resolve to one source, candidate FRC, WHAT
        # seal and freeze. Lineage is historical, not a second normative source.
        graph = self.closure(aid, authoritative=True)
        for kind in ("source", "frc", "frc_seal", "freeze", "plan", "plan_seal"):
            matches = {x for x in graph if self.artifact(x)["type"] == kind}
            if len(matches) > 1:
                raise Failure("DEPENDENCY_MISMATCH", type=kind, identities=sorted(matches))

    def _put(self, kind, project, content, deps, actor, schema="authority-1"):
        envelope = {"type": kind, "schema": schema, "serializer": "CJ-1",
                    "digest_algorithm": "sha256", "project": project,
                    "content": content, "dependencies": dict(deps)}
        aid = identity(envelope)
        for dep in deps.values():
            if self.artifact(dep)["project"] != project:
                raise Failure("CROSS_PROJECT_DEPENDENCY")
        existed = self.db.execute("SELECT 1 FROM artifacts WHERE id=?", (aid,)).fetchone()
        if not existed:
            self.db.execute("INSERT INTO artifacts VALUES (?, ?)", (aid, canonical(envelope).decode()))
            issuer = "controller-service" if kind in INTERNAL else actor
            role = "controller" if kind in INTERNAL else self._role(actor, PRODUCERS[kind])
            self._event("ARTIFACT_REGISTERED", aid, issuer, role, "CANDIDATE")
        return aid

    def execute(self, credential, project, command, *, expected_revision, **args):
        """Atomic compare-and-append. The only authority-changing public API."""
        actor = None
        self.db.execute("BEGIN IMMEDIATE")
        try:
            actor = self._actor(credential, project)
            if self.revision != expected_revision:
                raise Failure("REVISION_RACE", expected=expected_revision, actual=self.revision)
            handlers = {name: getattr(self, "_" + name) for name in (
                "register", "adopt", "review", "validate", "begin_review", "approve",
                "seal_frc", "seal_plan", "clarify", "answer", "supersede", "invalidate",
                "grant", "reserve", "complete", "bind_verification",
                "approve_research", "begin_research_evaluation", "seal_research_frc")}
            if command not in handlers:
                raise Failure("UNKNOWN_COMMAND", command=command)
            try:
                result = handlers[command](actor, project, **args)
            except (KeyError, TypeError, ValueError) as exc:
                raise Failure("MALFORMED_REQUEST", command=command) from exc
            self.db.execute("COMMIT")
            return result
        except Failure as exc:
            self.db.execute("ROLLBACK")
            # A denial is also immutable history; it cannot alter subject state.
            self.db.execute("BEGIN IMMEDIATE")
            subject = args.get("subject")
            if subject and not self.db.execute("SELECT 1 FROM artifacts WHERE id=?", (subject,)).fetchone():
                subject = None
            self._event("GRANT_DENIED" if command in {"grant", "reserve"} else "TRANSITION_DENIED",
                        subject, actor or "unattributed", "controller", "UNCHANGED",
                        reason=exc.as_dict())
            self.db.execute("COMMIT")
            raise
        except Exception:
            self.db.execute("ROLLBACK")
            raise

    def _subject(self, subject, project, kind=None):
        a = self.artifact(subject)
        if a["project"] != project:
            raise Failure("SCOPE_DENIED")
        if kind and a["type"] != kind:
            raise Failure("TYPE_MISMATCH", expected=kind, actual=a["type"])
        self._fresh(subject)
        self._coherent(subject)
        return a

    def _register(self, actor, project, kind, content, dependencies=None, schema="authority-1"):
        if kind not in EDGES:
            raise Failure("RESERVED_OR_UNKNOWN_TYPE", type=kind)
        self._role(actor, PRODUCERS[kind])
        deps = dependencies or {}
        if kind == "research_plan" and "author" in self.principals[actor]["roles"]:
            raise Failure("AUTHOR_VERIFICATION_ROLE_CONFLICT")
        if kind == "research_review":
            prior = [e["subject"] for e in self.events() if e["type"] == "ARTIFACT_REGISTERED"
                     and e["subject"] and self.artifact(e["subject"])["type"] == "research_review"
                     and self.artifact(e["subject"])["dependencies"].get("frc") == deps.get("frc")]
            if len(prior) >= self.MAX_RESEARCH_REVIEWS:
                raise Failure("FINITE_RESEARCH_REVIEW_EXHAUSTED")
        if type(content) is bytes:
            content = {"encoding": "base64-exact-bytes", "bytes": base64.b64encode(content).decode("ascii")}
        for name, required in EDGES[kind].items():
            if name not in deps or self.artifact(deps[name])["type"] != required:
                raise Failure("REQUIRED_DEPENDENCY", edge=name, type=required)
        # Optional edges are typed too, never opaque unvalidated locators.
        for name, dep in deps.items():
            self._fresh(dep)
            if name not in EDGES[kind]:
                allowed = {"predecessor": "source", "answer": "answer", "context": "context"}
                required = ("policy" if name.startswith("policy:") else
                            "answer" if name.startswith("answer:") else allowed.get(name))
                permitted = kind == "source" or (kind in {"frc", "soi"} and name.startswith("policy:"))
                if not permitted or not required or self.artifact(dep)["type"] != required:
                    raise Failure("UNKNOWN_DEPENDENCY_EDGE", edge=name)
        if kind == "soi":
            if any(self.artifact(x)["type"] == "frc" for dep in deps.values() for x in self.closure(dep)):
                raise Failure("BLIND_INPUT_VIOLATION")
        if kind == "model":
            self._need(deps["grant"], "DISPATCH_RESERVED")
            reservation = next(e["evidence"] for e in self.events()
                               if e["subject"] == deps["grant"] and e["type"] == "DISPATCH_RESERVED")
            if self.artifact(reservation)["content"]["actor"] != actor:
                raise Failure("RESERVATION_ACTOR_MISMATCH")
        if kind == "target":
            if not any(e["type"] == "DISPATCH_COMPLETED" and e["evidence"] == deps["model"] for e in self.events()):
                raise Failure("AUTHORING_INCOMPLETE")
        aid = self._put(kind, project, content, deps, actor, schema)
        self._coherent(aid)
        return aid

    def _adopt(self, actor, project, subject, evidence=None):
        role = self._role(actor, {"owner"})
        a = self._subject(subject, project)
        if a["type"] not in {"source", "policy", "message", "context"}:
            raise Failure("INVALID_ADOPTION_TYPE")
        if a["type"] == "source":
            self._need(a["dependencies"]["message"], "HUMAN_AUTHORIZED")
            for name, dep in a["dependencies"].items():
                if name.startswith("policy:"):
                    self._need(dep, "POLICY_SEALED")
                    if self._blocked(dep):
                        raise Failure("POLICY_DISPUTED")
                if name == "context":
                    self._need(dep, "HUMAN_AUTHORIZED")
                if name == "answer" or name.startswith("answer:"):
                    self._need(dep, "CLARIFICATION_ANSWERED")
        if a["type"] == "policy":
            self._need(subject, "REVIEW_COMMITTED", "ACCEPTED")
            self._need(subject, "MECHANICALLY_VALIDATED")
            if self._blocked(subject):
                raise Failure("POLICY_DISPUTED")
        self._event("HUMAN_AUTHORIZED", subject, actor, role, "HUMAN_AUTHORIZED", evidence=evidence)
        if a["type"] == "policy":
            seal = self._put("policy_seal", project, {"purpose": "policy-default", "authority_events": self._evidence_ids(subject)},
                             {"policy": subject}, actor)
            self._event("POLICY_SEALED", subject, "controller-service", "controller", "SEALED", evidence=seal)
        return subject

    def _review(self, actor, project, subject, outcome, rationale, access):
        role = self._role(actor, {"reviewer"})
        a = self._subject(subject, project)
        if actor == self._producer(subject) and a["type"] not in {"coverage", "structural_receipt"}:
            raise Failure("SELF_REVIEW")
        if a["type"] not in {"policy", "coverage", "structural", "structural_receipt", "adequacy", "v1", "plan"}:
            raise Failure("INVALID_REVIEW_TYPE")
        if outcome not in {"ACCEPTED", "DISPUTED", "UNSUPPORTED", "REVISION_REQUIRED", "REJECTED"}:
            raise Failure("INVALID_REVIEW_OUTCOME")
        if not rationale or type(access) is not list:
            raise Failure("MISSING_REVIEW_RECEIPT")
        # Bind rationale and admitted access list as immutable evidence, not booleans.
        for dep in access:
            self.artifact(dep)
        if a["type"] == "coverage":
            d = a["dependencies"]
            soi = self.artifact(d["soi"])
            frc = self.artifact(d["frc"])
            if soi["dependencies"] != frc["dependencies"]:
                raise Failure("SOURCE_SET_MISMATCH")
            self._need(d["soi"], "SOI_COMMITTED")
            self._need(d["frc"], "CANDIDATE_COMMITTED")
        self._event("REVIEW_COMMITTED", subject, actor, role, "REVIEWED",
                    evidence={"rationale": rationale, "access": access}, reason=outcome)
        if a["type"] == "coverage" and outcome in {"REVISION_REQUIRED", "REJECTED"}:
            self._event("REVIEW_DISPOSITION", a["dependencies"]["frc"], actor, role,
                        outcome, evidence=subject)
        return subject

    def _validate(self, actor, project, subject, check, outcome="PASS", access=None):
        role = self._role(actor, {"mechanical", "controller"})
        a = self._subject(subject, project)
        if outcome != "PASS":
            raise Failure("VALIDATION_FAILED", check=check)
        if check not in {"identity-closure", "synthetic-producer-receipt"}:
            raise Failure("UNKNOWN_CHECK")
        self._event("MECHANICALLY_VALIDATED", subject, actor, role, "MECHANICALLY_VALIDATED",
                    evidence={"check": check, "synthetic": check == "synthetic-producer-receipt"})
        if a["type"] == "soi":
            # Minimal access evidence bound at commitment; actual isolation is a
            # future workspace/deployment integration, not an assertion of truth.
            if set(access or []) != set(a["dependencies"].values()):
                raise Failure("BLIND_INPUT_VIOLATION")
            self._event("SOI_COMMITTED", subject, actor, role, "COMMITTED", evidence={"access": access})
        if a["type"] == "frc":
            self._event("CANDIDATE_COMMITTED", subject, actor, role, "DRAFT")
        return subject

    def _begin_review(self, actor, project, subject, soi):
        self._role(actor, {"controller"})
        frc = self._subject(subject, project, "frc")
        inventory = self._subject(soi, project, "soi")
        self._need(subject, "CANDIDATE_COMMITTED")
        self._need(soi, "SOI_COMMITTED")
        if frc["dependencies"] != inventory["dependencies"]:
            raise Failure("SOURCE_SET_MISMATCH")
        self._need(frc["dependencies"]["source"], "HUMAN_AUTHORIZED")
        if self.state(subject)["lifecycle"] != "DRAFT":
            raise Failure("INVALID_TRANSITION")
        self._event("REVIEW_STARTED", subject, actor, "controller", "REVIEW", evidence=soi)
        return subject

    def _approve(self, actor, project, subject, coverage, structural):
        self._role(actor, {"owner"})
        self._subject(subject, project, "frc")
        if self.state(subject)["lifecycle"] != "REVIEW":
            raise Failure("INVALID_TRANSITION", required="REVIEW")
        for aid, kind in ((coverage, "coverage"), (structural, "structural")):
            a = self._subject(aid, project, kind)
            if a["dependencies"]["frc"] != subject:
                raise Failure("DEPENDENCY_MISMATCH")
            self._need(aid, "MECHANICALLY_VALIDATED")
        self._need(coverage, "REVIEW_COMMITTED", "ACCEPTED")
        inventory = self.artifact(coverage)["dependencies"]["soi"]
        committed_inventory = next(e["evidence"] for e in self.events()
                                   if e["subject"] == subject and e["type"] == "REVIEW_STARTED")
        if inventory != committed_inventory:
            raise Failure("REVIEW_INVENTORY_MISMATCH")
        self._check_policies(subject)
        # Later disagreement cannot be hidden by an earlier accepted event.
        if self._blocked(coverage):
            raise Failure("DISPUTED_COVERAGE")
        if not any(self._has(structural, "REVIEW_COMMITTED", o) for o in ("ACCEPTED", "UNSUPPORTED")):
            raise Failure("MISSING_STRUCTURAL_STATUS")
        if any(self._has(structural, "REVIEW_COMMITTED", o)
               for o in ("DISPUTED", "REVISION_REQUIRED", "REJECTED")):
            raise Failure("DISPUTED_STRUCTURAL")
        evidence = self._evidence_ids(subject) + self._evidence_ids(coverage) + self._evidence_ids(structural)
        approval = self._put("approval", project, {"purpose": "WHAT", "principal": actor, "authority_events": sorted(set(evidence))},
                             {"frc": subject, "coverage": coverage, "structural": structural}, actor)
        self._event("APPROVAL_GRANTED", subject, actor, "owner", "APPROVED", evidence=approval)
        return approval

    def _check_policies(self, subject):
        """Enforce explicit scoped selection, not natural-language precedence."""
        graph = self.closure(subject, authoritative=True)
        policies = {x for x in graph if self.artifact(x)["type"] == "policy"}
        bindings = self.artifact(subject)["content"].get("policy_applications", [])
        if {b["policy"] for b in bindings} != policies:
            raise Failure("POLICY_APPLICATION_REQUIRED")
        for binding in bindings:
            policy = self.artifact(binding["policy"])["content"]
            self._need(binding["policy"], "POLICY_SEALED")
            if self._blocked(binding["policy"]):
                raise Failure("POLICY_DISPUTED")
            if binding.get("mode") == "FEATURE_EXCEPTION":
                if policy.get("waivable") is not True or not binding.get("feature_decision"):
                    raise Failure("POLICY_CONFLICT")
            elif binding.get("mode") == "DEFAULT":
                if binding.get("feature_decision"):
                    raise Failure("POLICY_CANNOT_OVERRIDE_FEATURE")
            else:
                raise Failure("POLICY_CONFLICT")

    def _blocked(self, aid):
        return any(e["subject"] == aid and e["type"] == "REVIEW_COMMITTED"
                   and e["reason"] != "ACCEPTED" for e in self.events())

    def _seal_frc(self, actor, project, subject):
        self._role(actor, {"controller"})
        self._subject(subject, project, "frc")
        if self.state(subject)["lifecycle"] != "APPROVED":
            raise Failure("INVALID_TRANSITION", required="APPROVED")
        approval = next(e["evidence"] for e in reversed(self.events())
                        if e["subject"] == subject and e["type"] == "APPROVAL_GRANTED")
        self._fresh(approval)
        coverage = self.artifact(approval)["dependencies"]["coverage"]
        if self._blocked(coverage):
            raise Failure("DISPUTED_COVERAGE")
        structural = self.artifact(approval)["dependencies"]["structural"]
        if any(self._has(structural, "REVIEW_COMMITTED", o)
               for o in ("DISPUTED", "REVISION_REQUIRED", "REJECTED")):
            raise Failure("DISPUTED_STRUCTURAL")
        self._check_policies(subject)
        self._need(subject, "MECHANICALLY_VALIDATED")
        seal = self._put("frc_seal", project, {"purpose": "WHAT", "authority_events": self._evidence_ids(approval)}, {"approval": approval}, actor)
        self._event("ARTIFACT_SEALED", subject, actor, "controller", "SEALED", evidence=seal)
        return seal

    def _seal_plan(self, actor, project, subject):
        self._role(actor, {"verification_authority"})
        a = self._subject(subject, project, "plan")
        self._need(subject, "REVIEW_COMMITTED", "ACCEPTED")
        self._need(subject, "MECHANICALLY_VALIDATED")
        if self._blocked(subject):
            raise Failure("PLAN_NOT_READY")
        self._need(a["dependencies"]["freeze"], "MECHANICALLY_VALIDATED")
        self._event("PLAN_APPROVAL_GRANTED", subject, actor, "verification_authority", "APPROVED")
        seal = self._put("plan_seal", project, {"purpose": "independent-verification", "principal": actor,
                                               "authority_events": self._evidence_ids(subject)},
                         {"plan": subject}, actor)
        self._event("PLAN_SEALED", subject, "controller-service", "controller", "SEALED", evidence=seal)
        return seal

    def _clarify(self, actor, project, subject, question):
        role = self._role(actor, {"formalizer", "reviewer"})
        frc = self._subject(subject, project, "frc")
        q = self._subject(question, project, "question")
        if q["dependencies"]["source"] != frc["dependencies"]["source"]:
            raise Failure("DEPENDENCY_MISMATCH")
        if self.state(subject)["lifecycle"] not in {"DRAFT", "REVIEW"}:
            raise Failure("INVALID_TRANSITION")
        self._event("CLARIFICATION_REQUESTED", subject, actor, role, "CLARIFICATION", evidence=question)
        return question

    def _answer(self, actor, project, subject):
        self._role(actor, {"owner"})
        a = self._subject(subject, project, "answer")
        d = a["dependencies"]
        if self.artifact(d["question"])["dependencies"]["source"] != d["source"]:
            raise Failure("DEPENDENCY_MISMATCH")
        if not any(e["type"] == "CLARIFICATION_REQUESTED" and e["evidence"] == d["question"] for e in self.events()):
            raise Failure("QUESTION_NOT_REQUESTED")
        if any(e["type"] == "CLARIFICATION_ANSWERED" and
               self.artifact(e["subject"])["dependencies"]["question"] == d["question"] for e in self.events()):
            raise Failure("CONFLICTING_ANSWER", resolution="explicit supersession required")
        self._event("CLARIFICATION_ANSWERED", subject, actor, "owner", "HUMAN_AUTHORIZED")
        old = self.artifact(d["source"])
        deps = dict(old["dependencies"])
        if "answer" in deps:
            prior = deps.pop("answer")
            deps["answer:" + prior] = prior
        deps.update(predecessor=d["source"], answer=subject)
        new = self._put("source", project, {"revision_of": d["source"], "answer": subject}, deps, actor)
        self._event("HUMAN_AUTHORIZED", new, actor, "owner", "HUMAN_AUTHORIZED", evidence=subject)
        self._event("ARTIFACT_SUPERSEDED", d["source"], actor, "owner", "SUPERSEDED", evidence=new)
        return new

    def _supersede(self, actor, project, subject, replacement):
        self._role(actor, {"owner"})
        old = self._subject(subject, project)
        new = self._subject(replacement, project, old["type"])
        if subject == replacement:
            raise Failure("SAME_REPLACEMENT")
        if old["type"] in {"source", "policy"}:
            self._need(replacement, "HUMAN_AUTHORIZED")
        self._event("ARTIFACT_SUPERSEDED", subject, actor, "owner", "SUPERSEDED", evidence=replacement)
        return replacement

    def _invalidate(self, actor, project, subject, reason):
        self._role(actor, {"owner", "controller"})
        self._subject(subject, project)
        self._event("DEPENDENCY_INVALIDATED", subject, actor, "controller", "REVOKED_FOR_NEW_USE", reason=reason)

    def _grant(self, actor, project, subject):
        self._role(actor, {"controller"})
        a = self._subject(subject, project, "bundle")
        if self._has(subject, "GRANT_ISSUED"):
            raise Failure("GRANT_ALREADY_ISSUED", requirement="new explicit authoring bundle/attempt")
        graph = self.closure(subject, authoritative=True)
        for kind in ("coverage", "structural", "structural_receipt", "bdi", "adequacy", "v1", "plan", "freeze"):
            matches = [x for x in graph if self.artifact(x)["type"] == kind]
            if len(matches) != 1:
                raise Failure("MISSING_OR_AMBIGUOUS_STAGE", stage=kind)
            aid = matches[0]
            self._need(aid, "MECHANICALLY_VALIDATED")
            if kind in {"coverage", "structural", "structural_receipt", "adequacy", "v1", "plan"}:
                self._need(aid, "REVIEW_COMMITTED", "ACCEPTED")
                if self._blocked(aid):
                    raise Failure("UNSUPPORTED_OR_DISPUTED", stage=kind)
            # The trusted producer receipt declares native result; AI content
            # alone cannot make this sufficient without the events above.
            expected = {"structural_receipt": "SUPPORTED", "bdi": "SUPPORTED",
                        "adequacy": "ADEQUATE", "v1": "FAITHFUL_COMPLETE", "plan": "READY"}.get(kind)
            if expected and self.artifact(aid)["content"].get("outcome") != expected:
                raise Failure("UNSUPPORTED_OUTCOME", stage=kind)
        seals = [x for x in graph if self.artifact(x)["type"] == "frc_seal"]
        if len(seals) != 1:
            raise Failure("MISSING_WHAT_SEAL")
        if self.artifact(seals[0])["content"].get("purpose") != "WHAT":
            raise Failure("RESEARCH_NATIVE_PIPELINE_REQUIRED")
        frc = next(x for x in graph if self.artifact(x)["type"] == "frc")
        self._need(frc, "ARTIFACT_SEALED")
        self._check_policies(frc)
        plan = self.artifact(a["dependencies"]["plan_seal"])["dependencies"]["plan"]
        self._need(plan, "PLAN_SEALED")
        grant = self._put("grant", project, {"purpose": "implementation", "action": "author",
                                            "prerequisite_closure": sorted(graph), "authority_events": self._evidence_ids(subject)},
                          {"bundle": subject, "freeze": a["dependencies"]["freeze"]}, actor)
        self._event("GRANT_ISSUED", subject, actor, "controller", "IMPLEMENTATION_AUTHORIZED", evidence=grant)
        return grant

    def applicable(self, grant, subject, freeze, action="author"):
        try:
            g = self.artifact(grant)
            if g["type"] != "grant" or g["content"]["action"] != action:
                raise Failure("GRANT_SCOPE_MISMATCH")
            if g["dependencies"] != {"bundle": subject, "freeze": freeze}:
                raise Failure("GRANT_IDENTITY_MISMATCH")
            self._fresh(grant)
            self._coherent(grant)
            self._need(subject, "GRANT_ISSUED")
            for aid in self.closure(grant, authoritative=True):
                if self._blocked(aid):
                    raise Failure("AUTHORITY_DISPUTED", artifact=aid)
            return {"applicable": True, "grant": grant}
        except Failure as exc:
            return {"applicable": False, "failure": exc.as_dict()}

    def _reserve(self, actor, project, subject, grant, freeze):
        self._role(actor, {"author"})
        bundle = self._subject(subject, project, "bundle")
        plan_seal = self.artifact(bundle["dependencies"]["plan_seal"])
        plan = plan_seal["dependencies"]["plan"]
        if actor in {self._producer(plan), plan_seal["content"]["principal"]}:
            raise Failure("AUTHOR_VERIFICATION_ROLE_CONFLICT")
        result = self.applicable(grant, subject, freeze)
        if not result["applicable"]:
            raise Failure(**{"code": result["failure"]["code"], **result["failure"]["details"]})
        if self._has(grant, "DISPATCH_RESERVED"):
            raise Failure("DISPATCH_REPLAY")
        reservation = self._put("reservation", project, {"actor": actor, "stage": "author"},
                                {"grant": grant, "bundle": subject}, actor)
        self._event("DISPATCH_RESERVED", grant, actor, "author", "RESERVED", evidence=reservation)
        return reservation

    def _complete(self, actor, project, subject, output):
        self._role(actor, {"author"})
        a = self._subject(subject, project, "reservation")
        if a["content"]["actor"] != actor:
            raise Failure("RESERVATION_ACTOR_MISMATCH")
        if self._has(subject, "DISPATCH_COMPLETED"):
            raise Failure("DISPATCH_REPLAY")
        model = self._subject(output, project, "model")
        if model["dependencies"] != a["dependencies"]:
            raise Failure("DEPENDENCY_MISMATCH")
        grant = a["dependencies"]["grant"]
        freeze = self.artifact(grant)["dependencies"]["freeze"]
        if not self.applicable(grant, a["dependencies"]["bundle"], freeze)["applicable"]:
            raise Failure("AUTHORITY_NO_LONGER_APPLICABLE")
        self._event("DISPATCH_COMPLETED", subject, actor, "author", "COMPLETED", evidence=output)
        return output

    def _bind_verification(self, actor, project, subject):
        self._role(actor, {"verifier"})
        a = self._subject(subject, project, "verification")
        graph = self.closure(subject)
        models = [x for x in graph if self.artifact(x)["type"] == "model"]
        if any(self._producer(m) == actor for m in models):
            raise Failure("SELF_VERIFICATION")
        self._need(subject, "MECHANICALLY_VALIDATED")
        self._need(a["dependencies"]["target"], "MECHANICALLY_VALIDATED")
        plan = self.artifact(a["dependencies"]["plan_seal"])["dependencies"]["plan"]
        self._need(plan, "PLAN_SEALED")
        self._event("VERIFICATION_BOUND", subject, actor, "verifier", "EXTERNALLY_VERIFIED",
                    evidence=a["dependencies"], reason=a["content"].get("outcome"))
        return subject

    def state(self, aid):
        self.artifact(aid)
        events = [e for e in self.events() if e["subject"] == aid]
        lifecycle = "DRAFT"
        for e in events:
            if e["type"] in {"REVIEW_STARTED", "APPROVAL_GRANTED", "ARTIFACT_SEALED", "CLARIFICATION_REQUESTED", "REVIEW_DISPOSITION"}:
                lifecycle = e["state"]
        try:
            self._fresh(aid)
            eligible = True
        except Failure:
            eligible = False
        return {"lifecycle": lifecycle, "candidate": True,
                "reviewed": self._has(aid, "REVIEW_COMMITTED") or self._has(aid, "APPROVAL_GRANTED"),
                "human_authorized": self._has(aid, "HUMAN_AUTHORIZED") or self._has(aid, "APPROVAL_GRANTED"),
                "mechanically_validated": self._has(aid, "MECHANICALLY_VALIDATED"),
                "sealed": self._has(aid, "ARTIFACT_SEALED") or self._has(aid, "PLAN_SEALED") or self._has(aid, "POLICY_SEALED"),
                "implementation_authorized": any(self.applicable(e["evidence"], aid,
                    self.artifact(e["evidence"])["dependencies"]["freeze"])["applicable"] for e in events if e["type"] == "GRANT_ISSUED"),
                "eligible_for_new_use": eligible}

    def audit(self, aid):
        graph = self.closure(aid)
        events = self.events()
        return {"identity": aid, "artifact": self.artifact(aid), "state": self.state(aid),
                "sources": sorted(x for x in graph if self.artifact(x)["type"] == "source"),
                "dependencies": sorted(graph - {aid}),
                "authority_evidence": [e for e in events if e["subject"] in graph],
                "grants": [e["evidence"] for e in events if e["type"] == "GRANT_ISSUED" and aid in self.closure(e["evidence"])],
                "supersessions": [e for e in events if e["type"] == "ARTIFACT_SUPERSEDED" and e["subject"] in graph],
                "journal_times": {str(rev): timestamp for rev, timestamp in self.db.execute("SELECT revision,recorded_at FROM journal")},
                "incomplete_reservations": [e["evidence"] for e in events if e["type"] == "DISPATCH_RESERVED"
                                           and not self._has(e["evidence"], "DISPATCH_COMPLETED")]}
