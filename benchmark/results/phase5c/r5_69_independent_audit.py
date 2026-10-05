"""Separate-process stopped-candidate integrity audit, never a gate retry."""
import ast
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation.security_r5_47 import SecretRejected
from benchmark.evaluation.preexposure_r5_45 import unseal
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

OUT = ROOT / 'benchmark/results/phase5c/R5_69-evidence'
PROTECTED = {r.path.resolve() for r in guard.repository_resources(ROOT)}
ATTEMPTS = []


def protect(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        if Path(os.fsdecode(args[0])).resolve() in PROTECTED:
            ATTEMPTS.append('DENIED_BEFORE_CONTENT')
            raise RuntimeError('R5_69_PROTOCOL_HALT')


sys.addaudithook(protect)


def ordinary(path):
    assert path.resolve() not in PROTECTED
    return path.read_bytes()


def read(name):
    raw = ordinary(OUT / (name + '.json'))
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    context = {'schema': schemas.QUALIFICATION_IDENTITY,
               'schema_identity': schemas.QUALIFICATION_IDENTITY_PIN} if name == 'qualification-identity' else {}
    publication.safe_bytes(value, **context)
    return value


def audit():
    plan, identity, freeze = [read(n) for n in ('stage-plan', 'qualification-identity', 'freeze')]
    failure, terminal = [read(n) for n in ('starting-state-failure', 'terminal-stop')]
    # The qualification already stopped and its attempted summary was refused.
    # Derive a separate audit inventory from persisted artifacts; do not retry
    # that publication, edit frozen orchestration or resume qualification.
    assert not (OUT / 'summary.json').exists()
    states = {r['name']: 'NOT_RUN' for r in plan['preflight'] + plan['regressions'] + plan['integration']}
    states.update({'mechanism-continuity': 'PASS', terminal['failed_stage']: 'FAIL'})
    summary = {'classification': terminal['classification'], 'plan': plan['identity'],
        'qualification': identity['identity'], 'production_batches': 0, 'production_receipts': 0,
        'production_certificates': 0, 'synthetic_accounting': [0, 0, 0], 'b02_accounting': [0, 0, 0, 0],
        'opening_accounting': [0, 0], 'b02_read_attempts': 0, 'b02_content_reads': 0,
        'repair_occurred': False, 'retry_occurred': False, 'resume_occurred': False,
        'core_semantics': 30, 'stages': states, 'scope': 'independent stopped artifact inventory',
        'qualification_summary_publication': 'REJECTED_NOT_RETRIED'}
    unseal(plan)
    unseal(identity)
    assert plan['identity'] == identity['plan'] == freeze['plan'] == summary['plan']
    assert identity['identity'] == freeze['qualification'] == summary['qualification']
    assert digest(ordinary(ROOT / 'benchmark/results/phase5c/r5_69_qualification.py')) == identity['orchestration']
    assert digest(canonical(read('worker-registry'))) == identity['registry'] == plan['worker_registry']
    for name, pin in plan['implementation_sha256'].items():
        assert digest(ordinary(ROOT / name)) == pin
    policy = read('authority-policy')
    assert digest(canonical(policy)) == plan['authority_policy']
    assert len(policy['members']) == 1083
    sealed_names = {n for n, r in policy['members'].items() if r['classification'] == 'SEALED'}
    assert len(sealed_names) == 11
    assert sealed_names == {p.relative_to(ROOT).as_posix() for p in PROTECTED} & set(policy['members'])
    assert len(sealed_names & set(policy['frozen_authority'])) == 2
    old_inventory = loads(ordinary(OUT.parent / 'R5_66-evidence/sealed-inventory.json'))
    assert {n: policy['members'][n] for n in sealed_names} == old_inventory['members']
    # Independent source analysis of the exact executed call path, not another
    # invocation of the stopped gate or its validator.
    tree = ast.parse(ordinary(ROOT / failure['component']))
    gate = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'StaticGate')
    prepare = next(n for n in gate.body if isinstance(n, ast.FunctionDef) and n.name == 'prepare')
    assert ast.unparse(prepare.body[1].value) == 'validate(self.cert, self.capsule, self.evidence, self.policy, self.capture())'
    validate = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'validate')
    assert any(isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == 'certificate'
               for n in ast.walk(validate))
    certificate = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'certificate')
    first_if = next(n for n in certificate.body if isinstance(n, ast.If))
    assert "policy['infrastructure']" in ast.unparse(first_if.test)
    assert isinstance(first_if.body[0], ast.Raise)
    v3_tree = ast.parse(ordinary(ROOT / 'benchmark/evaluation/certificate_r5_55.py'))
    fields = next(n.value for n in v3_tree.body if isinstance(n, ast.Assign)
                  and any(isinstance(t, ast.Name) and t.id == 'POLICY_FIELDS' for t in n.targets))
    assert 'infrastructure' not in ast.literal_eval(fields)
    assert failure['validator_invoked'] and failure['rejected']
    assert failure['input_protocol'] == 'lykoi-production-certificate-v3'
    assert failure['input_mode'] == plan['mode'] == 'PRODUCTION_SEALED'
    assert summary['classification'] == terminal['classification'] == 'R5_69_OBSERVATION_CONTROL_GAP'
    selected = [t for r in plan['regressions'] if r['name'].startswith('harness-')
                for t in r.get('selection', {}).get('identities', []) if t in exclusion.index()['tests']]
    assert len(selected) == len(set(selected)) == 36
    assert len(plan['regressions']) == freeze['regression_stages'] == 193
    assert summary['production_batches'] == summary['production_receipts'] == summary['production_certificates'] == 0
    assert not list(OUT.rglob('receipt-*.json'))
    for name in ('batches', 'certificate.json', 'capsule.json', 'qualified-authority.json',
                 'production-gate', 'production-declaration.json', 'observation-authorization.json', 'opening.json'):
        assert not (OUT / name).exists()
    assert summary['synthetic_accounting'] == [0, 0, 0] and summary['b02_accounting'] == [0, 0, 0, 0]
    assert summary['opening_accounting'] == [0, 0]
    assert summary['b02_read_attempts'] == summary['b02_content_reads'] == 0
    assert all(summary[n] is False for n in ('repair_occurred', 'retry_occurred', 'resume_occurred'))
    assert summary['stages']['production-gate-consumer-compatibility'] == 'FAIL'
    assert summary['stages']['mechanism-continuity'] == 'PASS'
    assert all(v == 'NOT_RUN' for k, v in summary['stages'].items()
               if k not in ('production-gate-consumer-compatibility', 'mechanism-continuity'))
    baseline = read('preservation-baseline')
    for name, pin in baseline['files'].items():
        assert digest(ordinary(ROOT / name)) == pin
    for name, row in baseline['sealed_metadata_only'].items():
        stat = (ROOT / name).stat()
        assert row == {'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns}
    old = loads(ordinary(OUT.parent / 'R5_67-evidence/summary.json'))
    assert old['classification'] == 'R5_67_PRODUCTION_CERTIFICATE_GAP'
    assert not subprocess.check_output(['git', 'diff', '--name-only', '--', 'benchmark/results'], cwd=ROOT)
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    from benchmark.results.phase5c.r5_43_qualification import contamination
    assert SCHEMA['core_constructs'] == summary['core_semantics'] == 30 and not contamination()['findings']
    assert not ATTEMPTS
    publication.persist(OUT / 'independent-stopped-inventory.json', summary)
    publication.persist(OUT / 'independent-stopped-audit.json', {'status': 'PASS',
        'scope': 'independent source-contract diagnosis and terminal-candidate integrity; no gate retry',
        'production_final_audit': 'NOT_RUN', 'qualification_promoted': False,
        'identity_schema_revalidation': 'PASS', 'plan_unchanged': True,
        'production_gate_compatibility': 'FAIL_CONFIRMED',
        'authority_policy_members': 1083, 'sealed_metadata_members': 11, 'sealed_frozen_metadata_pins': 2,
        'fresh_authority_and_sealed_verification': 'NOT_RUN', 'capsule': 'NOT_RUN', 'receipts': 'EMPTY',
        'workspace': 'NOT_RUN', 'production_declaration': 'NOT_ISSUED',
        'safe_exclusion': 'PINNED_NOT_EXECUTED', 'protected_metadata_skips': 36,
        'synthetic_observation_combined_opening_post_state_replay': 'NOT_RUN',
        'historical_unsealed_byte_preserved': len(baseline['files']),
        'historical_sealed_metadata_preserved': len(baseline['sealed_metadata_only']),
        'historical_classifications_preserved': True, 'contamination': 'clean', 'semantic_count': 30,
        'b02_read_attempts': 0, 'b02_content_reads': 0, 'b02_accounting': [0, 0, 0, 0],
        'opening_accounting': [0, 0], 'synthetic_accounting': [0, 0, 0],
        'ai_independence_regressions': 'NOT_RUN', 'no_repair_retry_resume': True,
        'evidence_sha256': {p.name: digest(ordinary(p)) for p in OUT.glob('*.json')}})
    print({'independent_stopped_audit': 'PASS', 'historical_unsealed': len(baseline['files'])})


def final():
    assert read('independent-stopped-audit')['status'] == 'PASS'
    names = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--modified'],
                                    cwd=ROOT, text=True).splitlines()
    dispositions, pins, rejected = {}, {}, []
    for name in sorted(set(names)):
        path = ROOT / name
        if path.suffix not in ('.py', '.md', '.json'):
            continue
        raw = ordinary(path)
        if path == OUT / 'qualification-identity.json':
            read('qualification-identity')
            dispositions[name] = 'SCHEMA_CLASSIFIED_PUBLICATION'
        else:
            try:
                dispositions[name] = publication.check_source(name, raw)
            except SecretRejected:
                dispositions[name] = 'REJECTED_DETAILS_WITHHELD'
                rejected.append(name)
        pins[name] = digest(raw)
        check = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(path)],
                               cwd=ROOT, capture_output=True, timeout=10)
        assert check.returncode in (0, 1) and not check.stdout
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True).returncode == 0
    for path in OUT.glob('*.json'):
        read(path.stem)
    assert not ATTEMPTS
    publication.persist(OUT / 'publication-integrity.json', {'status': 'FAIL' if rejected else 'PASS',
        'scope': 'stopped-candidate source, metadata, evidence and documentation publication',
        'source_sha256': pins, 'source_dispositions': dispositions,
        'rejected_sources': rejected, 'no_repair_retry_resume': True,
        'qualification_identity': 'R5.64 schema-classified public protocol authorization',
        'synthetic_fixture_content_published': False, 'protected_content_published': False,
        'diagnostics': 'redacted', 'git_diff_check': 'PASS', 'new_file_whitespace_check': 'PASS',
        'production_security_regressions': 'NOT_RUN', 'ai_independence_regressions': 'NOT_RUN',
        'b02_read_attempts': 0, 'b02_content_reads': 0})
    print({'publication_integrity': 'FAIL' if rejected else 'PASS', 'whitespace': 'PASS'})


if __name__ == '__main__':
    {'audit': audit, 'final': final}[sys.argv[1]]()
