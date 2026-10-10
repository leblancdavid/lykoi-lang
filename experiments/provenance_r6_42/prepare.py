"""Verify inherited baseline, construct independent witnesses, freeze before execution."""
from datetime import datetime, timezone
import hashlib
from common import ROOT, HERE, OUT, c, read, save, sha, git, verify_files
from forms import compact, explicit, coordinates
from oracle import expected


def prepare():
    assert not (OUT / 'FREEZE.json').exists(), 'one immutable prospective freeze only'
    inherited = read(ROOT / 'benchmark/results/phase6/r6_41/BASELINE.json')['protected_files']
    verify_files(inherited)
    publications = {}
    protected = dict(inherited)
    for round_id in ('r6_32', 'r6_40', 'r6_41'):
        directory = ROOT / 'benchmark/results/phase6' / round_id
        manifest = directory / 'PUBLICATION-IDENTITIES.json'
        receipt = directory / 'VERIFICATION.json'
        items = read(manifest)['files']
        verify_files(items)
        assert read(receipt)['manifest_sha256'] == sha(manifest)
        assert read(receipt)['passed'] is True
        publications[round_id] = {'files': len(items), 'manifest_sha256': sha(manifest), 'receipt_sha256': sha(receipt)}
        for name, record in items.items():
            protected[name] = record['sha256']
        for path in (manifest, receipt):
            protected[path.relative_to(ROOT).as_posix()] = sha(path)
    kernel_path = 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json'
    kernel = read(ROOT / kernel_path)
    assert kernel['final_count'] == 26
    implementations = {name: digest for name, digest in protected.items()
                       if name.startswith(('src/', 'schema/', 'air/', 'generated/',
                           'experiments/semantic_interpreter/', 'experiments/typed_composition_r6_18/',
                           'experiments/lifecycle_r6_32/', 'experiments/semantic_adapter_r6_23/',
                           'experiments/semantic_contracts_r6_25/'))}
    assert any(name.startswith('src/') for name in implementations)
    save(OUT / 'BASELINE.json', {'head': git('rev-parse', 'HEAD'), 'initial_status': 'clean before R6.42 edits',
         'kernel': 26, 'kernel_accounting_sha256': sha(ROOT / kernel_path),
         'kernel_method': 'preserved accounting and byte-identical production; no new recount',
         'publications': publications, 'protected_files': protected, 'protected_count': len(protected),
         'implementation_identities': implementations, 'implementation_count': len(implementations),
         'historical_acceptance_rescored': False, 'verified_utc': datetime.now(timezone.utc).isoformat()})
    package = compact()
    exact, mapping, _ = explicit(package)
    flat, _, pairs = explicit(package, flat=True)
    save(OUT / 'COMPACT.json', package)
    save(OUT / 'EXACT.json', exact)
    save(OUT / 'FLAT.json', flat)
    save(OUT / 'EXPECTED-MAP.json', mapping)
    paths = coordinates(package)
    expansion_paths = {}
    for node in mapping:
        chain = []
        for side in ('left', 'right'):
            if node == paths[side] or node.startswith(paths[side] + '/'):
                chain.append({'call_local': side, 'definition': package['definitions'][1]['identity']})
                if node == paths[side + '_inner'] or node.startswith(paths[side + '_inner'] + '/'):
                    chain.append({'call_local': 'inner', 'definition': package['definitions'][0]['identity']})
        expansion_paths[node] = chain
    save(OUT / 'CORRESPONDENCE.json', {'flat_to_exact': pairs, 'symbolic_origins': mapping,
         'expansion_paths': expansion_paths, 'unpaired_exact_regions': [paths[s] for s in ('left', 'left_inner', 'right', 'right_inner')],
         'caller_check_sites': {'post_low': {'producer_region': paths['left'], 'consumer_node': paths['root'] + '/post_low'},
                                'post_high': {'producer_region': paths['right'], 'consumer_node': paths['root'] + '/post_high'}},
         'unsupported_fields': ['authored_text_line_column', 'expression_occurrence_identity', 'dynamic_integer_operand_lineage'],
         'flat_annotation_is_authorship_claim': False})
    inputs = [bytes([x, y]) for x in range(6) for y in range(6)] + [b'', b'\x02', b'\x02\x01\x00']
    rows = []
    for data in inputs:
        row = {'input_hex': data.hex(), 'forms': {}}
        for form in ('compact', 'exact', 'flat'):
            observation = expected(package, data, flat=form == 'flat')
            # Hand-derived totals are a separate sanity check, not learned from runtime.
            if len(data) == 2:
                code = observation['envelope'].get('error', {}).get('code', 'success')
                if code == 'INNER':
                    key = 'first' if data[0] > 3 else 'second'
                    total = {'first': (15, 13), 'second': (27, 21)}[key]
                else:
                    total = {'POST_LOW': (37, 29), 'POST_HIGH': (43, 35), 'success': (51, 43)}[code]
                assert observation['envelope']['work'] == total[form == 'flat']
            cutoffs = []
            for budget in range(observation['envelope']['work'] + 2):
                cutoff = expected(package, data, flat=form == 'flat', budget=budget)
                cutoffs.append({'budget': budget, 'envelope': cutoff['envelope'],
                                'trace_sha256': cutoff['trace_sha256'], 'checks': cutoff['checks']})
            row['forms'][form] = {**observation, 'cutoffs': cutoffs}
        rows.append(row)
    save(OUT / 'EXPECTATIONS.json', {'authority': 'CONTRACT-1.md and unchanged VM/R6.18 specification',
         'independence': 'semantics-derived before execution, same coordinator; not participant/output-derived',
         'domain': {'x': [0, 5], 'y': [0, 5], 'unique_pairs': 36, 'malformed_inputs': 3}, 'rows': rows})
    import copy
    body_tamper, pin_tamper = copy.deepcopy(package), copy.deepcopy(package)
    body_tamper['definitions'][0]['steps'][0]['node']['code'] = 'ALTERED'
    pin_tamper['program']['steps'][3]['node']['identity'] = '0' * 64
    controls = [
        {'label': 'wrong_returned_span_input_origin', 'expected': 'UNSUPPORTED_PROVENANCE',
         'claim': {'kind': 'error_offset', 'input_hex': '0000', 'form': 'compact', 'offset': 0}},
        {'label': 'authored_text_offset_claim', 'expected': 'UNSUPPORTED_PROVENANCE',
         'claim': {'kind': 'authored_text_line_column', 'node': paths['root'] + '/post_low', 'value': [1, 1]}},
        {'label': 'invented_integer_lineage', 'expected': 'UNSUPPORTED_PROVENANCE',
         'claim': {'kind': 'dynamic_integer_operand_lineage', 'node': paths['left'], 'value': [0]}},
        {'label': 'wrong_nested_path', 'expected': 'CORRESPONDENCE_REJECT',
         'claim': {'kind': 'node_origin', 'node': paths['left_inner'] + '/guard',
                   'origin': mapping[paths['left_inner'] + '/guard'],
                   'expansion_path': expansion_paths[paths['right_inner'] + '/guard']}},
        {'label': 'wrong_local_origin', 'expected': 'CORRESPONDENCE_REJECT',
         'claim': {'kind': 'node_origin', 'node': paths['left_inner'] + '/guard',
                   'origin': {'definition': package['definitions'][0]['identity'], 'local': 'sum'},
                   'expansion_path': expansion_paths[paths['left_inner'] + '/guard']}},
        {'label': 'missing_region_mapping', 'expected': 'CORRESPONDENCE_REJECT',
         'claim': {'kind': 'node_origin', 'node': paths['left'], 'origin': None, 'expansion_path': []}},
        {'label': 'wrong_flat_node_pair', 'expected': 'CORRESPONDENCE_REJECT',
         'claim': {'kind': 'flat_pair', 'node': 'flat/Entry/left_guard', 'exact_node': paths['right_inner'] + '/guard'}},
        {'label': 'identity_body_tampering', 'expected': 'IDENTITY', 'package': body_tamper},
        {'label': 'identity_call_pin_tampering', 'expected': 'IDENTITY', 'package': pin_tamper},
        {'label': 'full_flat_envelope_equivalence', 'expected': 'UNSUPPORTED_PROVENANCE',
         'claim': {'kind': 'full_flat_envelope_equivalence', 'input_hex': '0201'}}]
    save(OUT / 'CONTROL-EXPECTATIONS.json', controls)
    manifest = {'forms': {}, 'definition_pins': {d['name']: d['identity'] for d in package['definitions'] + [package['program']]},
                'execution_semantics_changed': False, 'frozen_before_candidate_execution': True}
    for name in ('COMPACT', 'EXACT', 'FLAT'):
        path = OUT / (name + '.json')
        manifest['forms'][name.lower()] = {'file': path.relative_to(ROOT).as_posix(), 'file_sha256': sha(path),
                                         'canonical_sha256': hashlib.sha256(c.canonical(read(path))).hexdigest()}
    save(OUT / 'REPRESENTATION-MANIFEST.json', manifest)
    files = list(HERE.glob('*.py')) + [HERE / 'CONTRACT-1.md'] + list(OUT.glob('*.json'))
    save(OUT / 'FREEZE.json', {'round': 'R6.42', 'frozen_utc': datetime.now(timezone.utc).isoformat(),
         'candidate_executions_before_freeze': 0, 'files': {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(files)}})
    print('R6.42 frozen:', len(protected), 'protected identities;', len(rows), 'inputs; three forms')


if __name__ == '__main__':
    prepare()
