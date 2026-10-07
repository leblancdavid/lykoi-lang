"""Read-only artifact inventory; publish compact, exclusive audit snapshots.

Uses only the standard library. Never invokes experiment drivers or rewrites
evidence. JSON/gzip measurements are computed in memory, not saved over inputs.
"""

import argparse
from collections import Counter
import datetime
import hashlib
import json
from pathlib import Path
import re
import subprocess
import zlib


ROOT = Path(__file__).resolve().parents[2]
SCOPES = ("benchmark/results", "experiments", "generated", "rehearsal")
MIB = 1024 * 1024
ENCODER = json.JSONEncoder(ensure_ascii=True, allow_nan=False, separators=(",", ":"))


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT)


def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(MIB), b""):
            digest.update(block)
    return digest.hexdigest()


def compact_size(value):
    return sum(len(chunk.encode("utf-8")) for chunk in ENCODER.iterencode(value))


def classification(path):
    if "__pycache__" in path.parts or path.suffix in (".pyc", ".pyo"):
        return "disposable_python_cache"
    if path.parts[0] == "generated":
        return "derived_backend_with_committed_regression_contract"
    if path.parts[0] == "experiments":
        return "historical_plan_model_or_execution_record_preserve"
    if "-SYNTHETIC" in path.name and path.suffix == ".json":
        return "observed_synthetic_run_with_derived_payload_preserve"
    if "-TRANSFER-EVIDENCE" in path.name or re.search(r"-B\d{2}-RESULT\.json$", path.name):
        return "observed_transfer_run_with_derived_payload_preserve"
    if path.name.endswith("-CANDIDATE.json"):
        return "captured_source_interpretation_and_plan_preserve"
    if "-LOCK" in path.name or "-AUDIT" in path.name:
        return "provenance_lock_or_integrity_record_preserve"
    if path.suffix == ".py":
        return "generator_or_reproduction_source_preserve"
    return "research_input_or_observation_preserve_pending_individual_review"


def profile(path):
    compressor = zlib.compressobj(level=6, wbits=31)
    gzip_size = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(MIB), b""):
            gzip_size += len(compressor.compress(block))
    gzip_size += len(compressor.flush())
    with path.open(encoding="utf-8") as stream:
        data = json.load(stream)
    result = {
        "compact_json_bytes": compact_size(data),
        "gzip_level_6_bytes": gzip_size,
        "top_level_compact_bytes": {k: compact_size(v) for k, v in data.items()},
        "observed_run_summary": {
            "metadata": {k: data[k] for k in ("utc", "external_invocations", "distribution", "scope", "limitations") if k in data},
            "cases": [
                {k: case[k] for k in ("case", "first_blocker", "native", "stages", "external_invocations") if k in case}
                for case in data.get("cases", []) if isinstance(case, dict)
            ],
            "status": "Extracted from preserved original bytes; not a replacement for full evidence.",
        },
    }
    cases = data.get("cases", [])
    if cases and isinstance(cases[0], dict):
        case = cases[0]
        audit = case.get("audit", {})
        by_kind = Counter()
        artifacts = audit.get("artifacts", {})
        for artifact in artifacts.values():
            by_kind[artifact.get("type", "unknown")] += compact_size(artifact)
        strings = Counter()

        def walk(value):
            if isinstance(value, str) and len(value) >= 1024:
                strings[value] += 1
            elif isinstance(value, dict):
                for item in value.values():
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        walk(case)
        repeated = sorted(
            ((len(text.encode("utf-8")) * (count - 1), text, count)
             for text, count in strings.items() if count > 1),
            reverse=True,
        )
        result["first_case_profile"] = {
            "case": case.get("case"),
            "field_compact_bytes": {k: compact_size(v) for k, v in case.items()},
            "audit_artifact_count": len(artifacts),
            "audit_artifact_compact_bytes_by_kind": dict(by_kind.most_common()),
            "largest_repeated_strings": [
                {"sha256_utf8": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                 "utf8_bytes": len(text.encode("utf-8")), "occurrences": count,
                 "duplicate_utf8_bytes": duplicate}
                for duplicate, text, count in repeated[:5]
            ],
        }
    return result


