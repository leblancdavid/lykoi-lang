"""ExistingScalar-1: typed WHAT facts lowered to the existing v0.3 algebra.

No prose interpretation, benchmark dispatch or new runtime operations. The
formalizer emits these facts; source reconciliation and owner seals authorize them.
"""
import copy
import json
import re

from air_compiler.parser import parse
from air_compiler.validator import validate
from benchmark.evaluation import formal_requirements_r5_80 as frc
from benchmark.evaluation import behavioral_discovery_r5_82 as discovery
from benchmark.evaluation import implementation_adequacy_r5_81 as adequacy
from lykoi_controller import Failure

PROFILE = "existing-scalar-1"
V1 = "LykoiContractV1"
FACETS = ("storage", "fields", "creation", "listing", "lifecycle", "evolution")
OPTIONAL_FACETS = ("guards", "clock_queries")


def typed(relation):
    return relation.get("parameters", {}).get("profile") == PROFILE


def applies(contract):
    return any(typed(o["relation"]) for o in contract["obligations"])


def require(value, reason):
    if not value:
        raise Failure("INVALID_TYPED_SCALAR_RELATION", reason=reason)


def keys(value, names):
    require(type(value) is dict and set(value) == set(names), "Closed typed object: " + str(names))


def name(value):
    require(type(value) is str and re.fullmatch(r"[a-z][a-z0-9_]*", value), "Invalid semantic name")


def command_name(value):
    require(type(value) is str and re.fullmatch(r"[a-z][a-z0-9_-]*", value), "Invalid command token")


def facts(contract):
    frc.validate(contract)
    result = {}
    for o in contract["obligations"]:
        r = o["relation"]
        if not typed(r):
            continue
        require(r["kind"] == "crud", "Scalar facts use the existing crud relation kind")
        p = r["parameters"]
        keys(p, ("profile", "facet", "value"))
        require(p["facet"] in FACETS + OPTIONAL_FACETS and p["facet"] not in result, "Unknown/duplicate scalar facet")
        result[p["facet"]] = copy.deepcopy(p["value"])
    require(set(FACETS) <= set(result), "Missing scalar facet; empty is explicit, never inferred")
    validate_facts(result)
    return result


