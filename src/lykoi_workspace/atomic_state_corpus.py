"""Five source-authorized domains; ordinary state plus coupled record creation."""
import copy

from air_compiler.atomic_state import COMMIT
from air_compiler.references import identity, erase
from .mutable_corpus import capture
from .input_corpus import parameters
from .reference_corpus import assemble, operation, parameter, write, external_plan, step
from .predicate_corpus import operand, compare, group
from lykoi_pipeline import mutable_profile

TEXT_TYPE = dict(type="string", domain=[])
TIME = dict(type="timestamp", domain=[])


def binding(source, error="invalid_history"):
    return dict(source=source, invalid_error=error)


def captures():
    records = []
    for domain, command, policy in (("Inventory", "adjust-stock-band", "occurrence"), ("Account", "change-status", "timestamp_id"), ("Document", "change-owner", "occurrence"), ("Deployment", "deploy", "timestamp_id"), ("Ledger", "set-status", "occurrence")):
        base = capture("profile", "allow", "replace", [])
        f = base["scalar"]; f["storage"]["path"] = domain.lower() + ".json"
        m = dict(collections=[], mutations=[], creation_pipelines=[], predicate_semantics=dict(booleans=[], guards=[], invariants=[]))
        model = mutable_profile.scalar.lower(f)
        m["input_contracts"] = parameters(model, m)
        history = domain + "History"
        pi, hi = identity(domain), identity(history)
        action = dict(type="enum", domain=[command, "create", "advance", "delete"])
        fields = dict(id=hi, subject=pi, action=action, actor=TEXT_TYPE, timestamp=TIME, payload=TEXT_TYPE)
        params = dict(id=parameter(pi, "id"), value=parameter(TEXT_TYPE, "value"), record=parameter(hi, "record"), actor=parameter(TEXT_TYPE, "actor"))
        primary = operation(command, domain, "update", params, [write("description", operand("parameter", TEXT_TYPE, name="value"), error="invalid_primary")], lookup="id", missing="record_not_found")
        refs = dict(primary=domain, entities=[dict(name=history, key="id", fields=fields, initial=[])], references=[dict(entity=history, field="subject", target=domain, existence=dict(policy="unchecked", error=None), deletion=dict(policy="permit", error=None), migration=None)], operations=[primary, operation("delete", domain, "delete", {"id": parameter(pi, "id")}, lookup="id", missing="record_not_found")], guards=[], commit=dict(scope="one_store", mutation="one_record", isolation="exclusive_operation", rejection="unchanged"))
        clock = next(c["id"] for c in model["capabilities"] if c["kind"] == "utc_clock")
        uuid = next(c["id"] for c in model["capabilities"] if c["kind"] == "uuid_v4")
        def creation(kind, key_source, image, actor):
            return dict(entity=history, bindings=dict(id=binding(key_source), subject=binding(dict(kind=image, type=pi, name="id")), action=binding(operand("literal", action, value=kind)), actor=binding(actor), timestamp=binding(dict(kind="resource", type=TIME, name="clock")), payload=binding(dict(kind=image, type=TEXT_TYPE, name="description"))), duplicate_error="history_exists")
        op = dict(command=command, entity=domain, parameters={n: p["type"] for n, p in params.items()}, resources=[dict(name="clock", type=TIME, capability=clock)], on="success", sampling="once_per_operation", ordering="declared_creation_occurrence", creations=[creation(command, operand("parameter", hi, name="record"), "after", operand("parameter", TEXT_TYPE, name="actor"))])
        atom = dict(operations=[op], queries=[], append_only=[history], commit=copy.deepcopy(COMMIT))
        # Primary resource/lifecycle/delete paths use the same generic frame.
        for cmd, image in (("create", "after"), ("advance", "after"), ("delete", "before")):
            pt = {p["parameter"]: p["type"] for p in m["input_contracts"] if p["operation"] == cmd}
            if cmd in ("advance", "delete"): pt = dict(id=pi)
            if "id" in pt: pt["id"] = pi
            atom["operations"].append(dict(command=cmd, entity=domain, parameters=pt, resources=[dict(name="clock", type=TIME, capability=clock), dict(name="record_id", type=hi, capability=uuid)], on="success", sampling="once_per_operation", ordering="declared_creation_occurrence", creations=[creation(cmd, dict(kind="resource", type=hi, name="record_id"), image, operand("literal", TEXT_TYPE, value="authorized-system"))]))
        qfields = {n: erase(t) for n, t in fields.items()}
        order = [] if policy == "occurrence" else [dict(field="timestamp", direction="ASC"), dict(field="id", direction="ASC")]
        for cmd, query_params, pred in (("history", {}, compare(operand("field", qfields["subject"], name="subject"), operand("field", qfields["subject"], name="subject"))), ("history-subject", {"subject": qfields["subject"]}, compare(operand("field", qfields["subject"], name="subject"), operand("parameter", qfields["subject"], name="subject"))), ("history-action", {"action": action}, compare(operand("field", action, name="action"), operand("parameter", action, name="action")))):
            atom["queries"].append(dict(id=cmd, source=dict(collection=history, fields=qfields, unique_key="id"), parameters=query_params, predicate=pred, comparison=dict(scope="predicate_nodes"), ordering=order, validation=[], inclusion=[], effect=dict(state="read_only", persistence="unchanged"), result=dict(shape="collection", cardinality="zero_or_more", no_match="empty")))
        m["atomic_state_semantics"] = atom
        source = ("Public " + domain + " bounded durable-history authority. Inventory adjusts a named stock band; Account/Ledger set a status label; Document changes an ownership label; Deployment sets a deployment-state label. These are typed strings, not numeric calculations. Complete normative facts: " + repr(dict(scalar=f, mutable=m, references=refs)) + ". Each listed primary operation commits exactly one typed history record in the same success-only atomic transition. Supplied actor/record identity are preserved; create/advance/delete use the explicitly authorized system actor and UUID capability. UTC clock is declared and shared once per operation. History is append-only through exposed operations. Query order is " + policy + "; no numeric sequence value is required. Deleted subjects retain history. No independent history mutation exists.")
        candidate = assemble("atomic-" + domain.lower(), source, f, m, refs, dict(atomic_state_profile="atomic-durable-state-1"))
        row = dict(id="a", nickname="a", description="old", state="active", created_at="2020-01-01T00:00:00Z")
        records.append(dict(candidate=candidate, domain=domain, history=history, command=command, policy=policy, scalar=f, mutable=m, references=refs, atomic=atom, record=row, path=f["storage"]["path"]))
    return records


