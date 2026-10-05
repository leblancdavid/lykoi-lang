"""Independent read-only stopped-candidate diagnosis; no stage retries."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import publication_r5_70 as typed
from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import preexposure_r5_45 as envelopes
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

OUT = ROOT / 'benchmark/results/phase5c/R5_71-evidence'
PROTECTED = {r.path.resolve() for r in guard.repository_resources(ROOT)}
ATTEMPTS = []


def protect(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        if Path(os.fsdecode(args[0])).resolve() in PROTECTED:
            ATTEMPTS.append('DENIED_BEFORE_CONTENT')
            raise RuntimeError('R5_71_PROTOCOL_HALT')


sys.addaudithook(protect)


def ordinary(name):
    path = ROOT / name
    assert path.resolve() not in PROTECTED
    return path.read_bytes()


def read(name):
    raw = ordinary('benchmark/results/phase5c/R5_71-evidence/' + name + '.json')
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    return value


def write(name, value):
    publication.persist(OUT / (name + '.json'), value)


def diagnose():
    terminal, plan, identity = read('terminal-stop'), read('stage-plan'), read('qualification-identity')
    assert terminal['classification'] == 'R5_71_AUTHORITY_GAP'
    assert terminal['failed_stage'] == 'qualified-authority'
    envelopes.unseal(plan)
    envelopes.unseal(identity)
    publication.safe_bytes(identity, schema=schemas.QUALIFICATION_IDENTITY,
                           schema_identity=schemas.QUALIFICATION_IDENTITY_PIN)
    assert identity['plan'] == plan['identity']
    assert identity['orchestration'] == plan['driver_identity'] == digest(ordinary('benchmark/results/phase5c/r5_71_qualification.py'))
    policy = read('authority-policy')
    assert sealed.identity(policy) == plan['authority_policy']
    assert digest(canonical(read('worker-registry'))) == plan['worker_registry'] == identity['registry']
    assert all(digest(ordinary(n)) == pin for n, pin in plan['implementation_sha256'].items())
    # Inspect ordinary comparisons only. Never invoke qualify() again, restore
    # content, change a pin, run a required regression or construct a certificate.
    matches, mismatches = [], {}
    for name, row in policy['members'].items():
        if row['classification'] != 'ORDINARY':
            continue
        raw = ordinary(name)
        compared = raw.replace(b'\r\n', b'\n') if row['representation_kind'] == 'utf8-lf-text' else raw
        if digest(compared) == row['sha256']:
            matches.append(name)
        else:
            mismatches[name] = {'expected': row['sha256'], 'physical': digest(raw),
                'lf_normalized': digest(raw.replace(b'\r\n', b'\n')),
                'representation_kind': row['representation_kind'], 'blob': row['blob'],
                'lf_matches_expected': digest(raw.replace(b'\r\n', b'\n')) == row['sha256']}
    # Only mismatching ORDINARY blobs may enter this metadata diagnosis.
    blobs = checkout.blobs(ROOT, [r['blob'] for r in mismatches.values() if r['blob']])
    current = checkout.tree(ROOT, 'HEAD')
    for name, row in mismatches.items():
        if row['blob']:
            row['pinned_repository_blob_matches_expected'] = digest(blobs[row['blob']]) == row['expected']
            row['current_committed_mapping_matches_pinned'] = current.get(name, {}).get('blob') == row['blob']
    assert mismatches
    write('ordinary-authority-diagnosis', {'status': 'PASS', 'scope': 'read-only stopped diagnosis; no qualifier retry',
        'ordinary_members': len(matches) + len(mismatches), 'matching_members': len(matches),
        'mismatches': mismatches, 'protected_read_attempts': len(ATTEMPTS), 'protected_content_reads': 0})
    print({'ordinary_members': len(matches) + len(mismatches), 'matching': len(matches), 'mismatches': mismatches})


def preservation():
    saved = read('preservation-baseline')
    assert all(digest(ordinary(n)) == pin for n, pin in saved['files'].items())
    for name, meta in saved['sealed_metadata_only'].items():
        stat = (ROOT / name).stat()
        assert meta == {'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns}
    return {'status': 'PASS', 'unsealed_files': len(saved['files']),
            'protected_metadata_files': len(saved['sealed_metadata_only'])}


def final():
    stopped, diagnosis, plan = read('terminal-stop'), read('ordinary-authority-diagnosis'), read('stage-plan')
    mismatches = diagnosis['mismatches']
    assert set(mismatches) == {'benchmark/evaluation/security_r5_47.py', 'benchmark/evaluation/tier2_r5_51.py'}
    assert all(r['representation_kind'] == 'utf8-lf-text' and not r['lf_matches_expected'] and
        r['pinned_repository_blob_matches_expected'] and not r['current_committed_mapping_matches_pinned']
        for r in mismatches.values())
    provenance = {}
    committed = checkout.tree(ROOT, 'HEAD')
    r564 = checkout.tree(ROOT, '6d81f2d')
    for name, row in mismatches.items():
        assert digest(ordinary(name)) == plan['implementation_sha256'][name]
        assert committed[name] == r564[name]
        data = checkout.blobs(ROOT, [committed[name]['blob']])[committed[name]['blob']]
        assert data.replace(b'\r\n', b'\n') == ordinary(name).replace(b'\r\n', b'\n')
        log = subprocess.check_output(['git', 'log', '-1', '--format=%H', '--', name], cwd=ROOT, text=True).strip()
        assert log.startswith('6d81f2d')
        provenance[name] = {'authority_expected': row['expected'], 'current_qualified_implementation': digest(ordinary(name)),
            'current_repository_blob': committed[name]['blob'], 'last_change_commit': log,
            'qualified_change_record': 'R5_64-CONTEXT-AWARE-CREDENTIAL-PUBLICATION-RECONCILIATION.md',
            'matches_r571_frozen_implementation': True, 'matches_r564_committed_implementation': True,
            'failure_is_not_checkout_representation': True}
    write('failure-provenance', {'status': 'PASS', 'determination': 'ACCUMULATED_FRAMEWORK_INTEGRATION_FAILURE',
        'reason': 'full inherited authority policy still binds pre-R5.64 versions of two qualified publication mechanisms',
        'members': provenance, 'qualifier_retried': False, 'source_or_authority_modified': False})
    assert all(read(n)['status'] == 'PASS' for n in ('freeze', 'mechanism-continuity', 'sealed-members', 'frozen-pins'))
    assert len(read('sealed-members')['resources']) == 11 and len(read('frozen-pins')['sealed_frozen_pins']) == 2
    assert not any((OUT / n).exists() for n in ('qualified-authority.json', 'capsule.json', 'production-declaration.json',
        'batches', 'certificate.json', 'workspace.json', 'production-gate', 'synthetic-flow.json'))
    assert not Path('C:/Users/lblan/AppData/Local/Temp/opencode/r571-production-workspace').exists()
    declared = plan['required_metadata_only_skips']
    assert len(declared) == len(set(declared)) == 36 and all(n in exclusion.index()['tests'] for n in declared)
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    assert not contamination()['findings'] and SCHEMA['core_constructs'] == 30 and not ATTEMPTS
    history = preservation()
    write('historical-preservation', history)
    states = {s['name']: 'NOT_RUN' for s in plan['preflight'] + plan['regressions'] + plan['integration']}
    states.update({n: 'PASS' for n in ('mechanism-continuity', 'sealed-members', 'frozen-pins')})
    states['qualified-authority'] = 'FAIL'
    summary = {'classification': stopped['classification'], 'failed_stage': stopped['failed_stage'],
        'determination': 'ACCUMULATED_FRAMEWORK_INTEGRATION_FAILURE',
        'recommendation': 'SIMPLIFIED_PHASE5_RUNNER_REQUIRED',
        'concrete_failure': 'inherited full authority hashes contradict qualified R5.64/current implementation hashes for two mechanisms',
        'qualification': read('qualification-identity')['identity'], 'plan': plan['identity'], 'stages': states,
        'starting_state': 'FAIL', 'production_gate_qualified': False,
        'ordinary_authority_members': diagnosis['ordinary_members'], 'ordinary_authority_matches': diagnosis['matching_members'],
        'ordinary_authority_mismatches': len(mismatches), 'sealed_commitments_verified': 11, 'sealed_frozen_pins_verified': 2,
        'required_regression_stages': len(plan['regressions']), 'production_batches': 0, 'production_receipts': 0,
        'production_certificates': 0, 'production_declarations': 0, 'synthetic_accounting': [0, 0, 0, 0],
        'b02_read_attempts': 0, 'b02_content_reads': 0, 'b02_accounting': [0, 0, 0, 0],
        'b02_opening_accounting': [0, 0], 'b02_observation_grants': 0,
        'metadata_only_skip_declarations': 36, 'executed_metadata_only_skips': 0,
        'core_semantics': 30, 'contamination': 'clean', 'historical_preservation': history,
        'repair_occurred': False, 'retry_occurred': False, 'resume_occurred': False,
        'production_final_audit': 'NOT_RUN', 'stopped_integrity_audit': 'PASS',
        'ai_independence_regressions': 'NOT_RUN', 'phase5c': 'paused'}
    write('summary', summary)
    names = subprocess.check_output(['git', 'ls-files', '--modified', '--others', '--exclude-standard'],
                                   cwd=ROOT, text=True).splitlines()
    pins, dispositions = {}, {}
    for name in names:
        if name == 'benchmark/results/phase5c/R5_71-evidence/stopped-final-audit.json':
            continue  # Output cannot contain its own physical-byte digest.
        raw = ordinary(name)
        if name.endswith('/qualification-identity.json') and '/R5_71-evidence/' in name:
            publication.safe_bytes(loads(raw), schema=schemas.QUALIFICATION_IDENTITY,
                                   schema_identity=schemas.QUALIFICATION_IDENTITY_PIN)
            dispositions[name] = 'SCHEMA_CLASSIFIED_PUBLICATION'
        elif name == 'benchmark/results/phase5c/r5_71_qualification.py':
            dispositions[name] = typed.check_python_source(raw,
                trusted_source_identity=plan['publication_policy']['source_sha256'],
                schema=typed.SUMMARY_CONTEXT, schema_identity=typed.SUMMARY_PIN)
        else:
            dispositions[name] = publication.check_source(name, raw)
        pins[name] = digest(raw)
        result = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(ROOT / name)],
                                cwd=ROOT, capture_output=True, timeout=10)
        assert result.returncode in (0, 1) and not result.stdout
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True).returncode == 0
    write('stopped-final-audit', {'status': 'PASS', 'scope': 'stopped evidence only; no promotion of unrun production gates',
        'source_and_evidence_sha256': pins, 'publication_dispositions': dispositions,
        'historical_preservation': history, 'new_file_whitespace': 'PASS', 'git_diff_check': 'PASS',
        'protected_read_attempts': 0, 'protected_content_reads': 0})
    print({k: v for k, v in summary.items() if k != 'stages'})


if __name__ == '__main__':
    {'diagnose': diagnose, 'final': final}[sys.argv[1]]()
