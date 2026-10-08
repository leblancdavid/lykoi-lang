"""Fresh source captures and fixed plans; existing exposed evaluation, no harness changes."""
import copy
import datetime
import json
import importlib.util
from pathlib import Path

from air_compiler.references import identity, compose as references
from air_compiler.computation import INTEGER, TIME, DURATION
from air_compiler.mutable_values import compose
from lykoi_pipeline import mutable_profile
from lykoi_workspace.authorization_corpus import permission, CONVERSION
from lykoi_workspace.reference_corpus import extent, parameter, write
from lykoi_workspace.predicate_corpus import operand, compare, group, unary
from lykoi_workspace.computation_corpus import graph, node, count
from lykoi_workspace.atomic_state_corpus import binding
from lykoi_controller import Failure

OUT = Path(__file__).resolve().parent


def load(name, file):
    s = importlib.util.spec_from_file_location(name, OUT / file)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


generic = load("generic113transfer", "R5_113-generic.py")
prior = load("capture112for113", "R5_112-transfer.py")
ev = load("evaluate113transfer", "R5_103-evaluate.py")


def captures():
    records = prior.captures()  # Re-read actual frozen sources; no saved FRC replay.
    for r in records:
        r["capture_round"] = "R5.113 fresh typed source-reviewed capture after generic lock"
        if r["id"] not in ("B18", "B19"): continue
        case = r["id"]
        facets = {o["relation"]["parameters"].get("facet"): o for o in r["rows"] if o["relation"]["parameters"].get("profile") == mutable_profile.PROFILE}
        refs = facets["reference_semantics"]["relation"]["parameters"]["value"]
        atom = facets["atomic_state_semantics"]["relation"]["parameters"]["value"]
        role = dict(type="enum", domain=["ADMIN", "USER"])
        users = next(e for e in refs["entities"] if e["name"] == "User")
        users["fields"]["role"] = role
        for row in users["initial"]:
            assert row["id"] == "system"; row["role"] = "ADMIN"  # Actual B17 authority.
        create_user = next(o for o in refs["operations"] if o["command"] == "create-user")
        role_parameter = parameter(role, "role", invalid="invalid_role"); role_parameter["default"] = "USER"
        create_user["parameters"]["role"] = role_parameter
        create_user["changes"].append(write("role", operand("parameter", role, name="role"), error="invalid_role"))
        actor = identity("User")
        same_actor = compare(operand("field", actor, name="related.id"), operand("parameter", actor, name="actor"))
        exists = extent("User", same_actor, value=1)
        def has_role(value):
            return extent("User", group("and", same_actor, compare(operand("field", role, name="related.role"), operand("literal", role, value=value))), value=1)
        auth = dict(operations=[])
        for op in atom["operations"]:
            params = copy.deepcopy(op["parameters"])
            owner = operand("parameter", actor, name="owner") if op["command"] == "create" else operand("field", actor, name="primary.owner")
            if op["command"] == "create": params["owner"] = actor
            allowed = group("or", has_role("ADMIN"), group("and", has_role("USER"), compare(owner, operand("parameter", actor, name="actor"))))
            p = permission(op["command"], "Task", params, allowed)
            if op["command"] == "create": p["lookup"] = None
            p["actor"]["invalid_error"] = "unknown_actor"
            p["checks"] = [dict(predicate=exists, error="unknown_actor")]
            auth["operations"].append(p)
        r["rows"] = [o for o in r["rows"] if not o["id"].endswith(("/primary_actor_authorization", "/recurring_successor_effect_integration"))]
        r["rows"].append(dict(id=case + "/authorization_semantics", basis="STATED", derived_from=[], source_quote=r["source"], statement="B17 explicitly supplies actor selectors, not authentication: existing actor then ADMIN or USER owning target/creation owner; errors and unchanged prewrite frame exact", relation=dict(kind="crud", parameters=dict(profile=mutable_profile.PROFILE, facet="authorization_semantics", value=auth))))
        r["domains"].update(authorization_profile="prewrite-authorization-1", effect_composition_profile="conditional-created-effects-1", duration_conversion_profile="elapsed-day-conversion-1")
        if case == "B19":
            nullable = dict(type="integer", domain=[], nullable=True)
            creation = next(p for p in auth["operations"] if p["command"] == "create")
            days_input = operand("parameter", nullable, name="recurrence_days")
            due_input = operand("parameter", {**TIME, "nullable": True}, name="due_date")
            valid_recurrence = group("or", group("not", unary("present", days_input)), group("and", compare(days_input, operand("literal", nullable, value=0), op="gt"), unary("present", due_input), group("not", unary("is_null", due_input))))
            creation["checks"].append(dict(predicate=valid_recurrence, error="invalid_recurrence"))
            scalar_f = {o["relation"]["parameters"]["facet"]: o["relation"]["parameters"]["value"] for o in r["rows"] if o["relation"]["parameters"].get("profile") == "existing-scalar-1"}
            scalar_copy = copy.deepcopy(scalar_f); scalar_copy["storage"]["version"] = max([1] + [m["to"] for m in scalar_copy["evolution"]])
            base = mutable_profile.scalar.integrate_facets(mutable_profile.scalar.extend_model(scalar_copy, r["domains"].get("scalar_base_model"), allow_unchanged=True), scalar_copy)
            values = {name: row["relation"]["parameters"]["value"] for name, row in facets.items() if name not in ("reference_semantics", "atomic_state_semantics")}
            ir = compose(base, values); ri = references(ir, refs)
            complete = next(o for o in atom["operations"] if o["command"] == "complete")
            original = complete["creations"][0]; original.update(binding="original_audit", when=None, depends_on=[])
            when = group("not", unary("is_null", operand("field", nullable, name="primary.recurrence_days")))
            task, audit = identity("Task"), identity("AuditHistory")
            uuid = next(c["id"] for c in base["capabilities"] if c["kind"] == "uuid_v4")
            complete["resources"] += [dict(name="successor_id", type=task, capability=uuid, observation="binding"), dict(name="successor_audit_id", type=audit, capability=uuid, observation="binding")]
            bindings = {n: binding(operand("after", typ, name=n)) for n, typ in ri["types"]["Task"].items()}
            bindings["id"] = binding(operand("resource", task, name="successor_id"))
            bindings["created_at"] = binding(operand("resource", TIME, name="clock"))
            bindings["status"] = binding(operand("literal", ri["types"]["Task"]["status"], value="pending"))
            bindings["dependencies"] = binding(operand("literal", ri["types"]["Task"]["dependencies"], value=[]))
            if "archived" in bindings: bindings["archived"] = binding(operand("literal", ri["types"]["Task"]["archived"], value=False))
            refine_days = node("days", "refine_integer", [operand("before", nullable, name="recurrence_days")]); refine_days["null"] = dict(policy="reject")
            refine_due = node("due", "refine_instant", [operand("before", ri["types"]["Task"]["due_date"], name="due_date")], TIME); refine_due["null"] = dict(policy="reject")
            scale = node("seconds", "days_to_seconds", [operand("computed", INTEGER, name="days")], DURATION, deps=["days"]); scale["conversion"] = copy.deepcopy(CONVERSION)
            shift = node("successor_due", "shift_utc_seconds", [operand("computed", TIME, name="due"), operand("computed", DURATION, name="seconds")], TIME, deps=["due", "seconds"])
            bindings["due_date"] = binding(operand("computed", TIME, name="successor_due"))
            successor = dict(binding="successor", entity="Task", when=when, depends_on=[], computations=graph([refine_days, refine_due, scale, shift]), bindings=bindings, duplicate_error="id_collision")
            successor_audit = copy.deepcopy(original)
            successor_audit.update(binding="successor_audit", when=copy.deepcopy(when), depends_on=["successor"])
            successor_audit["bindings"]["id"] = binding(operand("resource", audit, name="successor_audit_id"))
            successor_audit["bindings"]["task"] = binding(dict(kind="created", type=task, effect="successor", entity="Task", field="id", alternative=None))
            actions = ri["types"]["AuditHistory"]["operation"]
            successor_audit["bindings"]["operation"] = binding(operand("literal", actions, value="create"))
            successor_audit["computations"] = graph([node("history_size", "value", [count("AuditHistory", audit)]), node("second_sequence", "add", [operand("computed", INTEGER, name="history_size"), operand("literal", INTEGER, value=2)], deps=["history_size"])])
            successor_audit["bindings"]["sequence"] = binding(operand("computed", INTEGER, name="second_sequence"))
            complete["creations"] = [original, successor, successor_audit]
        # The source supplies a creation default and system role, but never an
        # existing non-system role. Do not silently use USER/ADMIN on migration.
        question = "What role must migration assign to pre-existing non-system users? B17 supplies only the new-user default USER and system ADMIN; B18/B19 do not resolve historical role authority."
        r["rows"].insert(0, dict(id=case + "/historical_role_authority", basis="STATED", derived_from=[], source_quote=r["source"], statement="Historical non-system role authority remains undetermined; creation defaults cannot authorize migration", relation=dict(kind="crud", parameters=dict(required_capability="source_authorized_related_role_migration", specification=dict(system="ADMIN", new_default="USER", historical_non_system=None, source_authority="unanswered")))))
        r["question"] = question
        r["interpretation_notes"] = ["Prewrite selector-role-owner permissions are now represented compositionally, without claiming authentication.", "Unknown/missing/forbidden failures, typed current roles and new-user omission defaults are declared independently.", "Existing non-system historical role migration is unanswered; formalization must refuse a guessed role.", "Conditional successor, dependent successor audit, explicit independent IDs, nullable refinement and elapsed-day conversion are typed for B19; no benchmark dispatch or recurrence primitive.", "No full B18/B19 authoring or behavioral success is claimed before authority resolution."]
    return records


