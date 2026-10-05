"""Independent R5.74 evidence/publication auditor; no issuance or observation.

Preserves the frozen controller's source-publication failure. Independently reads
canonical evidence and ledger events; never repairs or resumes the experiment.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OUT = ROOT / 'benchmark/results/phase5c/R5_74-qualified-evidence'
REPORT = 'benchmark/results/phase5c/R5_74-ACTUAL-HELDOUT-AUTHORIZATION-PATH-QUALIFICATION.md'


def independent_read(path):
    raw = Path(path).read_bytes()
    def pairs(items):
        r.require(len(dict(items)) == len(items), 'duplicate evidence keys')
        return dict(items)
    value = json.loads(raw, object_pairs_hook=pairs)
    def encode(item):
        return json.dumps(item, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=False, allow_nan=False).encode()
    r.require(raw == encode(value) + b'\n', 'independent canonical check failed')
    if 'identity' in value:
        body = {key: child for key, child in value.items() if key != 'identity'}
        r.require(hashlib.sha256(encode(body)).hexdigest() == value['identity'],
                  'independent evidence hash mismatch')
    return value


def read(name):
    return independent_read(OUT / (name + '.json'))


def publication(source):
    """Only public regex placeholders, never concrete credential headers/payloads.

    Allow the exact detection placeholder in a re.compile literal or the exact
    constant concatenation assigned to marker in a publication-check function.
    Restrict by AST role and exact value, never source filename. Other source
    text and actual credential values pass through the ordinary rejecting scan.
    """
    marker = ('-----BEGIN '
              + '.*PRIVATE KEY')
    tree = ast.parse(source)
    expressions = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == 're'
                and node.func.attr == 'compile' and node.args
                and isinstance(node.args[0], ast.Constant) and type(node.args[0].value) is str
                and marker in node.args[0].value):
            expressions.append((node.args[0], False))
        if isinstance(node, ast.FunctionDef) and node.name == 'publication':
            for assignment in node.body:
                if (isinstance(assignment, ast.Assign) and len(assignment.targets) == 1
                        and isinstance(assignment.targets[0], ast.Name)
                        and assignment.targets[0].id == 'marker'):
                    expr = assignment.value
                    if (isinstance(expr, ast.BinOp) and isinstance(expr.op, ast.Add)
                            and isinstance(expr.left, ast.Constant) and type(expr.left.value) is str
                            and isinstance(expr.right, ast.Constant) and type(expr.right.value) is str
                            and expr.left.value + expr.right.value == marker):
                        expressions.append((expr, True))
    inspected = source
    for expr, whole in expressions:
        text = ast.get_source_segment(source, expr)
        replacement = repr('PUBLIC_DETECTION_RULE') if whole else text.replace(marker, 'PUBLIC_DETECTION_RULE')
        inspected = inspected.replace(text, replacement, 1)
    r.safe_bytes({'source': inspected})
    return {'status': 'PASS', 'public_detection_expressions': len(expressions)}


def check():
    state, commitment, health, frozen, grant, lifecycle = (read(name) for name in
        ('state', 'fake-commitment', 'health', 'fake-freeze', 'fake-authorization', 'fake-lifecycle'))
    r.require(r.current_state(ROOT) == state and state['semantic_count'] == 30, 'current-state drift')
    expected_freeze = {'kind': 'ExperimentFreeze', 'state': state['identity'], 'benchmark': commitment['identity'],
        'health': health['identity'], 'runner': state['runner'], 'observation_count': 0, 'repair_state': 'clean',
        'ledger': str((OUT / 'fake-ledger').resolve())}
    r.require({key: value for key, value in frozen.items() if key != 'identity'} == expected_freeze,
              'freeze linkage mismatch')
    r.require(health['state'] == state['identity'] and set(health['results']) == set(r.HEALTH_STAGES),
              'health linkage mismatch')
    for stage in r.HEALTH_STAGES:
        evidence = read('health-' + stage)
        r.require(evidence['status'] == 'PASS' and evidence['state'] == state['identity']
                  and evidence['protected_read_attempts'] == 0
                  and health['results'][stage] == {k: v for k, v in evidence.items() if k != 'identity'},
                  'stage health mismatch')
    r.require(read('health-runner')['detail']['passed'] == 74, 'runner evidence incomplete')
    actual = read('b02-metadata-eligibility')['benchmark']
    r.require(actual == r.benchmark_commitment(ROOT) and r.eligible(actual, r.ACTUAL_HELD_OUT, actual['identity']),
              'B02 structural metadata mismatch')
    for directory in (OUT / 'b02-ledger', ROOT / 'benchmark/results/phase5c/R5_72-qualified-evidence/actual-ledger',
                      ROOT / 'benchmark/results/phase5c/R5_74-evidence/b02-ledger'):
        r.require(directory.is_dir() and not list(directory.iterdir()), 'B02 ledger not empty')
    r.require(grant['mode'] == r.ACTUAL_HELD_OUT and grant['operation'] == r.STATIC_OPERATION
              and grant['benchmark'] == commitment['identity'] and grant['freeze'] == frozen['identity']
              and grant['ledger'] == frozen['ledger']
              and all(grant[key] is False for key in ('generation', 'execution', 'acceptance', 'repair')),
              'fake authorization mismatch')
    paths = sorted((OUT / 'fake-ledger').glob('*.json'))
    r.require([path.name for path in paths] == [f'{i:02d}.json' for i in range(6)], 'ledger sequence mismatch')
    events = [independent_read(path) for path in paths]
    r.require([event['transition'] for event in events] ==
              ['AUTHORIZED', 'OPENING_RESERVED', 'OPENING_CONSUMED', 'DISPATCHED', 'COMPLETED', 'INVALIDATED'],
              'independent transition mismatch')
    for i, event in enumerate(events):
        r.require(event['freeze'] == frozen['identity'] and event['previous'] ==
                  (events[i - 1]['identity'] if i else None), 'independent ledger linkage mismatch')
    r.require(events[0]['details']['grant'] == grant['identity']
              and events[4]['details']['benchmark'] == commitment['identity']
              and lifecycle['opening_count'] == lifecycle['observation_count'] == 1
              and lifecycle['post_check']['status'] == 'PASS' and lifecycle['final_status'] == 'multiple/invalid'
              and all(lifecycle[key] for key in ('replay_rejected', 'second_authorization_rejected',
                  'repair_drift_rejected', 'repair_authorization_rejected'))
              and lifecycle['mutated_state']['identity'] != state['identity'], 'lifecycle evidence mismatch')
    r.require(r.digest((OUT / 'fake-contract.txt').read_bytes()) ==
              commitment['resources']['opaque:fake-resource']['commitment'], 'stand-in commitment mismatch')
    invocation = read('invocation')
    r.require('-c' not in invocation['command'] and invocation['inline_source'] is False
              and invocation['runner'] == state['runner'] and invocation['result']['status'] == 'PASS'
              and invocation['result']['protected_read_attempts'] == 0, 'structured invocation mismatch')
    preserved = read('preservation')
    for row in preserved['ordinary']:
        r.require(r.digest((ROOT / row['path']).read_bytes()) == row['sha256'], 'historical evidence changed')
    for row in preserved['protected_metadata_only']:
        stat = (ROOT / row['path']).stat()
        r.require(stat.st_size == row['size'] and stat.st_mtime_ns == row['mtime_ns'], 'protected metadata changed')
    for path in OUT.rglob('*.json'):
        value = independent_read(path)
        r.safe_bytes(value)
        if value.get('kind') == 'OneTimeObservationAuthorization':
            r.require(value['benchmark'] != actual['identity'], 'B02 authorization created')
    sources = ['benchmark/evaluation/' + name for name in
               ('phase5_runner_v2.py', 'phase5_worker_v2.py', 'test_phase5_runner_v2.py')]
    sources += ['benchmark/results/phase5c/r5_74_qualification.py',
                'benchmark/results/phase5c/r5_74_readonly_audit.py']
    source_checks = {}
    for name in sources:
        source = (ROOT / name).read_text(encoding='utf-8')
        source_checks[name] = {**publication(source), 'sha256': r.digest(source.encode())}
        if name in sources[:2]:
            for node in ast.walk(ast.parse(source)):
                if isinstance(node, ast.ImportFrom) and (node.module or '').startswith('benchmark.evaluation'):
                    r.require(node.module == 'benchmark.evaluation.phase5_worker_v2' or
                              (node.module == 'benchmark.evaluation' and
                               all(alias.name == 'phase5_runner_v2' for alias in node.names)),
                              'R5_74_SIMPLIFICATION_REGRESSION')
                if isinstance(node, ast.ImportFrom):
                    r.require(not (node.module or '').startswith('benchmark.results'),
                              'R5_74_SIMPLIFICATION_REGRESSION')
    # Adversarial publication check: concrete credential content cannot take
    # the exact public-placeholder AST exception.
    for source in ('value = ' + repr('SECRET' + '[' + 'fake]'),
                   'marker = ' + repr('-----BEGIN '
                                     + 'RSA PRIVATE KEY-----')):
        try:
            publication(source)
        except r.Rejected:
            continue
        raise r.Rejected('publication concrete value accepted')
    r.require(not r.git(ROOT, 'diff', '--check'), 'diff check failed')
    return {'status': 'PASS', 'classification': 'R5_74_ACTUAL_HELDOUT_PATH_QUALIFIED',
        'state': state['identity'], 'benchmark': actual['identity'], 'fake_freeze': frozen['identity'],
        'health': health['identity'], 'core_semantics': 30, 'b02_structurally_eligible': True,
        'b02_read_attempts': 0, 'b02_content_reads': 0, 'b02_authorizations': 0,
        'b02_reservations_openings_dispatches_completions': [0, 0, 0, 0],
        'b02_generation_execution_acceptance_repair': [0, 0, 0, 0],
        'fake_actual_openings': 1, 'fake_actual_observations': 1,
        'historical_ordinary_files': len(preserved['ordinary']),
        'historical_protected_metadata_files': len(preserved['protected_metadata_only']),
        'source_publication': source_checks,
        'simplicity': {'core_modules': 2, 'authorization_layers': 1, 'experiment_artifact_types': 6,
            'normal_transitions': list(r.TRANSITIONS), 'terminal_transition': 'INVALIDATED',
            'qualification_support_files': 3},
        'preserved_audit_failure': 'source-text false positive on public detection-marker concatenation; no replay',
        'diff_check': 'PASS'}


def audit():
    result = check()
    pins = [{'path': path.relative_to(ROOT).as_posix(), 'sha256': r.digest(path.read_bytes())}
            for path in sorted(OUT.rglob('*.json'))]
    r.persist(OUT / 'summary.json', r.seal({**result, 'artifact_pins': pins}))
    print(json.dumps({key: value for key, value in result.items() if key != 'source_publication'}))


def final():
    result = check()
    summary = read('summary')
    for row in summary['artifact_pins']:
        r.require(r.digest((ROOT / row['path']).read_bytes()) == row['sha256'], 'artifact pin changed')
    for name, row in summary['source_publication'].items():
        r.require(r.digest((ROOT / name).read_text(encoding='utf-8').encode()) == row['sha256'], 'source pin changed')
    docs = ('docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md', REPORT,
            'benchmark/results/phase5c/R5_74-development-failure.md',
            'benchmark/results/phase5c/R5_74-publication-audit-failure.md')
    for name in docs:
        r.safe_bytes({'prose': (ROOT / name).read_text(encoding='utf-8')})
    r.persist(OUT / 'post-report-audit.json', r.seal({'status': 'PASS', 'summary': summary['identity'],
        'publication': 'PASS', 'diff_check': result['diff_check'], 'b02_read_attempts': 0,
        'b02_authorizations': 0, 'documentation': [
            {'path': name, 'sha256': r.digest((ROOT / name).read_bytes())} for name in docs]}))
    print(json.dumps({'post_report_audit': 'PASS', 'publication': 'PASS', 'b02_accounting': 'zero'}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['audit', 'final'])
    args = parser.parse_args()
    with r.Boundary(ROOT).active():
        {'audit': audit, 'final': final}[args.command]()
