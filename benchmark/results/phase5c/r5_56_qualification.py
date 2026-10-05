"""Fresh bounded qualification using unchanged R5.50/51/53/55 mechanisms.

No benchmark subject loader or new observation/certificate mechanism. A concrete
integration failure stops this candidate; all downstream stages remain incomplete.
"""

from collections import Counter
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import certificate_r5_55 as certificates
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import qualified_authority_r5_55 as authority
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure

RESULTS = ROOT / 'benchmark/results/phase5c'
OUT = Path(os.environ.get('LYKOI_R551_EVIDENCE', str(RESULTS / 'R5_56-evidence')))
WORK = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r556-qualified-production-workspace')
EXPERIMENT = 'R5.56-fresh-complete-production-tier2-qualification-v1'
DRIVER = 'benchmark/results/phase5c/r5_56_qualification.py'
PIN = '31d4b3632cfcdbf1e928ddf3cbeaf2b88fad97e50ba502b78cf1434d09a114b8'
CURRENT = '5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea'
PROSE = {'docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md'}
PRESERVE = {'benchmark/results/phase5c/' + n for n in (
    'R5_40-implementation-profile-lock.json', 'R5_41-implementation-lock.json',
    'R5_47-infrastructure-lock-v2.json', 'R5_43-infrastructure-lock.json')}
HISTORICAL_SECURITY = {
    'test_security_r5_47.SecurityTests.test_historical_lock_unchanged',
    'test_security_r5_47.SecurityTests.test_ignore_effective_behavior'}
DOWNSTREAM = ('synthetic-reservation', 'synthetic-dispatch', 'synthetic-completion',
              'post-observation', 'second-dispatch-prevention', 'no-repair-enforcement')


def write(name, value):
    security.persist(OUT / (name + '.json'), value)


def read(name):
    raw = (OUT / (name + '.json')).read_bytes()
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    security.safe_bytes(value)
    return value


def boundary():
    from benchmark.results.phase5c.r5_51_qualification import boundary as previous
    policy = previous()
    policy['scopes']['evaluator'].extend([DRIVER,
        'benchmark/results/phase5c/r5_56_independent_audit.py'])
    policy['scopes']['authority'].extend([
        'benchmark/results/phase5c/R5_53-authority-successor-v1.json',
        'docs/authority-successor-r5.53.md'])
    policy['purpose'] = 'fresh complete qualification; synthetic only; stop on concrete failure'
    policy['checkout_policy'] = authority.REPRESENTATION
    return policy


def capture():
    executable = shutil.which('git')
    version = subprocess.check_output([executable, '--version'], timeout=10).decode().strip()
    tool = tier.dependency('git', version, executable, 'content/index/provenance qualification only')
    return tier.capture(WORK, boundary(), tier.controlled_environment(os.environ, WORK), tools=[tool])


def definitions():
    from benchmark.results.phase5c import r5_51_qualification as old
    stages = old.definitions()
    # Historical physical locks and the V1 fixture lifecycle are not production
    # prerequisites. Authority/frozen pins use the qualified current interface.
    for name in ('synthetic-lifecycle', 'authority-integrity', 'core-count',
                 'implementation-contamination', *['lock-' + n for n in old.LOCKS]):
        stages.pop(name)
    stages.update({
        'identity': ['core'], 'authority': ['qualified-authority'],
        'contamination': ['contamination'], 'workspace': ['workspace'],
        'authority-r553': ['suite', 'benchmark/evaluation', 'test_authority_r5_53.py', False],
        'certificate-v2': ['suite', 'benchmark/evaluation', 'test_certificate_r5_55.py', False]})
    return stages


def mechanism(name, definition):
    return digest(canonical({'driver': digest((WORK / DRIVER).read_bytes()),
                            'definition': definition, 'stage': name}))


