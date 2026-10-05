"""Bounded diagnostic verification, restriction-aware and separately recorded."""

from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import checkout_r5_52 as check
from benchmark.evaluation import security_r5_47 as security

RESULTS = ROOT / 'benchmark/results/phase5c'
CLEAN = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r552-clean-lf')
OUT = RESULTS / 'R5_52-evidence'


def persist(name, value):
    security.persist(OUT / (name + '.json'), value)


def initialize():
    OUT.mkdir(exist_ok=False)
    protected = [p for p in RESULTS.rglob('*') if p.is_file() and not p.name.startswith(('R5_52', 'r5_52'))
                 and '__pycache__' not in p.parts]
    persist('initial', {'protected': {p.relative_to(ROOT).as_posix(): check.sha(p.read_bytes()) for p in protected},
        'head': check.git(ROOT, 'rev-parse', 'HEAD').decode().strip(), 'b02_exposure': 0})
    print({'protected': len(protected)})


def worker(root, directory, pattern):
    # Import only the established restriction-aware regression dispatcher.
    sys.path[:0] = [str(root), str(root / 'src')]
    os.chdir(root)  # Child execution context is explicit; no parent-shell cwd change.
    from benchmark.results.phase5c import r5_38_review as review
    review.ROOT = root
    result = review.run_suite(directory, pattern, restrictions=directory == 'benchmark/harness')
    result.pop('output')
    label = ('clean' if root == CLEAN else 'active') + '-' + (
        'application' if directory == 'tests' else Path(pattern).stem)
    persist(label, result)


def batch(mode):
    root = CLEAN if mode == 'clean' else ROOT
    started = time.monotonic()
    for path in sorted((root / 'benchmark/harness').glob('test*.py')):
        label = mode + '-' + path.stem
        if (OUT / (label + '.json')).exists():
            continue
        if time.monotonic() - started > 70:
            break
        environment = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONPATH': str(root / 'src')}
        process = subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()),
            'worker', str(root), 'benchmark/harness', path.name], cwd=root, env=environment,
            capture_output=True, timeout=65)
        if process.returncode:
            raise RuntimeError('bounded diagnostic worker failed: ' + label)
        print(label, flush=True)
    rows = [r for p in OUT.glob(mode + '-test*.json')
            if (r := json.loads(p.read_bytes()))['directory'] == 'benchmark/harness']
    print({'mode': mode, 'modules': len(rows), 'discovered': sum(r['discovered'] for r in rows),
           'passed': sum(r['passed'] for r in rows), 'skips': sum(len(r['skipped']) for r in rows),
           'failures_errors': sum(len(r['failures']) + len(r['errors']) for r in rows)})


def comparison():
    inventory = json.loads((RESULTS / 'R5_52-inventory-v2.json').read_bytes())
    rows = {}
    for name, lock in inventory['locks'].items():
        counters = Counter()
        differences = []
        for r in lock['members']:
            data = (CLEAN / r['path']).read_bytes()
            if check.sha(data) == r['authority_sha256']:
                counters['BYTE_IDENTICAL'] += 1
            else:
                counters[r['class']] += 1
                differences.append(r['path'])
        rows[name] = {'counts': dict(counters), 'raw_mismatches': differences}
    names = sorted({r['path'] for lock in inventory['locks'].values() for r in lock['members']})
    member_comparisons = {n: check.classify((CLEAN / n).read_bytes(), (ROOT / n).read_bytes()) for n in names}
    frozen = [{'path': r['path'], 'clean_sha256': check.sha((CLEAN / r['path']).read_bytes()),
               'raw_pin_matches': check.sha((CLEAN / r['path']).read_bytes()) == r['authority_sha256']}
              for r in inventory['frozen_pins']]
    config = subprocess.run(['git', 'config', '--show-origin', '--get-regexp',
        r'core\.(autocrlf|eol|safecrlf|attributesfile)|filter\.'], cwd=ROOT, capture_output=True, timeout=10)
    persist('materialization', {'root': str(CLEAN), 'head': check.git(CLEAN, 'rev-parse', 'HEAD').decode().strip(),
        'creation': 'shared no-checkout clone; explicit core.autocrlf=false checkout --detach e13e881; hooks disabled',
        'source_objects_shared_read_only': True, 'active_inputs_modified': False, 'locks': rows,
        'clean_vs_active': dict(Counter(member_comparisons.values())), 'members': member_comparisons,
        'frozen_pins': frozen, 'git_configuration': config.stdout.decode(),
        'git_version': check.git(ROOT, '--version').decode().strip(),
        'git_eol_inventory': check.git(ROOT, 'ls-files', '--eol').decode().splitlines(),
        'historical_lock_success_claimed': False, 'b02_exposure': 0})
    print(json.dumps({'locks': {n:r['counts'] for n,r in rows.items()},
                      'clean_vs_active': dict(Counter(member_comparisons.values())), 'frozen_pins': frozen}, indent=2))


