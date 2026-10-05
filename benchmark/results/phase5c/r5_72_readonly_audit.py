"""Independent read-only final qualification audit; never replays a lifecycle.

The first driver's source-as-value scan rejects its own public detection regex.
This audit distinguishes that AST-bound regex from raw credential material.
It does not modify the frozen implementation or recreate historical evidence.
"""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OUT = ROOT / 'benchmark/results/phase5c/R5_72-qualified-evidence'


def read(name):
    raw = (OUT / (name + '.json')).read_bytes()
    value = json.loads(raw)
    r.require(raw == json.dumps(value, sort_keys=True, separators=(',', ':'),
        ensure_ascii=False, allow_nan=False).encode() + b'\n', 'independent canonical check failed')
    if 'identity' in value:
        body = {k: v for k, v in value.items() if k != 'identity'}
        pin = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(',', ':'),
            ensure_ascii=False, allow_nan=False).encode()).hexdigest()
        r.require(pin == value['identity'], 'independent evidence hash mismatch')
    return value


def source_publication(source):
    """Public regex syntax has no private key header/payload.

    The sole lexical exception must be inside a literal argument of re.compile
    and contain the metacharacter placeholder, never an actual algorithm name.
    Other recognizable credentials/marked values reject without echoing them.
    No source filename or producer identity confers an exception.
    """
    tree = ast.parse(source)
    marker = ('-----BEGIN '
              + '.*PRIVATE KEY')
    sources = []
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name) and node.func.value.id == 're'
                and node.func.attr == 'compile' and node.args
                and isinstance(node.args[0], ast.Constant) and type(node.args[0].value) is str
                and marker in node.args[0].value):
            literal = ast.get_source_segment(source, node.args[0])
            sources.append(literal)
    # Remove only the public metacharacter marker inside the verified regex
    # literal. Literal header/credential values elsewhere remain inspected.
    inspected = source
    for literal in sources:
        inspected = inspected.replace(literal, literal.replace(marker, 'PUBLIC_DETECTION_RULE'), 1)
    r.safe_bytes({'source': inspected})
    return {'status': 'PASS', 'public_regex_literals': len(sources)}


