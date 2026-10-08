"""R5.114 source-bound historical transformations and sealed host observations."""
import copy

from air_compiler.references import identity
from air_compiler.computation import INTEGER
from .authorization_corpus import captures as authorized
from .reference_corpus import assemble, reference, sequence, write, operation, step, external_plan
from .predicate_corpus import operand
from .computation_corpus import graph, node


def captures():
    result = []
    for r in authorized():
        domain, refs, m, f = r["primary"], r["references"], r["mutable"], r["scalar"]
        operator = domain + "Operator"
        user = next(e for e in refs["entities"] if e["name"] == operator)
        role = user["fields"]["role"]
        user["fields"]["historical_role"] = copy.deepcopy(role)
        create = next(o for o in refs["operations"] if o["command"] == "create-operator")
        create["changes"].append(write("historical_role", operand("literal", role, value="viewer")))
        for u in r["entities"][operator]: u["historical_role"] = u["role"]
        entity = {"Inventory": "Stock", "Document": "DocumentRevision", "Account": "Employee", "Renewal": "Subscription", "Project": "Membership"}[domain]
        fields = dict(id=identity(entity), amount=INTEGER, note=dict(type="string", domain=[]))
        old = dict(id="historical", amount=5, note="verbatim unrelated state")
        if domain == "Document":
            fields["prior_owner"] = identity(operator); old["prior_owner"] = "operator"
            refs["references"].append(reference(entity, "prior_owner", operator, deletion="unavailable"))
        nullable = dict(type="integer", domain=[], nullable=True)
        additions = []
        if domain in ("Inventory", "Renewal"):
            fields["reserved"] = nullable
            additions.append(dict(field="reserved", source=operand("literal", nullable, value=None)))
        elif domain == "Document":
            fields["owner"] = identity(operator)
            refs["references"].append(reference(entity, "owner", operator, deletion="unavailable"))
            additions.append(dict(field="owner", source=operand("before", identity(operator), name="prior_owner")))
        elif domain == "Project":
            fields["members"] = sequence(identity(operator))
            refs["references"].append(reference(entity, "members", operator, deletion="unavailable"))
            additions.append(dict(field="members", source=operand("literal", fields["members"], value=["operator"])))
        else:
            fields["role"] = role
            additions.append(dict(field="role", source=operand("literal", role, value="editor")))
        fields["adjusted"] = nullable
        refs["entities"].append(dict(name=entity, key="id", fields=fields, initial=[]))
        refs["operations"].append(operation("list-historical", entity, "list", order=["id"]))
        roles = dict(entity=operator, add_fields=[dict(field="role", source=operand("before", role, name="historical_role"))], computations=None)
        steps = [dict(**{"from": 2}, to=3, entities=[roles, dict(entity=entity, add_fields=additions, computations=None)]),
                 dict(**{"from": 3}, to=4, entities=[dict(entity=entity, add_fields=[dict(field="adjusted", source=operand("computed", INTEGER, name="adjusted"))], computations=graph([node("adjusted", "add", [operand("before", INTEGER, name="amount"), operand("literal", INTEGER, value=1)])]))])]
        m["historical_state_semantics"] = dict(steps=steps, invalid="invalid_state", rejection="unchanged", preservation="unrelated_fields")
        f["storage"]["version"] = 4
        domains = copy.deepcopy(r["candidate"]["domains"])
        domains["historical_state_profile"] = "historical-related-state-1"
        source = "Synthetic " + domain + " historical-state R5.114 contract. Complete typed declarations are normative: " + repr(dict(scalar=f, mutable=m, references=refs)) + ". New operators default to viewer; historical operator role derives only from persisted historical_role, and absent/invalid historical_role rejects. Employee introduction explicitly assigns editor independently of creation. References preserve their nominal target. Related-only 2->3 and 3->4 introductions preserve all other fields; computations see the whole transition-before store. Each invalid or failed migration leaves all durable bytes unchanged. Trusted-adjust receives only verifier-owned controlled_host context; ordinary CLI actor is never trusted identity. No authentication is claimed."
        r["candidate"] = assemble("historical-" + domain.lower(), source, f, m, refs, domains)
        r["entity"], r["old_related"] = entity, old
        current = copy.deepcopy(old)
        for a in additions:
            current[a["field"]] = a["source"].get("value", old.get(a["source"].get("name")))
        current["adjusted"] = 6
        r["entities"][entity] = [current]
        result.append(r)
    ambiguous = copy.deepcopy(result[2])
    ambiguous["candidate"]["id"] += "-ambiguous"
    ambiguous["candidate"]["question"] = "Which historical role is authorized when historical_role is absent? New-user defaults do not answer this."
    result.append(ambiguous)
    return result


