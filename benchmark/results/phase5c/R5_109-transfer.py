"""Fresh source-reviewed exposed transfer against the immutable R5.109 generic lock."""
import copy
import datetime
import hashlib
import json
from pathlib import Path

from air_compiler.mutable_values import compose
from air_compiler.references import identity
from lykoi_controller import Failure, canonical
from lykoi_pipeline import mutable_profile
from lykoi_workspace.input_corpus import parameters, staged
from lykoi_workspace.predicate_corpus import operand, compare, group
from lykoi_workspace.reference_corpus import assemble, sequence, extent, reach, parameter, operation, write, external_plan, step

OUT = Path(__file__).resolve().parent
import importlib.util


def load(name, file):
    s = importlib.util.spec_from_file_location(name, OUT / file)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


generic = load("generic109transfer", "R5_109-generic.py")
prior = load("capture107for109", "R5_107-transfer.py")
ev = load("evaluate109transfer", "R5_103-evaluate.py")
TARGETS = ("B14", "B15", "B16")


def captures():
    records = prior.captures()  # Fresh reads of all frozen source bundles.
    template = next(r for r in records if r["id"] == "B13")
    for r in records:
        r["capture_round"] = "R5.109 fresh source-reviewed capture after generic lock"
        if r["id"] not in TARGETS: continue
        case = r["id"]
        f = {o["relation"]["parameters"]["facet"]: copy.deepcopy(o["relation"]["parameters"]["value"]) for o in template["rows"] if o["relation"]["parameters"].get("profile") == "existing-scalar-1"}
        m = {o["relation"]["parameters"]["facet"]: copy.deepcopy(o["relation"]["parameters"]["value"]) for o in template["rows"] if o["relation"]["parameters"].get("profile") == mutable_profile.PROFILE}
        queries = {}
        for o in template["rows"]:
            p = o["relation"]["parameters"]
            if o["relation"]["kind"] == "filter_order": queries.setdefault(p["query"], dict(id=p["query"]))[p["facet"]] = copy.deepcopy(p["value"])
        # Source-authorized prior owner field; the relationship round now refines
        # its meaning for B16 instead of inventing a parallel ownership field.
        f["fields"].append(dict(name="owner", type="string", domain=[], nullable=False, preservation="verbatim"))
        f["creation"]["bindings"].append(dict(field="owner", source="input", value=None, default=None if case == "B16" else dict(value="", trigger="omitted", boundary="creation")))
        f["evolution"][-1]["defaults"]["owner"] = ""
        m["creation_pipelines"].append(dict(field="owner", pipeline=[dict(kind="transform", operation="trim"), staged(stage="TRANSFORMED", error="invalid_owner")], error="invalid_owner"))
        # Preserve the prior explicitly raw-empty-sensitive category validation.
        m["creation_pipelines"][0]["pipeline"][1]["when"] = dict(stage="RAW", predicate="nonempty")
        m["collections"].append(dict(name="dependencies", element=dict(type="identifier", domain=[]), ordering="insertion", duplicates="unique", equality="exact", creation=dict(source="literal", value=[]), migration=[dict(**{"from": 3}, to=4, value=[])]))
        m.pop("input_contracts")
        for mutation in m["mutations"]:
            for w in mutation["changes"]:
                if w.get("omitted") == "reject" and w.get("missing_error") is None:
                    w["missing_error"] = "capture_builder_only"
        base = mutable_profile.scalar.integrate_facets(mutable_profile.scalar.lower(f, copy.deepcopy(prior.source.MODEL)), f)
        types = compose(base, m)["value_types"]
        m["input_contracts"] = parameters(base, m)
        for p in m["input_contracts"]:
            if p["presence"] == "required": p["missing"] = dict(kind="cli_rejection")
        for mutation in m["mutations"]:
            for w in mutation["changes"]:
                if w.get("missing_error") == "capture_builder_only": w["missing_error"] = None
        if case == "B16":
            p = next(p for p in m["input_contracts"] if p["operation"] == "create" and p["parameter"] == "owner")
            p["missing"] = dict(kind="application_error", error="invalid_owner")
        task = identity("Task")
        pkey = operand("field", task, name="primary.id")
        dep = operand("parameter", task, name="depends_on")
        cycle = group("and", group("not", compare(dep, pkey)), group("not", reach("Task", "dependencies", dep, pkey)))
        add = operation("add-dependency", "Task", "update", {"id": parameter(task, "id", missing="task_not_found", invalid="task_not_found"), "depends_on": parameter(task, "depends-on", missing="task_not_found", invalid="task_not_found")}, [write("dependencies", dep, "append", "invalid_dependency")], guards=[dict(predicate=cycle, error="invalid_dependency")], lookup="id", missing="task_not_found")
        refs = dict(primary="Task", entities=[], references=[dict(entity="Task", field="dependencies", target="Task", existence=dict(policy="required", error="task_not_found"), deletion=dict(policy="restrict", error="dependency_in_use"), migration=None)], operations=[add], guards=[], commit=dict(scope="one_store", mutation="one_record", isolation="exclusive_operation", rejection="unchanged"))
        if case in ("B15", "B16"):
            related = operand("field", task, name="related.id")
            domain = compare(related, operand("field", sequence(task), name="primary.dependencies"), member=True)
            status = types["status"]
            complete = compare(operand("field", status, name="related.status"), operand("literal", status, value="completed"))
            refs["guards"].append(dict(command="complete", parameters={"id": task}, predicate=extent("Task", group("and", domain, group("not", complete))), error="incomplete_dependencies"))
        if case == "B16":
            user = identity("User")
            refs["entities"] = [dict(name="User", key="id", fields=dict(id=user), initial=[dict(id="system")])]
            refs["references"].append(dict(entity="Task", field="owner", target="User", existence=dict(policy="required", error="invalid_owner"), deletion=dict(policy="unavailable", error=None), migration=dict(when="missing_or_empty", value="system")))
            # Required CLI IDs are bound to the common missing-ID contract; blank
            # values have the separately declared invalid_user outcome.
            refs["operations"] += [operation("create-user", "User", "create", {"id": parameter(user, "id", missing="task_not_found", invalid="invalid_user")}, [write("id", operand("parameter", user, name="id"), error="invalid_user")], duplicate="user_exists"), operation("list-users", "User", "list", order=["id"])]
        normal = assemble(case, r["source"], f, m, refs, copy.deepcopy(template["domains"]))
        r["rows"], r["domains"] = normal["rows"], normal["domains"]
        for q in queries.values():
            # Existing query field view now includes the persisted new fields.
            q["source"]["fields"] = copy.deepcopy(types)
            if "amendment" in q: q["amendment"]["base"]["source"]["fields"] = copy.deepcopy(types)
        owner = operand("parameter", types["owner"], name="owner")
        visible = group("not", compare(operand("field", types["archived"], name="archived"), operand("literal", types["archived"], value=True)))
        queries["list-owner"] = dict(id="list-owner", source=dict(collection="state_tasks", fields=copy.deepcopy(types), unique_key="id"), parameters=dict(owner=types["owner"]), predicate=group("and", compare(operand("field", types["owner"], name="owner"), owner), visible), comparison=dict(scope="predicate_nodes"), ordering=[dict(field="created_at", direction="ASC"), dict(field="id", direction="ASC")], validation=[], inclusion=[], effect=dict(state="read_only", persistence="unchanged"), result=dict(shape="collection", cardinality="zero_or_more", no_match="empty"))
        for command, q in queries.items():
            for facet, value in q.items():
                if facet == "id": continue
                r["rows"].append(dict(id=case + "/" + command + "/" + facet, basis="STATED", derived_from=[], source_quote=r["source"], statement="Source-authorized preserved query " + command + " " + facet, relation=dict(kind="filter_order", parameters=dict(query=command, facet=facet, value=copy.deepcopy(value)))))
        r["interpretation_notes"] = ["Requirement-local normal schema 4 extends canonical schema 3; no cumulative historical achievement claimed.", "All prior archive/transition/delete guards retained; dependencies include archived targets.", "B16 users have no exposed deletion operation: policy unavailable preserves the missing deletion authority rather than guessing restrict or permit.", "Wire owner filters retain their explicit stored-string matching adapter; reference write/guard operands carry nominal target meaning."]
        # Syntax/type audit only, before fixing any transfer outcome. This must
        # never repair the generic implementation.
        contract = dict(schema_version="FormalRequirementContract-0.1", contract_id=case, revision=1, source=dict(id=case + "/source", text=r["source"], classification="SYNTHETIC", sha256=hashlib.sha256(r["source"].encode()).hexdigest()), obligations=r["rows"], context=dict(scope="Pre-outcome syntax/type audit", domains=r["domains"], assumptions=[], component_authority=None), issues=[], unspecified=[], implementation_choices=[], lineage=[], formalizer="R5.109 active-agent capture", review=None)
        mutable_profile.facts(contract)
    return records


