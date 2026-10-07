"""Public source-first input/value closure captures; same-agent synthetic evidence."""
import copy
import hashlib

from lykoi_controller import canonical
from lykoi_pipeline import mutable_profile
from air_compiler.mutable_values import compose
from . import mutable_corpus as old


def staged(rule="nonempty", stage="RAW", predicate="present", error="empty_value"):
    return dict(kind="validate", rule=rule, error=error, stage=stage,
                when=None if predicate is None else dict(stage="RAW", predicate=predicate))


def explicit(steps):
    transformed = False
    for step in steps:
        if step["kind"] == "transform":
            transformed = True
        elif step["kind"] == "map_elements":
            explicit(step["pipeline"]); transformed = True
        else:
            step.update(stage="TRANSFORMED" if transformed else "RAW", when=dict(stage="RAW", predicate="present"))


def parameters(base, mutable):
    """Fixture construction only: serialize explicit declarations for source review."""
    ir = compose(base, mutable)
    model, types = ir["model"], ir["value_types"]
    create = next(b for b in model["behaviors"] if b["kind"] == "create")
    command = next(c["token"] for c in model["commands"] if c.get("behavior") == create["id"])
    fields = {f["id"]: f["name"] for t in model["types"] if t["kind"] == "record" for f in t["fields"]}
    result = []
    def add(op, n, typ, required, encoding, error):
        result.append(dict(operation=op, parameter=n, type=copy.deepcopy(typ), presence="required" if required else "optional",
            binding=dict(source="cli_flag", flag="--" + n.replace("_", "-"), encoding=encoding),
            missing=dict(kind="application_error", error=error) if required else None))
    for i in create["inputs"]:
        context = next((p for p in mutable.get("primary_interfaces", {}).get("context_inputs", []) if p["command"] == command and p["name"] == i["name"]), None)
        if context:
            continue
        a = next(a for a in create["assignments"] if a.get("id") == i["id"])
        encoding = "json" if types[fields[a["field"]]]["type"] == "integer" else next((c["creation"]["encoding"] for c in mutable["collections"] if c["creation"].get("input") == i["name"]), "text")
        add(command, i["name"], types[fields[a["field"]]], a["source"] == "input", encoding, "missing_" + i["name"])
    for m in mutable["mutations"]:
        add(m["command"], m["lookup"], types[m["lookup"]], True, "text", "missing_identity")
        for w in m["changes"]:
            if "source" in w:
                continue
            typ = types[w["field"]] if w["operation"] == "replace" else types[w["field"]]["element"]
            add(m["command"], w["input"], typ, w["omitted"] == "reject", "json" if typ["type"] in ("collection", "boolean", "integer") else "text", w["missing_error"])
    from air_compiler.references import erase
    for p in mutable.get("primary_interfaces", {}).get("context_inputs", []):
        add(p["command"], p["name"], erase(p["type"]), True, "text", p["missing_error"])
        behavior = next((b for b in model["behaviors"] if any(c.get("behavior") == b["id"] and c["token"] == p["command"] for c in model["commands"])), None)
        if behavior and behavior["kind"] != "create":
            for i in behavior["inputs"]:
                if i["name"] != p["name"]:
                    add(p["command"], i["name"], types[i["name"]], True, "text", "missing_identity")
    return result


