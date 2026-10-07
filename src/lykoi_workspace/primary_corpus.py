"""Unrelated synthetic primary numeric/context/history/successor authority."""
import copy

from air_compiler.computation import INTEGER, TIME
from air_compiler.references import identity, erase, compose as references
from air_compiler.mutable_values import compose
from air_compiler.atomic_state import COMMIT
from lykoi_pipeline import mutable_profile
from .mutable_corpus import capture, mutation, change
from .input_corpus import parameters
from .reference_corpus import assemble, operation, parameter, write, reference, step, external_plan
from .predicate_corpus import operand, compare
from .computation_corpus import node, graph, count
from .atomic_state_corpus import binding


def captures():
    result = []
    for domain in ("Inventory", "Document", "Account", "Session", "Renewal"):
        f = capture("profile", "allow", "replace", [])["scalar"]
        f["storage"].update(path=domain.lower() + "-primary.json", version=2)
        num = dict(type="integer", domain=[], nullable=False)
        nullable = dict(type="integer", domain=[], nullable=True)
        ints = [dict(name="quantity", type=num, creation=dict(source="literal", value=0), migration=[dict(**{"from": 1}, to=2, value=10)]), dict(name="limit", type=nullable, creation=dict(source="input_default", input="limit", default=7, pipeline=[], error="invalid_number"), migration=[dict(**{"from": 1}, to=2, value=None)])]
        actor = identity(domain + "Operator")
        contexts = [dict(command=cmd, name="actor", type=actor, role="actor", authority="explicit_parameter", missing_error="actor_required", invalid_error="invalid_actor") for cmd in ("create", "advance", "set-limit")]
        m = dict(collections=[], mutations=[mutation("set-limit", [change("limit", optional=True, steps=[])])], creation_pipelines=[], predicate_semantics=dict(booleans=[], guards=[], invariants=[]), primary_interfaces=dict(integers=ints, context_inputs=contexts))
        base = mutable_profile.scalar.lower({**f, "storage": {**f["storage"], "version": 1}})
        m["input_contracts"] = parameters(base, m)
        # Nominal actors are parameters, never the primary owner or an ambient user.
        hi, pi = identity(domain + "History"), identity(domain)
        params = dict(id=parameter(pi, "id"), adjustment=parameter(INTEGER, "adjustment", encoding="json"), actor=parameter(actor, "actor", missing="actor_required"), record=parameter(hi, "record"), successor=parameter(pi, "successor"))
        op = operation("adjust", domain, "update", params, [write("quantity", operand("computed", num, name="quantity"))], lookup="id", missing="record_not_found")
        op["computations"] = graph([node("quantity", "add", [operand("before", num, name="quantity"), operand("parameter", INTEGER, name="adjustment")], num)])
        day = parameter(TIME, "day", invalid="invalid_day", encoding="utc_day")
        day["conversion"] = dict(source="gregorian_utc_day", target="instant", boundary="start_of_day", timezone="UTC", precision="seconds", invalid="reject")
        day_params = dict(id=params["id"], day=day, actor=params["actor"], record=params["record"])
        set_day = operation("set-day", domain, "update", day_params, [write("created_at", operand("parameter", TIME, name="day"))], lookup="id", missing="record_not_found")
        history = domain + "History"
        refs = dict(primary=domain, entities=[dict(name=domain + "Operator", key="id", fields=dict(id=actor), initial=[dict(id="operator")]), dict(name=history, key="id", fields=dict(id=hi, subject=pi, actor=actor, ordinal=INTEGER, quantity=num), initial=[])], references=[reference(history, "subject", domain, deletion="permit"), reference(history, "actor", domain + "Operator", deletion="unavailable")], operations=[op, set_day], guards=[], commit=dict(scope="one_store", mutation="one_record", isolation="exclusive_operation", rejection="unchanged"))
        ir = compose(base, m); ri = references(ir, refs)
        model = ir["model"]
        uuid = next(c["id"] for c in model["capabilities"] if c["kind"] == "uuid_v4")
        clock = next(c["id"] for c in model["capabilities"] if c["kind"] == "utc_clock")
        operations = []
        for cmd in ("adjust", "create", "advance", "set-limit"):
            pt = {n: p["type"] for n, p in params.items()} if cmd == "adjust" else {p["parameter"]: p["type"] for p in m["input_contracts"] if p["operation"] == cmd}
            if "id" in pt: pt["id"] = pi
            pt["actor"] = actor
            resources = [dict(name="clock", type=TIME, capability=clock)]
            if cmd != "adjust": resources.append(dict(name="history_id", type=hi, capability=uuid))
            ordinal = graph([node("size", "value", [count(history, hi)]), node("ordinal", "add", [operand("computed", INTEGER, name="size"), operand("literal", INTEGER, value=1)], deps=["size"])])
            row = dict(entity=history, duplicate_error="history_exists", bindings=dict(id=binding(operand("parameter", hi, name="record") if cmd == "adjust" else operand("resource", hi, name="history_id")), subject=binding(operand("after", pi, name="id")), actor=binding(operand("parameter", actor, name="actor")), ordinal=binding(operand("computed", INTEGER, name="ordinal")), quantity=binding(operand("after", num, name="quantity"))))
            creations = [row]
            if cmd == "adjust":
                bindings = {n: binding(operand("after", t, name=n)) for n, t in ri["types"][domain].items()}
                bindings["id"] = binding(operand("parameter", pi, name="successor"))
                bindings["created_at"] = binding(operand("resource", ri["types"][domain]["created_at"], name="clock"))
                creations.append(dict(entity=domain, bindings=bindings, duplicate_error="successor_exists"))
            operations.append(dict(command=cmd, entity=domain, parameters=pt, resources=resources, on="success", sampling="once_per_operation", ordering="declared_creation_occurrence", computations=ordinal, creations=creations))
        fields = {n: erase(t) for n, t in ri["types"][history].items()}
        day_atom = copy.deepcopy(operations[0])
        day_atom.update(command="set-day", parameters={n: p["type"] for n, p in day_params.items()}, creations=day_atom["creations"][:1])
        operations.append(day_atom)
        q = dict(id="history", source=dict(collection=history, fields=fields, unique_key="id"), parameters={}, predicate=compare(operand("field", INTEGER, name="ordinal"), operand("literal", INTEGER, value=0), op="ge"), comparison=dict(scope="predicate_nodes"), ordering=[dict(field="ordinal", direction="ASC"), dict(field="id", direction="ASC")], validation=[], inclusion=[], effect=dict(state="read_only", persistence="unchanged"), result=dict(shape="collection", cardinality="zero_or_more", no_match="empty"))
        m["atomic_state_semantics"] = dict(operations=operations, queries=[q], append_only=[history], commit=copy.deepcopy(COMMIT))
        source = "Synthetic " + domain + " primary contract. Complete typed declarations are normative: " + repr(dict(scalar=f, mutable=m, references=refs)) + ". Quantity is signed-64, with historical 10 distinct from creation 0. Nullable limit defaults to 7 only when omitted at creation, historical null, explicit null clears, omitted mutation preserves. Actor is explicitly supplied operation-context identity in the declared operator collection; never authenticated implicitly or substituted from owner. Each successful write creates one history row, cardinality of entire pre-operation append-only history plus one. Adjust also creates a same-primary successor, field provenance exactly declared, in the same atomic commit. No calendar policy or recurrence is authorized."
        source += " Absolute Gregorian UTC-day transport explicitly denotes start-of-day at 00:00:00Z with second precision; it does not add calendar arithmetic. null-limits selects exactly records with limit null, returns whole records sorted ascending id, empty on no match, read-only with unchanged persistence."
        candidate = assemble("primary-" + domain.lower(), source, f, m, refs, dict(atomic_state_profile="atomic-durable-state-1", computation_profile="typed-computation-1", primary_interface_profile="primary-value-interfaces-1"))
        candidate["domains"]["collection_store"] = dict(kind="composed_scalar", state=base["state"][0]["id"])
        query = dict(source=dict(collection=base["state"][0]["id"], fields=ir["value_types"], unique_key="id"), parameters={}, predicate=dict(kind="is_null", result_type="boolean", operand=operand("field", nullable, name="limit")), comparison=dict(scope="predicate_nodes"), ordering=[dict(field="id", direction="ASC")], validation=[], inclusion=[], effect=dict(state="read_only", persistence="unchanged"), result=dict(shape="collection", cardinality="zero_or_more", no_match="empty"))
        for facet, value in query.items():
            candidate["rows"].append(dict(id=candidate["id"] + "/null-limits/" + facet, basis="STATED", derived_from=[], source_quote=source, statement="Explicit null numeric selection " + facet, relation=dict(kind="filter_order", parameters=dict(query="null-limits", facet=facet, value=copy.deepcopy(value)))))
        row = dict(id="a", nickname="a", description="old", state="active", created_at="2020-01-01T00:00:00Z", quantity=10, limit=None)
        result.append(dict(candidate=candidate, primary=domain, history=history, scalar=f, mutable=m, references=refs, record=row, path=f["storage"]["path"]))
    return result


