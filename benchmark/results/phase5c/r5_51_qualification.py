"""Bounded R5.51 qualification stages; never loads or evaluates a B02 subject.

Fresh FAIL/INCOMPLETE diagnostics are retained. No historical receipt is reused,
no failed stage is retried, and unsuccessful required locks prevent certification.
"""

import ast
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]

from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure

OUTPUT = Path(os.environ.get('LYKOI_R551_EVIDENCE', str(ROOT / 'benchmark/results/phase5c/R5_51-evidence'))).resolve()
DRIVER = 'benchmark/results/phase5c/r5_51_qualification.py'
EXPERIMENT = 'R5.51-infrastructure-qualification-v1'
LOCKS = {'historical': 'R5_40-implementation-profile-lock.json',
         'prospective': 'R5_41-implementation-lock.json',
         'infrastructure': 'R5_47-infrastructure-lock-v2.json'}


def write(name, value):
    security.persist(OUTPUT / (name + '.json'), value)


def read(name):
    value = (OUTPUT / (name + '.json')).read_bytes()
    item = loads(value)
    if value != canonical(item) + b'\n':
        raise ProtocolFailure('noncanonical qualification evidence')
    return item


def boundary():
    return {'scopes': {
        'subject': ['air', 'generated', 'benchmark/conventional', 'benchmark/results'],
        'compiler': ['src', 'benchmark/semantic'],
        'semantics': ['schema', 'docs/axiom-v0.3.md', 'benchmark/semantic/format.py'],
        'profiles': ['benchmark/semantic', 'benchmark/harness/test_optional_support_r5_41.py'],
        'authority': ['benchmark/requirements', 'benchmark/baseline.md', 'benchmark/harness',
                      'benchmark/README.md', 'benchmark/results/BASELINE.md',
                      'benchmark/results/phase5c/R5_2_2-POST-B16-CORRECTED-CONTINUATION.md',
                      'benchmark/results/phase5c/R5_40-frozen-regression-authority.txt',
                      *['benchmark/results/phase5c/' + p for p in LOCKS.values()]],
        'evaluator': ['benchmark/evaluation', 'benchmark/harness', 'tests', DRIVER,
                      'benchmark/results/phase5c/r5_38_review.py',
                      'benchmark/results/phase5c/r5_41_review.py']},
        'recorder': digest((ROOT / 'benchmark/evaluation/recorder_r5_43.py').read_bytes()),
        'claim': 'frozen externally observable behavioral contract under recorded relevant state and compatible declared platform',
        'purpose': 'infrastructure qualification only; no B02 dispatch authority',
        'consumer': 'explicit restricted suite/stage definitions; no authoring startup or network inference',
        'exclusions': ['development provider/account/model/editor/IDE/prompt configuration outside consumed roots',
                       'evidence/report outputs outside import and discovery roots',
                       'ordinary native descendants represented by platform declaration'],
        'native_materiality': [], 'unknown': []}


def capture():
    executable = shutil.which('git')
    version = subprocess.run([executable, '--version'], capture_output=True, timeout=10).stdout.decode().strip()
    tool = tier.dependency('git', version, executable, 'scoped committed/index content inspection')
    return tier.capture(ROOT, boundary(), tier.controlled_environment(os.environ, ROOT), tools=[tool])


def definitions():
    result = {'harness-' + p.stem: ['suite', 'benchmark/harness', p.name, True]
              for p in sorted((ROOT / 'benchmark/harness').glob('test*.py'))}
    result.update({
        'application': ['suite', 'tests', 'test*.py', False],
        'focused-r541': ['suite', 'benchmark/harness', 'test_optional_support_r5_41.py', True],
        'recorder-r543': ['suite', 'benchmark/harness', 'test_canonical_evidence_r5_43.py', True],
        'certificate-r545': ['suite', 'benchmark/evaluation', 'test_preexposure_r5_45.py', False],
        'security-r547': ['suite', 'benchmark/evaluation', 'test_security_r5_47.py', False],
        'methodology-r550': ['suite', 'benchmark/evaluation', 'test_reproducibility_boundary_r5_50.py', False],
        'ai-independence': ['suite', 'benchmark/evaluation', 'test_ai_independence_r5_49.py', False],
        'tier2': ['suite', 'benchmark/evaluation', 'test_tier2_r5_51.py', False],
        'synthetic-lifecycle': ['synthetic'], 'coherence': ['coherence'],
        'dependencies': ['dependencies'], 'authority-integrity': ['authority'],
        'core-count': ['core'], 'implementation-contamination': ['contamination'],
        **{'lock-' + n: ['lock', n] for n in LOCKS},
        'validate': ['command', 'validate'], 'safety': ['command', 'safety'], 'diff': ['diff']})
    return result


