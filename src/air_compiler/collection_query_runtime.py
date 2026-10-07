"""Trusted query backend template: standalone standard-library JSON subprocess."""
import argparse
import copy
import json
import sys
from datetime import datetime
from pathlib import Path

if __package__:
    from .predicate_runtime import predicate_eval


class ApplicationError(Exception):
    pass


def matches_type(value, kind):
    return ((kind == "string" and type(value) is str) or
            (kind == "integer" and type(value) is int) or
            (kind == "boolean" and type(value) is bool) or
            (kind == "strings" and type(value) is list and all(type(x) is str for x in value)))


def execute(model, records, inputs, *, providers=None):
    if model["predicate"].get("result_type") == "boolean":
        resources = prepare_query(model, inputs, providers=providers)
        return execute_predicate_query(model, records, inputs, resources=resources)
    # Input validation precedes selection and never rewrites the parameter value.
    if set(inputs) != set(model["parameters"]) or any(type(v) is not str for v in inputs.values()):
        raise ApplicationError("invalid_input")
    for rule in model["validation"]:
        value = inputs[rule["parameter"]]
        if (rule["rule"] == "nonempty" and value == "") or (rule["rule"] == "nonblank" and not value.strip()):
            raise ApplicationError(rule["error"])
    fields = model["source"]["fields"]
    identity = model["source"]["unique_key"]
    if type(records) is not list:
        raise ApplicationError("invalid_state")
    seen = set()
    for record in records:
        if (type(record) is not dict or set(record) != set(fields) or
                any(not matches_type(record[k], v) for k, v in fields.items()) or record[identity] in seen):
            raise ApplicationError("invalid_state")
        seen.add(record[identity])

    pred = legacy_predicate(model)
    selected = []
    for record in records:
        if not predicate_eval(pred, record, inputs):
            continue
        selected.append(copy.deepcopy(record))
    # Stable sorts from least to most significant key preserve key precedence.
    for key in reversed(model["ordering"]):
        selected.sort(key=lambda r: r[key["field"]], reverse=key["direction"] == "DESC")
    if not selected:
        behavior = model["result"]["no_match"]
        if behavior == "error":
            raise ApplicationError(model["result"]["error"])
        if behavior == "null":
            return None
    return selected


def legacy_predicate(model):
    """Compatibility query facts normalize into the common algebra, never prose."""
    string = dict(type="string", domain=[])
    def typ(k):
        return dict(type="collection", element=string, ordering="insertion", duplicates="allow", equality="exact") if k == "strings" else dict(type=k, domain=[])
    def field(n):
        return dict(kind="field", name=n, type=typ(model["source"]["fields"][n]))
    p, policy = model["predicate"], model["comparison"]
    o = p["operand"]
    operand = dict(kind="parameter", name=o["parameter"], type=string) if "parameter" in o else dict(kind="literal", value=o["constant"], type=string)
    contains = p["operator"] == "contains"
    tree = dict(kind="member" if contains else "compare", result_type="boolean", operator="in" if contains else "eq", left=operand if contains else field(p["field"]), right=field(p["field"]) if contains else operand, policy=policy, nulls="false")
    children = [tree]
    for rule in model["inclusion"]:
        if rule["mode"] == "equals":
            children.append(dict(kind="compare", result_type="boolean", operator="eq", left=field(rule["field"]), right=dict(kind="literal", type=field(rule["field"])["type"], value=rule["value"]), policy=dict(case="sensitive", normalization="none"), nulls="false"))
    return tree if len(children) == 1 else dict(kind="and", result_type="boolean", children=children)


def predicate_matches_type(v, t):
    if v is None:
        return t.get("nullable", False)
    k = t["type"]
    if k == "collection":
        return (type(v) is list and all(predicate_matches_type(x, t["element"]) for x in v)
                and (t["duplicates"] == "allow" or len({json.dumps(x) for x in v}) == len(v)))
    if k == "boolean":
        return type(v) is bool
    if type(v) is not str:
        return False
    if k == "enum":
        return v in t["domain"]
    if k == "timestamp":
        if not v.endswith("Z"):
            return False
        try:
            datetime.fromisoformat(v.replace("Z", "+00:00"))
            return True
        except ValueError:
            return False
    return k in ("string", "identifier")


