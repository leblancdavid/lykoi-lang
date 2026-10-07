"""Fresh current typed exposed transfer, after the generic content lock.

Capture/plan code only. Unsupported precursor/interface demands remain explicit;
partial typed predicates never grant coverage of the whole source request.
"""
import copy
import datetime
import hashlib
import json
from pathlib import Path

import importlib.util
from air_compiler.mutable_values import compose
from lykoi_pipeline import mutable_profile
from lykoi_workspace.input_corpus import parameters, staged
from lykoi_workspace.predicate_corpus import operand, compare, group, unary

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name, filename):
    s = importlib.util.spec_from_file_location(name, OUT / filename)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


generic = load("pins106transfer", "R5_106-generic.py")
prior = load("fresh105for106", "R5_105-transfer.py")
ev = load("evaluate106transfer", "R5_103-evaluate.py")
source = prior.prior.old


def captures():
    records = prior.captures()  # frozen source bundles are freshly read, no saved candidate replay
    for r in records:
        r["capture_round"] = "R5.106 current typed source interpretation after generic content lock"
        r["capture_note"] = "Fresh frozen-source bundle; current supported facts reviewed, unsupported demands retained; no inferred authority"
        if r["id"] not in ("B08", "B09", "B11", "B12", "B13"):
            continue
        case = r["id"]
        f = source.scalar_facts(); f["storage"]["version"] = 4
        if case == "B12": f["fields"][4]["domain"].append("CRITICAL")
        sf = copy.deepcopy(f); sf["storage"]["version"] = 3
        base = mutable_profile.scalar.integrate_facets(mutable_profile.scalar.extend_model(sf, copy.deepcopy(source.MODEL), allow_unchanged=True), sf)
        semantics = dict(booleans=[dict(name="archived", creation=dict(source="literal", value=False), migration=[dict(**{"from": 3}, to=4, value=False)])], guards=[], invariants=[])
        m = dict(collections=[], mutations=[], creation_pipelines=[], predicate_semantics=semantics)
        ir = compose(base, m); types = ir["value_types"]
        def field(n): return operand("field", types[n], name=n)
        def literal(n, v): return operand("literal", types[n], value=v)
        archived = compare(field("archived"), literal("archived", True))
        pending = compare(field("status"), literal("status", "pending"))
        completed = compare(field("status"), literal("status", "completed"))
        q = None
        if case == "B08":
            q = ("list-archived", {}, archived)
        if case == "B09":
            due = field("due_date")
            q = ("list-due", {"start": types["due_date"], "end": types["due_date"]}, group("and", group("not", archived), pending,
                group("not", unary("is_null", due)), compare(due, operand("parameter", types["due_date"], name="start"), "ge"), compare(due, operand("parameter", types["due_date"], name="end"), "le")))
        if case == "B11":
            semantics["guards"] = [dict(command="delete", predicate=group("or", pending, group("and", completed, archived)), error="delete_requires_archive", rejection="unchanged")]
        if case == "B12":
            due = field("due_date")
            element = {"type": "enum", "domain": types["priority"]["domain"]}
            allowed = dict(type="collection", element=element, ordering="insertion", duplicates="unique", equality="exact")
            q = ("list-urgent", {}, group("and", group("not", archived), pending, group("not", unary("is_null", due)),
                compare(due, operand("resource", types["due_date"], name="utc_clock"), "lt"), compare(field("priority"), operand("literal", allowed, value=["HIGH", "CRITICAL"]), member=True)))
        if case == "B13":
            semantics["guards"] = [dict(command="complete", predicate=group("not", archived), error="invalid_transition", rejection="unchanged")]
            m["collections"] = [dict(name="notes", element=dict(type="string", domain=[]), ordering="insertion", duplicates="allow", equality="exact", creation=dict(source="literal", value=[]), migration=[dict(**{"from": 3}, to=4, value=[])])]
            m["mutations"] = [dict(command="append-note", lookup="id", missing_error="task_not_found", changes=[dict(field="notes", input="text", operation="append", omitted="reject", missing_error="builder_only", pipeline=[dict(kind="transform", operation="trim"), staged(stage="TRANSFORMED", error="invalid_note")], invalid_error="invalid_note")], guards=[dict(predicate=group("not", archived), error="invalid_transition")], effect=dict(atomicity="single_record", persistence="atomic", rejection="unchanged"))]
        m["input_contracts"] = parameters(base, m)
        for p in m["input_contracts"]:
            if p["presence"] == "required": p["missing"] = dict(kind="cli_rejection")
        if case == "B13": m["mutations"][0]["changes"][0]["missing_error"] = None
        r["rows"] = []
        r["domains"] = dict(evaluation_scope="Requirement-local exposed transfer; partial represented components do not satisfy precursor demands", capability_profile=mutable_profile.PROFILE,
            scalar_base_model=copy.deepcopy(source.MODEL), input_value_profile="typed-input-values-1", predicate_profile="typed-predicates-1")
        def add(facet, value, profile="existing-scalar-1"):
            r["rows"].append(dict(id=case + "/" + facet, basis="STATED", derived_from=[], source_quote=r["source"], statement="R5.106 source-authorized " + facet,
                relation=dict(kind="crud", parameters=dict(profile=profile, facet=facet, value=copy.deepcopy(value)))))
        for facet, value in f.items(): add(facet, value)
        for facet, value in m.items(): add(facet, value, mutable_profile.PROFILE)
        if q:
            command, params, tree = q
            facts = dict(source=dict(collection="state_tasks", fields=types, unique_key="id"), parameters=params, predicate=tree, comparison=dict(scope="predicate_nodes"), ordering=[dict(field="created_at", direction="ASC"), dict(field="id", direction="ASC")], validation=[], inclusion=[], effect=dict(state="read_only", persistence="unchanged"), result=dict(shape="collection", cardinality="zero_or_more", no_match="empty"))
            r["domains"]["collection_store"] = dict(kind="composed_scalar", state="state_tasks")
            for facet, value in facts.items():
                r["rows"].append(dict(id=case + "/" + command + "/" + facet, basis="STATED", derived_from=[], source_quote=r["source"], statement="R5.106 authorized " + command + " " + facet, relation=dict(kind="filter_order", parameters=dict(query=command, facet=facet, value=copy.deepcopy(value)))))
        # Current predicates cannot invent a constant-write command or amend
        # existing listing interfaces. These inherited source demands remain
        # separately material, rather than disappearing because a guard is typed.
        gaps = [dict(required_capability="literal_boolean_mutation_and_existing_selection_amendments", specification=source.DEMANDS["B08"])]
        if case == "B09": gaps.append(dict(required_capability="typed_query_parameter_errors_and_preconditions", specification=dict(timestamp_error="invalid_due_date", ordered_bounds_error="invalid_window", equal_endpoints="valid", rejection="unchanged")))
        if case == "B12": gaps.append(dict(required_capability="common_predicate_resource_binding", specification=dict(resource="utc_clock", scope="sample_once_per_readonly_query", preserve="list-overdue_all_priorities")))
        for i, gap in enumerate(gaps):
            r["rows"].append(dict(id=case + "/remaining-profile-seam/" + str(i), basis="STATED", derived_from=[], source_quote=r["source"], statement="Unclosed source-authorized interface/precursor demand", relation=dict(kind="invariant", parameters=gap)))
        r["interpretation_notes"] = ["Boolean storage and predicate trees now represented, but archive's source-authorized literal write/interface is not replaced by an invented boolean input.",
            "No unsupported historical filtering demand is silently removed. Clock binding/query error authority is separate from pure comparison capability."]
    return records


