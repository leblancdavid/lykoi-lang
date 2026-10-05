"""R5.60 frozen experiment orchestration; unchanged qualified mechanisms.

No subject loader. FAIL/INCOMPLETE is terminal. Outputs are never repair inputs.
"""

import os
from pathlib import Path
import subprocess
import sys
import time
import unittest

ENTRY = time.monotonic()
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import bounded_driver_r5_57 as bounded
from benchmark.evaluation import certificate_r5_55 as certificates
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import continuity_r5_59 as continuity
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import qualified_authority_r5_55 as authority
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure
from benchmark.results.phase5c import r5_58_qualification as prior

RESULTS = ROOT / 'benchmark/results/phase5c'
OUT = Path(os.environ.get('LYKOI_R560_EVIDENCE', str(RESULTS / 'R5_60-evidence')))
WORK = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r560-production-workspace')
DRIVER = 'benchmark/results/phase5c/r5_60_qualification.py'
EXPERIMENT = 'R5.60-final-fresh-production-tier2-v1'
INTEGRATION = prior.INTEGRATION
BASE_BOUNDARY = prior.inherited.boundary


def write(name, value):
    publication.persist(OUT / (name + '.json'), value)


def read(name):
    raw = (OUT / (name + '.json')).read_bytes()
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    publication.safe_bytes(value)
    return value


def boundary():
    policy = BASE_BOUNDARY()
    policy['scopes']['evaluator'].extend([DRIVER,
        'benchmark/results/phase5c/r5_60_independent_audit.py',
        'benchmark/results/phase5c/r5_58_qualification.py',
        'benchmark/results/phase5c/r5_57_driver.py'])
    policy['purpose'] = 'R5.60 final fresh production qualification; synthetic only; no repair/retry'
    return policy


def capture():
    return prior.capture()


def freeze():
    assert OUT.parent.is_dir() and not OUT.exists()
    OUT.mkdir()
    names = subprocess.check_output(['git', 'ls-files', 'benchmark/results'], cwd=ROOT, text=True).splitlines()
    write('preservation-baseline', {'files': {n: digest((ROOT / n).read_bytes()) for n in names}})
    stages = []
    def add(name, definition, purpose):
        stages.append({'name': name, 'definition': definition, 'purpose': purpose,
            'required': True, 'execution_class': 'bounded subprocess',
            'dependencies': [stages[-1]['name']] if stages else [],
            'cost': vars(bounded.production_cost(35))})
    for name, definition in (('identity', ['core']), ('authority', ['qualified-authority']),
                             ('contamination', ['contamination']), ('workspace', ['workspace'])):
        add(name, definition, name)
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
        ('checkout', 'benchmark/evaluation', 'test_checkout_r5_52.py', False, 8),
        ('continuity', 'benchmark/evaluation', 'test_continuity_r5_59.py', False, 8),
        ('publication', 'benchmark/evaluation', 'test_publication_r5_59.py', False, 8),
        ('ai-independence', 'benchmark/evaluation', 'test_ai_independence_r5_49.py', False, 8)]
    suites += [('harness-' + p.stem, 'benchmark/harness', p.name, True, 8)
               for p in sorted((ROOT / 'benchmark/harness').glob('test*.py'))]
    for label, directory, pattern, restricted, size in suites:
        loader = unittest.TestLoader()
        tests = list(prior.flatten(loader.discover(str(ROOT / directory), pattern)))
        assert not loader.errors and tests
        ids = [t.id() for t in tests]
        assert len(ids) == len(set(ids))
        for i in range(0, len(ids), size):
            add(f'{label}-{i // size:02d}', ['suite', directory, pattern, restricted, ids[i:i + size]],
                'frozen exact methods; existing prospective CertificateV2 fixture')
    for name in ('coherence', 'dependencies', 'validate', 'safety', 'diff'):
        add(name, ['check', name], 'current matrix/schema/traceability and required checks')
    add('publication-integrity-regression', ['publication-integrity'], 'canonical secret-safe outputs and preservation')
    pre = ('starting-continuity', 'authority-materialization', 'qualified-authority',
           'tier2-capsule', 'starting-state')
    plan = tier.seal({'experiment': EXPERIMENT, 'regressions': stages,
        'preflight': [{'name': n, 'required': True, 'execution_class': 'qualified existing API',
                       'dependencies': [] if i == 0 else [pre[i - 1]]}
                      for i, n in enumerate(pre)],
        'integration': [{'name': n, 'required': True,
            'dependencies': [INTEGRATION[i - 1]] if i else [stages[-1]['name']],
            'execution_class': 'qualified production integration; synthetic only'}
            for i, n in enumerate(INTEGRATION)],
        'budget_seconds': 110, 'boundary_reserve': 5,
        'stage_granularity': 'at most eight methods; CertificateV2 at most four; never split dynamically',
        'policy': 'fixed order; terminal FAIL/INCOMPLETE; non-admitted stages PENDING',
        'restrictions': 'existing sealed-B02 and historical-live-tree skips only; no receipt reuse',
        'materialization_policy': 'existing qualified LF baseline and exact pinned authority inputs before capture',
        'b02_authorized': False, 'core_semantics': 30})
    write('stage-plan', plan)
    write('qualification-identity', tier.seal({'experiment': EXPERIMENT, 'plan': plan['identity'],
        'authority': prior.inherited.CURRENT, 'bounded_driver': bounded.VERSION,
        'driver_implementation': digest((ROOT / 'benchmark/evaluation/bounded_driver_r5_57.py').read_bytes()),
        'orchestration': digest((ROOT / DRIVER).read_bytes()), 'fresh_receipts_only': True}))
    print({'plan': plan['identity'], 'qualification': read('qualification-identity')['identity'],
           'required_regressions': len(stages), 'integration': len(INTEGRATION)})


