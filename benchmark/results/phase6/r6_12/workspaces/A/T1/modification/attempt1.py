import json
import re
import sys


def keys(value, names):
    return type(value) is dict and set(value) == set(names)


def text(value, pattern):
    return type(value) is str and re.fullmatch(pattern, value) is not None


def integer(value, low, high):
    return type(value) is int and low <= value <= high


def run(request):
    shape = {"error": "shape", "at": -1}
    if not keys(request, ("stock", "ops")):
        return shape
    stock, ops = request["stock"], request["ops"]
    if type(stock) is not list or not 1 <= len(stock) <= 8:
        return shape
    if type(ops) is not list or len(ops) > 16:
        return shape
    for row in stock:
        if not (keys(row, ("sku", "qty")) and text(row["sku"], r"[A-Z]{1,4}")
                and integer(row["qty"], 0, 100)):
            return shape
    for op in ops:
        if type(op) is not dict or op.get("kind") not in ("reserve", "release", "ship", "resize"):
            return shape
        names = ("kind", "id", "sku", "n") if op["kind"] == "reserve" else ("kind", "id")
        if op["kind"] == "resize":
            names = ("kind", "id", "n")
        if not keys(op, names) or not text(op["id"], r"[a-z]{1,4}"):
            return shape
        if op["kind"] == "reserve" and not (text(op["sku"], r"[A-Z]{1,4}") and integer(op["n"], 1, 100)):
            return shape
        if op["kind"] == "resize" and not integer(op["n"], 1, 100):
            return shape
    if len({row["sku"] for row in stock}) != len(stock):
        return {"error": "duplicate_sku", "at": -1}
    state = {row["sku"]: dict(sku=row["sku"], free=row["qty"], held=0, shipped=0) for row in stock}
    holds, used = {}, set()
    for index, op in enumerate(ops):
        ident, kind = op["id"], op["kind"]
        error = None
        if kind == "reserve":
            if ident in used:
                error = "duplicate_id"
            elif op["sku"] not in state:
                error = "unknown_sku"
            elif state[op["sku"]]["free"] < op["n"]:
                error = "insufficient"
            else:
                row = state[op["sku"]]
                row["free"] -= op["n"]
                row["held"] += op["n"]
                holds[ident] = dict(id=ident, sku=op["sku"], n=op["n"])
                used.add(ident)
        elif ident not in holds:
            error = "unknown_hold"
        elif kind == "resize":
            hold = holds[ident]
            row = state[hold["sku"]]
            delta = op["n"] - hold["n"]
            if delta > row["free"]:
                error = "insufficient"
            else:
                row["free"] -= delta
                row["held"] += delta
                hold["n"] = op["n"]
        else:
            hold = holds.pop(ident)
            row = state[hold["sku"]]
            row["held"] -= hold["n"]
            row["free" if kind == "release" else "shipped"] += hold["n"]
        if error:
            return {"error": error, "at": index}
    return {"stock": [state[k] for k in sorted(state)], "holds": [holds[k] for k in sorted(holds)]}


if __name__ == "__main__":
    print(json.dumps(run(json.load(sys.stdin))))