def plan(r):
    path, cmd = r["path"], r["command"]
    payload = dict(schema_version=1, records=[r["record"]], entities={r["history"]: []})
    argv = lambda value, record: [cmd, "--id", "a", "--value", value, "--record", record, "--actor", "operator"]
    after = {**r["record"], "description": "new"}
    steps = [step(path, ["history"], []), step(path, [cmd, "--id", "absent", "--value", "new", "--record", "one", "--actor", "operator"], error="record_not_found"), step(path, argv("new", "one"), after, preserve=False), step(path, ["list"], [after]), step(path, ["history"], contains=['"id": "one"', '"subject": "a"', '"action": "' + cmd + '"', '"actor": "operator"', '"payload": "new"']), step(path, argv("partial", "one"), error="history_exists"), step(path, ["list"], [after]), step(path, argv("final", "two"), {**after, "description": "final"}, preserve=False), step(path, ["history-subject", "--subject", "a"], contains=['"id": "one"', '"id": "two"']), step(path, ["history-subject", "--subject", "absent"], []), step(path, ["history-action", "--action", "create"], []), step(path, ["history-action", "--action", cmd], contains=['"id": "one"', '"id": "two"']), step(path, ["advance", "--id", "a"], {**after, "description": "final", "state": "inactive"}, preserve=False), step(path, ["advance", "--id", "a"], error="invalid_state_transition"), step(path, ["delete", "--id", "a"], {**after, "description": "final", "state": "inactive"}, preserve=False), step(path, ["list"], []), step(path, ["history-subject", "--subject", "a"], contains=['"action": "delete"', '"id": "one"', '"id": "two"'])]
    cases = [dict(id="coupled-create-query-delete-reload", initial_files=[dict(path=path, json=payload)], steps=steps), dict(id="empty-read-and-create", initial_files=[], steps=[step(path, ["history"], []), step(path, ["create", "--nickname", " "], error="empty_value"), step(path, ["create", "--nickname", "fresh"], preserve=False, contains=['"nickname": "fresh"']), step(path, ["history-action", "--action", "create"], contains=['"action": "create"', '"actor": "authorized-system"'])])]
    p = external_plan(r["candidate"], path, cases)
    p["producer"] = "R5.110 source-side literal history oracle"
    return p