def initialize():
    assert OUT.parent.is_dir() and not OUT.exists() and WORK.parent.is_dir() and not WORK.exists()
    historical = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
                  for p in (ROOT / 'benchmark/results').rglob('*') if p.is_file()
                  and '__pycache__' not in p.parts and p.name not in
                  {'r5_56_qualification.py', 'r5_56_independent_audit.py'}}
    # Establish implementation continuity from R5.55's qualified snapshot, not
    # from a filename or a previously successful receipt.
    prior = loads((RESULTS / 'R5_55-qualified-evidence/materialization.json').read_bytes())
    names = ('benchmark/evaluation/qualified_authority_r5_55.py',
             'benchmark/evaluation/certificate_r5_55.py',
             'benchmark/evaluation/tier2_r5_51.py',
             'benchmark/evaluation/test_reproducibility_boundary_r5_50.py')
    continuity = {n: digest((ROOT / n).read_bytes()) for n in names}
    assert all(h == prior['files'][n]['sha256'] for n, h in continuity.items())
    auth_raw = (RESULTS / 'R5_55-qualified-evidence/authorization.json').read_bytes()
    authorization = loads(auth_raw)
    assert digest(canonical(authorization)) == PIN
    assert authorization['authority_identity'] == CURRENT
    manifest = loads((ROOT / authorization['manifest']).read_bytes())
    assert len(manifest['members']) == 1083
    assert digest((ROOT / authorization['manifest']).read_bytes()) == authorization['manifest_sha256']
    material = tier.Workspace.materialize(ROOT, WORK, boundary()['scopes'])
    # Explicit, pre-freeze governed baseline: LF is already a qualified checkout
    # representation. Evolving research prose is selected from pinned authority
    # blobs, never implicitly exempted. Historical lock/evidence bytes stay raw.
    blobs = checkout.blobs(WORK, [r['blob'] for r in manifest['members'].values() if r['blob']])
    changes = {}
    preserved = PRESERVE | set(authorization['historical_evidence'])
    for name, row in manifest['members'].items():
        physical = (WORK / name).read_bytes()
        repository = physical if row['blob'] is None else blobs[row['blob']]
        assert digest(repository) == row['sha256']
        if name in PROSE:
            selected = repository
            reason = 'explicit pinned baseline research prose, before qualification'
        elif name not in preserved and row['kind'] == 'utf8-lf-text':
            assert physical.replace(b'\r\n', b'\n') == repository
            selected = repository
            reason = 'qualified LF checkout representation, before qualification'
        else:
            selected = physical
            reason = 'exact historical/material bytes preserved'
        if physical != selected:
            (WORK / name).write_bytes(selected)
            changes[name] = {'source': digest(physical), 'selected': digest(selected), 'reason': reason}
    OUT.mkdir()
    write('development-disposition', {
        'prior_workspace': 'r556-production-workspace',
        'prior_initialization': 'FAIL before capsule/receipts: driver required uniform CRLF expansion',
        'cause': 'driver assertion stricter than qualified authority_r5_53.materialization',
        'correction': 'use existing exact CRLF-pair relationship, including mixed LF/CRLF',
        'prior_workspace_preserved': True, 'prior_evidence_reused': False,
        'prior_capsule_issued': False, 'prior_certificate_issued': False,
        'prior_reservations': 0, 'prior_dispatches': 0, 'prior_completions': 0})
    write('initial', {'historical': historical, 'implementation_continuity': continuity,
                     'source_git_status': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT).decode(),
                     'b02_exposure': 0, 'b02_reservations': 0, 'b02_dispatches': 0, 'b02_completions': 0})
    write('materialization', material)
    write('pre-freeze-selection', {'changes': changes, 'preserved_physical_inputs': sorted(preserved),
          'source_files_modified': False, 'historical_results_reclassified': False,
          'policy': 'explicit pinned baseline plus qualified LF representation before frozen capture'})
    write('authority-policy', authorization)
    gate_dir = OUT / 'production-gate'
    gate_dir.mkdir()
    marker = tier.Workspace(WORK, gate_dir, EXPERIMENT).enter()
    qualified = authority.qualify(WORK, authorization, trusted_policy_identity=PIN)
    frozen = capture()
    assert frozen == capture() == loads(canonical(frozen))
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    assert contamination()['findings'] == [] and SCHEMA['core_constructs'] == 30
    write('qualified-authority', qualified)
    write('capsule', frozen)
    write('definitions', definitions())
    write('starting-state', {'status': 'PASS', 'authority': qualified['authority'],
        'members': len(qualified['checkout']['members']),
        'checkout_relationships': dict(Counter(r['relationship'] for r in qualified['checkout']['members'].values())),
        'implementation_continuity': continuity, 'workspace': marker,
        'frozen_pins': qualified['frozen_authority'], 'canonical_capsule': True,
        'deterministic_capture': True, 'contamination': 'clean', 'semantic_count': 30,
        'b02_exposure': 0, 'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'synthetic_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'historical_security_assertions': sorted(HISTORICAL_SECURITY),
        'scope': 'all required stages PASS; historical assertions recorded separately; no B02 authority'})
    print({'starting_state': 'PASS', 'members': 1083, 'required_stages': len(definitions()),
           'capsule': frozen['identity']})