def captures():
    records = old.captures()
    for r in records:
        domain, field, f, m = r["domain"], r["collection"], r["scalar"], r["mutable"]
        # Existing scalar enum literal is intentionally not a creation default.
        f["fields"].append(dict(name="category", type="enum", domain=["public", "private"], nullable=False, preservation="verbatim"))
        f["creation"]["bindings"].append(dict(field="category", source="literal", value="public", default=None))
        if domain == "contact":
            m["collections"][0]["creation"] = dict(source="input", input="aliases", encoding="json", pipeline=[], error="invalid_value")
        else:
            m["collections"][0]["creation"] = dict(source="literal", value=["Seed", "A", "Seed"] if domain == "product" else [])
            if domain == "product":
                m["collections"][0]["duplicates"] = "allow"
        for mutation in m["mutations"]:
            for w in mutation["changes"]:
                explicit(w["pipeline"])
        # Optional raw-empty acceptance differs from whitespace after trim.
        m["mutations"].append(old.mutation("conditional-description", [old.change("description", optional=True,
            steps=[old.TRIM, staged(stage="TRANSFORMED", predicate="nonempty"), staged(rule="typed", stage="PERSISTED", predicate=None)])]))
        m["mutations"].append(old.mutation("optional-nickname", [old.change("nickname", optional=True,
            steps=[staged(stage="RAW"), old.TRIM])]))
        base = mutable_profile.scalar.lower(f)
        m["input_contracts"] = parameters(base, m)
        if domain == "contact":
            next(p for p in m["input_contracts"] if p["operation"] == "create" and p["parameter"] == "aliases")["binding"]["flag"] = "--alias-data"
        source = (f"Input closure for {domain} in {r['path']}, schema 1. Atomic writes and rejection preserve all prior bytes. "
            "UUID-v4 and UTC-clock allocate identity and creation time. nickname is required, verbatim on creation and nonblank (empty_value); "
            "description input is verbatim and defaults to empty only on omission. category is the literal enum public, never an input/default. "
            "state is initially active and advance changes it to inactive; absent id is record_not_found and repeated advance is invalid_state_transition. "
            "list is whole records ordered created_at then id. find-value tests exact case-sensitive membership, no normalization, includes both lifecycle states, read only. "
            f"The collection {field} has insertion order, exact equality, duplicate policy {m['collections'][0]['duplicates']}. "
            + ("Creation requires supplied JSON aliases through --alias-data; missing is missing_aliases. " if domain == "contact" else
               f"Creation initializes literal {m['collections'][0]['creation']['value']!r}, with no collection creation input or default. ")
            + "write-values uses the declared append/add-unique/replace and pipeline; required value missing is missing_value. "
            "rename trims then validates TRANSFORMED nonempty; rename-raw validates RAW nonempty then trims, accepting raw whitespace. "
            "update-description replaces verbatim if present; update-profile atomically trims/validates nickname and replaces optional description. "
            "conditional-description skips omission, trims supplied input, validates transformed nonempty only if RAW nonempty, then checks PERSISTED candidate type. "
            "optional-nickname skips omission, rejects supplied RAW empty, and trims whitespace to empty. "
            "External required parameters use declared application errors independent of parser defaults; missing identity is missing_identity, missing nickname on create is missing_nickname. "
            "No historical migration. The following exact typed policies are explicitly authorized: " + repr(dict(scalar=f, mutable=m)))
        rows = []
        for profile, values in (("existing-scalar-1", f), (mutable_profile.PROFILE, m)):
            for facet, value in values.items():
                rows.append(dict(id=domain + "/" + facet, basis="STATED", derived_from=[], source_quote=source, statement="Authorized " + facet,
                    relation=dict(kind="crud", parameters=dict(profile=profile, facet=facet, value=copy.deepcopy(value)))))
        query_rows = [o for o in r["candidate"]["rows"] if o["relation"]["kind"] == "filter_order"]
        for o in query_rows:
            o["source_quote"] = source
        rows += query_rows
        r["candidate"].update(id="input-" + domain, source=source, rows=rows)
        r["candidate"]["domains"]["input_value_profile"] = "typed-input-values-1"
    return records


def plan(r):
    domain, path, field = r["domain"], r["path"], r["collection"]
    p = old.plan(r)
    behavior = p["cases"][0]
    behavior["initial_files"][0]["json"][0]["category"] = "public"
    for s in behavior["steps"]:
        expected = s.get("stdout_json")
        for row in (expected if type(expected) is list else [expected]):
            if type(row) is dict and "id" in row:
                row["category"] = "public"
    last = copy.deepcopy(behavior["steps"][-1]["stdout_json"][0])
    def add(argv, value=None, error=None):
        step = dict(argv=argv, returncode=1 if error else 0, contains=[])
        if error:
            step.update(stdout_exact="", stderr_json={"error": error}, preserved=[path])
        else:
            step.update(stdout_json=copy.deepcopy(value), stderr_exact="")
        behavior["steps"].append(step)
    add(["optional-nickname", "--id", "known"], last)
    add(["optional-nickname", "--id", "known", "--nickname", ""], error="empty_value")
    last["nickname"] = ""; add(["optional-nickname", "--id", "known", "--nickname", "   "], last)
    add(["conditional-description", "--id", "known"], last)
    last["description"] = ""; add(["conditional-description", "--id", "known", "--description", ""], last)
    add(["conditional-description", "--id", "known", "--description", "   "], error="empty_value")
    last["description"] = "Text"; add(["conditional-description", "--id", "known", "--description", " Text "], last)
    add(["list"], [last])
    create = p["cases"][1]
    supplied = ["--alias-data", '["B","A","B"]'] if domain == "contact" else []
    initial = ["B", "A", "B"] if domain == "contact" else ["Seed", "A", "Seed"] if domain == "product" else []
    create["steps"] = [
        dict(argv=["create", "--nickname", "Created", *supplied], returncode=0, contains=['"category": "public"', '"' + field + '": ' + __import__('json').dumps(initial)], stderr_exact=""),
        dict(argv=["list"], returncode=0, contains=['"category": "public"', '"' + field + '": ' + __import__('json').dumps(initial)], preserved=[path], stderr_exact=""),
        dict(argv=["create", *supplied], returncode=1, contains=[], stdout_exact="", stderr_json={"error": "missing_nickname"}, preserved=[path])]
    if domain == "contact":
        create["steps"].append(dict(argv=["create", "--nickname", "Missing"], returncode=1, contains=[], stdout_exact="", stderr_json={"error": "missing_aliases"}, preserved=[path]))
    if domain == "product":
        create["steps"].append(dict(argv=["find-value", "--value", "Seed"], returncode=0, contains=['"keywords": ["Seed", "A", "Seed"]'], preserved=[path], stderr_exact=""))
    for c in p["cases"]:
        c.pop("identity", None); c["identity"] = hashlib.sha256(canonical(c)).hexdigest()
    for row in p["coverage"]:
        row["cases"] = [c["identity"] for c in p["cases"]]
    p["producer"] = "R5.105 source-first multi-domain literal oracle"
    return p
