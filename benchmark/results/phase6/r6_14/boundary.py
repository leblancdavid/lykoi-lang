"""Transparent integer-to-byte input boundary; no relation calculation."""
def pack(arguments, arity):
    if len(arguments) != arity:
        return None, dict(code='MISSING' if len(arguments)<arity else 'ARITY', index=min(len(arguments),arity))
    for index, value in enumerate(arguments):
        if type(value) is not int:
            return None, dict(code='TYPE', index=index)
        if not 0 <= value <= 255:
            return None, dict(code='RANGE', index=index)
    return bytes(arguments), None
