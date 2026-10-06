"""Publish public R5.87 example and read-only known public LF diagnostics."""
from pathlib import Path
import json
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "src"), str(ROOT)]

from lykoi_workspace.example import demonstrate, render_transcript
from benchmark.results.phase5c.r5_86.demonstrate import checkout_diagnostics


def evidence():
    with tempfile.TemporaryDirectory() as tmp:
        result = demonstrate(Path(tmp) / "public.sqlite")
    diagnostics = checkout_diagnostics()
    assert all(d["lf_matches_historical_pin"] for d in diagnostics.values())
    return {"example": result, "transcript": render_transcript(result),
            "read_only_public_checkout_diagnostics": diagnostics,
            "B03": {"PRISTINE": True, "NOT_EVALUATED": True,
                    "NOT_EXPOSED_TO_LYKOI_DEVELOPMENT": True,
                    "all_session_access_and_activity_counters": 0,
                    "basis": "Inherited status and public-only round activity; no protected inspection"},
            "R5.83-CANDIDATE-1": "UNACTIVATED"}


if __name__ == "__main__":
    result = evidence()
    if len(sys.argv) == 2 and sys.argv[1] == "--publish":
        target = Path(__file__).with_name("example-evidence.json")
        if target.exists():
            raise FileExistsError("Prospective evidence is published once; do not overwrite")
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))
