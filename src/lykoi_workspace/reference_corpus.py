"""Source-authorized synthetic reference compositions across six public domains."""
import copy
import hashlib

from air_compiler.references import identity
from lykoi_controller import canonical
from lykoi_pipeline import mutable_profile
from .mutable_corpus import capture
from .input_corpus import parameters
from .predicate_corpus import operand, compare, group

BOOLEAN = dict(type="boolean", domain=[], nullable=False)


def sequence(t, duplicates="unique"):
    return dict(type="collection", element=t, ordering="insertion", duplicates=duplicates, equality="exact")


def extent(entity, predicate, relation="eq", value=0):
    return dict(kind="extent", result_type="boolean", selection=dict(entity=entity, binding="related", predicate=predicate), relation=relation, value=value)


def reach(entity, field, source, target):
    return dict(kind="reachable", result_type="boolean", entity=entity, field=field, source=source, target=target, paths="nonempty")


def parameter(t, flag, missing="missing_value", invalid="invalid_value", encoding="text"):
    return dict(type=copy.deepcopy(t), flag="--" + flag, encoding=encoding, missing_error=missing, invalid_error=invalid)


def write(field, source, operation="replace", error="invalid_reference"):
    return dict(field=field, source=source, operation=operation, invalid_error=error)


def operation(command, entity, kind, params=None, changes=None, guards=None, lookup=None, missing=None, duplicate=None, order=None):
    return dict(command=command, entity=entity, kind=kind, parameters=params or {}, lookup=lookup, missing_error=missing, duplicate_error=duplicate, changes=changes or [], guards=guards or [], order=order or [])


def reference(entity, field, target, deletion="restrict", migration=None):
    return dict(entity=entity, field=field, target=target, existence=dict(policy="required", error="missing_target"), deletion=dict(policy=deletion, error="reference_in_use" if deletion == "restrict" else None), migration=migration)


def assemble(name, source, scalar, mutable, refs, domains=None):
    mutable = copy.deepcopy(mutable)
    mutable["reference_semantics"] = copy.deepcopy(refs)
    rows = []
    for profile, facts in (("existing-scalar-1", scalar), (mutable_profile.PROFILE, mutable)):
        for facet, value in facts.items():
            rows.append(dict(id=name + "/" + facet, basis="STATED", derived_from=[], source_quote=source, statement="Authorized " + facet, relation=dict(kind="crud", parameters=dict(profile=profile, facet=facet, value=copy.deepcopy(value)))))
    context = dict(capability_profile=mutable_profile.PROFILE, input_value_profile="typed-input-values-1", predicate_profile="typed-predicates-1", reference_profile="persistent-references-1")
    context.update(domains or {})
    return dict(id=name, source=source, rows=rows, question=None, domains=context)


