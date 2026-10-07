"""Fresh exposed captures and literal external plans against generic lock 3."""
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

from air_compiler.mutable_values import compose
from air_compiler.query_interfaces import listing
from lykoi_controller import Failure, canonical
from lykoi_pipeline import mutable_profile
from lykoi_workspace.interface_corpus import amend, literal_change
from lykoi_workspace.input_corpus import parameters, staged
from lykoi_workspace.predicate_corpus import operand, compare, group, unary

OUT = Path(__file__).resolve().parent


def load(name, file):
    s = importlib.util.spec_from_file_location(name, OUT / file)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


generic = load("generic107transfer", "R5_107-generic.py")
prior = load("capture106for107", "R5_106-transfer.py")
ev = load("evaluate107transfer", "R5_103-evaluate.py")
source = prior.source
TARGETS = ("B08", "B09", "B11", "B12", "B13")


def captures():
    records = prior.captures()
    for r in records:
        r["capture_round"] = "R5.107 fresh source-reviewed typed capture after final generic lock 3"
        r["capture_note"] = "Frozen source files freshly read; supported facts reviewed in current semantics, never saved FRC replay"
        if r["id"] not in TARGETS: continue
        case = r["id"]
        f = source.scalar_facts(); f["storage"]["version"] = 4
        f["fields"][4]["domain"].append("CRITICAL")
        for n in ("source", "category"):
            f["fields"].append(dict(name=n, type="string", domain=[], nullable=False, preservation="verbatim"))
            f["creation"]["bindings"].append(dict(field=n, source="input", value=None, default=dict(value="", trigger="omitted", boundary="creation")))
        f["evolution"].append(dict(**{"from": 3}, to=4, defaults={"source": "", "category": ""}, boundary="explicit_migration", preservation="unrelated_fields"))
        base = mutable_profile.scalar.lower(f, copy.deepcopy(source.MODEL))
        semantics = dict(booleans=[dict(name="archived", creation=dict(source="literal", value=False), migration=[dict(**{"from": 3}, to=4, value=False)])], guards=[], invariants=[])
        m = dict(collections=[dict(name=n, element=dict(type="string", domain=[]), ordering="insertion", duplicates="unique" if n == "tags" else "allow", equality="exact",
            creation=dict(input="tag", encoding="repeated", default=[], pipeline=[dict(kind="map_elements", pipeline=[dict(kind="transform", operation="trim"), staged(stage="TRANSFORMED", error="invalid_tag")]), dict(kind="transform", operation="stable_deduplicate")], error="invalid_tag") if n == "tags" else dict(source="literal", value=[]),
            migration=[dict(**{"from": 3}, to=4, value=[])]) for n in ("tags", "notes")], mutations=[], creation_pipelines=[dict(field="category", pipeline=[dict(kind="transform", operation="trim"), staged(stage="TRANSFORMED", predicate="nonempty", error="invalid_category")], error="invalid_category")], predicate_semantics=semantics)
        types = compose(base, m)["value_types"]
        def field(n): return operand("field", types[n], name=n)
        def literal(n, v): return operand("literal", types[n], value=v)
        archived = compare(field("archived"), literal("archived", True))
        visible = group("not", archived)
        pending = compare(field("status"), literal("status", "pending"))
        completed = compare(field("status"), literal("status", "completed"))
        effect = dict(atomicity="single_record", persistence="atomic", rejection="unchanged")
        m["mutations"] = [dict(command="archive", lookup="id", missing_error="task_not_found", changes=[literal_change("archived", types["archived"], True)], guards=[dict(predicate=visible, error="invalid_transition")], effect=effect),
            dict(command="append-note", lookup="id", missing_error="task_not_found", changes=[dict(field="notes", input="text", operation="append", omitted="reject", missing_error="builder_only", pipeline=[dict(kind="transform", operation="trim"), staged(stage="TRANSFORMED", error="invalid_note")], invalid_error="invalid_note")], guards=[dict(predicate=visible, error="invalid_transition")] if case == "B13" else [], effect=effect)]
        if case in ("B11", "B13"):
            semantics["guards"].append(dict(command="delete", predicate=group("or", pending, group("and", completed, archived)), error="delete_requires_archive", rejection="unchanged"))
        if case == "B13":
            semantics["guards"].append(dict(command="complete", predicate=visible, error="invalid_transition", rejection="unchanged"))
        m["input_contracts"] = parameters(base, m)
        for p in m["input_contracts"]:
            if p["presence"] == "required": p["missing"] = dict(kind="cli_rejection")
        m["mutations"][1]["changes"][0]["missing_error"] = None
        def query(command, params, tree, **extra):
            return dict(id=command, source=dict(collection="state_tasks", fields=copy.deepcopy(types), unique_key="id"), parameters=params, predicate=tree, comparison=dict(scope="predicate_nodes"), ordering=[dict(field="created_at", direction="ASC"), dict(field="id", direction="ASC")], validation=[], inclusion=[], effect=dict(state="read_only", persistence="unchanged"), result=dict(shape="collection", cardinality="zero_or_more", no_match="empty"), **extra)
        queries = {token: amend(listing(base, types, token), visible) for token in ("list", "list-high", "list-overdue")}
        for command, n, parameter, membership in (("list-tag", "tags", "tag", True), ("list-status", "status", "status", False), ("list-category", "category", "category", False)):
            typ = types[n]["element"] if membership else types[n]
            p = operand("parameter", typ, name=parameter)
            tree = compare(p, field(n), member=True) if membership else compare(field(n), p)
            q = query(command, {parameter: typ}, tree)
            if membership: q["validation"] = [dict(parameter="tag", rule="nonblank", error="invalid_tag")]
            queries[command] = amend(q, visible)
        queries["list-archived"] = query("list-archived", {}, archived)
        if case == "B09":
            due = field("due_date")
            timestamp = dict(type="timestamp", domain=[], nullable=False)
            start, end = [operand("parameter", timestamp, name=n) for n in ("start", "end")]
            queries["list-due"] = query("list-due", {"start": timestamp, "end": timestamp}, group("and", visible, pending, group("not", unary("is_null", due)), compare(due, start, "ge"), compare(due, end, "le")), preconditions=[dict(predicate=compare(start, end, "le"), error="invalid_window", stage="before_selection", rejection="unchanged")], parameter_errors={n: dict(missing={"kind": "cli_rejection"}, invalid="invalid_due_date") for n in ("start", "end")})
        if case == "B12":
            cid = next(c["id"] for c in base["capabilities"] if c["kind"] == "utc_clock")
            timestamp = dict(type="timestamp", domain=[], nullable=False)
            allowed = dict(type="collection", element={k: v for k, v in types["priority"].items() if k != "nullable"}, ordering="insertion", duplicates="unique", equality="exact")
            queries["list-urgent"] = query("list-urgent", {}, group("and", visible, pending, compare(field("due_date"), operand("resource", timestamp, name="declared_now"), "lt"), compare(field("priority"), operand("literal", allowed, value=["HIGH", "CRITICAL"]), member=True)), resources=[dict(name="declared_now", type=timestamp, capability=cid, sampling="once_per_query")])
        r["domains"].update(capability_profile=mutable_profile.PROFILE, scalar_base_model=copy.deepcopy(source.MODEL), input_value_profile="typed-input-values-1", predicate_profile="typed-predicates-1", predicate_value_interface_profile="predicate-value-interfaces-1", collection_store=dict(kind="composed_scalar", state="state_tasks"), evaluation_scope="Requirement-local exposed transfer with represented archive listing precursors; not cumulative achievement")
        r["rows"] = []
        for profile, facts in (("existing-scalar-1", f), (mutable_profile.PROFILE, m)):
            for facet, value in facts.items():
                r["rows"].append(dict(id=case + "/" + facet, basis="STATED", derived_from=[], source_quote=r["source"], statement="R5.107 authorized " + facet, relation=dict(kind="crud", parameters=dict(profile=profile, facet=facet, value=copy.deepcopy(value)))))
        for command, q in queries.items():
            for facet, value in q.items():
                if facet == "id": continue
                r["rows"].append(dict(id=case + "/" + command + "/" + facet, basis="STATED", derived_from=[], source_quote=r["source"], statement="R5.107 authorized " + command + " " + facet, relation=dict(kind="filter_order", parameters=dict(query=command, facet=facet, value=copy.deepcopy(value)))))
        r["interpretation_notes"] = ["Exact literal archive write, unchanged status, repeat rejection; prior selection normalized and explicitly conjoined with nonarchived selection.", "Existing declared clocks and source input/precondition errors retained; missing required CLI query inputs retain CLI rejection, no missing application identity guessed.", "Additive schema 4 is a disposable requirement-local realization against canonical schema 3, not cumulative historical migration numbering."]
    return records


