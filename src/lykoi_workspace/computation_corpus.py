"""Source-authorized numeric mutation, history and successor in five domains."""
import copy

from air_compiler.computation import INTEGER, TIME, DURATION, POLICY
from air_compiler.atomic_state import COMMIT
from air_compiler.references import identity
from .atomic_state_corpus import captures as substrate, binding
from .reference_corpus import assemble, operation, parameter, write, external_plan, step
from .predicate_corpus import operand, compare


def node(name, op, args, typ=INTEGER, deps=None):
    return dict(binding=name, operator=op, type=copy.deepcopy(typ), operands=args, depends_on=deps or [], error="computation_failed")


def graph(nodes): return dict(nodes=nodes, policy=copy.deepcopy(POLICY))


def count(entity, field_type):
    value = operand("field", field_type, name="selected.id")
    return dict(kind="cardinality", type=copy.deepcopy(INTEGER), selection=dict(entity=entity, binding="selected", predicate=compare(value, value)))


def captures():
    result = []
    for domain in ("Inventory", "Retry", "Session", "Subscription", "Ledger"):
        seed = substrate()[0]
        f, m = copy.deepcopy(seed["scalar"]), copy.deepcopy(seed["mutable"])
        f["storage"]["path"] = domain.lower() + "-numeric.json"
        metric, history = domain + "Value", domain + "History"
        mi, hi = identity(metric), identity(history)
        fields = dict(id=mi, quantity=INTEGER, due_at=TIME)
        params = dict(id=parameter(mi, "id"), adjustment=parameter(INTEGER, "adjustment", encoding="json"), seconds=parameter(DURATION, "seconds", encoding="json"), record=parameter(hi, "record"), successor=parameter(mi, "successor"))
        op = operation("compute", metric, "update", params, [write("quantity", operand("computed", INTEGER, name="new_quantity")), write("due_at", operand("computed", TIME, name="next_due"))], lookup="id", missing="missing_record")
        op["computations"] = graph([node("new_quantity", "add", [operand("before", INTEGER, name="quantity"), operand("parameter", INTEGER, name="adjustment")]), node("next_due", "shift_utc_seconds", [operand("before", TIME, name="due_at"), operand("parameter", DURATION, name="seconds")], TIME)])
        # Computed binding consumed by existing typed predicate, independently
        # of write-time type checks. Negative inventory adjustment is admitted.
        op["guards"] = [dict(predicate=compare(operand("computed", INTEGER, name="new_quantity"), operand("literal", INTEGER, value=-100), op="ge"), error="quantity_rejected")]
        create = operation("create-value", metric, "create", {"id": parameter(mi, "id")}, [write("id", operand("parameter", mi, name="id")), write("quantity", operand("literal", INTEGER, value=0)), write("due_at", operand("literal", TIME, value="2024-02-28T12:00:00Z"))], duplicate="value_exists")
        refs = dict(primary="Inventory", entities=[dict(name=metric, key="id", fields=fields, initial=[]), dict(name=history, key="id", fields=dict(id=hi, ordinal=INTEGER, quantity=INTEGER), initial=[])], references=[], operations=[create, op, operation("values", metric, "list", order=["id"])], guards=[], commit=dict(scope="one_store", mutation="one_record", isolation="exclusive_operation", rejection="unchanged"))
        ac = dict(command="compute", entity=metric, parameters={n: p["type"] for n, p in params.items()}, resources=[], on="success", sampling="once_per_operation", ordering="declared_creation_occurrence", computations=graph([node("size", "value", [count(history, hi)]), node("ordinal", "add", [operand("computed", INTEGER, name="size"), operand("literal", INTEGER, value=1)], deps=["size"])]), creations=[dict(entity=history, bindings=dict(id=binding(operand("parameter", hi, name="record")), ordinal=binding(operand("computed", INTEGER, name="ordinal")), quantity=binding(operand("after", INTEGER, name="quantity"))), duplicate_error="history_exists"), dict(entity=metric, bindings=dict(id=binding(operand("parameter", mi, name="successor")), quantity=binding(operand("after", INTEGER, name="quantity")), due_at=binding(operand("after", TIME, name="due_at"))), duplicate_error="successor_exists")])
        q = dict(id="history", source=dict(collection=history, fields=dict(id=dict(type="identifier", domain=[]), ordinal=INTEGER, quantity=INTEGER), unique_key="id"), parameters={}, predicate=compare(operand("field", INTEGER, name="ordinal"), operand("literal", INTEGER, value=0), op="ge"), comparison=dict(scope="predicate_nodes"), ordering=[dict(field="ordinal", direction="ASC"), dict(field="id", direction="ASC")], validation=[], inclusion=[], effect=dict(state="read_only", persistence="unchanged"), result=dict(shape="collection", cardinality="zero_or_more", no_match="empty"))
        atom = dict(operations=[ac], queries=[q], append_only=[history], commit=copy.deepcopy(COMMIT))
        m["atomic_state_semantics"] = atom
        source = ("Synthetic " + domain + ": complete normative typed authority " + repr(dict(scalar=f, mutable=m, references=refs)) + ". Signed 64-bit integers include negatives, JSON integral numbers only, overflow rejects unchanged. Compute reads the operation-before quantity and due timestamp, adds adjustment, and displaces due by declared fixed elapsed UTC seconds. No clock or calendar month arithmetic. History ordinal equals pre-operation entire history cardinality plus one. Append-only history has one row per successful operation, exclusively reserved one-store commit. Exactly one ordinary successor value record copies the computed quantity and due timestamp in that same commit. All typed declarations, dependencies, errors and source bindings are normative. Inventory quantity, Retry attempts, Session/Subscription expiry displacement and Ledger adjustment share this bounded policy; no general domain-authority claim.")
        candidate = assemble("computation-" + domain.lower(), source, f, m, refs, dict(atomic_state_profile="atomic-durable-state-1", computation_profile="typed-computation-1"))
        result.append(dict(candidate=candidate, scalar=f, mutable=m, references=refs, atomic=atom, metric=metric, history=history, path=f["storage"]["path"], domain=domain))
    return result


