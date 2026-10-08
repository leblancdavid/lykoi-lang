"""T2: bounded samples, conventional initial authoring."""
def solve(data):
    def reject(code, offset):
        return {'status': 'reject', 'code': code, 'offset': offset}
    if len(data) > 64:
        return reject('INPUT_LIMIT', 64)
    if not data:
        return reject('TRUNCATED', 0)
    if data[0] != ord('A'):
        return reject('SYNTAX', 0)
    values = []
    for offset, number in enumerate(data[1:], 1):
        if len(values) == 8:
            return reject('OCCURRENCE_LIMIT', offset)
        if number > 10:
            return reject('RANGE', offset)
        values.append(number)
    return {'status': 'success', 'value': values}
