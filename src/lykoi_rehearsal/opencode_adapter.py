"""R5.91 single configured OAuth path; no credential extraction or routing."""
import copy
import json
import os
from pathlib import Path
import subprocess
import tempfile

from lykoi_controller import Failure, canonical
from lykoi_controller.controller import parse_json
from lykoi_pipeline.controller import digest
from .adapters import AIAdapter, PROMPTS

VERSION = "public-opencode-adapter-r5.91-1"
PROTOCOL = "opencode-json-events-to-bound-json-1"
ROLE_PROTOCOL = {
    "formalizer": "STATED obligations must have derived_from: []. Issue objects must have exactly id, category (AMBIGUITY/CONFLICT/QUESTION), description, affects (obligation IDs), alternatives (strings), witness (null/object), resolved (false). Relation kind must be one of sum, increment, crud, filter_order, normalize_ascii, transition, invariant, persist, optional_dispatch, selection_prefix, effects, priority_extension, priority_rank, priority_create, priority_list, priority_filter, migration_preserve, default, public_state_alternatives, durable_content_constraints. Existing title-creation relation is crud with parameters {domain: task creation, result: supplied title}; omitted priority relation is priority_create with parameters {condition: priority omitted, result: LOW/NORMAL/HIGH}. Use these only when faithful; retain unsupported obligations and ambiguities. Authority is {obligation ID: [evidence identity]}, NOT its inverse.",
    "reviewer": "Existing title-creation relation is crud with parameters {domain: task creation, result: supplied title}; omitted priority relation is priority_create with parameters {condition: priority omitted, result: LOW/NORMAL/HIGH}. Use only when faithful to source, retaining every unsupported obligation. Authority is {item ID: [evidence identity]}. Allowed inventory categories are BEHAVIOR, FREEDOM, CONSUMER_RESTRICTION, CARDINALITY_BOUND, AMBIGUITY, CONFLICT, UNSPECIFIED, NONBEHAVIORAL. Every item requires at least one nonempty exact source span, including uncertainty items. source_span supplies the exact whole-source span; you may copy it if a whole-source statement is applicable. End is exclusive, not inclusive. All non-whitespace characters must be accounted for. Never access a formalizer candidate.",
    "author": "The output source must use exactly the root fields of fixture.source. v1 is an input contract, NOT a permitted source field. Preserve the compiler seed vocabulary and IDs; make only changes needed for authorized obligations. Do not insert explanatory metadata or invent syntax.",
    "verifier": "Native plan shape: {version: external-cli-plan-1, outcome: READY or UNVERIFIED, producer: descriptive string, cases: [{id: string, obligations: [WHAT obligation IDs], initial_state: fresh_directory, steps: [{argv: [command and flags], returncode: integer, contains: [strings], absent: [strings optional]}], invariants: [], transitions: string, rejections: string}], coverage: [{obligation: WHAT obligation ID, classification: EXERCISED or UNVERIFIED or AUTHORIZED_FREEDOM, justification: string, cases: [case IDs]}], limitations: [strings]}. Do not calculate hashes; refer to case IDs in coverage. The controller computes case identities and rewrites references only. Public CLI syntax is create --title TEXT --description TEXT [--priority LOW|NORMAL|HIGH]; argv starts with create, not an executable prefix. This is public interface information, not implementation access."
}
ENVELOPE_INSTRUCTION = (
    "Return one JSON object only, with binding copied exactly from the input and output "
    "conforming to the supplied output_schema. No markdown or commentary. No tools. "
    "All output is an untrusted candidate. Authority maps obligation/item IDs to lists "
    "of supplied evidence identities. Reviewer interpretations map inventory item IDs "
    "to objects with statement and relation (kind and parameters). Reviewer categories "
    "are BEHAVIOR, DOMAIN, AMBIGUITY, POLICY, CONTEXT or EXCLUSION. Use stable descriptive "
    "logical IDs (e.g. TITLE), not evidence identities. Exact spans are zero-based Python "
    "string offsets. No inferred conventions."
)


def cli_configuration(role, model):
    return {"$schema": "https://opencode.ai/config.json", "share": "disabled",
            "autoupdate": False, "snapshot": False, "model": model, "small_model": model,
            "permission": "deny", "tools": {"*": False}, "instructions": [],
            "agent": {"lykoi-" + role: {"mode": "primary", "temperature": 0,
                       "prompt": role_prompt(role),
                       "tools": {"*": False}, "permission": "deny"},
                      "title": {"disable": True}, "summary": {"disable": True}},
            "compaction": {"auto": False}}


def role_prompt(role):
    return PROMPTS[role] + "\n" + ENVELOPE_INSTRUCTION + "\n" + ROLE_PROTOCOL[role]


def normalize_plan(plan):
    """Only deterministic identity/reference assignment; never repair expectations."""
    plan = copy.deepcopy(plan)
    references = {}
    for case in plan["cases"]:
        old = case.pop("identity", None)
        identity = digest(case)
        if case["id"] in references:
            raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Duplicate case ID")
        references[case["id"]] = identity
        if old:
            references[old] = identity
        case["identity"] = identity
    for row in plan["coverage"]:
        row["cases"] = [references.get(ref, ref) for ref in row["cases"]]
    return plan