def snapshot(threshold, profile_threshold):
    tracked = set(git("ls-files", "--cached", "-z").decode("utf-8").split("\0"))
    ignored = set(git("ls-files", "--others", "--ignored", "--exclude-standard", "-z").decode("utf-8").split("\0"))
    all_files = sorted({p for scope in SCOPES for p in (ROOT / scope).rglob("*") if p.is_file()})
    groups = {}
    rows = []
    controls = []
    for path in all_files:
        name = path.relative_to(ROOT).as_posix()
        size = path.stat().st_size
        state = "tracked" if name in tracked else "ignored" if name in ignored else "untracked"
        category = classification(path.relative_to(ROOT))
        group = groups.setdefault(category, {"files": 0, "bytes": 0})
        group["files"] += 1
        group["bytes"] += size
        if size >= threshold:
            row = {"path": name, "bytes": size, "sha256": sha(path),
                   "git_state": state, "classification": category,
                   "disposition": "preserve; no deletion or ignore migration authorized"}
            if path.suffix == ".json" and size >= profile_threshold:
                row["size_profile"] = profile(path)
            rows.append(row)
        elif path.name.startswith(("R5_106-", "R5_107-")):
            controls.append({"path": name, "bytes": size, "sha256": sha(path), "git_state": state})
    dependencies = []
    for name in ("air/task_manager.json", "src/lykoi_workspace/predicate_corpus.py",
                 "src/lykoi_workspace/interface_corpus.py", "src/lykoi_pipeline/pipeline.py",
                 "benchmark/results/phase5c/R5_103-evaluate.py",
                 "benchmark/results/phase5c/R5_105-generic.py",
                 "benchmark/artifacts/audit.py"):
        path = ROOT / name
        dependencies.append({"path": name, "bytes": path.stat().st_size, "sha256": sha(path)})
    pin_checks = []
    for filename, key in (("R5_107-GENERIC-LOCK-3.json", "history"),
                          ("R5_107-FINAL-AUDIT.json", "evidence_sha256")):
        path = ROOT / "benchmark/results/phase5c" / filename
        if not path.exists():
            continue
        pins = json.loads(path.read_text(encoding="utf-8"))[key]
        missing, mismatched = [], []
        for name, expected in pins.items():
            target = ROOT / name if key == "history" else path.parent / name
            if not target.is_file():
                missing.append(name)
            elif sha(target) != expected:
                mismatched.append(name)
        pin_checks.append({"record": path.relative_to(ROOT).as_posix(), "field": key,
                           "pins": len(pins), "missing": missing, "mismatched": mismatched})
    return {
        "version": "Lykoi-artifact-storage-audit-1",
        "utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_head": git("rev-parse", "HEAD").decode().strip(),
        "working_tree_note": "Includes uncommitted files; Git HEAD alone cannot reproduce this snapshot.",
        "scopes": list(SCOPES),
        "large_threshold_bytes": threshold,
        "profile_threshold_bytes": profile_threshold,
        "summary": {"files": len(all_files), "bytes": sum(v["bytes"] for v in groups.values()),
                    "by_classification": groups},
        "large_artifacts": sorted(rows, key=lambda r: (-r["bytes"], r["path"])),
        "current_round_compact_records": controls,
        "reviewed_dependencies": dependencies,
        "historical_pin_checks": pin_checks,
        "limitations": [
            "Size and generation do not establish byte-for-byte reproducibility or permission to delete.",
            "Only large files and current-round compact records/dependencies carry per-file hashes.",
            "JSON compact/gzip sizes are measurements; original bytes were not changed.",
            "Replay produces new observations and cannot recreate original time, IDs, journals or first results.",
            "Historical replay was not run; driver prerequisites and prior code versions remain necessary.",
        ],
    }


def verify(path):
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data["large_artifacts"] + data["current_round_compact_records"] + data["reviewed_dependencies"]
    failed = []
    for row in rows:
        source = ROOT / row["path"]
        if not source.is_file() or source.stat().st_size != row["bytes"] or sha(source) != row["sha256"]:
            failed.append(row["path"])
    print(json.dumps({"verified_records": len(rows), "failed": failed}, indent=2))
    return int(bool(failed))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--output", type=Path, help="New JSON manifest; fails if it already exists")
    mode.add_argument("--verify", type=Path, help="Verify saved sizes and hashes without running experiments")
    parser.add_argument("--threshold-mib", type=int, default=1)
    parser.add_argument("--profile-mib", type=int, default=50)
    args = parser.parse_args()
    if args.verify:
        return verify(args.verify)
    if args.threshold_mib <= 0 or args.profile_mib <= 0:
        parser.error("thresholds must be positive")
    if args.output.exists() or not args.output.parent.is_dir():
        parser.error("output must be new and its parent directory must exist")
    data = snapshot(args.threshold_mib * MIB, args.profile_mib * MIB)
    with args.output.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(data, stream, indent=2)
        stream.write("\n")
    print(json.dumps({"output": str(args.output), "summary": data["summary"],
                      "large_artifacts": len(data["large_artifacts"]),
                      "historical_pin_checks": data["historical_pin_checks"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
