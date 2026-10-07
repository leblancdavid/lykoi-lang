"""Fresh exposed source captures, fixed before results, against generic lock."""
import copy
import datetime
import hashlib
import json
from pathlib import Path

from lykoi_controller import Failure

import importlib.util

OUT = Path(__file__).resolve().parent


def load(name, file):
    s = importlib.util.spec_from_file_location(name, OUT / file)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


generic = load("generic110transfer", "R5_110-generic.py")
prior = load("capture109for110", "R5_109-transfer.py")
ev = load("evaluate110transfer", "R5_103-evaluate.py")


def captures():
    records = prior.captures()  # Fresh frozen-source reads, not saved FRC replay.
    template = next(r for r in records if r["id"] == "B16")
    for r in records:
        r["capture_round"] = "R5.110 fresh typed source-reviewed capture after generic lock"
        if r["id"] != "B18": continue
        # Preserve the qualified task/user/reference substrate. Represent the
        # residual source demand as ordinary typed state, not external events.
        r["rows"] = copy.deepcopy(template["rows"])
        r["domains"] = copy.deepcopy(template["domains"])
        for row in r["rows"]:
            row["id"] = row["id"].replace("B16/", "B18/")
            row["source_quote"] = r["source"]
        specs = {
            "numeric_history_state": dict(
                representation="ordinary_durable_ordered_record_collection",
                fields={"sequence": dict(type="integer", monotonic=True, value_authority="not_determined_by_source"), "timestamp": dict(type="timestamp", capability="declared_utc_clock", sampling="once_per_operation"), "actor": dict(type="identifier", entity="User", source="authorized_actor_input"), "operation": dict(type="enum", domain=["create", "complete", "delete", "archive", "append-note", "add-dependency"]), "task": dict(type="identifier", entity="Task", source="affected_identity")},
                cardinality_per_success=1, cardinality_per_rejection=0,
                coupling=dict(scope="one_store", primary="task_write", secondary="typed_record_create", rejection="unchanged"),
                ordering=["sequence"], migration_initial=[], query="list-audit", excluded=["create-user"],
                boundary="Normal integer durable fields/cardinality-value binding unavailable; max+1/counter successor not authorized or implemented. Ordered history alone does not satisfy numeric sequence demand."),
            "primary_actor_binding": dict(commands=["create", "complete", "delete", "archive", "append-note", "add-dependency"], parameter=dict(name="actor", type="identifier", entity="User"), presence="required", missing_error="actor_required", unknown_error="unknown_actor", before="mutation", boundary="Existing primary normal command parameters do not include B17 actor; the related-operation synthetic actor binding does not supply this precursor. Existing non-system migration role remains unanswered.")}
        for name, value in specs.items():
            r["rows"].append(dict(id="B18/" + name, basis="STATED", derived_from=[], source_quote=r["source"], statement="Source-authorized ordinary durable history boundary: " + name, relation=dict(kind="crud", parameters=dict(required_capability=name, specification=value))))
        r["interpretation_notes"] = ["Generic coupled ordinary durable records now work; no external network/event substrate is required.", "Fresh typed source demand keeps the numeric sequence and actor fields; no order-only substitution, max+1 rule, system actor default or B17 migration-role answer is invented.", "Residual unsupported typed facets must reject coverage; no authoring or behavioral success for a partial B18 representation is claimed."]
    return records


def plan(r):
    return None if r["id"] == "B18" else prior.plan(r)


