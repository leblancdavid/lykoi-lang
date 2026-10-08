import json
import re
import sys


def hex_string(value, limit):
    return (type(value) is str and len(value) <= limit and len(value) % 2 == 0
            and re.fullmatch(r"[0-9a-fA-F]*", value) is not None)


def conflict(a, b):
    start_a, old_a, _ = a
    start_b, old_b, _ = b
    end_a, end_b = start_a + len(old_a), start_b + len(old_b)
    if not old_a and not old_b:
        return start_a == start_b
    if not old_a:
        return start_b <= start_a < end_b
    if not old_b:
        return start_a <= start_b < end_a
    return max(start_a, start_b) < min(end_a, end_b)


def run(request):
    shape = {"error": "shape", "at": -1}
    if type(request) is not dict or set(request) != {"hex", "patches"}:
        return shape
    if not hex_string(request["hex"], 64):
        return shape
    patches = request["patches"]
    if type(patches) is not list or len(patches) > 16:
        return shape
    for patch in patches:
        if type(patch) is not dict or set(patch) != {"at", "old", "new", "when"}:
            return shape
        if not (type(patch["at"]) is int and 0 <= patch["at"] <= 32
                and hex_string(patch["old"], 16) and hex_string(patch["new"], 16)
                and patch["when"] in ("always", "match", "absent")):
            return shape
    data = bytes.fromhex(request["hex"])
    decoded = [(p["at"], bytes.fromhex(p["old"]), bytes.fromhex(p["new"])) for p in patches]
    for i, (at, old, new) in enumerate(decoded):
        if at + len(old) > len(data):
            return {"error": "bounds", "at": i}
    applied, skipped = [], []
    for i, (at, old, new) in enumerate(decoded):
        matches = data[at:at + len(old)] == old
        if patches[i]["when"] == "absent":
            (skipped if matches else applied).append(i)
        elif matches:
            applied.append(i)
        elif patches[i]["when"] == "always":
            return {"error": "mismatch", "at": i}
        else:
            skipped.append(i)
    for position, i in enumerate(applied):
        for j in applied[position + 1:]:
            if conflict(decoded[i], decoded[j]):
                return {"error": "conflict", "at": i, "other": j}
    result, cursor = bytearray(), 0
    for i in sorted(applied, key=lambda i: decoded[i][0]):
        at, old, new = decoded[i]
        result.extend(data[cursor:at])
        result.extend(new)
        cursor = at + len(old)
    result.extend(data[cursor:])
    return {"hex": result.hex(), "applied": applied, "skipped": skipped}


if __name__ == "__main__":
    print(json.dumps(run(json.load(sys.stdin))))
