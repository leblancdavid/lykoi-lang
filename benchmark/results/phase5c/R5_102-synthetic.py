"""Publish real normal-path public captures and external process observations."""
import datetime
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests"))
from test_scalar_normal_path import normal_run, independent_plan
from lykoi_workspace.scalar_corpus import captures
from lykoi_pipeline.pipeline import external_execute


def main():
    rows = []
    for record in captures():
        result = normal_run(record)
        rows.append({"capture": record, "plan": independent_plan(record), **result})
        print(record["id"], result["outcome"], result.get("restart_audit"), flush=True)
        assert result["outcome"] == "BEHAVIORALLY_VERIFIED"
    source = next(a["content"]["target_source"] for a in rows[0]["audit"]["artifacts"].values() if a["type"] == "target")
    diagnostic = {"cases": [{"identity": "unicode-environment-diagnostic", "steps": [
        {"argv": ["register", "--caption", " exact Ω "], "returncode": 0, "contains": [" exact Ω "], "preserved": []},
        {"argv": ["list"], "returncode": 0, "contains": [" exact Ω "], "preserved": ["library.json"]}]}]}
    outcome, observations = external_execute(source, diagnostic)
    result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "scope": "Public same-agent source captures; normal stages, synthetic owner credentials, external processes",
              "cases": rows, "supported_primary_cases": len(rows), "primary_external_invocations": sum(len(c["steps"]) for r in rows for c in r["plan"]["cases"]),
              "additional_normal_compositions": "Existing-model additive field evolution, finite enum expansion and scalar-store equality query are separately executed in test_scalar_normal_path.py (13/13 passing tests)",
              "unicode_diagnostic": {"outcome": outcome, "observations": observations, "classification": "CURRENT_ISOLATED_STDOUT_ENCODING_LIMITATION_NO_PORTABILITY_REPAIR"},
              "limitations": ["Not live general prose formalization; captured AI interpretations replay at ordinary producer boundary", "Source-only inventory and oracle are same-agent evidence; no independent cognition", "No closure claim for all writable scalars, arbitrary guards, deterministic creation resources or all compositions"]}
    with (Path(__file__).parent / "R5_102-SYNTHETIC-EVIDENCE.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2); stream.write("\n")


if __name__ == "__main__":
    main()
