"""Public source captures for bounded interface closure, across unrelated domains."""
import copy
import hashlib

from lykoi_controller import canonical
from air_compiler.mutable_values import compose
from air_compiler.query_interfaces import listing
from lykoi_pipeline import mutable_profile
from . import predicate_corpus as prior
from .input_corpus import parameters
from .mutable_corpus import mutation
from .predicate_corpus import operand, compare, group


def literal_change(field, typ, value):
    return dict(field=field, source=dict(kind="literal", type=copy.deepcopy(typ), value=value), operation="replace", pipeline=[], invalid_error="invalid_value")


def amend(base, predicate, composition="and"):
    q = copy.deepcopy(base)
    q["predicate"] = predicate if composition == "replace" else group(composition, base["predicate"], predicate)
    q["amendment"] = dict(base=copy.deepcopy(base), composition=composition, predicate=copy.deepcopy(predicate))
    return q


def captures():
    records = prior.captures()
    for r, domain in zip(records, ("accounts", "products", "documents", "sessions")):
        r["domain"] = domain
        f, m = r["scalar"], r["mutable"]
        m.pop("input_contracts")
        base = mutable_profile.scalar.lower(f)
        types = compose(base, m)["value_types"]
        def field(n): return operand("field", types[n], name=n)
        def literal(n, v): return operand("literal", types[n], value=v)
        disabled = compare(field("enabled"), literal("enabled", False))
        m["mutations"].append(mutation("deactivate", [literal_change("enabled", types["enabled"], False)]))
        m["mutations"].append(mutation("literal-profile", [literal_change("nickname", types["nickname"], "Closed"), literal_change("category", types["category"], "private"), literal_change("expires_at", types["expires_at"], "2000-01-01T00:00:00Z"), literal_change(r["collection"], types[r["collection"]], ["Saved"])]))
        m["input_contracts"] = parameters(base, m)
        queries = {}
        for row in r["candidate"]["rows"]:
            p = row["relation"]["parameters"]
            if row["relation"]["kind"] == "filter_order":
                queries.setdefault(p["query"], dict(id=p["query"]))[p["facet"]] = copy.deepcopy(p["value"])
        queries["list"] = amend(listing(base, types, "list"), disabled)
        # A source-declared existing clock listing also receives selection only.
        # Add through the existing scalar facet before recomposing its base.
        f["clock_queries"] = [dict(command="past-sessions", predicates=[dict(kind="field_before_clock", field="expires_at", clock="utc_clock")], order=["created_at", "id"], result="whole_records", effect="read_only")]
        base = mutable_profile.scalar.integrate_facets(mutable_profile.scalar.lower({k: v for k, v in f.items() if k != "clock_queries"}), f)
        m.pop("input_contracts")
        m["input_contracts"] = parameters(base, m)
        queries["past-sessions"] = amend(listing(base, types, "past-sessions"), disabled)
        queries["select-products"] = amend(queries["select-products"], compare(field("category"), literal("category", "public")))
        queries["select-members"] = amend(queries["select-members"], disabled)
        owner = operand("parameter", types["nickname"], name="owner")
        nonempty = group("not", compare(owner, literal("nickname", "")))
        capability = next(c["id"] for c in base["capabilities"] if c["kind"] == "utc_clock")
        clock_type = dict(type="timestamp", domain=[], nullable=False)
        clock = operand("resource", clock_type, name="declared_now")
        resource = dict(name="declared_now", type=clock_type, capability=capability, sampling="once_per_query")
        q = copy.deepcopy(queries["select-sessions"])
        q.update(id="expired", parameters={}, predicate=compare(field("expires_at"), clock, "lt"), resources=[resource])
        queries["expired"] = q
        q = copy.deepcopy(q)
        q.update(id="owner-expired", parameters={"owner": types["nickname"]},
            predicate=group("and", compare(field("nickname"), owner), compare(field("expires_at"), clock, "lt")),
            preconditions=[dict(predicate=nonempty, error="invalid_owner", stage="before_selection", rejection="unchanged")],
            parameter_errors={"owner": dict(missing="missing_owner", invalid="invalid_owner_type")},
            validation=[dict(parameter="owner", rule="nonblank", error="blank_owner")],
            ordering=[dict(field="created_at", direction="DESC"), dict(field="id", direction="ASC")])
        queries["owner-expired"] = q
        q = copy.deepcopy(q); q.update(id="owner-required", validation=[])
        queries["owner-required"] = q
        q = copy.deepcopy(q); q.update(id="owner-cli", parameter_errors={"owner": dict(missing={"kind": "cli_rejection"}, invalid="invalid_owner_type")})
        queries["owner-cli"] = q
        queries = {k: v for k, v in queries.items() if k in ("list", "past-sessions", "select-products", "select-members", "expired", "owner-expired", "owner-required", "owner-cli")}
        source = ("Public " + domain + " interface closure. Exact source-authorized contracts: " + repr(dict(scalar=f, mutable=m, queries=queries)) +
            ". Literal mutations write exact values without inputs or default triggers. Existing list and membership queries gain explicitly conjoined selection only; all other query behavior is preserved. Parameter missing/type validation precedes nonblank validation, then query preconditions, then selection; errors reject without storage writes. Queries use the declared UTC capability, sampled once per query, injectable by the existing host provider mechanism. No ambient clock operand or arithmetic. Owner precondition rejects empty owner; no matches is an empty collection.")
        rows = []
        for profile, facts in (("existing-scalar-1", f), (mutable_profile.PROFILE, m)):
            for facet, value in facts.items():
                rows.append(dict(id=domain + "/" + facet, basis="STATED", derived_from=[], source_quote=source, statement="Authorized " + facet, relation=dict(kind="crud", parameters=dict(profile=profile, facet=facet, value=copy.deepcopy(value)))))
        for command, query in queries.items():
            for facet, value in query.items():
                if facet == "id": continue
                rows.append(dict(id=domain + "/" + command + "/" + facet, basis="STATED", derived_from=[], source_quote=source, statement="Authorized " + command + " " + facet, relation=dict(kind="filter_order", parameters=dict(query=command, facet=facet, value=copy.deepcopy(value)))))
        r["queries"] = queries
        r["candidate"].update(id="interfaces-" + domain, source=source, rows=rows)
        r["candidate"]["domains"]["predicate_value_interface_profile"] = "predicate-value-interfaces-1"
    return records


