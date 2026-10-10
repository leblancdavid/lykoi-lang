"""Prospective expectations from specifications; no candidate execution imports."""
from datetime import datetime, timezone
from common import ROOT, HERE, OUT, OLD, read, sha, save, verify, git


def locations(package):
    guarded, nested = package['definitions']
    root = 'program/' + package['program']['identity']
    paths = {'root': root}
    for side in ('left', 'right'):
        paths[side] = root + '/' + side + '/' + nested['identity']
        paths[side + '_inner'] = paths[side] + '/inner/' + guarded['identity']
    return paths


def wanted(data, paths, flat):
    p = 'flat/Entry' if flat else paths['root']
    cells, decodes = [], []

    def cell(node, value, span):
        cells.append({'node': node, 'value': value, 'span': span, 'origins': []})

    def outcome(code, offset, node, work):
        return {'status': 'reject', 'code': code, 'offset': offset, 'node': node,
                'stage': 'structure' if code in ('TRUNCATED', 'TRAILING') else 'validation',
                'work': work, 'cells': cells, 'decodes': decodes}

    for index, key in enumerate(('x', 'y')):
        if len(data) <= index:
            return outcome('TRUNCATED', index, p + '/' + key, 2 if index == 0 else 5)
        span = [index, index + 1]
        decodes.append({'node': p + '/' + key, 'value': data[index], 'span': span,
                        'raw_origins': [index], 'numeric_origins': []})
        cell(p + '/' + key, data[index], span)
    if len(data) > 2:
        return outcome('TRAILING', 2, p + '/end', 8)
    cell(p + '/end', None, [2, 2])
    values = []
    for index, side in enumerate(('left', 'right')):
        g = paths[side + '_inner']
        guard = p + '/' + side + '_guard' if flat else g + '/guard'
        if data[index] > 3:
            return outcome('INNER', index, guard,
                           ((13, 21) if flat else (15, 27))[index])
        cell(guard, None, [2, 2])
        val = data[index] + 1
        cell(p + '/' + side if flat else g + '/sum', val, [index, index + 1])
        if not flat:
            cell(g, val, [2, 2])
            cell(paths[side], val, [2, 2])
        values.append(val)
    if values[0] < 3:
        return outcome('POST_LOW', 0 if flat else 2, p + '/post_low', 29 if flat else 37)
    cell(p + '/post_low', None, [2, 2])
    if sum(values) > 6:
        return outcome('POST_HIGH', 1 if flat else 2, p + '/post_high', 35 if flat else 43)
    cell(p + '/post_high', None, [2, 2])
    val = sum(values)
    cell(p + '/total', val, [0, 1] if flat else [2, 2])
    cell(p, val, [0, 2])
    cell(p + '/encode', None, [2, 2])
    return {'status': 'success', 'value': val, 'output_hex': val.to_bytes(2, 'big').hex(),
            'span': [0, 2], 'origins': [], 'consumed': 2, 'work': 43 if flat else 51,
            'cells': cells, 'decodes': decodes}


def prepare():
    assert not (OUT / 'FREEZE.json').exists()
    protected = dict(read(OLD / 'BASELINE.json')['protected_files'])
    publications = {}
    for name in ('r6_32', 'r6_40', 'r6_41', 'r6_42'):
        directory = ROOT / 'benchmark/results/phase6' / name
        manifest, receipt = directory / 'PUBLICATION-IDENTITIES.json', directory / 'VERIFICATION.json'
        records = read(manifest)['files']
        verify(records)
        assert read(receipt)['passed'] and read(receipt)['manifest_sha256'] == sha(manifest)
        publications[name] = {'files': len(records), 'manifest_sha256': sha(manifest),
                              'receipt_sha256': sha(receipt)}
        protected.update({k: v['sha256'] for k, v in records.items()})
        for path in (manifest, receipt):
            protected[path.relative_to(ROOT).as_posix()] = sha(path)
    # Preserve local raw evidence without interpreting or rescoring it.
    for name, record in read(OLD / 'RAW-ARCHIVES.json')['files'].items():
        path = OLD / name
        assert sha(path) == record['raw_sha256']
        protected[path.relative_to(ROOT).as_posix()] = sha(path)
    verify(protected)
    kernel = 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json'
    assert read(ROOT / kernel)['final_count'] == 26
    save('BASELINE.json', {'head': git('rev-parse', 'HEAD'), 'initial_status': 'clean before edits',
         'protected_files': protected, 'protected_count': len(protected), 'publications': publications,
         'kernel': 26, 'kernel_accounting_sha256': sha(ROOT / kernel),
         'method': 'inherited hash chain plus R6.42 publication and raw originals; no rescoring',
         'created_utc': datetime.now(timezone.utc).isoformat()})
    package = read(OLD / 'COMPACT.json')
    paths = locations(package)
    inputs = [bytes([a, b]) for a in range(6) for b in range(6)] + [b'', b'\x02', b'\x02\x01\x00']
    save('EXPECTATIONS.json', {'version': 'r6_43-observation-1', 'paths': paths,
         'authority': 'unchanged semantic specifications and frozen implementation, not R6.42 outputs',
         'review_independence': 'candidate-output-independent; same coordinator, not independent cognition',
         'budgets': [0, 13, 43, 51],
         'rows': [{'input_hex': data.hex(), 'forms': {form: wanted(data, paths, form == 'flat')
                  for form in ('compact', 'exact', 'flat')}} for data in inputs]})
    from review import review
    save('PREEXECUTION-REVIEW.json', review())
    files = list(HERE.glob('*.py')) + [HERE / 'OBSERVATION-1.md', OUT / 'BASELINE.json',
                                     OUT / 'EXPECTATIONS.json', OUT / 'PREEXECUTION-REVIEW.json']
    files += [OLD / name for name in ('COMPACT.json', 'EXACT.json', 'FLAT.json',
                                     'EXPECTED-MAP.json', 'CORRESPONDENCE.json')]
    save('FREEZE.json', {'round': 'R6.43', 'candidate_executions_before_freeze': 0,
         'frozen_utc': datetime.now(timezone.utc).isoformat(),
         'files': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(files)}})
    print('Frozen R6.43:39 inputs;', len(protected), 'protected files; review precedes execution')


if __name__ == '__main__':
    prepare()
