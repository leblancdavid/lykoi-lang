"""T2 base contract: ordered bounded run expansion."""


def solve(data: bytes):
    if len(data) > 64:
        return {"status": "reject", "code": "INPUT_LIMIT", "offset": 64}
    if not data:
        return {"status": "reject", "code": "TRUNCATED", "offset": 0}
    if data[0] != 1:
        return {"status": "reject", "code": "VERSION", "offset": 0}
    values = []
    position = 1
    records = 0
    while position < len(data):
        if records == 8:
            return {"status": "reject", "code": "OCCURRENCE_LIMIT", "offset": 17}
        count = data[position]
        if count > 4:
            return {"status": "reject", "code": "RUN", "offset": position}
        position += 1
        if position == len(data):
            return {"status": "reject", "code": "TRUNCATED", "offset": position}
        values.extend([data[position]] * count)
        position += 1
        records += 1
    return {"status": "success", "value": values, "output": bytes(values).hex()}