def audit():
    state, benchmark, health, frozen = (read(n) for n in ('state', 'benchmark', 'health', 'freeze'))
    r.require(r.current_state(ROOT) == state, 'frozen implementation changed')
    r.require(r.benchmark_commitment(ROOT) == benchmark, 'sealed metadata changed')
    for stage in r.HEALTH_STAGES:
        result = read('health-' + stage)
        r.require(result['state'] == state['identity'] and result['status'] == 'PASS'
                  and result['protected_read_attempts'] == 0, 'health evidence failed')
        r.require(health['results'][stage] == r.verify(result), 'health linkage mismatch')
    r.require(r.freeze(state, benchmark, health) == frozen, 'freeze mismatch')
    preserved = read('preservation')
    for row in preserved['ordinary']:
        r.require(hashlib.sha256((ROOT / row['path']).read_bytes()).hexdigest() == row['sha256'],
                  'historical evidence changed')
    for row in preserved['protected_metadata_only']:
        stat = (ROOT / row['path']).stat()
        r.require(stat.st_size == row['size'] and stat.st_mtime_ns == row['mtime_ns'], 'protected metadata drift')
    r.require(r.Ledger(OUT / 'actual-ledger').status() == 'zero', 'B02 accounting changed')
    events = r.Ledger(OUT / 'synthetic-ledger').events()
    fake, grant, lifecycle = (read(n) for n in ('synthetic-freeze', 'synthetic-authorization', 'synthetic-lifecycle'))
    r.require([e['transition'] for e in events] == [*r.TRANSITIONS, 'INVALIDATED']
              and all(e['freeze'] == fake['identity'] for e in events)
              and events[0]['details']['grant'] == grant['identity']
              and lifecycle['post_check_before_repair']['status'] == 'PASS'
              and lifecycle['observations'] == lifecycle['openings'] == 1
              and lifecycle['replay_rejected'] and lifecycle['repair_rejected'], 'synthetic evidence failed')
    for path in OUT.rglob('*.json'):
        r.load(path)
    sources = ('benchmark/evaluation/phase5_runner_v2.py', 'benchmark/evaluation/phase5_worker_v2.py',
               'benchmark/evaluation/test_phase5_runner_v2.py',
               'benchmark/results/phase5c/r5_72_qualification.py',
               'benchmark/results/phase5c/r5_72_readonly_audit.py')
    source_checks = {}
    for name in sources:
        source = (ROOT / name).read_text(encoding='utf-8')
        try:
            checked = source_publication(source)
        except r.Rejected:
            raise r.Rejected('source publication rejected: ' + name) from None
        source_checks[name] = {**checked, 'sha256': r.digest(source.encode())}
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom) and node.module == 'benchmark.evaluation':
                r.require(all(a.name == 'phase5_runner_v2' for a in node.names), 'R5_72_SIMPLIFICATION_FAILURE')
            if isinstance(node, ast.ImportFrom) and (node.module or '').startswith('benchmark.results'):
                raise r.Rejected('R5_72_SIMPLIFICATION_FAILURE')
    # Behavioral tests are independent of implementation event construction.
    r.require(read('health-runner')['detail']['passed'] == 30, 'missing runner qualification tests')
    diff = r.git(ROOT, 'diff', '--check')
    r.require(not diff, 'whitespace check failed')
    artifact_pins = [{'path': p.relative_to(ROOT).as_posix(), 'sha256': r.digest(p.read_bytes())}
                     for p in sorted(OUT.rglob('*.json'))]
    summary = r.seal({'classification': 'R5_72_SIMPLIFIED_PHASE5_RUNNER_QUALIFIED',
        'state': state['identity'], 'benchmark': benchmark['identity'], 'freeze': frozen['identity'],
        'health': health['identity'], 'core_semantics': 30, 'protected_read_attempts': 0,
        'protected_content_reads': 0, 'b02_accounting': [0, 0, 0, 0], 'b02_opening': [0, 0],
        'actual_authorizations': 0, 'actual_ledger': 'zero', 'repair_state': 'clean',
        'synthetic_openings': 1, 'synthetic_observations': 1,
        'historical_ordinary_files': len(preserved['ordinary']),
        'protected_historical_metadata': len(preserved['protected_metadata_only']),
        'source_publication': source_checks, 'artifact_integrity': artifact_pins,
        'simplicity': {'core_modules': 2, 'experiment_artifact_types': 6, 'authorization_layers': 1,
            'required_observation_transitions': 5, 'invalidation_transition': 1,
            'qualification_support_files': 3},
        'preserved_driver_failure': 'source-as-value publication false positive on public regex; not replayed',
        'next_gate': 'R5.73 separately authorized actual one-shot static experiment; no repair/retry'})
    r.persist(OUT / 'summary.json', summary)
    print({k: summary[k] for k in ('classification', 'state', 'benchmark', 'freeze', 'health',
        'core_semantics', 'historical_ordinary_files', 'protected_historical_metadata', 'simplicity')})


def final():
    summary = read('summary')
    r.require(r.current_state(ROOT)['identity'] == summary['state'], 'frozen state drift')
    r.require(r.benchmark_commitment(ROOT)['identity'] == summary['benchmark'], 'sealed metadata drift')
    for row in summary['artifact_integrity']:
        r.require(r.digest((ROOT / row['path']).read_bytes()) == row['sha256'], 'qualification evidence drift')
    for name, row in summary['source_publication'].items():
        source = (ROOT / name).read_text(encoding='utf-8')
        r.require(r.digest(source.encode()) == row['sha256'], 'qualification source drift')
        source_publication(source)
    docs = ('docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md',
            'benchmark/results/phase5c/R5_72-SIMPLIFIED-PHASE5-RUNNER-QUALIFICATION.md')
    for name in docs:
        r.safe_bytes({'prose': (ROOT / name).read_text(encoding='utf-8')})
    r.require(not r.git(ROOT, 'diff', '--check'), 'whitespace check failed')
    r.persist(OUT / 'post-report-audit.json', r.seal({'status': 'PASS', 'summary': summary['identity'],
        'publication': 'PASS', 'diff_check': 'PASS', 'protected_read_attempts': 0,
        'frozen_state': summary['state'], 'documentation': [
            {'path': name, 'sha256': r.digest((ROOT / name).read_bytes())} for name in docs]}))
    print({'post_report_read_only_validation': 'PASS', 'publication': 'PASS', 'b02': 'unopened'})


if __name__ == '__main__':
    with r.Boundary(ROOT).active():
        {'audit': audit, 'final': final}[sys.argv[1]]()