def lock_result(name):
    path = ROOT / 'benchmark/results/phase5c' / LOCKS[name]
    lock = loads(path.read_bytes())
    identity = lock.get('identity', digest(canonical(lock)))
    body = {k: v for k, v in lock.items() if k != 'identity'}
    identity_valid = 'identity' not in lock or digest(canonical(body)) == identity
    differences = [n for n, h in lock['files'].items()
                   if not (ROOT / n).is_file() or digest((ROOT / n).read_bytes()) != h]
    ancestry = subprocess.run([shutil.which('git'), '--no-replace-objects', 'merge-base',
                              '--is-ancestor', lock['head'], 'HEAD'], cwd=ROOT,
                             capture_output=True, timeout=10).returncode == 0
    return {'successful': not differences and identity_valid and ancestry, 'identity': identity,
            'identity_valid': identity_valid, 'members': len(lock['files']),
            'historical_ancestry_valid': ancestry,
            'matching': len(lock['files']) - len(differences), 'differences': differences,
            'treatment': 'physical byte comparison; no line-ending normalization or historical bypass'}


def dependencies():
    from benchmark.evaluation import dependency_provenance_r5_49 as provenance
    from benchmark.evaluation import dependency_inventory_r5_49 as inventory
    external = set()
    dynamic = []
    # Prospective production slice plus fixed-source compiler. Historical study
    # modules are bound as content, but not mislabeled as executed dependencies.
    paths = list((ROOT / 'src').rglob('*.py')) + list((ROOT / 'benchmark/semantic').glob('*.py'))
    paths += list((ROOT / 'benchmark/evaluation').glob('*.py'))
    for path in paths:
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Import):
                external.update(n.name.split('.')[0] for n in node.names)
            elif isinstance(node, ast.ImportFrom) and not node.level and node.module:
                external.add(node.module.split('.')[0])
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == '__import__':
                dynamic.append(path.relative_to(ROOT).as_posix())
    candidates = list((ROOT / 'generated').glob('*.py')) + paths
    bound = provenance.members(ROOT, [p.relative_to(ROOT).as_posix() for p in candidates])
    resolver = provenance.Resolver(bound, installed={})
    deployment = inventory.deployment(ROOT)
    deployed = {r['name']: r for r in deployment['resolved_deployment_helpers']}
    unknown, standalone = [], []
    for name in sorted(external - sys.stdlib_module_names - {'air_compiler', 'benchmark'}):
        matching = [p for p in candidates if p.stem == name]
        if name in deployed:
            standalone.append(deployed[name])
        elif matching:
            standalone.extend({'name': name, **resolver.location(p)} for p in matching)
        else:
            unknown.append(name)
    return {'successful': not unknown, 'direct_nonstandard_roots': unknown,
            'resolved_project_standalone_imports': standalone, 'deployment': deployment,
            'resolved_packages': [], 'dynamic_import_review_locations': sorted(set(dynamic)),
            'policy': 'stdlib under exact declared CPython; project/copy helpers bound in scopes; no third-party requirement',
            'native_boundary': 'ordinary native platform declared; no material native exception identified'}


