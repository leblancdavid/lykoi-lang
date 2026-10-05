"""Read-only stopped-state evidence; no authorization, opener or evaluator.

This is not a retry of R5.73 preflight and cannot resume the halted experiment.
"""
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OLD = ROOT / 'benchmark/results/phase5c/R5_72-qualified-evidence'
OUT = ROOT / 'benchmark/results/phase5c'
REPORT = 'R5_73-ONE-SHOT-HELD-OUT-B02-STATIC-SUPPORT-TRANSFER.md'


def check():
    state, benchmark, health, frozen, summary, publication = (
        r.load(OLD / (name + '.json')) for name in
        ('state', 'benchmark', 'health', 'freeze', 'summary', 'post-report-audit'))
    for value in (state, benchmark, health, frozen, summary, publication):
        r.verify(value)
    observed = r.current_state(ROOT)
    r.require(observed == state, 'stopped CurrentState changed')
    r.require(r.benchmark_commitment(ROOT) == benchmark, 'stopped commitment changed')
    r.require(r.health_record(state, health['results']) == health, 'health invalid')
    for stage in r.HEALTH_STAGES:
        row = r.load(OLD / ('health-' + stage + '.json'))
        r.require(r.verify(row) == health['results'][stage], 'health linkage changed')
        r.require(row['protected_read_attempts'] == 0, 'health protected attempts')
    r.require(r.freeze(state, benchmark, health) == frozen, 'freeze changed')
    r.require(summary['classification'] == 'R5_72_SIMPLIFIED_PHASE5_RUNNER_QUALIFIED'
              and publication['status'] == 'PASS'
              and publication['summary'] == summary['identity'], 'qualification invalid')
    for row in summary['artifact_integrity']:
        r.require(r.digest((ROOT / row['path']).read_bytes()) == row['sha256'],
                  'qualification artifact changed')
    ledger = r.Ledger(OLD / 'actual-ledger')
    r.require(ledger.status() == 'zero' and not ledger.events(), 'actual ledger nonzero')
    source = ROOT / 'benchmark/evaluation/phase5_runner_v2.py'
    tree = ast.parse(source.read_text(encoding='utf-8'))
    functions = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    issuer = functions['authorize_synthetic']
    observer = functions['observe']
    issuer_literals = [node.value for node in ast.walk(issuer) if isinstance(node, ast.Constant)]
    observer_literals = [node.value for node in ast.walk(observer) if isinstance(node, ast.Constant)]
    r.require('R5_72_PROTOCOL_HALT: actual benchmark authorization prohibited' in issuer_literals
              and 'synthetic-only' in observer_literals and 'synthetic' in observer_literals,
              'synthetic restriction missing')
    return {
        'current_state': state['identity'], 'post_state': observed['identity'],
        'experiment_freeze': frozen['identity'], 'health': health['identity'],
        'benchmark': benchmark['identity'], 'runner': state['runner'],
        'health_result': 'PASS_REVALIDATED_INHERITED_EVIDENCE_NOT_FRESH_EXECUTION',
        'contamination': health['results']['matrix-schema-trace-contamination'],
        'commitments': benchmark['resources'],
        'frozen_pins': {name: row['commitment'] for name, row in benchmark['resources'].items()
                        if row['frozen']},
        'ledger': ledger.status(), 'semantic_count': observed['semantic_count'],
        'no_repair': observed == state,
        'actual_path': {'issuer': 'authorize_synthetic', 'issuer_line': issuer.lineno,
                        'observer': 'observe', 'observer_line': observer.lineno,
                        'scope': 'synthetic-only', 'actual_authorization_available': False},
    }


def main():
    boundary = r.Boundary(ROOT)
    with boundary.active():
        result = check()
        if sys.argv[1] == 'record':
            value = r.seal({
                'kind': 'R5_73StoppedExperimentEvidence',
                'classification': 'R5_73_PREEXPOSURE_HALT',
                'question_result': 'NOT_OBSERVED', 'lifecycle': 'NOT_RUN',
                'preexposure_invocation': 'FAIL_PYTHON_SYNTAX_ERROR_BEFORE_IMPORT',
                'cause': 'Frozen runner only authorizes and observes synthetic resources',
                'stopped_integrity': result,
                'accounting': {name: 0 for name in (
                    'read_attempts', 'content_reads', 'authorizations', 'opening_reservations',
                    'openings', 'exposures', 'observation_dispatches', 'observation_completions',
                    'generation', 'execution', 'frozen_acceptance', 'repair')},
                'support_results': {name: 'NOT_EVALUATED' for name in (
                    'contract_count', 'checked_plans', 'rejections', 'readiness', 'audit',
                    'admission', 'compatibility', 'whole_contract', 'unsupported_requirements')},
                'replay_prevention': 'No grant issued; frozen actual path rejects before reservation',
                'audit_source': r.digest(Path(__file__).read_bytes()),
                'protected_read_attempts': boundary.attempts,
            })
            r.persist(OUT / 'R5_73-stopped-evidence.json', value)
        elif sys.argv[1] == 'final':
            value = r.load(OUT / 'R5_73-stopped-evidence.json')
            r.verify(value)
            r.require(value['stopped_integrity'] == result, 'stopped evidence drift')
            r.require(value['audit_source'] == r.digest(Path(__file__).read_bytes()), 'audit drift')
            names = ['docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md',
                     'benchmark/results/phase5c/' + REPORT]
            for name in names:
                r.safe_bytes({'prose': (ROOT / name).read_text(encoding='utf-8')})
            r.safe_bytes({'source': Path(__file__).read_text(encoding='utf-8')})
            r.require(not r.git(ROOT, 'diff', '--check'), 'whitespace failure')
            r.persist(OUT / 'R5_73-post-report-audit.json', r.seal({
                'kind': 'R5_73StoppedPublicationAudit', 'status': 'PASS',
                'evidence': value['identity'], 'state': result['post_state'],
                'publication': 'PASS', 'diff_check': 'PASS',
                'protected_read_attempts': boundary.attempts,
                'documents': {name: r.digest((ROOT / name).read_bytes()) for name in names},
            }))
        else:
            raise ValueError('unknown stopped-audit operation')
        print(r.canonical({'classification': value['classification'],
                           'stopped_integrity': result, 'protected_read_attempts': boundary.attempts}).decode())


if __name__ == '__main__':
    main()