def plan(r):
    if r["id"] not in TARGETS: return prior.prior.plan(r)
    case, ids = r["id"], [o["id"] for o in r["rows"]]
    def task(i, priority="NORMAL", status="pending", archived=False, due="2000-01-01T00:00:00Z"):
        return dict(id=i, title=i, description="  preserved  ", status=status, priority=priority, created_at="2020-01-01T00:00:00Z", due_date=due, source=" verbatim ", category="Work", tags=["Work"], notes=["Old"], archived=archived)
    a, b, c, d = task("a", "HIGH"), task("b", "LOW", "completed"), task("c", "CRITICAL", archived=True), task("d", due=None)
    steps = []
    def step(argv, expected=None, error=None, preserve=True, contains=None):
        s = dict(argv=argv, returncode=1 if error else 0, contains=contains or [])
        if preserve: s["preserved"] = ["tasks.json"]
        if error: s.update(stdout_exact="", stderr_json={"error": error})
        else:
            s["stderr_exact"] = ""
            if expected is not None: s["stdout_json"] = copy.deepcopy(expected)
        return s
    steps += [step(["list"], [a, b, d]), step(["list-high"], [a]), step(["list-overdue"], [a]), step(["list-tag", "--tag", "Work"], [a, b, d]), step(["list-tag", "--tag", "work"], []), step(["list-tag", "--tag", " Work "], []), step(["list-tag", "--tag", " "], error="invalid_tag"), step(["list-status", "--status", "completed"], [b]), step(["list-category", "--category", "Work"], [a, b, d]), step(["list-archived"], [c])]
    if case == "B09":
        flags = ["--start", "2000-01-01T00:00:00Z", "--end", "2000-01-01T00:00:00Z"]
        steps += [step(["list-due", *flags], [a]), step(["list-due", "--start", "2001-01-01T00:00:00Z", "--end", "2000-01-01T00:00:00Z"], error="invalid_window"), step(["list-due", "--start", "bad", "--end", "2000-01-01T00:00:00Z"], error="invalid_due_date"), step(["list-due", "--start", "2000-01-01T00:00:00+00:00", "--end", "2001-01-01T00:00:00Z"], error="invalid_due_date"), step(["list-due", "--start", "1999-01-01T00:00:00Z", "--end", "2001-01-01T00:00:00Z"], [a])]
    if case == "B12":
        steps += [step(["list-urgent"], [a])]
    if case in ("B11", "B13"):
        steps += [step(["delete", "--id", "b"], error="delete_requires_archive")]
    if case == "B13":
        steps += [step(["complete", "--id", "c"], error="invalid_transition"), step(["append-note", "--id", "c", "--text", " Note "], error="invalid_transition"), step(["list-archived"], [c])]
    archived_b = {**b, "archived": True}
    steps += [step(["archive", "--id", "b"], archived_b, preserve=False), step(["archive", "--id", "b"], error="invalid_transition"), step(["list-archived"], [archived_b, c]), step(["list-status", "--status", "completed"], []), step(["list"], [a, d]), step(["archive", "--id", "absent"], error="task_not_found")]
    archived_a = {**a, "archived": True}
    steps += [step(["archive", "--id", "a"], archived_a, preserve=False), step(["list-high"], []), step(["list-overdue"], []), step(["list-tag", "--tag", "Work"], [d]), step(["list-category", "--category", "Work"], [d])]
    if case in ("B11", "B13"):
        steps += [step(["delete", "--id", "b"], archived_b, preserve=False), step(["delete", "--id", "c"], c, preserve=False), step(["delete", "--id", "a"], archived_a, preserve=False), step(["delete", "--id", "d"], d, preserve=False), step(["list-archived"], [])]
    def scenario(name, payload, checks):
        x = dict(id=name, obligations=ids, initial_state="fresh_directory", initial_files=[] if payload is None else [dict(path="tasks.json", json=payload)], steps=checks, invariants=["Exact whole records and unchanged rejected/query bytes"], transitions="Separate subprocess reload", rejections="Source-declared errors")
        x["identity"] = hashlib.sha256(canonical(x)).hexdigest(); return x
    cases = [scenario("archive-composition", dict(schema_version=4, records=[d, c, b, a]), steps)]
    legacy = {k: v for k, v in a.items() if k not in ("archived", "tags", "notes", "source", "category")}
    migrated = {**legacy, "archived": False, "tags": [], "notes": [], "source": "", "category": ""}
    cases += [scenario("migration", dict(schema_version=3, records=[legacy]), [step(["list"], error="migration_required"), step(["migrate"], {"migrated": 1}, preserve=False), step(["list"], [migrated]), step(["migrate"], {"migrated": 0})]),
        scenario("creation", None, [step(["create", "--title", "New", "--description", "Kept", "--tag", " A ", "--tag", "A", "--category", " Work "], preserve=False, contains=['"archived": false', '"tags": ["A"]', '"notes": []', '"category": "Work"']), step(["list"], contains=['"archived": false', '"category": "Work"'])]),
        scenario("invalid-state", dict(schema_version=4, records=[{"id": "bad"}]), [step(["list"], error="invalid_state")]), scenario("missing-store", None, [step(["list"], []), step(["list-archived"], [])])]
    if case == "B12":
        low, critical, normal, future = task("low", "LOW"), task("critical", "CRITICAL"), task("normal"), task("future", "HIGH", due="2999-01-01T00:00:00Z")
        cases.append(scenario("clock-priority-partition", dict(schema_version=4, records=[normal, low, future, critical]), [step(["list-urgent"], [critical]), step(["list-overdue"], [critical, low, normal])]))
    if case == "B13":
        note = {**a, "notes": ["Old", "New"]}; complete = {**note, "status": "completed"}; archived_note = {**complete, "archived": True}
        cases.append(scenario("terminal-notes-and-lifecycle", dict(schema_version=4, records=[a]), [step(["append-note", "--id", "a", "--text", " New "], note, preserve=False), step(["complete", "--id", "a"], complete, preserve=False), step(["archive", "--id", "a"], archived_note, preserve=False), step(["append-note", "--id", "a", "--text", "No"], error="invalid_transition"), step(["complete", "--id", "a"], error="invalid_transition"), step(["list-archived"], [archived_note]), step(["delete", "--id", "a"], archived_note, preserve=False)]))
    return dict(version="external-cli-plan-1", outcome="READY", producer="R5.107 source-reviewed literal oracle", source_sha256=hashlib.sha256(r["source"].encode()).hexdigest(), cases=cases, coverage=[dict(obligation=i, classification="EXERCISED", justification="Archive/selection/clock/precondition/persistence source partitions with preserved baseline behavior", cases=[c["identity"] for c in cases]) for i in ids], limitations=["Same-agent capture/inventory/oracle and synthetic approval; exposed requirement-local regression, not cumulative or held-out"])


