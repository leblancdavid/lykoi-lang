"""T4 base contract: bounded nesting trace."""


def solve(data: bytes):
    if len(data) > 64:
        return {"status": "reject", "code": "INPUT_LIMIT", "offset": 64}
    depth = 0
    pairs = 0
    for position, symbol in enumerate(data):
        if position == 8:
            return {"status": "reject", "code": "OCCURRENCE_LIMIT", "offset": 8}
        if symbol == 40:
            depth += 1
            if depth > 2:
                return {"status": "reject", "code": "DEPTH", "offset": position}
        elif symbol == 41:
            if depth == 0:
                return {"status": "reject", "code": "UNDERFLOW", "offset": position}
            depth -= 1
            pairs += 1
        else:
            return {"status": "reject", "code": "SYNTAX", "offset": position}
    if depth:
        return {"status": "reject", "code": "UNCLOSED", "offset": len(data)}
    return {"status": "success", "value": {"pairs": pairs}, "output": bytes([pairs]).hex()}
