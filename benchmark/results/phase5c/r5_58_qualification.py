"""Fresh R5.58 experiment orchestration using qualified, unchanged mechanisms."""

import io
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest

ENTRY = time.monotonic()
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import bounded_driver_r5_57 as bounded
from benchmark.evaluation import certificate_r5_55 as certificates
from benchmark.evaluation import qualified_authority_r5_55 as authority
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure
from benchmark.results.phase5c import r5_56_qualification as inherited

RESULTS = ROOT / 'benchmark/results/phase5c'
OUT = Path(os.environ.get('LYKOI_R558_EVIDENCE', str(RESULTS / 'R5_58-evidence')))
WORK = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r558-production-workspace')
DRIVER = 'benchmark/results/phase5c/r5_58_qualification.py'
EXPERIMENT = 'R5.58-fresh-multi-batch-production-tier2-v1'
INTEGRATION = ('production-certificate', 'cooperative-workspace-linkage',
    'production-pre-observation', 'synthetic-reservation', 'synthetic-dispatch',
    'synthetic-completion', 'post-observation', 'second-observation-prevention',
    'no-repair-enforcement', 'independent-final-audit', 'publication-integrity')


def write(name, body):
    security.persist(OUT / (name + '.json'), body)


def read(name):
    raw = (OUT / (name + '.json')).read_bytes()
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    security.safe_bytes(value)
    return value


def boundary():
    policy = inherited.boundary()
    policy['scopes']['evaluator'].extend([DRIVER,
        'benchmark/results/phase5c/r5_58_independent_audit.py',
        'benchmark/results/phase5c/r5_57_driver.py'])
    policy['purpose'] = 'R5.58 fresh production qualification; synthetic only; no repair or retry'
    return policy


def capture():
    executable = shutil.which('git')
    version = subprocess.check_output([executable, '--version'], timeout=10).decode().strip()
    tool = tier.dependency('git', version, executable, 'content/index/provenance qualification only')
    return tier.capture(WORK, boundary(), tier.controlled_environment(os.environ, WORK), tools=[tool])


def flatten(suite):
    for test in suite:
        if isinstance(test, unittest.TestSuite):
            yield from flatten(test)
        else:
            yield test


def freeze():
    assert OUT.parent.is_dir() and not OUT.exists()
    OUT.mkdir()
    tracked = subprocess.check_output(['git', 'ls-files', 'benchmark/results'], cwd=ROOT, text=True).splitlines()
    write('preservation-baseline', {'files': {n: digest((ROOT / n).read_bytes()) for n in tracked}})
    stages = []
    def add(name, definition, purpose, execution='bounded subprocess'):
        stages.append({'name': name, 'definition': definition, 'purpose': purpose,
            'execution_class': execution, 'required': True,
            'dependencies': [stages[-1]['name']] if stages else [],
            'cost': vars(bounded.production_cost(35))})
    for name, definition, purpose in (
        ('identity', ['core'], 'semantic registry remains 30'),
        ('authority', ['qualified-authority'], 'fresh successor authority and all frozen pins'),
        ('contamination', ['contamination'], 'implementation/profile contamination clean'),
        ('workspace', ['workspace'], 'dedicated cooperative ownership')):
        add(name, definition, purpose)
    suites = [('application', 'tests', 'test*.py', False, 8),
        ('focused-r541', 'benchmark/harness', 'test_optional_support_r5_41.py', True, 8),
        ('recorder', 'benchmark/harness', 'test_canonical_evidence_r5_43.py', True, 8),
        ('certificate-v1', 'benchmark/evaluation', 'test_preexposure_r5_45.py', False, 8),
        ('certificate-v2', 'benchmark/evaluation', 'test_certificate_driver_r5_57.py', False, 4),
        ('security', 'benchmark/evaluation', 'test_security_r5_47.py', False, 8),
        ('methodology', 'benchmark/evaluation', 'test_reproducibility_boundary_r5_50.py', False, 8),
        ('tier2', 'benchmark/evaluation', 'test_tier2_r5_51.py', False, 8),
        ('bounded-driver', 'benchmark/evaluation', 'test_bounded_driver_r5_57.py', False, 8),
        ('authority-r553', 'benchmark/evaluation', 'test_authority_r5_53.py', False, 8),
        ('ai-independence', 'benchmark/evaluation', 'test_ai_independence_r5_49.py', False, 8)]
    suites += [('harness-' + p.stem, 'benchmark/harness', p.name, True, 8)
               for p in sorted((ROOT / 'benchmark/harness').glob('test*.py'))]
    for label, directory, pattern, restricted, size in suites:
        loader = unittest.TestLoader()
        tests = list(flatten(loader.discover(str(ROOT / directory), pattern)))
        assert not loader.errors and tests
        ids = [t.id() for t in tests]
        assert len(ids) == len(set(ids))
        for i in range(0, len(ids), size):
            add(f'{label}-{i // size:02d}', ['suite', directory, pattern, restricted, ids[i:i + size]],
                label + ': frozen exact method membership; qualified prospective fixture for CertificateV2')
    for name in ('coherence', 'dependencies', 'validate', 'safety', 'diff'):
        add(name, ['check', name], name + ' including schema/traceability and publication integrity')
    plan = tier.seal({'experiment': EXPERIMENT, 'regressions': stages,
        'integration': [{'name': n, 'required': True, 'dependencies':
            [INTEGRATION[i - 1]] if i else [stages[-1]['name']],
            'purpose': n, 'execution_class': 'qualified production integration; synthetic only'}
            for i, n in enumerate(INTEGRATION)],
        'budget_seconds': 110, 'boundary_reserve': 5,
        'policy': 'fixed order; stop on FAIL or INCOMPLETE; clean boundaries remain pending',
        'stage_granularity': 'at most eight methods; CertificateV2 at most four; no dynamic splitting',
        'b02_authorized': False, 'core_semantics': 30})
    write('stage-plan', plan)
    print({'plan': plan['identity'], 'required_regression_stages': len(stages), 'integration': len(INTEGRATION)})


