"""Evidence-only post-report audit. Never opens B03 or calls evaluation APIs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
result_path = OUT / "R5_97-B03_FIRST_RESULT.json"
result_bytes = result_path.read_bytes()
result = json.loads(result_bytes)
result_hash = hashlib.sha256(result_bytes).hexdigest()
assert (OUT / "R5_97-B03_FIRST_RESULT.sha256").read_text(encoding="ascii").split()[0] == result_hash
checks = []
for entry in result["evidence"]:
    path = ROOT / entry["path"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], entry["path"]
    checks.append({"path": entry["path"], "sha256": entry["sha256"], "status": "MATCH"})

access = json.loads((OUT / "R5_97-B03-ACCESS.json").read_text(encoding="utf-8"))
frc = json.loads((OUT / "R5_97-FRC.json").read_text(encoding="utf-8"))
soi = json.loads((OUT / "R5_97-SOI.json").read_text(encoding="utf-8"))
assert access["source_text"] == frc["source"]["text"]
assert hashlib.sha256(access["source_text"].encode()).hexdigest() == result["source_sha256"]
canonical = json.dumps(frc, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False).encode()
assert hashlib.sha256(canonical).hexdigest() == result["frc_commitment"]
text = access["source_text"]
for item in soi["items"]:
    for span in item["spans"]:
        assert text[span["start"]:span["end"]] == span["quote"]
assert "".join(line["quote"] for line in soi["source_lines"]) == text
assert len(frc["obligations"]) == len(soi["items"]) == 9
assert {o["id"] for o in frc["obligations"]} == set(result["affected_obligations"])
assert not frc["issues"]
assert all(value == "NOT_RUN" for value in result["downstream"].values())
assert result["B03_FIRST_RESULT"] == "DECISION_DISCOVERY_UNSUPPORTED"
assert result["native_result"]["code"] == "STRUCTURAL_COVERAGE_FAILURE"

snapshot = (OUT / "R5_97-PRE-B03-SNAPSHOT.md").read_text(encoding="utf-8")
assert sum(map(int, re.findall(r"Ran (\d+) tests", snapshot))) == 190
assert snapshot.count("Exit code: 0") == 10
assert "ALL SELECTED CHECKS PASSED" in snapshot
finished = re.search(r"Finished \(UTC\): (\S+)", snapshot).group(1)
assert datetime.fromisoformat(finished) < datetime.fromisoformat(access["first_access_started_utc"])
assert datetime.fromisoformat(access["first_access_started_utc"]) < datetime.fromisoformat(result["recorded_utc"])

tracked = subprocess.check_output(["git", "diff", "--name-only", "HEAD"], cwd=ROOT, text=True).splitlines()
allowed = {"AGENTS.md", "README.md", "benchmark/README.md", "docs/agent-workflow.md",
           "docs/project-overview.md", "docs/decisions.md", "docs/research-log.md"}
assert set(tracked) <= allowed, tracked
untracked = subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard"], cwd=ROOT, text=True).splitlines()
assert all(path.startswith("benchmark/results/phase5c/R5_97-") for path in untracked), untracked
status = subprocess.check_output(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=ROOT, text=True)
report_path = OUT / "R5_97-B03-HELD-OUT-EVALUATION.md"
report = report_path.read_text(encoding="utf-8")
links = re.findall(r"\]\(([^)]+)\)", report)
assert all((OUT / link).is_file() for link in links), links
audit = {
    "round": "R5.97", "audit": "EVIDENCE_ONLY_NO_EVALUATION_REPLAY", "status": "PASS",
    "utc": datetime.now(timezone.utc).isoformat(), "first_result_sha256": result_hash,
    "evidence_checks": checks, "source_text_and_span_bindings": "MATCH",
    "pre_access_baseline": "190/190 tests; ten exit-zero checks; snapshot completed before first access",
    "machinery_changed": False, "tracked_changes": tracked, "working_tree": status,
    "report_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
    "report_local_links": links, "downstream": result["downstream"],
    "source_reads_in_this_audit": 0, "evaluation_function_calls_in_this_audit": 0,
    "audit_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
}
with (OUT / "R5_97-AUDIT.json").open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(audit, stream, indent=2, ensure_ascii=False)
    stream.write("\n")
print("PASS: first-result commitment, all ten evidence commitments, source/FRC/span bindings, snapshot chronology, report links, and unchanged machinery. No B03 reread or evaluation replay.")
print("First-result SHA-256: " + result_hash)
