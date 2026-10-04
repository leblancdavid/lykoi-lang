"""Stopped-run accounting only. Never repairs/retries an R5.48 stage."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from benchmark.results.phase5c import r5_48_qualification as stopped
from benchmark.evaluation.recorder_r5_43 import canonical, digest


def report():
    quarantine = stopped.read('quarantine')
    frozen = stopped.read('state')
    if not quarantine['all_receipts_quarantined']:
        raise ValueError('stopped-run quarantine missing')
    if canonical(stopped.capture()) != canonical(frozen):
        raise ValueError('observed state changed; reporting cannot refresh it')
    changed = [name for name, expected in quarantine['receipts'].items()
               if digest((stopped.OUTPUT / name).read_bytes()) != expected]
    if changed:
        raise ValueError('quarantined receipts changed')
    evidence = {n: stopped.read(n) for n in stopped.definitions()
                if (stopped.OUTPUT / (n + '.json')).exists()}
    harness = [r['result'] for n, r in evidence.items() if n.startswith('harness-')]
    diagnostics = {}
    # These are separate read-only stopped-state diagnostics, not the missing
    # stages, not a continuation and not reusable certificate evidence.
    for name in ('validate', 'safety', 'diff'):
        command = ['git', 'diff', '--check'] if name == 'diff' else [
            sys.executable, '-B', '-S', '-m', 'air_compiler.cli', name, 'air/task_manager.json']
        p = subprocess.run(command, cwd=ROOT, env=stopped.identity.isolated_environment(__import__('os').environ, ROOT),
                           capture_output=True, timeout=30)
        diagnostics[name] = {'successful': p.returncode == 0, 'exit': p.returncode,
                             'output_withheld': True, 'qualification_stage': False}
    stopped.write('post-halt-diagnostics', diagnostics)
    aliases = {n: n + '.py' for n in (
        'input_binding_r5_32', 'optional_support_r5_41', 'refined_runtime_r5_28',
        'state_runtime_r5_39', 'transport_runtime_r5_34', 'transport_runtime_r5_35')}
    aliases['transport_helpers_r5_41'] = 'transport_runtime_r5_35.py'
    rows = []
    for name, filename in sorted(aliases.items()):
        source = 'benchmark/semantic/' + filename
        rows.append({'module': name, 'implementation': source,
                     'sha256': digest((ROOT / source).read_bytes()),
                     'domain': 'BUILD_EXECUTION',
                     'reason': 'repository-owned standalone deployment runtime/helper, not a third-party package'})
    stopped.write('inventory-failure-adjudication', {
        'failed_receipt_preserved': True, 'qualification_restarted': False,
        'cause': 'static import root screen omitted copied standalone module resolution and deployment alias',
        'repository_runtime_roots': rows,
        'alias_evidence': {'path': 'benchmark/semantic/application_boundary_r5_41.py',
                           'sha256': digest((ROOT / 'benchmark/semantic/application_boundary_r5_41.py').read_bytes()),
                           'line': 96},
        'core_provider_references': [],
        'correction_policy': 'prospective separately authorized inventory resolver; frozen run remains halted'})
    if canonical(stopped.capture()) != canonical(frozen):
        raise ValueError('stopped reporting changed observed identity')
    checks = stopped.boundary()
    result = {
        'primary_classification': 'R5_48_PROTOCOL_HALT',
        'reason': 'dependency-inventory verification failed; repository-owned standalone import roots misclassified',
        'secondary_limitation': 'EXECUTION_STATE_IDENTITY_V2_PRODUCTION_CLOSURE_UNQUALIFIED',
        'ai_independence': 'SUPPORTED_WITHIN_INSPECTED_AND_TESTED_CORE_SCOPE_NOT_A_QUALIFIED_RUN',
        'execution_identity_protocol': stopped.identity.PROTOCOL,
        'observed_identity': frozen['identity'], 'observed_state_unchanged': True,
        'unknown_material_groups': frozen['unknown'],
        'required_stages': len(stopped.definitions()), 'completed_receipts': len(evidence),
        'pass_receipts_before_quarantine': sum(r['status'] == 'PASS' for r in evidence.values()),
        'failed_receipts': [n for n, r in evidence.items() if r['status'] != 'PASS'],
        'not_run_stages': [n for n in stopped.definitions() if n not in evidence],
        'all_receipts_quarantined': True, 'quarantined_receipt_changes': changed,
        'evidence_reusable': False, 'full_74_stage_qualification_pass': False,
        'production_certificate_issued': False, 'production_toctou_qualified': False,
        'restricted_harness': {'discovered': sum(r['discovered'] for r in harness),
                               'passed': sum(r['passed'] for r in harness),
                               'skipped': sum(len(r['skipped']) for r in harness)},
        'regression_counts_before_quarantine': {n: {k: evidence[n]['result'][k] for k in
            ('discovered', 'passed', 'skipped', 'failures', 'errors')} for n in
            ('application', 'focused', 'recorder', 'certificate', 'security', 'publication', 'execution-v2')},
        'coherence_before_quarantine': {k: evidence['coherence']['result'][k] for k in
            ('profiles', 'rows', 'canonical_equal', 'deterministic', 'structure', 'traceability', 'contamination')},
        'independent_stopped_diagnostics': diagnostics, 'locks': checks,
        'b02': {n: 0 for n in ('reservations', 'dispatches', 'checked_plans', 'readiness', 'audit',
                              'admission', 'static_support', 'generation', 'execution', 'frozen_acceptance')},
        'core_semantics': 30, 'b03_prospectively_touched': False, 'b17_exposed': False,
        'b17_classified': False, 'phase5c': 'paused', 'r5_46_prototype_promoted': False,
        'rotation_status': 'ROTATION_STATUS_EXTERNAL_OR_UNVERIFIED'}
    stopped.write('stopped-summary', result)
    print({k: result[k] for k in ('primary_classification', 'required_stages', 'completed_receipts',
                                 'pass_receipts_before_quarantine', 'not_run_stages', 'restricted_harness')})


def integrity():
    quarantine, frozen = stopped.read('quarantine'), stopped.read('state')
    changed = [n for n, h in quarantine['receipts'].items() if digest((stopped.OUTPUT / n).read_bytes()) != h]
    if changed or canonical(stopped.capture()) != canonical(frozen):
        raise ValueError('stopped reporting integrity failure')
    p = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True)
    if p.returncode:
        raise ValueError('reporting diff failed')
    result = {'primary_classification': 'R5_48_PROTOCOL_HALT', 'successful_stopped_integrity': True,
              'quarantined_receipt_changes': changed, 'observed_state_unchanged': True,
              'locks': stopped.boundary(), 'diff_check_exit': p.returncode,
              'production_certificate_issued': False,
              'reporting_hashes': {n: digest((ROOT / n).read_bytes()) for n in
                  ('docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md',
                   'docs/ai-independence-r5.48.md',
                   'benchmark/results/phase5c/R5_48-EXECUTION-STATE-AND-AI-INDEPENDENCE.md')},
              'evidence': {p.name: digest(p.read_bytes()) for p in sorted(stopped.OUTPUT.glob('*')) if p.is_file()}}
    stopped.write('stopped-final-integrity', result)
    print({'stopped_integrity': 'PASS', 'classification': result['primary_classification']})


if __name__ == '__main__':
    try:
        {'report': report, 'integrity': integrity}[sys.argv[1]]()
    except Exception:
        print('stopped R5.48 accounting failed; raw diagnostics withheld', file=sys.stderr)
        raise SystemExit(1)
