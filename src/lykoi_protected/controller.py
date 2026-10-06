"""Exact protected authority, durable opening reservation and disclosure ledger.

artifact()/db are trusted service APIs, never worker capabilities. Every worker
disclosure uses protected_deliver. A custodian callback is trusted to implement
the declared open; it is not a path supplied by a worker.
"""
import copy

from lykoi_controller import Failure, canonical
from lykoi_controller.controller import identity
from lykoi_pipeline.controller import digest
from . import VERSION, PURPOSE, CLASSIFICATION
from .compatibility import service, frc
from .freeze import integrity
from .policy import POLICY, COUNTERS


class ProtectedController(service.RehearsalController):
    def __init__(self, path, principals, *, candidate, **kwargs):
        self.candidate = copy.deepcopy(candidate)
        super().__init__(path, principals, **kwargs)
        pin = canonical({"candidate": candidate["identity"], "policy": POLICY}).decode()
        self.db.execute("INSERT OR IGNORE INTO config VALUES ('protected-r5.94', ?)", (pin,))
        if self.db.execute("SELECT value FROM config WHERE key='protected-r5.94'").fetchone()[0] != pin:
            self.close()
            raise Failure("PROTECTED_FREEZE_SUBSTITUTION")

    def components(self):
        value = super().components()
        value["protected"] = {"version": VERSION, "candidate": self.candidate["identity"], "policy": POLICY}
        value["files"].update(self.candidate["files"])
        return value

    def _put(self, kind, project, content, deps, actor, schema="authority-1"):
        if kind == "context" and "controller" in self.principals[actor]["roles"]:
            envelope = {"type": kind, "schema": schema, "serializer": "CJ-1", "digest_algorithm": "sha256",
                        "project": project, "content": content, "dependencies": dict(deps)}
            aid = identity(envelope)
            if not self.db.execute("SELECT 1 FROM artifacts WHERE id=?", (aid,)).fetchone():
                self.db.execute("INSERT INTO artifacts VALUES (?, ?)", (aid, canonical(envelope).decode()))
                self._event("ARTIFACT_REGISTERED", aid, actor, "controller", "CANDIDATE")
            return aid
        if kind == "source" and "context" in deps:
            c = self.artifact(deps["context"])["content"]
            if c.get("version") == VERSION and "source_identity" in c:
                content = {**content, "classification": CLASSIFICATION,
                           "protected_identity": c["source_identity"], "authorization": deps["context"]}
        return super()._put(kind, project, content, deps, actor, schema)

    def check_freeze(self, freeze):
        self.require_active()
        return super().check_freeze(freeze)

    def check_bundle(self, aid):
        origin = self.protected_origin(aid)
        if origin:
            c = self.artifact(origin)["content"]
            self.authorization(origin, self.artifact(aid)["project"], c["source_identity"], c["run"])
        return super().check_bundle(aid)

    def _subject(self, subject, project, kind=None):
        a = super()._subject(subject, project, kind)
        origin = self.protected_origin(subject)
        if origin:
            c = self.artifact(origin)["content"]
            self.authorization(origin, project, c["source_identity"], c["run"])
        return a

    def require_active(self, project=None):
        if not (getattr(self, "_in_dispatch", False) and getattr(self, "_candidate_checked", False)):
            if not integrity(self.candidate):
                raise Failure("PROTECTED_FREEZE_DRIFT")
            if getattr(self, "_in_dispatch", False):
                self._candidate_checked = True
        active = [e for e in self.events() if e["type"] == "PROTECTED_ACTIVATED"]
        if len(active) != 1:
            raise Failure("PROTECTED_ACTIVATION_REQUIRED")
        a = self.artifact(active[0]["subject"])
        self._fresh(active[0]["subject"])
        if project is not None and a["project"] != project:
            raise Failure("PROTECTED_SCOPE_DENIED")
        return active[0]["subject"]

    def execute(self, credential, project, command, *, expected_revision, **args):
        # One physical-byte verification per atomic dispatch; native checks can
        # recursively revisit the same freeze hundreds of times in that dispatch.
        self._in_dispatch, self._candidate_checked = True, False
        try:
            return self._execute(credential, project, command, expected_revision=expected_revision, **args)
        finally:
            self._in_dispatch, self._candidate_checked = False, False

    def _execute(self, credential, project, command, *, expected_revision, **args):
        if not command.startswith("protected_"):
            return super().execute(credential, project, command, expected_revision=expected_revision, **args)
        actor = "unattributed"
        self.db.execute("BEGIN IMMEDIATE")
        try:
            actor = self._actor(credential, project)
            if self.revision != expected_revision:
                raise Failure("REVISION_RACE")
            allowed = {"protected_activate", "protected_authorize", "protected_reserve",
                       "protected_read", "protected_admit", "protected_incomplete", "protected_deliver", "protected_terminal"}
            if command not in allowed:
                raise Failure("PROTECTED_SCOPE_DENIED")
            try:
                result = getattr(self, "_" + command)(actor, project, **args)
            except (KeyError, TypeError, ValueError):
                raise Failure("MALFORMED_PROTECTED_REQUEST") from None
            self.db.execute("COMMIT")
            return result
        except Failure as exc:
            self.db.execute("ROLLBACK")
            self.db.execute("BEGIN IMMEDIATE")
            self._event("PROTECTED_DENIED", None, actor, "controller", "UNCHANGED",
                        evidence={"command": command, "source_identity": args.get("source_identity"),
                                  "authorization": args.get("authorization")}, reason=exc.as_dict())
            self.db.execute("COMMIT")
            raise
        except Exception:
            self.db.execute("ROLLBACK")
            raise

    def _record(self, actor, project, content):
        # Internal controller-owned context records; callers cannot create these
        # via ordinary context registration and thereby acquire authority.
        return self._put("context", project, {"version": VERSION, **content}, {}, actor)

    def _protected_activate(self, actor, project, purpose, candidate_identity):
        self._role(actor, {"owner"})
        if (purpose != PURPOSE or candidate_identity != self.candidate["identity"]
                or not integrity(self.candidate) or any(e["type"] == "PROTECTED_ACTIVATED" for e in self.events())):
            raise Failure("PROTECTED_ACTIVATION_DENIED")
        if self.model_configurations != self.candidate["models"] or self.approved_plans:
            raise Failure("PROTECTED_CONFIGURATION_DRIFT")
        roles = {r: {a for a, p in self.principals.items() if r in p["roles"]}
                 for r in ("admission", "formalizer", "reviewer", "author", "verifier", "verification_authority")}
        if (any(not a for a in roles.values()) or roles["formalizer"] & roles["reviewer"]
                or any(roles["author"] & roles[r] for r in roles if r != "author")):
            raise Failure("PROTECTED_ROLE_SEPARATION_FAILURE")
        from lykoi_rehearsal.service import public_author_seed
        if self.author_fixture != public_author_seed():
            raise Failure("PROTECTED_CONFIGURATION_DRIFT")
        aid = self._record(actor, project, {"purpose": purpose, "candidate_identity": candidate_identity})
        self._event("PROTECTED_ACTIVATED", aid, actor, "owner", "ACTIVE")
        return aid

    def _protected_authorize(self, actor, project, source_identity, run, policy_identity, clarification):
        self._role(actor, {"owner"})
        active = self.require_active(project)
        if (type(source_identity) is not str or not source_identity.strip() or type(run) is not str or not run.strip()
                or policy_identity != digest(POLICY)):
            raise Failure("PROTECTED_AUTHORIZATION_SCOPE_DENIED")
        if (type(clarification) is not dict or set(clarification) != {"mode", "principal"}
                or clarification["mode"] not in {"HUMAN_AVAILABLE", "UNAVAILABLE_TERMINATE", "PREAUTHORIZED_AUTHORITY"}):
            raise Failure("PROTECTED_CLARIFICATION_POLICY_REQUIRED")
        principal = clarification["principal"]
        if clarification["mode"] == "UNAVAILABLE_TERMINATE":
            if principal is not None:
                raise Failure("PROTECTED_CLARIFICATION_POLICY_REQUIRED")
        elif (principal not in self.principals or "owner" not in self.principals[principal]["roles"]
              or project not in self.principals[principal]["projects"]):
            raise Failure("PROTECTED_CLARIFICATION_AUTHORITY_REQUIRED")
        for e in self.events():
            if e["type"] == "PROTECTED_AUTHORIZED":
                old = self.artifact(e["subject"])["content"]
                if old["source_identity"] == source_identity or old["run"] == run:
                    raise Failure("PROTECTED_SINGLE_EVALUATION_ONLY")
        aid = self._record(actor, project, {"source_identity": source_identity, "run": run,
                           "activation": active, "candidate_identity": self.candidate["identity"],
                           "policy_identity": policy_identity, "clarification": clarification})
        self._event("PROTECTED_AUTHORIZED", aid, actor, "owner", "AUTHORIZED_NOT_ACCESSED")
        return aid

    def authorization(self, authorization, project, source_identity, run, *, terminal=False):
        active = self.require_active(project)
        a = self._subject(authorization, project, "context")
        self._need(authorization, "PROTECTED_AUTHORIZED")
        c = a["content"]
        if (c["activation"] != active or c["candidate_identity"] != self.candidate["identity"]
                or c["policy_identity"] != digest(POLICY) or c["source_identity"] != source_identity or c["run"] != run):
            raise Failure("PROTECTED_AUTHORIZATION_MISMATCH")
        self._fresh(active)
        if not terminal and self._has(authorization, "PROTECTED_TERMINAL"):
            raise Failure("PROTECTED_EVALUATION_TERMINAL")
        return c

    def _protected_reserve(self, actor, project, authorization, source_identity, run):
        self._role(actor, {"admission"})
        self.authorization(authorization, project, source_identity, run)
        if self._has(authorization, "PROTECTED_OPEN_RESERVED"):
            raise Failure("PROTECTED_OPEN_ALREADY_RESERVED")
        self._event("PROTECTED_OPEN_RESERVED", authorization, actor, "admission", "RESERVED",
                    evidence={"source_identity": source_identity, "run": run})
        return authorization

    def _protected_admit(self, actor, project, authorization, source_identity, run, text, session):
        self._role(actor, {"admission"})
        self._role(actor, {"owner"})
        self.authorization(authorization, project, source_identity, run)
        self._need(authorization, "PROTECTED_OPEN_RESERVED")
        self._need(authorization, "PROTECTED_SOURCE_READ")
        read = next(e for e in self.events() if e["subject"] == authorization and e["type"] == "PROTECTED_SOURCE_READ")
        if read["evidence"]["content_identity"] != digest(text):
            raise Failure("PROTECTED_SOURCE_CONTENT_SUBSTITUTION")
        if self._has(authorization, "PROTECTED_SOURCE_ADMITTED"):
            raise Failure("PROTECTED_SOURCE_ALREADY_ADMITTED")
        reserved = next(e for e in self.events() if e["subject"] == authorization and e["type"] == "PROTECTED_OPEN_RESERVED")
        if reserved["actor"] != actor or type(text) is not str or not text.strip() or session != run:
            raise Failure("PROTECTED_ADMISSION_MISMATCH")
        message = self._put("message", project, {"workspace": session, "text": text, "version": 1,
                            "classification": CLASSIFICATION, "provenance": "human_statement"}, {}, actor)
        self._adopt(actor, project, message)
        source = self._put("source", project, {"workspace": session, "classification": CLASSIFICATION,
                           "protected_identity": source_identity, "authorization": authorization,
                           "provenance": "human_statement"}, {"message": message, "context": authorization}, actor)
        self._adopt(actor, project, authorization)
        self._adopt(actor, project, source)
        self._event("PROTECTED_SOURCE_ADMITTED", authorization, actor, "admission", "SOURCE_ADMITTED",
                    evidence={"source": source, "message": message, "source_identity": source_identity})
        return source

    def _protected_read(self, actor, project, authorization, source_identity, run, text):
        self._role(actor, {"admission"})
        self.authorization(authorization, project, source_identity, run)
        self._need(authorization, "PROTECTED_OPEN_RESERVED")
        reserved = next(e for e in self.events() if e["subject"] == authorization and e["type"] == "PROTECTED_OPEN_RESERVED")
        if reserved["actor"] != actor or self._has(authorization, "PROTECTED_SOURCE_READ") or type(text) is not str:
            raise Failure("PROTECTED_READ_MISMATCH")
        self._event("PROTECTED_SOURCE_READ", authorization, actor, "admission", "SOURCE_READ",
                    evidence={"content_identity": digest(text), "source_identity": source_identity})
        return authorization

    def _protected_incomplete(self, actor, project, authorization, source_identity, run):
        self._role(actor, {"admission"})
        self.authorization(authorization, project, source_identity, run)
        self._need(authorization, "PROTECTED_OPEN_RESERVED")
        self._event("PROTECTED_TERMINAL", authorization, actor, "admission", "INCOMPLETE")

    def protected_origin(self, aid):
        origins = {self.artifact(x)["content"]["authorization"] for x in self.closure(aid)
                   if self.artifact(x)["type"] == "source" and "authorization" in self.artifact(x)["content"]}
        if len(origins) > 1:
            raise Failure("PROTECTED_SOURCE_SET_MISMATCH")
        return next(iter(origins), None)

    def _protected_deliver(self, actor, project, subject, authorization, source_identity, run, recipient_role, session):
        role = recipient_role
        c = self.authorization(authorization, project, source_identity, run)
        self._role(actor, {role})
        a = self._subject(subject, project)
        if not session or self.protected_origin(subject) != authorization:
            raise Failure("PROTECTED_DELIVERY_SCOPE_DENIED")
        kind = a["type"]
        if role in {"formalizer", "reviewer"} and kind == "source":
            result = copy.deepcopy(a)
        elif role == "author" and kind == "bundle":
            self.check_bundle(subject)
            self._need(subject, "GRANT_ISSUED")
            grant = next(e["evidence"] for e in self.events() if e["type"] == "GRANT_ISSUED" and e["subject"] == subject)
            self._need(grant, "DISPATCH_RESERVED")
            reservation = next(e["evidence"] for e in self.events() if e["subject"] == grant and e["type"] == "DISPATCH_RESERVED")
            if self.artifact(reservation)["content"]["actor"] != actor or a["content"]["manifest"]["run"] != run:
                raise Failure("PROTECTED_DELIVERY_SCOPE_DENIED")
            result = copy.deepcopy(a["content"]["author_input"])
        elif role in POLICY["formal"] and kind not in {"message", "source", "answer", "question", "context", "bundle"}:
            if role in {"verifier", "verification_authority"} and kind not in {"frc", "v1", "plan", "plan_seal", "target", "verification"}:
                raise Failure("PROTECTED_VISIBILITY_DENIED")
            if role == "reviewer" and any(self.artifact(x)["type"] == "frc" for x in self.closure(subject)):
                inventories = [x for x in self.closure(subject) if self.artifact(x)["type"] == "source"]
                if not any(e["type"] == "SOI_COMMITTED" and self.artifact(e["subject"])["dependencies"]["source"] in inventories
                           for e in self.events()):
                    raise Failure("PROTECTED_SOI_COMMITMENT_REQUIRED")
            result = copy.deepcopy(a)
            if role in {"verifier", "verification_authority", "mechanical"} and kind == "frc":
                # Return only the existing formal WHAT-side representation; the
                # service's native checks retain the full protected contract.
                contract = result["content"]["contract"]
                contract["source"] = {k: v for k, v in contract["source"].items() if k != "text"}
                for obligation in contract["obligations"]:
                    obligation.pop("source_quote", None)
                result["content"] = {"contract": contract}
        else:
            raise Failure("PROTECTED_VISIBILITY_DENIED")
        self._event("PROTECTED_DELIVERED", authorization, actor, role,
                    {"formalizer": "FORMALIZATION_EXPOSED", "reviewer": "REVIEW_EXPOSED",
                     "author": "AUTHOR_EXPOSED", "verifier": "VERIFICATION_EXPOSED"}.get(role, "FORMAL_ARTIFACT_EXPOSED"),
                    evidence={"artifact": subject, "session": session, "kind": kind,
                              "representation": "RAW_SOURCE" if kind == "source" else "DERIVED_FORMAL"})
        return result

    def _protected_terminal(self, actor, project, authorization, source_identity, run, outcome):
        self._role(actor, {"controller"})
        self.authorization(authorization, project, source_identity, run)
        self._event("PROTECTED_TERMINAL", authorization, actor, "controller", outcome)
        return outcome

    def ledger(self, source_identity):
        counts = dict.fromkeys(COUNTERS, 0)
        authorizations = {e["subject"] for e in self.events() if e["type"] == "PROTECTED_AUTHORIZED"
                          and self.artifact(e["subject"])["content"]["source_identity"] == source_identity}
        states, receipts = ["PRISTINE"], []
        for e in self.events():
            if e["subject"] not in authorizations:
                if e["type"] == "PROTECTED_DENIED" and e["evidence"].get("source_identity") == source_identity:
                    counts["denials"] += 1
                continue
            if not e["type"].startswith("PROTECTED_"):
                continue
            receipts.append(e)
            if e["type"] == "PROTECTED_AUTHORIZED":
                counts["authorizations"] += 1
            elif e["type"] == "PROTECTED_OPEN_RESERVED":
                counts["open_attempts"] += 1
            elif e["type"] == "PROTECTED_SOURCE_READ":
                counts["source_opens"] += 1
                counts["source_reads"] += 1
            elif e["type"] == "PROTECTED_SOURCE_ADMITTED":
                counts["source_admissions"] += 1
            elif e["type"] == "PROTECTED_DELIVERED":
                key = e["role"] + "_exposures"
                if key in counts:
                    counts[key] += 1
            if e["state"] not in states:
                states.append(e["state"])
        return {"source_identity": source_identity, "counters": counts, "observed_states": states,
                "receipts": receipts, "pristine": counts["source_reads"] == 0,
                "development_knowledge": "AUTHORIZED_DERIVED_EXPOSURE" if counts["author_exposures"] else "UNEXPOSED"}

    def _register(self, actor, project, kind, content, dependencies=None, schema="authority-1"):
        # A protected controller cannot be used as an unguarded public workflow.
        self.require_active(project)
        if kind in {"message", "source"}:
            raise Failure("PROTECTED_CUSTODIAN_ADMISSION_REQUIRED")
        if kind in {"answer", "question"}:
            origin = self.protected_origin((dependencies or {})["source"])
            c = self.artifact(origin)["content"]
            if kind == "answer" and (c["clarification"]["mode"] == "UNAVAILABLE_TERMINATE" or c["clarification"]["principal"] != actor):
                raise Failure("PROTECTED_CLARIFICATION_UNAVAILABLE")
        if kind == "frc":
            frc.validate(content["contract"])
            if content["contract"]["source"]["classification"] != CLASSIFICATION:
                raise Failure("PROTECTED_PROVENANCE_LOSS")
            source = self.artifact((dependencies or {})["source"])
            message = self.artifact(source["dependencies"]["message"])
            record = content["contract"]["source"]
            if record["id"] != (dependencies or {})["source"] or record["text"] != message["content"]["text"]:
                raise Failure("PROTECTED_SOURCE_CONTENT_SUBSTITUTION")
        deps = dependencies or {}
        for dep in deps.values():
            origin = self.protected_origin(dep)
            if origin:
                c = self.artifact(origin)["content"]
                self.authorization(origin, project, c["source_identity"], c["run"])
                if kind == "bundle" and content["manifest"]["run"] != c["run"]:
                    raise Failure("PROTECTED_RUN_MISMATCH")
        return super()._register(actor, project, kind, content, dependencies, schema)