def worker(name):
    definition = definitions()[name]
    kind = definition[0]
    if kind == 'suite':
        from benchmark.results.phase5c.r5_38_review import run_suite
        result = run_suite(*definition[1:])
        result.pop('output')
        result['failures'] = [r['test'] for r in result['failures']]
        result['errors'] = [r['test'] for r in result['errors']]
    elif kind == 'lock':
        result = lock_result(definition[1])
    elif kind == 'dependencies':
        result = dependencies()
    elif kind == 'core':
        from benchmark.semantic.application_boundary_r5_41 import SCHEMA
        result = {'successful': type(SCHEMA['core_constructs']) is int and SCHEMA['core_constructs'] == 30,
                  'semantic_count': SCHEMA['core_constructs']}
    elif kind == 'contamination':
        from benchmark.results.phase5c.r5_43_qualification import contamination
        result = {**contamination(), 'successful': True}
    elif kind == 'authority':
        expected = {
            'benchmark/requirements/B01.md': 'b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d',
            'benchmark/requirements/B02.md': '8a76e276240fa840c473be60a8e7ed0e10bd0c165426b1bfc84741e69872032b',
            'benchmark/harness/profiles/B02.json': '46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f',
            'benchmark/results/phase5c/R5_40-frozen-regression-authority.txt': '16d55bac4dc1efa3debc6764ddde9dc27c16b7538de476a0fae9cf7db7519596'}
        differences = [n for n, h in expected.items() if digest((ROOT / n).read_bytes()) != h]
        original = subprocess.run([shutil.which('git'), '--no-replace-objects', 'show',
                                   '5064950:benchmark/harness/regression.py'], cwd=ROOT,
                                  capture_output=True, timeout=10)
        original_valid = original.returncode == 0 and digest(original.stdout) == expected[
            'benchmark/results/phase5c/R5_40-frozen-regression-authority.txt']
        result = {'successful': not differences and original_valid, 'members': expected,
                  'differences': differences, 'original_oracle_valid': original_valid,
                  'integrity_only': True, 'oracle_executed': False}
    elif kind == 'synthetic':
        from benchmark.evaluation.test_tier2_r5_51 import Tier2Tests
        fixture = Tier2Tests()
        fixture.setUp()
        try:
            gate = fixture.gate()
            value = gate.observe_synthetic('synthetic:mineral-census', lambda: {'mineral_count': 3})
            artifacts = {p.name: loads(p.read_bytes()) for p in fixture.output.glob('*.json')}
            result = {'successful': value == {'mineral_count': 3}, 'artifacts': artifacts,
                      'synthetic_only': True, 'actual_git_inspection': 'mocked empty synthetic Git records',
                      'b02_exposure': 0, 'counts': gate.recorder.counts()}
        finally:
            fixture.doCleanups()
    elif kind == 'coherence':
        from benchmark.results.phase5c.r5_41_review import matrix
        from benchmark.harness.test_optional_support_r5_41 import setup
        from benchmark.semantic import profile_audit_r5_41 as audit
        app, spec, state, config = setup()
        configuration = {'transport': spec, 'state': state, 'launch': config}
        reference = 'benchmark/harness/test_optional_support_r5_41.py'
        traces = [{'path': p, 'value': v, 'artifact': reference,
                   'sha256': digest((ROOT / reference).read_bytes()), 'clause': 'setup',
                   'interpretation': 'Independent declared shape and public mapping.'}
                  for p, v in audit.leaves(configuration)]
        first, second = matrix(), matrix()
        saved = loads((ROOT / 'benchmark/results/phase5c/R5_41-independent-coherence-matrix.json').read_bytes())
        result = {'profiles': len(first['profiles']), 'rows': len(first['rows']),
                  'canonical_equal': canonical(first) == canonical(saved),
                  'deterministic': canonical(first) == canonical(second),
                  'structure': audit.structure(configuration),
                  'traceability': audit.traceability(configuration, traces, ROOT, {reference}),
                  'contamination': audit.contamination(configuration)}
        result['successful'] = (result['profiles'] == 16 and result['rows'] == 84 and
            result['canonical_equal'] and result['deterministic'] and result['structure']['valid'] and
            result['traceability']['valid'] and not result['contamination'])
    else:
        command = [shutil.which('git'), 'diff', '--check'] if kind == 'diff' else [sys.executable, '-B', '-S', '-c',
            "import sys; sys.path.insert(0,'src'); from air_compiler.cli import main; main()",
            definition[1], 'air/task_manager.json']
        process = subprocess.run(command, cwd=ROOT, env=tier.controlled_environment(os.environ, ROOT),
                                 capture_output=True, timeout=30)
        result = {'successful': process.returncode == 0, 'exit': process.returncode, 'output_withheld': True}
    write(name + '-worker', result)


def initialize():
    OUTPUT.mkdir(exist_ok=False)
    tier.Workspace(ROOT, OUTPUT, EXPERIMENT).enter()
    write('capsule', capture())
    write('definitions', definitions())
    write('authorization', {'experiment': EXPERIMENT, 'scope': 'infrastructure and synthetic observations only',
                            'b02_exposure_authorized': False, 'core_semantics': 30})
    print({'stages': len(definitions()), 'b02_exposure_authorized': False})


def materialize():
    value = tier.Workspace.materialize(ROOT, sys.argv[2], boundary()['scopes'])
    security.persist(ROOT / 'benchmark/results/phase5c/R5_51-materialization.json', value)
    print({'materialization': value['identity'], 'copied_files': len(value['files'])})