def plan(r):
    if r["id"] not in TARGETS: return prior.plan(r)
    case = r["id"]
    path = "tasks.json"
    def task(i, status="pending", archived=False, deps=None, owner="system" if case == "B16" else ""):
        return dict(id=i, title=i, description="preserved", status=status, priority="NORMAL", created_at="2020-01-01T00:00:00Z", due_date=None, source="", category="", tags=[], notes=[], archived=archived, owner=owner, dependencies=deps or [])
    a, b, c, d = task("a"), task("b", archived=True), task("c", "completed", True), task("d", "completed")
    def scenario(name, payload, steps): return dict(id=name, initial_files=[] if payload is None else [dict(path=path, json=payload)], steps=steps)
    def payload(rows, users=None):
        return dict(schema_version=4, records=copy.deepcopy(rows), entities={} if case != "B16" else dict(User=users if users is not None else [dict(id="system")]))
    steps = []
    def add(argv, expected=None, error=None, preserve=True, contains=None): steps.append(step(path, argv, expected, error, preserve, contains))
    add(["list"], [a, d])
    add(["add-dependency", "--id", "a", "--depends-on", "absent"], error="task_not_found")
    add(["add-dependency", "--id", "absent", "--depends-on", "c"], error="task_not_found")
    add(["add-dependency", "--id", "a", "--depends-on", "a"], error="invalid_dependency")
    a["dependencies"] = ["b"]
    add(["add-dependency", "--id", "a", "--depends-on", "b"], a, preserve=False)
    add(["add-dependency", "--id", "a", "--depends-on", "b"], error="invalid_dependency")
    b["dependencies"] = ["c"]
    add(["add-dependency", "--id", "b", "--depends-on", "c"], b, preserve=False)
    add(["add-dependency", "--id", "c", "--depends-on", "a"], error="invalid_dependency")
    add(["delete", "--id", "b"], error="dependency_in_use")
    add(["delete", "--id", "c"], error="dependency_in_use")
    add(["complete", "--id", "b"], error="invalid_transition")
    if case in ("B15", "B16"):
        add(["complete", "--id", "a"], error="incomplete_dependencies")
    add(["append-note", "--id", "b", "--text", "Note"], error="invalid_transition")
    add(["delete", "--id", "d"], error="delete_requires_archive")
    add(["list-archived"], [b, c])
    original = [task("a"), task("b", archived=True), task("c", "completed", True), task("d", "completed")]
    cases = [scenario("references-cycles-and-prior-guards", payload(original), steps)]
    if case in ("B15", "B16"):
        a, b, c = task("a", deps=["b", "c"]), task("b"), task("c", "completed", True)
        after_b = {**b, "status": "completed"}; after_a = {**a, "status": "completed"}
        checks = [step(path, ["complete", "--id", "a"], error="incomplete_dependencies"), step(path, ["complete", "--id", "b"], after_b, preserve=False), step(path, ["complete", "--id", "a"], after_a, preserve=False), step(path, ["complete", "--id", "a"], error="invalid_transition"), step(path, ["list-archived"], [c]), step(path, ["list"], [after_a, after_b])]
        cases.append(scenario("ALL-mixed-empty-and-archived", payload([c, b, a]), checks))
    # Canonical legacy migration adds all source-authorized local fields.
    legacy = {k: v for k, v in task("legacy").items() if k in ("id", "title", "description", "status", "priority", "created_at", "due_date")}
    migrated = task("legacy")
    cases.append(scenario("migration-and-reload", dict(schema_version=3, records=[legacy]), [step(path, ["list"], error="migration_required"), step(path, ["migrate"], {"migrated": 1}, preserve=False), step(path, ["list"], [migrated]), step(path, ["migrate"], {"migrated": 0})]))
    if case == "B16":
        fresh = []
        fresh += [step(path, ["list-users"], [dict(id="system")]), step(path, ["create-user", "--id", "system"], error="user_exists"), step(path, ["create-user", "--id", " "], error="invalid_user"), step(path, ["create-user", "--id", "Alice"], dict(id="Alice"), preserve=False), step(path, ["create-user", "--id", "alice"], dict(id="alice"), preserve=False), step(path, ["list-users"], [dict(id="Alice"), dict(id="alice"), dict(id="system")]), step(path, ["create", "--title", "Owned", "--description", "Kept"], error="invalid_owner"), step(path, ["create", "--title", "Owned", "--description", "Kept", "--owner", "unknown"], error="invalid_owner"), step(path, ["create", "--title", "Owned", "--description", "Kept", "--owner", " Alice "], preserve=False, contains=['"owner": "Alice"', '"dependencies": []']), step(path, ["list-owner", "--owner", "Alice"], contains=['"owner": "Alice"']), step(path, ["list-owner", "--owner", "ALICE"], [])]
        cases.append(scenario("users-required-ownership", None, fresh))
        # Pre-reference schema-4 values exercise semantic migration authority and
        # nonempty-owner retry, independently of additive canonical migration.
        old = [task("empty", owner=""), task("unknown", owner="later")]
        checks = [step(path, ["migrate"], error="invalid_owner"), step(path, ["create-user", "--id", "later"], dict(id="later"), preserve=False), step(path, ["migrate"], {"migrated": 2}, preserve=False), step(path, ["list-owner", "--owner", "system"], [task("empty")]), step(path, ["list-owner", "--owner", "later"], [task("unknown", owner="later")]), step(path, ["migrate"], {"migrated": 0})]
        cases.append(scenario("owner-migration-rejection-create-and-retry", dict(schema_version=4, records=old), checks))
    else:
        cases.append(scenario("new-empty-reference-values", None, [step(path, ["create", "--title", "New", "--description", "Kept"], preserve=False, contains=['"dependencies": []']), step(path, ["list"], contains=['"dependencies": []'])]))
    return external_plan(r, path, cases)