def captures():
    result = []
    for primary, target in (("Order", "Customer"), ("Project", "User"), ("Document", "Owner"), ("Department", "Employee"), ("Team", "Member"), ("Category", "CategoryOwner")):
        r = capture("profile", "allow", "replace", [])
        f = r["scalar"]
        f["storage"]["path"] = primary.lower() + ".json"
        f["fields"].append(dict(name="owner_id", type="identifier", domain=[], nullable=False, preservation="verbatim"))
        f["creation"]["bindings"].append(dict(field="owner_id", source="input", value=None, default=None))
        f["creation"]["validation"].append(dict(field="owner_id", rule="nonblank", error="missing_target"))
        m = dict(collections=[dict(name=n, element=dict(type="identifier", domain=[]), ordering="insertion", duplicates="unique", equality="exact", creation=dict(source="literal", value=[]), migration=[]) for n in ("member_ids", "parent_ids")], mutations=[], creation_pipelines=[], predicate_semantics=dict(booleans=[], guards=[], invariants=[]))
        base = mutable_profile.scalar.lower(f)
        m["input_contracts"] = parameters(base, m)
        pi, ti = identity(primary), identity(target)
        pkey = operand("field", pi, name="primary.id")
        rid = operand("field", ti, name="related.id")
        member = compare(rid, operand("field", sequence(ti), name="primary.member_ids"), member=True)
        active = compare(operand("field", BOOLEAN, name="related.active"), operand("literal", BOOLEAN, value=True))
        all_active = extent(target, group("and", member, group("not", active)))
        params = {"id": parameter(pi, "id"), "value": parameter(ti, "value")}
        ops = [operation("create-target", target, "create", {"id": parameter(ti, "id"), "active": parameter(BOOLEAN, "active", encoding="json")}, [write("id", operand("parameter", ti, name="id")), write("active", operand("parameter", BOOLEAN, name="active"))], duplicate="target_exists"),
            operation("list-targets", target, "list", order=["id"]),
            operation("set-target-state", target, "update", {"id": parameter(ti, "id"), "active": parameter(BOOLEAN, "active", encoding="json")}, [write("active", operand("parameter", BOOLEAN, name="active"))], lookup="id", missing="missing_target"),
            operation("delete-target", target, "delete", {"id": parameter(ti, "id")}, lookup="id", missing="missing_target")]
        for command, field, action in (("replace-owner", "owner_id", "replace"), ("add-member", "member_ids", "add_unique"), ("remove-member", "member_ids", "remove")):
            ops.append(operation(command, primary, "update", copy.deepcopy(params), [write(field, operand("parameter", ti, name="value"), action)], lookup="id", missing="record_not_found"))
        parent = operand("parameter", pi, name="value")
        guards = [dict(predicate=group("and", group("not", compare(parent, pkey)), group("not", reach(primary, "parent_ids", parent, pkey))), error="cycle_rejected")]
        ops.append(operation("add-parent", primary, "update", {"id": parameter(pi, "id"), "value": parameter(pi, "value")}, [write("parent_ids", parent, "append")], guards=guards, lookup="id", missing="record_not_found"))
        ops.append(operation("delete-primary", primary, "delete", {"id": parameter(pi, "id")}, lookup="id", missing="record_not_found"))
        refs = dict(primary=primary, entities=[dict(name=target, key="id", fields=dict(id=ti, active=BOOLEAN), initial=[])], references=[reference(primary, "owner_id", target), reference(primary, "member_ids", target), reference(primary, "parent_ids", primary)], operations=ops,
            guards=[dict(command="advance", parameters={"id": pi}, predicate=all_active, error="related_state_rejected")], commit=dict(scope="one_store", mutation="one_record", isolation="exclusive_operation", rejection="unchanged"))
        if primary == "Department":
            # Reverse selection is exercised from a distinct referring entity.
            e = dict(name="Employment", key="id", fields=dict(id=identity("Employment"), department_id=pi), initial=[])
            refs["entities"].append(e)
            refs["references"].append(reference("Employment", "department_id", primary))
            refs["operations"].append(operation("create-employment", "Employment", "create", {"id": parameter(identity("Employment"), "id"), "department": parameter(pi, "department")}, [write("id", operand("parameter", identity("Employment"), name="id")), write("department_id", operand("parameter", pi, name="department"))], duplicate="employment_exists"))
        source = ("Public " + primary + " persistent reference contract. The following complete typed authority is normative: " + repr(dict(scalar=f, mutable=m, reference_composition=refs)) + ". Identity values use existing exact nonblank strings with nominal entity types. Reference errors, finite selected domains, collection order/duplicate policy, related ALL guard, restrictive deletion and nonempty-path cycle policy are explicit. One coherent store operation reads related entities and mutates one record; rejected operations leave bytes unchanged. No cascade or multi-record effects.")
        candidate = assemble("reference-" + primary.lower(), source, f, m, refs)
        initial = [dict(id=i, nickname=i, description="preserved", state="active", created_at="2020-01-01T00:00:00Z", owner_id="owner", member_ids=[], parent_ids=[]) for i in ("a", "b", "c")]
        result.append(dict(candidate=candidate, scalar=f, mutable=m, references=refs, primary=primary, target=target, path=f["storage"]["path"], records=initial))
    return result


def external_plan(candidate, path, cases):
    ids = [o["id"] for o in candidate["rows"]]
    for c in cases:
        c.update(obligations=ids, initial_state="fresh_directory", invariants=["Typed identities, coherent reference integrity and unchanged rejected bytes"], transitions="Separate subprocesses and reload", rejections="Only explicit declared errors")
        c["identity"] = hashlib.sha256(canonical(c)).hexdigest()
    return dict(version="external-cli-plan-1", outcome="READY", producer="R5.109 source-side literal oracle", source_sha256=hashlib.sha256(candidate["source"].encode()).hexdigest(), cases=cases, coverage=[dict(obligation=i, classification="EXERCISED", justification="Explicit reference, reverse selection, related-state, cycle, reload and rejection partitions", cases=[c["identity"] for c in cases]) for i in ids], limitations=["Same-agent captures/inventory/oracle, synthetic owner approval; finite behavioral evidence, not held-out generalization"])


