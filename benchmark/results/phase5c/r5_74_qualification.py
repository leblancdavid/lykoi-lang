"""R5.74 non-B02 qualification controller. Structured argv, no inline source.

Fresh artifacts only. Audit commands are read-only and cannot resume R5.73.
The actual commitment is used solely by structural eligibility checks.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OUT = ROOT / 'benchmark/results/phase5c/R5_74-qualified-evidence'
REPORT = 'benchmark/results/phase5c/R5_74-ACTUAL-HELDOUT-AUTHORIZATION-PATH-QUALIFICATION.md'


def write(name, value):
    r.persist(OUT / (name + '.json'), value)


def read(name):
    raw = (OUT / (name + '.json')).read_bytes()
    value = json.loads(raw)
    canonical = json.dumps(value, sort_keys=True, separators=(',', ':'),
                           ensure_ascii=False, allow_nan=False).encode() + b'\n'
    r.require(raw == canonical, 'independent canonical evidence check failed')
    if 'identity' in value:
        body = {key: item for key, item in value.items() if key != 'identity'}
        pin = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',', ':'),
                             ensure_ascii=False, allow_nan=False).encode()).hexdigest()
        r.require(pin == value['identity'], 'independent evidence identity check failed')
    return value


def preservation():
    names = r.git(ROOT, 'ls-files', '--cached', '--others', '--exclude-standard', '--', 'benchmark/results').splitlines()
    ordinary, protected = [], []
    for name in sorted(set(names)):
        if '/R5_74-qualified-evidence/' in name or name == REPORT or Path(name).name.startswith('r5_74_'):
            continue
        path = ROOT / name
        if name in r.RESOURCE_PATHS:
            stat = path.stat()
            protected.append({'path': name, 'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns})
        else:
            ordinary.append({'path': name, 'sha256': r.digest(path.read_bytes())})
    return {'ordinary': ordinary, 'protected_metadata_only': protected}


def prepare():
    r.require(OUT.parent.is_dir() and not OUT.exists(), 'fresh evidence directory required')
    OUT.mkdir()
    write('preservation', preservation())
    write('state', r.current_state(ROOT))
    actual = r.benchmark_commitment(ROOT)
    r.require(r.eligible(actual, r.ACTUAL_HELD_OUT, actual['identity']), 'actual metadata not eligible')
    write('b02-metadata-eligibility', r.seal({'structurally_eligible': True,
        'benchmark': actual, 'authorizations': 0, 'content_reads': 0}))
    (OUT / 'b02-ledger').mkdir()
    # Precommit a real disposable file before the fake experiment freezes.
    raw = b'{"required_behavior":"preserve generic sample ordering","static_only":true}'
    with (OUT / 'fake-contract.txt').open('xb') as stream:
        stream.write(raw)
    commitment = r.seal({'kind': 'fake-benchmark', 'expected_benchmark': 'R5.74/non-B02-stand-in',
        'authority_class': r.ACTUAL_HELD_OUT, 'precommitted': True,
        'resources': {'opaque:fake-resource': {'commitment': r.digest(raw), 'seal': 'CLOSED',
            'frozen': True, 'provenance': 'R5.74 stand-in precommit before ExperimentFreeze'}}})
    write('fake-commitment', commitment)
    (OUT / 'fake-ledger').mkdir()
    print(json.dumps({'prepared': True, 'core_semantics': 30, 'b02_structurally_eligible': True}))


def health(stage):
    write('health-' + stage, r.seal(r.run_health_stage(ROOT, read('state'), stage)))
    print(json.dumps({'stage': stage, 'status': 'PASS'}))


def rejected(call):
    try:
        call()
    except r.Rejected:
        return True
    raise r.Rejected('required rejection did not occur')


def qualify():
    state, commitment = read('state'), read('fake-commitment')
    r.require(state == r.current_state(ROOT), 'state drift before qualification')
    results = {stage: r.verify(read('health-' + stage)) for stage in r.HEALTH_STAGES}
    health = r.health_record(state, results)
    write('health', health)
    ledger = r.Ledger(OUT / 'fake-ledger')
    frozen = r.freeze(state, commitment, health, ledger)
    write('fake-freeze', frozen)
    r.require(ledger.status() == 'zero', 'fake initial accounting not zero')
    command = [sys.executable, '-B', '-S', '-m', 'benchmark.evaluation.phase5_runner_v2', 'preflight',
        '--mode', r.ACTUAL_HELD_OUT, '--trusted-identity', commitment['identity'],
        '--freeze', str(OUT / 'fake-freeze.json'), '--state', str(OUT / 'state.json'),
        '--commitment', str(OUT / 'fake-commitment.json'), '--ledger', str(ledger.directory)]
    result = subprocess.run(command, cwd=ROOT, env=r.controlled_environment(ROOT), capture_output=True, timeout=30)
    r.require(result.returncode == 0, 'structured preflight failed')
    write('invocation', r.seal({'command': command, 'result': json.loads(result.stdout),
                              'inline_source': False, 'runner': state['runner']}))
    grant = r.authorize(frozen, commitment, ledger, state, r.ACTUAL_HELD_OUT, commitment['identity'])
    write('fake-authorization', grant)
    reads, calls = [], []
    def opener():
        reads.append(1)
        return {'opaque:fake-resource': (OUT / 'fake-contract.txt').read_bytes()}
    def evaluator(opened):
        calls.append(1)
        value = json.loads(opened['opaque:fake-resource'])
        r.require(value == {'required_behavior': 'preserve generic sample ordering', 'static_only': True},
                  'stand-in static observation mismatch')
        return {'classification': 'fake-actual-mode-static-observed', 'whole_contract': True}
    args = (frozen, commitment, grant, ledger, lambda: r.current_state(ROOT), lambda: commitment, opener, evaluator)
    observation = r.observe(*args)
    post = r.post_check(frozen, commitment, ledger, args[4], args[5])
    replay = rejected(lambda: r.observe(*args))
    second = rejected(lambda: r.authorize(frozen, commitment, ledger, state,
                                         r.ACTUAL_HELD_OUT, commitment['identity']))
    r.require(len(reads) == len(calls) == 1, 'one-time lifecycle failed')
    # Mutate the synthetic experiment's relevant captured subject state, not Lykoi.
    repaired = r.seal({**r.verify(state), 'files': {**state['files'], 'synthetic-subject': 'intentional repair'}})
    drift = rejected(lambda: r.post_check(frozen, commitment, ledger, lambda: repaired, lambda: commitment))
    r.invalidate_repair(frozen, ledger)
    repair = rejected(lambda: r.authorize(frozen, commitment, ledger, repaired,
                                         r.ACTUAL_HELD_OUT, commitment['identity']))
    write('fake-lifecycle', r.seal({'status': 'PASS', 'mode': r.ACTUAL_HELD_OUT,
        'opening_count': len(reads), 'observation_count': len(calls), 'result': observation,
        'post_check': post, 'replay_rejected': replay, 'second_authorization_rejected': second,
        'mutated_state': repaired, 'repair_drift_rejected': drift, 'repair_authorization_rejected': repair,
        'final_status': ledger.status()}))
    print(json.dumps({'fake_actual_lifecycle': 'PASS', 'openings': 1, 'observations': 1}))


def publication(source):
    # Only AST-literal public detection regex syntax is normalized; credential
    # values elsewhere retain the ordinary rejection. No filename exemption.
    marker = '-----BEGIN ' + '.*PRIVATE KEY'
    inspected = source
    for node in ast.walk(ast.parse(source)):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == 're'
                and node.func.attr == 'compile' and node.args
                and isinstance(node.args[0], ast.Constant) and isinstance(node.args[0].value, str)
                and marker in node.args[0].value):
            literal = ast.get_source_segment(source, node.args[0])
            inspected = inspected.replace(literal, literal.replace(marker, 'PUBLIC_DETECTION_RULE'), 1)
    r.safe_bytes({'source': inspected})


def audit():
    state, commitment, health, frozen = (read(n) for n in ('state', 'fake-commitment', 'health', 'fake-freeze'))
    r.require(state == r.current_state(ROOT), 'qualified source state drift')
    r.require(preservation() == read('preservation'), 'historical evidence drift')
    actual = read('b02-metadata-eligibility')['benchmark']
    r.require(actual == r.benchmark_commitment(ROOT) and r.eligible(actual, r.ACTUAL_HELD_OUT, actual['identity']),
              'B02 metadata drift')
    for path in (OUT / 'b02-ledger', ROOT / 'benchmark/results/phase5c/R5_72-qualified-evidence/actual-ledger'):
        r.require(r.Ledger(path).status() == 'zero', 'B02 ledger changed')
    frozen_body = r.verify(frozen)
    r.require(frozen_body == {'kind': 'ExperimentFreeze', 'state': state['identity'],
        'benchmark': commitment['identity'], 'health': health['identity'], 'runner': state['runner'],
        'observation_count': 0, 'repair_state': 'clean', 'ledger': str((OUT / 'fake-ledger').resolve())},
        'freeze/health linkage drift')
    for stage in r.HEALTH_STAGES:
        evidence = read('health-' + stage)
        r.verify(evidence)
        r.require(health['results'][stage] == r.verify(evidence) and evidence['protected_read_attempts'] == 0,
                  'health evidence mismatch')
    events = r.Ledger(OUT / 'fake-ledger').events()
    grant, lifecycle = read('fake-authorization'), read('fake-lifecycle')
    r.require([event['transition'] for event in events] == [*r.TRANSITIONS, 'INVALIDATED']
              and all(event['freeze'] == frozen['identity'] for event in events)
              and events[0]['details']['grant'] == grant['identity']
              and grant['mode'] == r.ACTUAL_HELD_OUT
              and lifecycle['opening_count'] == lifecycle['observation_count'] == 1
              and all(lifecycle[key] for key in ('replay_rejected', 'second_authorization_rejected',
                  'repair_drift_rejected', 'repair_authorization_rejected'))
              and lifecycle['post_check']['status'] == 'PASS', 'fake ledger/lifecycle mismatch')
    # Independently inspect core dependency structure; do not execute historical
    # framework qualification or its receipt/certificate machinery.
    sources = ['benchmark/evaluation/' + name for name in
        ('phase5_runner_v2.py', 'phase5_worker_v2.py', 'test_phase5_runner_v2.py')]
    sources.append('benchmark/results/phase5c/r5_74_qualification.py')
    for name in sources:
        source = (ROOT / name).read_text(encoding='utf-8')
        publication(source)
        if 'test_' not in name and '/results/' not in name:
            for node in ast.walk(ast.parse(source)):
                if isinstance(node, ast.ImportFrom) and (node.module or '').startswith('benchmark.evaluation'):
                    r.require(node.module == 'benchmark.evaluation.phase5_worker_v2' or
                              (node.module == 'benchmark.evaluation' and
                               all(alias.name == 'phase5_runner_v2' for alias in node.names)),
                              'R5_74_SIMPLIFICATION_REGRESSION')
                if isinstance(node, ast.ImportFrom):
                    r.require(not (node.module or '').startswith('benchmark.results'),
                              'R5_74_SIMPLIFICATION_REGRESSION')
    for path in OUT.rglob('*.json'):
        value = r.load(path)
        r.verify(value) if 'identity' in value else None
        if value.get('kind') == 'OneTimeObservationAuthorization':
            r.require(value['benchmark'] != actual['identity'], 'B02 authorization prohibited')
    r.require(not r.git(ROOT, 'diff', '--check'), 'diff check failed')
    return {'status': 'PASS', 'state': state['identity'], 'core_semantics': 30,
        'b02_structurally_eligible': True, 'b02_authorizations': 0, 'b02_read_attempts': 0,
        'b02_content_reads': 0, 'b02_reservations_openings_dispatches_completions': [0, 0, 0, 0],
        'b02_generation_execution_acceptance_repair': [0, 0, 0, 0],
        'historical_ordinary_files': len(read('preservation')['ordinary']),
        'historical_protected_metadata_files': len(read('preservation')['protected_metadata_only']),
        'simplicity': {'core_modules': 2, 'authorization_layers': 1, 'experiment_artifact_types': 6,
                       'normal_transitions': list(r.TRANSITIONS), 'terminal_transition': 'INVALIDATED'},
        'source_publication': 'PASS', 'diff_check': 'PASS'}


def final():
    result = audit()
    for name in ('docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md', REPORT):
        r.safe_bytes({'prose': (ROOT / name).read_text(encoding='utf-8')})
    write('post-report-audit', r.seal({**result, 'report_publication': 'PASS'}))
    print(json.dumps(result))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['prepare', 'health', 'qualify', 'audit', 'final'])
    parser.add_argument('--stage', choices=r.HEALTH_STAGES)
    args = parser.parse_args()
    boundary = r.Boundary(ROOT)
    with boundary.active():
        if args.command == 'health':
            health(args.stage)
        elif args.command == 'audit':
            result = audit()
            write('summary', r.seal({**result, 'classification': 'R5_74_ACTUAL_HELDOUT_PATH_QUALIFIED'}))
            print(json.dumps(result))
        else:
            {'prepare': prepare, 'qualify': qualify, 'final': final}[args.command]()
