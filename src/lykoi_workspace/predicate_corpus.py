"""Public multi-domain typed source captures and pre-author external plans."""
import copy
import hashlib

from lykoi_controller import canonical
from lykoi_pipeline import mutable_profile
from air_compiler.mutable_values import compose
from . import input_corpus as prior, mutable_corpus as old


def operand(kind, typ, name=None, value=None, stage=None):
    return dict(kind=kind, type=copy.deepcopy(typ), **({"value": value} if kind == "literal" else {"stage": stage} if kind == "value" else {"name": name}))


def compare(left, right, op="eq", case="sensitive", normalization="none", member=False):
    return dict(kind="member" if member else "compare", result_type="boolean", operator="in" if member else op, left=left, right=right, policy=dict(case=case, normalization=normalization), nulls="false")


def group(kind, *children):
    return dict(kind=kind, result_type="boolean", **({"child": children[0]} if kind == "not" else {"children": list(children)}))


def unary(kind, op):
    return dict(kind=kind, result_type="boolean", operand=op)


def captures():
    records = prior.captures()
    for r, domain in zip(records, ("products", "users", "sessions", "documents")):
        r["domain"] = domain
        f, m = r["scalar"], r["mutable"]
        f["fields"].append(dict(name="expires_at", type="timestamp", domain=[], nullable=True, preservation="verbatim"))
        f["creation"]["bindings"].append(dict(field="expires_at", source="input", value=None, default=dict(value=None, trigger="omitted", boundary="creation")))
        f["creation"]["validation"].append(dict(field="expires_at", rule="timestamp_utc", error="invalid_timestamp"))
        boolean = dict(type="boolean", domain=[], nullable=False)
        m["predicate_semantics"] = dict(booleans=[dict(name="enabled", creation=dict(source="literal", value=False), migration=[])], guards=[], invariants=[])
        change = old.change("enabled", steps=[], optional=False)
        change["invalid_error"] = "invalid_boolean"
        m["mutations"].append(old.mutation("set-enabled", [change]))
        # Compose without input declarations while constructing their exact source
        # declarations; the fixture is reviewed as literal typed source below.
        m.pop("input_contracts")
        base = mutable_profile.scalar.lower(f)
        ir = compose(base, m); types = ir["value_types"]
        m["input_contracts"] = prior.parameters(base, m)
        next(p for p in m["input_contracts"] if p["operation"] == "set-enabled" and p["parameter"] == "enabled")["binding"]["encoding"] = "json"
        def field(n): return operand("field", types[n], name=n)
        def literal(n, v): return operand("literal", types[n], value=v)
        eq_enabled = compare(field("enabled"), literal("enabled", False))
        eq_state = compare(field("state"), literal("state", "active"))
        m["predicate_semantics"]["guards"] = [dict(command="advance", predicate=group("and", eq_state, eq_enabled), error="guard_rejected", rejection="unchanged")]
        raw_type = types["description"]
        raw = operand("value", raw_type, stage="RAW")
        condition = group("and", unary("present", raw), group("not", compare(raw, operand("literal", raw_type, value=""))))
        next(op for op in m["mutations"] if op["command"] == "conditional-description")["changes"][0]["pipeline"][1]["when"] = condition
        # Also exercise common predicates on mutable-operation preconditions.
        next(op for op in m["mutations"] if op["command"] == "rename")["guards"] = [dict(predicate=eq_enabled, error="guard_rejected")]
        name_type = types["nickname"]
        owners = dict(type="collection", element={"type": "string", "domain": []}, ordering="insertion", duplicates="allow", equality="exact")
        category = compare(field("category"), literal("category", "public"))
        alpha = compare(field("nickname"), operand("literal", name_type, value="Alpha"))
        enabled = group("not", eq_enabled)
        expires = field("expires_at")
        bound_type = types["expires_at"]
        cutoff = operand("parameter", bound_type, name="cutoff")
        params = {"primary": name_type, "secondary": name_type}
        predicates = {
            "select-products": ({}, group("and", category, eq_enabled)),
            "select-users": (params, group("or", compare(field("nickname"), operand("parameter", name_type, name="primary")), compare(field("nickname"), operand("parameter", name_type, name="secondary")))),
            "select-sessions": ({"cutoff": bound_type}, group("and", group("not", unary("is_null", expires)), compare(expires, cutoff, "lt"))),
            "select-range": ({"lower": bound_type, "upper": bound_type}, group("and", compare(expires, operand("parameter", bound_type, name="lower"), "ge"), compare(expires, operand("parameter", bound_type, name="upper"), "le"))),
            "select-documents": ({"allowed": owners}, compare(field("nickname"), operand("parameter", owners, name="allowed"), member=True)),
            "select-members": ({"value": {"type": "string", "domain": []}}, group("and", compare(operand("parameter", {"type": "string", "domain": []}, name="value"), field(r["collection"]), member=True), eq_state)),
            "group-inner": ({}, group("and", category, group("or", alpha, enabled))),
            "group-outer": ({}, group("or", group("and", category, alpha), enabled)),
        }
        rows = []
        source = ("Public " + domain + " predicate composition source. Exact authorized policies follow: " + repr(dict(scalar=f, mutable=m, queries=predicates)) +
                  ". Queries return whole records, read-only, empty on no match, ascending id. Operators and parentheses are structural. Timestamp bounds are UTC instants, inclusive range and strict cutoff; atomic comparisons on null are false. Boolean enabled is literal false on creation, JSON replace on set-enabled. Guards reject guard_rejected before writing and preserve bytes. Conditional-description observes RAW presence AND NOT RAW equality to empty; validation still observes TRANSFORMED after trim. No integer arithmetic or entity relationships.")
        for profile, facts in (("existing-scalar-1", f), (mutable_profile.PROFILE, m)):
            for facet, value in facts.items():
                rows.append(dict(id=domain + "/" + facet, basis="STATED", derived_from=[], source_quote=source, statement="Authorized " + facet, relation=dict(kind="crud", parameters=dict(profile=profile, facet=facet, value=copy.deepcopy(value)))))
        for command, (parameters, tree) in predicates.items():
            query = dict(source=dict(collection="state", fields=types, unique_key="id"), parameters=parameters, predicate=tree, comparison=dict(scope="predicate_nodes"), ordering=[dict(field="id", direction="ASC")], validation=[], inclusion=[], effect=dict(state="read_only", persistence="unchanged"), result=dict(shape="collection", cardinality="zero_or_more", no_match="empty"))
            for facet, value in query.items():
                rows.append(dict(id=domain + "/" + command + "/" + facet, basis="STATED", derived_from=[], source_quote=source, statement="Authorized " + command + " " + facet, relation=dict(kind="filter_order", parameters=dict(query=command, facet=facet, value=copy.deepcopy(value)))))
        r["candidate"].update(id="predicate-" + domain, source=source, rows=rows)
        r["candidate"]["domains"]["predicate_profile"] = "typed-predicates-1"
    return records


