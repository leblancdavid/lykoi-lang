"""Explicit dependency manifest, external identity verification and machine preflight."""
import copy
import json
from pathlib import Path
import platform
import sys

from lykoi_pipeline.controller import ROOT, digest
from lykoi_runtime.verify import provenance, verify_selected
from .content import TEXT_TYPES, TEXT_CONTRACT, CLASSES, content_identity, canonical_text, sha_bytes, semantic_entry, verify_entry
from .opencode import semantic_models, qualify, tool_provenance, CONTRACT as OPENCODE_CONTRACT

BASE = "benchmark/results/phase5c/r5_94a/candidate-2/protected-freeze-candidate.json"
BASE_IDENTITY = "7635e16fdf2c2fd61f4878bc8d6924fa9995d24a9c92111c07e3fb404878ea03"
EXTRA = ("docs/freeze-dependency-classes-v1.md", "docs/opencode-adapter-contract-v1.md",
         "rehearsal/opencode-adapter-contract-v1.json", "rehearsal/validate_r5_94b.py",
         "tests/test_portable_freeze.py", "tests/test_portable_execution.py")
# Historical Windows freeze included both spellings of one tracked source file.
# This explicit locator is an evidence-bound alias, not global case folding.
HISTORICAL_LOCATORS = {"src/lykoi_controller/Controller.py": "src/lykoi_controller/controller.py"}


def read_record(path):
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    assert value["identity"] == digest({k: v for k, v in value.items() if k != "identity"}), "Historical record integrity"
    return value


def semantic_body(candidate):
    body = {k: copy.deepcopy(v) for k, v in candidate.items() if k not in {"identity", "provenance", "provenance_identity"}}
    body["dependencies"] = [semantic_entry(e) for e in body["dependencies"]]
    return body


def provenance_body(candidate):
    return {"machine": candidate["provenance"], "dependencies": {e["dependency"]: e["provenance"] for e in candidate["dependencies"]}}


