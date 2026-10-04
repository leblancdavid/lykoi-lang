"""Bounded, restriction-preserving observation; never a production certificate."""

import importlib.metadata
import importlib.util
import os
from pathlib import Path
import shutil
import site
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from benchmark.evaluation import execution_identity_r5_46 as identity
from benchmark.evaluation import preexposure_r5_45 as prior
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, persist
from benchmark.results.phase5c import r5_45_qualification as inherited

OUTPUT = ROOT / 'benchmark/results/phase5c/R5_46-evidence'
EXCLUDED = ['benchmark/results/phase5c/R5_46-evidence']
CLASSIFICATION = 'R5_46_PROTOCOL_HALT'


def definitions():
    result = inherited.definitions()
    result['execution-identity'] = ['suite', 'benchmark/evaluation', 'test_execution_identity_r5_46.py', 'ordinary']
    result['dependency-inventory'] = ['inventory']
    return result


def inventory():
    modules = {}
    for name in ('json', 'hashlib', 'subprocess', 'tempfile', 'locale', 'site',
                 '_hashlib', '_ssl', '_ctypes', 'unicodedata', 'zlib'):
        spec = importlib.util.find_spec(name)
        origin = spec.origin if spec else None
        path = Path(origin) if origin and origin not in ('built-in', 'frozen') else None
        modules[name] = {'origin_kind': 'file' if path else origin,
                         'filename': path.name if path else None,
                         'sha256': digest(path.read_bytes()) if path and path.is_file() else None}
    startup = {}
    for directory in [*site.getsitepackages(), site.getusersitepackages()]:
        path = Path(directory)
        if path.is_dir():
            for item in sorted(path.glob('*.pth')):
                startup[item.name] = {'sha256': digest(item.read_bytes()),
                                      'executable_lines': sum(line.startswith(b'import ') or line.startswith(b'import\t')
                                                              for line in item.read_bytes().splitlines())}
    executable = shutil.which('git')
    version = subprocess.check_output([executable, '--version'], timeout=10, text=True).strip()
    runtime_root = Path(sys.executable).parent
    native = {p.name: digest(p.read_bytes()) for p in sorted(runtime_root.glob('*.dll'))}
    names = sorted(name for name in os.environ if name.upper().startswith(('PYTHON', 'GIT', 'LYKOI')) or
                   name.upper() in {'PATH', 'PATHEXT', 'SYSTEMROOT', 'COMSPEC', 'TEMP', 'TMP',
                                    'HOME', 'USERPROFILE', 'LANG', 'LC_ALL', 'LC_CTYPE', 'TZ'})
    return {'successful': True, 'observation_only': True, 'runtime': identity.runtime(),
            'resolved_installed_distributions': sorted(
                [{'name': d.metadata['Name'], 'version': d.version} for d in importlib.metadata.distributions()],
                key=lambda d: (d['name'].lower(), d['version'])),
            'selected_resolved_modules': modules, 'runtime_root_dll_hashes': native,
            'startup_pth': startup, 'user_site_enabled': site.ENABLE_USER_SITE,
            'git': {'version': version, 'executable_sha256': digest(Path(executable).read_bytes())},
            'candidate_environment_names_only': names, 'secret_values_persisted': False,
            'unknown_material_closure': [
                'transitive and late-loaded Python/Git native libraries and OS behavior',
                'effective descendant import search, startup customization and readable bytecode',
                'external Git attributes/ignore/config-driven helpers and complete Git behavior slicing'],
            'production_certificate_qualified': False}


def snapshot():
    return prior.seal({'protocol': 'r5.46-observational-repository-snapshot',
                       'files': prior.tree(ROOT, EXCLUDED), 'definitions': definitions()})


def worker(name):
    if (OUTPUT / 'quarantine.json').exists():
        raise identity.ProtocolFailure('halted qualification cannot execute workers')
    if name == 'dependency-inventory':
        result = inventory()
        persist(OUTPUT / (name + '-worker.json'), result)
    elif name == 'execution-identity':
        from benchmark.results.phase5c.r5_38_review import run_suite
        result = run_suite('benchmark/evaluation', 'test_execution_identity_r5_46.py')
        persist(OUTPUT / (name + '-worker.json'), result)
    else:
        inherited.OUTPUT = OUTPUT
        inherited.worker(name)
        return
    if not result['successful']:
        raise SystemExit(1)


def initialize():
    OUTPUT.mkdir(exist_ok=False)
    persist(OUTPUT / 'state.json', snapshot())
    persist(OUTPUT / 'initial-boundary.json', {
        'classification_pending': True, 'production_qualification_blocked': True,
        'inherited_local_changes': ['R5.45 prospective implementation/evidence', 'three research documents'],
        'protected_inherited_files': {p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
            for p in sorted(ROOT.rglob('*')) if p.is_file() and
            ('R5_45-' in p.as_posix() or p.name in ('r5_45_qualification.py', 'r5_45_finalize.py',
                'preexposure_r5_45.py', 'test_preexposure_r5_45.py', 'preexposure-r5.45.md'))},
        'zero_exposure_required': True})
    print({'stages': len(definitions()), 'snapshot': prior.reload(OUTPUT / 'state.json')['identity']})


