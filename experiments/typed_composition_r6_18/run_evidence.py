"""Publish bounded exhaustive qualification, retained controls, and host measurements."""
import copy
import hashlib
import json
import platform
import statistics
import time
import tracemalloc
from unittest.mock import patch
from composition import (HERE, FOUNDATION, Diagnostic, _expand_validated, canonical,
                         diagnose, expand, load, validate, vm)
from controls import SERIALIZATION, controls, scalar_program
from examples import examples, explicit_twin
from preservation import verify, sha


def serial(x):
    if type(x) is bytes:
        return {'bytes_hex': x.hex()}
    if type(x) is dict:
        return {k: serial(v) for k, v in x.items()}
    if type(x) in (tuple, list):
        return [serial(v) for v in x]
    return x


def save(name, data):
    (HERE / name).write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')


def traced(plan, data, limits=None):
    events = []
    original = vm.Machine

    class TraceMachine(original):
        def run(self, node, env, depth=1):
            events.append({'node': node['id'], 'cursor': self.i, 'work_before': self.work, 'depth': depth})
            return super().run(node, env, depth)

    with patch.object(vm, 'Machine', TraceMachine):
        result = vm.execute(plan, data, limits)
    assert result == vm.execute(plan, data, limits), 'instrumentation changed public envelope'
    return result, events


def measure(fn, repetitions=200):
    samples = []
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        fn()
        samples.append(time.perf_counter_ns() - start)
    tracemalloc.start()
    fn()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return {'repetitions': repetitions, 'median_ns': statistics.median(samples),
            'min_ns': min(samples), 'max_ns': max(samples), 'python_peak_bytes_one_call': peak}


