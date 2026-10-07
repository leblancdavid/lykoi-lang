"""Bounded semantic parameters and separate external binding validation."""
from .mutable_values import keys, require, pipeline

VERSION = "typed-input-values-1"


def validate_contracts(model, types, facts):
    from lykoi_pipeline.scalar_profile import name
    declarations = facts["input_contracts"]
    require(type(declarations) is list, "Explicit input contracts")
    create = next(b for b in model["behaviors"] if b["kind"] == "create")
    command = next(c for c in model["commands"] if c.get("behavior") == create["id"])
    record = next(t for t in model["types"] if t["kind"] == "record")
    fields = {f["id"]: f["name"] for f in record["fields"]}
    expected = {}
    for i in create["inputs"]:
        assignment = next(a for a in create["assignments"] if a.get("id") == i["id"])
        encoding = next((c["creation"]["encoding"] for c in facts["collections"] if c["creation"].get("input") == i["name"]), "text")
        expected[(command["token"], i["name"])] = (types[fields[assignment["field"]]], assignment["source"] == "input", encoding)
    for m in facts["mutations"]:
        expected[(m["command"], m["lookup"])] = (types[m["lookup"]], True, "text")
        for w in m["changes"]:
            typ = types[w["field"]] if w["operation"] == "replace" else types[w["field"]]["element"]
            expected[(m["command"], w["input"])] = (typ, w["omitted"] == "reject", "json" if typ["type"] == "collection" else "text")
    seen, flags = set(), set()
    for p in declarations:
        keys(p, ("operation", "parameter", "type", "presence", "binding", "missing"))
        name(p["parameter"])
        key = (p["operation"], p["parameter"])
        require(key in expected and key not in seen, "Correct unique semantic parameter binding; constants are not parameters")
        seen.add(key)
        typ, required, encoding = expected[key]
        require(p["type"] == typ, "Exact parameter type, domain and collection policy")
        require(p["presence"] == ("required" if required else "optional"), "Presence must agree with operation, not parser defaults")
        keys(p["binding"], ("source", "flag", "encoding"))
        b = p["binding"]
        require(b["source"] == "cli_flag" and type(b["flag"]) is str and b["flag"].startswith("--") and len(b["flag"]) > 2 and all(ch.isalnum() or ch in "-_" for ch in b["flag"][2:]), "Declared external flag adapter")
        require(b["encoding"] == encoding, "Faithful external type encoding")
        require((p["operation"], b["flag"]) not in flags, "No conflicting external bindings")
        flags.add((p["operation"], b["flag"]))
        if required:
            require(type(p["missing"]) is dict, "Required input needs declared missing behavior")
            if p["missing"].get("kind") == "application_error":
                keys(p["missing"], ("kind", "error")); name(p["missing"]["error"])
                mutation = next((m for m in facts["mutations"] if m["command"] == p["operation"]), None)
                if mutation and p["parameter"] != mutation["lookup"]:
                    w = next(w for w in mutation["changes"] if w["input"] == p["parameter"])
                    require(w["missing_error"] == p["missing"]["error"], "Missing-input authority agrees across API and external binding")
            else:
                keys(p["missing"], ("kind",))
                require(p["missing"]["kind"] == "cli_rejection", "Declared structured application error or external missing-input rejection")
                mutation = next((m for m in facts["mutations"] if m["command"] == p["operation"]), None)
                if mutation and p["parameter"] != mutation["lookup"]:
                    w = next(w for w in mutation["changes"] if w["input"] == p["parameter"])
                    require(w["missing_error"] is None, "CLI rejection must not fabricate an API application error")
        else:
            require(p["missing"] is None, "Optional input cannot invent missing error")
    require(seen == set(expected), "Every creation and mutation parameter has one required external binding")
    # An explicitly selected closure cannot silently fall back to CURRENT-stage validation.
    def explicit(steps):
        for step in steps:
            if step["kind"] == "validate":
                require("stage" in step and "when" in step, "Closure validation needs explicit stage and condition")
            if step["kind"] == "map_elements":
                explicit(step["pipeline"])
    for c in facts["collections"]:
        explicit(c["creation"].get("pipeline", []))
    for c in facts["creation_pipelines"]:
        explicit(c["pipeline"])
    for m in facts["mutations"]:
        for w in m["changes"]:
            explicit(w["pipeline"])