class OpenCodeAdapter(AIAdapter):
    """Reuse R5.89 input/schema checks; replace only the invocation mechanism.

    The installed CLI owns OAuth, including refresh. This code never reads auth.json.
    No attach/continue/session argument: each invocation creates a fresh context.
    """
    isolation = "SEPARATE_CONTEXT_SOURCE_BLIND_TO_CANDIDATE_NO_INDEPENDENT_MODEL_COGNITION"

    def __init__(self, role, config):
        super().__init__(role, config, transport=self._invoke)
        self.attempts = []
        self.last_output = None
        self.cli_session = None
        self.last_input = None

    def _request(self, request):
        bound = super()._request(request)
        if self.role == "reviewer":
            text = bound["source"]["text"]
            bound["source_span"] = {"start": 0, "end": len(text), "quote": text}
        self.last_input = copy.deepcopy(bound)
        return bound

    def _invoke(self, payload):
        executable = Path(self.config["executable"])
        if (self.config.get("provider") != "github-copilot" or not executable.is_file()
                or self.config.get("model") != "claude-sonnet-4.6"):
            raise Failure("AI_CONFIGURATION_UNAVAILABLE", role=self.role)
        model = self.config["provider"] + "/" + self.config["model"]
        sent = json.loads(payload["messages"][1]["content"])
        sent["output_schema"] = payload["response_format"]["json_schema"]["schema"]
        self.attempts.append({"role": self.role, "input_identity": sent["binding"],
                              "status": "DISPATCHED"})
        # Preserve normal OAuth data location; isolate project/global instructions.
        # Clear only inherited local-server settings for the fresh in-process CLI;
        # never attach to or bypass authentication on an existing server.
        env = {k: v for k, v in os.environ.items() if not k.startswith("OPENCODE_")}
        with tempfile.TemporaryDirectory(prefix="lykoi-ai-role-") as tmp:
            env.update(XDG_CONFIG_HOME=tmp, OPENCODE_CONFIG_CONTENT=canonical(cli_configuration(self.role, model)).decode(),
                       OPENCODE_DISABLE_CLAUDE_CODE="1", OPENCODE_DISABLE_EXTERNAL_SKILLS="1")
            try:
                result = subprocess.run([str(executable), "run", "--model", model, "--agent", "lykoi-" + self.role,
                                         "--format", "json", "Return the bound JSON response to the request on stdin."],
                                        input=canonical(sent), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        cwd=tmp, env=env, timeout=self.config["timeout_seconds"])
            except (OSError, subprocess.TimeoutExpired) as exc:
                self.attempts[-1]["status"] = type(exc).__name__
                raise Failure("AI_EXECUTION_FAILURE", role=self.role, reason=type(exc).__name__) from None
        # Provider errors/headers/stderr are never retained: they may contain secrets.
        if len(result.stdout) > 1000000 or result.returncode:
            self.attempts[-1]["status"] = "CLI_FAILURE"
            raise Failure("AI_EXECUTION_FAILURE", role=self.role, reason="CLI_FAILURE")
        texts, sessions = [], set()
        for line in result.stdout.decode("utf-8", errors="strict").splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if event.get("type") == "error":
                self.attempts[-1].update(status="PROVIDER_ERROR", status_code=event.get("error", {}).get("data", {}).get("statusCode"))
                raise Failure("AI_EXECUTION_FAILURE", role=self.role, reason="PROVIDER_ERROR")
            if event.get("type") == "tool_use":
                raise Failure("PRODUCER_INPUT_ALLOWLIST_VIOLATION", reason="Unexpected tool call")
            if event.get("sessionID"):
                sessions.add(event["sessionID"])
            if event.get("type") == "text":
                texts.append(event["part"]["text"])
        if len(sessions) != 1 or not texts:
            raise Failure("INVALID_PRODUCER_OUTPUT", reason="Missing fresh CLI session/text")
        self.cli_session = sessions.pop()
        text = "".join(texts).strip()
        # Accept one conventional JSON fence; no heuristic object extraction/repair.
        if text.startswith("```json\n") and text.endswith("\n```"):
            text = text[8:-4]
        self.last_output = text
        self.attempts[-1].update(status="LIVE_RESPONSE", session=self.cli_session)
        return {"model": None, "id": None, "choices": [{"message": {"content": text}}]}

    def produce(self, request):
        output = super().produce(request)
        receipt = self.receipts[-1]
        receipt.update(adapter=VERSION, execution="LIVE_OPENCODE_OAUTH", access_path="installed OpenCode CLI / GitHub Copilot OAuth",
                       cli_session=self.cli_session, protocol=PROTOCOL,
                       role_prompt_identity=digest(role_prompt(self.role)),
                       cli_configuration_identity=digest(cli_configuration(self.role, "github-copilot/claude-sonnet-4.6")),
                       model_version_exposed=None, returned_model=None)
        self.provenance.update(receipt)
        return copy.deepcopy(output)
