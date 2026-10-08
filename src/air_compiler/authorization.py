"""Source-declared permission predicates over the committed operation snapshot."""
import copy

from .references import keys, require, validate_condition, identity

VERSION = "prewrite-authorization-1"
FACET = "authorization_semantics"


def compose(ir, references, facts):
    keys(facts, ("operations",))
    model = ir["model"]
    primary = references["facts"]["primary"]
    related = {o["command"]: o for o in references["facts"]["operations"]}
    commands = {c["token"]: next(b for b in model["behaviors"] if b["id"] == c["behavior"]) for c in model["commands"] if "behavior" in c}
    mutations = {m["command"]: m for m in ir["facts"]["mutations"]}
    seen = set()
    for op in facts["operations"]:
        keys(op, ("command", "entity", "lookup", "actor", "parameters", "predicate", "error", "observation", "rejection") + (("checks",) if "checks" in op else ()))
        cmd = op["command"]
        require(cmd not in seen and cmd in set(related) | set(commands) | set(mutations), "Unique existing authorization operation")
        seen.add(cmd)
        require(op["observation"] == "committed_operation_before" and op["rejection"] == "unchanged", "Prewrite permission, never filtering")
        require(type(op["error"]) is str and bool(op["error"]), "Declared permission rejection")
        if cmd in related:
            r = related[cmd]
            require(r["kind"] != "list", "Authorization guards write contracts")
            entity, lookup = r["entity"], r["lookup"]
            params = {n: p["type"] for n, p in r["parameters"].items()}
        else:
            entity = primary
            b = commands.get(cmd)
            require(b is None or b["kind"] in ("create", "transition", "update", "delete"), "Write operation only")
            lookup = references["identities"][primary] if b and b["kind"] != "create" else mutations[cmd]["lookup"] if not b else None
            params = {p["parameter"]: p["type"] for p in ir["facts"].get("input_contracts", []) if p["operation"] == cmd}
            from .primary_interfaces import contexts
            params.update(contexts(ir["facts"], cmd))
            if lookup in params: params[lookup] = identity(primary)
            if b and b["kind"] == "create":
                record = next(t for t in model["types"] if t["kind"] == "record")
                field_names = {f["id"]: f["name"] for f in record["fields"]}
                input_names = {i["id"]: i["name"] for i in b["inputs"]}
                # Creation inputs bound to declared persistent references inherit
                # that exact nominal target; no arbitrary nominal cast is allowed.
                for assignment in b["assignments"]:
                    name = field_names[assignment["field"]]
                    typ = references["types"][primary][name]
                    if assignment["source"] in ("input", "input_default") and "entity" in typ:
                        params[input_names[assignment["id"]]] = typ
        require(op["entity"] == entity and op["lookup"] == lookup and op["parameters"] == params, "Exact operation parameter and preimage authority")
        actor = op["actor"]
        keys(actor, ("name", "type", "source", "context", "missing_error", "invalid_error"))
        require(actor["name"] in params and actor["type"] == params[actor["name"]] and actor["type"] == identity(actor["type"].get("entity")), "Nominal actor binding")
        require(actor["source"] in ("explicit_parameter", "trusted_context"), "No inferred authenticated actor")
        require((actor["context"] is None) if actor["source"] == "explicit_parameter" else (type(actor["context"]) is str and bool(actor["context"])), "Explicit authorized embedding context; CLI has no trusted principal")
        require(all(type(actor[k]) is str and bool(actor[k]) for k in ("missing_error", "invalid_error")), "Declared actor errors")
        validate_condition(op["predicate"], references["types"], {"primary": entity} if lookup else {}, params)
        require(type(op.get("checks", [])) is list and len(op.get("checks", [])) <= 64, "Bounded ordered prewrite checks")
        for check in op.get("checks", []):
            keys(check, ("predicate", "error"))
            require(type(check["error"]) is str and bool(check["error"]), "Explicit prewrite check error")
            validate_condition(check["predicate"], references["types"], {"primary": entity} if lookup else {}, params)
    return dict(version=VERSION, facts=copy.deepcopy(facts))
