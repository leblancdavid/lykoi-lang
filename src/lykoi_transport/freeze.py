"""Prospective neutral freeze; all 137 R5.94B content pins remain exact."""
import copy
import json
import platform
import sys

from lykoi_pipeline.controller import ROOT, digest
from lykoi_runtime.verify import verify_selected, provenance
from lykoi_freeze.content import canonical_text, sha_bytes, semantic_entry, TEXT_TYPES
from lykoi_freeze.freeze import semantic_body, provenance_body, verify_content as historical_verify
from . import CONTRACT
from .verify import BASE, qualify

VERSION = "protected-provider-neutral-freeze-r5.94c-1"
BASE_IDENTITY = "060adb4e30505f3488e36502626f20c4e58a8aa2742b635ddbaca4ce2b943915"


def base():
    value = json.loads((ROOT / BASE).read_text(encoding="utf-8"))
    check = historical_verify(value, BASE_IDENTITY)
    if not check["passed"]:
        raise ValueError("INHERITED_CANONICAL_CONTENT_DRIFT")
    return value


def build(transport):
    original = base()
    candidate = copy.deepcopy(original)
    candidate.update(version=VERSION, candidate="R5.94C-GENERIC-PROTECTED-CANDIDATE-1", supersedes=BASE_IDENTITY)
    for entry in candidate["dependencies"]:
        if entry["dependency"] == "opencode-transport":
            entry.update(dependency="ai-worker-transport", contract=CONTRACT,
                         reason="Isolated worker behavior is required; implementation is independently qualified runtime provenance")
    paths = {p.relative_to(ROOT).as_posix() for p in (ROOT / "src/lykoi_transport").glob("*.py")}
    paths.update({"docs/ai-worker-transport-contract-v1.md", "docs/provider-neutral-freeze-r5.94c.md",
                  "rehearsal/ai-worker-transport-contract-v1.json", "rehearsal/validate_r5_94c.py", "tests/test_ai_transport.py"})
    paths.add("rehearsal/audit_r5_94c.py")
    for name in sorted(paths):
        data = (ROOT / name).read_bytes()
        candidate["dependencies"].append({"dependency": name, "type": TEXT_TYPES[(ROOT / name).suffix],
            "freeze_class": "CANONICAL_CONTENT_PIN", "canonicalization": "UTF8_CRLF_TO_LF_V1",
            "content_sha256": sha_bytes(canonical_text(data)), "reason": "Prospective neutral transport interface/qualification/freeze procedure",
            "provenance": {"physical_sha256": sha_bytes(data)}})
    candidate["provenance"] = {"python": provenance(), "transport": transport.provenance(),
                               "platform": platform.platform(), "repository_location": str(ROOT)}
    candidate["identity"] = digest(semantic_body(candidate))
    candidate["provenance_identity"] = digest(provenance_body(candidate))
    return candidate


def verify_content(candidate, expected_identity, root=ROOT):
    try:
        assert candidate["identity"] == expected_identity == digest(semantic_body(candidate)), "CANDIDATE_IDENTITY_MISMATCH"
        assert candidate["version"] == VERSION, "FREEZE_VERSION_MISMATCH"
        assert candidate["provenance_identity"] == digest(provenance_body(candidate)), "PROVENANCE_INTEGRITY_FAILURE"
        original = json.loads((ROOT / BASE).read_text(encoding="utf-8"))
        assert original["identity"] == BASE_IDENTITY == digest(semantic_body(original)), "HISTORICAL_BASE_SUBSTITUTION"
        inherited = [semantic_entry(e) for e in original["dependencies"] if e["freeze_class"] == "CANONICAL_CONTENT_PIN"]
        assert len(inherited) == 137
        actual = {e["dependency"]: semantic_entry(e) for e in candidate["dependencies"]}
        assert all(actual[e["dependency"]] == e for e in inherited), "INHERITED_PIN_WEAKENED"
        assert candidate["models"] == original["models"] and candidate["semantics"] == original["semantics"], "SEMANTIC_OR_MODEL_DRIFT"
        assert candidate["supersedes"] == BASE_IDENTITY
        # Reuse the unchanged strict file/class verifier, projecting ONLY the
        # transport contract locator and format header to its historical vocabulary.
        projected = copy.deepcopy(candidate)
        projected["version"] = original["version"]
        for e in projected["dependencies"]:
            if e["dependency"] == "ai-worker-transport":
                assert e["contract"] == CONTRACT
                e.update(dependency="opencode-transport", contract="OPENCODE_ADAPTER_CONTRACT_V1")
        projected["identity"] = digest(semantic_body(projected))
        projected["provenance_identity"] = digest(provenance_body(projected))
        return historical_verify(projected, projected["identity"], root)
    except (AssertionError, KeyError, TypeError, ValueError, OSError) as exc:
        return {"passed": False, "checks": [], "failures": [{"dependency": "neutral-freeze", "reason": str(exc)}]}


def preflight(candidate, expected_identity, transport, *, regression):
    content = verify_content(candidate, expected_identity)
    result = {"candidate_identity": candidate.get("identity"), "eligible": False, "content": content,
              "active": False, "target_authorizations": [], "failures": list(content["failures"])}
    if not content["passed"]:
        return result
    runtime = verify_selected(sys.executable)
    live = qualify(transport, candidate["models"])
    result.update(python=runtime, transport=live, regression=regression,
                  platform_containment={"contract": "PYTHON_RUNTIME_CONTRACT_V1", "passed": runtime["status"] == "RUNTIME_COMPATIBLE"})
    if runtime["status"] != "RUNTIME_COMPATIBLE":
        result["failures"].append({"dependency": "python-runtime/platform-containment", "reason": runtime["status"]})
    if live["status"] != "TRANSPORT_COMPATIBLE":
        result["failures"].append({"dependency": "ai-worker-transport/model-availability", "reason": live["status"]})
    if not regression["passed"]:
        result["failures"].append({"dependency": "transport/protected/verification-machinery", "reason": "REGRESSION_FAILED"})
    result["eligible"] = not result["failures"]
    return result