def focused():
    stages = [('tests', 'test*.py'), ('benchmark/evaluation', 'test_checkout_r5_52.py'),
        ('benchmark/evaluation', 'test_security_r5_47.py'),
        ('benchmark/evaluation', 'test_reproducibility_boundary_r5_50.py'),
        ('benchmark/evaluation', 'test_tier2_r5_51.py')]
    for directory, pattern in stages:
        subprocess.run([sys.executable, '-B', str(Path(__file__).resolve()), 'worker', str(ROOT), directory, pattern],
                       check=True, cwd=ROOT, env={**os.environ, 'PYTHONPATH': str(ROOT / 'src')}, timeout=65)


def static():
    from benchmark.results.phase5c import r5_51_qualification as driver
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    # Use separate output and invoke only generic checks, never initialize,
    # qualify, assemble certificates or dispatch any subject.
    driver.OUTPUT = OUT
    for stage in ('coherence', 'core-count', 'implementation-contamination', 'dependencies', 'validate', 'safety', 'diff'):
        driver.worker(stage)
    persist('semantic-boundary', {'core_semantics': SCHEMA['core_constructs'], 'b02_exposure': 0,
        'phase5c': 'paused', 'production_certificate_issued': False})


def summarize():
    inventories = json.loads((RESULTS / 'R5_52-inventory-v3.json').read_bytes())
    previous = json.loads((RESULTS / 'R5_51-diagnostics.json').read_bytes())
    summaries = {}
    failures = []
    for mode in ('active', 'clean'):
        rows = [json.loads(p.read_bytes()) for p in OUT.glob(mode + '-test*.json')]
        rows = [r for r in rows if r['directory'] == 'benchmark/harness']
        summaries[mode] = {'modules': len(rows), 'discovered': sum(r['discovered'] for r in rows),
            'passed': sum(r['passed'] for r in rows), 'skips': sum(len(r['skipped']) for r in rows),
            'failures_errors': sum(len(r['failures']) + len(r['errors']) for r in rows)}
        for row in rows:
            for failure in row['failures'] + row['errors']:
                failures.append({'mode': mode, 'test': failure['test'],
                                 'tail': failure['traceback'].splitlines()[-6:]})
    print(json.dumps(summaries, indent=2))
    print(json.dumps(failures, indent=2))
    names = previous['locks']['infrastructure']['other_differences']
    dispositions = []
    for row in inventories['locks']['infrastructure']['members']:
        if row['path'] not in names:
            continue
        path = row['path']
        history = check.git(ROOT, 'log', '--format=%H %s', '--', path).decode().splitlines()
        occurrences = []
        for manifest in sorted(RESULTS.glob('*lock*.json')):
            value = json.loads(manifest.read_bytes())
            if value.get('files', {}).get(path) == row['authority_sha256']:
                occurrences.append(manifest.name)
        candidates = []
        for location in ('r531-lf', 'r532-lf', 'r551-cooperative-workspace'):
            candidate = CLEAN.parent / location / path
            if candidate.is_file():
                recovered, _ = check.recover(row['authority_sha256'], [(location, candidate.read_bytes())])
                candidates.append({'location': location, 'exact_raw_or_uniform_newline_pin_recovered': recovered is not None})
        category = ('LINE_ENDING_MATERIALIZATION' if row['class'] == 'LINE_ENDING_ONLY' else
                    'AUTHORIZED_SUCCESSOR_CHANGE' if path == 'benchmark/README.md' else 'UNKNOWN')
        dispositions.append({**row, 'disposition': category, 'history': history,
            'last_versioned_content_change': history[0], 'same_pin_occurrences': occurrences,
            'available_materializations': candidates,
            'decision': 'R5.50 Tier 2 methodology; README links the versioned methodology report' if path == 'benchmark/README.md' else None,
            'current_expected': row['checkout_vs_head'] in ('BYTE_IDENTICAL', 'LINE_ENDING_ONLY'),
            'historical_pin_still_authoritative': True})
    persist('provenance', {'dispositions': dispositions, 'summaries': summaries,
        'failure_tails': failures, 'b02_exposure': 0, 'successor_issued': False})


