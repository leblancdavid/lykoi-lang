"""Prospective production adapter wiring around unchanged R5.86–88 authority."""
import copy
import hashlib

from air_compiler.parser import parse
from air_compiler.validator import validate
from lykoi_controller import Failure, canonical
from lykoi_pipeline import Pipeline, PipelineController, contracts, plans
from lykoi_pipeline.controller import ROOT, digest
from . import adapters, mappings, verification


def public_author_seed():
    import json
    source = json.loads((ROOT / "air/task_manager.json").read_text(encoding="utf-8"))
    source["scenarios"] = []  # public toolchain example, no scenario expected results
    return {"identity": "public-compiler-seed-1", "source": source}


class RehearsalController(PipelineController):
    def __init__(self, path, principals, *, model_configurations, author_seed, approved_plans=None):
        self.model_configurations = copy.deepcopy(model_configurations)
        self.approved_plans = copy.deepcopy(approved_plans or {})
        super().__init__(path, principals, author_fixture=author_seed)
        config = canonical({"models": self.model_configurations, "plans": self.approved_plans}).decode()
        self.db.execute("INSERT OR IGNORE INTO config VALUES ('public-rehearsal-1', ?)", (config,))
        if self.db.execute("SELECT value FROM config WHERE key='public-rehearsal-1'").fetchone()[0] != config:
            self.close()
            raise Failure("FREEZE_FAILURE", reason="Public service configuration substitution")

    def components(self):
        value = super().components()
        value["public_rehearsal"] = {"version": "public-rehearsal-1", "models": self.model_configurations,
                                     "prompts": adapters.PROMPTS, "registry": mappings.REGISTRY,
                                     "containment": verification.CONTAINMENT, "approved_plans": digest(self.approved_plans)}
        for path in ("src/lykoi_rehearsal/__init__.py", "src/lykoi_rehearsal/adapters.py", "src/lykoi_rehearsal/mappings.py",
                     "src/lykoi_rehearsal/service.py", "src/lykoi_rehearsal/verification.py", "src/lykoi_rehearsal/containment_worker.py",
                     "src/lykoi_rehearsal/freeze.py", "src/lykoi_rehearsal/invoke.py",
                     "rehearsal/public-capability-profile-1.json", "rehearsal/model-configurations-1.json", "rehearsal/semantic-qualification-1.json"):
            value["files"][path] = hashlib.sha256((ROOT / path).read_bytes()).hexdigest()
        value["author_adapter"] = adapters.VERSION
        return value

    def expected_plan(self, contract):
        plan = copy.deepcopy(self.approved_plans.get(digest(contract)))
        return verification.review(contract, plan if plan is not None else verification.produce(contract))

    def _native(self, aid):
        a = self.artifact(aid)
        d, value = a["dependencies"], a["content"]
        if a["schema"] == contracts.VERSION and a["type"] == "v1":
            self._native(d["adequacy"])
            if self.artifact(d["adequacy"])["dependencies"]["seal"] != d["seal"]:
                raise Failure("DEPENDENCY_MISMATCH")
            _, contract = self.what(d["seal"])
            if value != mappings.project(contract):
                raise Failure("NATIVE_EVIDENCE_MISMATCH", stage="v1")
            return
        if a["schema"] == contracts.VERSION and a["type"] == "model":
            self.check_bundle(d["bundle"])
            freeze = self.artifact(d["grant"])["dependencies"]["freeze"]
            if not self.applicable(d["grant"], d["bundle"], freeze)["applicable"]:
                raise Failure("GRANT_DENIAL")
            if (set(value) != {"source", "source_identity", "run", "author_adapter", "isolation", "receipt"}
                    or value["source_identity"] != digest(value["source"])
                    or value["author_adapter"] != adapters.VERSION
                    or value["run"] != self.artifact(d["bundle"])["content"]["manifest"]["run"]
                    or value["receipt"]["output_identity"] != digest({"source": value["source"]})
                    or value["receipt"]["input_identity"] != digest(self.artifact(d["bundle"])["content"]["author_input"])
                    or value["receipt"]["instruction_identity"] != digest(adapters.PROMPTS["author"])
                    or value["receipt"]["role"] != "author"
                    or value["receipt"]["configuration_identity"] != digest(self.model_configurations["roles"]["author"])):
                raise Failure("AUTHORING_FAILURE")
            return
        return super()._native(aid)


