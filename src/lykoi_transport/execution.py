"""Process-local qualification and neutral controller/worker wiring."""
import copy

from lykoi_controller import Failure
from lykoi_freeze.execution import CrossMachineProtectedController as HistoricalController
from lykoi_protected.controller import ProtectedController
from lykoi_protected.compatibility import view
from lykoi_runtime.verify import provenance
from . import CONTRACT
from .freeze import preflight, verify_content, VERSION

private = view("src/lykoi_protected/controller.py", bindings={
    "integrity": lambda candidate: verify_content(candidate, candidate["identity"])["passed"]})


class ExecutionGuard:
    def __init__(self, candidate, expected_identity, transport, regression):
        self.candidate = copy.deepcopy(candidate)
        self.expected_identity, self.transport, self.regression = expected_identity, transport, regression
        self.requalify()

    def requalify(self):
        result = preflight(self.candidate, self.expected_identity, self.transport, regression=self.regression)
        if not result["eligible"]:
            raise Failure("MACHINE_INELIGIBLE", evidence=result)
        self.actual = {"python": provenance(), "transport": self.transport.provenance()}
        if (self.actual["python"] != result["python"]["provenance"]
                or self.actual["transport"] != result["transport"]["provenance"]):
            raise Failure("IMPLEMENTATION_DRIFT_DURING_QUALIFICATION")
        self.qualification = result

    def ensure(self):
        content = verify_content(self.candidate, self.expected_identity)
        if not content["passed"]:
            raise Failure("PROTECTED_FREEZE_DRIFT", evidence=content)
        actual = {"python": provenance(), "transport": self.transport.provenance()}
        if actual != self.actual:
            self.requalify()
        return copy.deepcopy(self.actual)


class NeutralProtectedController(HistoricalController):
    _protected_activate = private.ProtectedController._protected_activate

    def __init__(self, *args, candidate, expected_identity, transport, regression, **kwargs):
        self.machine = ExecutionGuard(candidate, expected_identity, transport, regression)
        if kwargs.get("model_configurations") != candidate["models"]:
            raise Failure("PROTECTED_CONFIGURATION_DRIFT")
        ProtectedController.__init__(self, *args, candidate=candidate, **kwargs)

    def _check_candidate_binding(self):
        content = verify_content(self.candidate, self.machine.expected_identity)
        if not content["passed"]:
            raise Failure("PROTECTED_FREEZE_DRIFT", evidence=content)

    def require_active(self, project=None):
        if not (getattr(self, "_in_dispatch", False) and getattr(self, "_candidate_checked", False)):
            self._check_candidate_binding()
            self.machine.ensure()
        return private.ProtectedController.require_active(self, project)

    def components(self):
        value = super().components()
        value["protected"]["version"] = VERSION
        value["tools"] = {"python_contract": "PYTHON_RUNTIME_CONTRACT_V1", "ai_worker_transport_contract": CONTRACT}
        return value