def plan(r):
    path = r["path"]
    initial = dict(schema_version=1, records=[], entities={r["metric"]: [], r["history"]: []})
    row = dict(id="a", quantity=0, due_at="2024-02-28T12:00:00Z")
    argv = lambda adjustment, seconds, rid, successor: ["compute", "--id", "a", "--adjustment", str(adjustment), "--seconds", str(seconds), "--record", rid, "--successor", successor]
    first = dict(id="a", quantity=3, due_at="2024-02-29T12:00:00Z")
    final = dict(id="a", quantity=2, due_at="2024-02-28T12:00:00Z")
    steps = [step(path, ["create-value", "--id", "a"], row, preserve=False), step(path, ["values"], [row]), step(path, argv(3, 86400, "h1", "b"), first, preserve=False), step(path, ["history"], [dict(id="h1", ordinal=1, quantity=3)]), step(path, ["values"], [first, {**first, "id": "b"}]), step(path, argv(1, 0, "h1", "c"), error="history_exists"), step(path, argv(1, 0, "h2", "b"), error="successor_exists"), step(path, argv(2**63-1, 0, "h2", "c"), error="computation_failed"), step(path, argv(-104, 0, "h2", "c"), error="quantity_rejected"), step(path, argv(0, 2**63-1, "h2", "c"), error="computation_failed"), step(path, argv("true", 0, "h2", "c"), error="invalid_value"), step(path, argv("1.0", 0, "h2", "c"), error="invalid_value"), step(path, argv(-1, -86400, "h2", "c"), final, preserve=False), step(path, ["history"], [dict(id="h1", ordinal=1, quantity=3), dict(id="h2", ordinal=2, quantity=2)]), step(path, ["values"], [final, {**first, "id": "b"}, {**final, "id": "c"}])]
    return external_plan(r["candidate"], path, [dict(id="numeric-temporal-history-successor-reload", initial_files=[dict(path=path, json=initial)], steps=steps)])
