"""Source-first synthetic multi-domain captures and independent literal oracles.

These are same-agent captured interpretations, not a natural-language parser.
No benchmark sources, IDs, captures or acceptance suites are used.
"""
import copy
import hashlib

from lykoi_controller import canonical
from lykoi_pipeline.mutable_profile import PROFILE
from .query_corpus import response

TRIM = dict(kind="transform", operation="trim")
DEDUP = dict(kind="transform", operation="stable_deduplicate")
NONEMPTY = dict(kind="validate", rule="nonempty", error="empty_value")


def change(field, operation="replace", steps=None, optional=False):
    return dict(field=field, input=field, operation=operation, omitted="unchanged" if optional else "reject", missing_error=None if optional else "missing_value", pipeline=copy.deepcopy(steps or []), invalid_error="invalid_value")


def mutation(command, changes):
    return dict(command=command, lookup="id", missing_error="record_not_found", changes=changes, guards=[], effect=dict(atomicity="single_record", persistence="atomic", rejection="unchanged"))


def capture(domain, duplicates, operation, steps):
    collection = {"article": "labels", "contact": "aliases", "product": "keywords", "profile": "interests"}[domain]
    path = domain + ".json"
    source = (f"Store {domain} records in {path}, schema 1, missing file is empty. Every write is atomic; rejection leaves bytes and records unchanged. "
        "create allocates a declared UUID-v4 id and UTC created_at, preserves supplied nickname and description verbatim, initializes state active. "
        "description omitted on creation defaults to empty string. nickname is required and must be nonblank or empty_value. "
        "list returns whole records by created_at then id ascending. advance changes active to inactive; missing id is record_not_found and repeat is invalid_state_transition, with unchanged state. "
        f"Declare {collection} as an ordered string collection, insertion order, exact case-sensitive equality and duplicates {duplicates}. "
        f"On creation {collection} defaults to empty only when omitted; supplied collections use the explicit pipeline below. No historical migration exists for schema 1. "
        f"write-values performs {operation} on {collection} using " + repr(steps) + ". Required mutation input omitted is missing_value; wrong typed values are invalid_value. "
        "rename trims nickname then rejects empty with empty_value; rename-raw rejects empty raw nickname then trims, so raw whitespace may persist as empty. "
        "update-description preserves supplied description verbatim, including empty string; omitted leaves it unchanged. "
        "update-profile simultaneously trims then validates nickname and replaces description verbatim if supplied; missing nickname is missing_value. "
        "All mutations look up immutable id first (record_not_found), preserve independent lifecycle and unrelated fields, validate the final type and atomically persist the entire record. "
        f"find-value --value selects exact membership in {collection}, sensitive case and no normalization or parameter validation, include active and inactive, whole records ordered by created_at then id, empty on no match, read only.")
    fields = [dict(name=n, type=t, domain=dom, nullable=False, preservation="verbatim") for n, t, dom in [
        ("id", "identifier", []), ("created_at", "timestamp", []), ("nickname", "string", []), ("description", "string", []), ("state", "enum", ["active", "inactive"])]]
    scalar = dict(storage=dict(path=path, version=1, missing="empty_collection", write="atomic", rejection="unchanged"), fields=fields,
        creation=dict(command="create", bindings=[dict(field=n, source=s, value=v, default=default) for n, s, v, default in [
            ("id", "uuid_v4", None, None), ("created_at", "utc_clock", None, None), ("nickname", "input", None, None),
            ("description", "input", None, dict(value="", trigger="omitted", boundary="creation")), ("state", "literal", "active", None)]],
            validation=[dict(field="nickname", rule="nonblank", error="empty_value")]),
        listing=dict(command="list", order=["created_at", "id"], result="whole_records"),
        lifecycle=[dict(field="state", initial="active", source="active", target="inactive", command="advance", missing_error="record_not_found", transition_error="invalid_state_transition", rejection="unchanged")], evolution=[])
    mutable = dict(collections=[dict(name=collection, element=dict(type="string", domain=[]), ordering="insertion", duplicates=duplicates, equality="exact",
        creation=dict(input=collection, encoding="json", default=[], pipeline=[DEDUP] if duplicates == "unique" else [], error="invalid_value"), migration=[])],
        mutations=[mutation("write-values", [change(collection, operation, steps)]), mutation("rename", [change("nickname", steps=[TRIM, NONEMPTY])]),
            mutation("rename-raw", [change("nickname", steps=[NONEMPTY, TRIM])]), mutation("update-description", [change("description", optional=True)]),
            mutation("update-profile", [change("nickname", steps=[TRIM, NONEMPTY]), change("description", optional=True)])], creation_pipelines=[])
    if domain == "article":
        source += " Creation accepts repeated --label values; trim and reject empty with empty_value per element, then stable deduplication preserving first occurrence and relative order."
        mutable["collections"][0]["creation"].update(input="label", encoding="repeated", pipeline=[dict(kind="map_elements", pipeline=[TRIM, NONEMPTY]), DEDUP])
    rows = []
    for profile, values in (("existing-scalar-1", scalar), (PROFILE, mutable)):
        for facet, value in values.items():
            rows.append(dict(id=domain + "/" + facet, basis="STATED", derived_from=[], source_quote=source, statement="Explicit " + facet + " for " + domain, relation=dict(kind="crud", parameters=dict(profile=profile, facet=facet, value=copy.deepcopy(value)))))
    query = dict(id=domain + "-membership", source=source, operation="find-value", facts=dict(
        source=dict(collection="state", fields={"id": "string", "created_at": "string", collection: "strings", "state": "string"}, unique_key="id"),
        parameters={"value": "string"}, predicate=dict(field=collection, operator="contains", operand={"parameter": "value"}),
        comparison=dict(case="sensitive", normalization="none"), ordering=[dict(field="created_at", direction="ASC"), dict(field="id", direction="ASC")],
        validation=[], inclusion=[dict(field="state", mode="all")], effect=dict(state="read_only", persistence="unchanged"), result=dict(shape="collection", cardinality="zero_or_more", no_match="empty")))
    rows += response(query, {"text": source}, [])["obligations"]
    candidate = dict(id="synthetic-" + domain, source=source, rows=rows, question=None, domains=dict(capability_profile=PROFILE, collection_store=dict(kind="composed_scalar", state="state")))
    return dict(domain=domain, path=path, collection=collection, scalar=scalar, mutable=mutable, candidate=candidate)


