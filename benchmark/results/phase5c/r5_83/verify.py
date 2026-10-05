"""Verify only the frozen public R5.83 evidence; stdout, no protected inspection."""
import json

from benchmark.results.phase5c.r5_83.audit import ROOT, run


def verify():
    snapshot = ROOT / "benchmark/results/phase5c/r5_83/audit.json"
    expected = json.loads(snapshot.read_text(encoding="utf-8"))
    observed = run()
    if observed != expected:
        raise ValueError("R5.83 audit evidence or pinned ordinary components drifted")
    print(json.dumps({"R5_83_evidence_reproduction": "PASS",
                      "ordinary_component_pins": len(observed["pins_exact_physical_sha256"]),
                      "classification": observed["classification"],
                      "protected_access": "NOT_PERFORMED"}, indent=2))


if __name__ == "__main__":
    verify()