def validate_facts(f):
    require(set(FACETS) <= set(f) <= set(FACETS + OPTIONAL_FACETS), "Closed scalar facets")
    keys(f["storage"], ("path", "version", "missing", "write", "rejection"))
    s = f["storage"]
    require(type(s["path"]) is str and re.fullmatch(r"[a-z][a-z0-9_-]*\.json", s["path"]), "Local JSON resource path")
    require(type(s["version"]) is int and s["version"] >= 1, "Schema version")
    require(s["missing"] == "empty_collection" and s["write"] == "atomic" and s["rejection"] == "unchanged", "Existing persistence policies only")
    require(type(f["fields"]) is list and bool(f["fields"]), "Nonempty scalar fields")
    seen = set()
    for field in f["fields"]:
        keys(field, ("name", "type", "domain", "nullable", "preservation"))
        name(field["name"])
        require(field["name"] not in seen, "Duplicate field")
        seen.add(field["name"])
        require(field["type"] in ("string", "identifier", "enum", "timestamp"), "Writable scalar type not present in v0.3")
        require(type(field["nullable"]) is bool and (not field["nullable"] or field["type"] == "timestamp"), "Only existing timestamp nullability")
        require(field["preservation"] == "verbatim", "Write transformations are not existing semantics")
        domain = field["domain"]
        require((field["type"] == "enum" and type(domain) is list and bool(domain) and all(type(x) is str for x in domain) and len(set(domain)) == len(domain)) or (field["type"] != "enum" and domain == []), "Exact finite enum domain")
    keys(f["creation"], ("command", "bindings", "validation"))
    name(f["creation"]["command"])
    require(type(f["creation"]["bindings"]) is list and type(f["creation"]["validation"]) is list, "Creation arrays")
    bound = set()
    for b in f["creation"]["bindings"]:
        keys(b, ("field", "source", "value", "default"))
        require(b["field"] in seen and b["field"] not in bound, "Creation field binding")
        bound.add(b["field"])
        require(b["source"] in ("input", "literal", "uuid_v4", "utc_clock"), "Explicit creation resource/input")
        if b["source"] == "input":
            require(b["value"] is None, "Input preservation has no transform")
        elif b["source"] in ("uuid_v4", "utc_clock"):
            require(b["value"] is None, "Resource value supplied by declared capability")
        if b["default"] is not None:
            keys(b["default"], ("value", "trigger", "boundary"))
            require(b["source"] == "input" and b["default"]["trigger"] == "omitted" and b["default"]["boundary"] == "creation", "Explicit creation-only omission default")
    require(bound == seen, "Every field has explicit creation authority")
    for v in f["creation"]["validation"]:
        keys(v, ("field", "rule", "error"))
        require(v["field"] in seen and v["rule"] in ("nonblank", "timestamp_utc"), "Existing scalar guard")
        name(v["error"])
        binding = next(b for b in f["creation"]["bindings"] if b["field"] == v["field"])
        require(binding["source"] == "input", "Input guard requires input authority")
        require(v["rule"] != "nonblank" or binding["default"] is None, "Existing nonblank guard requires supplied input, not inferred presence semantics")
    keys(f["listing"], ("command", "order", "result"))
    name(f["listing"]["command"])
    require(type(f["listing"]["order"]) is list and bool(f["listing"]["order"]) and all(x in seen for x in f["listing"]["order"]), "Explicit ascending field order")
    require(f["listing"]["result"] == "whole_records", "Whole records preserved")
    require(type(f["lifecycle"]) is list, "Lifecycle array")
    for t in f["lifecycle"]:
        keys(t, ("field", "initial", "source", "target", "command", "missing_error", "transition_error", "rejection"))
        require(t["field"] in seen and t["initial"] == t["source"] and t["source"] != t["target"] and t["rejection"] == "unchanged", "Existing guarded transition")
        for k in ("command", "missing_error", "transition_error"):
            name(t[k])
    require(type(f["evolution"]) is list, "Explicit evolution array")
    for m in f["evolution"]:
        keys(m, ("from", "to", "defaults", "boundary", "preservation"))
        require(type(m["from"]) is int and type(m["to"]) is int and m["to"] == m["from"] + 1, "Additive migration version")
        require(type(m["defaults"]) is dict and bool(m["defaults"]) and set(m["defaults"]) <= seen, "Explicit migration field defaults")
        require(m["boundary"] == "explicit_migration" and m["preservation"] == "unrelated_fields", "No inferred historical default authority")
    require(type(f.get("guards", [])) is list and type(f.get("clock_queries", [])) is list, "Explicit integration arrays")
    for g in f.get("guards", []):
        keys(g, ("command", "field", "value", "error", "rejection"))
        command_name(g["command"]); name(g["error"])
        require(g["field"] in seen and g["rejection"] == "unchanged", "Existing equality guard field/frame")
    for q in f.get("clock_queries", []):
        keys(q, ("command", "predicates", "order", "result", "effect"))
        command_name(q["command"])
        require(type(q["predicates"]) is list and bool(q["predicates"]), "Existing conjunction selection only")
        require(type(q["order"]) is list and bool(q["order"]) and all(n in seen for n in q["order"]), "Declared query order")
        require(q["result"] == "whole_records" and q["effect"] == "read_only", "Existing read-only whole-record selection")
        for p in q["predicates"]:
            if p.get("kind") == "field_equals":
                keys(p, ("kind", "field", "value"))
            else:
                keys(p, ("kind", "field", "clock"))
                require(p["kind"] == "field_before_clock" and p["clock"] == "utc_clock", "Existing strict clock comparison only")
            require(p["field"] in seen, "Declared predicate field")