def main():
    lock_path = OUT / "R5_107-GENERIC-LOCK-3.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    records = captures()
    for r in records:
        generic.publish("R5_107-" + r["id"] + "-CANDIDATE.json", dict(case=r["id"], producer_capture=r, external_plan=plan(r)))
    pins = {r["id"]: hashlib.sha256((OUT / ("R5_107-" + r["id"] + "-CANDIDATE.json")).read_bytes()).hexdigest() for r in records}
    generic.publish("R5_107-CORPUS-LOCK.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=pins, implementation_lock_sha256=hashlib.sha256(lock_path.read_bytes()).hexdigest(), transfer_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), rule="All twenty fresh captures/plans fixed before first transfer outcome"))
    results = []
    for r in records:
        path = OUT / ("R5_107-" + r["id"] + "-CANDIDATE.json")
        fixed = json.loads(path.read_text(encoding="utf-8"))
        try:
            x = ev.evaluate(fixed["producer_capture"], fixed["external_plan"])
        except Failure as exc:
            stages = {s: "NOT_REACHED" for s in ev.STAGES}; stages["FORMALIZATION"] = "BLOCKED"
            x = dict(case=r["id"], stages=stages, first_blocker="FORMALIZATION", native=exc.code, terminal=dict(outcome=exc.code, failure=exc.as_dict()), candidate=fixed["producer_capture"], external_plan=fixed["external_plan"])
        results.append(x)
        generic.publish("R5_107-" + r["id"] + "-RESULT.json", x)
        print(x["case"], x["first_blocker"], x["native"], flush=True)
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    assert pins == {case: hashlib.sha256((OUT / ("R5_107-" + case + "-CANDIDATE.json")).read_bytes()).hexdigest() for case in pins}
    before = {x["case"]: x for x in json.loads((OUT / "R5_106-TRANSFER-EVIDENCE.json").read_text(encoding="utf-8"))["cases"]}
    comparison = [dict(case=x["case"], r5_106_first_blocker=before[x["case"]]["first_blocker"], r5_107_first_blocker=x["first_blocker"], native=x["native"], newly_reached=[s for s in ev.STAGES if before[x["case"]]["stages"][s] == "NOT_REACHED" and x["stages"][s] != "NOT_REACHED"], stages=x["stages"], behaviorally_verified=x["first_blocker"] == "SUCCESS", next_blocker=None if x["first_blocker"] == "SUCCESS" else x.get("terminal", {}).get("failure", x["native"])) for x in results]
    distribution = {k: sum(x["first_blocker"] == k for x in results) for k in ("FORMALIZATION", "STRUCTURAL", "BDI", "ADEQUACY", "REPRESENTATION", "AUTHORING", "COMPILATION", "RUNTIME", "BEHAVIORAL_VERIFICATION", "SUCCESS")}
    generic.publish("R5_107-TRANSFER-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), scope="Fresh typed exposed requirement-local regression, not held-out/cumulative", implementation_unchanged=True, history_unchanged=True, distribution=distribution, cases=results))
    generic.publish("R5_107-COMPARISON.json", dict(distribution=distribution, cases=comparison, external_invocations=sum(x.get("external_invocations", 0) for x in results)))
    lines = ["# R5.107 — fresh fixed exposed transfer", "", "R5.106 is preserved. Exposed requirement-local regression, not held-out/cumulative evidence.", "", "| Case | R5.106 first blocker | R5.107 first blocker | Newly reached stages | Behavioral success |", "| --- | --- | --- | --- | --- |"]
    for x in comparison:
        lines.append("| " + x["case"] + " | " + x["r5_106_first_blocker"] + " | " + x["r5_107_first_blocker"] + " | " + (", ".join(x["newly_reached"]) or "None") + " | " + ("Yes" if x["behaviorally_verified"] else "No") + " |")
    lines += ["", "Native blockers and stages: `R5_107-COMPARISON.json`. Source, authority, receipts and external observations: `R5_107-TRANSFER-EVIDENCE.json`."]
    with (OUT / "R5_107-CAPABILITY-MATRIX.md").open("x", encoding="utf-8", newline="\n") as f: f.write("\n".join(lines) + "\n")


if __name__ == "__main__": main()