def plan(r):
    path = r["path"]; row = r["record"]; primary = r["primary"]
    entities = {e["name"]: e["initial"] for e in r["references"]["entities"]}
    old = {n: v for n, v in row.items() if n not in ("quantity", "limit")}
    payload = dict(schema_version=1, records=[old], entities=entities)
    adjust = lambda value, rid="h", successor="b", actor="operator": ["adjust", "--id", "a", "--adjustment", str(value), "--record", rid, "--successor", successor, "--actor", actor]
    after = {**row, "quantity": 12}
    steps = [step(path, ["migrate"], {"migrated": 1}, preserve=False), step(path, ["list"], [row]), step(path, ["advance", "--id", "a"], error="actor_required"), step(path, adjust(2, actor="absent"), error="missing_target"), step(path, adjust("true"), error="invalid_value"), step(path, adjust(2**63), error="invalid_value"), step(path, adjust(2**63-1), error="computation_failed"), step(path, adjust(2), after, preserve=False), step(path, ["history"], [dict(id="h", subject="a", actor="operator", ordinal=1, quantity=12)]), step(path, adjust(1, "h2", "b"), error="successor_exists"), step(path, ["set-limit", "--id", "a", "--actor", "operator", "--limit", "4"], {**after, "limit": 4}, preserve=False), step(path, ["set-limit", "--id", "a", "--actor", "operator", "--limit", "null"], after, preserve=False), step(path, ["set-limit", "--id", "a", "--actor", "operator"], after), step(path, ["advance", "--id", "a", "--actor", "operator"], {**after, "state": "inactive"}, preserve=False), step(path, ["history"], contains=['"ordinal": 4', '"actor": "operator"']), step(path, ["create", "--nickname", "fresh", "--actor", "operator"], preserve=False, contains=['"quantity": 0', '"limit": 7']), step(path, ["create", "--nickname", "null", "--limit", "null", "--actor", "operator"], preserve=False, contains=['"limit": null']), step(path, ["create", "--nickname", "bad", "--limit", "1.0", "--actor", "operator"], error="invalid_number")]
    scheduled = {**row, "created_at": "2024-02-29T00:00:00Z"}
    day_args = lambda d: ["set-day", "--id", "a", "--day", d, "--actor", "operator", "--record", "day-history"]
    day_case = dict(id="utc-day-representation", initial_files=[dict(path=path, json=dict(schema_version=2, records=[row], entities=entities))], steps=[step(path, day_args("2023-02-29"), error="invalid_day"), step(path, day_args("2024-02-29T00:00:00Z"), error="invalid_day"), step(path, day_args("2024-02-29"), scheduled, preserve=False), step(path, ["list"], [scheduled])])
    day_case["steps"].append(step(path, ["null-limits"], [scheduled]))
    return external_plan(r["candidate"], path, [dict(id="primary-numeric-context-history-successor", initial_files=[dict(path=path, json=payload)], steps=steps), day_case])