def main():
    lock_path = OUT / "R5_110-GENERIC-LOCK.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    corpus_path = OUT / "R5_110-CORPUS-LOCK.json"
    if not corpus_path.exists():
        records = captures()
        for r in records: generic.publish("R5_110-" + r["id"] + "-CANDIDATE.json", dict(case=r["id"], producer_capture=r, external_plan=plan(r)))
        generic.publish(corpus_path.name, dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases={r["id"]: generic.digest(OUT / ("R5_110-" + r["id"] + "-CANDIDATE.json")) for r in records}, implementation_lock_sha256=generic.digest(lock_path), transfer_script_sha256=generic.digest(Path(__file__)), rule="All twenty source captures/oracles fixed before first outcome; resume exact bytes only"))
    corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
    assert corpus["transfer_script_sha256"] == generic.digest(Path(__file__))
    results = []
    for case, digest in corpus["cases"].items():
        path = OUT / ("R5_110-" + case + "-CANDIDATE.json")
        assert generic.digest(path) == digest
        fixed = json.loads(path.read_text(encoding="utf-8"))
        result_path = OUT / ("R5_110-" + case + "-RESULT.json")
        if result_path.exists(): x = json.loads(result_path.read_text(encoding="utf-8"))
        else:
            try: x = ev.evaluate(fixed["producer_capture"], fixed["external_plan"])
            except Failure as exc:
                stages = {s: "NOT_REACHED" for s in ev.STAGES}; stages["FORMALIZATION"] = "BLOCKED"
                x = dict(case=case, stages=stages, first_blocker="FORMALIZATION", native=exc.code, terminal=dict(outcome=exc.code, failure=exc.as_dict()))
            generic.publish(result_path.name, x)
        results.append(x)
        print(case, x["first_blocker"], x["native"], flush=True)
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    before = {x["case"]: x for x in json.loads((OUT / "R5_109-TRANSFER-EVIDENCE.json").read_text(encoding="utf-8"))["cases"]}
    comparison = [dict(case=x["case"], r5_109_blocker=before[x["case"]]["first_blocker"], r5_110_blocker=x["first_blocker"], native=x["native"], newly_reached=[s for s in ev.STAGES if before[x["case"]]["stages"][s] == "NOT_REACHED" and x["stages"][s] != "NOT_REACHED"], stages=x["stages"], behaviorally_verified=x["first_blocker"] == "SUCCESS", next_blocker=None if x["first_blocker"] == "SUCCESS" else x.get("terminal", {}).get("failure", x["native"])) for x in results]
    distribution = {k: sum(x["first_blocker"] == k for x in results) for k in ("FORMALIZATION", "STRUCTURAL", "BDI", "ADEQUACY", "REPRESENTATION", "AUTHORING", "COMPILATION", "RUNTIME", "BEHAVIORAL_VERIFICATION", "SUCCESS")}
    generic.publish("R5_110-TRANSFER-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), scope="Exposed requirement-local development/regression; not held-out or cumulative", implementation_unchanged=True, history_unchanged=True, distribution=distribution, cases=results))
    generic.publish("R5_110-COMPARISON.json", dict(distribution=distribution, external_invocations=sum(x.get("external_invocations", 0) for x in results), cases=comparison))
    lines = ["# R5.110 — frozen exposed transfer", "", "R5.109 is preserved. Exposed requirement-local regression, not held-out/cumulative evidence.", "", "| Case | R5.109 blocker | R5.110 blocker | Newly reached stages | Behavioral success |", "| --- | --- | --- | --- | --- |"]
    for x in comparison: lines.append("| " + x["case"] + " | " + x["r5_109_blocker"] + " | " + x["r5_110_blocker"] + " | " + (", ".join(x["newly_reached"]) or "None") + " | " + ("Yes" if x["behaviorally_verified"] else "No") + " |")
    lines += ["", "B18 now has ordinary typed durable-state demands rather than an external-effect label. Its required numeric sequence and inherited primary actor bindings remain unsupported; partial coverage rejects before BDI. Generic ordered history succeeds in five domains, but does not establish B18 success.", "", "Exact native/stage receipts: `R5_110-COMPARISON.json`, `R5_110-TRANSFER-EVIDENCE.json`."]
    with (OUT / "R5_110-CAPABILITY-MATRIX.md").open("x", encoding="utf-8", newline="\n") as f: f.write("\n".join(lines) + "\n")


if __name__ == "__main__": main()