def plan(r):
    path, collection = r["path"], r["collection"]
    rows = [dict(id=i, nickname=n, description="preserved", state="active", category=c, created_at="2020-01-01T00:00:00Z", expires_at=e, enabled=b, **{collection: []}) for i, n, c, e, b in [("a", "Alpha", "public", None, False), ("b", "Beta", "public", "2024-01-01T00:00:00Z", True), ("c", "Gamma", "private", "2024-02-01T00:00:00Z", True)]]
    a, b, c = copy.deepcopy(rows)
    steps = []
    def step(argv, expected=None, error=None, preserve=True, contains=None):
        s = dict(argv=argv, returncode=1 if error else 0, contains=contains or [])
        if preserve: s["preserved"] = [path]
        if error: s.update(stdout_exact="", stderr_json={"error": error})
        else:
            s["stderr_exact"] = ""
            if expected is not None: s["stdout_json"] = copy.deepcopy(expected)
        steps.append(s)
    step(["select-products"], [a])
    step(["select-users", "--primary", "Alpha", "--secondary", "Gamma"], [a, c])
    step(["select-users", "--primary", "alpha", "--secondary", "absent"], [])
    step(["select-sessions", "--cutoff", "2024-02-01T00:00:00Z"], [b])
    step(["select-range", "--lower", "2024-01-01T00:00:00Z", "--upper", "2024-02-01T00:00:00Z"], [b, c])
    step(["select-range", "--lower", "2024-01-01T00:00:00.001Z", "--upper", "2024-02-01T00:00:00Z"], [c])
    step(["select-documents", "--allowed", '["Gamma","Alpha"]'], [a, c])
    step(["select-documents", "--allowed", '[]'], [])
    step(["select-documents", "--allowed", '[true]'], error="invalid_input")
    step(["group-inner"], [a, b]); step(["group-outer"], [a, b, c])
    step(["advance", "--id", "b"], error="guard_rejected")
    step(["rename", "--id", "b", "--nickname", "trimmed"], error="guard_rejected")
    step(["set-enabled", "--id", "a", "--enabled", '"false"'], error="invalid_boolean")
    a["enabled"] = True; step(["set-enabled", "--id", "a", "--enabled", "true"], a, preserve=False)
    step(["select-products"], [])
    step(["advance", "--id", "a"], error="guard_rejected")
    a["enabled"] = False; step(["set-enabled", "--id", "a", "--enabled", "false"], a, preserve=False)
    step(["conditional-description", "--id", "a"], a)
    a["description"] = ""; step(["conditional-description", "--id", "a", "--description", ""], a, preserve=False)
    step(["conditional-description", "--id", "a", "--description", "   "], error="empty_value")
    a["description"] = "Text"; step(["conditional-description", "--id", "a", "--description", " Text "], a, preserve=False)
    a["state"] = "inactive"; step(["advance", "--id", "a"], a, preserve=False)
    step(["advance", "--id", "a"], error="guard_rejected")
    step(["list"], [a, b, c])
    mutation = next(m for m in r["mutable"]["mutations"] if m["command"] == "write-values")["changes"][0]
    raw = " Seed " if mutation["operation"] == "add_unique" else "Seed" if mutation["operation"] == "append" else '["Seed","A","Seed"]'
    a[collection] = ["Seed"] if mutation["operation"] != "replace" else ["Seed", "A", "Seed"]
    if any(s.get("operation") == "stable_deduplicate" for s in mutation["pipeline"]):
        a[collection] = ["Seed", "A"]
    step(["write-values", "--id", "a", "--" + collection, raw], a, preserve=False)
    step(["select-members", "--value", "Seed"], [])  # inactive state excluded
    step(["rename", "--id", "a", "--nickname", " Trimmed "], {**a, "nickname": "Trimmed"}, preserve=False)
    a["nickname"] = "Trimmed"
    step(["select-users", "--primary", "Trimmed", "--secondary", "absent"], [a])
    ids = [o["id"] for o in r["candidate"]["rows"]]
    case = dict(id="composition", obligations=ids, initial_state="fresh_directory", initial_files=[dict(path=path, json=rows)], steps=steps, invariants=["Read-only and rejected guards preserve bytes"], transitions="Separate subprocess reload", rejections="Typed values and explicit guard errors")
    case["identity"] = hashlib.sha256(canonical(case)).hexdigest()
    supplied = ["--aliases", "[]"] if collection == "aliases" else []
    create = dict(id="creation-reload", obligations=ids, initial_state="fresh_directory", initial_files=[], steps=[dict(argv=["create", "--nickname", "Fresh", *supplied], returncode=0, contains=['"enabled": false', '"expires_at": null'], stderr_exact=""), dict(argv=["list"], returncode=0, contains=['"enabled": false', '"expires_at": null'], stderr_exact="", preserved=[path])], invariants=["Boolean creation and persistence"], transitions="Reload", rejections="None")
    create["identity"] = hashlib.sha256(canonical(create)).hexdigest()
    cases = [case, create]
    return dict(version="external-cli-plan-1", outcome="READY", producer="R5.106 public typed source literal oracle", source_sha256=hashlib.sha256(r["candidate"]["source"].encode()).hexdigest(), cases=cases, coverage=[dict(obligation=i, classification="EXERCISED", justification="Source-defined predicate, guard, input-stage and persistence observations", cases=[c["identity"] for c in cases]) for i in ids], limitations=["Same-agent captures/inventory/oracle; synthetic approval; not independent cognition"])