def initialize():
    assert not (OUT / 'summary.json').exists()
    phase = 'starting-continuity'
    try:
        assert WORK.parent.is_dir() and not WORK.exists()
        plan = read('stage-plan')
        identity = read('qualification-identity')
        tier.envelopes.unseal(plan)
        tier.envelopes.unseal(identity)
        assert identity['plan'] == plan['identity']
        snapshot = loads((RESULTS / 'R5_55-qualified-evidence/materialization.json').read_bytes())
        tree = checkout.tree(ROOT, 'HEAD')
        names = ('benchmark/evaluation/qualified_authority_r5_55.py',
                 'benchmark/evaluation/certificate_r5_55.py', 'benchmark/evaluation/tier2_r5_51.py',
                 'benchmark/evaluation/test_reproducibility_boundary_r5_50.py')
        rows = {}
        for n in names:
            repository = checkout.blobs(ROOT, [tree[n]['blob']])[tree[n]['blob']]
            rows[n] = continuity.verify(repository, (ROOT / n).read_bytes(),
                repository_sha256=snapshot['files'][n]['sha256'], kind='utf8-lf-text')
        r557 = loads((RESULTS / 'R5_57-evidence/summary.json').read_bytes())
        r559 = loads((RESULTS / 'R5_59-evidence/summary.json').read_bytes())
        assert r557['classification'] == 'R5_57_BOUNDED_DRIVER_QUALIFIED'
        assert r559['classification'] == 'R5_59_CONTINUITY_PUBLICATION_RECONCILED'
        n = 'benchmark/evaluation/bounded_driver_r5_57.py'
        repository = checkout.blobs(ROOT, [tree[n]['blob']])[tree[n]['blob']]
        rows[n] = continuity.verify(repository, (ROOT / n).read_bytes(),
            repository_sha256=r557['implementation'][n], kind='utf8-lf-text')
        pins = loads((RESULTS / 'R5_59-evidence/publication-integrity.json').read_bytes())['source_sha256']
        for n in ('benchmark/evaluation/continuity_r5_59.py', 'benchmark/evaluation/publication_r5_59.py'):
            repository = checkout.blobs(ROOT, [tree[n]['blob']])[tree[n]['blob']]
            # The focused source record pins physical bytes. Establish its repository
            # identity from the independent committed blob, preserving both records.
            assert digest(repository) == pins[n] or digest(repository.replace(b'\n', b'\r\n')) == pins[n]
            rows[n] = continuity.verify(repository, (ROOT / n).read_bytes(),
                repository_sha256=digest(repository), kind='utf8-lf-text')
        write('starting-continuity', {'status': 'PASS', 'mechanisms': rows})
        phase = 'authority-materialization'
        authorization = loads((RESULTS / 'R5_55-qualified-evidence/authorization.json').read_bytes())
        assert digest(canonical(authorization)) == prior.inherited.PIN
        manifest = loads((ROOT / authorization['manifest']).read_bytes())
        assert manifest['identity'] == prior.inherited.CURRENT and len(manifest['members']) == 1083
        write('materialization', tier.Workspace.materialize(ROOT, WORK, boundary()['scopes']))
        blobs = checkout.blobs(WORK, [r['blob'] for r in manifest['members'].values() if r['blob']])
        changes = {}
        preserved = prior.inherited.PRESERVE | set(authorization['historical_evidence'])
        for n, row in manifest['members'].items():
            physical = (WORK / n).read_bytes()
            repository = physical if row['blob'] is None else blobs[row['blob']]
            if row['blob'] is None and row['kind'] == 'utf8-lf-text':
                repository = physical.replace(b'\r\n', b'\n')
            assert digest(repository) == row['sha256']
            selected = physical
            if n in prior.inherited.PROSE or n not in preserved and row['kind'] == 'utf8-lf-text':
                if n not in prior.inherited.PROSE:
                    continuity.verify(repository, physical, repository_sha256=row['sha256'], kind=row['kind'])
                selected = repository
            if selected != physical:
                (WORK / n).write_bytes(selected)
                changes[n] = {'source': digest(physical), 'selected': digest(selected)}
        # Exact-byte evidence is materialized from already pinned repository data;
        # it is never accepted by a text-equivalence comparison.
        exact = {authorization['manifest']: authorization['manifest_sha256'],
                 authorization['qualification']: authorization['qualification_sha256'],
                 authorization['audit']: authorization['audit_sha256'],
                 authorization['decision']: manifest['decision_sha256'],
                 **authorization['historical_evidence'],
                 **{authorization['predecessor_root'] + '/' + r['path']: r['raw_sha256']
                    for r in manifest['predecessors']}}
        for n, pin in exact.items():
            physical = (WORK / n).read_bytes()
            if digest(physical) == pin:
                continue
            repository = checkout.git(WORK, 'show', 'HEAD:' + n)
            candidates = (repository, repository.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))
            selected = next(v for v in candidates if digest(v) == pin)
            (WORK / n).write_bytes(selected)
            changes[n] = {'source': digest(physical), 'selected': pin, 'exact_pin': True}
        write('pre-freeze-selection', {'changes': changes, 'source_files_modified': False,
            'historical_results_reclassified': False, 'policy': plan['materialization_policy']})
        write('authority-policy', authorization)
        (OUT / 'production-gate').mkdir()
        marker = tier.Workspace(WORK, OUT / 'production-gate', EXPERIMENT).enter()
        phase = 'qualified-authority'
        qualified = authority.qualify(WORK, authorization, trusted_policy_identity=prior.inherited.PIN)
        write('qualified-authority', qualified)
        phase = 'tier2-capsule'
        frozen = capture()
        assert frozen == capture() == loads(canonical(frozen))
        write('capsule', frozen)
        phase = 'starting-state'
        from benchmark.results.phase5c.r5_43_qualification import contamination
        from benchmark.semantic.application_boundary_r5_41 import SCHEMA
        assert not contamination()['findings'] and SCHEMA['core_constructs'] == 30
        write('starting-state', {'status': 'PASS', 'qualified_authority': qualified['identity'],
            'members': 1083, 'capsule': frozen['identity'], 'deterministic_capture': True,
            'canonical_reload': True, 'workspace': marker, 'continuity': continuity.VERSION,
            'publication': 'publication_r5_59', 'contamination': 'clean', 'semantic_count': 30,
            'b02_exposure': 0, 'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
            'plan': plan['identity'], 'qualification': identity['identity'], 'receipts_reused': False})
        (OUT / 'batches').mkdir()
        driver().initialize()
        print({'starting_state': 'PASS', 'authority': qualified['identity'], 'capsule': frozen['identity']})
    except Exception as error:
        write('starting-state-failure', {'status': 'FAIL', 'stage': phase,
            'exception_class': type(error).__name__, 'diagnostics': 'withheld', 'repair_permitted': False})
        classification = ('R5_60_QUALIFIED_AUTHORITY_GAP' if phase in ('qualified-authority', 'authority-materialization')
            else 'R5_60_TIER2_CAPSULE_GAP' if phase == 'tier2-capsule' else 'R5_60_PROTOCOL_HALT')
        stop(classification, phase)
        raise SystemExit(2)


