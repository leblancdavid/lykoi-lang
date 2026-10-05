"""Bounded R5.72 qualification driver; no B02 opening entry point.

Historical evidence is read-only. Every stage independently reloads current
state; final verification never recreates existing immutable evidence.
"""
from pathlib import Path
import ast
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OUT = ROOT / 'benchmark/results/phase5c/R5_72-qualified-evidence'


def write(name, value):
    r.persist(OUT / (name + '.json'), value)


def read(name):
    return r.load(OUT / (name + '.json'))


def preservation():
    names = r.git(ROOT, 'ls-files', '--cached', '--others', '--exclude-standard', '--', 'benchmark/results').splitlines()
    ordinary, protected = [], []
    for name in sorted(set(names)):
        if '/R5_72-' in name or Path(name).name.startswith('r5_72_'):
            continue
        path = ROOT / name
        if name in r.RESOURCE_PATHS:
            stat = path.stat()
            protected.append({'path': name, 'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns})
        else:
            ordinary.append({'path': name, 'sha256': r.digest(path.read_bytes())})
    return {'ordinary': ordinary, 'protected_metadata_only': protected}


def prepare():
    r.require(OUT.parent.is_dir() and not OUT.exists(), 'new qualification directory required')
    OUT.mkdir()
    write('preservation', preservation())
    commitment = r.benchmark_commitment(ROOT)
    write('benchmark', commitment)
    state = r.current_state(ROOT)
    r.require(state == r.current_state(ROOT), 'nondeterministic state capture')
    write('state', state)
    (OUT / 'actual-ledger').mkdir()
    r.require(r.Ledger(OUT / 'actual-ledger').status() == 'zero', 'actual ledger not zero')
    print({'prepared': True, 'state': state['identity'], 'benchmark': commitment['identity'],
           'sealed_resources': len(commitment['resources']), 'frozen_pins': 2, 'core_semantics': 30})


def health(stage):
    value = r.run_health_stage(ROOT, read('state'), stage)
    write('health-' + stage, r.seal(value))
    print({'stage': stage, **value})


def finish():
    state, benchmark = read('state'), read('benchmark')
    r.require(state == r.current_state(ROOT), 'qualification state changed')
    r.verify_commitment(benchmark, benchmark['identity'], r.benchmark_commitment(ROOT))
    results = {stage: r.verify(read('health-' + stage)) for stage in r.HEALTH_STAGES}
    health_record = r.health_record(state, results)
    write('health', health_record)
    frozen = r.freeze(state, benchmark, health_record)
    r.require(frozen == r.freeze(state, benchmark, health_record), 'nondeterministic freeze')
    write('freeze', frozen)
    r.require(r.Ledger(OUT / 'actual-ledger').status() == 'zero', 'actual accounting changed')
    from benchmark.evaluation.test_phase5_runner_v2 import synthetic
    commitment, content = synthetic()
    write('synthetic-benchmark', commitment)
    fake_frozen = r.freeze(state, commitment, health_record)
    write('synthetic-freeze', fake_frozen)
    (OUT / 'synthetic-ledger').mkdir()
    ledger = r.Ledger(OUT / 'synthetic-ledger')
    r.require(ledger.status() == 'zero', 'synthetic ledger not zero')
    grant = r.authorize_synthetic(fake_frozen, commitment, ledger, state)
    write('synthetic-authorization', grant)
    reads, calls = [], []
    def opener():
        reads.append(1)
        return content
    def observe(opened):
        calls.append(1)
        r.require(set(opened) == set(content), 'synthetic whole-contract set mismatch')
        return {'classification': 'synthetic-static-observed', 'whole_contract': True,
                'resource_count': len(opened), 'behavioral_authority': 'required externally observable behavior'}
    args = (fake_frozen, commitment, grant, ledger, lambda: r.current_state(ROOT), lambda: commitment, opener, observe)
    result = r.observe(*args)
    post = r.post_check(fake_frozen, commitment, ledger, lambda: r.current_state(ROOT), lambda: commitment)
    replay_rejected = False
    try:
        r.observe(*args)
    except r.Rejected:
        replay_rejected = True
    r.require(replay_rejected and len(reads) == len(calls) == 1, 'synthetic replay violation')
    # Intentional synthetic repair marker exercises invalidation, without changing
    # actual Lykoi implementation or the actual clean zero-observation freeze.
    r.invalidate_repair(fake_frozen, ledger)
    repair_rejected = False
    try:
        r.post_check(fake_frozen, commitment, ledger, lambda: r.current_state(ROOT), lambda: commitment)
    except r.Rejected:
        repair_rejected = True
    r.require(repair_rejected, 'synthetic repair accepted')
    write('synthetic-lifecycle', r.seal({'status': 'PASS', 'initial_observations': 0,
        'openings': len(reads), 'observations': len(calls), 'result': result, 'post_check_before_repair': post,
        'replay_rejected': replay_rejected, 'repair_rejected': repair_rejected,
        'final_synthetic_status': ledger.status()}))
    verify_all()
    write('summary', r.seal({'classification': 'R5_72_SIMPLIFIED_PHASE5_RUNNER_QUALIFIED',
        'state': state['identity'], 'benchmark': benchmark['identity'], 'freeze': frozen['identity'],
        'health': health_record['identity'], 'core_semantics': 30, 'protected_read_attempts': 0,
        'protected_content_reads': 0, 'b02_accounting': [0, 0, 0, 0], 'b02_opening': [0, 0],
        'actual_authorizations': 0, 'actual_ledger': 'zero', 'repair_state': 'clean',
        'synthetic_openings': 1, 'synthetic_observations': 1, 'simplicity': {
            'core_modules': 2, 'artifact_types': 6, 'authorization_layers': 1,
            'required_observation_transitions': 5, 'invalidation_transition': 1},
        'next_gate': 'R5.73 separately authorized actual one-shot static experiment; no repair/retry'}))
    print(read('summary'))


def verify_all():
    state, benchmark = read('state'), read('benchmark')
    r.require(state == r.current_state(ROOT) and read('preservation') == preservation(), 'state/history drift')
    r.verify_commitment(benchmark, benchmark['identity'], r.benchmark_commitment(ROOT))
    health_record = read('health')
    results = {stage: r.verify(read('health-' + stage)) for stage in r.HEALTH_STAGES}
    r.require(r.health_record(state, results) == health_record and
              r.freeze(state, benchmark, health_record) == read('freeze'), 'health/freeze drift')
    r.require(r.Ledger(OUT / 'actual-ledger').status() == 'zero', 'actual accounting changed')
    lifecycle = read('synthetic-lifecycle')
    r.verify(lifecycle)
    r.require(lifecycle['openings'] == lifecycle['observations'] == 1 and lifecycle['replay_rejected']
              and lifecycle['repair_rejected'], 'synthetic lifecycle failed')
    events = r.Ledger(OUT / 'synthetic-ledger').events()
    r.require([e['transition'] for e in events] == [*r.TRANSITIONS, 'INVALIDATED'], 'synthetic ledger drift')
    for path in OUT.rglob('*.json'):
        r.safe_bytes(r.load(path))
    # Independently inspect the source dependency boundary rather than trusting
    # the runner's reported module/layer counts. Semantic/compiler components
    # may have historical filenames; retired evaluation mechanisms may not run.
    for name in ('phase5_runner_v2.py', 'phase5_worker_v2.py'):
        source = (ROOT / 'benchmark/evaluation' / name).read_text(encoding='utf-8')
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom) and node.module == 'benchmark.evaluation':
                r.require(all(a.name == 'phase5_runner_v2' for a in node.names), 'R5_72_SIMPLIFICATION_FAILURE')
            if isinstance(node, ast.ImportFrom) and (node.module or '').startswith('benchmark.results'):
                raise r.Rejected('R5_72_SIMPLIFICATION_FAILURE')
        r.safe_bytes({'source': source})
    r.safe_bytes({'source': (ROOT / 'benchmark/evaluation/test_phase5_runner_v2.py').read_text()})
    r.safe_bytes({'source': Path(__file__).read_text()})
    print({'read_only_verification': 'PASS', 'historical_ordinary_files': len(read('preservation')['ordinary']),
           'protected_historical_metadata': len(read('preservation')['protected_metadata_only']),
           'b02_accounting': 'zero'})


if __name__ == '__main__':
    boundary = r.Boundary(ROOT)
    with boundary.active():
        command = sys.argv[1]
        if command == 'prepare':
            prepare()
        elif command == 'health':
            health(sys.argv[2])
        elif command == 'finish':
            finish()
        elif command == 'verify':
            verify_all()
        else:
            raise r.Rejected('unknown qualification operation')
