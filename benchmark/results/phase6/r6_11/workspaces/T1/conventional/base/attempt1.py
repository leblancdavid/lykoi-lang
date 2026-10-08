"""T1: two-channel aggregation, conventional initial authoring."""
def solve(data):
    if len(data) > 64:
        return {'status': 'reject', 'code': 'INPUT_LIMIT', 'offset': 64}
    if len(data) < 2:
        return {'status': 'reject', 'code': 'TRUNCATED', 'offset': len(data)}
    if len(data) > 2:
        return {'status': 'reject', 'code': 'TRAILING', 'offset': 2}
    x, y = data
    return {'status': 'success', 'value': {'left': x, 'right': y, 'total': x + y}}