def initialize():
    assert WORK.parent.is_dir() and not WORK.exists()
    plan = read('stage-plan')
    prior = loads((RESULTS / 'R5_55-qualified-evidence/materialization.json').read_bytes())
    names = ('benchmark/evaluation/qualified_authority_r5_55.py',
        'benchmark/evaluation/certificate_r5_55.py', 'benchmark/evaluation/tier2_r5_51.py',
        'benchmark/evaluation/test_reproducibility_boundary_r5_50.py')
    continuity = {n: digest((ROOT / n).read_bytes()) for n in names}
    assert all(h == prior['files'][n]['sha256'] for n, h in continuity.items())
    r557 = loads((RESULTS / 'R5_57-evidence/summary.json').read_bytes())
    assert r557['classification'] == 'R5_57_BOUNDED_DRIVER_QUALIFIED'
    assert digest((ROOT / 'benchmark/evaluation/bounded_driver_r5_57.py').read_bytes()) == r557['implementation']['benchmark/evaluation/bounded_driver_r5_57.py']
    authorization = loads((RESULTS / 'R5_55-qualified-evidence/authorization.json').read_bytes())
    assert digest(canonical(authorization)) == inherited.PIN
    manifest = loads((ROOT / authorization['manifest']).read_bytes())
    assert manifest['identity'] == inherited.CURRENT and len(manifest['members']) == 1083
    material = tier.Workspace.materialize(ROOT, WORK, boundary()['scopes'])
    write('materialization', material)
    blobs = checkout.blobs(WORK, [r['blob'] for r in manifest['members'].values() if r['blob']])
    changes = {}
    preserved = inherited.PRESERVE | set(authorization['historical_evidence'])
    for name, row in manifest['members'].items():
        physical = (WORK / name).read_bytes()
        repository = physical if row['blob'] is None else blobs[row['blob']]
        assert digest(repository) == row['sha256']
        if name in inherited.PROSE:
            selected = repository
        elif name not in preserved and row['kind'] == 'utf8-lf-text':
            assert physical.replace(b'\r\n', b'\n') == repository
            selected = repository
        else:
            selected = physical
        if selected != physical:
            (WORK / name).write_bytes(selected)
            changes[name] = {'source': digest(physical), 'selected': digest(selected)}
    write('pre-freeze-selection', {'changes': changes, 'policy': 'existing qualified LF representation and pinned baseline prose',
        'historical_results_reclassified': False, 'source_files_modified': False})
    write('authority-policy', authorization)
    gate_dir = OUT / 'production-gate'
    gate_dir.mkdir()
    marker = tier.Workspace(WORK, gate_dir, EXPERIMENT).enter()
    qualified = authority.qualify(WORK, authorization, trusted_policy_identity=inherited.PIN)
    write('qualified-authority', qualified)
    frozen = capture()
    assert frozen == capture() == loads(canonical(frozen))
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    assert not contamination()['findings'] and SCHEMA['core_constructs'] == 30
    write('capsule', frozen)
    write('starting-state', {'status': 'PASS', 'implementation_continuity': continuity,
        'qualified_driver': bounded.VERSION, 'qualified_authority': qualified['identity'],
        'members': 1083, 'capsule': frozen['identity'], 'deterministic_capture': True,
        'canonical_reload': True, 'workspace': marker, 'contamination': 'clean',
        'semantic_count': 30, 'b02_exposure': 0,
        'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'r556_receipts_reused': False, 'plan': plan['identity']})
    (OUT / 'batches').mkdir()
    driver().initialize()
    print({'starting_state': 'PASS', 'capsule': frozen['identity'], 'authority': qualified['identity']})


def mechanism(stage):
    return digest(canonical({'plan': read('stage-plan')['identity'], 'stage': stage,
        'driver': digest((WORK / DRIVER).read_bytes())}))


def live_authority():
    return authority.qualify(WORK, read('authority-policy'), trusted_policy_identity=inherited.PIN)['identity']


def driver():
    stages = {}
    for stage in read('stage-plan')['regressions']:
        name = stage['name']
        environment = tier.controlled_environment(os.environ, WORK)
        environment['LYKOI_R558_EVIDENCE'] = str(OUT)
        stages[name] = {'mechanism': mechanism(stage), 'cost': bounded.Cost(**stage['cost']),
            'run': bounded.child([sys.executable, '-B', '-S', str(WORK / DRIVER), 'worker', name],
                WORK, environment, OUT / (name + '-worker.json'))}
    return bounded.Driver(OUT / 'batches', EXPERIMENT, read('capsule'), read('qualified-authority')['identity'],
        stages, capture, live_authority)


def worker(name):
    stage = next(s for s in read('stage-plan')['regressions'] if s['name'] == name)
    definition = stage['definition']
    if definition[0] == 'suite':
        _, directory, pattern, restricted, ids = definition
        loader = unittest.TestLoader()
        tests = {t.id(): t for t in flatten(loader.discover(str(ROOT / directory), pattern))}
        assert not loader.errors and set(ids).issubset(tests)
        selected = [tests[i] for i in ids]
        for test in selected:
            identity = test.id()
            prohibited = restricted and (identity.startswith(('test_b02_retry_r5_17.',
                'test_b02_retry_r5_19.', 'test_b02_retry_r5_21.', 'test_b02_integration_r5_23.')) or
                identity.endswith('test_read_only_validation_of_both_continuation_states'))
            historical = identity.endswith('test_lock_and_frozen_artifacts_remain_byte_identical')
            if prohibited or historical:
                def skip(prohibited=prohibited):
                    raise unittest.SkipTest('sealed B02 restriction' if prohibited else 'preserved historical live-tree assertion')
                setattr(test, test._testMethodName, skip)
        started = time.monotonic()
        result = unittest.TextTestRunner(stream=io.StringIO(), verbosity=2).run(unittest.TestSuite(selected))
        value = {'successful': result.wasSuccessful(), 'discovered': result.testsRun,
            'passed': result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
            'failures': [t.id() for t, _ in result.failures], 'errors': [t.id() for t, _ in result.errors],
            'skipped': [{'test': t.id(), 'reason': reason} for t, reason in result.skipped],
            'method_ids': ids, 'seconds': time.monotonic() - started}
    elif definition[0] == 'qualified-authority':
        value = {'successful': live_authority() == read('qualified-authority')['identity'],
            'qualified_authority': live_authority(), 'members': 1083}
    elif definition[0] == 'workspace':
        value = {'successful': True, **tier.Workspace(WORK, OUT / 'production-gate', EXPERIMENT).verify()}
    else:
        from benchmark.results.phase5c import r5_51_qualification as old
        old.OUTPUT = OUT
        mapping = {'identity': 'core-count', 'contamination': 'implementation-contamination'}
        target = mapping.get(name, name)
        old.worker(target)
        value = read(target + '-worker')
        if name == 'contamination':
            value['successful'] = value['findings'] == []
        if target == name:
            return
    write(name + '-worker', value)


def batch():
    assert not (OUT / 'summary.json').exists()
    row = driver().batch(110, started=ENTRY)
    print({'batch': row['identity'], 'new_receipts': len(row['receipts']),
        'disposition': row['disposition'], 'next': row['next'], 'elapsed': row['elapsed']})
    if row['disposition'] == 'STOPPED':
        raise SystemExit(2)


def finish():
    receipts, _, count = driver().validate()
    plan = read('stage-plan')
    assert len(receipts) == len(plan['regressions'])
    qualified, frozen, authorization = [read(n) for n in ('qualified-authority', 'capsule', 'authority-policy')]
    statuses = {s['name']: 'PASS' for s in plan['regressions']}
    statuses.update({n: 'NOT_RUN' for n in INTEGRATION})
    policy = {'experiment': EXPERIMENT, 'stages': {s['name']: mechanism(s) for s in plan['regressions']},
        'qualified_authority': qualified['identity'], 'authority_role': frozen['roles']['authority'],
        'semantic_count': 30, 'canonical_protocol': tier.CANONICAL_PROTOCOL,
        'recorder': frozen['policy']['recorder'],
        'observation_state': {'reservations': 0, 'dispatches': 0, 'completions': 0}}
    write('certificate-policy', policy)
    classification = 'R5_58_PRODUCTION_CERTIFICATE_GAP'
    issued = False
    try:
        cert = certificates.certificate(qualified, frozen, receipts, policy, WORK, authorization,
            trusted_policy_identity=inherited.PIN)
        write('certificate', cert)
        assert cert == loads(canonical(cert)) == certificates.certificate(qualified, frozen, receipts,
            policy, WORK, authorization, trusted_policy_identity=inherited.PIN)
        assert certificates.validate(read('certificate'), qualified, frozen, receipts, policy,
            capture(), WORK, authorization, trusted_policy_identity=inherited.PIN)
        issued = True
        statuses['production-certificate'] = 'PASS'
        write('certificate-verification', {'status': 'PASS', 'deterministic_assembly': True,
            'canonical_reload': True, 'fresh_linkage': True, 'receipt_count': len(receipts)})
    except ProtocolFailure:
        statuses['production-certificate'] = 'FAIL'
    if issued:
        workspace = tier.Workspace(WORK, OUT / 'production-gate', EXPERIMENT)
        workspace.verify()
        assert capture() == frozen and live_authority() == qualified['identity']
        statuses['cooperative-workspace-linkage'] = 'PASS'
        write('workspace-linkage', {'status': 'PASS', 'authority': qualified['identity'],
            'capsule': frozen['identity'], 'certificate': cert['identity'], 'workspace': workspace.verify()})
        gate = tier.StaticGate(workspace, cert, frozen, receipts, policy, capture,
            {'locks': lambda: {}, 'authority': live_authority, 'contamination': lambda: []})
        try:
            gate.prepare()
        except ProtocolFailure:
            statuses['production-pre-observation'] = 'FAIL'
            classification = 'R5_58_OBSERVATION_CONTROL_GAP'
            write('production-pre-observation', {'status': 'FAIL',
                'component': 'tier2_r5_51.StaticGate.prepare -> tier2_r5_51.validate -> CertificateV1',
                'v2_validation_separately_passed': True, 'reservation_permitted': False,
                'reason': 'qualified production StaticGate does not consume successor-aware ProductionCertificateV2',
                'repair_permitted': False, 'retry_permitted': False})
        else:
            raise ProtocolFailure('unexpected gate compatibility: stop before synthetic dispatch')
    write('terminal-stop', {'classification': classification, 'repair_permitted': False,
        'retry_permitted': False, 'b02_exposure': 0, 'synthetic_reservations': 0,
        'synthetic_dispatches': 0, 'synthetic_completions': 0})
    harness = [r['result'] for n, r in receipts.items() if n.startswith('harness-')]
    write('summary', {'primary_classification': classification, 'stages': statuses,
        'plan': plan['identity'], 'qualification': bounded.reload(OUT / 'batches/qualification.json')['identity'],
        'batches': count, 'receipt_count': len(receipts),
        'receipts': {n: r['identity'] for n, r in receipts.items()},
        'tests_passed': sum(r['result'].get('passed', 0) for r in receipts.values()),
        'restricted_harness': {'discovered': sum(r.get('discovered', 0) for r in harness),
            'passed': sum(r.get('passed', 0) for r in harness),
            'skipped': sum(len(r.get('skipped', [])) for r in harness)},
        'production_certificate_issued': issued, 'production_qualified': False,
        'capsule': frozen['identity'], 'qualified_authority': qualified['identity'],
        'synthetic_reservations': 0, 'synthetic_dispatches': 0, 'synthetic_completions': 0,
        'b02_exposure': 0, 'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'core_semantics': 30, 'phase5c': 'paused'})
    print({'classification': classification, 'certificate_issued': issued, 'receipts': len(receipts)})


if __name__ == '__main__':
    {'freeze': freeze, 'initialize': initialize, 'batch': batch,
     'worker': lambda: worker(sys.argv[2]), 'finish': finish}[sys.argv[1]]()
