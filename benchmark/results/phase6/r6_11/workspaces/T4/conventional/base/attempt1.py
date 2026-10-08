"""T4: ordered ASCII preflight, configuration structure, then range."""
def solve(data):
    def reject(code, offset):
        return {'status': 'reject', 'code': code, 'offset': offset}
    if len(data) > 64:
        return reject('INPUT_LIMIT', 64)
    for offset, byte in enumerate(data):
        if byte > 127:
            return reject('ENCODING', offset)
    if not data:
        return reject('TRUNCATED', 0)
    if data.startswith(b'on:'):
        enabled, cursor = True, 3
    elif data.startswith(b'off:'):
        enabled, cursor = False, 4
    else:
        return reject('SYNTAX', 0)
    if cursor == len(data):
        return reject('TRUNCATED', cursor)
    if not 48 <= data[cursor] <= 57:
        return reject('DIGIT', cursor)
    number = data[cursor] - 48
    if cursor + 1 == len(data):
        return reject('TRUNCATED', len(data))
    if data[cursor + 1] != 10:
        return reject('SYNTAX', cursor + 1)
    if cursor + 2 < len(data):
        return reject('TRAILING', cursor + 2)
    if number > 5:
        return reject('RANGE', cursor)
    return {'status': 'success', 'value': {'enabled': enabled, 'limit': number}}