def worker(name):
    from benchmark.results.phase5c import r5_51_qualification as old
    definition = definitions()[name]
    kind = definition[0]
    if kind == 'suite':
        from benchmark.results.phase5c.r5_38_review import run_suite
        result = run_suite(*definition[1:])
        result.pop('output')
        # Persist only structured IDs/status, never arbitrary worker diagnostics.
        result['failures'] = [r['test'] for r in result['failures']]
        result['errors'] = [r['test'] for r in result['errors']]
        if name == 'security-r547':
            write('security-full-raw', result)
            observed = set(result['failures']) | set(result['errors'])
            unexpected = observed - HISTORICAL_SECURITY
            result = {**result, 'historical_assertions': sorted(observed & HISTORICAL_SECURITY),
                      'current_security_passed': result['passed'],
                      'successful': not unexpected and result['passed'] == 20,
                      'interpretation': '20 current publication/security witnesses; two preserved superseded host assertions'}
    elif kind == 'qualified-authority':
        qualified = authority.qualify(ROOT, read('authority-policy'), trusted_policy_identity=PIN)
        assert qualified == read('qualified-authority')
        result = {'successful': True, 'qualified_authority': qualified['identity'],
                  'members': len(qualified['checkout']['members'])}
    elif kind == 'workspace':
        result = {'successful': True, **tier.Workspace(ROOT, OUT / 'production-gate', EXPERIMENT).verify()}
    else:
        old.OUTPUT = OUT
        old.worker({'identity': 'core-count', 'contamination': 'implementation-contamination'}.get(name, name))
        result = read({'identity': 'core-count', 'contamination': 'implementation-contamination'}.get(name, name) + '-worker')
        if name == 'contamination':
            result['successful'] = result['findings'] == []
    write(name + '-fresh-worker', result)


def batch():
    assert not (OUT / 'summary.json').exists()
    frozen = read('capsule')
    started = time.monotonic()
    for name, definition in read('definitions').items():
        if (OUT / ('receipt-' + name + '.json')).exists():
            continue
        if time.monotonic() - started > 70:
            break
        assert not (OUT / (name + '-attempt.json')).exists(), 'interrupted stage cannot retry'
        before = capture()
        assert before == frozen
        write(name + '-attempt', {'status': 'INCOMPLETE', 'capsule': frozen['identity']})
        status, result = 'INCOMPLETE', {'successful': False, 'reason': 'bounded worker incomplete'}
        try:
            process = subprocess.run([sys.executable, '-B', '-S', str(WORK / DRIVER), 'worker', name],
                cwd=WORK, env=tier.controlled_environment({**os.environ, 'LYKOI_R551_EVIDENCE': str(OUT)}, WORK),
                capture_output=True, timeout=65)
            if process.returncode == 0:
                result = read(name + '-fresh-worker')
                status = 'PASS' if result['successful'] else 'FAIL'
            else:
                status, result = 'FAIL', {'successful': False, 'reason': 'worker failed; diagnostics withheld'}
        except subprocess.TimeoutExpired:
            pass
        after = capture()
        row = tier.receipt(before, after, EXPERIMENT, name, mechanism(name, definition), status, result)
        write('receipt-' + name, row)
        print({'stage': name, 'status': row['status']}, flush=True)
        if row['status'] != 'PASS':
            write('regression-stop', {'stage': name, 'status': row['status'], 'retry_permitted': False})
            return
    print({'completed': len(list(OUT.glob('receipt-*.json'))), 'required': len(read('definitions'))})


