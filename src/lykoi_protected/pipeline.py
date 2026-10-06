"""Protected handoffs around the unchanged semantic back half."""
import copy

from air_compiler.parser import parse
from air_compiler.validator import validate
from lykoi_controller import Failure, canonical
from lykoi_pipeline.controller import digest
from lykoi_rehearsal import adapters
from .compatibility import service


class ProtectedPipeline(service.RehearsalPipeline):
    def __init__(self, *args, authorization, source_identity, run, **kwargs):
        self.authorization, self.source_identity, self.run = authorization, source_identity, run
        super().__init__(*args, mode="CALIBRATION", **kwargs)
        self.mode = "PROTECTED_EVALUATION"

    def _infrastructure(self):
        self.c.authorization(self.authorization, self.project, self.source_identity, self.run)

    def deliver(self, role, subject, session):
        return self.call(role, "protected_deliver", subject=subject, authorization=self.authorization,
                         source_identity=self.source_identity, run=self.run, recipient_role=role, session=session)

    def prepare(self, seal, run, **kwargs):
        self._infrastructure()
        if run != self.run or self.c.protected_origin(seal) != self.authorization:
            raise Failure("PROTECTED_RUN_MISMATCH")
        # Deterministic WHAT-side verifier sees formal input at plan preparation,
        # not original prose. Its request/receipt is separately accounted.
        fid, _ = self.c.what(seal)
        self.deliver("verifier", fid, run + ":verification-plan")
        result = super().prepare(seal, run, **kwargs)
        if result["outcome"] != "IMPLEMENTATION_AUTHORIZED":
            self.finish(result["outcome"])
        return result

    def author(self, bundle, grant, freeze):
        self._infrastructure()
        if not self.c.applicable(grant, bundle, freeze)["applicable"]:
            raise Failure("GRANT_DENIAL")
        reservation = self.call("author", "reserve", subject=bundle, grant=grant, freeze=freeze)
        self.c.check_freeze(freeze)
        request = self.deliver("author", bundle, self.author_adapter.session)
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
        self.deliver("verifier", target, self.run + ":verification-executor")
        self.deliver("verifier", plan_seal, self.run + ":verification-executor")
        return super().verify(target, plan_seal, freeze)

    def finish(self, outcome):
        return self.call("controller", "protected_terminal", authorization=self.authorization,
                         source_identity=self.source_identity, run=self.run, outcome=outcome)

    def execute(self, prepared):
        result = super().execute(prepared)
        if prepared["outcome"] == "IMPLEMENTATION_AUTHORIZED":
            self.finish(result["outcome"])
        return result
