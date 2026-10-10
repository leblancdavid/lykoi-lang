"""Execute only frozen R6.42 observations, preserving raw representation differences."""
import copy
from collections import Counter
from datetime import datetime, timezone
from unittest.mock import patch
from common import ROOT, OUT, c, read, save, serial, verify_files, verify_freeze
from oracle import cell, trace_digest
import sys
sys.path.insert(0, str(ROOT / 'experiments/lifecycle_r6_32'))
from lifecycle import Registry


def observe(plan, data, budget=None):
    events, checks = [], []
    original = c.vm.Machine

    class Observed(original):
        def charge(self, site=None):
            events.append({'kind': 'charge', 'node': self.node, 'cursor': self.i,
                           'work_before': self.work, 'site': self.i if site is None else site})
            return super().charge(site)

        def run(self, node, env, depth=1):
            events.append({'kind': 'enter', 'node': node['id'], 'cursor': self.i,
                           'work_before': self.work, 'depth': depth})
            # Record entry, not a claim that a predicate evaluated before cutoff.
            if node['op'] == 'check':
                label = node['code']
                if label == 'INNER':
                    label = ('left' if '/left' in node['id'] else 'right') + ':INNER'
                checks.append(label)
            result = super().run(node, env, depth)
            events.append({'kind': 'return', 'node': node['id'], 'cursor': self.i,
                           'work_after': self.work, 'depth': depth,
                           'cell': cell(result.value, result.start, result.end, result.origins)})
            return result

    limits = None if budget is None else {'work': budget}
    with patch.object(c.vm, 'Machine', Observed):
        envelope = c.vm.execute(plan, data, limits)
    plain = c.vm.execute(plan, data, limits)
    assert envelope == plain, 'observation instrumentation changed execution'
    return {'envelope': serial(envelope), 'trace': events, 'trace_sha256': trace_digest(events), 'checks': checks}


def functional(observation):
    envelope = observation['envelope']
    if envelope['status'] == 'success':
        return {k: envelope[k] for k in ('status', 'value', 'output', 'consumed')}
    return {'status': envelope['status'], 'code': envelope['error']['code'],
            'stage': envelope['error']['stage'], 'checks': observation['checks']}


def claim_verdict(claim, correspondence, defaults):
    kind = claim['kind']
    if kind in correspondence['unsupported_fields']:
        return 'UNSUPPORTED_PROVENANCE'
    if kind == 'node_origin':
        node = claim['node']
        return ('SUPPORTED' if claim['origin'] == correspondence['symbolic_origins'].get(node)
                and claim['expansion_path'] == correspondence['expansion_paths'].get(node)
                and node in correspondence['symbolic_origins'] else 'CORRESPONDENCE_REJECT')
    if kind == 'flat_pair':
        return ('SUPPORTED' if correspondence['flat_to_exact'].get(claim['node']) == claim['exact_node']
                else 'CORRESPONDENCE_REJECT')
    if kind == 'error_offset':
        envelope = defaults[claim['input_hex']][claim['form']]['envelope']
        return 'SUPPORTED' if envelope['error']['offset'] == claim['offset'] else 'UNSUPPORTED_PROVENANCE'
    if kind == 'full_flat_envelope_equivalence':
        row = defaults[claim['input_hex']]
        return 'SUPPORTED' if row['compact'] == row['flat'] else 'UNSUPPORTED_PROVENANCE'
    return 'UNSUPPORTED_PROVENANCE'