def batch():
    if (OUTPUT / 'quarantine.json').exists():
        raise identity.ProtocolFailure('halted qualification cannot resume')
    frozen = prior.reload(OUTPUT / 'state.json')
    if canonical(snapshot()) != canonical(frozen):
        raise identity.ProtocolFailure('observational repository inputs changed')
    started = time.monotonic()
    environment = {**os.environ, 'PYTHONPATH': str(ROOT / 'src'), 'PYTHONDONTWRITEBYTECODE': '1'}
    for name, definition in definitions().items():
        if (OUTPUT / (name + '.json')).exists():
            continue
        remaining = 85 - (time.monotonic() - started)
        if remaining < 30:
            break
        before = snapshot()
        mechanism = digest(canonical(definition))
        persist(OUTPUT / (name + '-attempt.json'), prior.stage(frozen['identity'], name, 'INCOMPLETE',
                {'successful': False, 'reason': 'no completion receipt'}, mechanism))
        command = [sys.executable, '-B', str(Path(__file__).resolve()), 'worker', name]
        status, telemetry = prior.bounded(command, ROOT, environment, min(70, remaining))
        path = OUTPUT / (name + '-worker.json')
        result = loads(path.read_bytes()) if status != 'INCOMPLETE' and path.exists() else {'successful': False}
        if canonical(before) != canonical(snapshot()) or canonical(before) != canonical(frozen):
            status, result = 'FAIL', {'successful': False, 'reason': 'mid-stage repository mutation'}
        persist(OUTPUT / (name + '.json'), prior.stage(frozen['identity'], name, status,
                {**result, 'supervision': telemetry, 'production_reusable': False}, mechanism))
        print({'stage': name, 'status': status, 'seconds': telemetry['elapsed_seconds']}, flush=True)
        if status != 'PASS':
            raise SystemExit(1)
    print({'completed': sum((OUTPUT / (n + '.json')).exists() for n in definitions()),
           'required': len(definitions())})


def final():
    """Stopped-run accounting only: no qualification retry or certificate."""
    from benchmark.results.phase5c.r5_43_qualification import historical_lock, contamination
    from benchmark.results.phase5c.r5_42_review import authority
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    stages = {name: prior.reload(OUTPUT / (name + '.json')) for name in definitions()
              if (OUTPUT / (name + '.json')).exists()}
    baseline = loads((OUTPUT / 'initial-boundary.json').read_bytes())
    drift = [name for name, expected in baseline['protected_inherited_files'].items()
             if digest((ROOT / name).read_bytes()) != expected]
    forbidden = ('B02', 'B03', 'B17', 'due_date', 'due-date', 'task_manager')
    new_paths = [ROOT / 'benchmark/evaluation' / name for name in
                 ('execution_identity_r5_46.py', 'test_execution_identity_r5_46.py')]
    findings = [p.name for p in new_paths if any(word in p.read_text() for word in forbidden)]
    command = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    infrastructure = loads((OUTPUT.parent / 'R5_43-infrastructure-lock.json').read_bytes())
    mismatches = [name for name, expected in infrastructure['files'].items()
                  if not (ROOT / name).is_file() or digest((ROOT / name).read_bytes()) != expected]
    body = {k: v for k, v in infrastructure.items() if k != 'identity'}
    locks = {'historical': historical_lock('R5_40-implementation-profile-lock.json'),
             'prospective': historical_lock('R5_41-implementation-lock.json'),
             'infrastructure': {'valid': not mismatches,
                 'identity_valid': digest(canonical(body)) == infrastructure['identity'],
                 'identity': infrastructure['identity'], 'protected_files': len(infrastructure['files']),
                 'matching_files': len(infrastructure['files']) - len(mismatches), 'mismatches': mismatches}}
    suites = [s['result'] for n, s in stages.items() if n.startswith('harness-')]
    frozen, current = prior.reload(OUTPUT / 'state.json'), snapshot()
    changed = [n for n, h in frozen['files'].items() if current['files'].get(n) != h]
    added = [n for n in current['files'] if n not in frozen['files']]
    persist(OUTPUT / 'quarantine.json', {
        'primary_classification': CLASSIFICATION, 'permanently_stopped': True,
        'reason': 'concurrent repository mutation; protected infrastructure member changed',
        'protected_mismatches': mismatches, 'changed_since_freeze': changed, 'added_since_freeze': added,
        'all_stage_evidence_quarantined': True, 'reusable_pass_evidence': False,
        'b02_exposure': 0,
        'receipts_sha256': {p.name: digest(p.read_bytes()) for p in sorted(OUTPUT.glob('*.json'))}})
    result = {'primary_classification': CLASSIFICATION, 'production_certificate_issued': False,
              'stages': {n: s['identity'] for n, s in stages.items()},
              'stage_statuses': {n: s['status'] for n, s in stages.items()},
              'required_stages': len(definitions()), 'completed_receipts': len(stages),
              'harness_partial_accepted_before_quarantine': {
                  'discovered': sum(s.get('discovered', 0) for s in suites),
                  'passed': sum(s.get('passed', 0) for s in suites),
                  'skipped': sum(len(s.get('skipped', [])) for s in suites)},
              'full_regression_pass_established': False, 'evidence_reusable': False,
              'locks': locks, 'authority': authority(), 'contamination': contamination(),
              'new_infrastructure_contamination': findings, 'inherited_r5_45_drift': drift,
              'core_semantics': SCHEMA['core_constructs'],
              'b02': {name: 0 for name in ('reservations', 'dispatches', 'static_support', 'checked_plans',
                      'readiness', 'audit', 'admission', 'generation', 'execution', 'frozen_acceptance')},
              'b03_prospectively_touched': False, 'b17_exposed': False,
              'b17_classified': False, 'phase5c': 'paused',
              'costs_seconds': {n: s['result']['supervision']['elapsed_seconds'] for n, s in stages.items()},
              'bounded_execution_identity_measurements': 'not reached; no bound established',
              'dependency_inventory_observation': inventory(),
              'synthetic_tests': {'initial_run': 46, 'errors': 46,
                   'reason': 'config.hex used instead of config.stdout.hex; fixed before snapshot',
                   'expanded_tests': 49, 'post_fix_execution': 'not reached before protocol halt'},
              'diff_check': {'exit': command.returncode, 'stderr': command.stderr},
              'reporting_drift': changed, 'reporting_additions': added,
              'unqualified_prototype_hashes': {p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
                                               for p in new_paths + [Path(__file__).resolve()]}}
    persist(OUTPUT / 'summary.json', result)
    persist(OUTPUT / 'classification.json', {'primary_classification': CLASSIFICATION,
            'summary_sha256': digest((OUTPUT / 'summary.json').read_bytes()), 'b02_dispatches': 0})
    print({'classification': CLASSIFICATION, 'partial_harness': result['harness_partial_accepted_before_quarantine'],
           'locks': locks, 'synthetic_tests': result['synthetic_tests']})


