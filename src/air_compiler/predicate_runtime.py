"""Self-contained pure predicate interpreter inserted by normal lowering."""
from datetime import datetime


def predicate_value(o, record, inputs, stages, resources):
    k = o["kind"]
    if k == "literal":
        return o["value"]
    if k == "value":
        return stages[o["stage"]]
    return (record if k == "field" else inputs if k in ("parameter", "computed") else resources).get(o["name"])


def predicate_eval(tree, record=None, inputs=None, stages=None, resources=None):
    record, inputs, stages, resources = record or {}, inputs or {}, stages or {}, resources or {}
    k = tree["kind"]
    def ev(t):
        return predicate_eval(t, record, inputs, stages, resources)
    if k in ("and", "or"):
        values = [ev(c) for c in tree["children"]]  # all pure operands, no effects
        return all(values) if k == "and" else any(values)
    if k == "not":
        return not ev(tree["child"])
    if k == "present":
        o = tree["operand"]
        return o["stage"] in stages if o["kind"] == "value" else o["name"] in inputs
    def value(o):
        return predicate_value(o, record, inputs, stages, resources)
    if k == "is_null":
        return value(tree["operand"]) is None
    left, right = value(tree["left"]), value(tree["right"])
    if left is None or right is None:
        return False
    def normalized(v):
        if tree["left"]["type"]["type"] == "timestamp":
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        if tree["policy"]["normalization"] == "strip":
            v = v.strip()
        return v.casefold() if tree["policy"]["case"] == "casefold" else v
    left = normalized(left)
    if k == "member":
        return any(left == normalized(v) for v in right)
    right = normalized(right)
    op = tree["operator"]
    if op == "eq":
        return left == right
    if op == "lt":
        return left < right
    if op == "le":
        return left <= right
    if op == "gt":
        return left > right
    return left >= right
