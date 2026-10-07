"""Evaluate the exact locked canonical JSON corpus after capture interruption.

No candidate, plan, implementation or historical result is edited by this script.
"""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("transfer106locked", OUT / "R5_106-transfer.py")
t = importlib.util.module_from_spec(s); s.loader.exec_module(t)
generic, ev = t.generic, t.ev


def main():
    lock_path = OUT / "R5_106-GENERIC-LOCK.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    corpus = json.loads((OUT / "R5_106-CORPUS-LOCK.json").read_text(encoding="utf-8"))
    assert hashlib.sha256(lock_path.read_bytes()).hexdigest() == corpus["implementation_lock_sha256"]
    assert hashlib.sha256((OUT / "R5_106-transfer.py").read_bytes()).hexdigest() == corpus["transfer_script_sha256"]
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    saved = []
    for case, sha in corpus["cases"].items():
        path = OUT / ("R5_106-" + case + "-CANDIDATE.json")
        assert hashlib.sha256(path.read_bytes()).hexdigest() == sha
        saved.append(json.loads(path.read_text(encoding="utf-8")))
    generic.publish("R5_106-TRANSFER-RESUME-LOCK.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), corpus_lock_sha256=hashlib.sha256((OUT / "R5_106-CORPUS-LOCK.json").read_bytes()).hexdigest(), resume_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), rule="Execute exact locked canonical JSON captures/plans; no post-outcome product repair"))
    results = []
    for record in saved:
        x = ev.evaluate(record["producer_capture"], record["external_plan"]); results.append(x)
        print(x["case"], x["first_blocker"], x["native"], flush=True)
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    before = {x["case"]: x for x in json.loads((OUT / "R5_105-TRANSFER-EVIDENCE.json").read_text(encoding="utf-8"))["cases"]}
    comparison = [dict(case=x["case"], r5_105_first_blocker=before[x["case"]]["first_blocker"], r5_106_first_blocker=x["first_blocker"], native=x["native"], newly_reached=[s for s in ev.STAGES if before[x["case"]]["stages"][s] == "NOT_REACHED" and x["stages"][s] != "NOT_REACHED"], stages=x["stages"], behaviorally_verified=x["first_blocker"] == "SUCCESS", next_blocker=None if x["first_blocker"] == "SUCCESS" else x.get("terminal", {}).get("failure", x["native"])) for x in results]
    distribution = {k: sum(x["first_blocker"] == k for x in results) for k in ("FORMALIZATION", "STRUCTURAL", "BDI", "ADEQUACY", "REPRESENTATION", "AUTHORING", "COMPILATION", "RUNTIME", "BEHAVIORAL_VERIFICATION", "SUCCESS")}
    generic.publish("R5_106-TRANSFER-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), scope="Fresh current typed exposed local regression, no held-out/cumulative claim", implementation_unchanged=True, history_unchanged=True, candidates_unchanged=True, interruption="R5_106-TRANSFER-INTERRUPTION.json", distribution=distribution, cases=results))
    generic.publish("R5_106-COMPARISON.json", dict(distribution=distribution, cases=comparison, external_invocations=sum(x.get("external_invocations", 0) for x in results)))
    lines = ["# R5.106 — fixed exposed current typed transfer", "", "R5.105 is the preserved baseline. Exposed local regression only; no held-out/cumulative claim.", "", "| Case | R5.105 first blocker | R5.106 first blocker | Newly reached stages | Behavioral success |", "| --- | --- | --- | --- | --- |"]
    for x in comparison:
        lines.append("| " + x["case"] + " | " + x["r5_105_first_blocker"] + " | " + x["r5_106_first_blocker"] + " | " + (", ".join(x["newly_reached"]) or "None") + " | " + ("Yes" if x["behaviorally_verified"] else "No") + " |")
    lines += ["", "All stages/native blockers: `R5_106-COMPARISON.json`. Full source, reconciliation, normal pipeline and external evidence: `R5_106-TRANSFER-EVIDENCE.json`.", "", "B08/B09/B11/B12/B13 now retain typed predicate/boolean/guard components; whole coverage still refuses unclosed interface/precursor demands. Partial component representation is not counted as behavioral success.", "", "The initial in-memory producer canonicalization interruption is preserved in `R5_106-TRANSFER-INTERRUPTION.json`; this completed evaluation reads the original locked candidate bytes."]
    with (OUT / "R5_106-CAPABILITY-MATRIX.md").open("x", encoding="utf-8", newline="\n") as f: f.write("\n".join(lines) + "\n")


if __name__ == "__main__": main()