def lower(f, base=None):
    """Deterministic implementation of authorized facts, using only v0.3 nodes."""
    validate_facts(f)
    if base is not None:
        return integrate_facets(extend_model(f, base), f)
    fields = {x["name"]: x for x in f["fields"]}
    bindings = {x["field"]: x for x in f["creation"]["bindings"]}
    identity = [x for x, b in bindings.items() if b["source"] == "uuid_v4"]
    require(len(identity) == 1 and fields[identity[0]]["type"] == "identifier", "One existing UUID-backed stable identity")
    key = identity[0]
    require(key in f["listing"]["order"], "Deterministic identity tie key")
    fid = lambda n: "field:" + n
    typ = lambda n: "type:" + n if fields[n]["type"] == "enum" else "prim:timestamp" if fields[n]["type"] == "timestamp" else "prim:string"
    d = {"axiom_version": "0.3", "application": {"id": "application", "name": "scalar_records"},
         "types": [], "capabilities": [], "state": [], "invariants": [], "behaviors": [],
         "commands": [], "errors": [], "migrations": [], "state_machines": [], "transitions": []}
    for n, x in fields.items():
        if x["type"] == "enum":
            d["types"].append({"id": typ(n), "name": n, "kind": "enum", "values": x["domain"]})
    d["types"] += [{"id": "record", "name": "Record", "kind": "record", "fields": [
        {"id": fid(n), "name": n, "type": typ(n), **({"nullable": True} if x["nullable"] else {})} for n, x in fields.items()]},
        {"id": "records", "name": "Records", "kind": "list", "item_type": "record"}]
    d["capabilities"] = [{"id": "store", "kind": "json_file", "path": f["storage"]["path"], "missing_file": "empty_collection"},
        {"id": "read", "kind": "resource_access", "resource": "store", "action": "read"},
        {"id": "write", "kind": "resource_access", "resource": "store", "action": "write"}]
    resources = sorted({b["source"] for b in bindings.values()} & {"uuid_v4", "utc_clock"})
    d["capabilities"] += [{"id": r, "kind": r} for r in resources]
    error_codes = {"invalid_state", "persistence_failure", "id_collision"}
    if f["storage"]["version"] > 1:
        error_codes.add("migration_required")
    error_codes |= {v["error"] for v in f["creation"]["validation"]}
    error_codes |= {t[k] for t in f["lifecycle"] for k in ("missing_error", "transition_error")}
    d["errors"] = [{"id": "error:" + e, "code": e} for e in sorted(error_codes)]
    d["invariants"] = [{"id": "unique", "kind": "unique_field", "state": "state", "field": fid(key)},
        {"id": "valid", "kind": "all_records_valid", "state": "state", "field_rules": []}]
    d["state"] = [{"id": "state", "name": "records", "type": "records", "storage": "store", "key_field": fid(key),
        "schema_version": f["storage"]["version"], "invariants": ["unique", "valid"]}]

    def behavior(command, kind):
        builtin = {"invalid_state", "persistence_failure"}
        if f["storage"]["version"] > 1:
            builtin.add("migration_required")
        if kind == "create":
            builtin.add("id_collision")
        b = {"id": "behavior:" + command, "name": command, "kind": kind, "state": "state", "inputs": [],
             "output": "records" if kind == "list" else "record", "dependencies": ["state", "store"],
             "requires": ["read"] + ([] if kind == "list" else ["write"]), "reads": ["state"],
             "writes": [] if kind == "list" else ["state"], "effects": ["state_read", "file_read"] + ([] if kind == "list" else ["state_write", "file_write"]),
             "conditions": [], "assignments": [], "guarantees": [], "failures": ["error:" + x for x in sorted(builtin)]}
        c = {"id": "command:" + command, "token": command, "behavior": b["id"], "arguments": []}
        d["behaviors"].append(b); d["commands"].append(c)
        return b, c

    create, cmd = behavior(f["creation"]["command"], "create")
    for n, b in bindings.items():
        assignment = {"field": fid(n)}
        if b["source"] == "input":
            iid = "input:create:" + n
            create["inputs"].append({"id": iid, "name": n, "type": typ(n), **({"nullable": True} if fields[n]["nullable"] else {})})
            cmd["arguments"].append({"flag": "--" + n.replace("_", "-"), "input": iid, "required": b["default"] is None})
            assignment.update(source="input" if b["default"] is None else "input_default", id=iid)
            if b["default"] is not None:
                assignment["value"] = b["default"]["value"]
        elif b["source"] == "literal":
            assignment.update(source="literal", value=b["value"])
        else:
            assignment.update(source="capability", id=b["source"])
            create["dependencies"].append(b["source"]); create["requires"].append(b["source"])
            create["effects"].append("random_id" if b["source"] == "uuid_v4" else "clock_read")
        create["assignments"].append(assignment)
    for index, v in enumerate(f["creation"]["validation"]):
        create["conditions"].append({"id": "guard:create:" + str(index), "kind": "nonblank_input" if v["rule"] == "nonblank" else "timestamp_input", "input": "input:create:" + v["field"], "failure": "error:" + v["error"]})
        create["failures"].append("error:" + v["error"])
    literals = [a for a in create["assignments"] if a["source"] == "literal"]
    require(bool(literals), "Existing backend requires a literal result guarantee on creation")
    create["guarantees"] = [{"id": "guarantee:create:value", "kind": "result_field_equals", "field": literals[0]["field"], "value": literals[0]["value"]},
        {"id": "guarantee:create:stored", "kind": "result_in_state", "state": "state"}]
    create["guarantees"] += [{"id": "guarantee:create:" + n, "kind": "result_field_equals_assignment", "field": fid(n)} for n, b in bindings.items() if b["source"] == "input"]
    create["guarantees"] += [{"id": "guarantee:create:literal:" + a["field"], "kind": "result_field_equals_assignment", "field": a["field"]} for a in literals[1:]]
    for k in ("dependencies", "requires", "effects", "failures"):
        create[k] = sorted(set(create[k]))
    listing, _ = behavior(f["listing"]["command"], "list")
    listing["order_by"] = [fid(n) for n in f["listing"]["order"]]
    listing["guarantees"] = [{"id": "guarantee:list", "kind": "result_equals_state_sorted", "state": "state"}]
    for t in f["lifecycle"]:
        n = t["field"]
        require(fields[n]["type"] == "enum" and bindings[n]["source"] == "literal" and bindings[n]["value"] == t["initial"], "Source-authorized initial lifecycle state")
        mid, tid = "machine:" + n, "transition:" + t["command"]
        require(not any(m["id"] == mid for m in d["state_machines"]), "Bounded single transition per field")
        update, command = behavior(t["command"], "update")
        iid = "input:" + t["command"] + ":id"
        update["inputs"] = [{"id": iid, "name": key, "type": "prim:string"}]
        command["arguments"] = [{"flag": "--" + key.replace("_", "-"), "input": iid, "required": True}]
        update["lookup"] = {"field": fid(key), "input": iid}
        guard = "guard:" + t["command"]
        update["conditions"] = [{"id": guard + ":exists", "kind": "record_exists", "failure": "error:" + t["missing_error"]},
            {"id": guard, "kind": "record_field_equals", "field": fid(n), "value": t["source"], "failure": "error:" + t["transition_error"]}]
        update["assignments"] = [{"field": fid(n), "source": "literal", "value": t["target"]}]
        update["performs"] = tid
        update["failures"] = sorted(set(update["failures"] + ["error:" + t["missing_error"], "error:" + t["transition_error"]]))
        update["guarantees"] = [{"id": "guarantee:" + t["command"] + ":value", "kind": "result_field_equals", "field": fid(n), "value": t["target"]},
            {"id": "guarantee:" + t["command"] + ":stored", "kind": "result_in_state", "state": "state"}]
        d["state_machines"].append({"id": mid, "name": n, "field": fid(n), "initial": t["initial"], "transitions": [tid]})
        d["transitions"].append({"id": tid, "machine": mid, "source": t["source"], "target": t["target"], "trigger": update["id"], "guard": guard, "effects": ["state_write"]})
    for m in f["evolution"]:
        d["migrations"].append({"id": "migration:" + str(m["from"]), "state": "state", "from_version": m["from"], "to_version": m["to"],
            "add_fields": [{"field": fid(n), "value": v} for n, v in m["defaults"].items()], "requires": ["read", "write"], "effects": ["state_read", "state_write", "file_read", "file_write"]})
    if d["migrations"]:
        d["commands"].append({"id": "command:migrate", "token": "migrate", "migration": max(d["migrations"], key=lambda m: m["to_version"])["id"], "arguments": []})
    return integrate_facets(d, f)