def build(executable):
    original = read_record(BASE)
    assert original["identity"] == BASE_IDENTITY, "Historical base substitution"
    inherited = original["files"]
    paths = set(inherited) | {BASE} | set(EXTRA)
    # Audit source import closure of the executing infrastructure, not protected directories.
    for package in ("lykoi_freeze", "air_compiler", "lykoi_controller", "lykoi_workspace", "lykoi_pipeline", "lykoi_protected", "lykoi_rehearsal", "lykoi_runtime"):
        paths.update(p.relative_to(ROOT).as_posix() for p in (ROOT / "src" / package).glob("*.py"))
    dependencies, comparisons = [], []
    for name in sorted(paths):
        locator = HISTORICAL_LOCATORS.get(name, name)
        path = ROOT / locator
        if path.suffix not in TEXT_TYPES:
            raise ValueError("AMBIGUOUS_DEPENDENCY_TYPE:" + name)
        data = path.read_bytes()
        lf = canonical_text(data)
        current = sha_bytes(data)
        if name in inherited:
            pin = inherited[name]
            if pin not in {current, sha_bytes(lf), sha_bytes(lf.replace(b"\n", b"\r\n"))}:
                raise ValueError("INHERITED_CONTENT_DRIFT_OR_AMBIGUOUS_CLASSIFICATION:" + name)
            comparisons.append({"dependency": name, "historical_physical_sha256": pin,
                                "current_physical_sha256": current, "canonical_sha256": sha_bytes(lf),
                                "historical_representation": "physical" if pin == current else "LF" if pin == sha_bytes(lf) else "CRLF",
                                "representation_only_difference": current != pin, "content_continuity": True})
        dependencies.append({"dependency": name, "type": TEXT_TYPES[path.suffix], "freeze_class": "CANONICAL_CONTENT_PIN",
                             "canonicalization": TEXT_CONTRACT, "content_sha256": sha_bytes(lf),
                             "reason": "Immutable semantic implementation/configuration or supporting historical/procedure evidence; line-ending representation alone is incidental",
                             "provenance": {"physical_sha256": current, "historical_physical_sha256": inherited.get(name)}})
        if locator != name:
            assert inherited[name] == inherited[locator], "Ambiguous historical case alias"
            dependencies[-1].update(locator=locator, reason="Historical case-only alias of the same tracked source, proven by identical inherited pin; canonical tracked locator avoids Windows-only lookup")
    for name, contract, reason in (
        ("python-runtime", "PYTHON_RUNTIME_CONTRACT_V1", "Runtime and stdlib interchangeability requires existing behavioral probes/tests"),
        ("opencode-transport", OPENCODE_CONTRACT, "Configured role transport interchangeability requires live interface/isolation qualification"),
        ("platform-containment", "PYTHON_RUNTIME_CONTRACT_V1", "Supported OS/architecture, durable filesystem/process and actual trusted-local denial hooks are qualified, not path-pinned")):
        dependencies.append({"dependency": name, "type": "execution-infrastructure", "freeze_class": "COMPATIBILITY_CONTRACT",
                             "contract": contract, "reason": reason, "provenance": {"recorded_in": "machine"}})
    dependencies.append({"dependency": "machine-installation-and-representation", "type": "audit-provenance", "freeze_class": "PROVENANCE_ONLY",
                         "reason": "Exact runtime/tool bytes, absolute locations, OS particulars and physical text representation do not define experimental meaning",
                         "provenance": {"recorded_in": "machine"}})
    semantics = {k: copy.deepcopy(v) for k, v in original.items() if k not in {"identity", "files", "runtime", "version", "candidate", "models", "supersedes"}}
    models = semantic_models(original["models"])
    for name, field, value, reason in (
        ("experiment-semantic-envelope", "semantics", semantics, "Exact inherited instructions, schemas, mappings, capability, protected policy, taxonomy and historical evidence; no semantic rewriting"),
        ("worker-model-access-configuration", "models", models, "Exact provider/model/temperature/timeout/policy, independent of the interchangeable transport artifact")):
        dependencies.append({"dependency": name, "type": "canonical-structured-data", "freeze_class": "CANONICAL_CONTENT_PIN",
                             "canonicalization": "CJ-1", "embedded_field": field, "content_sha256": digest(value), "reason": reason,
                             "provenance": {"representation": "Embedded structured value; physical container hash recorded in final evidence", "serialized_CJ1_sha256": digest(value)}})
    # Retain old smoke/receipts as historical evidence, not live eligibility checks.
    candidate = {"version": "protected-portable-freeze-r5.94b-1", "candidate": "R5.94B-GENERIC-PROTECTED-CANDIDATE-2",
                 "supersedes": original["identity"], "semantics": semantics, "models": models,
                 "dependencies": dependencies, "active": False, "target_authorizations": [],
                 "provenance": {"python": provenance(), "opencode": tool_provenance(executable),
                                "os": {"system": platform.system(), "release": platform.release(), "machine": platform.machine()},
                                "repository_location": str(ROOT), "cross_machine_comparison": comparisons}}
    candidate["identity"] = digest(semantic_body(candidate))
    candidate["provenance_identity"] = digest(provenance_body(candidate))
    return candidate