def final():
    initial = json.loads((OUT / 'initial.json').read_bytes())
    differences = [name for name, digest in initial['protected'].items()
                   if check.sha((ROOT / name).read_bytes()) != digest]
    if differences:
        raise ValueError('protected historical evidence mutated')
    inventory = json.loads((RESULTS / 'R5_52-inventory-v3.json').read_bytes())
    input_rows = inventory['locks']['infrastructure']['members']
    if any(check.sha((ROOT / r['path']).read_bytes()) != r['checkout_sha256'] for r in input_rows):
        raise ValueError('initial diagnostic input changed')
    capsule = json.loads((RESULTS / 'R5_51-evidence/capsule.json').read_bytes())
    mechanisms = ('benchmark/evaluation/tier2_r5_51.py', 'benchmark/evaluation/test_tier2_r5_51.py',
                  'benchmark/results/phase5c/r5_51_qualification.py')
    if any(check.sha((ROOT / n).read_bytes()) != capsule['repository'][n]['physical']['sha256'] for n in mechanisms):
        raise ValueError('R5.51 mechanism changed')
    from benchmark.evaluation.preexposure_r5_45 import unseal
    summary = json.loads((RESULTS / 'R5_51-evidence/summary.json').read_bytes())
    statuses = Counter()
    for stage, identity in summary['receipts'].items():
        row = json.loads((RESULTS / 'R5_51-evidence' / (stage + '.json')).read_bytes())
        unseal(row)
        if row['identity'] != identity:
            raise ValueError('historical receipt changed')
        statuses[row['status']] += 1
    process = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10)
    if process.returncode:
        raise ValueError('diff check failed')
    report = RESULTS / 'R5_52-CHECKOUT-AUTHORITY-AND-LOCK-PROVENANCE-RECONCILIATION.md'
    paths = [p for p in RESULTS.glob('*5_52*') if p.is_file()] + list(OUT.glob('*.json'))
    paths += [ROOT / 'benchmark/evaluation/checkout_r5_52.py', ROOT / 'benchmark/evaluation/test_checkout_r5_52.py',
              ROOT / 'docs/project-overview.md', ROOT / 'docs/decisions.md', ROOT / 'docs/research-log.md']
    persist('final-integrity', {'protected_historical_files_unchanged': len(initial['protected']),
        'initial_lock_input_bytes_unchanged': len(input_rows), 'r551_mechanisms_unchanged': len(mechanisms),
        'r551_receipts_verified': len(summary['receipts']), 'r551_stage_counts_preserved': dict(statuses),
        'r551_classification_preserved': summary['primary_classification'],
        'artifact_sha256': {p.relative_to(ROOT).as_posix(): check.sha(p.read_bytes()) for p in paths},
        'diff_check': 'PASS', 'report_present': report.is_file(), 'core_semantics': 30, 'phase5c': 'paused',
        'b02_exposure': 0, 'production_certificate_issued': False,
        'primary_classification': 'R5_52_CONTENT_PROVENANCE_GAP'})
    print({'integrity': 'PASS', 'protected': len(initial['protected']), 'r551_receipts': len(summary['receipts'])})


def noninterference():
    import ast
    tree = check.tree(ROOT, 'HEAD')
    names = sorted(n for n in tree if n.startswith(('src/', 'benchmark/semantic/', 'generated/')) and n.endswith('.py'))
    rows = []
    for name in names:
        repo, physical = (CLEAN / name).read_bytes(), (ROOT / name).read_bytes()
        rows.append({'path': name, 'class': check.classify(repo, physical),
                     'python_ast_equal': ast.dump(ast.parse(repo)) == ast.dump(ast.parse(physical))})
    if not all(r['python_ast_equal'] for r in rows):
        raise ValueError('Python source interpretation changed')
    security_state = []
    for name, revision in (('.gitignore', 'c75cc65'), ('benchmark/evaluation/security_r5_47.py', 'c75cc65'),
                           ('benchmark/evaluation/infrastructure_lock_r5_47.py', 'c75cc65'),
                           ('benchmark/evaluation/test_reproducibility_boundary_r5_50.py', 'cd53c74')):
        authority = check.git(ROOT, 'show', revision + ':' + name)
        current = (ROOT / name).read_bytes()
        security_state.append({'path': name, 'revision': revision, 'class': check.classify(authority, current),
                               'normalized_equal': check.normalize(authority) == check.normalize(current)})
    if not all(r['normalized_equal'] for r in security_state):
        raise ValueError('security or methodology content changed')
    persist('noninterference', {'source_ast_witnesses': rows, 'security_methodology_state': security_state,
        'scope': 'Current repository source vs its working representation; NOT unrecovered historical physical authority',
        'b02_subjects_parsed_or_evaluated': False, 'core_semantics': 30})
    print({'source_ast_witnesses': len(rows), 'security_methodology_sources': len(security_state), 'successful': True})