def integrate_facets(d, f):
    """Bind already-executable v0.3 guards and equality/before-clock selections.

    Ordered guard failures are preserved. New conflicting guards on a field and
    command collisions refuse, rather than silently changing old authority.
    """
    types = {t["id"]: t for t in d["types"]}
    state = d["state"][0]
    fields = {x["name"]: x["id"] for x in types[types[state["type"]]["item_type"]]["fields"]}
    commands = {c["token"]: c for c in d["commands"]}
    def error(code):
        old = next((e for e in d["errors"] if e["code"] == code), None)
        if old is None:
            old = {"id": "error:integration:" + code, "code": code}; d["errors"].append(old)
        return old["id"]
    for i, g in enumerate(f.get("guards", [])):
        require(g["command"] in commands and "behavior" in commands[g["command"]], "Guard requires existing command")
        b = next(b for b in d["behaviors"] if b["id"] == commands[g["command"]]["behavior"])
        require(b["kind"] in ("update", "delete"), "Existing lookup guard operations only")
        require(b["conditions"][0]["kind"] == "record_exists", "Existence precondition precedes field guard")
        prior = [c for c in b["conditions"] if c["kind"] == "record_field_equals" and c["field"] == fields[g["field"]]]
        eid = error(g["error"])
        require(not prior or all(c["value"] == g["value"] and c["failure"] == eid for c in prior), "CONFLICT: existing guard authority")
        if not prior:
            b["conditions"].append({"id": "guard:integration:" + str(i), "kind": "record_field_equals", "field": fields[g["field"]], "value": g["value"], "failure": eid})
            b["failures"] = sorted(set(b["failures"] + [eid]))
    for q in f.get("clock_queries", []):
        require(q["command"] not in commands, "CONFLICT: existing command authority")
        require(state["key_field"] in [fields[n] for n in q["order"]], "Identity tie key required")
        read = next(c["id"] for c in d["capabilities"] if c["kind"] == "resource_access" and c["resource"] == state["storage"] and c["action"] == "read")
        predicates = []
        clocks = set()
        for p in q["predicates"]:
            node = {**p, "field": fields[p["field"]]}
            if p["kind"] == "field_before_clock":
                clock = next((c for c in d["capabilities"] if c["kind"] == "utc_clock"), None)
                if clock is None:
                    clock = {"id": "utc_clock", "kind": "utc_clock"}; d["capabilities"].append(clock)
                node["clock"] = clock["id"]; clocks.add(clock["id"])
            predicates.append(node)
        bid = "behavior:selection:" + q["command"]
        failures = [e["id"] for e in d["errors"] if e["code"] in ("invalid_state", "persistence_failure", "migration_required")]
        d["behaviors"].append({"id": bid, "name": q["command"], "kind": "list", "state": state["id"], "inputs": [], "output": state["type"],
            "dependencies": sorted({state["id"], state["storage"]} | clocks), "requires": sorted({read} | clocks), "reads": [state["id"]], "writes": [],
            "effects": ["state_read", "file_read"] + (["clock_read"] if clocks else []), "conditions": [], "assignments": [],
            "filter": predicates[0] if len(predicates) == 1 else {"kind": "all", "predicates": predicates}, "order_by": [fields[n] for n in q["order"]],
            "guarantees": [{"id": "guarantee:selection:" + q["command"], "kind": "result_equals_state_sorted", "state": state["id"]}], "failures": failures})
        d["commands"].append({"id": "command:selection:" + q["command"], "token": q["command"], "behavior": bid, "arguments": []})
        commands[q["command"]] = d["commands"][-1]
    validate(parse(json.dumps(d)))
    return d


