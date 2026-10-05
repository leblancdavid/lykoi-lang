"""Record and independently audit the first, terminal R5.63 freeze failure.

No qualification execution, identity reconstruction, repair or retry is exposed.
The failed orchestration source and its already-persisted plan remain immutable.
"""

import ast
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.evaluation.preexposure_r5_45 import unseal

OUT = ROOT / 'benchmark/results/phase5c/R5_63-evidence'
RUNNER = 'benchmark/results/phase5c/r5_63_qualification.py'


def read(name):
    raw = (OUT / (name + '.json')).read_bytes()
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    publication.safe_bytes(value)
    return value


def write(name, value):
    publication.persist(OUT / (name + '.json'), value)


def record():
    assert not (OUT / 'summary.json').exists()
    plan = read('stage-plan')
    unseal(plan)
    assert (OUT / 'worker-registry.json').exists()
    assert not (OUT / 'qualification-identity.json').exists()
    assert not (OUT / 'freeze.json').exists()
    source = (ROOT / RUNNER).read_bytes()
    tree = ast.parse(source)
    freeze = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'freeze')
    assignments = [n for n in ast.walk(freeze) if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'identity' for t in n.targets)]
    assert len(assignments) == 1
    expression = assignments[0].value
    assert ast.unparse(expression.func) == 'tier.seal'
    assert 'authorization' in [k.value for k in expression.args[0].keys]
    failure = {'status': 'FAIL', 'stage': 'qualification-identity-publication',
        'exception_class': 'SecretRejected', 'diagnostic': 'SECRET_VALUE_REJECTED: credential field field authorization',
        'rejected_field': 'authorization', 'rejected_value_kind': 'public authority-policy digest',
        'command': 'python -B -S benchmark/results/phase5c/r5_63_qualification.py freeze',
        'exit': 1, 'attempts': 1, 'plan': plan['identity'],
        'runner_sha256': digest(source), 'plan_bytes_sha256': digest((OUT / 'stage-plan.json').read_bytes()),
        'qualification_identity_issued': False, 'production_execution_started': False,
        'protected_read_attempts': 0, 'protected_content_loaded': False,
        'repair_permitted': False, 'retry_permitted': False, 'resume_permitted': False}
    write('terminal-failure', failure)
    stages = {s['name']: 'NOT_RUN' for group in ('preflight', 'regressions', 'integration')
              for s in plan[group]}
    stages['qualification-identity-publication'] = 'FAIL'
    write('summary', {'classification': 'R5_63_PROTOCOL_HALT',
        'failed_stage': 'qualification-identity-publication', 'stages': stages,
        'plan': plan['identity'], 'qualification_identity': None,
        'regression_stages': len(plan['regressions']), 'integration_stages': len(plan['integration']),
        'starting_state': 'NOT_RUN', 'fresh_qualified_authority_issued': False,
        'fresh_capsule_issued': False, 'production_certificate_issued': False,
        'cooperative_workspace_materialized': False, 'production_gate_qualified': False,
        'production_batches': 0, 'production_receipts': 0, 'historical_receipts_reused': 0,
        'synthetic_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'b02_accounting': {'exposure': 0, 'reservations': 0, 'dispatches': 0, 'completions': 0},
        'core_semantics': 30, 'semantic_change': False, 'phase5c': 'paused',
        'repair_occurred': False, 'retry_occurred': False, 'resume_permitted': False,
        'next': 'owner adjudication of identity publication failure; no B02 authorization'})
    write('quarantine', {'classification': 'R5_63_PROTOCOL_HALT', 'quarantine': True,
        'scope': 'entire R5.63 candidate, frozen plan and worker registry',
        'reason': 'terminal qualification identity publication rejection',
        'plan': plan['identity'], 'production_receipts': 0, 'protected_exposure': False,
        'repair_permitted': False, 'retry_permitted': False, 'resume_permitted': False})
    print({'classification': 'R5_63_PROTOCOL_HALT', 'regression_stages': len(plan['regressions']),
           'plan': plan['identity'], 'qualification_identity': 'NOT_ISSUED'})