def main():
    lock_path = OUT / "R5_106-GENERIC-LOCK.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    records = captures(); plans = {r["id"]: prior.plan(r) for r in records}
    for r in records:
        generic.publish("R5_106-" + r["id"] + "-CANDIDATE.json", dict(case=r["id"], producer_capture=r, external_plan=plans[r["id"]]))
    generic.publish("R5_106-CORPUS-LOCK.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases={r["id"]: hashlib.sha256((OUT / ("R5_106-" + r["id"] + "-CANDIDATE.json")).read_bytes()).hexdigest() for r in records}, implementation_lock_sha256=hashlib.sha256(lock_path.read_bytes()).hexdigest(), transfer_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), rule="All twenty captures/plans fixed before first transfer outcome"))
    results = []
    for r in records:
        x = ev.evaluate(r, plans[r["id"]]); results.append(x)
        print(x["case"], x["first_blocker"], x["native"], flush=True)
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    before = {x["case"]: x for x in json.loads((OUT / "R5_105-TRANSFER-EVIDENCE.json").read_text(encoding="utf-8"))["cases"]}
    comparison = [dict(case=x["case"], r5_105_first_blocker=before[x["case"]]["first_blocker"], r5_106_first_blocker=x["first_blocker"], native=x["native"], newly_reached=[s for s in ev.STAGES if before[x["case"]]["stages"][s] == "NOT_REACHED" and x["stages"][s] != "NOT_REACHED"], stages=x["stages"], behaviorally_verified=x["first_blocker"] == "SUCCESS", next_blocker=None if x["first_blocker"] == "SUCCESS" else x.get("terminal", {}).get("failure", x["native"])) for x in results]
    distribution = {k: sum(x["first_blocker"] == k for x in results) for k in ("FORMALIZATION", "STRUCTURAL", "BDI", "ADEQUACY", "REPRESENTATION", "AUTHORING", "COMPILATION", "RUNTIME", "BEHAVIORAL_VERIFICATION", "SUCCESS")}
    generic.publish("R5_106-TRANSFER-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), scope="Fresh current typed exposed local regression, no held-out/cumulative claim", implementation_unchanged=True, history_unchanged=True, distribution=distribution, cases=results))
    generic.publish("R5_106-COMPARISON.json", dict(distribution=distribution, cases=comparison, external_invocations=sum(x.get("external_invocations", 0) for x in results)))
    lines = ["# R5.106 — fixed exposed current typed transfer", "", "R5.105 is the preserved baseline. Exposed local regression only; no held-out/cumulative claim.", "", "| Case | R5.105 first blocker | R5.106 first blocker | Newly reached stages | Behavioral success |", "| --- | --- | --- | --- | --- |"]
    for x in comparison:
        lines.append("| " + x["case"] + " | " + x["r5_105_first_blocker"] + " | " + x["r5_106_first_blocker"] + " | " + (", ".join(x["newly_reached"]) or "None") + " | " + ("Yes" if x["behaviorally_verified"] else "No") + " |")
    lines += ["", "All stages/native blockers: `R5_106-COMPARISON.json`. Full source, reconciliation, normal pipeline and external evidence: `R5_106-TRANSFER-EVIDENCE.json`.", "", "B08/B09/B11/B12/B13 now retain typed predicate/boolean/guard components; whole coverage still refuses unclosed interface/precursor demands. No predicate component success is counted as a behavioral request success."]
    with (OUT / "R5_106-CAPABILITY-MATRIX.md").open("x", encoding="utf-8", newline="\n") as f: f.write("\n".join(lines) + "\n")


if __name__ == "__main__": main()
