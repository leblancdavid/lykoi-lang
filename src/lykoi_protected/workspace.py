"""Existing requirements lifecycle with truthful provenance and gated delivery."""
from lykoi_controller import Failure
from . import CLASSIFICATION
from .compatibility import workspace


class ProvenanceWorkspace(workspace.Workspace):
    """Public comparison workspace uses the identical prospective FRC version."""
    def __init__(self, *args, classification="PUBLIC", **kwargs):
        if classification not in {"PUBLIC", "SYNTHETIC", CLASSIFICATION}:
            raise Failure("UNKNOWN_SOURCE_CLASSIFICATION")
        self.classification = classification
        super().__init__(*args, **kwargs)
        if classification == CLASSIFICATION:
            from .controller import ProtectedController
            if not isinstance(self, ProtectedWorkspace) or not isinstance(self.c, ProtectedController):
                raise Failure("PROTECTED_CONTROLLER_REQUIRED")


class ProtectedWorkspace(ProvenanceWorkspace):
    def __init__(self, *args, authorization, source_identity, **kwargs):
        super().__init__(*args, classification=CLASSIFICATION, **kwargs)
        self.authorization, self.source_identity = authorization, source_identity

    def _bound(self, credential_role, command, **args):
        return self._call(credential_role, command, authorization=self.authorization,
                          source_identity=self.source_identity, run=self.session, **args)

    def ingest(self, credential, text, policies=()):
        raise Failure("PROTECTED_CUSTODIAN_ADMISSION_REQUIRED")

    def admit(self, opener):
        # Reservation commits before the custodian callback can open anything.
        self._bound("admission", "protected_reserve")
        try:
            text = opener()
            self._bound("admission", "protected_read", text=text)
            return self._bound("admission", "protected_admit", text=text, session=self.session)
        except Exception:
            self._bound("admission", "protected_incomplete")
            raise

    def _produce(self, producer, role):
        if producer.role != role or not producer.session:
            raise Failure("PRODUCER_ROLE_MISMATCH")
        from .adapter import ProtectedAIAdapter, ProtectedOpenCodeAdapter
        if (type(producer) not in {ProtectedAIAdapter, ProtectedOpenCodeAdapter}
                or producer.classification != CLASSIFICATION
                or producer.config != self.c.model_configurations["roles"][role]):
            raise Failure("PROTECTED_WORKER_CONFIGURATION_MISMATCH")
        self._bound(role, "protected_deliver", subject=self.source, recipient_role=role, session=producer.session)
        # Delivery recorded even if producer execution subsequently fails.
        return super()._produce(producer, role)

    def route_disagreement(self, coverage):
        policy = self.c.artifact(self.authorization)["content"]["clarification"]
        if policy["mode"] == "UNAVAILABLE_TERMINATE":
            self._bound("controller", "protected_terminal", outcome="CLARIFICATION_UNAVAILABLE")
            raise Failure("PROTECTED_CLARIFICATION_UNAVAILABLE")
        return super().route_disagreement(coverage)

    def ask(self, question_id):
        policy = self.c.artifact(self.authorization)["content"]["clarification"]
        if policy["mode"] == "UNAVAILABLE_TERMINATE":
            self._bound("controller", "protected_terminal", outcome="CLARIFICATION_UNAVAILABLE")
            raise Failure("PROTECTED_CLARIFICATION_UNAVAILABLE")
        return super().ask(question_id)