def extend_model(f, base):
    """Generic additive scalar evolution of an explicitly authorized existing model.

    Existing operations/guards/resources/IDs remain intact. No guessed migrations,
    field rewrites, command renames, or unsupported precursor fields are created.
    """
    validate(parse(json.dumps(base)))
    desired = lower({k: v for k, v in f.items() if k in FACETS})
    d = copy.deepcopy(base)
    types = {t["id"]: t for t in d["types"]}
    state = d["state"][0]
    record = types[types[state["type"]]["item_type"]]
    old = {x["name"]: x for x in record["fields"]}
    all_fields = {x["name"]: x for x in f["fields"]}
    require(set(old) <= set(all_fields), "Existing fields cannot disappear")
    require(f["storage"]["path"] == next(c["path"] for c in d["capabilities"] if c["id"] == state["storage"]), "Existing resource binding cannot change")
    def semantic_type(x, table):
        t = x["type"]
        return ("enum", table[t]["values"]) if t in table else (t, [])
    desired_types = {t["id"]: t for t in desired["types"]}
    new_record = next(t for t in desired["types"] if t["kind"] == "record")
    new_fields = {x["name"]: x for x in new_record["fields"]}
    enum_changes = set()
    for n, x in old.items():
        before, after = semantic_type(x, types), semantic_type(new_fields[n], desired_types)
        compatible = before == after
        if before[0] == after[0] == "enum" and set(before[1]) < set(after[1]):
            compatible = True; enum_changes.add(n)
            types[x["type"]]["values"] = copy.deepcopy(after[1])
            for inv in d["invariants"]:
                pred = inv.get("predicate", {})
                if pred.get("operator") == "IN" and pred.get("field") == x["id"]:
                    pred["values"] = copy.deepcopy(after[1])
        require(compatible and x.get("nullable", False) == new_fields[n].get("nullable", False), "Existing type preserved; only explicit finite enum expansion")
    added = set(all_fields) - set(old)
    require(bool(added or enum_changes or any(f.get(k) for k in OPTIONAL_FACETS)), "Explicit field introduction, enum expansion or existing integration facet")
    require((state["schema_version"] < f["storage"]["version"]) if added else state["schema_version"] == f["storage"]["version"], "Explicit additive field schema boundary; enum expansion preserves version")
    mapping = {"state": state["id"], "record": record["id"], "records": state["type"], "store": state["storage"]}
    mapping.update({"field:" + n: x["id"] for n, x in old.items()})
    def remap(node):
        if type(node) is dict: return {k: copy.deepcopy(v) if k == "value" else remap(v) for k, v in node.items()}
        if type(node) is list: return [remap(v) for v in node]
        return mapping.get(node, node) if type(node) is str else node
    # Match existing creation semantics by field name, never prose or benchmark ID.
    base_create = next(b for b in d["behaviors"] if b["kind"] == "create")
    desired_create = next(b for b in desired["behaviors"] if b["kind"] == "create")
    base_command = next(c for c in d["commands"] if c.get("behavior") == base_create["id"])
    require(base_command["token"] == f["creation"]["command"], "Existing creation command binding")
    base_inputs = {i["id"]: i["name"] for i in base_create["inputs"]}
    desired_inputs = {i["id"]: i["name"] for i in desired_create["inputs"]}
    caps = {c["id"]: c["kind"] for c in d["capabilities"]}
    def assignment_semantics(a, inputs, cap_types):
        return (a["source"], inputs[a["id"]] if a["source"] in ("input", "input_default") else cap_types[a["id"]] if a["source"] == "capability" else None, a.get("value"))
    for n, x in old.items():
        a = next(a for a in base_create["assignments"] if a["field"] == x["id"])
        b = next(a for a in desired_create["assignments"] if a["field"] == "field:" + n)
        require(assignment_semantics(a, base_inputs, caps) == assignment_semantics(b, desired_inputs, {c["id"]: c["kind"] for c in desired["capabilities"]}), "Existing creation binding/default/resource authority unchanged")
    # Existing validation, lifecycle and listing clauses must be restated faithfully.
    base_guards = sorted((base_inputs[c["input"]], c["kind"], next(e["code"] for e in d["errors"] if e["id"] == c["failure"])) for c in base_create["conditions"])
    desired_guards = sorted((desired_inputs[c["input"]], c["kind"], next(e["code"] for e in desired["errors"] if e["id"] == c["failure"])) for c in desired_create["conditions"] if desired_inputs[c["input"]] in old)
    require(base_guards == desired_guards, "Existing rejection behavior preserved")
    base_list = next(b for b in d["behaviors"] if next(c["token"] for c in d["commands"] if c.get("behavior") == b["id"]) == f["listing"]["command"])
    require(base_list["kind"] == "list" and "filter" not in base_list and base_list["order_by"] == [mapping.get("field:" + n, "field:" + n) for n in f["listing"]["order"]], "Existing listing authority preserved")
    require(len(d["transitions"]) == len(f["lifecycle"]), "Existing lifecycle coverage")
    for t in f["lifecycle"]:
        transition = next(x for x in d["transitions"] if next(c["token"] for c in d["commands"] if c.get("behavior") == x["trigger"]) == t["command"])
        machine = next(m for m in d["state_machines"] if m["id"] == transition["machine"])
        b = next(b for b in d["behaviors"] if b["id"] == transition["trigger"])
        error = lambda eid: next(e["code"] for e in d["errors"] if e["id"] == eid)
        require((machine["field"], machine["initial"], transition["source"], transition["target"]) == (old[t["field"]]["id"], t["initial"], t["source"], t["target"]), "Existing lifecycle meaning preserved")
        require(error(b["conditions"][0]["failure"]) == t["missing_error"] and error(next(c["failure"] for c in b["conditions"] if c["id"] == transition["guard"])) == t["transition_error"], "Existing lifecycle errors preserved")
    for n in sorted(added):
        require(next(b for b in f["creation"]["bindings"] if b["field"] == n)["source"] == "input", "Added field uses existing input binding")
        record["fields"].append(new_fields[n])
        if new_fields[n]["type"] in desired_types:
            d["types"].append(desired_types[new_fields[n]["type"]])
        a = next(a for a in desired_create["assignments"] if a["field"] == "field:" + n)
        base_create["assignments"].append(remap(a))
        base_create["inputs"].append(next(i for i in desired_create["inputs"] if i["id"] == a["id"]))
        base_command["arguments"].append(next(arg for arg in next(c for c in desired["commands"] if c.get("behavior") == desired_create["id"])["arguments"] if arg["input"] == a["id"]))
        base_create["guarantees"].append(next(g for g in desired_create["guarantees"] if g.get("field") == "field:" + n))
        for condition in desired_create["conditions"]:
            if condition.get("input") != a["id"]:
                continue
            require(a["source"] == "input" or condition["kind"] == "timestamp_input", "Existing nonblank guard needs a supplied required input")
            error_node = next(e for e in desired["errors"] if e["id"] == condition["failure"])
            prior_error = next((e for e in d["errors"] if e["code"] == error_node["code"]), None)
            if prior_error is None:
                prior_error = copy.deepcopy(error_node); d["errors"].append(prior_error)
            node = remap(condition); node["failure"] = prior_error["id"]
            base_create["conditions"].append(node)
            base_create["failures"] = sorted(set(base_create["failures"] + [prior_error["id"]]))
    for m in desired["migrations"]:
        if m["to_version"] <= state["schema_version"]:
            prior = next(x for x in d["migrations"] if x["to_version"] == m["to_version"])
            require(prior["add_fields"] == remap(m["add_fields"]), "Historical migration authority preserved")
        else:
            require(set(a["field"] for a in m["add_fields"]) <= {"field:" + n for n in added}, "No historical field repair inferred")
            access = [c["id"] for c in d["capabilities"] if c["kind"] == "resource_access" and c["resource"] == state["storage"]]
            m = remap(m); m["requires"] = access
            d["migrations"].append(m)
    state["schema_version"] = f["storage"]["version"]
    for b in d["behaviors"]:
        if f["storage"]["version"] > 1 and not any(next(e["code"] for e in d["errors"] if e["id"] == x) == "migration_required" for x in b["failures"]):
            e = next((e for e in d["errors"] if e["code"] == "migration_required"), None)
            if e is None:
                e = {"id": "error:migration_required", "code": "migration_required"}; d["errors"].append(e)
            b["failures"].append(e["id"])
    if d["migrations"] and not any("migration" in c for c in d["commands"]):
        d["commands"].append({"id": "command:migrate", "token": "migrate", "migration": d["migrations"][-1]["id"], "arguments": []})
    for c in d["commands"]:
        if "migration" in c and d["migrations"]:
            c["migration"] = max(d["migrations"], key=lambda m: m["to_version"])["id"]
    additions = {a["field"]: a["value"] for m in d["migrations"] if m["from_version"] >= base["state"][0]["schema_version"] for a in m["add_fields"]}
    require(set(additions) == {"field:" + n for n in added}, "Each added field requires explicit migration authority")
    for scenario in d.get("scenarios", []):
        for row in scenario.get("records", [scenario["record"]] if "record" in scenario else []):
            row.update(copy.deepcopy(additions))
    validate(parse(json.dumps(d)))
    return d


