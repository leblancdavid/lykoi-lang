"""Read-only final content/scope audit; writes one new audit artifact exclusively."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
    assert result.returncode == 0, result.stderr
    return result.stdout


def main():
    freeze = json.loads((OUT / "R5_98-SYNTHETIC-FREEZE.json").read_text(encoding="utf-8"))
    for path, expected in freeze["files"].items():
        assert sha(ROOT / path) == expected, path
    assert sha(OUT / "R5_98-VERIFICATION.json") == freeze["verification_sha256"]
    record = json.loads((OUT / "R5_97-B03_FIRST_RESULT.json").read_text(encoding="utf-8"))
    for evidence in record["evidence"]:
        assert sha(ROOT / evidence["path"]) == evidence["sha256"], evidence["path"]
    first_sha = (OUT / "R5_97-B03_FIRST_RESULT.sha256").read_text(encoding="utf-8").split()[0]
    assert sha(OUT / "R5_97-B03_FIRST_RESULT.json") == first_sha
    verification = json.loads((OUT / "R5_98-VERIFICATION.json").read_text(encoding="utf-8"))
    summary = []
    for command in verification["commands"]:
        assert command["exit"] == 0
        counts = re.findall(r"Ran (\d+) tests?", command["stderr"])
        summary.append({"argv": command["argv"], "tests": int(counts[-1]) if counts else None, "exit": 0})
    total = sum(row["tests"] or 0 for row in summary)
    assert total == 263, total
    generic = [path for path in freeze["files"] if path.startswith("src/")]
    forbidden = []
    for path in generic:
        if re.search(r"B03|list-tag|\btags\b", (ROOT / path).read_text(encoding="utf-8")):
            forbidden.append(path)
    assert not forbidden, forbidden
    tracked_changes = git("diff", "--name-only").splitlines()
    assert set(tracked_changes) <= {"README.md", "docs/project-overview.md", "docs/decisions.md", "docs/research-log.md"}, tracked_changes
    git("diff", "--check")
    new_files = git("ls-files", "--others", "--exclude-standard").splitlines()
    allowed = lambda p: (p.startswith("src/lykoi_query/") or p in (
        "src/air_compiler/collection_query.py", "src/air_compiler/collection_query_runtime.py",
        "docs/collection-query-v0.1.md", "tests/test_collection_query.py", "tests/test_collection_query_behavior.py")
        or p.startswith("benchmark/results/phase5c/R5_98-"))
    assert all(allowed(path) for path in new_files), new_files
    whitespace = []
    for path in new_files:
        for number, line in enumerate((ROOT / path).read_text(encoding="utf-8").splitlines(), 1):
            if line.rstrip(" \t") != line:
                whitespace.append([path, number])
    assert not whitespace, whitespace
    result = {"outcome": "PASS", "head": git("rev-parse", "HEAD").strip(), "test_total": total,
              "command_summary": summary, "tracked_changes": tracked_changes, "new_files": new_files,
              "generic_forbidden_identifiers": forbidden, "whitespace_findings": whitespace,
              "frozen_generic_content_unchanged_after_transfer": True,
              "R5_97_first_result_commitment_valid": True, "R5_97_evidence_valid": 10,
              "historical_tracked_implementation_requirements_oracles_results_changed": False,
              "B04_access": "No B04 or later unexposed requirement accessed by this round; attestation, not OS enforcement"}
    with (OUT / "R5_98-AUDIT.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2)
        stream.write("\n")
    print("PASS:", total, "tests; frozen content, historical evidence, identifiers, whitespace and scope verified")


if __name__ == "__main__":
    main()