def final_integrity():
    """Record reporting completion without refreshing quarantined stage identity."""
    from benchmark.results.phase5c.r5_43_qualification import historical_lock, contamination
    from benchmark.results.phase5c.r5_42_review import authority
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    quarantine = loads((OUTPUT / 'quarantine.json').read_bytes())
    changed_receipts = [name for name, expected in quarantine['receipts_sha256'].items()
                        if digest((OUTPUT / name).read_bytes()) != expected]
    infrastructure = loads((OUTPUT.parent / 'R5_43-infrastructure-lock.json').read_bytes())
    mismatches = [name for name, expected in infrastructure['files'].items()
                  if not (ROOT / name).is_file() or digest((ROOT / name).read_bytes()) != expected]
    command = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    paths = [ROOT / name for name in ('docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md',
             'benchmark/evaluation/execution_identity_r5_46.py',
             'benchmark/evaluation/test_execution_identity_r5_46.py')]
    paths += [Path(__file__).resolve(), OUTPUT.parent /
              'R5_46-COMPLETE-EXECUTION-STATE-AND-DEPENDENCY-IDENTITY-QUALIFICATION.md']
    result = {'primary_classification': CLASSIFICATION, 'quarantined_receipt_mutations': changed_receipts,
              'historical_lock': historical_lock('R5_40-implementation-profile-lock.json'),
              'prospective_lock': historical_lock('R5_41-implementation-lock.json'),
              'infrastructure_lock': {'matching_files': len(infrastructure['files']) - len(mismatches),
                  'protected_files': len(infrastructure['files']), 'mismatches': mismatches, 'valid': not mismatches},
              'authority': authority(), 'contamination': contamination(), 'core_semantics': SCHEMA['core_constructs'],
              'owner_explanation': 'Separate security correction rewrote offending commit and added gitignore rules',
              'no_restart_authorized': True, 'b02_exposure': 0, 'production_certificate_issued': False,
              'diff_check': {'exit': command.returncode, 'stderr': command.stderr},
              'completed_reporting_hashes': {p.relative_to(ROOT).as_posix(): digest(p.read_bytes()) for p in paths},
              'evidence_hashes': {p.name: digest(p.read_bytes()) for p in sorted(OUTPUT.glob('*.json'))}}
    if changed_receipts or command.returncode or SCHEMA['core_constructs'] != 30:
        raise identity.ProtocolFailure('stopped-run reporting integrity failure')
    persist(OUTPUT / 'final-integrity.json', result)
    print({'primary_classification': CLASSIFICATION, 'quarantined_receipt_mutations': changed_receipts,
           'infrastructure_lock': result['infrastructure_lock'], 'diff_exit': command.returncode})


if __name__ == '__main__':
    {'initialize': initialize, 'batch': batch, 'worker': lambda: worker(sys.argv[2]),
     'final': final, 'final-integrity': final_integrity}[sys.argv[1]]()