def batch():
    if (OUTPUT / 'summary.json').exists() or (OUTPUT / 'quarantine.json').exists():
        raise ProtocolFailure('qualification stopped')
    frozen = read('capsule')
    if frozen != capture():
        raise ProtocolFailure('qualification state changed')
    started = time.monotonic()
    for name, definition in definitions().items():
        if (OUTPUT / (name + '.json')).exists():
            continue
        if (OUTPUT / (name + '-attempt.json')).exists():
            raise ProtocolFailure('incomplete prior attempt; retry prohibited')
        remaining = 85 - (time.monotonic() - started)
        if remaining < 25:
            break
        write(name + '-attempt', {'capsule': frozen['identity'], 'status': 'INCOMPLETE',
                                  'mechanism': digest(canonical(definition))})
        before = capture()
        status, result = 'INCOMPLETE', {'successful': False, 'reason': 'stage interrupted'}
        try:
            process = subprocess.run([sys.executable, '-B', '-S', str(Path(__file__).resolve()), 'worker', name],
                                     cwd=ROOT, env=tier.controlled_environment(os.environ, ROOT),
                                     capture_output=True, timeout=min(65, remaining - 5))
            if process.returncode == 0 and (OUTPUT / (name + '-worker.json')).exists():
                result = read(name + '-worker')
                status = 'PASS' if result['successful'] else 'FAIL'
            else:
                status, result = 'FAIL', {'successful': False, 'reason': 'worker failed; diagnostics withheld'}
        except subprocess.TimeoutExpired:
            pass
        after = capture()
        write(name, tier.receipt(before, after, EXPERIMENT, name, digest(canonical(definition)), status, result))
        print({'stage': name, 'status': status}, flush=True)
        if before != after or before != frozen:
            write('quarantine', {'reason': 'material stage mutation', 'reusable': False, 'b02_exposure': 0})
            raise ProtocolFailure('qualification drift')
    print({'completed': sum((OUTPUT / (n + '.json')).exists() for n in definitions()),
           'required': len(definitions())})


def final():
    frozen = read('capsule')
    if frozen != capture() or (OUTPUT / 'quarantine.json').exists():
        raise ProtocolFailure('qualification identity no longer valid')
    receipts = {n: read(n) for n in definitions()}
    for n, row in receipts.items():
        tier.envelopes.unseal(row)
        if (row['capsule'] != frozen['identity'] or row['experiment'] != EXPERIMENT or
                row['mechanism'] != digest(canonical(definitions()[n]))):
            raise ProtocolFailure('mixed qualification evidence')
    harness = [r['result'] for n, r in receipts.items() if n.startswith('harness-')]
    counts = {'discovered': sum(r.get('discovered', 0) for r in harness),
              'passed': sum(r.get('passed', 0) for r in harness),
              'skipped': sum(len(r.get('skipped', [])) for r in harness)}
    # Explicit negative certificate assembly against actual failed prerequisites.
    policy = {'experiment': EXPERIMENT, 'infrastructure': tier.INFRASTRUCTURE,
              'semantic_count': 30, 'canonical_protocol': tier.CANONICAL_PROTOCOL,
              'authority': frozen['roles']['authority'], 'recorder': frozen['policy']['recorder'],
              'stages': {n: digest(canonical(n)) for n in tier.REQUIRED},
              'required_locks': {n: receipts['lock-' + n]['result']['identity'] for n in LOCKS}}
    lock_pass = all(receipts['lock-' + n]['status'] == 'PASS' for n in LOCKS)
    results = {'identity': {'successful': True, 'semantic_count': 30},
               'locks': {'successful': lock_pass, 'required_lock_state': policy['required_locks']},
               'contamination': {'successful': receipts['coherence']['status'] == 'PASS',
                                 'findings': receipts['coherence']['result'].get('contamination', ['incomplete'])},
               'workspace': {'successful': True, 'dedicated': True}}
    actual = {n: tier.receipt(frozen, frozen, EXPERIMENT, n, policy['stages'][n],
                             'PASS' if results[n]['successful'] else 'FAIL', results[n]) for n in tier.REQUIRED}
    rejected = False
    try:
        tier.certificate(frozen, actual, policy)
    except ProtocolFailure:
        rejected = True
    write('certificate-rejection', {'successful': rejected, 'policy': policy, 'receipts': actual,
                                    'production_certificate_issued': False,
                                    'reason': 'required physical byte locks fail in byte-preserving dedicated workspace'})
    summary = {'primary_classification': 'R5_51_TIER2_CERTIFICATE_GAP',
               'capsule': frozen['identity'], 'restricted_harness': counts,
               'stages': {n: r['status'] for n, r in receipts.items()},
               'receipt_count': len(receipts), 'receipts': {n: r['identity'] for n, r in receipts.items()},
               'production_certificate_issued': False, 'production_qualified': False,
               'synthetic_lifecycle': receipts['synthetic-lifecycle']['status'],
               'b02_exposure': 0, 'core_semantics': 30, 'phase5c': 'paused'}
    write('summary', summary)
    print({'classification': summary['primary_classification'], 'restricted_harness': counts,
           'stages': len(receipts), 'failed': [n for n, r in receipts.items() if r['status'] != 'PASS']})


if __name__ == '__main__':
    try:
        {'materialize': materialize,
         'initialize': initialize, 'batch': batch, 'worker': lambda: worker(sys.argv[2]), 'final': final}[sys.argv[1]]()
    except Exception:
        print('R5.51 operation failed; untrusted diagnostics withheld', file=sys.stderr)
        raise SystemExit(1)
