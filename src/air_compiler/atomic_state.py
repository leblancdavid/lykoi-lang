"""Bounded ordinary record creation coupled to an existing atomic store write."""
import copy

from .references import keys, require, erase, value_type, identity, validate_condition
from .mutable_values import valid_value
from .predicates import same_type
from .collection_query import validate as validate_query

VERSION = "atomic-durable-state-1"
FACET = "atomic_state_semantics"
COMMIT = dict(scope="one_store", mutation="bounded_records", isolation="exclusive_operation", rejection="unchanged")


def compose(ir, references, facts):
    keys(facts, ("operations", "queries", "append_only", "commit"))
    require(facts["commit"] == COMMIT, "Explicit bounded atomic frame")
    types, ids = references["types"], references["identities"]
    primary = references["facts"]["primary"]
    model = ir["model"]
    behaviors = {c["token"]: next(b for b in model["behaviors"] if b["id"] == c["behavior"]) for c in model["commands"] if "behavior" in c}
    mutations = {m["command"]: m for m in ir["facts"]["mutations"]}
    related = {o["command"]: o for o in references["facts"]["operations"]}
    commands = set(behaviors) | set(mutations) | set(related) | {"migrate"}
    capabilities = {c["id"]: c["kind"] for c in model["capabilities"]}
    require(type(facts["append_only"]) is list and len(set(facts["append_only"])) == len(facts["append_only"]), "Explicit unique closed-write entities")
    require(all(e in types and e != primary for e in facts["append_only"]), "Related append-only collection")
    require(all(o["kind"] == "list" for o in related.values() if o["entity"] in facts["append_only"]), "Append-only disallows standalone write operations")
    seen = set()
    for op in facts["operations"]:
        keys(op, ("command", "entity", "parameters", "resources", "on", "sampling", "ordering", "creations") + (("computations",) if "computations" in op else ()))
        cmd, entity = op["command"], op["entity"]
        require(cmd not in seen and cmd in commands and cmd != "migrate", "Existing unique primary write command")
        seen.add(cmd)
        require(op["on"] == "success" and op["sampling"] == "once_per_operation" and op["ordering"] == "declared_creation_occurrence", "Success-only creation, declared observation and occurrence order")
        if cmd in related:
            r = related[cmd]
            require(r["kind"] != "list" and r["entity"] == entity, "Primary related write")
            kind = r["kind"]
            params = {n: p["type"] for n, p in r["parameters"].items()}
        else:
            require(entity == primary, "Existing primary state binding")
            kind = behaviors[cmd]["kind"] if cmd in behaviors else "update"
            require(kind in ("create", "transition", "delete", "update"), "No creation on readonly command")
            params = {p["parameter"]: p["type"] for p in ir["facts"].get("input_contracts", []) if p["operation"] == cmd}
            if cmd in behaviors and kind != "create":
                params = {i["name"]: params.get(i["name"], identity(primary)) for i in behaviors[cmd]["inputs"]}
            if ids[primary] in params: params[ids[primary]] = identity(primary)
            from .primary_interfaces import contexts
            params.update(contexts(ir["facts"], cmd))
        require(op["parameters"] == params, "Exact existing primary input authority")
        resources = {}
        for r in op["resources"]:
            keys(r, ("name", "type", "capability") + (("observation",) if "observation" in r else ()))
            require(r["name"] not in resources and r["capability"] in capabilities, "Unique declared resource binding")
            value_type(r["type"], types)
            k = capabilities[r["capability"]]
            require(r.get("observation", "operation") in ("operation", "binding") and (r.get("observation") != "binding" or k == "uuid_v4"), "Independent named identity observation only; clock stays shared")
            require((k == "utc_clock" and erase(r["type"]) == dict(type="timestamp", domain=[])) or (k == "uuid_v4" and r["type"]["type"] == "identifier"), "Existing clock/identity capability")
            resources[r["name"]] = r["type"]
        computed = {}
        if "computations" in op:
            from .computation import validate as validate_computation
            computed = validate_computation(op["computations"], types, entity, params, resources, images=("after",) if kind == "create" else ("before",) if kind == "delete" else ("before", "after"))
        require(type(op["creations"]) is list and 1 <= len(op["creations"]) <= 8, "Bounded nonempty creation sequence")
        named = {c["binding"]: c for c in op["creations"] if "binding" in c}
        extended = bool(named)
        require(not extended or len(named) == len(op["creations"]), "Every dependent image explicitly named, uniquely")
        dependencies = {}
        for creation in op["creations"]:
            keys(creation, ("entity", "bindings", "duplicate_error") + (("binding", "when", "depends_on") if extended else ()) + (("computations",) if "computations" in creation else ()))
            e = creation["entity"]
            require(e in types, "Ordinary typed record creation, including same-primary successor")
            local_computed = computed
            if extended:
                require(type(creation["binding"]) is str and bool(creation["binding"]), "Explicit created image name")
                if creation["when"] is not None:
                    validate_condition(creation["when"], types, {"primary": entity} if kind != "create" else {}, params)
                dependencies[creation["binding"]] = []
            if "computations" in creation:
                from .computation import validate as validate_computation
                local = validate_computation(creation["computations"], types, entity, params, resources, images=("after",) if kind == "create" else ("before",) if kind == "delete" else ("before", "after"))
                require(not set(computed) & set(local), "Local computations cannot shadow operation results")
                local_computed = {**computed, **local}
            require(type(creation["duplicate_error"]) is str and bool(creation["duplicate_error"]), "Declared duplicate error")
            require(set(creation["bindings"]) == set(types[e]), "Complete authorized typed payload; no JSON blob")
            for n, b in creation["bindings"].items():
                keys(b, ("source", "invalid_error"))
                require(type(b["invalid_error"]) is str and bool(b["invalid_error"]), "Declared record validation failure")
                s = b["source"]
                if s.get("kind") == "created":
                    keys(s, ("kind", "type", "effect", "entity", "field", "alternative"))
                    require(extended and s["effect"] in named and s["effect"] != creation["binding"], "Declared distinct dependency image")
                    parent = named[s["effect"]]
                    require(s["entity"] == parent["entity"] and s["field"] in types[s["entity"]] and same_type(s["type"], types[s["entity"]][s["field"]]) and same_type(s["type"], types[e][n]), "Exact created entity/field type")
                    if s["effect"] not in dependencies[creation["binding"]]: dependencies[creation["binding"]].append(s["effect"])
                    alternative = s["alternative"]
                    require(parent["when"] is None or parent["when"] == creation["when"] or alternative is not None, "Conditional dependency must be selected or have explicit alternative")
                    if alternative is not None:
                        keys(alternative, ("kind", "type", "value"))
                        require(alternative["kind"] == "literal" and same_type(alternative["type"], s["type"]) and valid_value(alternative["value"], erase(s["type"])), "Explicit typed alternative; no guessed fallback")
                    continue
                if s.get("kind") == "computed":
                    from .computation import bound
                    bound(s, local_computed, types[e][n])
                    continue
                require(s.get("kind") in ("literal", "parameter", "before", "after", "resource"), "Existing typed value sources only; no arithmetic")
                keys(s, ("kind", "type", "value") if s["kind"] == "literal" else ("kind", "type", "name"))
                require(same_type(s["type"], types[e][n]), "Exact nominal payload type")
                if s["kind"] == "literal":
                    require(valid_value(s["value"], erase(s["type"])), "Typed literal payload")
                else:
                    env = params if s["kind"] == "parameter" else resources if s["kind"] == "resource" else types[entity]
                    require(s["name"] in env and same_type(s["type"], env[s["name"]]), "Explicit bound payload source")
                    require(not (kind == "create" and s["kind"] == "before") and not (kind == "delete" and s["kind"] == "after"), "Available observation image")
        for name, deps in dependencies.items():
            declared = named[name]["depends_on"]
            require(type(declared) is list and len(set(declared)) == len(declared) and set(declared) == set(deps), "Exact explicit effect dependencies")
        pending = set(dependencies)
        while pending:
            ready = {n for n in pending if not set(dependencies[n]) & pending}
            require(bool(ready), "Acyclic effect graph")
            pending -= ready
    for q in facts["queries"]:
        require(q["id"] not in commands, "Unique query command")
        commands.add(q["id"])
        e = q["source"]["collection"]
        require(e in types and e != primary and q["source"] == dict(collection=e, fields={n: erase(t) for n, t in types[e].items()}, unique_key=ids[e]), "Exact ordinary entity CollectionQuery binding")
        validate_query(q, complete=True, occurrence_order=True)
    return dict(version=VERSION, facts=copy.deepcopy(facts))
