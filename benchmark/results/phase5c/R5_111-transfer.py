"""Fresh exposed source captures and fixed plans against R5.111 generic lock."""
import copy
import datetime
import json
from pathlib import Path
import importlib.util

from air_compiler.computation import INTEGER, TIME
from air_compiler.references import identity, erase
from lykoi_controller import Failure
from lykoi_workspace.predicate_corpus import operand, compare

OUT = Path(__file__).resolve().parent


def load(name, file):
    s = importlib.util.spec_from_file_location(name, OUT / file)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


generic = load("generic111transfer", "R5_111-generic.py")
prior = load("capture110for111", "R5_110-transfer.py")
ev = load("evaluate111transfer", "R5_103-evaluate.py")


def captures():
    records = prior.captures()  # Re-read frozen sources; do not replay saved FRCs.
    for r in records:
        r["capture_round"] = "R5.111 fresh typed source-reviewed capture after generic lock"
        if r["id"] == "B18":
            # Numeric durable schema is now representable. Full operation coupling
            # is kept unsupported with the inherited actor interface, rather than
            # supplying an invented system actor or partial behavioural plan.
            row = next(o for o in r["rows"] if o["relation"]["parameters"].get("facet") == "reference_semantics")
            refs = row["relation"]["parameters"]["value"]
            audit = "AuditHistory"
            fields = dict(id=identity(audit), sequence=INTEGER, timestamp=TIME, actor=identity("User"), operation=dict(type="enum", domain=["create", "complete", "delete", "archive", "append-note", "add-dependency"]), task=identity("Task"))
            refs["entities"].append(dict(name=audit, key="id", fields=fields, initial=[]))
            refs["references"] += [dict(entity=audit, field="actor", target="User", existence=dict(policy="required", error="unknown_actor"), deletion=dict(policy="unavailable", error=None), migration=None), dict(entity=audit, field="task", target="Task", existence=dict(policy="unchecked", error=None), deletion=dict(policy="permit", error=None), migration=None)]
            qfields = {n: erase(t) for n, t in fields.items()}
            q = dict(id="list-audit", source=dict(collection=audit, fields=qfields, unique_key="id"), parameters={}, predicate=compare(operand("field", INTEGER, name="sequence"), operand("field", INTEGER, name="sequence")), comparison=dict(scope="predicate_nodes"), ordering=[dict(field="sequence", direction="ASC"), dict(field="id", direction="ASC")], validation=[], inclusion=[], effect=dict(state="read_only", persistence="unchanged"), result=dict(shape="collection", cardinality="zero_or_more", no_match="empty"))
            from air_compiler.atomic_state import COMMIT
            r["rows"].append(dict(id="B18/atomic_state_semantics", basis="STATED", derived_from=[], source_quote=r["source"], statement="Ordinary integer-valued audit schema, empty migration and sequence-order read; full success coupling remains in unresolved primary actor integration demand", relation=dict(kind="crud", parameters=dict(profile="typed-mutable-values-1", facet="atomic_state_semantics", value=dict(operations=[], queries=[q], append_only=[audit], commit=copy.deepcopy(COMMIT))))))
            r["domains"].update(computation_profile="typed-computation-1", atomic_state_profile="atomic-durable-state-1")
            residual = next(o for o in r["rows"] if o["id"] == "B18/numeric_history_state")
            residual["id"] = "B18/primary_history_integration"
            residual["relation"]["parameters"]["required_capability"] = "primary_history_integration"
            spec = residual["relation"]["parameters"]["specification"]
            spec["boundary"] = "Integer fields/cardinality plus one are generically executable. Complete primary mutation history needs inherited required actor binding; existing legacy primary parameter authority cannot express it. No complete coupled-operation graph or behavioral success claimed."
            spec["fields"]["sequence"]["value_authority"] = "Monotonic demand can be met by whole append-only pre-operation cardinality + 1 under exclusive operation, empty initial history and one successful row; this is an implementation policy, not an exact source max+1 requirement."
            r["interpretation_notes"] = ["Numeric history works generically without Event, but full B18 primary/actor integration is not closed.", "Typed numeric schema and sequence read represented; success-only coupled creations for all affected primary commands remain an explicit unsupported demand.", "No system actor or B17 migration-role answer invented; no partial B18 external success claimed."]
        if r["id"] == "B19":
            # Keep the complete source demand and unsupported typed requirement,
            # refining its diagnosis without marking unreachable stages passed.
            r["interpretation_notes"] = ["Checked integer addition and fixed typed duration displacement now execute generically.", "B19 requires nullable recurrence-days on existing primary creation/migration, positive runtime N UTC days, preserved primary successor fields/fresh ID and clock, empty dependencies, and ordered actor-attributed dual audit entries.", "No runtime day-to-second conversion, nullable primary integer introduction, primary same-entity coupled creation or inherited actor interface is implemented. Full contract remains structurally unsupported; synthetic related successor is not B19 success."]
    return records


