"""Portable protected controller with process-local qualification and audit provenance."""
import sys

from lykoi_controller import Failure
from lykoi_runtime.verify import contract_pin, provenance, verify_selected
from .compatibility import view
from .portable_freeze import integrity
from .controller import ProtectedController

# Replace only the integrity dependency in a private view; historical code is
# preserved. All original admission/authorization/verification decisions remain.
private = view("src/lykoi_protected/controller.py", bindings={"integrity": integrity})


class PortableProtectedController(ProtectedController):
    require_active = private.ProtectedController.require_active
    _protected_activate = private.ProtectedController._protected_activate

    def __init__(self, *args, **kwargs):
        self.runtime_qualification = verify_selected(sys.executable)
        if self.runtime_qualification["status"] != "RUNTIME_COMPATIBLE":
            raise Failure("RUNTIME_INCOMPATIBLE", evidence=self.runtime_qualification)
        self.runtime_provenance = self.runtime_qualification["provenance"]
        super().__init__(*args, **kwargs)

    def components(self):
        value = super().components()
        value["tools"] = {"python_contract": contract_pin()}
        return value

    def execute(self, *args, **kwargs):
        # A new process always qualifies independently; in-process artifact
        # replacement also forces requalification before the next dispatch.
        actual = provenance()
        if actual != self.runtime_provenance:
            result = verify_selected(sys.executable)
            if result["status"] != "RUNTIME_COMPATIBLE" or result["provenance"] != actual:
                raise Failure("RUNTIME_INCOMPATIBLE", evidence=result)
            self.runtime_qualification, self.runtime_provenance = result, actual
        return super().execute(*args, **kwargs)

    def _event(self, kind, subject, actor, role, state, evidence=None, reason=None):
        # Existing evidence is sometimes an artifact ID, not a dictionary, and
        # is consumed as exact authority. Keep it byte-for-byte unchanged.
        # Add a separate append-only provenance receipt in the same transaction.
        super()._event("RUNTIME_EXECUTION_PROVENANCE", None, actor, role, "QUALIFIED",
                      evidence={"operation": kind, "operation_subject": subject,
                                "operation_revision": self.revision + 2,
                                "contract": contract_pin(), "provenance": self.runtime_provenance,
                                "qualification": self.runtime_qualification["status"]})
        return super()._event(kind, subject, actor, role, state, evidence=evidence, reason=reason)
