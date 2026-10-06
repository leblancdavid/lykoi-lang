"""Physical-byte public component freeze and requirement-blind eligibility check."""
import hashlib
import copy
import os
import json
from pathlib import Path
import sys

from lykoi_pipeline.controller import ROOT, component_paths, digest
from lykoi_pipeline import contracts
from . import adapters, mappings, verification

VERSION = "public-rehearsal-freeze-1"
EXTRA = (
    "src/lykoi_rehearsal/__init__.py", "src/lykoi_rehearsal/adapters.py", "src/lykoi_rehearsal/mappings.py",
    "src/lykoi_rehearsal/service.py", "src/lykoi_rehearsal/verification.py", "src/lykoi_rehearsal/containment_worker.py",
    "src/lykoi_rehearsal/freeze.py", "src/lykoi_rehearsal/invoke.py",
    "rehearsal/public-capability-profile-1.json", "rehearsal/model-configurations-1.json", "rehearsal/semantic-qualification-1.json",
    "air/task_manager.json", "docs/axiom-v0.3.md", "docs/axiom-v0.2.md", "docs/public-rehearsal-capability-r5.89.md",
    "tests/test_public_rehearsal.py", "rehearsal/calibration-corpus-1.json", "rehearsal/qualify.py"
)


def configurations():
    return json.loads((ROOT / "rehearsal/model-configurations-1.json").read_text(encoding="utf-8"))


def snapshot():
    return {"version": VERSION, "candidate": "R5.89-PUBLIC-CANDIDATE-1", "purpose": "FUTURE_PUBLIC_REHEARSAL_ONLY",
            "active": False, "future_requirement_selected": False, "protected_authorization": False,
            "files": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in sorted(set(component_paths()) | set(EXTRA))},
            "runtime": {"python": sys.version, "executable": hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                        "libraries": {n: hashlib.sha256((Path(sys.executable).parent / n).read_bytes()).hexdigest()
                                      for n in (f"python{sys.version_info.major}{sys.version_info.minor}.zip", f"python{sys.version_info.major}{sys.version_info.minor}.dll")
                                      if (Path(sys.executable).parent / n).is_file()}},
            "versions": {"controller": "authority-1", "workspace": "workspace-1", "pipeline": "sealed-pipeline-1+public-rehearsal-1",
                         "profile": "PublicRehearsalCapabilityProfile-1", "registry": mappings.REGISTRY["version"],
                         "semantic_producers": adapters.VERSION, "author": adapters.VERSION,
                         "verifier": "WHAT_SIDE_DETERMINISTIC_RULE_PRODUCER_1_NOT_FIXTURE_LOOKUP",
                         "compiler": "0.3.0", "semantics": "axiom-0.3", "bdi": contracts.discovery.VERSION_BDI, "adequacy": contracts.adequacy.VERSION},
            "models": configurations(), "instructions": copy.deepcopy(adapters.PROMPTS), "schemas": copy.deepcopy(adapters.SCHEMAS),
            "mapping_registry": copy.deepcopy(mappings.REGISTRY), "verification_rules": copy.deepcopy(verification.CONTAINMENT),
            "qualification": json.loads((ROOT / "rehearsal/semantic-qualification-1.json").read_text(encoding="utf-8"))}


def seal_snapshot():
    body = snapshot()
    return {**body, "identity": digest(body)}


def integrity(candidate):
    try:
        body = {k: v for k, v in candidate.items() if k != "identity"}
        expected = snapshot()
        return candidate["identity"] == digest(body) and body == expected
    except (KeyError, OSError, TypeError, ValueError):
        return False


