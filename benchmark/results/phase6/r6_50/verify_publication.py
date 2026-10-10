"""Read-only R6.50 integrity checks; emits inventory/receipt, never writes files."""
import argparse
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
OLD = ROOT / "benchmark/results/phase6/r6_49"
MANIFEST = OUT / "PUBLICATION-IDENTITIES.json"
RECEIPT = OUT / "VERIFICATION.json"
REPORT = ROOT / "benchmark/results/phase6/R6_50-REPORT.md"
DOCS = [ROOT / f"docs/{name}-r6.50.md" for name in
        ("project-overview", "research-log", "decisions")]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate key {key}: {path}")
            result[key] = value
        return result

    def bad(value):
        raise ValueError(f"nonfinite JSON {value}: {path}")

    return json.loads(path.read_bytes(), object_pairs_hook=pairs, parse_constant=bad)


def inventory():
    return sorted([REPORT] + DOCS + [p for p in OUT.iterdir()
                   if p.is_file() and p not in (MANIFEST, RECEIPT)])


def baseline():
    inherited = read(OLD / "BASELINE.json")
    publication = read(OLD / "PUBLICATION-IDENTITIES.json")
    protected = dict(inherited["protected_files"])
    for name, record in publication["files"].items():
        assert (ROOT / name).stat().st_size == record["bytes"], name
        protected[name] = record["sha256"]
    old_receipt = read(OLD / "VERIFICATION.json")
    assert old_receipt["manifest_sha256"] == sha(OLD / "PUBLICATION-IDENTITIES.json")
    # Receipt hash is frozen by the new manifest's baseline_bindings.
    for name in ("PUBLICATION-IDENTITIES.json", "VERIFICATION.json"):
        path = OLD / name
        protected[path.relative_to(ROOT).as_posix()] = sha(path)
    for name, digest in protected.items():
        assert sha(ROOT / name) == digest, name
    assert inherited["kernel"] == 26
    accounting = read(ROOT / "benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json")
    assert accounting["final_count"] == 26 and accounting["additions"] == []
    index = read(OLD / "DATASET-INDEX.json")
    assert index["tier_t_count"] == 10 and index["tier_e_count"] == 0
    assert len(index["entries"]) == 10
    for entry in index["entries"]:
        assert entry["tier_t"] == "T_CANDIDATE_ADMITTED"
        assert entry["tier_e"] == "NOT_QUALIFIED"
        assert entry["partition"] == "training_development"
        assert all(entry["admission_gates"].values())
    ledger = read(OLD / "R6_48-SUCCESSOR-LEDGER.json")
    assert ledger["historical_admitted_count"] == 0 and len(ledger["entries"]) == 8
    original = read(ROOT / "benchmark/results/phase6/r6_48/TRAINING-READY-EXPORT-MANIFEST.json")
    assert original["admitted_episode_count"] == 0
    return {
        "inherited_protected_count": len(inherited["protected_files"]),
        "protected_count_including_r6_49_publication": len(protected),
        "baseline_bindings": {name: sha(OLD / name) for name in
                              ("BASELINE.json", "PUBLICATION-IDENTITIES.json", "VERIFICATION.json")},
        "kernel": 26,
        "original_r6_48_admission": 0,
        "successor_tier_t": 10,
        "tier_e": 0,
    }


def make_manifest():
    return {"round": "R6.50", "excluded": [MANIFEST.name, RECEIPT.name],
            "baseline": baseline(),
            "files": {p.relative_to(ROOT).as_posix():
                      {"sha256": sha(p), "bytes": p.stat().st_size} for p in inventory()}}


def walk_schema(value, schema):
    count = 0
    if isinstance(value, dict):
        if "$ref" in value:
            ref = value["$ref"]
            assert ref.startswith("#/"), ref
            node = schema
            for key in ref[2:].split("/"):
                node = node[key.replace("~1", "/").replace("~0", "~")]
            assert isinstance(node, dict)
            count += 1
        if value.get("type") == "object" and "required" in value:
            assert set(value["required"]) <= set(value.get("properties", {}))
        for child in value.values():
            count += walk_schema(child, schema)
    elif isinstance(value, list):
        for child in value:
            count += walk_schema(child, schema)
    return count


def verify():
    manifest = read(MANIFEST)
    assert manifest == make_manifest(), "publication/baseline identity mismatch"
    status = read(OUT / "STATUS.json")
    assert status["classification"] == "R6_50_INDEPENDENT_EVALUATION_GAP"
    assert not status["custody_enforceable"] and status["human_commissioner"] is None
    schema = read(OUT / "paired-example-1.schema.json")
    assert schema["$id"] == "urn:lykoi:paired-example:1"
    assert set(schema["required"]) == set(schema["properties"])
    refs = walk_schema(schema, schema)
    links = 0
    for path in inventory():
        text = path.read_text(encoding="utf-8")
        data = path.read_bytes()
        assert data.endswith(b"\n") and b"\r" not in data, path
        assert not any(line.endswith((" ", "\t")) for line in text.splitlines()), path
        assert not re.search(r"(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})", text), path
        if path.suffix == ".json":
            read(path)
        if path.suffix == ".py":
            compile(text, str(path), "exec")
        if path.suffix == ".md":
            for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
                if "://" in target or target.startswith("#"):
                    continue
                resolved = (path.parent / target.split("#")[0]).resolve()
                assert resolved.is_relative_to(ROOT)
                assert resolved.exists() or resolved == RECEIPT, (path, target)
                links += 1
    assert not subprocess.check_output(["git", "diff", "--name-only"], cwd=ROOT, text=True).strip()
    git_status = subprocess.check_output(["git", "status", "--porcelain", "--untracked-files=all"], cwd=ROOT, text=True)
    allowed = set(manifest["files"]) | {p.relative_to(ROOT).as_posix() for p in (MANIFEST, RECEIPT)}
    for line in git_status.splitlines():
        assert line.startswith("?? ") and line[3:].replace("\\", "/") in allowed, line
    diff = subprocess.run(["git", "diff", "--check"], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    return {"passed": True, "classification": status["classification"],
            "manifest_sha256": sha(MANIFEST), **manifest["baseline"],
            "publication_payload_files": len(manifest["files"]),
            "publication_payload_bytes": sum(row["bytes"] for row in manifest["files"].values()),
            "local_schema_refs_checked": refs, "relative_links_checked": links,
            "schema_check_scope": "strict JSON, local refs and required/property consistency; no full JSON Schema validator or dataset execution",
            "preservation_failures": [], "tracked_diff_empty": True,
            "new_file_whitespace_and_credential_patterns_checked": True,
            "git_diff_check_returncode": diff.returncode,
            "historical_acceptance_executions": 0, "training_runs": 0,
            "independent_commissioning_established": False, "custody_enforceable": False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=("inventory", "receipt", "check"))
    args = parser.parse_args()
    if args.mode == "inventory":
        result = make_manifest()
    else:
        result = verify()
        if args.mode == "check":
            assert result == read(RECEIPT), "receipt mismatch"
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