def host_step(path, actor="operator", inputs=None, context_source="controlled_host", expected=None, error=None, preserve=True):
    s = step(path, [], expected, error, preserve)
    s["host"] = dict(command="trusted-adjust", inputs=inputs or dict(id="a", adjustment=1, record="h", successor="b", successor_history="sh"), execution_context=dict(source=context_source, actor=actor))
    return s


def plan(r):
    if r["candidate"]["question"]: return None
    path, entity, domain = r["path"], r["entity"], r["primary"]
    current = dict(schema_version=4, records=[r["record"]], entities=r["entities"])
    cases = []
    # Reuse literal source-side migration expectations, not target-generated ones.
    for version in (1, 2, 3, 4):
        old = copy.deepcopy(current); old["schema_version"] = version
        if version == 1:
            old["records"][0].pop("quantity"); old["records"][0].pop("limit")
        if version <= 2:
            for u in old["entities"][domain + "Operator"]: u.pop("role")
            old["entities"][entity] = [r["old_related"]]
        elif version == 3: old["entities"][entity][0].pop("adjusted")
        expected = copy.deepcopy(current)
        if version == 1: expected["records"][0].update(quantity=10, limit=None)
        migrated = sum(len(rows) for rows in old["entities"].values()) + 1 if version < 4 else 0
        first = step(path, ["migrate"], dict(migrated=migrated), preserve=version == 4)
        first["files"] = [dict(path=path, json=expected)]
        cases.append(dict(id="cross-version-" + str(version), initial_files=[dict(path=path, json=old)], steps=[first, step(path, ["migrate"], dict(migrated=0)), step(path, ["list-historical"], expected["entities"][entity])]))
    for mode in ("missing-authority", "invalid-role", "invalid-number", "unknown-field", "dangling"):
        old = copy.deepcopy(current); old["schema_version"] = 2
        for u in old["entities"][domain + "Operator"]: u.pop("role")
        old["entities"][entity] = [copy.deepcopy(r["old_related"])]
        error = "invalid_state"
        if mode == "missing-authority": old["entities"][domain + "Operator"][0].pop("historical_role")
        if mode == "invalid-role": old["entities"][domain + "Operator"][0]["historical_role"] = "invented"
        if mode == "invalid-number": old["entities"][entity][0]["amount"] = True
        if mode == "unknown-field": old["entities"][entity][0]["unexpected"] = 1
        if mode == "dangling": old["records"][0]["owner_id"] = "missing"; error = "missing_target"
        cases.append(dict(id=mode, initial_files=[dict(path=path, json=old)], steps=[step(path, ["migrate"], error=error)]))
    after = {**r["record"], "quantity": 11}
    post = copy.deepcopy(current); post["records"] = [after, {**after, "id": "b", "created_at": "2020-01-03T00:00:00Z"}]
    post["entities"][r["history"]] = [dict(id="sh", subject="b", actor="operator", ordinal=2, quantity=11), dict(id="h", subject="a", actor="operator", ordinal=1, quantity=11)]
    forged = dict(id="a", adjustment=1, actor="other", record="h", successor="b", successor_history="sh")
    checks = [host_step(path, "viewer", error="permission_denied"), host_step(path, inputs=forged, error="invalid_actor"), host_step(path, context_source="cli", error="invalid_actor"), step(path, ["trusted-adjust", "--id", "a", "--adjustment", "1", "--actor", "operator", "--record", "h", "--successor", "b", "--successor-history", "sh"], error="context_required")]
    if domain not in ("Inventory", "Project"): checks.append(host_step(path, "other", error="permission_denied"))
    success = host_step(path, expected=after, preserve=False); success["files"] = [dict(path=path, json=post)]
    checks += [success, step(path, ["list-historical"], r["entities"][entity]), host_step(path, error="history_exists")]
    cases.append(dict(id="sealed-host-permission-restart", initial_files=[dict(path=path, json=current)], steps=checks))
    persisted = copy.deepcopy(current)
    persisted["entities"][domain + "Operator"][0]["historical_role"] = "viewer"
    cases.append(dict(id="current-role-and-new-default-are-independent", initial_files=[dict(path=path, json=persisted)], steps=[step(path, ["migrate"], dict(migrated=0)), step(path, ["create-operator", "--id", "new"], dict(id="new", role="viewer", historical_role="viewer"), preserve=False)]))
    return external_plan(r["candidate"], path, cases)