def audit():
    summary, failure, plan = read('summary'), read('terminal-failure'), read('stage-plan')
    unseal(plan)
    assert summary['classification'] == 'R5_63_PROTOCOL_HALT'
    assert summary['plan'] == failure['plan'] == plan['identity']
    assert digest((ROOT / RUNNER).read_bytes()) == failure['runner_sha256']
    assert digest((OUT / 'stage-plan.json').read_bytes()) == failure['plan_bytes_sha256']
    assert digest(canonical(read('worker-registry'))) == plan['worker_registry']
    assert read('quarantine')['quarantine'] is True
    assert not any((OUT / n).exists() for n in ('qualification-identity.json', 'freeze.json',
        'batches', 'certificate.json', 'capsule.json', 'qualified-authority.json', 'production-gate'))
    assert not list(OUT.rglob('receipt-*.json'))
    assert summary['production_batches'] == summary['production_receipts'] == 0
    assert summary['synthetic_accounting'] == {'reservations': 0, 'dispatches': 0, 'completions': 0}
    assert summary['b02_accounting'] == {'exposure': 0, 'reservations': 0, 'dispatches': 0, 'completions': 0}
    assert summary['repair_occurred'] is summary['retry_occurred'] is False
    baseline = read('preservation-baseline')
    resources = {r.path.relative_to(ROOT).as_posix() for r in guard.repository_resources(ROOT)}
    for name, pin in baseline['files'].items():
        assert name not in resources and digest((ROOT / name).read_bytes()) == pin
    for name, row in baseline['sealed_metadata_only'].items():
        assert name in resources
        info = (ROOT / name).stat()
        assert row == {'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
    changed = subprocess.check_output(['git', 'diff', '--name-only', '--', 'benchmark/results'],
                                     cwd=ROOT, text=True).splitlines()
    assert changed == []
    for round_, expected, field in ((60, 'R5_60_PROTOCOL_HALT', 'primary_classification'),
                                    (61, 'R5_61_PROTECTED_RESOURCE_GAP', 'classification'),
                                    (62, 'R5_62_MEDIATED_CHILD_EXECUTION_QUALIFIED', 'classification')):
        row = loads((OUT.parent / f'R5_{round_}-evidence/summary.json').read_bytes())
        assert row[field] == expected
    prohibited = exclusion.index()['tests']
    ids = [i for s in plan['regressions'] if s['name'].startswith('harness-')
           for i in s.get('selection', {}).get('identities', []) if i in prohibited]
    assert len(ids) == len(set(ids)) == len(prohibited) == 36
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    from benchmark.results.phase5c.r5_43_qualification import contamination
    assert SCHEMA['core_constructs'] == summary['core_semantics'] == 30
    clean = contamination()
    assert clean['findings'] == []
    evidence = {p.name: digest(p.read_bytes()) for p in OUT.glob('*.json')}
    for path in OUT.glob('*.json'):
        read(path.stem)
    write('independent-stopped-audit', {'status': 'PASS',
        'scope': 'terminal freeze failure and stopped-candidate integrity; no production promotion',
        'production_final_audit': 'NOT_RUN', 'plan_unchanged': True, 'runner_unchanged': True,
        'qualification_identity': 'NOT_ISSUED', 'authority': 'NOT_RUN', 'capsule': 'NOT_ISSUED',
        'certificate': 'NOT_ISSUED', 'receipt_set': 'EMPTY', 'cross_batch_linkage': 'NOT_RUN',
        'mediated_execution': 'NOT_RUN', 'workspace': 'NOT_MATERIALIZED',
        'observation_pre_post': 'NOT_RUN', 'exclusion_pin': exclusion.INDEX_PIN,
        'prohibited_metadata_ids': 36, 'fresh_child_skip_execution': 'NOT_RUN',
        'historical_unsealed_byte_digests_verified': len(baseline['files']),
        'sealed_result_metadata_verified': len(baseline['sealed_metadata_only']),
        'historical_results_diff': changed, 'historical_classifications_preserved': True,
        'canonical_publication_integrity': 'PASS', 'evidence_sha256': evidence,
        'contamination': clean, 'core_semantics': 30, 'b02_accounting': summary['b02_accounting'],
        'synthetic_accounting': summary['synthetic_accounting'], 'no_repair_or_resume': True})
    print({'independent_stopped_audit': 'PASS', 'historical_unsealed': len(baseline['files']),
           'sealed_metadata_only': len(baseline['sealed_metadata_only'])})


def publication_check():
    assert (OUT / 'independent-stopped-audit.json').exists()
    names = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--modified'],
                                   cwd=ROOT, text=True).splitlines()
    pins, dispositions = {}, {}
    resources = {r.path.relative_to(ROOT).as_posix() for r in guard.repository_resources(ROOT)}
    for name in sorted(set(names)):
        path = ROOT / name
        if path.suffix in ('.py', '.md', '.json'):
            assert name not in resources
            raw = path.read_bytes()
            dispositions[name] = publication.check_source(name, raw)
            pins[name] = digest(raw)
            check = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(path)],
                                   cwd=ROOT, capture_output=True, timeout=10)
            assert check.returncode in (0, 1) and not check.stdout
    check = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10)
    assert check.returncode == 0
    for path in OUT.glob('*.json'):
        read(path.stem)
    write('publication-integrity', {'status': 'PASS', 'scope': 'stopped-run artifacts and documentation',
        'source_sha256': pins, 'source_dispositions': dispositions, 'git_diff_check': 'PASS',
        'new_file_whitespace_check': 'PASS', 'production_security_regressions': 'NOT_RUN',
        'ai_independence_regressions': 'NOT_RUN', 'b02_exposure': 0})
    print({'publication_integrity': 'PASS', 'git_diff_check': 'PASS'})


if __name__ == '__main__':
    {'record': record, 'audit': audit, 'publication': publication_check}[sys.argv[1]]()
