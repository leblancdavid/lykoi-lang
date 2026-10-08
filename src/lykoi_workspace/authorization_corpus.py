"""Generic document/project/inventory/account/schedule permission compositions."""
import copy
import json

from air_compiler.references import identity
from air_compiler.computation import INTEGER, TIME, DURATION
from .primary_corpus import captures as primary_captures
from .reference_corpus import assemble, parameter, reference, extent, external_plan, step, operation, write
from .predicate_corpus import operand, compare, group
from .computation_corpus import graph, node
from .atomic_state_corpus import binding

CONVERSION = dict(source="elapsed_days", target="elapsed_seconds", seconds_per_day=86400, negative="preserve", overflow="reject")


def permission(command, entity, params, predicate, source="explicit_parameter"):
    return dict(command=command, entity=entity, lookup="id", actor=dict(name="actor", type=params["actor"], source=source, context="controlled_host" if source == "trusted_context" else None, missing_error="context_required" if source == "trusted_context" else "actor_required", invalid_error="invalid_actor"), parameters=copy.deepcopy(params), predicate=predicate, error="permission_denied", observation="committed_operation_before", rejection="unchanged")


def captures():
    result = []
    for r in primary_captures():
        domain = r["primary"]
        if domain == "Session": continue
        f, m, refs = r["scalar"], r["mutable"], r["references"]
        actor = identity(domain + "Operator")
        role = dict(type="enum", domain=["editor", "viewer"])
        refs["entities"][0]["fields"]["role"] = role
        refs["entities"][0]["initial"] = []
        role_parameter = parameter(role, "role"); role_parameter["default"] = "viewer"
        refs["operations"].append(operation("create-operator", domain + "Operator", "create", dict(id=parameter(actor, "id"), role=role_parameter), [write("id", operand("parameter", actor, name="id")), write("role", operand("parameter", role, name="role"))], duplicate="operator_exists"))
        f["fields"].append(dict(name="owner_id", type="identifier", domain=[], nullable=False, preservation="verbatim"))
        f["creation"]["bindings"].append(dict(field="owner_id", source="input", value=None, default=None))
        f["creation"]["validation"].append(dict(field="owner_id", rule="nonblank", error="owner_required"))
        m["input_contracts"].append(dict(operation="create", parameter="owner_id", type=dict(type="string", domain=[], nullable=False), presence="required", binding=dict(source="cli_flag", flag="--owner-id", encoding="text"), missing=dict(kind="application_error", error="owner_required")))
        refs["references"].append(reference(domain, "owner_id", domain + "Operator", deletion="unavailable"))
        r["record"].update(owner_id="operator", limit=2)
        atom = m["atomic_state_semantics"]
        for op in atom["operations"]:
            if op["command"] == "create": op["parameters"]["owner_id"] = dict(type="string", domain=[], nullable=False)
        adjust = refs["operations"][0]
        hi = identity(r["history"])
        adjust["parameters"]["successor_history"] = parameter(hi, "successor-history")
        start_type = {**TIME, "nullable": True}
        start = parameter(start_type, "start", encoding="json"); start["default"] = r["record"]["created_at"]
        adjust["parameters"]["start"] = start
        op = atom["operations"][0]
        op["parameters"]["successor_history"] = hi
        op["parameters"]["start"] = start_type
        positive = compare(operand("parameter", INTEGER, name="adjustment"), operand("literal", INTEGER, value=0), op="gt")
        adjust["changes"][0]["when"] = copy.deepcopy(positive)
        history, successor = op["creations"]
        history.update(binding="history", when=positive, depends_on=[])
        successor.update(binding="successor", when=positive, depends_on=[])
        successor["bindings"]["owner_id"] = binding(operand("after", actor, name="owner_id"))
        nullable = dict(type="integer", domain=[], nullable=True)
        refined = node("days", "refine_integer", [operand("before", nullable, name="limit")]); refined["null"] = dict(policy="reject")
        scale = node("seconds", "days_to_seconds", [operand("computed", INTEGER, name="days")], DURATION, deps=["days"]); scale["conversion"] = copy.deepcopy(CONVERSION)
        start_instant = node("start_instant", "refine_instant", [operand("parameter", start_type, name="start")], TIME); start_instant["null"] = dict(policy="reject")
        shifted = node("next_instant", "shift_utc_seconds", [operand("computed", TIME, name="start_instant"), operand("computed", DURATION, name="seconds")], TIME, deps=["start_instant", "seconds"])
        successor["computations"] = graph([refined, scale, start_instant, shifted])
        successor["bindings"]["created_at"] = binding(operand("computed", TIME, name="next_instant"))
        successor["bindings"]["limit"] = binding(operand("computed", INTEGER, name="days"))
        child = copy.deepcopy(history)
        child.update(binding="successor_history", depends_on=["successor"])
        child["bindings"]["id"] = binding(operand("parameter", hi, name="successor_history"))
        child["bindings"]["subject"] = binding(dict(kind="created", type=identity(domain), effect="successor", entity=domain, field="id", alternative=None))
        child["bindings"]["quantity"] = binding(dict(kind="created", type=successor["bindings"]["quantity"]["source"]["type"], effect="successor", entity=domain, field="quantity", alternative=None))
        child["computations"] = graph([node("second_ordinal", "add", [operand("literal", INTEGER, value=2), copy.deepcopy(op["computations"]["nodes"][0]["operands"][0])])])
        child["bindings"]["ordinal"] = binding(operand("computed", INTEGER, name="second_ordinal"))
        # Deliberately forward-reference an image: declaration order is not meaning.
        op["creations"] = [child, history, successor]
        actor_match = compare(operand("field", actor, name="related.id"), operand("parameter", actor, name="actor"))
        has_role = extent(domain + "Operator", group("and", actor_match, compare(operand("field", role, name="related.role"), operand("literal", role, value="editor"))), value=1)
        owner = compare(operand("field", actor, name="primary.owner_id"), operand("parameter", actor, name="actor"))
        allowed = has_role if domain == "Inventory" else group("and", has_role, owner)
        if domain == "Account":
            permitted = dict(type="collection", element=actor, ordering="insertion", duplicates="unique", equality="exact")
            allowed = group("and", allowed, compare(operand("parameter", actor, name="actor"), operand("literal", permitted, value=["operator"]), member=True))
        trusted = copy.deepcopy(adjust); trusted["command"] = "trusted-adjust"
        refs["operations"].append(trusted)
        trusted_op = copy.deepcopy(op); trusted_op["command"] = "trusted-adjust"; atom["operations"].append(trusted_op)
        auth = dict(operations=[permission("adjust", domain, op["parameters"], allowed), permission("trusted-adjust", domain, op["parameters"], allowed, "trusted_context")])
        generated = copy.deepcopy(adjust); generated["command"] = "generated-adjust"; refs["operations"].append(generated)
        generated_op = copy.deepcopy(op); generated_op["command"] = "generated-adjust"
        uuid = next(c["capability"] for o in atom["operations"] for c in o["resources"] if c["type"]["type"] == "identifier")
        generated_op["resources"] += [dict(name=n, type=hi, capability=uuid, observation="binding") for n in ("original_history_id", "successor_history_id")]
        for effect, name in ((generated_op["creations"][0], "successor_history_id"), (generated_op["creations"][1], "original_history_id")):
            effect["bindings"]["id"] = binding(operand("resource", hi, name=name))
        atom["operations"].append(generated_op)
        auth["operations"].append(permission("generated-adjust", domain, op["parameters"], allowed))
        create = next(o for o in atom["operations"] if o["command"] == "create")
        create_params = {**create["parameters"], "owner_id": actor}
        create_owner = compare(operand("parameter", actor, name="owner_id"), operand("parameter", actor, name="actor"))
        create_permission = permission("create", domain, create_params, group("and", has_role, create_owner))
        create_permission["lookup"] = None
        auth["operations"].append(create_permission)
        m["authorization_semantics"] = auth
        source = "Synthetic " + domain + " R5.113 contract. Complete typed declarations are normative: " + repr(dict(scalar=f, mutable=m, references=refs)) + ". Explicit parameter actor selection does not authenticate a caller. trusted-adjust binds only controlled_host authorized embedding context; CLI has no trusted source. Roles are persisted current fields; no role migration or default is inferred. Permissions observe committed before state and reject unchanged. Positive adjustment selects two history records and one successor atomically. Unselected successor computation does not execute. Created-image binding is exact and graph ordered, separate from primary after and committed post images. Nullable limit rejects null when selected; days are elapsed days of 86400 seconds, signed and overflow checked."
        domains = dict(atomic_state_profile="atomic-durable-state-1", computation_profile="typed-computation-1", primary_interface_profile="primary-value-interfaces-1", authorization_profile="prewrite-authorization-1", effect_composition_profile="conditional-created-effects-1", duration_conversion_profile="elapsed-day-conversion-1")
        r["candidate"] = assemble("authorization-" + domain.lower(), source, f, m, refs, domains)
        r["entities"] = {e["name"]: copy.deepcopy(e["initial"]) for e in refs["entities"]}
        r["entities"][domain + "Operator"] = [dict(id="operator", role="editor"), dict(id="viewer", role="viewer"), dict(id="other", role="editor")]
        result.append(r)
    # Project is a distinct permission scope using the same generic compositions.
    project = copy.deepcopy(result[0])
    def rename(v):
        if type(v) is str: return v.replace("Inventory", "Project").replace("inventory", "project")
        if type(v) is dict: return {rename(k): rename(x) for k, x in v.items()}
        if type(v) is list: return [rename(x) for x in v]
        return v
    result.append(rename(project))
    return result