def captures():
    return [capture("article", "unique", "add_unique", [TRIM, NONEMPTY]), capture("contact", "allow", "append", []),
            capture("product", "unique", "replace", [DEDUP]), capture("profile", "allow", "replace", [])]


def plan(record):
    """Literal WHAT-side expected records, prepared before implementation authoring."""
    domain, path, field = record["domain"], record["path"], record["collection"]
    candidate = record["candidate"]
    base = dict(id="known", created_at="2020-01-01T00:00:00Z", nickname="Old", description="Original", state="active", **{field: []})
    state = copy.deepcopy(base); steps = []
    def step(argv, expected=None, error=None, preserved=False):
        item = dict(argv=argv, returncode=1 if error else 0, contains=[], stderr_json={"error": error} if error else None)
        if error:
            item["stdout_exact"] = ""
        else:
            item.pop("stderr_json"); item["stderr_exact"] = ""; item["stdout_json"] = copy.deepcopy(expected)
        if preserved:
            item["preserved"] = [path]
        steps.append(item)
    if domain in ("article", "contact"):
        for value, stored in [(" Z " if domain == "article" else "Z", "Z"), ("A", "A"), ("Z", "Z"), ("z", "z")]:
            if domain == "contact" or stored not in state[field]:
                state[field].append(stored)
            step(["write-values", "--id", "known", "--" + field, value], state)
    else:
        state[field] = ["Z", "A", "z"] if domain == "product" else ["Z", "A", "Z", "z"]
        step(["write-values", "--id", "known", "--" + field, '["Z","A","Z","z"]'], state)
    step(["list"], [state], preserved=True)
    step(["find-value", "--value", "Z"], [state], preserved=True)
    step(["find-value", "--value", " Z "], [], preserved=True)
    step(["find-value", "--value", "missing"], [], preserved=True)
    step(["update-description", "--id", "known"], state)
    state["description"] = ""; step(["update-description", "--id", "known", "--description", ""], state)
    state["description"] = "  verbatim  "; step(["update-description", "--id", "known", "--description", "  verbatim  "], state)
    state["nickname"] = "New"; step(["rename", "--id", "known", "--nickname", " New "], state)
    step(["rename", "--id", "known", "--nickname", "   "], error="empty_value", preserved=True)
    step(["rename", "--id", "known"], error="missing_value", preserved=True)
    step(["rename", "--id", "absent", "--nickname", "X"], error="record_not_found", preserved=True)
    step(["update-profile", "--id", "known", "--nickname", " ", "--description", "changed"], error="empty_value", preserved=True)
    state.update(nickname="Both", description="Together"); step(["update-profile", "--id", "known", "--nickname", " Both ", "--description", "Together"], state)
    state["nickname"] = ""; step(["rename-raw", "--id", "known", "--nickname", " "], state)
    step(["rename-raw", "--id", "known", "--nickname", ""], error="empty_value", preserved=True)
    state["state"] = "inactive"; step(["advance", "--id", "known"], state)
    state["nickname"] = "After"; step(["rename", "--id", "known", "--nickname", " After "], state)
    step(["find-value", "--value", "Z"], [state], preserved=True)
    step(["list"], [state], preserved=True)
    ids = [o["id"] for o in candidate["rows"]]
    case = dict(id=domain + "-behavior", obligations=ids, initial_state="fresh_directory", initial_files=[dict(path=path, json=[base])], steps=steps,
        invariants=["Atomic rejection and unrelated lifecycle preservation"], transitions="Ordered independent external processes reload the same store", rejections="Exact source-declared errors")
    case["identity"] = hashlib.sha256(canonical(case)).hexdigest()
    # Creation/default resources execute separately without guessing allocated IDs.
    create = dict(id=domain + "-creation", obligations=ids, initial_state="fresh_directory", steps=[
        dict(argv=["create", "--nickname", "Created"], returncode=0, contains=['"nickname": "Created"', '"' + field + '": []']),
        dict(argv=["list"], returncode=0, contains=['"nickname": "Created"', '"' + field + '": []'], preserved=[path])], invariants=["Creation defaults and persistence"], transitions="Create then reload", rejections="None")
    create["identity"] = hashlib.sha256(canonical(create)).hexdigest()
    if domain == "article":
        create["steps"] += [dict(argv=["create", "--nickname", "Repeated", "--label", " B ", "--label", "A", "--label", "B", "--label", "b"], returncode=0, contains=['"labels": ["B", "A", "b"]']),
            dict(argv=["create", "--nickname", "Rejected", "--label", " "], returncode=1, contains=[], stdout_exact="", stderr_json={"error": "empty_value"}, preserved=[path])]
        create.pop("identity"); create["identity"] = hashlib.sha256(canonical(create)).hexdigest()
    return dict(version="external-cli-plan-1", outcome="READY", producer="SOURCE_FIRST_LITERAL_ORACLE_SAME_AGENT", source_sha256=hashlib.sha256(candidate["source"].encode()).hexdigest(), cases=[case, create], coverage=[dict(obligation=oid, classification="EXERCISED", justification="Source-first literal multi-domain behavior", cases=[case["identity"], create["identity"]]) for oid in ids], limitations=["Same-agent source extraction and oracle; synthetic owner authority"])
