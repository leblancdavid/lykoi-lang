"""Optional OpenCode implementation; installed CLI owns its existing OAuth."""
import json
import subprocess
from unittest.mock import patch

from lykoi_controller import Failure, canonical
from lykoi_controller.controller import parse_json
from lykoi_pipeline.controller import digest
from lykoi_freeze.opencode import tool_provenance, selected, REAL_RUN
from lykoi_rehearsal.opencode_adapter import OpenCodeAdapter, cli_configuration, role_prompt
from .adapter import Result


class OpenCodeTransport:
    def __init__(self, executable):
        self.executable = str(selected(executable))

    def identity(self):
        return {"implementation": "lykoi-opencode-transport", "interface_version": "r5.94c-1"}

    def provenance(self):
        return {**self.identity(), "installation": tool_provenance(self.executable)}

    def invoke(self, invocation):
        evidence = {"transport": self.identity(), "request_id": invocation.request_id,
                    "session": None, "actual_model_route": None, "status": "FAILURE"}
        try:
            before = self.provenance()
            evidence["implementation"] = before
            config = invocation.configuration
            if config != {"provider": "github-copilot", "model": "claude-sonnet-4.6", "temperature": 0, "timeout_seconds": 180}:
                raise Failure("AI_CONFIGURATION_UNAVAILABLE")
            if invocation.instructions != role_prompt(invocation.role):
                raise Failure("AI_INSTRUCTION_MISMATCH")
            adapter = OpenCodeAdapter(invocation.role, {**config, "executable": self.executable})
            route = config["provider"] + "/" + config["model"]

            def observe(argv, **kwargs):
                from pathlib import Path
                if list(Path(kwargs["cwd"]).iterdir()):
                    raise Failure("AI_CONTEXT_BOUNDARY_FAILURE")
                expected = cli_configuration(invocation.role, route)
                if json.loads(kwargs["env"]["OPENCODE_CONFIG_CONTENT"]) != expected:
                    raise Failure("AI_CONTEXT_BOUNDARY_FAILURE")
                effective = REAL_RUN([self.executable, "debug", "config"], cwd=kwargs["cwd"], env=kwargs["env"],
                                     capture_output=True, timeout=30)
                if effective.returncode:
                    raise Failure("AI_CONTEXT_CONFIGURATION_UNAVAILABLE")
                resolved = json.loads(effective.stdout)
                agent = resolved["agent"]["lykoi-" + invocation.role]
                if not (agent["prompt"] == invocation.instructions and agent["temperature"] == 0
                        and agent["tools"] == resolved["tools"] == {"*": False}
                        and agent["permission"] == resolved["permission"] == {"*": "deny"}
                        and resolved["instructions"] == [] and resolved.get("plugin", []) == []
                        and resolved["model"] == resolved["small_model"] == route
                        and resolved["compaction"]["auto"] is False and resolved["snapshot"] is False
                        and resolved["share"] == "disabled" and resolved["autoupdate"] is False
                        and resolved["agent"]["title"]["disable"] and resolved["agent"]["summary"]["disable"]):
                    raise Failure("AI_CONTEXT_BOUNDARY_FAILURE")
                evidence["effective_instructions_tools_context_verified"] = True
                evidence["fresh_context_verified"] = True
                return REAL_RUN(argv, **kwargs)

            payload = {"messages": [{}, {"content": canonical(invocation.inputs).decode()}],
                       "response_format": {"json_schema": {"schema": invocation.schema}}}
            with patch("lykoi_rehearsal.opencode_adapter.subprocess.run", side_effect=observe):
                response = adapter._invoke(payload)
            evidence["session"] = adapter.cli_session
            export = REAL_RUN([self.executable, "export", adapter.cli_session], capture_output=True, timeout=30)
            if export.returncode:
                raise Failure("AI_SESSION_PROVENANCE_UNAVAILABLE")
            record = json.loads(export.stdout)
            messages = record["messages"]
            users = [m for m in messages if m["info"]["role"] == "user"]
            assistants = [m for m in messages if m["info"]["role"] == "assistant"]
            intended = canonical({**invocation.inputs, "output_schema": invocation.schema}).decode()
            if (len(users) != 1 or not any(intended in p.get("text", "") for p in users[0]["parts"])
                    or not assistants or any(p["type"] == "tool" for m in messages for p in m["parts"])):
                raise Failure("AI_SESSION_BOUNDARY_FAILURE")
            if any(m["info"]["providerID"] != config["provider"] or m["info"]["modelID"] != config["model"]
                   or m["info"]["agent"] != "lykoi-" + invocation.role for m in assistants):
                raise Failure("AI_MODEL_ROUTE_MISMATCH")
            evidence.update(actual_model_route=route, session_input_verified=True, export_identity=digest(record))
            if self.provenance() != before:
                raise Failure("IMPLEMENTATION_DRIFT_DURING_EXECUTION")
            envelope = parse_json(response["choices"][0]["message"]["content"])
            evidence["status"] = "SUCCESS"
            return Result(envelope, None, evidence)
        except (Failure, OSError, ValueError, KeyError, TypeError, IndexError, subprocess.TimeoutExpired) as exc:
            failure = exc.as_dict() if isinstance(exc, Failure) else {"code": "AI_EXECUTION_FAILURE", "reason": type(exc).__name__}
            # Never publish raw provider errors, config bodies, stderr or credentials.
            evidence["failure"] = failure
            return Result(None, {"transport_failure": failure}, evidence)
