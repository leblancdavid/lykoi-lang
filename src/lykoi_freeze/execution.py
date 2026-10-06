"""Process-local machine qualification and prospective controller/worker wiring."""
import copy
import platform
import sys

from lykoi_controller import Failure
from lykoi_pipeline.controller import digest
from lykoi_protected.controller import ProtectedController
from lykoi_protected.compatibility import view, service
from lykoi_protected.policy import POLICY
from lykoi_protected.adapter import SourceProvenance
from lykoi_rehearsal.opencode_adapter import OpenCodeAdapter
from lykoi_runtime.verify import provenance
from .freeze import preflight, verify_content
from .opencode import tool_provenance, runtime_config


class ExecutionGuard:
    def __init__(self, candidate, expected_identity, executable):
        self.candidate = copy.deepcopy(candidate)
        self.expected_identity, self.executable = expected_identity, str(executable)
        self.requalify()

    def requalify(self):
        check = preflight(self.candidate, self.expected_identity, self.executable, sys.executable)
        if not check["eligible"]:
            raise Failure("MACHINE_INELIGIBLE", evidence=check)
        actual = {"python": provenance(), "opencode": tool_provenance(self.executable)}
        if actual["python"] != check["python"]["provenance"] or actual["opencode"] != check["opencode"]["provenance"]:
            raise Failure("IMPLEMENTATION_DRIFT_DURING_QUALIFICATION")
        self.qualification, self.actual = check, actual

    def ensure(self):
        content = verify_content(self.candidate, self.expected_identity)
        if not content["passed"]:
            raise Failure("PROTECTED_FREEZE_DRIFT", evidence=content)
        try:
            actual = {"python": provenance(), "opencode": tool_provenance(self.executable)}
        except (OSError, ValueError) as exc:
            raise Failure("MACHINE_INELIGIBLE", reason=type(exc).__name__) from None
        if actual != self.actual:
            self.requalify()
        return copy.deepcopy(self.actual)


def _content_intact(candidate):
    return verify_content(candidate, candidate["identity"])["passed"]


private = view("src/lykoi_protected/controller.py", bindings={"integrity": _content_intact})


class CrossMachineProtectedController(ProtectedController):
    _protected_activate = private.ProtectedController._protected_activate

    def __init__(self, *args, candidate, expected_identity, executable, **kwargs):
        self.machine = ExecutionGuard(candidate, expected_identity, executable)
        if kwargs.get("model_configurations") != candidate["models"]:
            raise Failure("PROTECTED_CONFIGURATION_DRIFT")
        super().__init__(*args, candidate=candidate, **kwargs)

    def require_active(self, project=None):
        if not (getattr(self, "_in_dispatch", False) and getattr(self, "_candidate_checked", False)):
            self._check_candidate_binding()
            self.machine.ensure()
        return private.ProtectedController.require_active(self, project)

    def _check_candidate_binding(self):
        # The working controller copy must remain bound to the independently
        # approved identity, not just the guard's separately retained copy.
        content = verify_content(self.candidate, self.machine.expected_identity)
        if not content["passed"]:
            raise Failure("PROTECTED_FREEZE_DRIFT", evidence=content)

    def components(self):
        value = service.RehearsalController.components(self)
        value["protected"] = {"version": "protected-portable-freeze-r5.94b-1", "candidate": self.machine.expected_identity, "policy": POLICY}
        value["files"] = {e["dependency"]: e["content_sha256"] for e in self.candidate["dependencies"]
                          if e["freeze_class"] == "CANONICAL_CONTENT_PIN" and "embedded_field" not in e}
        value["tools"] = {"python_contract": "PYTHON_RUNTIME_CONTRACT_V1", "opencode_contract": "OPENCODE_ADAPTER_CONTRACT_V1"}
        return value

    def execute(self, *args, **kwargs):
        self._check_candidate_binding()
        self.machine.ensure()
        return super().execute(*args, **kwargs)

    def _event(self, kind, subject, actor, role, state, evidence=None, reason=None):
        super()._event("MACHINE_EXECUTION_PROVENANCE", None, actor, role, "QUALIFIED",
                       evidence={"operation": kind, "operation_subject": subject, "candidate": self.machine.expected_identity,
                                 "operation_revision": self.revision + 2, "implementation": self.machine.actual,
                                 "os": {"system": platform.system(), "release": platform.release(), "machine": platform.machine()}})
        return super()._event(kind, subject, actor, role, state, evidence=evidence, reason=reason)


class QualifiedOpenCodeAdapter(OpenCodeAdapter):
    """Semantic configuration is independent of machine-selected transport path."""
    def __init__(self, role, config, guard):
        if config != guard.candidate["models"]["roles"][role]:
            raise Failure("PROTECTED_CONFIGURATION_DRIFT")
        self.machine = guard
        super().__init__(role, config)

    def _invoke(self, payload):
        before = self.machine.ensure()
        semantic = self.config
        self.config = runtime_config(semantic, self.machine.executable)
        try:
            result = super()._invoke(payload)
        finally:
            self.config = semantic
        if {"python": provenance(), "opencode": tool_provenance(self.machine.executable)} != before:
            raise Failure("IMPLEMENTATION_DRIFT_DURING_EXECUTION")
        return result

    def produce(self, request):
        self.machine.ensure()
        output = super().produce(request)
        self.receipts[-1]["machine_provenance"] = copy.deepcopy(self.machine.actual)
        self.receipts[-1]["os_provenance"] = {"system": platform.system(), "release": platform.release(), "machine": platform.machine()}
        self.receipts[-1]["semantic_configuration_identity"] = digest(self.config)
        self.provenance.update(self.receipts[-1])
        return output


class QualifiedProtectedOpenCodeAdapter(SourceProvenance, QualifiedOpenCodeAdapter):
    """Reuse R5.94 source commitment classification without changing its semantics."""
    pass
