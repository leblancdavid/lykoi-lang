"""T3: structure, uniqueness, then ordered selection."""
def solve(data):
    def reject(code, offset):
        return {'status': 'reject', 'code': code, 'offset': offset}
    if len(data) > 64:
        return reject('INPUT_LIMIT', 64)
    records = []
    for offset in range(0, len(data), 2):
        if len(records) == 8:
            return reject('OCCURRENCE_LIMIT', offset)
        if offset + 1 == len(data):
            return reject('TRUNCATED', len(data))
        records.append({'id': data[offset], 'priority': data[offset + 1]})
    seen = set()
    for index, record in enumerate(records):
        if record['id'] in seen:
            return reject('DUPLICATE', 2 * index)
        seen.add(record['id'])
    return {'status': 'success', 'value': [r for r in records if r['priority'] <= 5]}
