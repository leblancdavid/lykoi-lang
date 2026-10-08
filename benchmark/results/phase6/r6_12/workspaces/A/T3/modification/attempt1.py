import functools
import json
import operator
import re
import sys


def run(request):
    if type(request) is not dict or set(request) != {"hex", "action"}:
        return {"error": "shape"}
    value = request["hex"]
    if (type(value) is not str or len(value) > 180 or len(value) % 2
            or re.fullmatch(r"[0-9a-fA-F]*", value) is None
            or request["action"] not in ("normalize", "prune", "coalesce")):
        return {"error": "shape"}
    data = bytes.fromhex(value)
    if len(data) < 2:
        return {"error": "short_header"}
    if data[0] != 1:
        return {"error": "version"}
    if data[1] > 8:
        return {"error": "count"}
    records, pos = [], 2
    for _ in range(data[1]):
        if pos + 2 > len(data):
            return {"error": "truncated"}
        tag, length = data[pos:pos + 2]
        if tag > 2:
            return {"error": "tag"}
        if length > 8:
            return {"error": "length"}
        end = pos + 2 + length
        if end >= len(data):
            return {"error": "truncated"}
        if functools.reduce(operator.xor, data[pos:end], 0) != data[end]:
            return {"error": "checksum"}
        records.append((tag, data[pos + 2:end]))
        pos = end + 1
    if pos != len(data):
        return {"error": "trailing"}
    normalized = []
    for tag, payload in records:
        if tag == 1:
            payload = payload[::-1]
        elif tag == 2:
            payload = bytes(sorted(payload))
        if request["action"] == "prune" and not payload:
            continue
        normalized.append((tag, payload))
    if request["action"] == "coalesce":
        coalesced = []
        for tag, payload in normalized:
            if (coalesced and coalesced[-1][0] == tag
                    and len(coalesced[-1][1]) + len(payload) <= 8):
                coalesced[-1] = (tag, coalesced[-1][1] + payload)
            else:
                coalesced.append((tag, payload))
        normalized = coalesced
    result = bytearray((1, len(normalized)))
    for tag, payload in normalized:
        record = bytes((tag, len(payload))) + payload
        result.extend(record)
        result.append(functools.reduce(operator.xor, record, 0))
    return {"hex": result.hex(), "records": len(normalized),
            "payloadBytes": sum(len(payload) for _, payload in normalized)}


if __name__ == "__main__":
    print(json.dumps(run(json.load(sys.stdin))))
