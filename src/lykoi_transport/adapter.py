"""Existing role boundary with interchangeable invocation infrastructure."""
import copy
from dataclasses import dataclass
from typing import Protocol
import uuid

from lykoi_controller import Failure
from lykoi_pipeline.controller import digest
from lykoi_protected.adapter import SourceProvenance
from lykoi_rehearsal.adapters import AIAdapter, SCHEMAS, obj, check_schema
from lykoi_rehearsal.opencode_adapter import role_prompt
from lykoi_runtime.verify import provenance


@dataclass(frozen=True)
class Invocation:
    role: str
    configuration: dict
    instructions: str
    inputs: dict
    schema: dict
    request_id: str


@dataclass(frozen=True)
class Result:
    envelope: dict | None
    failure: dict | None
    provenance: dict


class Transport(Protocol):
    def identity(self) -> dict: ...
    def provenance(self) -> dict: ...
    def invoke(self, invocation: Invocation) -> Result: ...


class WorkerAdapter(AIAdapter):
    """Normal workspace/pipeline produce interface; every output remains untrusted."""
    def __init__(self, role, config, transport, guard=None):
        super().__init__(role, config)
        self.worker_transport, self.guard = transport, guard
        self.isolation = "FRESH_ALLOWLISTED_CONTEXT_NO_PROVIDER_INDEPENDENCE"

    def _request(self, request):
        bound = super()._request(request)
        if self.role == "reviewer":
            text = bound["source"]["text"]
            bound["source_span"] = {"start": 0, "end": len(text), "quote": text}
        return bound

    def invoke(self, request, schema=None):
        if self.guard:
            before = self.guard.ensure()
            if self.worker_transport is not self.guard.transport:
                raise Failure("UNQUALIFIED_TRANSPORT_IMPLEMENTATION")
            if self.config != self.guard.candidate["models"]["roles"][self.role]:
                raise Failure("PROTECTED_CONFIGURATION_DRIFT")
        request_id = uuid.uuid4().hex
        receipt = {"transport": self.worker_transport.identity(), "role": self.role,
                   "configured_model": self.config["provider"] + "/" + self.config["model"],
                   "configuration_identity": digest(self.config), "instruction_identity": digest(role_prompt(self.role)),
                   "request_id": request_id, "status": "FAILURE", "authority": "UNTRUSTED_CANDIDATE"}
        try:
            bound = self._request(request)
            binding = digest(bound)
            envelope_schema = obj({"binding": {"enum": [binding]}, "output": schema or SCHEMAS[self.role]})
            receipt.update(input_identity=binding, input_artifacts={k: digest(v) for k, v in bound.items()},
                           schema_identity=digest(envelope_schema))
            invocation = Invocation(self.role, copy.deepcopy(self.config), role_prompt(self.role),
                                    {"binding": binding, "input": bound}, envelope_schema, request_id)
            try:
                result = self.worker_transport.invoke(invocation)
            except Failure:
                raise
            except Exception as exc:
                raise Failure("AI_EXECUTION_FAILURE", reason=type(exc).__name__) from None
            if result.failure is not None and result.envelope is not None:
                raise Failure("AI_TRANSPORT_CONTRACT_VIOLATION", reason="Failure included candidate")
            receipt["execution_provenance"] = copy.deepcopy(result.provenance)
            if result.failure is not None:
                raise Failure("AI_EXECUTION_FAILURE", **result.failure)
            if result.envelope is None:
                raise Failure("INVALID_PRODUCER_OUTPUT", reason="Missing result")
            check_schema(result.envelope, envelope_schema)
            route = result.provenance.get("actual_model_route")
            if route is not None and route != receipt["configured_model"]:
                raise Failure("AI_MODEL_ROUTE_MISMATCH")
            if self.guard:
                if {"python": provenance(),
                    "transport": self.worker_transport.provenance()} != before:
                    raise Failure("IMPLEMENTATION_DRIFT_DURING_EXECUTION")
            output = copy.deepcopy(result.envelope["output"])
            receipt.update(status="SUCCESS", output_identity=digest(output))
            self.receipts.append(receipt)
            self.provenance.update(receipt)
            return output
        except Failure as exc:
            receipt["failure"] = exc.as_dict()
            self.receipts.append(receipt)
            self.provenance.update(receipt)
            raise

    def produce(self, request):
        return self.invoke(request)


class ProtectedWorkerAdapter(SourceProvenance, WorkerAdapter):
    pass