def verify_content(candidate, expected_identity, root=ROOT):
    checks, failures = [], []
    try:
        assert expected_identity and candidate["identity"] == expected_identity == digest(semantic_body(candidate)), "CANDIDATE_IDENTITY_MISMATCH"
        assert candidate["version"] == "protected-portable-freeze-r5.94b-1"
        assert candidate["provenance_identity"] == digest(provenance_body(candidate)), "PROVENANCE_INTEGRITY_FAILURE"
        assert not candidate["active"] and not candidate["target_authorizations"], "GENERIC_CANDIDATE_AUTHORITY_CHANGED"
        entries = candidate["dependencies"]
        assert len({e["dependency"] for e in entries}) == len(entries), "DUPLICATE_DEPENDENCY"
        for entry in entries:
            assert entry["freeze_class"] in CLASSES and entry["reason"] and entry["type"], "UNCLASSIFIED_DEPENDENCY"
            kind, name = entry["freeze_class"], entry["dependency"]
            if kind in {"CANONICAL_CONTENT_PIN", "EXACT_BINARY_PIN"}:
                if entry["type"] == "canonical-structured-data":
                    assert kind == "CANONICAL_CONTENT_PIN" and entry["canonicalization"] == "CJ-1"
                    assert (name, entry["embedded_field"]) in {("experiment-semantic-envelope", "semantics"), ("worker-model-access-configuration", "models")}
                    actual = digest(candidate[entry["embedded_field"]])
                    passed = actual == entry["content_sha256"]
                    checks.append({"dependency": name, "freeze_class": kind, "passed": passed, "actual_identity": actual})
                    if not passed:
                        failures.append({"dependency": name, "reason": "EMBEDDED_PIN_MISMATCH"})
                    continue
                relative = Path(entry.get("locator", name))
                assert not relative.is_absolute() and ".." not in relative.parts, "NONPORTABLE_PIN_PATH"
                path = (root / relative).resolve()
                assert path.is_relative_to(root.resolve()), "PIN_PATH_ESCAPE"
                check = verify_entry(entry, path.read_bytes())
                checks.append(check)
                if not check["passed"]:
                    failures.append({"dependency": name, "reason": "PIN_MISMATCH"})
            elif kind == "COMPATIBILITY_CONTRACT":
                assert (name, entry["contract"]) in {("python-runtime", "PYTHON_RUNTIME_CONTRACT_V1"), ("opencode-transport", OPENCODE_CONTRACT),
                                                     ("platform-containment", "PYTHON_RUNTIME_CONTRACT_V1")}, "UNSUPPORTED_CONTRACT"
            else:
                assert name == "machine-installation-and-representation", "UNEXPECTED_PROVENANCE_DEPENDENCY"
        assert {e["dependency"] for e in entries if e["freeze_class"] == "COMPATIBILITY_CONTRACT"} == {"python-runtime", "opencode-transport", "platform-containment"}
    except (AssertionError, KeyError, OSError, ValueError, TypeError, UnicodeError) as exc:
        failures.append({"dependency": "freeze-manifest", "reason": str(exc) or type(exc).__name__})
    return {"passed": not failures, "checks": checks, "failures": failures}


def preflight(candidate, expected_identity, executable, interpreter=None):
    content = verify_content(candidate, expected_identity)
    result = {"candidate_identity": candidate.get("identity"), "eligible": False, "content": content,
              "active": False, "target_authorizations": [], "failures": list(content["failures"])}
    # Never execute changed qualification code when pin integrity failed.
    if not content["passed"]:
        return result
    runtime = verify_selected(interpreter or sys.executable)
    opencode = qualify(candidate["models"], executable)
    result.update(python=runtime, opencode=opencode,
                  actual_platform={"system": platform.system(), "release": platform.release(), "machine": platform.machine()},
                  platform_containment={"contract": "PYTHON_RUNTIME_CONTRACT_V1", "passed": runtime["status"] == "RUNTIME_COMPATIBLE"})
    if runtime["status"] != "RUNTIME_COMPATIBLE":
        result["failures"].append({"dependency": "python-runtime/platform-containment", "reason": "RUNTIME_INCOMPATIBLE", "details": runtime["failures"]})
    if opencode["status"] != "OPENCODE_COMPATIBLE":
        result["failures"].append({"dependency": "opencode-transport/model-availability", "reason": "OPENCODE_INCOMPATIBLE", "details": opencode["failures"]})
    result["eligible"] = not result["failures"]
    return result
