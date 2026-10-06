"""Stateless HTTPS AI producers; credentials stay in service environment only.

No tool use, conversation history, local paths, or controller credentials are
available to the remote model. Provider responses are untrusted candidates.
"""
import copy
import hashlib
import json
import os
import urllib.error
import urllib.request
import uuid

from lykoi_controller import Failure, canonical
from lykoi_controller.controller import parse_json
from lykoi_pipeline.controller import digest

VERSION = "public-ai-adapter-1"
PROMPTS = {
    "formalizer": "Extract WHAT only from source and authorized evidence. Do not infer conventions. Return obligations, exact source quotes, authority references, material issues and clarification questions. Use stable logical IDs. Ambiguity must remain visible. No implementation or approval. Supported downstream slice is task title creation optionally with explicit omitted priority LOW/NORMAL/HIGH; retain ALL unsupported obligations too, never simplify to this slice.",
    "reviewer": "Independently inventory source and authorized evidence without any formalizer candidate. Account for every non-whitespace source character with exact spans. Interpret every material obligation, uncertainty and policy independently. Use stable logical IDs. Copy supplied source commitment. Never approve requirements. Retain unsupported behavior; no conventions as authority.",
    "author": "Produce only a JSON Lykoi axiom_version 0.3 model. Implement the authorized V1 obligations using the frozen public compiler seed and semantics. Do not emit Python. Compiler semantics cannot be changed. No tools or file access. No acceptance tests or private verifier material are available. Return source only; unsupported language must fail.",
    "verifier": "Prepare candidate external CLI acceptance cases from sealed WHAT only. No author output or implementation. Every obligation needs executable traceable observations. Return the external-cli-plan-1 plan with command argv, integer returncode, contains/absent and coverage. Case identity is controller-computed. Unsupported observations must be UNVERIFIED. Expected results are private to verification and must never enter author inputs. This is a candidate, not verification authority."
}


def obj(properties, required=None):
    return {"type": "object", "properties": properties, "required": list(properties) if required is None else required,
            "additionalProperties": False}


def array(items):
    return {"type": "array", "items": items}


TEXT = {"type": "string"}
JSON_OBJECT = {"type": "object"}
RELATION = obj({"kind": TEXT, "parameters": JSON_OBJECT})
OBLIGATION = obj({"id": TEXT, "basis": {"enum": ["STATED", "NECESSARY_IMPLICATION"]}, "source_quote": TEXT,
                  "derived_from": array(TEXT), "statement": TEXT, "relation": RELATION})
FORMALIZER = obj({"obligations": array(OBLIGATION), "authority": JSON_OBJECT,
                 "questions": array(obj({"id": TEXT, "text": TEXT, "priority": {"enum": ["BLOCKING", "IMPORTANT", "INFORMATIONAL"]}, "affects": array(TEXT)})),
                 "issues": array(JSON_OBJECT), "unspecified": array(TEXT), "domains": JSON_OBJECT,
                 "lineage": array(JSON_OBJECT), "policy_applications": array(JSON_OBJECT),
                 "unsupported": array(TEXT), "necessary_implications": array(JSON_OBJECT), "exclusions": array(JSON_OBJECT), "structure": JSON_OBJECT},
                ["obligations", "authority", "questions", "issues"])
SOI_ITEM = obj({"id": TEXT, "spans": array(obj({"start": {"type": "integer"}, "end": {"type": "integer"}, "quote": TEXT})),
                "meaning": TEXT, "category": TEXT, "material": {"type": "boolean"}, "dependencies": array(TEXT)})
REVIEWER = obj({"inventory": obj({"version": {"enum": ["SourceObligationInventory-0.1"]}, "source_commitment": TEXT,
                                 "extractor": TEXT, "context_class": TEXT, "items": array(SOI_ITEM), "questions": array(TEXT), "limitations": array(TEXT)}),
                "interpretations": JSON_OBJECT, "authority": JSON_OBJECT, "domains": JSON_OBJECT, "unspecified": array(TEXT)},
               ["inventory", "interpretations", "authority"])
SCHEMAS = {"formalizer": FORMALIZER, "reviewer": REVIEWER,
           "author": obj({"source": JSON_OBJECT}), "verifier": obj({"plan": JSON_OBJECT})}


def check_schema(value, schema):
    """Dependency-free structural schema checks; native FRC/SOI/compiler add semantics."""
    if "anyOf" in schema:
        for option in schema["anyOf"]:
            try:
                check_schema(value, option)
                return
            except Failure:
                pass
        raise Failure("INVALID_PRODUCER_OUTPUT", reason="schema alternatives")
    types = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool, "null": type(None)}
    if "type" in schema and type(value) is not types[schema["type"]]:
        raise Failure("INVALID_PRODUCER_OUTPUT", reason="schema type")
    if "enum" in schema and value not in schema["enum"]:
        raise Failure("INVALID_PRODUCER_OUTPUT", reason="schema enum")
    if type(value) is dict:
        props = schema.get("properties", {})
        if not set(schema.get("required", [])) <= set(value):
            raise Failure("INVALID_PRODUCER_OUTPUT", reason="required field")
        if schema.get("additionalProperties") is False and set(value) - set(props):
            raise Failure("INVALID_PRODUCER_OUTPUT", reason="unknown field")
        for key in value.keys() & props.keys():
            check_schema(value[key], props[key])
        if type(schema.get("additionalProperties")) is dict:
            for key in value.keys() - props.keys():
                check_schema(value[key], schema["additionalProperties"])
    if type(value) is list and "items" in schema:
        for item in value:
            check_schema(item, schema["items"])