def mechanism(stage):
    return digest(canonical({'plan': read('stage-plan')['identity'], 'stage': stage,
        'qualification': read('qualification-identity')['identity'], 'version': bounded.VERSION,
        'driver': digest((WORK / DRIVER).read_bytes())}))


def live_authority():
    return authority.qualify(WORK, read('authority-policy'), trusted_policy_identity=prior.inherited.PIN)['identity']


def driver():
    identity, plan = read('qualification-identity'), read('stage-plan')
    tier.envelopes.unseal(identity)
    tier.envelopes.unseal(plan)
    assert identity['plan'] == plan['identity'] and identity['experiment'] == EXPERIMENT
    assert identity['orchestration'] == digest((WORK / DRIVER).read_bytes())
    stages = {}
    for stage in plan['regressions']:
        n = stage['name']
        environment = tier.controlled_environment(os.environ, WORK)
        environment['LYKOI_R560_EVIDENCE'] = str(OUT)
        stages[n] = {'mechanism': mechanism(stage), 'cost': bounded.Cost(**stage['cost']),
            'run': bounded.child([sys.executable, '-B', '-S', str(WORK / DRIVER), 'worker', n],
                                  WORK, environment, OUT / (n + '-worker.json'))}
    return bounded.Driver(OUT / 'batches', EXPERIMENT, read('capsule'), read('qualified-authority')['identity'],
                          stages, capture, live_authority)