def qualify():
    assert not (OUT / 'summary.json').exists()
    frozen, qualified, authorization, defs = [read(n) for n in
        ('capsule', 'qualified-authority', 'authority-policy', 'definitions')]
    assert capture() == frozen
    evidence = {n: read('receipt-' + n) for n in defs if (OUT / ('receipt-' + n + '.json')).exists()}
    stages = {n: evidence[n]['status'] if n in evidence else 'INCOMPLETE' for n in defs}
    issued, gate_reason = False, None
    classification = 'R5_56_PRODUCTION_REGRESSION_GAP'
    stages.update({'production-certificate': 'INCOMPLETE', 'production-pre-observation': 'INCOMPLETE',
                   **{n: 'INCOMPLETE' for n in DOWNSTREAM}})
    if all(stages[n] == 'PASS' for n in defs):
        policy = {'experiment': EXPERIMENT, 'stages': {n: mechanism(n, d) for n, d in defs.items()},
                  'qualified_authority': qualified['identity'], 'authority_role': frozen['roles']['authority'],
                  'semantic_count': 30, 'canonical_protocol': tier.CANONICAL_PROTOCOL,
                  'recorder': frozen['policy']['recorder'],
                  'observation_state': {'reservations': 0, 'dispatches': 0, 'completions': 0}}
        write('certificate-policy', policy)
        try:
            cert = certificates.certificate(qualified, frozen, evidence, policy, WORK, authorization,
                                           trusted_policy_identity=PIN)
            write('certificate', cert)
            assert cert == loads(canonical(cert)) == certificates.certificate(
                qualified, frozen, evidence, policy, WORK, authorization, trusted_policy_identity=PIN)
            assert certificates.validate(read('certificate'), qualified, frozen, evidence, policy,
                capture(), WORK, authorization, trusted_policy_identity=PIN)
            issued = True
            stages['production-certificate'] = 'PASS'
            write('certificate-verification', {'status': 'PASS', 'canonical_reload': True,
                  'deterministic_assembly': True, 'fresh_validation': True, 'receipts': len(evidence)})
        except ProtocolFailure:
            stages['production-certificate'] = 'FAIL'
            classification = 'R5_56_PRODUCTION_CERTIFICATE_GAP'
        if issued:
            workspace = tier.Workspace(WORK, OUT / 'production-gate', EXPERIMENT)
            # Instantiate the EXISTING qualified observation path, not an ad hoc
            # replacement or a silent monkeypatch of its V1 validator.
            gate = tier.StaticGate(workspace, cert, frozen, evidence, policy, capture,
                {'locks': lambda: {}, 'authority': lambda: qualified['identity'],
                 'contamination': lambda: []})
            try:
                gate.prepare()
            except ProtocolFailure as error:
                gate_reason = str(error)
                stages['production-pre-observation'] = 'FAIL'
                classification = 'R5_56_OBSERVATION_CONTROL_GAP'
                write('production-pre-observation', {'status': 'FAIL', 'reason': gate_reason,
                    'component': 'tier2_r5_51.StaticGate.prepare -> tier2_r5_51.validate -> V1 certificate',
                    'v2_validation_separately_passed': True, 'reservation_permitted': False,
                    'smallest_failure': 'unchanged StaticGate validates V1 policy, not ProductionCertificateV2',
                    'no_repair': True, 'no_dispatch': True})
            else:
                # This driver deliberately supplies no fallback observation path.
                # Unexpected compatibility must be independently established.
                raise ProtocolFailure('unexpected V1/V2 compatibility; stop before dispatch')
    write('terminal-stop', {'classification': classification, 'repair_permitted': False,
          'retry_permitted': False, 'synthetic_reservations': 0, 'synthetic_dispatches': 0,
          'synthetic_completions': 0, 'b02_exposure': 0})
    harness = [r['result'] for n, r in evidence.items() if n.startswith('harness-')]
    write('summary', {'primary_classification': classification, 'stages': stages,
        'required_receipts': len(defs), 'fresh_receipts': len(evidence),
        'restricted_harness': {'discovered': sum(r.get('discovered', 0) for r in harness),
            'passed': sum(r.get('passed', 0) for r in harness),
            'skipped': sum(len(r.get('skipped', [])) for r in harness),
            'failures': sum(len(r.get('failures', [])) for r in harness),
            'errors': sum(len(r.get('errors', [])) for r in harness)},
        'production_certificate_issued': issued, 'production_qualified': False,
        'capsule': frozen['identity'], 'qualified_authority': qualified['identity'],
        'gate_failure': gate_reason, 'synthetic_reservations': 0, 'synthetic_dispatches': 0,
        'synthetic_completions': 0, 'b02_exposure': 0,
        'production_b02_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'core_semantics': 30, 'phase5c': 'paused'})
    print({'classification': classification, 'certificate_issued': issued, 'gate_failure': gate_reason})


if __name__ == '__main__':
    {'initialize': initialize, 'batch': batch, 'worker': lambda: worker(sys.argv[2]),
     'qualify': qualify}[sys.argv[1]]()
