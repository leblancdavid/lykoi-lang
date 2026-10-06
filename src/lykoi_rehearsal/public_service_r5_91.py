"""Prospective public-only admission gate around unchanged R5.86–89 machinery."""
import copy
import hashlib

from lykoi_controller import Failure, canonical
from lykoi_pipeline.controller import ROOT, digest
from . import adapters
from .opencode_adapter import OpenCodeAdapter, VERSION as ADAPTER, role_prompt
from .public_freeze_r5_91 import VERSION, PURPOSE, EXTRA, eligibility, integrity
from .service import RehearsalController, RehearsalPipeline

ACTIVATION = "public-rehearsal-activation-r5.91-1"


class PublicController(RehearsalController):
    def __init__(self, path, principals, *, candidate, **kwargs):
        self.public_candidate = copy.deepcopy(candidate)
        super().__init__(path, principals, **kwargs)
        pin = canonical({"purpose": PURPOSE, "candidate": candidate["identity"]}).decode()
        self.db.execute("INSERT OR IGNORE INTO config VALUES ('public-r5.91', ?)", (pin,))
        if self.db.execute("SELECT value FROM config WHERE key='public-r5.91'").fetchone()[0] != pin:
            self.close()
            raise Failure("FREEZE_FAILURE", reason="Public freeze substitution on restart")

    def components(self):
        value = super().components()
        value["public_rehearsal_r5_91"] = {"candidate": self.public_candidate["identity"],
                                          "adapter": ADAPTER, "purpose": PURPOSE}
        for path in EXTRA:
            value["files"][path] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        return value

    def _native(self, aid):
        super()._native(aid)
        artifact = self.artifact(aid)
        if artifact["type"] == "model":
            receipt = artifact["content"]["receipt"]
            if (receipt.get("execution") != "LIVE_OPENCODE_OAUTH" or receipt.get("adapter") != ADAPTER
                    or receipt.get("authority") != "UNTRUSTED_CANDIDATE"
                    or receipt.get("role_prompt_identity") != digest(role_prompt("author"))):
                raise Failure("AUTHORING_FAILURE", reason="Frozen live author provenance mismatch")

    def activation(self):
        for event in self.events():
            if event["type"] != "HUMAN_AUTHORIZED" or event["subject"] is None:
                continue
            a = self.artifact(event["subject"])
            if a["type"] == "context" and a["content"].get("version") == ACTIVATION:
                if a["content"] != {"version": ACTIVATION, "purpose": PURPOSE,
                                    "candidate_identity": self.public_candidate["identity"], "active": True}:
                    raise Failure("FREEZE_FAILURE", reason="Activation mismatch")
                self._fresh(a["id"] if "id" in a else event["subject"])
                recorded = self.db.execute("SELECT recorded_at FROM journal WHERE revision=?", (event["revision"],)).fetchone()[0]
                return {"artifact": event["subject"], "event_identity": event["event_identity"],
                        "revision": event["revision"], "recorded_at": recorded, **a["content"]}
        return None

    def require_active(self):
        check = eligibility(self.public_candidate, self)
        active = self.activation()
        if not check["eligible"] or not active:
            raise Failure("PUBLIC_REHEARSAL_INELIGIBLE", evidence=check, freeze_active=bool(active))
        return active

    def _register(self, actor, project, kind, content, dependencies=None, schema="authority-1"):
        # Gate at the controller's admission boundary, BEFORE storing source/message.
        # All requirements-wizard callers use this same controller boundary.
        if kind not in {"context", "freeze"}:
            self.require_active()
        if kind == "context" and isinstance(content, dict) and content.get("version") == ACTIVATION:
            self._role(actor, {"owner"})
            check = eligibility(self.public_candidate, self)
            if (not check["eligible"] or content != {"version": ACTIVATION, "purpose": PURPOSE,
                    "candidate_identity": self.public_candidate["identity"], "active": True}
                    or self.activation() or self.db.execute("SELECT 1 FROM artifacts WHERE json_extract(envelope,'$.type') IN ('message','source')").fetchone()):
                raise Failure("FREEZE_FAILURE", reason="Invalid/late/repeated public activation", evidence=check)
        return super()._register(actor, project, kind, content, dependencies, schema)

    def _adopt(self, actor, project, subject, evidence=None):
        a = self.artifact(subject)
        if a["type"] == "context" and a["content"].get("version") == ACTIVATION:
            if (not eligibility(self.public_candidate, self)["eligible"] or self.activation()
                    or a["content"].get("candidate_identity") != self.public_candidate["identity"]):
                raise Failure("FREEZE_FAILURE", reason="Public activation rejected")
        return super()._adopt(actor, project, subject, evidence)

    def prove_admission_order(self):
        active = self.require_active()
        admitted = [e for e in self.events() if e["type"] == "ARTIFACT_REGISTERED"
                    and self.artifact(e["subject"])["type"] in {"message", "source"}]
        return {"activation": active, "admission_revisions": [e["revision"] for e in admitted],
                "freeze_predates_every_admission": all(active["revision"] < e["revision"] for e in admitted),
                "no_requirement_admitted": not admitted}


class PublicPipeline(RehearsalPipeline):
    def __init__(self, controller, project, credentials, author_adapter):
        if type(author_adapter) is not OpenCodeAdapter:
            raise Failure("PUBLIC_REHEARSAL_INELIGIBLE", reason="Live configured adapter required")
        # Inherited CALIBRATION selects native machinery without historical R5.89
        # qualification policy. R5.91 authority comes from this controller gate.
        super().__init__(controller, project, credentials, author_adapter, mode="CALIBRATION")
        self.mode = "PUBLIC_REHEARSAL"
        self._infrastructure()

    def _infrastructure(self):
        self.c.require_active()

    def record_halt(self, result):
        result["mode"] = "PUBLIC_REHEARSAL"
        return super().record_halt(result)

    def prepare(self, seal, run, *, review_rationale):
        self._infrastructure()
        fid, _ = self.c.what(seal)
        approval = self.c.artifact(self.c.artifact(seal)["dependencies"]["approval"])
        soi = self.c.artifact(self.c.artifact(approval["dependencies"]["coverage"])["dependencies"]["soi"])
        formal = self.c.artifact(fid)["content"]["producer"]
        review = soi["content"]["producer"]
        for role, producer in (("formalizer", formal), ("reviewer", review)):
            receipt = producer["provenance"]
            if (receipt.get("execution") != "LIVE_OPENCODE_OAUTH" or receipt.get("adapter") != ADAPTER
                    or receipt.get("role") != role or receipt.get("authority") != "UNTRUSTED_CANDIDATE"
                    or receipt.get("configuration_identity") != digest(self.c.model_configurations["roles"][role])
                    or receipt.get("role_prompt_identity") != digest(role_prompt(role))
                    or receipt.get("source_identity") != self.c.artifact(fid)["dependencies"]["source"]):
                raise Failure("SEMANTIC_PRODUCER_UNQUALIFIED", role=role)
        if formal["session"] == review["session"] or formal["provenance"]["cli_session"] == review["provenance"]["cli_session"]:
            raise Failure("SHARED_PRODUCER_CONTEXT")
        # Reuse the exact R5.89 native back half, with the prospective policy checked
        # above. No mappings, analyses, verification rules or grants are substituted.
        self.mode = "CALIBRATION"
        try:
            result = super().prepare(seal, run, review_rationale=review_rationale)
        finally:
            self.mode = "PUBLIC_REHEARSAL"
        result["mode"] = self.mode
        return result
