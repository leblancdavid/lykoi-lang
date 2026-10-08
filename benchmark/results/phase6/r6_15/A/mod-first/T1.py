"""T1: saturating calibration with staged superboost extension."""


def solve(data: bytes):
    if len(data) > 64:
        return {"status": "reject", "code": "INPUT_LIMIT", "offset": 64}
    if not data:
        return {"status": "reject", "code": "TRUNCATED", "offset": 0}
    mode = data[0]
    if mode not in (0, 1, 2):
        return {"status": "reject", "code": "MODE", "offset": 0}
    if len(data) < 3:
        return {"status": "reject", "code": "TRUNCATED", "offset": len(data)}
    if len(data) > 3:
        return {"status": "reject", "code": "TRAILING", "offset": 3}
    raw = data[1] + data[2] + 10 * mode
    amount = min(raw, 200)
    clipped = raw > 200
    return {
        "status": "success",
        "value": {"amount": amount, "clipped": clipped},
        "output": bytes((amount, int(clipped))).hex(),
    }