def plan(r): return None if r["id"] in ("B18", "B19") else prior.plan(r)


def main():
    lock_path = OUT / "R5_111-GENERIC-LOCK.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    corpus_path = OUT / "R5_111-CORPUS-LOCK.json"
    if not corpus_path.exists():
        records = captures()
        for r in records: generic.publish("R5_111-" + r["id"] + "-CANDIDATE.json", dict(case=r["id"], producer_capture=r, external_plan=plan(r)))
        generic.publish(corpus_path.name, dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases={r["id"]: generic.digest(OUT / ("R5_111-" + r["id"] + "-CANDIDATE.json")) for r in records}, implementation_lock_sha256=generic.digest(lock_path), transfer_script_sha256=generic.digest(Path(__file__)), rule="All twenty captures/plans fixed before first outcome; no saved candidate or generic repair"))
    corpus = json.loads(corpus_path.read_text(encoding="utf-8")); results = []
    assert corpus["transfer_script_sha256"] == generic.digest(Path(__file__))
    for case, digest in corpus["cases"].items():
        path = OUT / ("R5_111-" + case + "-CANDIDATE.json"); assert generic.digest(path) == digest
        fixed = json.loads(path.read_text(encoding="utf-8")); result_path = OUT / ("R5_111-" + case + "-RESULT.json")
        if result_path.exists(): x = json.loads(result_path.read_text(encoding="utf-8"))
        else:
            try: x = ev.evaluate(fixed["producer_capture"], fixed["external_plan"])
            except Failure as exc:
                stages = {s: "NOT_REACHED" for s in ev.STAGES}; stages["FORMALIZATION"] = "BLOCKED"
                x = dict(case=case, stages=stages, first_blocker="FORMALIZATION", native=exc.code, terminal=dict(outcome=exc.code, failure=exc.as_dict()))
            generic.publish(result_path.name, x)
        results.append(x); print(case, x["first_blocker"], x["native"], flush=True)
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    before = {x["case"]: x for x in json.loads((OUT / "R5_110-TRANSFER-EVIDENCE.json").read_text(encoding="utf-8"))["cases"]}
    comparison = [dict(case=x["case"], r5_110_blocker=before[x["case"]]["first_blocker"], r5_111_blocker=x["first_blocker"], native=x["native"], newly_reached=[s for s in ev.STAGES if before[x["case"]]["stages"][s] == "NOT_REACHED" and x["stages"][s] != "NOT_REACHED"], stages=x["stages"], behaviorally_verified=x["first_blocker"] == "SUCCESS", terminal=x.get("terminal")) for x in results]
    distribution = {k: sum(x["first_blocker"] == k for x in results) for k in ("FORMALIZATION", "STRUCTURAL", "BDI", "ADEQUACY", "REPRESENTATION", "AUTHORING", "COMPILATION", "RUNTIME", "BEHAVIORAL_VERIFICATION", "SUCCESS")}
    generic.publish("R5_111-TRANSFER-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), scope="Exposed requirement-local regression, not held-out or cumulative", implementation_unchanged=True, history_unchanged=True, distribution=distribution, cases=results))
    generic.publish("R5_111-COMPARISON.json", dict(distribution=distribution, external_invocations=sum(x.get("external_invocations", 0) for x in results), cases=comparison))
    lines = ["# R5.111 — frozen exposed transfer", "", "R5.110 preserved. Fresh exposed requirement-local regression, not held-out/cumulative evidence.", "", "| Case | R5.110 blocker | R5.111 blocker | Newly reached stages | Behavioral success |", "| --- | --- | --- | --- | --- |"]
    for x in comparison: lines.append("| " + x["case"] + " | " + x["r5_110_blocker"] + " | " + x["r5_111_blocker"] + " | " + (", ".join(x["newly_reached"]) or "None") + " | " + ("Yes" if x["behaviorally_verified"] else "No") + " |")
    lines += ["", "B18 numeric schema/cardinality computation works generically; inherited primary actor and complete primary-history integration remain structural. B19 needs nullable primary integer inputs, runtime UTC-day conversion, same-primary successor creation and actor/history integration. No downstream B18/B19 stage progress or success claimed. B17/B20 authority disputes remain.", "", "Native/stage receipts: `R5_111-COMPARISON.json`, `R5_111-TRANSFER-EVIDENCE.json`."]
    with (OUT / "R5_111-CAPABILITY-MATRIX.md").open("x", encoding="utf-8", newline="\n") as f: f.write("\n".join(lines) + "\n")


if __name__ == "__main__": main()