def structural(contract, fid):
    unsupported = [o["id"] for o in contract["obligations"] if not typed(o["relation"])]
    if contract["context"]["component_authority"] is not None:
        unsupported.append("@component-context")
    try:
        f = facts(contract)
        lower(f, contract["context"]["domains"].get("scalar_base_model"))
    except (Failure, ValueError, KeyError, TypeError) as exc:
        unsupported += [o["id"] for o in contract["obligations"] if typed(o["relation"])]
        f = None
        reason = str(exc)
    else:
        reason = None
    ops = []
    rows = []
    for o in contract["obligations"]:
        oid = o["id"]
        supported = oid not in unsupported
        rows.append({"obligation": oid, "classification": "REPRESENTED" if supported else "UNSUPPORTED", "relation": copy.deepcopy(o["relation"]), "operation": oid if supported else None, "justification": "Typed existing scalar semantics" if supported else "No existing scalar mapping"})
        if not supported:
            continue
        p = o["relation"]["parameters"]
        facts_, authority = {}, {}
        def fact(k, v):
            facts_[k] = {"value": v, "origin": [oid], "evidence": "SEALED_TYPED_RELATION"}
        def clause(k, v):
            authority[k] = {"allowed": [v], "authority": "DETERMINED", "source_quote": o["source_quote"]}
        if p["facet"] == "creation":
            optional = any(b["default"] is not None for b in p["value"]["bindings"])
            fact("optional_input", optional)
            if optional:
                clause("optional", "default")
            fact("normalize", False)
            fact("invalid_admitted", bool(p["value"]["validation"]))
            clause("invalid_input", "reject")
        if p["facet"] == "storage":
            fact("persist", True); fact("failure_after_write", True)
            clause("persistence", "durable"); clause("failure_atomicity", "rollback")
        if p["facet"] == "lifecycle" and p["value"]:
            fact("transition", True); fact("repeat", True); fact("poststate_admitted", True)
            clause("transition", "change"); clause("retry", "reject")
        if p["facet"] in ("listing", "clock_queries"):
            fact("collection", True); fact("max_results", "many"); fact("order_varies", False)
        if p["facet"] == "guards" and p["value"]:
            fact("invalid_admitted", True); clause("invalid_input", "reject")
        ops.append({"id": oid, "facts": facts_, "channels": {"return": "MEANINGFUL", "error": "MEANINGFUL", "later": "MEANINGFUL", "order": "MEANINGFUL"}, "authority": authority})
    return {"version": PROFILE, "source_frc": fid, "rows": rows, "facts": f,
            "interface": {"version": discovery.VERSION_BDI, "operations": ops}, "unsupported": sorted(set(unsupported)), "profile_failure": reason,
            "observation_scope": "Existing typed scalar facts only; every material obligation retained", "reachability": "Bounded existing v0.3 algebra; no general completeness proof"}