def eligibility(candidate, *, activation=None, controller=None):
    """No requirement argument, access, inference, or support decision exists here."""
    blockers = []
    intact = integrity(candidate)
    if not intact:
        blockers.append("COMPONENT_OR_CONFIGURATION_DRIFT")
    if (not activation or activation.get("candidate_identity") != candidate.get("identity")
            or activation.get("purpose") != "FUTURE_PUBLIC_REHEARSAL_ONLY" or activation.get("active") is not True):
        blockers.append("PUBLIC_FREEZE_NOT_ACTIVE")
    config = configurations()
    if not all(adapters.configured(config["roles"][r]) for r in ("formalizer", "reviewer", "author")):
        blockers.append("SEMANTIC_AUTHOR_MODELS_NOT_CONFIGURED")
    if not os.environ.get("LYKOI_REHEARSAL_API_KEY"):
        blockers.append("SEMANTIC_AUTHOR_CREDENTIAL_UNAVAILABLE")
    qualification = candidate.get("qualification", {})
    runs = qualification.get("live_ai_dry_runs", [])
    live_qualified = qualification.get("status") == "LIVE_CALIBRATION_APPROVED" and bool(qualification.get("approved_by")) and len(runs) >= 2
    for run in runs:
        receipts = run.get("receipts", {})
        live_qualified &= run.get("mode") == "CALIBRATION" and run.get("outcome") == "BEHAVIORALLY_VERIFIED"
        for role in ("formalizer", "reviewer", "author"):
            receipt = receipts.get(role, {})
            live_qualified &= (receipt.get("execution") == "LIVE_HTTPS" and receipt.get("role") == role
                               and receipt.get("configuration_identity") == digest(config["roles"][role])
                               and receipt.get("instruction_identity") == digest(adapters.PROMPTS[role])
                               and bool(receipt.get("input_identity")) and bool(receipt.get("output_identity")))
        live_qualified &= receipts.get("formalizer", {}).get("session") != receipts.get("reviewer", {}).get("session")
    if not live_qualified:
        blockers.append("REAL_AI_CALIBRATION_NOT_EXERCISED")
    # Explicit trusted-program scope permits Python API containment on Windows.
    # A hostile-code rehearsal would require a different qualified profile.
    if candidate.get("verification_rules") != verification.CONTAINMENT:
        blockers.append("CONTAINMENT_PROFILE_MISMATCH")
    if controller is None:
        blockers.append("CONTROLLER_HEALTH_NOT_ATTESTED")
    else:
        try:
            controller.events()
            actual = controller.components()
            if any(actual["files"].get(p) != pin for p, pin in candidate["files"].items() if p in actual["files"]):
                blockers.append("CONTROLLER_COMPONENT_DRIFT")
            if actual["public_rehearsal"]["models"] != config:
                blockers.append("CONTROLLER_CONFIGURATION_DRIFT")
            from .service import public_author_seed
            if controller.author_fixture != public_author_seed() or controller.approved_plans:
                blockers.append("CONTROLLER_SEED_OR_PLAN_CONFIGURATION_DRIFT")
            role_actors = {r: {actor for actor, p in controller.principals.items() if r in p["roles"]}
                           for r in ("formalizer", "reviewer", "author", "verifier", "verification_authority")}
            if (any(not actors for actors in role_actors.values()) or
                    any(role_actors["author"] & role_actors[r] for r in ("reviewer", "verifier", "verification_authority")) or
                    role_actors["formalizer"] & role_actors["reviewer"]):
                blockers.append("ROLE_SEPARATION_FAILURE")
        except (KeyError, OSError, ValueError):
            blockers.append("CONTROLLER_UNHEALTHY")
    return {"version": VERSION, "eligible": not blockers, "scope": "INFRASTRUCTURE_ONLY_NO_REQUIREMENT_INSPECTION",
            "candidate_identity": candidate.get("identity"), "integrity": intact, "blockers": blockers,
            "protected_authorization": False}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["candidate", "check"])
    args = parser.parse_args()
    if args.command == "candidate":
        output = seal_snapshot()
        destination = ROOT / "benchmark/results/phase5c/r5_89/public-freeze-candidate.json"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    else:
        candidate = json.loads((ROOT / "benchmark/results/phase5c/r5_89/public-freeze-candidate.json").read_text(encoding="utf-8"))
        output = eligibility(candidate)
    print(json.dumps(output, indent=2, sort_keys=True))
