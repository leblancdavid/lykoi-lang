"""Trusted query backend template: standalone standard-library JSON subprocess."""
import argparse
import copy
import json
import sys
from pathlib import Path


class ApplicationError(Exception):
    pass


def matches_type(value, kind):
    return ((kind == "string" and type(value) is str) or
            (kind == "integer" and type(value) is int) or
            (kind == "boolean" and type(value) is bool) or
            (kind == "strings" and type(value) is list and all(type(x) is str for x in value)))


def execute(model, records, inputs):
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

    pred = model["predicate"]
    operand = pred["operand"]
    target = inputs[operand["parameter"]] if "parameter" in operand else operand["constant"]
    def compare_value(value):
        if model["comparison"]["normalization"] == "strip":
            value = value.strip()
        if model["comparison"]["case"] == "casefold":
            value = value.casefold()
        return value
    target = compare_value(target)
    selected = []
    for record in records:
        values = record[pred["field"]] if pred["operator"] == "contains" else [record[pred["field"]]]
        if not any(compare_value(v) == target for v in values):
            continue
        if any(rule["mode"] == "equals" and record[rule["field"]] != rule["value"] for rule in model["inclusion"]):
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


def main(model):
    parser = argparse.ArgumentParser()
    parser.add_argument("--store", required=True)
    for name in model["parameters"]:
        parser.add_argument("--" + name, required=True)
    args = vars(parser.parse_args())
    path = Path(args.pop("store"))
    try:
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
