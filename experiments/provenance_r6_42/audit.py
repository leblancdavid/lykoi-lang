"""Read-only analysis of first R6.42 results; no candidate executions or oracle repair."""
from collections import Counter
import gzip
import hashlib
from common import ROOT, OUT, c, read, save, sha, verify_files, verify_freeze


def differences(a, b, path='$'):
    if type(a) is not type(b):
        return [(path, a, b)]
    if type(a) is dict:
        if set(a) != set(b):
            return [(path + '/keys', sorted(a), sorted(b))]
        return [d for key in a for d in differences(a[key], b[key], path + '/' + key)]
    if type(a) is list:
        if len(a) != len(b):
            return [(path + '/length', len(a), len(b))]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in differences(x, y, path + '/' + str(i))]
    return [] if a == b else [(path, a, b)]


def audit():
    verify_freeze()
    baseline = read(OUT / 'BASELINE.json')
    verify_files(baseline['protected_files'])
    evidence = read(OUT / 'DIFFERENTIAL.json')
    discrepancy_labels = Counter(d['label'] for d in evidence['discrepancies'])
    default_fields, differences_by_field = Counter(), Counter()
    examples, default_totals = {}, Counter()
    for failure in evidence['discrepancies']:
        if failure['label'] == 'default_oracle':
            expected, actual = failure['detail']['expected'], failure['detail']['actual']
            for field in expected:
                if expected[field] != actual[field]:
                    default_fields[field] += 1
            for path, wanted, observed in differences(expected['trace'], actual['trace']):
                category = '/'.join(path.split('/')[2:])
                differences_by_field[category] += 1
                examples.setdefault(category, {'input_hex': failure['detail']['input'],
                                              'form': failure['detail']['form'], 'path': path,
                                              'frozen_expected': wanted, 'observed': observed})
    expected_rows = {r['input_hex']: r for r in read(OUT / 'EXPECTATIONS.json')['rows']}
    full_exact_agreements, functional_agreements, raw_offset_differences = 0, 0, 0
    all_work_equal_expected, all_envelopes_equal_expected, all_checks_equal_expected = True, True, True
    for repeat in evidence['passes']:
        for row in repeat['rows']:
            forms = row['forms']
            full_exact_agreements += forms['compact'] == forms['exact']
            a, f = forms['compact']['envelope'], forms['flat']['envelope']
            if a['status'] == 'success':
                same_function = all(a[k] == f[k] for k in ('status', 'value', 'output', 'consumed'))
            else:
                same_function = a['status'] == f['status'] and all(a['error'][k] == f['error'][k] for k in ('code', 'stage'))
                same_function = same_function and forms['compact']['checks'] == forms['flat']['checks']
                raw_offset_differences += a['error']['offset'] != f['error']['offset']
            functional_agreements += same_function
            for form, observed in forms.items():
                frozen = expected_rows[row['input_hex']]['forms'][form]
                all_envelopes_equal_expected &= observed['envelope'] == frozen['envelope']
                all_work_equal_expected &= observed['envelope']['work'] == frozen['envelope']['work']
                all_checks_equal_expected &= observed['checks'] == frozen['checks']
                if repeat['pass'] == 1 and form == 'compact':
                    default_totals[observed['envelope'].get('error', {}).get('code', 'success')] += 1
    cutoff_matches, cutoff_exact_pairs, cutoff_diff_examples = Counter(), 0, []
    for row in evidence['cutoffs']:
        data = row['input_hex']
        for form, cutoffs in row['forms'].items():
            wanted = expected_rows[data]['forms'][form]['cutoffs']
            for observed, frozen in zip(cutoffs, wanted):
                for field in ('envelope', 'checks', 'trace_sha256'):
                    cutoff_matches[field] += observed[field] == frozen[field]
        for a, e in zip(row['forms']['compact'], row['forms']['exact']):
            cutoff_exact_pairs += a == e
        for a, f in zip(row['forms']['compact'], row['forms']['flat']):
            if a['envelope'] != f['envelope'] and len(cutoff_diff_examples) < 12 and data == '0201':
                cutoff_diff_examples.append({'input_hex': data, 'budget': a['budget'],
                                            'compact': a['envelope'], 'flat': f['envelope']})
    # Inspect exact source authority without changing any expectation or executing again.
    save(OUT / 'DISCREPANCY-ANALYSIS.json', {
        'method': 'read-only first-result comparison; no rerun, repair or rescoring',
        'discrepancy_labels': dict(discrepancy_labels), 'default_mismatched_fields': dict(default_fields),
        'default_trace_difference_categories': dict(differences_by_field), 'examples': examples,
        'root_cause': 'oracle expected raw-byte origins on numeric UInt8 Cells; VM decode returns Cell(v,x.start,x.end) with default empty origins',
        'authority': 'experiments/semantic_interpreter/interpreter.py lines348-354 and Cell default line10',
        'default_outcomes_per_form_per_pass': dict(default_totals),
        'compact_exact_full_default_agreements': full_exact_agreements, 'default_pair_comparisons': 78,
        'flat_functional_default_agreements': functional_agreements,
        'default_raw_offset_differences_two_passes': raw_offset_differences,
        'all_default_envelopes_equal_frozen': all_envelopes_equal_expected,
        'all_default_work_equal_frozen': all_work_equal_expected,
        'all_default_check_entry_order_equal_frozen': all_checks_equal_expected,
        'cutoff_observations': evidence['cutoff_observations'], 'cutoff_matches': dict(cutoff_matches),
        'compact_exact_cutoff_pairs_equal': cutoff_exact_pairs,
        'equal_budget_representation_difference_examples': cutoff_diff_examples,
        'classification_unchanged': read(OUT / 'RESULT.json')['classification'],
        'full_acceptance_claim': False, 'remaining_qualification_blocker': 'frozen intermediate numeric-origin expectation failure'})
    archives = {}
    for name in ('DIFFERENTIAL.json', 'ADVERSARIAL.json'):
        path = OUT / name
        raw = path.read_bytes()
        archive = OUT / (name + '.gz')
        with archive.open('xb') as target:
            target.write(gzip.compress(raw, mtime=0))
        assert gzip.decompress(archive.read_bytes()) == raw
        archives[name] = {'raw_sha256': hashlib.sha256(raw).hexdigest(), 'raw_bytes': len(raw),
                          'archive': archive.relative_to(ROOT).as_posix(), 'archive_sha256': sha(archive),
                          'archive_bytes': archive.stat().st_size, 'lossless_original_bytes_verified': True}
    save(OUT / 'RAW-ARCHIVES.json', {'files': archives, 'method': 'original JSON bytes retained losslessly in gzip; local originals unchanged'})
    print('First-result audit:', dict(discrepancy_labels))
    print('Default fields:', dict(default_fields), 'trace details:', dict(differences_by_field))
    print('Compact/exact default:', full_exact_agreements, '/78; flat functional:', functional_agreements, '/78')
    print('Cutoffs:', dict(cutoff_matches), 'exact pairs:', cutoff_exact_pairs)
    print('Outcome counts:', dict(default_totals))
    print('Raw archive byte sizes:', {k: (v['raw_bytes'], v['archive_bytes']) for k, v in archives.items()})


if __name__ == '__main__':
    audit()
