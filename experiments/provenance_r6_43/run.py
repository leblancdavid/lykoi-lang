"""One bounded successor qualification; unchanged saved plans, no historical rescoring."""
from copy import deepcopy
from datetime import datetime, timezone
import sys
from unittest.mock import patch
from common import ROOT, OUT, OLD, read, save, verify, serial, digest
from sidecar import label, UNAVAILABLE

sys.path.insert(0, str(ROOT / 'experiments/typed_composition_r6_18'))
import composition as c


def cell(value):
    return {'value': serial(value.value), 'span': [value.start, value.end], 'origins': list(value.origins)}


def observe(plan, data, budget=None):
    events = []
    original = c.vm.Machine

    class Observed(original):
        def charge(self, site=None):
            events.append({'kind': 'charge', 'node': self.node, 'cursor': self.i,
                           'work_before': self.work, 'site': self.i if site is None else site})
            return super().charge(site)

        def decode(self, codec, raw):
            events.append({'kind': 'decode_raw', 'node': self.node, 'codec': codec, 'cell': cell(raw)})
            result = super().decode(codec, raw)
            events.append({'kind': 'decode_numeric', 'node': self.node, 'codec': codec, 'cell': cell(result)})
            return result

        def run(self, node, env, depth=1):
            events.append({'kind': 'enter', 'node': node['id'], 'cursor': self.i, 'work_before': self.work})
            result = super().run(node, env, depth)
            events.append({'kind': 'return', 'node': node['id'], 'cursor': self.i,
                           'work_after': self.work, 'cell': cell(result)})
            return result

    limits = None if budget is None else {'work': budget}
    with patch.object(c.vm, 'Machine', Observed):
        envelope = c.vm.execute(plan, data, limits)
    plain = c.vm.execute(plan, data, limits)
    assert envelope == plain, 'instrumentation altered public execution'
    return {'envelope': serial(envelope), 'events': events}


def projection(observation):
    envelope = observation['envelope']
    if envelope['status'] == 'success':
        return {k: envelope[k] for k in ('status', 'value', 'output', 'consumed')}
    return {'status': envelope['status'], 'code': envelope['error']['code'], 'stage': envelope['error']['stage']}


def default_match(observed, wanted):
    envelope = observed['envelope']
    returns = [{'node': e['node'], **e['cell']} for e in observed['events'] if e['kind'] == 'return']
    raw = [e for e in observed['events'] if e['kind'] == 'decode_raw']
    numeric = [e for e in observed['events'] if e['kind'] == 'decode_numeric']
    if returns != wanted['cells'] or len(raw) != len(wanted['decodes']) or len(numeric) != len(raw):
        return False
    for a, b, expected in zip(raw, numeric, wanted['decodes']):
        if a['node'] != expected['node'] or b['node'] != expected['node']:
            return False
        if a['cell'] != {'value': {'bytes_hex': bytes([expected['value']]).hex()},
                         'span': expected['span'], 'origins': expected['raw_origins']}:
            return False
        if b['cell'] != {'value': expected['value'], 'span': expected['span'],
                         'origins': expected['numeric_origins']}:
            return False
    if envelope['status'] != wanted['status'] or envelope['work'] != wanted['work']:
        return False
    if wanted['status'] == 'success':
        return (envelope['value'] == wanted['value'] and envelope['output'] == {'bytes_hex': wanted['output_hex']}
                and envelope['consumed'] == wanted['consumed']
                and envelope['provenance'] == {'span': wanted['span'], 'origins': wanted['origins']})
    error = envelope['error']
    return all(error[k] == wanted[k] for k in ('code', 'offset', 'node', 'stage')) and error['path'] is None


def nodes(plan):
    result = {}

    def walk(n):
        result[n['id']] = n['op']
        for step in n.get('steps', []):
            walk(step['node'])

    walk(plan['decode'])
    walk(plan['encode'])
    return result


