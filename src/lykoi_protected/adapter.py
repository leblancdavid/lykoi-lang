"""Provenance-aware source-only commitment; original prompts stay unchanged."""
import hashlib

from lykoi_controller import Failure
from lykoi_pipeline.controller import digest
from lykoi_rehearsal.adapters import AIAdapter
from lykoi_rehearsal.opencode_adapter import OpenCodeAdapter
from . import CLASSIFICATION


class SourceProvenance:
    def __init__(self, *args, classification=CLASSIFICATION, **kwargs):
        if classification not in {"PUBLIC", "SYNTHETIC", CLASSIFICATION}:
            raise Failure("UNKNOWN_SOURCE_CLASSIFICATION")
        self.classification = classification
        super().__init__(*args, **kwargs)

    def _request(self, request):
        bound = super()._request(request)
        if self.role == "reviewer":
            s = request["source"]
            record = {"id": s["identity"], "text": s["text"], "classification": self.classification,
                      "sha256": hashlib.sha256(s["text"].encode()).hexdigest()}
            bound["source_commitment"] = digest({"revision": s["revision"], "record": record})
        return bound


class ProtectedAIAdapter(SourceProvenance, AIAdapter):
    pass


class ProtectedOpenCodeAdapter(SourceProvenance, OpenCodeAdapter):
    pass
