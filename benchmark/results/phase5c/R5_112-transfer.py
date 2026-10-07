"""Fresh exposed source capture, fixed before outcomes, against R5.112 lock."""
import copy
import datetime
import json
from pathlib import Path
import importlib.util

from air_compiler.references import identity
from air_compiler.atomic_state import COMMIT
from air_compiler.computation import INTEGER, TIME
from air_compiler.mutable_values import compose
from lykoi_pipeline import mutable_profile
from lykoi_workspace.computation_corpus import graph, node, count
from lykoi_workspace.atomic_state_corpus import binding
from lykoi_workspace.predicate_corpus import operand
from lykoi_workspace.reference_corpus import parameter
from lykoi_controller import Failure

OUT = Path(__file__).resolve().parent


def load(name, file):
    s = importlib.util.spec_from_file_location(name, OUT / file)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


generic = load("generic112transfer", "R5_112-generic.py")
prior = load("capture111for112", "R5_111-transfer.py")
ev = load("evaluate112transfer", "R5_103-evaluate.py")


def captures():
    records = prior.captures()  # Fresh frozen-source reads, no saved FRC replay.
    for r in records:
        r["capture_round"] = "R5.112 fresh typed source-reviewed capture after generic lock"
        if r["id"] == "B18":
            facets = {o["relation"]["parameters"].get("facet"): o for o in r["rows"] if o["relation"]["parameters"].get("profile") == mutable_profile.PROFILE}
            refs = facets["reference_semantics"]["relation"]["parameters"]["value"]
            mut = facets["mutations"]["relation"]["parameters"]["value"]
            context = [dict(command=cmd, name="actor", type=identity("User"), role="actor", authority="explicit_parameter", missing_error="actor_required", invalid_error="unknown_actor") for cmd in ("create", "complete", "delete", "archive", "append-note")]
            primary = dict(integers=[], context_inputs=context)
            r["rows"].append(dict(id="B18/primary_interfaces", basis="STATED", derived_from=[], source_quote=r["source"], statement="Explicit primary actor parameters, distinct from task owners; authorization remains separate", relation=dict(kind="crud", parameters=dict(profile=mutable_profile.PROFILE, facet="primary_interfaces", value=primary))))
            inputs = facets["input_contracts"]["relation"]["parameters"]["value"]
            for cmd in ("create", "complete", "delete", "archive", "append-note"):
                inputs.append(dict(operation=cmd, parameter="actor", type=dict(type="identifier", domain=[]), presence="required", binding=dict(source="cli_flag", flag="--actor", encoding="text"), missing=dict(kind="application_error", error="actor_required")))
                if cmd in ("complete", "delete"):
                    inputs.append(dict(operation=cmd, parameter="id", type=dict(type="string", domain=[], nullable=False), presence="required", binding=dict(source="cli_flag", flag="--id", encoding="text"), missing=dict(kind="application_error", error="task_not_found")))
            dep = next(o for o in refs["operations"] if o["command"] == "add-dependency")
            dep["parameters"]["actor"] = parameter(identity("User"), "actor", missing="actor_required", invalid="unknown_actor")
            scalar_f = {o["relation"]["parameters"]["facet"]: o["relation"]["parameters"]["value"] for o in r["rows"] if o["relation"]["parameters"].get("profile") == "existing-scalar-1"}
            scalar_copy = copy.deepcopy(scalar_f)
            scalar_copy["storage"]["version"] = max([1] + [m["to"] for m in scalar_copy["evolution"]])
            base = mutable_profile.scalar.integrate_facets(mutable_profile.scalar.extend_model(scalar_copy, r["domains"].get("scalar_base_model"), allow_unchanged=True), scalar_copy)
            clock = next(c["id"] for c in base["capabilities"] if c["kind"] == "utc_clock")
            uuid = next(c["id"] for c in base["capabilities"] if c["kind"] == "uuid_v4")
            atom = facets["atomic_state_semantics"]["relation"]["parameters"]["value"]
            audit, task, actor = identity("AuditHistory"), identity("Task"), identity("User")
            actions = next(e for e in refs["entities"] if e["name"] == "AuditHistory")["fields"]["operation"]
            for cmd in ("create", "complete", "delete", "archive", "append-note", "add-dependency"):
                pt = {n: p["type"] for n, p in dep["parameters"].items()} if cmd == "add-dependency" else {p["parameter"]: p["type"] for p in inputs if p["operation"] == cmd}
                if "id" in pt: pt["id"] = task
                pt["actor"] = actor
                image = "before" if cmd == "delete" else "after"
                ordinal = graph([node("size", "value", [count("AuditHistory", audit)]), node("sequence", "add", [operand("computed", INTEGER, name="size"), operand("literal", INTEGER, value=1)], deps=["size"])])
                row = dict(entity="AuditHistory", bindings=dict(id=binding(operand("resource", audit, name="audit_id")), sequence=binding(operand("computed", INTEGER, name="sequence")), timestamp=binding(operand("resource", TIME, name="clock")), actor=binding(operand("parameter", actor, name="actor")), operation=binding(operand("literal", actions, value=cmd)), task=binding(operand(image, task, name="id"))), duplicate_error="audit_id_collision")
                atom["operations"].append(dict(command=cmd, entity="Task", parameters=pt, resources=[dict(name="clock", type=TIME, capability=clock), dict(name="audit_id", type=audit, capability=uuid)], on="success", sampling="once_per_operation", ordering="declared_creation_occurrence", computations=ordinal, creations=[row]))
            r["domains"]["primary_interface_profile"] = "primary-value-interfaces-1"
            r["rows"] = [o for o in r["rows"] if o["id"] not in ("B18/primary_history_integration", "B18/primary_actor_binding")]
            r["rows"].append(dict(id="B18/primary_actor_authorization", basis="STATED", derived_from=[], source_quote=r["source"], statement="Inherited source-authorized actor existence/role/owner permission checks must precede all primary operations; non-system historical role remains unanswered", relation=dict(kind="crud", parameters=dict(required_capability="primary_actor_prewrite_authorization", specification=dict(unknown="unknown_actor", missing="actor_required", forbidden="permission_denied", actor_source="explicit_parameter", owner_source="primary_record_or_creation_input", role_source="User.role", observation="before_primary_operation", migration_authority="non_system_existing_user_role_not_determined", boundary="Explicit primary actor/history bindings are represented. Role-bearing user state and primary creation/lookup authorization ordering are not integrated; no system actor substitution or inferred migration role.")))))
            r["interpretation_notes"] = ["Primary context actor bindings and six declared success-only numeric history compositions now have normal typed facets.", "Full contract still requires inherited role/owner authorization before primary creation and mutation; this is not supplied by commit-time history actor integrity.", "B17 non-system historical role is unresolved; no actor default or partial external success is invented."]
        if r["id"] == "B19":
            # Fresh full typed demand reuses the inherited actor/history substrate;
            # represent primary numeric introduction separately from residual effects.
            template = next(x for x in records if x["id"] == "B18")
            r["rows"], r["domains"] = copy.deepcopy(template["rows"]), copy.deepcopy(template["domains"])
            for o in r["rows"]:
                o["id"] = o["id"].replace("B18/", "B19/")
                o["source_quote"] = r["source"]
            facets = {o["relation"]["parameters"].get("facet"): o for o in r["rows"] if o["relation"]["parameters"].get("profile") == mutable_profile.PROFILE}
            nullable = dict(type="integer", domain=[], nullable=True)
            facets["primary_interfaces"]["relation"]["parameters"]["value"]["integers"] = [dict(name="recurrence_days", type=nullable, creation=dict(source="input_default", input="recurrence_days", default=None, pipeline=[], error="invalid_recurrence"), migration=[dict(**{"from": 4}, to=5, value=None)])]
            facets["input_contracts"]["relation"]["parameters"]["value"].append(dict(operation="create", parameter="recurrence_days", type=nullable, presence="optional", binding=dict(source="cli_flag", flag="--recurrence-days", encoding="json"), missing=None))
            next(o for o in facets["atomic_state_semantics"]["relation"]["parameters"]["value"]["operations"] if o["command"] == "create")["parameters"]["recurrence_days"] = nullable
            for o in r["rows"]:
                if o["relation"]["kind"] == "filter_order":
                    p = o["relation"]["parameters"]
                    if p["facet"] == "source": p["value"]["fields"]["recurrence_days"] = nullable
                    if p["facet"] == "amendment": p["value"]["base"]["source"]["fields"]["recurrence_days"] = nullable
            storage = next(o for o in r["rows"] if o["relation"]["parameters"].get("profile") == "existing-scalar-1" and o["relation"]["parameters"].get("facet") == "storage")
            storage["relation"]["parameters"]["value"]["version"] = 5
            r["rows"].append(dict(id="B19/recurring_successor_effect_integration", basis="STATED", derived_from=[], source_quote=r["source"], statement="Complete recurrence input refinement, conditional successor and ordered dual history retain source authority", relation=dict(kind="crud", parameters=dict(required_capability="conditional_dimensioned_primary_successor", specification=dict(interval="positive_integer_when_due_supplied", invalid="invalid_recurrence", omitted=None, historical=None, conversion="N_UTC_calendar_days_to_fixed_duration", effect_membership="only_successful_completion_of_recurring_original", fields="preserve_declared_fields_fresh_identity_and_creation_clock_pending_status_empty_dependencies", history="complete_original_then_create_successor_both_completing_actor", boundary="Numeric nullable primary field and same-primary creation work. Nullable input refinement/day-duration scaling, conditional creation membership and binding a secondary created identity into its own history are not integrated.")))))
            r["interpretation_notes"] = ["Primary integer/null creation/migration/query and computed primary mutation work generically.", "Same-primary complete typed successors and explicit actor-bound cardinality history now compose.", "Absolute UTC-day midnight representation is not runtime N-day-to-duration conversion.", "Residual complete B19 needs source-authorized nullable-to-duration refinement/scaling, conditional successor/effect membership, successor-created-image binding for its history row and inherited prewrite actor authorization. Existing synthetic unconditional successor is not full B19 success."]
    return records