def run():
    assert not (OUT / 'DIFFERENTIAL.json').exists(), 'do not overwrite or rerun published attempt'
    frozen_count = verify_freeze()
    baseline = read(OUT / 'BASELINE.json')
    verify_files(baseline['protected_files'])
    package = c.load(c.canonical(read(OUT / 'COMPACT.json')).decode('ascii'))
    expanded = c.expand(package)
    plans = {'compact': expanded['plan'], 'exact': read(OUT / 'EXACT.json'), 'flat': read(OUT / 'FLAT.json')}
    expected_map = read(OUT / 'EXPECTED-MAP.json')
    correspondence = read(OUT / 'CORRESPONDENCE.json')
    discrepancies = []

    def require(ok, label, detail=None):
        if not ok:
            discrepancies.append({'label': label, 'detail': detail})

    require(plans['compact'] == plans['exact'], 'independent_expansion_structure')
    require(expanded['map'] == expected_map, 'independent_expansion_map')
    for plan in plans.values():
        c.vm.validate(plan)
    save(OUT / 'ACTUAL-EXPANSION.json', expanded)
    # New registry only: exact closure, repeated call identity and restart, no execution meanings.
    registry_path = OUT / 'registry'
    registry = Registry(registry_path)
    receipt = registry.admit(package['definitions'] + [package['program']], None)
    fetched = Registry(registry_path).retrieve(pin=package['program']['identity'])
    require(sorted(fetched, key=lambda d: d['identity']) == sorted(package['definitions'] + [package['program']], key=lambda d: d['identity']),
            'registry_restart_exact_closure')
    save(OUT / 'REGISTRY.json', {'receipt': receipt, 'retrieved_closure': fetched,
         'registry_semantics_unchanged': True, 'historical_registry_access': False})
    expectation_rows = read(OUT / 'EXPECTATIONS.json')['rows']
    defaults, passes, budgets, work_rows, provenance = {}, [], [], [], []
    representatives = {'0201', '0404', '0004', '0000', '0302', '', '02', '020100'}
    for repeat in (1, 2):
        default_rows = []
        for row in expectation_rows:
            data = bytes.fromhex(row['input_hex'])
            observed = {form: observe(plan, data) for form, plan in plans.items()}
            for form, observation in observed.items():
                wanted = {k: row['forms'][form][k] for k in ('envelope', 'trace', 'trace_sha256', 'checks')}
                require(observation == wanted, 'default_oracle', {'pass': repeat, 'input': data.hex(), 'form': form,
                                                                  'expected': wanted, 'actual': observation})
            require(observed['compact'] == observed['exact'], 'compact_exact_default', data.hex())
            require(functional(observed['compact']) == functional(observed['flat']), 'flat_functional_default', data.hex())
            if repeat == 1:
                defaults[data.hex()] = observed
                work_rows.append({'input_hex': data.hex(), 'status': observed['compact']['envelope']['status'],
                    'code': observed['compact']['envelope'].get('error', {}).get('code'),
                    'work': {form: o['envelope']['work'] for form, o in observed.items()},
                    'compact_minus_flat': observed['compact']['envelope']['work'] - observed['flat']['envelope']['work']})
                for form, o in observed.items():
                    error = o['envelope'].get('error')
                    if error:
                        raw_node = error['node']
                        at = correspondence['flat_to_exact'].get(raw_node) if form == 'flat' else raw_node
                        provenance.append({'input_hex': data.hex(), 'form': form, 'raw_error': error,
                            'comparison_exact_node': at, 'definition_local': expanded['map'].get(at),
                            'expansion_path': correspondence['expansion_paths'].get(at),
                            'is_flat_comparison_annotation': form == 'flat'})
            default_rows.append({'input_hex': data.hex(), 'forms': observed})
        passes.append({'pass': repeat, 'rows': default_rows, 'sha256': trace_digest(default_rows)})
    require(passes[0]['sha256'] == passes[1]['sha256'], 'deterministic_second_pass')
    # Every charge cutoff through completion+1 for every input and each form.
    cutoff_total = 0
    for row in expectation_rows:
        data = bytes.fromhex(row['input_hex'])
        by_form = {}
        for form, plan in plans.items():
            cutoff_rows = []
            for wanted in row['forms'][form]['cutoffs']:
                observation = observe(plan, data, wanted['budget'])
                reduced = {k: observation[k] for k in ('envelope', 'trace_sha256', 'checks')}
                require(reduced == {k: wanted[k] for k in reduced}, 'cutoff_oracle',
                        {'input': data.hex(), 'form': form, 'budget': wanted['budget'], 'expected': wanted, 'actual': observation})
                # Exact-vs-compact tested at the same numerical budget, including partial traces.
                if form == 'exact':
                    twin = observe(plans['compact'], data, wanted['budget'])
                    require(twin == observation, 'compact_exact_cutoff', {'input': data.hex(), 'budget': wanted['budget']})
                record = {'budget': wanted['budget'], **reduced}
                if data.hex() in representatives:
                    record['trace'] = observation['trace']
                cutoff_rows.append(record)
                cutoff_total += 1
            by_form[form] = cutoff_rows
        budgets.append({'input_hex': data.hex(), 'forms': by_form})
    controls = []
    for control in read(OUT / 'CONTROL-EXPECTATIONS.json'):
        if 'package' in control:
            observed = c.diagnose(copy.deepcopy(control['package']))
            verdict = observed['diagnostic']['code'] if observed['status'] == 'reject' else 'ACCEPTED'
        else:
            verdict = claim_verdict(control['claim'], correspondence, defaults)
            observed = {'verdict': verdict}
        require(verdict == control['expected'], 'adversarial_control', {'control': control, 'actual': observed})
        controls.append({**control, 'actual': observed, 'passed': verdict == control['expected']})
    positive_claims = []
    for node, origin in expanded['map'].items():
        claim = {'kind': 'node_origin', 'node': node, 'origin': origin,
                 'expansion_path': correspondence['expansion_paths'][node]}
        verdict = claim_verdict(claim, correspondence, defaults)
        require(verdict == 'SUPPORTED', 'positive_origin', node)
        positive_claims.append({'claim': claim, 'verdict': verdict})
    for node, at in correspondence['flat_to_exact'].items():
        claim = {'kind': 'flat_pair', 'node': node, 'exact_node': at}
        verdict = claim_verdict(claim, correspondence, defaults)
        require(verdict == 'SUPPORTED', 'positive_flat_pair', node)
        positive_claims.append({'claim': claim, 'verdict': verdict})
    save(OUT / 'DIFFERENTIAL.json', {'passes': passes, 'default_observations': len(expectation_rows) * 3 * 2,
         'cutoff_observations': cutoff_total, 'cutoffs': budgets,
         'cutoff_full_trace_inputs': sorted(representatives), 'discrepancies': discrepancies,
         'instrumentation_matches_uninstrumented': True, 'frozen_file_count': frozen_count})
    save(OUT / 'PROVENANCE.json', {'raw_errors_and_attribution': provenance, 'positive_claims': positive_claims,
         'actual_map': expanded['map'], 'frozen_correspondence': correspondence})
    histogram = Counter(r['compact_minus_flat'] for r in work_rows)
    save(OUT / 'WORK.json', {'rows': work_rows, 'compact_minus_flat_histogram': dict(sorted(histogram.items())),
         'logical_work_is_not_physical_cost': True, 'flat_equal_budget_outcomes_required': False})
    save(OUT / 'ADVERSARIAL.json', {'controls': controls, 'nested_repeated_and_ordering_inputs':
         {'nested_and_repeated_success': '0201', 'first_internal_conflicting': '0404',
          'second_internal_before_post_low': '0004', 'post_return_low': '0000', 'post_return_high': '0302'},
         'cutoff_observations': cutoff_total, 'discrepancies': discrepancies})
    verify_files(baseline['protected_files'])
    verify_freeze()
    result = {'round': 'R6.42', 'classification': 'R6_42_PROVENANCE_CORRESPONDENCE_QUALIFIED' if not discrepancies else 'R6_42_PROVENANCE_PARTIAL',
              'default_observations': len(expectation_rows) * 6, 'unique_inputs': len(expectation_rows), 'cutoff_observations': cutoff_total,
              'adversarial_controls': len(controls), 'positive_correspondence_claims': len(positive_claims),
              'discrepancies': len(discrepancies), 'scope': 'frozen finite domain only; unscored; model-free execution',
              'completed_utc': datetime.now(timezone.utc).isoformat(), 'kernel': 26}
    save(OUT / 'RESULT.json', result)
    print(result)


if __name__ == '__main__':
    run()
