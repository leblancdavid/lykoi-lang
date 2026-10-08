"""Fresh frozen-source typed captures after generic lock; authority halts preserved."""
import datetime
import importlib.util
import json
from pathlib import Path

from lykoi_controller import Failure

OUT = Path(__file__).resolve().parent


def load(name, file):
    s = importlib.util.spec_from_file_location(name, OUT / file)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


generic = load("generic114transfer", "R5_114-generic.py")
prior = load("capture113for114", "R5_113-transfer.py")
ev = load("evaluate114transfer", "R5_103-evaluate.py")


def captures():
    records = prior.captures()  # Producer re-reads actual sources; no saved FRC replay.
    for r in records:
        r["capture_round"] = "R5.114 fresh typed source-reviewed capture after generic lock"
        if r["id"] in ("B18", "B19"):
            r["interpretation_notes"].append("R5.114 now supports explicit historical related-state migration, but this source still supplies no non-system historical role authority. No migration value, trusted principal or downstream success is invented.")
    return records


def main():
    lock_path = OUT / "R5_114-GENERIC-LOCK.json"; lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    corpus_path = OUT / "R5_114-CORPUS-LOCK.json"
    if not corpus_path.exists():
        records = captures()
        for r in records: generic.publish("R5_114-" + r["id"] + "-CANDIDATE.json", dict(case=r["id"], producer_capture=r, external_plan=prior.plan(r)))
        generic.publish(corpus_path.name, dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases={r["id"]: generic.digest(OUT / ("R5_114-" + r["id"] + "-CANDIDATE.json")) for r in records}, implementation_lock_sha256=generic.digest(lock_path), transfer_script_sha256=generic.digest(Path(__file__)), rule="Twenty fresh source captures/plans fixed before first outcome"))
    corpus = json.loads(corpus_path.read_text(encoding="utf-8")); assert corpus["transfer_script_sha256"] == generic.digest(Path(__file__))
    results = []
    for case, digest in corpus["cases"].items():
        path = OUT / ("R5_114-" + case + "-CANDIDATE.json"); assert generic.digest(path) == digest
        fixed = json.loads(path.read_text(encoding="utf-8")); result_path = OUT / ("R5_114-" + case + "-RESULT.json")
        if result_path.exists(): x = json.loads(result_path.read_text(encoding="utf-8"))
        else:
            try: x = ev.evaluate(fixed["producer_capture"], fixed["external_plan"])
            except Failure as exc:
                stages = {s: "NOT_REACHED" for s in ev.STAGES}; stages["FORMALIZATION"] = "BLOCKED"
                x = dict(case=case, stages=stages, first_blocker="FORMALIZATION", native=exc.code, terminal=dict(outcome=exc.code, failure=exc.as_dict()))
            generic.publish(result_path.name, x)
        results.append(x); print(case, x["first_blocker"], x["native"], flush=True)
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    before = {x["case"]: x for x in json.loads((OUT / "R5_113-TRANSFER-EVIDENCE.json").read_text(encoding="utf-8"))["cases"]}
    comparison = [dict(case=x["case"], r5_113_blocker=before[x["case"]]["first_blocker"], r5_114_blocker=x["first_blocker"], native=x["native"], newly_reached=[s for s in ev.STAGES if before[x["case"]]["stages"][s] == "NOT_REACHED" and x["stages"][s] != "NOT_REACHED"], stages=x["stages"], behaviorally_verified=x["first_blocker"] == "SUCCESS") for x in results]
    distribution = {k: sum(x["first_blocker"] == k for x in results) for k in ("FORMALIZATION", "STRUCTURAL", "BDI", "ADEQUACY", "REPRESENTATION", "AUTHORING", "COMPILATION", "RUNTIME", "BEHAVIORAL_VERIFICATION", "SUCCESS")}
    generic.publish("R5_114-TRANSFER-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), scope="Exposed requirement-local regression, not held-out/cumulative", implementation_unchanged=True, history_unchanged=True, distribution=distribution, cases=results))
    generic.publish("R5_114-COMPARISON.json", dict(distribution=distribution, external_invocations=sum(x.get("external_invocations", 0) for x in results), cases=comparison))
    lines = ["# R5.114 — locked exposed transfer", "", "R5.113 preserved. Fresh typed source re-read, exposed regression, not held-out/cumulative evidence.", "", "| Case | R5.113 blocker | R5.114 blocker | Newly reached stages | Behavioral success |", "| --- | --- | --- | --- | --- |"]
    for x in comparison: lines.append("| " + x["case"] + " | " + x["r5_113_blocker"] + " | " + x["r5_114_blocker"] + " | " + (", ".join(x["newly_reached"]) or "None") + " | " + ("Yes" if x["behaviorally_verified"] else "No") + " |")
    lines += ["", "B17/B18/B19 retain unanswered non-system historical role authority; B20 retains unknown-member error ambiguity. New-user defaults, synthetic assumptions and conventional oracle outputs supply no answer. B18/B19 downstream stages remain NOT_REACHED. Exact receipts: `R5_114-COMPARISON.json` and `R5_114-TRANSFER-EVIDENCE.json`."]
    with (OUT / "R5_114-CAPABILITY-MATRIX.md").open("x", encoding="utf-8", newline="\n") as f: f.write("\n".join(lines) + "\n")


if __name__ == "__main__": main()
