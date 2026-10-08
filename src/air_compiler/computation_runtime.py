"""Lykoi-defined checked signed-64 and UTC fixed-second displacement."""
from datetime import timedelta, timezone
import re


def computation_value(source, rows, images, inputs, resources, values):
    k = source["kind"]
    if k == "literal": return copy.deepcopy(source["value"])
    if k == "cardinality":
        s = source["selection"]
        return sum(predicate_eval(s["predicate"], reference_fields({**({"primary": images["before"]} if images.get("before") else {}), s["binding"]: r}), inputs) for r in rows[s["entity"]])
    return copy.deepcopy((inputs if k == "parameter" else resources if k == "resource" else values if k == "computed" else images[k])[source["name"]])


def computation_evaluate(graph, rows, images, inputs, resources=None):
    values = {}
    for n in graph["nodes"]:
        try:
            args = [computation_value(s, rows, images, inputs, resources or {}, values) for s in n["operands"]]
            if any(not mutable_value_valid(v, s["type"]) for v, s in zip(args, n["operands"])):
                raise ValueError("operand domain")
            if n["operator"] == "value": result = args[0]
            elif n["operator"] == "add": result = args[0] + args[1]
            elif n["operator"] in ("refine_integer", "refine_instant"):
                if args[0] is None and n["null"]["policy"] == "reject": raise ValueError("null is not an integer")
                result = n["null"]["value"] if args[0] is None else args[0]
            elif n["operator"] == "days_to_seconds":
                # The exact scale and dimension are declared language meaning K26.
                result = args[0] * n["conversion"]["seconds_per_day"]
            else:
                # UTC instants only; elapsed SI-like seconds, no leap seconds,
                # timezone/DST/calendar months or implicit clock observation.
                if not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?Z", args[0]):
                    raise ValueError("canonical UTC instant required")
                instant = datetime.fromisoformat(args[0].replace("Z", "+00:00")).astimezone(timezone.utc)
                result = (instant + timedelta(seconds=args[1])).isoformat().replace("+00:00", "Z")
            if not mutable_value_valid(result, n["type"]): raise ValueError("result domain")
        except (ValueError, OverflowError, KeyError, TypeError):
            raise Failure(n["error"])
        values[n["binding"]] = result
    return values