def step(path, argv, expected=None, error=None, preserve=True, contains=None):
    s = dict(argv=argv, returncode=1 if error else 0, contains=contains or [])
    if preserve: s["preserved"] = [path]
    if error: s.update(stdout_exact="", stderr_json={"error": error})
    else:
        s["stderr_exact"] = ""
        if expected is not None: s["stdout_json"] = copy.deepcopy(expected)
    return s


def plan(r):
    path = r["path"]
    primary, target = r["primary"], r["target"]
    initial = dict(schema_version=1, records=copy.deepcopy(r["records"]), entities={e["name"]: copy.deepcopy(e["initial"]) for e in r["references"]["entities"]})
    initial["entities"][target] = [dict(id="owner", active=True), dict(id="m1", active=True), dict(id="m2", active=False)]
    a, b, c = copy.deepcopy(r["records"])
    steps = []
    def add(argv, expected=None, error=None, preserve=True, contains=None): steps.append(step(path, argv, expected, error, preserve, contains))
    add(["list"], [a, b, c])
    add(["replace-owner", "--id", "a", "--value", "absent"], error="missing_target")
    add(["replace-owner", "--id", "absent", "--value", "owner"], error="record_not_found")
    add(["add-member", "--id", "a", "--value", "absent"], error="missing_target")
    a["member_ids"] = ["m1"]
    add(["add-member", "--id", "a", "--value", "m1"], a, preserve=False)
    add(["add-member", "--id", "a", "--value", "m1"], a, preserve=False)
    a["member_ids"].append("m2")
    add(["add-member", "--id", "a", "--value", "m2"], a, preserve=False)
    add(["advance", "--id", "a"], error="related_state_rejected")
    add(["set-target-state", "--id", "m2", "--active", "true"], {"id": "m2", "active": True}, preserve=False)
    a["state"] = "inactive"
    add(["advance", "--id", "a"], a, preserve=False)
    add(["delete-target", "--id", "m2"], error="reference_in_use")
    a["member_ids"] = ["m1"]
    add(["remove-member", "--id", "a", "--value", "m2"], a, preserve=False)
    add(["delete-target", "--id", "m2"], {"id": "m2", "active": True}, preserve=False)
    add(["replace-owner", "--id", "b", "--value", "m2"], error="missing_target")
    add(["delete-target", "--id", "owner"], error="reference_in_use")
    add(["add-parent", "--id", "b", "--value", "b"], error="cycle_rejected")
    b["parent_ids"] = ["c"]
    add(["add-parent", "--id", "b", "--value", "c"], b, preserve=False)
    c["parent_ids"] = ["a"]
    add(["add-parent", "--id", "c", "--value", "a"], c, preserve=False)
    add(["add-parent", "--id", "a", "--value", "b"], error="cycle_rejected")
    add(["add-parent", "--id", "b", "--value", "c"], error="invalid_reference")
    add(["delete-primary", "--id", "c"], error="reference_in_use")
    add(["list"], [a, b, c])
    add(["create-target", "--id", "owner", "--active", "true"], error="target_exists")
    add(["create-target", "--id", " ", "--active", "true"], error="invalid_reference")
    if primary == "Department":
        add(["create-employment", "--id", "job", "--department", "b"], {"id": "job", "department_id": "b"}, preserve=False)
        add(["delete-primary", "--id", "b"], error="reference_in_use")
    cases = [dict(id="integrity-reload", initial_files=[dict(path=path, json=initial)], steps=steps)]
    create = [step(path, ["create-target", "--id", "fresh", "--active", "true"], {"id": "fresh", "active": True}, preserve=False),
        step(path, ["create", "--nickname", "New", "--owner-id", "missing"], error="missing_target"),
        step(path, ["create", "--nickname", "New", "--owner-id", "fresh"], preserve=False, contains=['"owner_id": "fresh"', '"parent_ids": []']),
        step(path, ["list"], contains=['"owner_id": "fresh"']),
        step(path, ["delete-target", "--id", "fresh"], error="reference_in_use")]
    cases.append(dict(id="creation", initial_files=[], steps=create))
    # ALL over an explicitly empty related selection is true.
    empty = copy.deepcopy(initial)
    cases.append(dict(id="empty-related-domain", initial_files=[dict(path=path, json=empty)], steps=[step(path, ["advance", "--id", "a"], {**r["records"][0], "state": "inactive"}, preserve=False)]))
    return external_plan(r["candidate"], path, cases)