def plan(r): return None if r["id"] in ("B18", "B19") else prior.plan(r)


def main():
    lock_path = OUT / "R5_112-GENERIC-LOCK.json"
    lock = json.loads(lock_path.read_text(encoding="utf-8"))
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    corpus_path = OUT / "R5_112-CORPUS-LOCK.json"
    if not corpus_path.exists():
        records = captures()
        for r in records: generic.publish("R5_112-" + r["id"] + "-CANDIDATE.json", dict(case=r["id"], producer_capture=r, external_plan=plan(r)))
        generic.publish(corpus_path.name, dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases={r["id"]: generic.digest(OUT / ("R5_112-" + r["id"] + "-CANDIDATE.json")) for r in records}, implementation_lock_sha256=generic.digest(lock_path), transfer_script_sha256=generic.digest(Path(__file__)), rule="All twenty fresh captures/plans fixed before first outcome"))
    corpus = json.loads(corpus_path.read_text(encoding="utf-8")); results = []
    assert corpus["transfer_script_sha256"] == generic.digest(Path(__file__))
    for case, digest in corpus["cases"].items():
        path = OUT / ("R5_112-" + case + "-CANDIDATE.json"); assert generic.digest(path) == digest
        fixed = json.loads(path.read_text(encoding="utf-8")); result_path = OUT / ("R5_112-" + case + "-RESULT.json")
        if result_path.exists(): x = json.loads(result_path.read_text(encoding="utf-8"))
        else:
            try: x = ev.evaluate(fixed["producer_capture"], fixed["external_plan"])
            except Failure as exc:
                stages = {s: "NOT_REACHED" for s in ev.STAGES}; stages["FORMALIZATION"] = "BLOCKED"
                x = dict(case=case, stages=stages, first_blocker="FORMALIZATION", native=exc.code, terminal=dict(outcome=exc.code, failure=exc.as_dict()))
            generic.publish(result_path.name, x)
        results.append(x); print(case, x["first_blocker"], x["native"], flush=True)
    assert generic.implementation_pins() == lock["implementation"] and generic.history_pins() == lock["history"]
    before = {x["case"]: x for x in json.loads((OUT / "R5_111-TRANSFER-EVIDENCE.json").read_text(encoding="utf-8"))["cases"]}
    comparison = [dict(case=x["case"], r5_111_blocker=before[x["case"]]["first_blocker"], r5_112_blocker=x["first_blocker"], native=x["native"], newly_reached=[s for s in ev.STAGES if before[x["case"]]["stages"][s] == "NOT_REACHED" and x["stages"][s] != "NOT_REACHED"], stages=x["stages"], behaviorally_verified=x["first_blocker"] == "SUCCESS", terminal=x.get("terminal")) for x in results]
    distribution = {k: sum(x["first_blocker"] == k for x in results) for k in ("FORMALIZATION", "STRUCTURAL", "BDI", "ADEQUACY", "REPRESENTATION", "AUTHORING", "COMPILATION", "RUNTIME", "BEHAVIORAL_VERIFICATION", "SUCCESS")}
    generic.publish("R5_112-TRANSFER-EVIDENCE.json", dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), scope="Exposed requirement-local regression, not held-out or cumulative", implementation_unchanged=True, history_unchanged=True, distribution=distribution, cases=results))
    generic.publish("R5_112-COMPARISON.json", dict(distribution=distribution, external_invocations=sum(x.get("external_invocations", 0) for x in results), cases=comparison))
    lines = ["# R5.112 — frozen exposed transfer", "", "R5.111 preserved. Fresh exposed regression, not held-out/cumulative evidence.", "", "| Case | R5.111 blocker | R5.112 blocker | Newly reached stages | Behavioral success |", "| --- | --- | --- | --- | --- |"]
    for x in comparison: lines.append("| " + x["case"] + " | " + x["r5_111_blocker"] + " | " + x["r5_112_blocker"] + " | " + (", ".join(x["newly_reached"]) or "None") + " | " + ("Yes" if x["behaviorally_verified"] else "No") + " |")
    lines += ["", "B18 actor/history bindings are represented but inherited primary role/owner authorization remains an explicit unsupported demand. B19 needs runtime N-day dimension/scaling, conditional successor/effect membership and successor-created-image history bindings. Absolute UTC-day midnight decoding does not discharge that demand. B17/B20 disputes remain.", "", "Native/stage receipts: `R5_112-COMPARISON.json`, `R5_112-TRANSFER-EVIDENCE.json`."]
    with (OUT / "R5_112-CAPABILITY-MATRIX.md").open("x", encoding="utf-8", newline="\n") as f: f.write("\n".join(lines) + "\n")


if __name__ == "__main__": main()