def plan(r):
    path, collection = r["path"], r["collection"]
    rows = [dict(id=i, nickname=n, description="preserved", state="active", category="public", created_at=t, expires_at=e, enabled=b, **{collection: ["Saved"]}) for i, n, t, e, b in [("a", "Alpha", "2020-01-01T00:00:00Z", None, True), ("b", "Beta", "2021-01-01T00:00:00Z", "2000-01-01T00:00:00Z", False), ("c", "Beta", "2022-01-01T00:00:00Z", "2999-01-01T00:00:00Z", False)]]
    a, b, c = copy.deepcopy(rows)
    steps = []
    def step(argv, expected=None, error=None, preserve=True):
        s = dict(argv=argv, returncode=1 if error else 0, contains=[])
        if preserve: s["preserved"] = [path]
        if error: s.update(stdout_exact="", stderr_json={"error": error})
        else: s.update(stdout_json=copy.deepcopy(expected), stderr_exact="")
        steps.append(s)
    step(["list"], [b, c])
    step(["select-members", "--value", "Saved"], [b, c])
    step(["select-products"], [b, c])
    step(["owner-expired"], error="missing_owner")
    step(["owner-required", "--owner", ""], error="invalid_owner")
    steps.append(dict(argv=["owner-cli"], returncode=2, contains=[], stdout_exact="", preserved=[path]))
    step(["owner-cli", "--owner", "Beta"], [b])
    step(["owner-expired", "--owner", ""], error="blank_owner")
    step(["owner-expired", "--owner", "   "], error="blank_owner")
    step(["owner-expired", "--owner", "Absent"], [])
    step(["owner-expired", "--owner", "Beta"], [b])
    step(["expired"], [b])
    step(["past-sessions"], [b])
    a["enabled"] = False; step(["deactivate", "--id", "a"], a, preserve=False)
    step(["list"], [a, b, c])
    a["state"] = "inactive"; step(["advance", "--id", "a"], a, preserve=False)
    step(["select-members", "--value", "Saved"], [b, c])
    a.update(nickname="Closed", category="private", expires_at="2000-01-01T00:00:00Z")
    step(["literal-profile", "--id", "a"], a, preserve=False)
    step(["owner-expired", "--owner", "Closed"], [a])
    step(["select-products"], [b, c])
    step(["deactivate", "--id", "absent"], error="record_not_found")
    ids = [o["id"] for o in r["candidate"]["rows"]]
    case = dict(id="interfaces", obligations=ids, initial_state="fresh_directory", initial_files=[dict(path=path, json=rows)], steps=steps, invariants=["Preserved unrelated fields, query order and rejection bytes"], transitions="Separate process reload", rejections="Declared errors before selection")
    case["identity"] = hashlib.sha256(canonical(case)).hexdigest()
    return dict(version="external-cli-plan-1", outcome="READY", producer="R5.107 literal external oracle", source_sha256=hashlib.sha256(r["candidate"]["source"].encode()).hexdigest(), cases=[case], coverage=[dict(obligation=i, classification="EXERCISED", justification="Source-defined composition observations; supplemental injected-clock subprocess tests", cases=[case["identity"]]) for i in ids], limitations=["Same-agent capture/inventory/oracle and synthetic approval; CLI default clock is supplemented by controlled provider subprocess verification"])