def publish():
    assert not (HERE / 'RESULTS.json').exists(), 'published results are immutable; use a separately authorized new run'
    verify()
    packages = examples()
    evidence = {'foundation_sha256': FOUNDATION, 'environment': {'python': platform.python_version(),
                'platform': platform.platform()}, 'contexts': {}, 'controls': [], 'serialization': [],
                'runtime_controls': []}
    for row in controls():
        observed = diagnose(load(canonical(row['package']).decode()), row['node_budget'])
        assert observed['status'] == 'reject' and observed['diagnostic']['code'] == row['expected'], row['label']
        evidence['controls'].append({**row, 'observed': observed})
    for label, text, code in SERIALIZATION:
        try:
            load(text)
            raise AssertionError(label)
        except Diagnostic as exc:
            assert exc.data['code'] == code
            evidence['serialization'].append({'label': label, 'input': text, 'expected': code, 'diagnostic': exc.data})

    for context, package in packages.items():
        expanded = expand(package)
        plan = expanded['plan']
        twin = explicit_twin(package)
        assert plan == twin
        vm.validate(twin)
        save(context + '.symbolic.json', package)
        save(context + '.expanded.json', plan)
        save(context + '.explicit.json', twin)
        save(context + '.expansion-map.json', {k: v for k, v in expanded.items() if k != 'plan'})
        row = {'symbolic_canonical_bytes': len(canonical(package)),
               'program_only_canonical_bytes': len(canonical(package['program'])),
               'registry_canonical_bytes': len(canonical(package['definitions'])),
               'expanded_canonical_bytes': len(canonical(plan)), 'expanded_nodes': expanded['nodes'],
               'definition_identity': package['definitions'][0]['identity'],
               'plan_identity': expanded['plan_identity'], 'passes': []}
        for repeat in range(3):
            digest = hashlib.sha256()
            counts = {'success': 0, 'BOUND': 0}
            work_min, work_max = 100000, 0
            work_total = 0
            start = time.perf_counter()
            for x in range(256):
                for y in range(256):
                    data = bytes([x, y]) if context == 'pair' else bytes([7, x, y])
                    a = vm.execute(plan, data)
                    b = vm.execute(twin, data)
                    assert a == b, (context, repeat, x, y)
                    value = x + y + (context != 'pair')
                    if value <= 255:
                        assert a['status'] == 'success' and type(a['value']) is int and a['value'] == value
                        assert a['output'] == value.to_bytes(2, 'big') and a['consumed'] == len(data)
                        counts['success'] += 1
                    else:
                        assert a['status'] == 'reject' and a['error']['code'] == 'BOUND'
                        # Frozen seq wraps returned Cell at its own cursor span.
                        expected_offset = 0 if context == 'pair' else (1 if x == 255 else 3)
                        assert a['error']['offset'] == expected_offset
                        counts['BOUND'] += 1
                    work = a['work']
                    work_min, work_max = min(work_min, work), max(work_max, work)
                    work_total += work
                    digest.update(canonical({'input': data.hex(), 'result': serial(a)}))
            elapsed = time.perf_counter() - start
            entry = {'repeat': repeat + 1, 'unique_byte_pairs': 65536, 'counts': counts,
                     'complete_observation_sha256': digest.hexdigest(), 'pair_comparison_seconds': elapsed,
                     'work_min': work_min, 'work_max': work_max, 'work_total': work_total}
            row['passes'].append(entry)
            print(context, repeat + 1, counts, 'seconds:', round(elapsed, 3), flush=True)
        assert len({p['complete_observation_sha256'] for p in row['passes']}) == 1
        prefix = b'' if context == 'pair' else b'\x07'
        inputs = [b'', prefix, prefix + b'\x01', prefix + b'\x01\x02',
                  prefix + b'\x01\x02\x00', prefix + b'\xff\xff',
                  prefix + b'\xff\x00', prefix + b'\x00\xff']
        if context != 'pair':
            inputs += [bytes([h, 255, 255]) for h in range(256)]
        full = vm.execute(plan, prefix + b'\x01\x02')['work']
        cases = [(d, None) for d in inputs]
        # Sweep each possible work cutoff for success, bound and trailing failures.
        for data in (prefix + b'\x01\x02', prefix + b'\xff\xff', prefix + b'\x01\x02\x00'):
            cases += [(data, {'work': w}) for w in range(full + 2)]
        cases += [(prefix + b'\x01\x02', {key: n}) for key, maximum in
                  [('depth', 6), ('input', 4), ('output', 3)] for n in range(maximum + 1)]
        for data, limits in cases:
            a, events_a = traced(plan, data, limits)
            b, events_b = traced(twin, data, limits)
            assert a == b and events_a == events_b
            evidence['runtime_controls'].append({'context': context, 'input_hex': data.hex(),
                'limits': limits, 'result': serial(a), 'ordered_entry_trace': events_a})
        # Check static expansion/maps determinism independently of runtime loops.
        for _ in range(10):
            assert expand(copy.deepcopy(package)) == expanded
        row['expansion_repeats'] = 10
        data = prefix + b'\x01\x02'
        row['measurements'] = {
            'symbolic_validation': measure(lambda: validate(package)),
            'expansion_after_symbolic_validation_including_vm_validation': measure(lambda: _expand_validated(package)),
            'full_wrapper_expand': measure(lambda: expand(package)),
            'foundation_validation': measure(lambda: vm.validate(plan)),
            'expanded_public_execution': measure(lambda: vm.execute(plan, data)),
            'explicit_public_execution': measure(lambda: vm.execute(twin, data)),
            'symbolic_expand_plus_public_execution': measure(lambda: vm.execute(expand(package)['plan'], data))}
        evidence['contexts'][context] = row
    assert evidence['contexts']['pair']['definition_identity'] == evidence['contexts']['header_increment']['definition_identity']
    # Runtime encode domain and arithmetic overflow are preserved, not optimized out.
    for value in (-2**63, -1, 0, 65535, 65536, 2**63 - 1):
        plan = expand(scalar_program(value))['plan']
        result = vm.execute(plan, b'')
        evidence.setdefault('scalar_domain_controls', []).append({'value': value, 'result': serial(result)})
    evidence['summary'] = {'classification': 'R6_18_TYPED_COMPOSITION_SUPPORTED',
                          'unique_pairs_per_context': 65536, 'contexts': 2, 'full_passes': 3,
                          'differential_pair_observations': 393216,
                          'public_executions_for_exhaustive_comparison': 786432,
                          'adversarial_representation_controls': len(evidence['controls']),
                          'serialization_controls': len(evidence['serialization']),
                          'runtime_trace_controls': len(evidence['runtime_controls']),
                          'logical_work_difference': 0, 'mismatches': 0}
    save('RESULTS.json', evidence)
    verify()
    print(evidence['summary'])


if __name__ == '__main__':
    publish()
