"""One-time evidence capture only; no Lykoi machinery or benchmark mutation."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[3]
snapshot = root / "benchmark/results/phase5c/R5_97-PRE-B03-SNAPSHOT.md"
output = root / "benchmark/results/phase5c/R5_97-B03-ACCESS.json"
assert snapshot.is_file() and not output.exists()
state = subprocess.check_output(["git", "status", "--porcelain=v1", "--untracked-files=all"], cwd=root, text=True)
started = datetime.now(timezone.utc).isoformat()
source_path = root / "benchmark/requirements/B03.md"
raw = source_path.read_bytes()
text = raw.decode("utf-8")
record = {
    "round": "R5.97", "benchmark": "B03", "source_path": "benchmark/requirements/B03.md",
    "first_access_started_utc": started,
    "access_completed_utc": datetime.now(timezone.utc).isoformat(),
    "prior_state": "HELD_OUT_UNREAD", "state": "EXPOSED_TO_FORMALIZATION",
    "snapshot_path": snapshot.relative_to(root).as_posix(),
    "snapshot_sha256": hashlib.sha256(snapshot.read_bytes()).hexdigest(),
    "source_sha256": hashlib.sha256(raw).hexdigest(), "source_byte_count": len(raw),
    "source_text": text, "text_encoding": "UTF-8; original line endings retained",
    "working_tree_at_access": state,
    "declaration": "No prior B03 inspection by this evaluation; inherited unread status per user and R5.96. B03 is permanently exposed from this access onward.",
    "model": "openai/gpt-6.1-sol", "provider": "OpenAI",
}
with output.open("x", encoding="utf-8", newline="\n") as stream:
    json.dump(record, stream, indent=2, ensure_ascii=False)
    stream.write("\n")
print(json.dumps(record, indent=2, ensure_ascii=False))