def args(value=1, actor="operator", command="adjust"):
    return [command, "--id", "a", "--adjustment", str(value), "--actor", actor, "--record", "h", "--successor", "b", "--successor-history", "sh"]


def plan(r):
    path = r["path"]; row = r["record"]
    initial = dict(schema_version=2, records=[row], entities=r["entities"])
    after = {**row, "quantity": 11}
    next_row = {**after, "id": "b", "created_at": "2020-01-03T00:00:00Z"}
    history = [dict(id="h", subject="a", actor="operator", ordinal=1, quantity=11), dict(id="sh", subject="b", actor="operator", ordinal=2, quantity=11)]
    checks = [step(path, ["create", "--nickname", "new", "--owner-id", "operator", "--actor", "viewer"], error="permission_denied"), step(path, ["create", "--nickname", "new", "--owner-id", "other", "--actor", "operator"], error="permission_denied"), step(path, args(actor="viewer"), error="permission_denied"), step(path, args(actor="absent"), error="permission_denied"), step(path, args(command="trusted-adjust"), error="context_required")]
    if r["primary"] not in ("Inventory", "Project"): checks.append(step(path, args(actor="other"), error="permission_denied"))
    checks += [step(path, args(-1), row, preserve=False), step(path, args(0), row, preserve=False), step(path, ["history"], []), step(path, args(), after, preserve=False), step(path, ["list"], [after, next_row]), step(path, ["history"], history), step(path, args(), error="history_exists")]
    cases = [dict(id="permission-conditional-dependency-restart", initial_files=[dict(path=path, json=initial)], steps=checks)]
    cases.append(dict(id="independent-declared-identity-observations", initial_files=[dict(path=path, json=initial)], steps=[step(path, args(command="generated-adjust"), after, preserve=False), step(path, ["history"], contains=['"ordinal": 1', '"ordinal": 2', '"subject": "b"'])]))
    cases.append(dict(id="creation-role-default-is-not-migration", initial_files=[dict(path=path, json=initial)], steps=[step(path, ["create-operator", "--id", "new"], dict(id="new", role="viewer"), preserve=False), step(path, ["create-operator", "--id", "editor", "--role", "editor"], dict(id="editor", role="editor"), preserve=False), step(path, ["create-operator", "--id", "bad", "--role", "null"], error="invalid_value")]))
    old_roles = copy.deepcopy(initial)
    for user in old_roles["entities"][r["primary"] + "Operator"]: user.pop("role")
    cases.append(dict(id="unauthorized-historical-role-default", initial_files=[dict(path=path, json=old_roles)], steps=[step(path, args(), error="invalid_state")]))
    if r["primary"] == "Account":
        other_owned = {**initial, "records": [{**row, "owner_id": "other"}]}
        cases.append(dict(id="declared-permitted-set", initial_files=[dict(path=path, json=other_owned)], steps=[step(path, args(actor="other"), error="permission_denied")]))
    cases.append(dict(id="nullable-instant-UTC-boundary", initial_files=[dict(path=path, json=initial)], steps=[step(path, args() + ["--start", "null"], error="computation_failed"), step(path, args() + ["--start", json.dumps("9999-12-31T00:00:00Z")], error="computation_failed"), step(path, args() + ["--start", json.dumps("2020-02-28T00:00:00Z")], after, preserve=False), step(path, ["list"], [after, {**after, "id": "b", "created_at": "2020-03-01T00:00:00Z"}])]))
    for value, error in ((None, "computation_failed"), (106751991167301, "computation_failed"), (-1, None)):
        original = {**row, "limit": value}
        expected = {**original, "quantity": 11}
        steps = [step(path, args(), expected if error is None else None, error=error, preserve=error is not None)]
        if error is None: steps.append(step(path, ["list"], [{**expected, "id": "b", "created_at": "2019-12-31T00:00:00Z"}, expected]))
        cases.append(dict(id="nullable-duration-" + str(value), initial_files=[dict(path=path, json={**initial, "records": [original]})], steps=steps))
    original = {**row, "limit": None}
    cases.append(dict(id="unselected-null-is-not-zero", initial_files=[dict(path=path, json={**initial, "records": [original]})], steps=[step(path, args(0), original, preserve=False), step(path, ["history"], [])]))
    return external_plan(r["candidate"], path, cases)