def worker(name):
    if name == 'publication-integrity-regression':
        for path in OUT.rglob('*.json'):
            raw = path.read_bytes()
            value = loads(raw)
            assert raw == canonical(value) + b'\n'
            publication.safe_bytes(value)
        write(name + '-worker', {'successful': True, 'publication': 'PASS'})
    else:
        prior.worker(name)


def batch():
    assert not (OUT / 'summary.json').exists()
    row = driver().batch(110, started=ENTRY)
    print({'batch': row['identity'], 'receipts': len(row['receipts']),
           'disposition': row['disposition'], 'next': row['next'], 'elapsed': row['elapsed']})
    if row['disposition'] == 'STOPPED':
        stop('R5_60_PRODUCTION_REGRESSION_GAP', list(row['receipts'])[-1])
        raise SystemExit(2)


def stop(classification, failed_stage, statuses=None):
    plan = read('stage-plan')
    receipts = {p.stem[len('receipt-'):]: bounded.reload(p)
                for p in (OUT / 'batches').glob('receipt-*.json')}
    states = {s['name']: receipts[s['name']]['status'] if s['name'] in receipts else 'NOT_RUN'
              for s in plan['regressions']}
    states.update({n: 'NOT_RUN' for n in INTEGRATION})
    states.update(statuses or {})
    gate_files = sorted(p.name for p in (OUT / 'production-gate').glob('*'))
    write('summary', {'primary_classification': classification, 'failed_stage': failed_stage,
        'plan': plan['identity'], 'qualification': read('qualification-identity')['identity'],
        'stages': states, 'receipt_count': len(receipts),
        'receipts': {n: r['identity'] for n, r in receipts.items()},
        'batches': len(list((OUT / 'batches').glob('batch-*.json'))),
        'production_certificate_issued': (OUT / 'certificate.json').exists(),
        'production_qualified': False, 'repair_permitted': False, 'retry_permitted': False,
        'synthetic_reservations': 0, 'synthetic_dispatches': 0, 'synthetic_completions': 0,
        'gate_files': gate_files, 'b02_exposure': 0,
        'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'core_semantics': 30, 'phase5c': 'paused'})


def finish():
    assert not (OUT / 'summary.json').exists()
    receipts, _, count = driver().validate()
    assert len(receipts) == len(read('stage-plan')['regressions'])
    qualified, frozen, authorization = [read(n) for n in ('qualified-authority', 'capsule', 'authority-policy')]
    policy = {'experiment': EXPERIMENT,
        'stages': {s['name']: mechanism(s) for s in read('stage-plan')['regressions']},
        'qualified_authority': qualified['identity'], 'authority_role': frozen['roles']['authority'],
        'semantic_count': 30, 'canonical_protocol': tier.CANONICAL_PROTOCOL,
        'recorder': frozen['policy']['recorder'],
        'observation_state': {'reservations': 0, 'dispatches': 0, 'completions': 0}}
    write('certificate-policy', policy)
    statuses = {}
    try:
        cert = certificates.certificate(qualified, frozen, receipts, policy, WORK, authorization,
                                        trusted_policy_identity=prior.inherited.PIN)
        assert cert == loads(canonical(cert)) == certificates.certificate(qualified, frozen, receipts,
            policy, WORK, authorization, trusted_policy_identity=prior.inherited.PIN)
        write('certificate', cert)
        assert certificates.validate(cert, qualified, frozen, receipts, policy, capture(), WORK,
            authorization, trusted_policy_identity=prior.inherited.PIN)
        statuses['production-certificate'] = 'PASS'
    except Exception:
        statuses['production-certificate'] = 'FAIL'
        stop('R5_60_PRODUCTION_CERTIFICATE_GAP', 'production-certificate', statuses)
        return
    workspace = tier.Workspace(WORK, OUT / 'production-gate', EXPERIMENT)
    workspace.verify()
    assert capture() == frozen and live_authority() == qualified['identity']
    statuses['cooperative-workspace-linkage'] = 'PASS'
    write('workspace-linkage', {'status': 'PASS', 'certificate': cert['identity'],
        'capsule': frozen['identity'], 'authority': qualified['identity'], 'workspace': workspace.verify()})
    gate = tier.StaticGate(workspace, cert, frozen, receipts, policy, capture,
                          {'locks': lambda: {}, 'authority': live_authority, 'contamination': lambda: []})
    try:
        gate.prepare()
    except ProtocolFailure:
        statuses['production-pre-observation'] = 'FAIL'
        write('production-pre-observation', {'status': 'FAIL', 'reservation_permitted': False,
            'component': 'tier2_r5_51.StaticGate.prepare -> tier2_r5_51.validate -> CertificateV1',
            'v2_validation_separately_passed': True, 'repair_permitted': False,
            'diagnostics': 'withheld'})
        stop('R5_60_OBSERVATION_CONTROL_GAP', 'production-pre-observation', statuses)
        print({'classification': read('summary')['primary_classification'], 'batches': count})
        return
    # Existing control requires the legacy certificate protocol. Reaching here
    # contrary to that fixed implementation is a state-integrity halt, not a
    # permission to improvise a dispatch adapter.
    stop('R5_60_PROTOCOL_HALT', 'unexpected-production-gate-state', statuses)


# Reuse only historical orchestration helpers, never their saved receipts.
prior.OUT, prior.WORK, prior.DRIVER, prior.EXPERIMENT = OUT, WORK, DRIVER, EXPERIMENT
prior.write, prior.read, prior.boundary = write, read, boundary
prior.mechanism, prior.live_authority = mechanism, live_authority

if __name__ == '__main__':
    {'freeze': freeze, 'initialize': initialize, 'batch': batch,
     'worker': lambda: worker(sys.argv[2]), 'finish': finish}[sys.argv[1]]()