class RehearsalPipeline(Pipeline):
    def __init__(self, controller, project, credentials, author_adapter, *, mode="PUBLIC_REHEARSAL", candidate=None, activation=None):
        super().__init__(controller, project, credentials)
        self.author_adapter = author_adapter
        if mode not in {"PUBLIC_REHEARSAL", "CALIBRATION"}:
            raise Failure("PUBLIC_REHEARSAL_INELIGIBLE", reason="Unknown mode")
        self.mode, self.candidate, self.activation = mode, copy.deepcopy(candidate), copy.deepcopy(activation)
        if author_adapter.role != "author" or author_adapter.config != controller.model_configurations["roles"]["author"]:
            raise Failure("FREEZE_FAILURE", reason="Author configuration mismatch")
        self._infrastructure()

    def _infrastructure(self):
        if self.mode == "PUBLIC_REHEARSAL":
            from .freeze import eligibility
            check = eligibility(self.candidate or {}, activation=self.activation, controller=self.c)
            if not check["eligible"] or self.author_adapter.transport is not None:
                raise Failure("PUBLIC_REHEARSAL_INELIGIBLE", evidence=check)

    def prepare(self, seal, run, *, review_rationale):
        self._infrastructure()  # Requirement-blind check precedes WHAT consumption.
        fid, contract = self.c.what(seal)
        if self.mode == "PUBLIC_REHEARSAL":
            approval = self.c.artifact(self.c.artifact(seal)["dependencies"]["approval"])
            soi = self.c.artifact(self.c.artifact(approval["dependencies"]["coverage"])["dependencies"]["soi"])
            formal = self.c.artifact(fid)["content"].get("producer", {})
            review = soi["content"].get("producer", {})
            for role, producer in (("formalizer", formal), ("reviewer", review)):
                receipt = producer.get("provenance", {})
                if (receipt.get("execution") != "LIVE_HTTPS" or receipt.get("role") != role
                        or receipt.get("configuration_identity") != digest(self.c.model_configurations["roles"][role])
                        or receipt.get("instruction_identity") != digest(adapters.PROMPTS[role])
                        or receipt.get("source_identity") != self.c.artifact(fid)["dependencies"]["source"]):
                    raise Failure("SEMANTIC_PRODUCER_UNQUALIFIED", role=role)
            if not formal.get("session") or formal.get("session") == review.get("session"):
                raise Failure("SHARED_PRODUCER_CONTEXT")
        result = {"seal": seal, "frc": fid, "run": run, "mode": self.mode}
        try:
            freeze = self.reg("controller", "freeze", self.c.components())
            result["freeze"] = freeze
            self.check(freeze)
            structural = self.reg("formalizer", "structural", contracts.structural(contract, fid), frc=fid)
            result["structural"] = structural
            self.check(structural)
            receipt = self.reg("reviewer", "structural_receipt", contracts.coverage(contract, self.c.artifact(structural)["content"]), seal=seal, structural=structural)
            result["structural_receipt"] = receipt
            self.check(receipt)
            self.review(structural, review_rationale)
            self.review(receipt, review_rationale)
            bdi = self.reg("mechanical", "bdi", contracts.bdi(contract, self.c.artifact(structural)["content"]), seal=seal, structural_receipt=receipt, freeze=freeze)
            result["bdi"] = bdi
            self.check(bdi)
            adequate = self.reg("mechanical", "adequacy", contracts.adequate(contract, self.c.artifact(bdi)["content"]), seal=seal, bdi=bdi, structural_receipt=receipt, freeze=freeze)
            result["adequacy"] = adequate
            self.check(adequate)
            self.review(adequate, review_rationale)
            projected = mappings.project(contract)
            v1 = self.reg("formalizer", "v1", projected, seal=seal, adequacy=adequate)
            result["v1"] = v1
            self.check(v1)
            self.review(v1, review_rationale)
            plan = self.reg("verifier", "plan", self.c.expected_plan(contract), seal=seal, freeze=freeze, structural_receipt=receipt, bdi=bdi, adequacy=adequate, v1=v1)
            result["plan"] = plan
            self.check(plan)
            self.review(plan, review_rationale)
            plan_seal = self.call("verification_authority", "seal_plan", subject=plan)
            result["plan_seal"] = plan_seal
            manifest = {"version": contracts.VERSION, "frc": fid, "what_seal": seal, "structural": structural,
                        "structural_receipt": receipt, "bdi": bdi, "adequacy": adequate, "v1": v1,
                        "plan_seal": plan_seal, "components": freeze, "run": run, "fixture": digest(self.c.author_fixture)}
            author_input = {"version": contracts.VERSION, "run": run, "v1": projected["normalized"],
                            "toolchain": {"compiler": "0.3.0", "semantics": "axiom-0.3"}, "fixture": copy.deepcopy(self.c.author_fixture)}
            bundle = self.reg("formalizer", "bundle", {"manifest": manifest, "author_input": author_input}, v1=v1, adequacy=adequate, plan_seal=plan_seal, freeze=freeze)
            result["bundle"] = bundle
            self.check(bundle)
            result["grant"] = self.call("controller", "grant", subject=bundle)
            result["outcome"] = "IMPLEMENTATION_AUTHORIZED"
        except Failure as exc:
            result.update(outcome=exc.code, failure=exc.as_dict())
            self.record_halt(result)
        return result

    def author(self, bundle, grant, freeze):
        self._infrastructure()
        if not self.c.applicable(grant, bundle, freeze)["applicable"]:
            raise Failure("GRANT_DENIAL")
        reservation = self.call("author", "reserve", subject=bundle, grant=grant, freeze=freeze)
        self.c.check_freeze(freeze)
        request = self.c.artifact(bundle)["content"]["author_input"]
        output = self.author_adapter.produce(request)
        try:
            validate(parse(canonical(output["source"]).decode()))
        except (ValueError, KeyError, TypeError) as exc:
            raise Failure("AUTHOR_CAPABILITY_FAILURE", reason=str(exc)) from None
        self.c.check_freeze(freeze)
        content = {"source": output["source"], "source_identity": digest(output["source"]), "run": request["run"],
                   "author_adapter": adapters.VERSION, "isolation": self.author_adapter.isolation,
                   "receipt": copy.deepcopy(self.author_adapter.receipts[-1])}
        model = self.reg("author", "model", content, bundle=bundle, grant=grant)
        self.check(model)
        self.call("author", "complete", subject=reservation, output=model)
        return model

    def verify(self, target, plan_seal, freeze):
        self._infrastructure()
        self.c.check_freeze(freeze)
        self.c._native(target)  # Only deterministic compiler output can execute.
        plan_id = self.c.artifact(plan_seal)["dependencies"]["plan"]
        outcome, observations = verification.execute(self.c.artifact(target)["content"]["target_source"], self.c.artifact(plan_id)["content"])
        self.c.check_freeze(freeze)
        result = self.reg("verifier", "verification", {"outcome": outcome, "target": target, "plan": plan_id,
                          "verifier": plans.VERSION, "bundle": {"target": target, "plan_seal": plan_seal}, "cases": observations,
                          "unresolved": [], "isolation": verification.CONTAINMENT}, target=target, plan_seal=plan_seal, freeze=freeze)
        self.check(result)
        self.call("verifier", "bind_verification", subject=result)
        return result