def prepare_query(model, inputs, *, providers=None):
    if not set(inputs) <= set(model["parameters"]):
        raise ApplicationError("invalid_input")
    for n, t in model["parameters"].items():
        errors = model.get("parameter_errors", {}).get(n, {})
        if n not in inputs:
            if errors.get("missing") == {"kind": "cli_rejection"}:
                raise ValueError("Required external query input: " + n)
            raise ApplicationError(errors.get("missing", "invalid_input"))
        if not predicate_matches_type(inputs[n], t):
            raise ApplicationError(errors.get("invalid", "invalid_input"))
    for rule in model["validation"]:
        value = inputs[rule["parameter"]]
        if (rule["rule"] == "nonempty" and value == "") or (rule["rule"] == "nonblank" and not value.strip()):
            raise ApplicationError(rule["error"])
    providers = {} if providers is None else providers
    allowed = {r["capability"] for r in model.get("resources", [])}
    if type(providers) is not dict or not set(providers) <= allowed or not all(callable(p) for p in providers.values()):
        raise ValueError("Providers bind declared query clock capabilities only")
    sampled, resources = {}, {}
    for r in model.get("resources", []):
        cid = r["capability"]
        if cid not in sampled:
            if cid in providers:
                sampled[cid] = providers[cid]()
            elif "SPEC" in globals():
                if by_id("capabilities", cid)["kind"] != "utc_clock":
                    raise ApplicationError("invalid_state")
                sampled[cid] = value_of(dict(source="capability", id=cid), {})
            else:
                raise ApplicationError("invalid_state")
        if not predicate_matches_type(sampled[cid], r["type"]):
            raise ApplicationError("invalid_state")
        resources[r["name"]] = sampled[cid]
    for pre in model.get("preconditions", []):
        if not predicate_eval(pre["predicate"], inputs=inputs, resources=resources):
            raise ApplicationError(pre["error"])
    return resources


def execute_predicate_query(model, records, inputs, *, resources=None):
    if resources is None:
        resources = prepare_query(model, inputs)
    fields, identity = model["source"]["fields"], model["source"]["unique_key"]
    if type(records) is not list:
        raise ApplicationError("invalid_state")
    seen = set()
    for r in records:
        if type(r) is not dict or set(r) != set(fields) or any(not predicate_matches_type(r[n], t) for n, t in fields.items()) or r[identity] in seen:
            raise ApplicationError("invalid_state")
        seen.add(r[identity])
    selected = [copy.deepcopy(r) for r in records if predicate_eval(model["predicate"], r, inputs, resources=resources)]
    for key in reversed(model["ordering"]):
        selected.sort(key=lambda r: datetime.fromisoformat(r[key["field"]].replace("Z", "+00:00")) if fields[key["field"]]["type"] == "timestamp" else r[key["field"]], reverse=key["direction"] == "DESC")
    if not selected:
        if model["result"]["no_match"] == "error":
            raise ApplicationError(model["result"]["error"])
        if model["result"]["no_match"] == "null":
            return None
    return selected


def main(model):
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", required=True)
    for name in model["parameters"]:
        parser.add_argument("--" + name, required=name not in model.get("parameter_errors", {}) or model["parameter_errors"][name]["missing"] == {"kind": "cli_rejection"}, default=argparse.SUPPRESS)
    args = vars(parser.parse_args())
    path = Path(args.pop("store"))
    try:
        if model["predicate"].get("result_type") == "boolean":
            for name, typ in model["parameters"].items():
                if name in args and typ["type"] in ("collection", "boolean"):
                    try:
                        args[name] = json.loads(args[name])
                    except ValueError:
                        raise ApplicationError("invalid_input")
        # Read only: no mkdir, migration, initialization or write path exists.
        records = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
        result = execute(model, records, args)
        print(json.dumps(result, ensure_ascii=False))
    except (OSError, ValueError):
        print(json.dumps({"error": "invalid_state"}), file=sys.stderr)
        sys.exit(1)
    except ApplicationError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        sys.exit(1)