def coverage(contract, projection):
    expected = structural(contract, projection["source_frc"])
    if expected != projection or expected["unsupported"]:
        raise Failure("STRUCTURAL_COVERAGE_FAILURE", unsupported=expected["unsupported"], reason=expected["profile_failure"])
    return {"outcome": "SUPPORTED", "version": PROFILE, "rows": copy.deepcopy(projection["rows"]), "scope": projection["observation_scope"], "limitations": [projection["reachability"]]}


def bdi(contract, projection):
    coverage(contract, projection)
    result = discovery.discover(contract, projection["interface"])
    return {"version": discovery.VERSION_BDI, "outcome": "SUPPORTED" if not result["unknown"] else "UNSUPPORTED", "result": result}


def adequate(contract, discovered):
    sidecar = discovery.adequacy_sidecar(contract, discovered["result"], coverage_reviewed=True)
    if not sidecar["decisions"] and sidecar["supported"]:
        sidecar["decisions"] = [{"id": "scalar:internal", "relevance": "INTERNAL", "reason": "No open supported choice"}]
    result = adequacy.analyze(contract, sidecar)
    return {"version": adequacy.VERSION, "outcome": "ADEQUATE" if result["status"] == "IMPLEMENTATION_ADEQUATE" else result["status"], "sidecar": sidecar, "result": result}