def configured(config):
    return (config.get("provider") == "openai-compatible" and bool(config.get("model"))
            and config.get("endpoint") == "https://api.openai.com/v1/chat/completions"
            and config.get("key_environment") == "LYKOI_REHEARSAL_API_KEY"
            and type(config.get("timeout_seconds")) is int and 1 <= config["timeout_seconds"] <= 120)


class AIAdapter:
    isolation = "STATELESS_SEPARATE_REQUEST_CONTEXT_NO_PROVIDER_INDEPENDENCE"

    def __init__(self, role, config, *, transport=None):
        if role not in PROMPTS:
            raise Failure("PRODUCER_ROLE_MISMATCH")
        self.role, self.config = role, copy.deepcopy(config)
        self.session = role + ":" + uuid.uuid4().hex
        self.transport = transport
        self.receipts = []
        self.provenance = {"provider": config.get("provider"), "model": config.get("model"),
                           "adapter": VERSION, "instruction_identity": digest(PROMPTS[role]),
                           "configuration_identity": digest(config), "execution": "NOT_RUN"}

    def _request(self, request):
        if self.role in ("formalizer", "reviewer"):
            allowed = {"role", "session", "source", "evidence", "output_schema", "instructions"}
            if set(request) != allowed or request["role"] != self.role or request["session"] != self.session:
                raise Failure("PRODUCER_INPUT_ALLOWLIST_VIOLATION")
            if set(request["source"]) != {"identity", "text", "revision"}:
                raise Failure("PRODUCER_INPUT_ALLOWLIST_VIOLATION")
            for e in request["evidence"]:
                if (set(e) - {"identity", "text", "provenance", "question", "waivable"}
                        or e["provenance"] not in {"human_statement", "clarification_answer", "approved_policy"}):
                    raise Failure("PRODUCER_INPUT_ALLOWLIST_VIOLATION")
        elif self.role == "author":
            if set(request) != {"version", "run", "v1", "toolchain", "fixture"}:
                raise Failure("AUTHOR_INPUT_ALLOWLIST_VIOLATION")
            from benchmark.evaluation.benchmark_documents_v1 import verify_contract
            verify_contract(request["v1"])
        else:
            if set(request) != {"what", "what_seal", "profile_identity"}:
                raise Failure("PRODUCER_INPUT_ALLOWLIST_VIOLATION")
        bound = copy.deepcopy(request)
        if self.role == "reviewer":
            s = request["source"]
            record = {"id": s["identity"], "text": s["text"], "classification": "SYNTHETIC",
                      "sha256": hashlib.sha256(s["text"].encode()).hexdigest()}
            bound["source_commitment"] = digest({"revision": s["revision"], "record": record})
        return bound

    def produce(self, request):
        bound = self._request(request)
        identity = digest(bound)
        output_schema = copy.deepcopy(SCHEMAS[self.role])
        if self.role == "formalizer":
            # Keep opaque historical relations compatible, but require the typed
            # profile schema for query-shaped parameters after model output.
            from lykoi_workspace.query_schema import relation_schema
            output_schema["properties"]["obligations"]["items"]["properties"]["relation"] = {
                "anyOf": [relation_schema(), RELATION]}
        schema = obj({"binding": {"enum": [identity]}, "output": output_schema})
        payload = {"model": self.config.get("model"), "temperature": 0,
                   "messages": [{"role": "system", "content": PROMPTS[self.role]},
                                {"role": "user", "content": canonical({"input": bound, "binding": identity}).decode()}],
                   "response_format": {"type": "json_schema", "json_schema": {"name": "lykoi_" + self.role,
                                       "strict": False, "schema": schema}}}
        if self.transport is None:
            if not configured(self.config):
                raise Failure("AI_CONFIGURATION_UNAVAILABLE", role=self.role)
            key = os.environ.get(self.config["key_environment"])
            if not key:
                raise Failure("AI_CREDENTIAL_UNAVAILABLE", role=self.role)
            req = urllib.request.Request(self.config["endpoint"], data=canonical(payload),
                                         headers={"Content-Type": "application/json", "Authorization": "Bearer " + key}, method="POST")
            try:
                with urllib.request.urlopen(req, timeout=self.config["timeout_seconds"]) as response:
                    raw = response.read(1000001)
                if len(raw) > 1000000:
                    raise Failure("PRODUCER_OUTPUT_TOO_LARGE")
                response = parse_json(raw.decode())
            except (OSError, urllib.error.HTTPError, ValueError) as exc:
                # Provider error bodies may echo sensitive request data. Do not persist them.
                raise Failure("AI_EXECUTION_FAILURE", role=self.role, reason=type(exc).__name__) from None
            execution = "LIVE_HTTPS"
        else:
            response = self.transport(copy.deepcopy(payload))
            execution = "TEST_TRANSPORT_NOT_REAL_AI"
        try:
            envelope = parse_json(response["choices"][0]["message"]["content"])
            check_schema(envelope, schema)
            if self.role == "formalizer":
                from lykoi_workspace.query_schema import validate_output
                validate_output(envelope["output"])
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise Failure("INVALID_PRODUCER_OUTPUT", reason=type(exc).__name__) from None
        receipt = {"adapter": VERSION, "role": self.role, "session": self.session,
                   "provider": self.config.get("provider"), "requested_model": self.config.get("model"),
                   "returned_model": response.get("model"), "provider_response_id": response.get("id"),
                   "instruction_identity": digest(PROMPTS[self.role]), "schema_identity": digest(schema),
                   "configuration_identity": digest(self.config), "input_identity": identity,
                   "source_identity": request.get("source", {}).get("identity", request.get("what_seal")),
                   "policy_evidence_identity": digest(request.get("evidence", [])),
                   "output_identity": digest(envelope["output"]), "authority": "UNTRUSTED_CANDIDATE", "execution": execution}
        self.receipts.append(receipt)
        self.provenance.update(receipt)
        return copy.deepcopy(envelope["output"])