def main():
    lock_path = OUT / "R5_109-GENERIC-LOCK.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    corpus_lock_path = OUT / "R5_109-CORPUS-LOCK.json"
    if not corpus_lock_path.exists():
        records = captures()
        for r in records:
            generic.publish("R5_109-" + r["id"] + "-CANDIDATE.json", dict(case=r["id"], producer_capture=r, external_plan=plan(r)))
        pins = {r["id"]: generic.digest(OUT / ("R5_109-" + r["id"] + "-CANDIDATE.json")) for r in records}
        generic.publish(corpus_lock_path.name, dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=pins, implementation_lock_sha256=generic.digest(lock_path), transfer_script_sha256=generic.digest(Path(__file__)), rule="All twenty candidate/source-side oracle captures fixed before first outcome; resume only unchanged bytes"))
    corpus_lock = json.loads(corpus_lock_path.read_text(encoding="utf-8"))
    assert corpus_lock["transfer_script_sha256"] == generic.digest(Path(__file__))
    results = []
    for case, digest in corpus_lock["cases"].items():
        path = OUT / ("R5_109-" + case + "-CANDIDATE.json")
        assert generic.digest(path) == digest
        fixed = json.loads(path.read_text(encoding="utf-8"))
        result_path = OUT / ("R5_109-" + case + "-RESULT.json")
        if result_path.exists():
            x = json.loads(result_path.read_text(encoding="utf-8"))
        else:
            try: x = ev.evaluate(fixed["producer_capture"], fixed["external_plan"])
            except Failure as exc:
                stages = {s: "NOT_REACHED" for s in ev.STAGES}; stages["FORMALIZATION"] = "BLOCKED"
                x = dict(case=case, stages=stages, first_blocker="FORMALIZATION", native=exc.code, terminal=dict(outcome=exc.code, failure=exc.as_dict()))
            generic.publish(result_path.name, x)
        results.append(x)
        print(case, x["first_blocker"], x["native"], flush=True)
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    before = {x["case"]: x for x in json.loads((OUT / "R5_107-TRANSFER-EVIDENCE.json").read_text(encoding="utf-8"))["cases"]}
    comparison = [dict(case=x["case"], r5_107_blocker=before[x["case"]]["first_blocker"], r5_109_blocker=x["first_blocker"], native=x["native"], newly_reached=[s for s in ev.STAGES if before[x["case"]]["stages"][s] == "NOT_REACHED" and x["stages"][s] != "NOT_REACHED"], stages=x["stages"], behaviorally_verified=x["first_blocker"] == "SUCCESS", next_blocker=None if x["first_blocker"] == "SUCCESS" else x.get("terminal", {}).get("failure", x["native"])) for x in results]
    distribution = {k: sum(x["first_blocker"] == k for x in results) for k in ("FORMALIZATION", "STRUCTURAL", "BDI", "ADEQUACY", "REPRESENTATION", "AUTHORING", "COMPILATION", "RUNTIME", "BEHAVIORAL_VERIFICATION", "SUCCESS")}
    generic.publish("R5_109-TRANSFER-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), scope="Exposed requirement-local development/regression; not held-out or cumulative", implementation_unchanged=True, history_unchanged=True, distribution=distribution, cases=results))
    generic.publish("R5_109-COMPARISON.json", dict(distribution=distribution, external_invocations=sum(x.get("external_invocations", 0) for x in results), cases=comparison))
    lines = ["# R5.109 — frozen exposed transfer", "", "R5.107 is preserved. Requirement-local exposed development/regression, not held-out/cumulative evidence.", "", "| Case | R5.107 blocker | R5.109 blocker | Newly reached stages | Behavioral success |", "| --- | --- | --- | --- | --- |"]
    for x in comparison: lines.append("| " + x["case"] + " | " + x["r5_107_blocker"] + " | " + x["r5_109_blocker"] + " | " + (", ".join(x["newly_reached"]) or "None") + " | " + ("Yes" if x["behaviorally_verified"] else "No") + " |")
    lines += ["", "Exact stage/native blocker receipts: `R5_109-COMPARISON.json` and `R5_109-TRANSFER-EVIDENCE.json`."]
    with (OUT / "R5_109-CAPABILITY-MATRIX.md").open("x", encoding="utf-8", newline="\n") as f: f.write("\n".join(lines) + "\n")


if __name__ == "__main__": main()