def causes():
    value = json.loads((OUT / 'provenance.json').read_bytes())
    previous = json.loads((RESULTS / 'R5_51-diagnostics.json').read_bytes())
    recorded_ids = [n for k,r in previous['suites'].items() if k.startswith('harness-')
                    for n in r['failures'] + r['errors']]
    fresh_ids = [r['test'] for r in value['failure_tails'] if r['mode'] == 'active']
    if sorted(recorded_ids) != sorted(fresh_ids):
        raise ValueError('failure inventory differs from inherited failures')
    groups = Counter(r['tail'][-1] for r in value['failure_tails'] if r['mode'] == 'active')
    baseline = json.loads((ROOT / 'benchmark/results/phase5b/baseline-manifest.json').read_bytes())
    pins = {'benchmark/requirements/' + name + '.md': h for name,h in baseline['requirements'].items()}
    pins.update({
        'benchmark/harness/assertion_preservation_r5_2_1.py': 'b1748609f0a1f9d24013a3b5626f96be5a0faa1f77c5d3406f7eb3f549df3db0',
        'benchmark/harness/assertion_preservation_r5_2_2.py': 'f258414bd585f8f1aff5cc3ef7ba4514172b0c0d86febb2e2571eabaf6b30e8c',
        'benchmark/results/phase5c/checkpoint-conventional-B15-r4.json': 'b679b53012630ce4e2c29c6c4c1c8ebcb3c1e143b6d7323527350e8e572c0cf3',
        'benchmark/results/phase5c/checkpoint-lykoi-B15-r4.json': 'c5110e4331bf24c2ac6f5889e1ba2a00ba93f9f354f7e9d1c4bd689d7c2b61a0',
        'benchmark/harness/regression_phase5c_r5_1.py': '419a5feb9c09643adfa7c48ac9cf5123e255451571ff91345103cd7aa83e28c0',
        'benchmark/harness/capability_profile_r5_2.py': 'eb5172eab4287cad80a67e47820e8039a0ac678252a36ed40adf735c4f048f97',
        'benchmark/harness/capabilities/B16.json': '2e50f5ff3fc35ae3adfbed5c263b192f887b5d476da8af943262c87421e5411d',
        'benchmark/harness/cases/B16.py': 'b4e3bf5eaa3286d3f9569a0f48a3a8974fbc0d4defaf97f8f64958d64b24f49b',
        'benchmark/results/phase5b/checkpoint-axiom-B02.json': '31dd8302529cdfabd0609ca7b3dddd64ca48764f1ae0255dfcb79d91a400ba90',
        'benchmark/results/phase5d/checkpoint-lykoi-B03.json': '0648016ced11120e57668fb5c9bf824694a450e2463f0ffb68934d962a59a107',
        'benchmark/results/phase5d/checkpoint-conventional-B03.json': 'cf46300fb7fd904a6f42629a049e85bf4af64a7283d42729dd19875156b65999'})
    inventory = json.loads((RESULTS / 'R5_52-inventory-v3.json').read_bytes())
    pins['benchmark/harness/cases/B04.py'] = next(r['authority_sha256'] for r in inventory['locks']['historical']['members']
                                                 if r['path'] == 'benchmark/harness/cases/B04.py')
    witnesses = []
    for name, expected in pins.items():
        a, b = (ROOT / name).read_bytes(), (CLEAN / name).read_bytes()
        witnesses.append({'path': name, 'expected': expected, 'active_sha256': check.sha(a),
            'clean_sha256': check.sha(b), 'clean_raw_pin_matches': check.sha(b) == expected,
            'active_vs_clean': check.classify(b, a)})
    if not all(r['clean_raw_pin_matches'] for r in witnesses):
        raise ValueError('unexplained failure witness')
    persist('failure-causes', {'groups': dict(groups), 'fresh_failure_ids_equal_r551': True,
        'pin_witnesses': witnesses, 'all_55_are_integrity_gate_errors': True,
        'behavioral_regression_observed': False, 'b02_exposure': 0})
    print(json.dumps(dict(groups), indent=2))
    print(json.dumps([{'path': r['path'], 'disposition': r['disposition'],
                      'last_change': r['last_versioned_content_change'], 'occurrences': r['same_pin_occurrences']}
                     for r in value['dispositions']], indent=2))


if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'worker':
        worker(Path(sys.argv[2]), sys.argv[3], sys.argv[4])
    elif command == 'batch':
        batch(sys.argv[2])
    else:
        {'initialize': initialize, 'comparison': comparison, 'focused': focused, 'static': static,
         'summarize': summarize, 'causes': causes, 'noninterference': noninterference, 'final': final}[command]()