def faithful_v1(contract):
    require(contract["context"]["domains"].get("capability_profile") == PROFILE, "Explicit profile selection required")
    p = structural(contract, frc.digest(contract)); coverage(contract, p)
    normal = {"schema_version": V1, "profile": PROFILE, "contract": copy.deepcopy(contract), "facts": copy.deepcopy(p["facts"])}
    return {"version": V1, "profile": PROFILE, "outcome": "FAITHFUL_COMPLETE", "document": normal, "normalized": copy.deepcopy(normal),
            "coverage": [{"frc_id": o["id"], "v1_id": o["id"]} for o in contract["obligations"]]}


def recover(normal):
    keys(normal, ("schema_version", "profile", "contract", "facts"))
    require(normal["schema_version"] == V1 and normal["profile"] == PROFILE, "Versioned scalar V1")
    contract = copy.deepcopy(normal["contract"])
    require(faithful_v1(contract)["normalized"] == normal, "Faithful complete V1 recovery")
    return contract


def formalizer_guidance():
    return ("ExistingScalar-1 profile existing-scalar-1 uses crud relations with parameters exactly "
            "{profile,facet,value}; one each storage, fields, creation, listing, lifecycle, evolution. "
            "Writable existing types are string, identifier, enum, timestamp; only timestamps can be nullable. "
            "Declare exact domains, verbatim preservation, bindings, omitted/creation-only defaults, "
            "nonblank/timestamp guards and errors, explicit atomic store/version, whole-record ascending "
            "listing, guarded initial/source/target transitions and explicit additive migration defaults. "
            "Do not infer historical defaults from creation defaults. Empty lifecycle/evolution is explicit. "
            "Missing material authority needs a blocking question/issue. Preserve unsupported obligations. "
            "Select domains capability_profile=existing-scalar-1. All facts still require source authority, "
            "source-only inventory reconciliation, project policy review and owner approval.")