def run():
    assert not (OUT / 'QUALIFICATION.json').exists(), 'one immutable attempt only'
    verify(read(OUT / 'FREEZE.json')['files'])
    baseline = read(OUT / 'BASELINE.json')
    verify(baseline['protected_files'])
    review = read(OUT / 'PREEXECUTION-REVIEW.json')
    assert review['passed'] and review['candidate_executions'] == 0
    package = c.load(c.canonical(read(OLD / 'COMPACT.json')).decode('ascii'))
    expanded = c.expand(package)
    plans = {'compact': expanded['plan'], 'exact': read(OLD / 'EXACT.json'), 'flat': read(OLD / 'FLAT.json')}
    correspondence = read(OLD / 'CORRESPONDENCE.json')
    expectations = read(OUT / 'EXPECTATIONS.json')
    failures, evidence, controls = [], [], []
    counts = {'default_observations': 0, 'default_expectation_passes': 0, 'compact_exact_default_pairs': 0,
              'flat_functional_pairs': 0, 'cutoff_observations': 0, 'compact_exact_cutoff_pairs': 0,
              'instrumented_plain_agreements': 0, 'sidecar_preservation_checks': 0,
              'numeric_decode_returns': 0, 'raw_decode_inputs': 0, 'sequence_returns': 0,
              'flat_offset_differences': 0}

    def require(condition, name, detail=None):
        if not condition:
            failures.append({'check': name, 'detail': detail})
        return bool(condition)

    require(plans['compact'] == plans['exact'], 'exact_expansion_structure')
    require(expanded['map'] == read(OLD / 'EXPECTED-MAP.json'), 'exact_expansion_map')
    defaults = {}
    pass_digests = []
    for repeat in (1, 2):
        pass_rows = []
        for row in expectations['rows']:
            data = bytes.fromhex(row['input_hex'])
            observations = {}
            for form, plan in plans.items():
                observed = observe(plan, data)
                snapshot = deepcopy(observed)
                side = label(observed, nodes(plan), expanded['map'] if form != 'flat' else {},
                             correspondence['expansion_paths'], correspondence['flat_to_exact'] if form == 'flat' else None)
                require(observed == snapshot and side['raw_observation_sha256'] == digest(snapshot), 'sidecar_raw_preservation')
                require(side['raw_error'] == observed['envelope'].get('error'), 'raw_error_preservation')
                require(all(v == 'UNAVAILABLE' for v in side['unavailable'].values()), 'unavailable_markers')
                if form == 'flat':
                    require(all(e['symbolic_origin']['status'] == 'UNAVAILABLE' for e in side['labels']), 'flat_not_authorship')
                counts['sidecar_preservation_checks'] += 1
                counts['instrumented_plain_agreements'] += 1
                counts['default_observations'] += 1
                counts['default_expectation_passes'] += require(default_match(observed, row['forms'][form]),
                       'successor_default_expectation', {'pass': repeat, 'input': data.hex(), 'form': form})
                counts['numeric_decode_returns'] += sum(e['kind'] == 'decode_numeric' for e in observed['events'])
                counts['raw_decode_inputs'] += sum(e['kind'] == 'decode_raw' for e in observed['events'])
                counts['sequence_returns'] += sum(e['category'] == 'SEQUENCE_RETURN_SPAN' for e in side['labels'])
                observations[form] = observed
                pass_rows.append({'pass': repeat, 'input_hex': data.hex(), 'form': form,
                                  'raw': observed, 'sidecar': side})
            counts['compact_exact_default_pairs'] += require(observations['compact'] == observations['exact'], 'default_exact_pair')
            counts['flat_functional_pairs'] += require(projection(observations['compact']) == projection(observations['flat']), 'flat_functional')
            a, b = observations['compact']['envelope'], observations['flat']['envelope']
            if a['status'] == 'reject' and a['error']['offset'] != b['error']['offset']:
                counts['flat_offset_differences'] += 1
            if repeat == 1:
                defaults[data.hex()] = observations
        pass_digests.append(digest([{k: v for k, v in r.items() if k != 'pass'} for r in pass_rows]))
        evidence.extend(pass_rows)
    require(pass_digests[0] == pass_digests[1], 'second_pass_determinism')
    for row in expectations['rows']:
        for budget in expectations['budgets']:
            observations = {}
            for form, plan in plans.items():
                observed = observe(plan, bytes.fromhex(row['input_hex']), budget)
                before = deepcopy(observed)
                side = label(observed, nodes(plan), expanded['map'] if form != 'flat' else {},
                             correspondence['expansion_paths'], correspondence['flat_to_exact'] if form == 'flat' else None)
                require(observed == before and side['raw_observation_sha256'] == digest(before), 'cutoff_sidecar_preservation')
                counts['cutoff_observations'] += 1
                counts['instrumented_plain_agreements'] += 1
                counts['sidecar_preservation_checks'] += 1
                observations[form] = observed
                evidence.append({'input_hex': row['input_hex'], 'form': form, 'budget': budget, 'raw': observed, 'sidecar': side})
            counts['compact_exact_cutoff_pairs'] += require(observations['compact'] == observations['exact'], 'cutoff_exact_pair')
    # All controls are expectation/metadata mutations, never candidate repairs.
    rows = {r['input_hex']: r['forms'] for r in expectations['rows']}

    def negative(name, expected, input_hex, form):
        accepted = default_match(defaults[input_hex][form], expected)
        controls.append({'label': name, 'expected_reject': True, 'actual_reject': not accepted,
                         'claim': expected, 'input_hex': input_hex, 'form': form})
        require(not accepted, name)

    wrong = deepcopy(rows['0201']['compact'])
    wrong['decodes'][0]['numeric_origins'] = [0]
    negative('numeric_origins_as_raw_byte_origins', wrong, '0201', 'compact')
    wrong = deepcopy(rows['0201']['compact'])
    wrong['decodes'][0]['raw_origins'] = []
    negative('raw_bytes_as_empty_numeric_origin', wrong, '0201', 'compact')
    wrong = deepcopy(rows['0201']['compact'])
    paths = expectations['paths']
    next(e for e in wrong['cells'] if e['node'] == paths['left'])['span'] = [0, 1]
    negative('returned_sequence_as_operand_span', wrong, '0201', 'compact')
    for data, wrong_offset in (('0000', 0), ('0302', 1)):
        wrong = deepcopy(rows[data]['compact'])
        wrong['offset'] = wrong_offset
        negative('compact_offset_normalization_' + data, wrong, data, 'compact')
    wrong = deepcopy(rows['0000']['flat'])
    wrong['offset'] = 2
    negative('flat_offset_normalization', wrong, '0000', 'flat')
    for node, origin in expanded['map'].items():
        require(origin == correspondence['symbolic_origins'][node], 'definition_local_correspondence', node)
        require(node in correspondence['expansion_paths'], 'expansion_path_available', node)
    raw = defaults['0201']['compact']
    side = label(raw, nodes(plans['compact']), expanded['map'], correspondence['expansion_paths'])
    left = next(e for e in side['labels'] if e['raw_node'] == paths['left_inner'] + '/sum')
    right_chain = correspondence['expansion_paths'][paths['right_inner'] + '/sum']
    controls.append({'label': 'wrong_sibling_path', 'expected_reject': True,
                     'actual_reject': left['symbolic_origin']['expansion_path'] != right_chain})
    require(controls[-1]['actual_reject'], 'wrong_sibling_path')
    low = defaults['0000']['compact']
    low_side = label(low, nodes(plans['compact']), expanded['map'], correspondence['expansion_paths'])
    consumer = next(e for e in low_side['labels'] if e['raw_node'] == paths['root'] + '/post_low')
    require(consumer['symbolic_origin']['expansion_path'] == [], 'consumer_not_producer_path')
    controls.append({'label': 'producer_path_as_consumer_path', 'expected_reject': True,
                     'actual_reject': consumer['symbolic_origin']['expansion_path'] != correspondence['expansion_paths'][paths['left']]})
    for key in UNAVAILABLE:
        controls.append({'label': 'invented_' + key, 'expected_reject': True,
                         'actual_reject': side['unavailable'][key] == 'UNAVAILABLE'})
        require(controls[-1]['actual_reject'], 'unsupported_' + key)
    missing = label(raw, nodes(plans['compact']), {}, {})
    require(all(e['symbolic_origin'] == {'status': 'UNAVAILABLE'} for e in missing['labels']), 'missing_map_no_inference')
    controls.append({'label': 'missing_map_must_not_infer_identity', 'expected_reject': True,
                     'actual_reject': all(e['symbolic_origin'] == {'status': 'UNAVAILABLE'} for e in missing['labels'])})
    flat43, compact43 = observe(plans['flat'], b'\x02\x01', 43), observe(plans['compact'], b'\x02\x01', 43)
    require(flat43['envelope']['status'] == 'success' and compact43['envelope']['error']['code'] == 'WORK_LIMIT', 'representation_budget_difference')
    controls.append({'label': 'full_flat_envelope_equivalence', 'expected_reject': True,
                     'actual_reject': defaults['0201']['compact'] != defaults['0201']['flat']})
    require(all(x['actual_reject'] for x in controls), 'all_adversarial_controls')
    verify(baseline['protected_files'])
    verify(read(OUT / 'FREEZE.json')['files'])
    save('QUALIFICATION.json', {'round': 'R6.43', 'counts': counts, 'failures': failures,
         'observations': evidence, 'default_pass_digests': pass_digests, 'actual_map': expanded['map'],
         'cutoff_independent_expected_trace_oracle': False})
    save('ADVERSARIAL.json', {'controls': controls, 'passed': all(x['actual_reject'] for x in controls),
         'budget_difference': {'input_hex': '0201', 'budget': 43, 'compact': compact43, 'flat': flat43},
         'candidate_artifacts_modified': False})
    save('RESULT.json', {'round': 'R6.43', 'classification': 'R6_43_PROVENANCE_QUALIFIED_BENCHMARK_PARTIAL' if not failures else 'R6_43_PROVENANCE_PARTIAL',
         'bounded_coordinate_qualification_passed': not failures, 'counts': counts, 'failures': len(failures),
         'adversarial_controls': len(controls), 'map_entries': len(expanded['map']),
         'independent_cognitive_review_established': False, 'review_is_candidate_output_independent': True,
         'benchmark_partial_reason': 'symbolic execution lacks state/effects; production bounded path available, independent realistic acceptance not supplied',
         'ai_calls': 0, 'kernel': 26, 'completed_utc': datetime.now(timezone.utc).isoformat()})
    print(read(OUT / 'RESULT.json'))


if __name__ == '__main__':
    run()