def plan(r): return None if r["id"] in ("B18", "B19") else prior.plan(r)


def main():
    lock_path = OUT / "R5_113-GENERIC-LOCK.json"; lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    corpus_path = OUT / "R5_113-CORPUS-LOCK.json"
    if not corpus_path.exists():
        records = captures()
        for r in records: generic.publish("R5_113-" + r["id"] + "-CANDIDATE.json", dict(case=r["id"], producer_capture=r, external_plan=plan(r)))
        generic.publish(corpus_path.name, dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases={r["id"]: generic.digest(OUT / ("R5_113-" + r["id"] + "-CANDIDATE.json")) for r in records}, implementation_lock_sha256=generic.digest(lock_path), transfer_script_sha256=generic.digest(Path(__file__)), rule="Twenty fresh captures/plans fixed before first outcome"))
    corpus = json.loads(corpus_path.read_text(encoding="utf-8")); assert corpus["transfer_script_sha256"] == generic.digest(Path(__file__))
    results = []
    for case, digest in corpus["cases"].items():
        path = OUT / ("R5_113-" + case + "-CANDIDATE.json"); assert generic.digest(path) == digest
        fixed = json.loads(path.read_text(encoding="utf-8")); result_path = OUT / ("R5_113-" + case + "-RESULT.json")
        if result_path.exists(): x = json.loads(result_path.read_text(encoding="utf-8"))
        else:
            try: x = ev.evaluate(fixed["producer_capture"], fixed["external_plan"])
            except Failure as exc:
                stages = {s: "NOT_REACHED" for s in ev.STAGES}; stages["FORMALIZATION"] = "BLOCKED"
                x = dict(case=case, stages=stages, first_blocker="FORMALIZATION", native=exc.code, terminal=dict(outcome=exc.code, failure=exc.as_dict()))
            generic.publish(result_path.name, x)
        results.append(x); print(case, x["first_blocker"], x["native"], flush=True)
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    before = {x["case"]: x for x in json.loads((OUT / "R5_112-TRANSFER-EVIDENCE.json").read_text(encoding="utf-8"))["cases"]}
    comparison = [dict(case=x["case"], r5_112_blocker=before[x["case"]]["first_blocker"], r5_113_blocker=x["first_blocker"], native=x["native"], newly_reached=[s for s in ev.STAGES if before[x["case"]]["stages"][s] == "NOT_REACHED" and x["stages"][s] != "NOT_REACHED"], stages=x["stages"], behaviorally_verified=x["first_blocker"] == "SUCCESS") for x in results]
    distribution = {k: sum(x["first_blocker"] == k for x in results) for k in ("FORMALIZATION", "STRUCTURAL", "BDI", "ADEQUACY", "REPRESENTATION", "AUTHORING", "COMPILATION", "RUNTIME", "BEHAVIORAL_VERIFICATION", "SUCCESS")}
    generic.publish("R5_113-TRANSFER-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), scope="Exposed requirement-local regression, not held-out/cumulative", implementation_unchanged=True, history_unchanged=True, distribution=distribution, cases=results))
    generic.publish("R5_113-COMPARISON.json", dict(distribution=distribution, external_invocations=sum(x.get("external_invocations", 0) for x in results), cases=comparison))
    lines = ["# R5.113 — locked exposed transfer", "", "R5.112 preserved. Exposed regression, not held-out/cumulative evidence.", "", "| Case | R5.112 blocker | R5.113 blocker | Newly reached stages | Behavioral success |", "| --- | --- | --- | --- | --- |"]
    for x in comparison: lines.append("| " + x["case"] + " | " + x["r5_112_blocker"] + " | " + x["r5_113_blocker"] + " | " + (", ".join(x["newly_reached"]) or "None") + " | " + ("Yes" if x["behaviorally_verified"] else "No") + " |")
    lines += ["", "B18/B19's implemented generic permission/effect interfaces expose inherited unanswered historical non-system role migration at formalization. No guessed USER migration or authenticated actor is admitted; neither case is claimed successful. B17/B20 remain disputed. Exact stage receipts: `R5_113-COMPARISON.json` and `R5_113-TRANSFER-EVIDENCE.json`."]
    with (OUT / "R5_113-CAPABILITY-MATRIX.md").open("x", encoding="utf-8", newline="\n") as f: f.write("\n".join(lines) + "\n")


if __name__ == "__main__": main()
