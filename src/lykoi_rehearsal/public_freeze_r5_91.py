"""One public experimental configuration, not a worker qualification registry."""
import copy
import hashlib
import json
from pathlib import Path

from lykoi_controller import Failure, canonical
from lykoi_pipeline.controller import ROOT, digest
from . import freeze as historical, adapters, verification
from .opencode_adapter import VERSION as ADAPTER, PROTOCOL, cli_configuration, role_prompt

VERSION = "public-rehearsal-freeze-r5.91-1"
PURPOSE = "FUTURE_PUBLIC_REHEARSAL_ONLY"
DIRECTORY = ROOT / "benchmark/results/phase5c/r5_91"
EXTRA = ("src/lykoi_rehearsal/opencode_adapter.py", "src/lykoi_rehearsal/public_freeze_r5_91.py",
         "src/lykoi_rehearsal/public_service_r5_91.py", "rehearsal/model-configurations-r5.91.json",
         "rehearsal/smoke_r5_91.py", "rehearsal/activate_r5_91.py", "rehearsal/verify_r5_91.py",
         "docs/public-rehearsal-protocol-r5.91.md", "tests/test_live_public_freeze.py",
         "benchmark/results/phase5c/r5_91/smoke-integration.json")


def configurations():
    return json.loads((ROOT / "rehearsal/model-configurations-r5.91.json").read_text(encoding="utf-8"))


def snapshot():
    body = historical.snapshot()
    body.update(version=VERSION, candidate="R5.91-PUBLIC-REHEARSAL-2", models=configurations(),
                instructions={r: role_prompt(r) for r in adapters.PROMPTS},
                qualification=None, smoke=json.loads((DIRECTORY / "smoke-integration.json").read_text()),
                model_policy=configurations()["policy"], protocol=PROTOCOL,
                role_cli_configurations={r: cli_configuration(r, "github-copilot/claude-sonnet-4.6") for r in adapters.PROMPTS})
    body["versions"].update(semantic_producers=ADAPTER, author=ADAPTER,
                             public_service="public-service-r5.91-1", candidate_plan=ADAPTER)
    paths = set(body["files"]) | set(EXTRA)
    paths |= {str(p.relative_to(ROOT)).replace("\\", "/") for p in (DIRECTORY / "attempt-3").glob("*.json")}
    body["files"] = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sorted(paths)}
    body["runtime"]["opencode"] = {"version": "1.1.25", "executable_sha256": hashlib.sha256(
        Path(configurations()["roles"]["author"]["executable"]).read_bytes()).hexdigest(),
        "returned_model_version": None, "provider_weights_pinned": False}
    return body


def seal_snapshot():
    body = snapshot()
    return {**body, "identity": digest(body)}


def integrity(candidate):
    try:
        body = {k: v for k, v in candidate.items() if k != "identity"}
        return candidate["identity"] == digest(body) and body == snapshot()
    except (OSError, ValueError, TypeError, KeyError):
        return False


def eligibility(candidate, controller):
    """Requirement-blind infrastructure check; no provider call or secret read."""
    blockers = []
    if not integrity(candidate):
        blockers.append("COMPONENT_OR_CONFIGURATION_DRIFT")
    config = configurations()
    smoke = candidate.get("smoke", {})
    if smoke.get("status") != "ROLE_INTEGRATION_SMOKE_ESTABLISHED":
        blockers.append("LIVE_ROLE_SMOKE_MISSING")
    sessions = set()
    for role in adapters.PROMPTS:
        receipt = smoke.get("roles", {}).get(role, {}).get("receipt", {})
        if (receipt.get("execution") != "LIVE_OPENCODE_OAUTH" or receipt.get("role") != role
                or receipt.get("adapter") != ADAPTER or receipt.get("authority") != "UNTRUSTED_CANDIDATE"
                or receipt.get("configuration_identity") != digest(config["roles"][role])
                or receipt.get("role_prompt_identity") != digest(role_prompt(role))
                or receipt.get("cli_configuration_identity") != digest(cli_configuration(role, "github-copilot/claude-sonnet-4.6"))
                or not receipt.get("schema_identity") or not receipt.get("input_identity") or not receipt.get("output_identity")
                or not receipt.get("cli_session")):
            blockers.append("LIVE_ROLE_PROVENANCE_MISMATCH:" + role)
        sessions.add(receipt.get("cli_session"))
    if len(sessions) != 4:
        blockers.append("SHARED_PRODUCER_CONTEXT")
    if controller is None:
        blockers.append("CONTROLLER_HEALTH_NOT_ATTESTED")
    else:
        try:
            controller.check_integrity()
            if controller.model_configurations != config or controller.approved_plans:
                blockers.append("CONTROLLER_CONFIGURATION_DRIFT")
            from .service import public_author_seed
            if controller.author_fixture != public_author_seed():
                blockers.append("CONTROLLER_SEED_DRIFT")
            roles = {r: {a for a, p in controller.principals.items() if r in p["roles"]}
                     for r in ("formalizer", "reviewer", "author", "verifier", "verification_authority")}
            if (any(not actors for actors in roles.values()) or roles["formalizer"] & roles["reviewer"]
                    or any(roles["author"] & roles[r] for r in ("reviewer", "verifier", "verification_authority"))):
                blockers.append("ROLE_SEPARATION_FAILURE")
        except (Failure, KeyError, ValueError):
            blockers.append("CONTROLLER_UNHEALTHY")
    return {"eligible": not blockers, "blockers": blockers, "candidate_identity": candidate.get("identity"),
            "scope": "INFRASTRUCTURE_ONLY_NO_REQUIREMENT_INSPECTION", "protected_authorization": False}
