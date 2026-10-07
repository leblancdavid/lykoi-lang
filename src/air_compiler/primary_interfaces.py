"""Explicit primary value introduction and operation-context parameter authority."""
import copy

from .mutable_values import keys, require, valid_value, pipeline
from .references import erase

VERSION = "primary-value-interfaces-1"


def integrate(model, facts, fields, types, record, create):
    keys(facts, ("integers", "context_inputs"))
    for declaration in facts["integers"]:
        keys(declaration, ("name", "type", "creation", "migration"))
        n, typ, creation = declaration["name"], declaration["type"], declaration["creation"]
        require(type(n) is str and n.isidentifier() and n not in fields, "Fresh named primary integer")
        keys(typ, ("type", "domain", "nullable"))
        require(typ["type"] == "integer" and typ["domain"] == [] and type(typ["nullable"]) is bool, "Explicit signed-64 nullable domain")
        fid = "field:primary:" + n
        field = dict(id=fid, name=n, type="prim:integer", nullable=typ["nullable"])
        fields[n] = field; types[n] = copy.deepcopy(typ); record["fields"].append(field)
        command = next(c for c in model["commands"] if c.get("behavior") == create["id"])
        if creation.get("source") == "literal":
            keys(creation, ("source", "value"))
            require(valid_value(creation["value"], typ), "Signed-64 creation literal")
            assignment = dict(field=fid, source="literal", value=creation["value"])
        else:
            defaulted = creation.get("source") == "input_default"
            require(defaulted or creation.get("source") == "input", "Explicit creation input/default")
            keys(creation, ("source", "input", "pipeline", "error") + (("default",) if defaulted else ()))
            require(creation["input"] not in {i["name"] for i in create["inputs"]}, "Distinct primary input")
            pipeline(creation["pipeline"], typ)
            if defaulted: require(valid_value(creation["default"], typ), "Typed creation default")
            iid = "input:primary:" + n
            create["inputs"].append(dict(id=iid, name=creation["input"], type="prim:integer"))
            command["arguments"].append(dict(flag="--" + creation["input"].replace("_", "-"), input=iid, required=not defaulted))
            assignment = dict(field=fid, source=creation["source"], id=iid)
            if defaulted: assignment["value"] = creation["default"]
        create["assignments"].append(assignment)
        create["guarantees"].append(dict(id="guarantee:primary:" + n, kind="result_field_equals_assignment", field=fid))
        require(type(declaration["migration"]) is list, "Separate historical authority")
        for m in declaration["migration"]:
            keys(m, ("from", "to", "value"))
            require(type(m["from"]) is int and m["from"] >= 1 and m["to"] == m["from"] + 1 and valid_value(m["value"], typ), "Explicit additive integer migration")
            state = model["state"][0]
            state["schema_version"] = max(state["schema_version"], m["to"])
            prior = next((x for x in model["migrations"] if x["from_version"] == m["from"]), None)
            if prior is None:
                access = [x["id"] for x in model["capabilities"] if x["kind"] == "resource_access" and x["resource"] == state["storage"]]
                prior = dict(id="migration:primary:" + str(m["from"]), state=state["id"], from_version=m["from"], to_version=m["to"], add_fields=[], requires=access, effects=["state_read", "state_write", "file_read", "file_write"])
                model["migrations"].append(prior)
            prior["add_fields"].append(dict(field=fid, value=copy.deepcopy(m["value"])))
        require(model["state"][0]["schema_version"] == 1 or len(declaration["migration"]) == 1, "Historical value cannot derive from creation default")
    seen = set()
    for p in facts["context_inputs"]:
        keys(p, ("command", "name", "type", "role", "authority", "missing_error", "invalid_error"))
        require(p["authority"] == "explicit_parameter" and p["role"] == "actor", "No implicit authenticated actor, owner or referenced entity substitution")
        require(p["type"].get("type") == "identifier" and p["type"].get("domain") == [] and type(p["type"].get("entity")) is str, "Nominal actor domain")
        require(all(type(p[k]) is str and bool(p[k]) for k in ("name", "missing_error", "invalid_error")), "Explicit context parameter/errors")
        require((p["command"], p["name"]) not in seen, "Unique actor context")
        seen.add((p["command"], p["name"]))
        command = next((c for c in model["commands"] if c["token"] == p["command"] and "behavior" in c), None)
        if command:
            behavior = next(b for b in model["behaviors"] if b["id"] == command["behavior"])
            require(behavior["kind"] != "list" and p["name"] not in {i["name"] for i in behavior["inputs"]}, "Distinct write-operation context")
            iid = "input:context:" + p["command"] + ":" + p["name"]
            behavior["inputs"].append(dict(id=iid, name=p["name"], type="prim:string"))
            command["arguments"].append(dict(flag="--" + p["name"].replace("_", "-"), input=iid, required=False))


def contexts(facts, command):
    return {p["name"]: p["type"] for p in facts.get("primary_interfaces", {}).get("context_inputs", []) if p["command"] == command}
