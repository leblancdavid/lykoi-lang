"""T3: ordered disjoint windows, base contract."""


def solve(data: bytes):
    if len(data) > 64:
        return {"status": "reject", "code": "INPUT_LIMIT", "offset": 64}
    windows = []
    position = 0
    while position < len(data):
        if len(windows) == 8:
            return {"status": "reject", "code": "OCCURRENCE_LIMIT", "offset": 16}
        start_position = position
        start = data[position]
        if start > 15:
            return {"status": "reject", "code": "RANGE", "offset": position}
        position += 1
        if position == len(data):
            return {"status": "reject", "code": "TRUNCATED", "offset": position}
        end = data[position]
        if end > 15:
            return {"status": "reject", "code": "RANGE", "offset": position}
        position += 1
        if start > end:
            return {"status": "reject", "code": "ORDER", "offset": start_position}
        if any(window["end"] > start for window in windows):
            return {"status": "reject", "code": "OVERLAP", "offset": start_position}
        windows.append({"start": start, "end": end})
    return {
        "status": "success",
        "value": windows,
        "output": (bytes((len(windows),)) + data).hex(),
    }
