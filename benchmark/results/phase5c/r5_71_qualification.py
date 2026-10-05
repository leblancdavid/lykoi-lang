"""R5.71 execution-only qualification. First FAIL/INCOMPLETE is permanent.

Uses existing qualified mechanisms; no protected subject loader or real grant.
Post-stop audit is read-only diagnosis, never qualification continuation.
"""
import ast
import os
from pathlib import Path
import subprocess
import sys
import time

ENTRY = time.monotonic()
ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import bounded_driver_r5_57 as bounded
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import certificate_r5_68 as modes
from benchmark.evaluation import mediated_child_r5_62 as child
from benchmark.evaluation import observation_consumer_r5_70 as consumer
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import publication_r5_70 as typed
from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, digest, loads

OUT = ROOT / 'benchmark/results/phase5c/R5_71-evidence'
SOURCE = 'benchmark/results/phase5c/r5_71_qualification.py'
EXPERIMENT = 'R5.71-final-existing-infrastructure-production-qualification-v1'
WORK = Path('C:/Users/lblan/AppData/Local/Temp/opencode/r571-production-workspace')
RESOURCES = guard.repository_resources(ROOT)
PROTECTED = {r.path.resolve() for r in RESOURCES}
ATTEMPTS = []
PHASE = 'freeze'


def protect(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        if Path(os.fsdecode(args[0])).resolve() in PROTECTED:
            ATTEMPTS.append('DENIED_BEFORE_CONTENT')
            raise ProtocolFailure('R5_71_PROTOCOL_HALT')


sys.addaudithook(protect)


def ordinary(name):
    path = ROOT / name
    assert path.resolve() not in PROTECTED
    return path.read_bytes()


def context(name):
    return ({'schema': schemas.QUALIFICATION_IDENTITY,
             'schema_identity': schemas.QUALIFICATION_IDENTITY_PIN}
            if name == 'qualification-identity' else {})


def write(name, value):
    publication.persist(OUT / (name + '.json'), value, **context(name))


def read(name):
    raw = ordinary('benchmark/results/phase5c/R5_71-evidence/' + name + '.json')
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    publication.safe_bytes(value, **context(name))
    return value


def historical(round_name, name):
    return loads(ordinary('benchmark/results/phase5c/' + round_name + '-evidence/' + name + '.json'))


def clean():
    from benchmark.results.phase5c.r5_43_qualification import contamination
    return contamination()['findings']


def authority():
    policy = read('authority-policy')
    return sealed.Authority(ROOT, policy, trusted_policy_identity=read('stage-plan')['authority_policy'],
                            observer=sealed.GitMetadata(ROOT))


def freeze():
    assert OUT.parent.is_dir() and not OUT.exists() and WORK.parent.is_dir() and not WORK.exists()
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard',
                                     'benchmark/results'], cwd=ROOT, text=True).splitlines()
    files, metadata = {}, {}
    for name in sorted(set(names) - {SOURCE}):
        path = ROOT / name
        if path.resolve() in PROTECTED:
            stat = path.stat()
            metadata[name] = {'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns}
        else:
            files[name] = digest(ordinary(name))
    OUT.mkdir()
    write('preservation-baseline', {'files': files, 'sealed_metadata_only': metadata})
    inherited = historical('R5_69', 'stage-plan')
    policy = historical('R5_69', 'authority-policy')
    assert len(policy['members']) == 1083
    assert sum(r['classification'] == 'SEALED' for r in policy['members'].values()) == 11
    write('authority-policy', policy)
    closure = sorted(p.relative_to(ROOT).as_posix()
        for directory in ('src', 'benchmark/semantic', 'benchmark/evaluation', 'benchmark/harness', 'tests')
        for p in (ROOT / directory).rglob('*.py')
        if p.resolve() not in PROTECTED and '__pycache__' not in p.parts)
    registry = child.registry(ROOT, {'safe-indexed-regressions': (
        'benchmark.evaluation.safe_workers_r5_62', 'harness', closure)})
    write('worker-registry', registry)
    registry_pin = digest(canonical(registry))
    stages = inherited['regressions']
    for filename, label in (('test_observation_consumer_r5_70.py', 'v3-consumer'),
                            ('test_publication_r5_70.py', 'v3-publication')):
        tree = ast.parse(ordinary('benchmark/evaluation/' + filename))
        ids = [filename[:-3] + '.' + cls.name + '.' + method.name
               for cls in tree.body if isinstance(cls, ast.ClassDef)
               for method in cls.body if isinstance(method, ast.FunctionDef) and method.name.startswith('test_')]
        for offset in range(0, len(ids), 4):
            stages.append({'name': f'{label}-{offset // 4:02d}', 'required': True,
                'definition': ['suite', 'benchmark/evaluation', filename, False, ids[offset:offset + 4]],
                'cost': vars(bounded.production_cost(35)), 'capabilities': sorted(guard.GENERIC)})
    for i, row in enumerate(stages):
        row['dependencies'] = [stages[i - 1]['name']] if i else ['starting-state']
        if row['definition'][0] == 'suite':
            prefix = row['definition'][1].replace('/', '.') + '.'
            row.update(worker_registry=registry_pin,
                worker_identity=child.worker_identity(registry['workers']['safe-indexed-regressions']),
                selection={'identities': [t if t in exclusion.index()['tests'] else prefix + t
                                         for t in row['definition'][4]]},
                worker='safe-indexed-regressions', mediated_policy=child.VERSION,
                exclusion=exclusion.INDEX_PIN, execution_class='mediated safe-indexed worker')
    skips = [t for r in stages if r['name'].startswith('harness-')
             for t in r.get('selection', {}).get('identities', []) if t in exclusion.index()['tests']]
    assert len(skips) == len(set(skips)) == 36
    pins = {n: digest(ordinary(n)) for n in inherited['implementation_sha256']}
    for name in ('observation_consumer_r5_70.py', 'observation_worker_r5_70.py', 'publication_r5_70.py'):
        path = 'benchmark/evaluation/' + name
        pins[path] = digest(ordinary(path))
    preflight = ['mechanism-continuity', 'sealed-members', 'frozen-pins', 'qualified-authority',
                 'tier2-capsule', 'production-declaration-integrity', 'starting-state']
    integration = ['production-certificate', 'cooperative-workspace', 'production-static-gate',
                   'synthetic-production-observation', 'replay-rejection', 'final-independent-audit']
    scopes = {'subject': ['air/task_manager.json'],
        'compiler': sorted(n for n in closure if n.startswith('src/')),
        'semantics': ['schema/axiom-v0.3.schema.json', 'docs/axiom-v0.3.md'],
        'profiles': sorted(n for n in closure if n.startswith('benchmark/semantic/')),
        'authority': ['benchmark/results/phase5c/R5_71-evidence/authority-policy.json',
                      'benchmark/results/phase5c/R5_71-evidence/qualified-authority.json'],
        'evaluator': sorted(n for n in closure if not n.startswith(('src/', 'benchmark/semantic/'))) + [SOURCE]}
    plan = tier.seal({**{k: v for k, v in inherited.items() if k not in ('identity', 'experiment')},
        'experiment': EXPERIMENT, 'regressions': stages,
        'preflight': [{'name': n, 'required': True, 'dependencies': [preflight[i - 1]] if i else []}
                      for i, n in enumerate(preflight)],
        'integration': [{'name': n, 'required': True,
            'dependencies': [integration[i - 1]] if i else [stages[-1]['name']]}
            for i, n in enumerate(integration)],
        'worker_registry': registry_pin, 'implementation_sha256': pins,
        'authority_policy': sealed.identity(policy), 'authority_adapter': sealed.PROTOCOL,
        'production_gate_adapter': 'benchmark.evaluation.observation_consumer_r5_70.StaticGate',
        'certificate_adapter': 'benchmark.evaluation.certificate_r5_68', 'mode': modes.PRODUCTION,
        'capsule_boundary': {'scopes': scopes, 'unknown': [], 'recorder': 'R5.71-canonical-recorder'},
        'publication_policy': {'identity_schema': schemas.QUALIFICATION_IDENTITY_PIN,
            'summary_schema': typed.SUMMARY_PIN, 'source_sha256': digest(ordinary(SOURCE).replace(b'\r\n', b'\n')),
            'typed_source_and_objects': True, 'fixture_nonpublication': True},
        'resources': {r.identity: r.capability for r in RESOURCES},
        'ordinary_verification': 'current permitted worktree read; qualified LF/CRLF representation; no hash replacement',
        'sealed_resource_policy': '11 CLOSED commitment/provenance members; two sealed frozen pins; no content API',
        'workspace_policy': 'R5.66 materialize; ordinary copies and opaque sealed references; no Git database',
        'synthetic_policy': 'fresh existing R5.70 synthetic production fixture; exactly one lifecycle; reject replay',
        'required_metadata_only_skips': skips,
        'driver_identity': digest(ordinary(SOURCE)), 'repair_permitted': False,
        'retry_permitted': False, 'resume_after_failure_permitted': False,
        'coverage': inherited['coverage'] + ['R5.70 consumer and publication integration']})
    write('stage-plan', plan)
    identity = tier.seal({'experiment': EXPERIMENT, 'plan': plan['identity'], 'authority': policy['authority'],
        'authorization': policy['policy_binding'], 'bounded_driver': bounded.VERSION,
        'mediated_worker_policy': child.VERSION, 'registry': registry_pin,
        'exclusion': exclusion.INDEX_PIN, 'resource_policy': guard.POLICY,
        'orchestration': digest(ordinary(SOURCE)), 'fresh_receipts_only': True,
        'state_binding': 'complete current production qualification; closed B02; no repair or retry'},
        **context('qualification-identity'))
    write('qualification-identity', identity)
    assert read('qualification-identity') == identity and read('stage-plan') == plan
    tier.envelopes.unseal(identity)
    write('freeze', {'status': 'PASS', 'plan': plan['identity'], 'qualification': identity['identity'],
        'constructed': True, 'sealed': True, 'persisted': True, 'schema_revalidation': True,
        'canonical_reload': True, 'regression_stages': len(stages), 'preflight_stages': len(preflight),
        'integration_stages': len(integration), 'metadata_only_skip_declarations': len(skips),
        'protected_read_attempts': len(ATTEMPTS)})
    print(read('freeze'))


def continuity():
    plan, identity = read('stage-plan'), read('qualification-identity')
    tier.envelopes.unseal(plan)
    tier.envelopes.unseal(identity)
    assert identity['plan'] == plan['identity'] and identity['orchestration'] == digest(ordinary(SOURCE))
    assert digest(canonical(read('worker-registry'))) == plan['worker_registry'] == identity['registry']
    assert sealed.identity(read('authority-policy')) == plan['authority_policy']
    for name, pin in plan['implementation_sha256'].items():
        assert digest(ordinary(name)) == pin
    old = historical('R5_70', 'summary-completed')
    assert old['classification'] == 'R5_70_V3_OBSERVATION_CONSUMER_QUALIFIED'
    assert old['protected_read_attempts'] == old['protected_content_reads'] == 0
    assert old['b02_accounting'] == [0, 0, 0, 0] and old['b02_opening_accounting'] == [0, 0]
    assert old['actual_observation_authorizations_created'] == 0 and old['core_semantics'] == 30
    for name, pin in historical('R5_70', 'publication-integrity-completed')['source_and_evidence_sha256'].items():
        if name.startswith('benchmark/evaluation/'):
            assert digest(ordinary(name)) == pin
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    assert not clean() and SCHEMA['core_constructs'] == 30 and not ATTEMPTS
    write('mechanism-continuity', {'status': 'PASS', 'inherited': old['classification'],
        'semantic_count': 30, 'contamination': 'clean', 'b02_accounting': [0, 0, 0, 0],
        'b02_opening_accounting': [0, 0], 'protected_read_attempts': 0, 'protected_content_reads': 0,
        'historical_behavioral_receipts_reused': False})


def capture():
    return tier.capture(ROOT, read('stage-plan')['capsule_boundary'], tier.controlled_environment({}, ROOT))


def mechanism(row):
    return digest(canonical({'qualification': read('qualification-identity')['identity'],
        'plan': read('stage-plan')['identity'], 'stage': row, 'driver': digest(ordinary(SOURCE))}))


def certificate_policy():
    capsule = read('capsule')
    return {'experiment': EXPERIMENT,
        'stages': {r['name']: mechanism(r) for r in read('stage-plan')['regressions']},
        'qualified_authority': read('qualified-authority')['identity'],
        'authority_role': capsule['roles']['authority'], 'semantic_count': 30,
        'canonical_protocol': tier.CANONICAL_PROTOCOL, 'recorder': capsule['policy']['recorder'],
        'observation_state': {'reservations': 0, 'dispatches': 0, 'completions': 0}}


def start():
    global PHASE
    assert not (OUT / 'terminal-stop.json').exists()
    PHASE = 'mechanism-continuity'
    continuity()
    adapter = authority()
    PHASE = 'sealed-members'
    rows = {}
    for name, row in adapter.policy['members'].items():
        if row['classification'] == 'SEALED':
            observed = adapter.observer(name, row)
            assert observed == {k: row[k] for k in ('resource', 'sha256', 'blob', 'mode', 'provenance', 'source')}
            rows[row['resource']] = {'commitment': row['sha256'], 'object': row['blob'],
                'provenance': sealed.identity(row['provenance']), 'seal': 'CLOSED', 'current_content_read': False,
                'frozen': row['frozen']}
    assert len(rows) == 11 and not ATTEMPTS
    write('sealed-members', {'status': 'PASS', 'resources': rows, 'content_reads': 0})
    PHASE = 'frozen-pins'
    frozen = {r: v for r, v in rows.items() if v['frozen']}
    assert len(frozen) == 2
    write('frozen-pins', {'status': 'PASS', 'sealed_frozen_pins': frozen, 'content_reads': 0})
    PHASE = 'qualified-authority'
    qualified = adapter.qualify()
    write('qualified-authority', qualified)
    PHASE = 'tier2-capsule'
    capsule = capture()
    assert capsule == capture() == loads(canonical(capsule))
    write('capsule', capsule)
    PHASE = 'production-declaration-integrity'
    policy = certificate_policy()
    write('certificate-policy', policy)
    declaration = {'protocol': modes.DECLARATION_PROTOCOL, 'schema_binding': modes.DECLARATION_SCHEMA_PIN,
        'experiment': EXPERIMENT, 'qualification': read('qualification-identity')['identity'],
        'mode': modes.PRODUCTION, 'scope': modes.SCOPES[modes.PRODUCTION],
        'authority': qualified['authority'], 'qualified_authority': qualified['identity'],
        'resource_policy': qualified['policy_binding'], 'capsule': capsule['identity'],
        'certificate_policy': digest(canonical(policy)), 'allowed_operation': modes.OPERATIONS[modes.PRODUCTION],
        'sealed_policy': 'CLOSED_NO_OPEN_NO_OBSERVATION', 'observation_state': 'ZERO_UNOBSERVED',
        'seal_open_authorized': False}
    publication.persist(OUT / 'production-declaration.json', declaration,
        schema=modes.DECLARATION_SCHEMA, schema_identity=modes.DECLARATION_SCHEMA_PIN)
    write('declaration-pin', {'trusted_declaration_identity': digest(canonical(declaration))})
    assert modes.eligibility(declaration, qualified=qualified, capsule=capsule, policy=policy, **binding())
    write(PHASE, {'status': 'PASS', 'declaration': digest(canonical(declaration)), 'opening_authority': False})
    PHASE = 'starting-state'
    assert not clean() and not ATTEMPTS
    write(PHASE, {'status': 'PASS', 'capsule': capsule['identity'], 'qualified_authority': qualified['identity'],
        'b02_accounting': [0, 0, 0, 0], 'opening_accounting': [0, 0]})
    (OUT / 'batches').mkdir()
    driver().initialize()
    print({'starting-state': 'PASS'})


def binding():
    return dict(trusted_declaration_identity=read('declaration-pin')['trusted_declaration_identity'],
                mode=modes.PRODUCTION, qualification=read('qualification-identity')['identity'])


def control(row):
    definition = row['definition']
    name = row['name']
    if name == 'identity':
        from benchmark.semantic.application_boundary_r5_41 import SCHEMA
        return {'successful': SCHEMA['core_constructs'] == 30, 'semantic_count': SCHEMA['core_constructs'],
                'qualification': read('qualification-identity')['identity']}
    if name == 'authority':
        return {'successful': True, 'qualified_authority': authority().qualify()['identity']}
    if name == 'contamination':
        findings = clean()
        return {'successful': not findings, 'findings': findings}
    if name == 'workspace':
        return {'successful': WORK.parent.is_dir() and not WORK.exists(), 'dedicated': True,
                'policy': 'deferred fresh R5.66 materialization after certificate issuance'}
    if definition == ['publication-integrity']:
        for path in OUT.rglob('*.json'):
            if path.name not in ('qualification-identity.json', 'production-declaration.json'):
                publication.safe_bytes(loads(path.read_bytes()))
        return {'successful': True}
    if definition == ['check', 'diff']:
        return {'successful': subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True).returncode == 0}
    if definition[0] == 'check' and definition[1] in ('validate', 'safety'):
        result = subprocess.run([sys.executable, '-B', '-S', '-m', 'air_compiler.cli', definition[1],
            'air/task_manager.json'], cwd=ROOT, env=tier.controlled_environment({}, ROOT), capture_output=True, timeout=30)
        return {'successful': result.returncode == 0, 'exit': result.returncode}
    # Existing generic coherence and dependency checks, never subject loaders.
    from benchmark.results.phase5c import r5_51_qualification as previous
    if definition == ['check', 'coherence']:
        previous.OUTPUT = OUT
        previous.worker('coherence')
        return read('coherence-worker')
    if definition == ['check', 'dependencies']:
        return previous.dependencies()
    raise ProtocolFailure('unknown frozen control-plane stage')


def driver():
    assert not (OUT / 'terminal-stop.json').exists()
    plan, registry = read('stage-plan'), read('worker-registry')
    stages = {}
    for row in plan['regressions']:
        run = (bounded.qualified_child(ROOT, registry, plan['worker_registry'], row['worker'],
               row['capabilities'], row['selection']) if row['definition'][0] == 'suite'
               else lambda timeout, row=row: control(row))
        stages[row['name']] = {'mechanism': mechanism(row), 'cost': bounded.Cost(**row['cost']),
                              'capabilities': row['capabilities'], 'run': run}
    return bounded.Driver(OUT / 'batches', EXPERIMENT, read('capsule'), read('qualified-authority')['identity'],
        stages, capture, lambda: authority().qualify()['identity'], resources=RESOURCES)


def batch():
    global PHASE
    PHASE = 'regression-batch'
    result = driver().batch(110, started=ENTRY)
    print({'disposition': result['disposition'], 'receipts': len(result['receipts']), 'next': result['next']})
    if result['disposition'] == 'STOPPED':
        PHASE = next(reversed(result['receipts']))
        stop('R5_71_PRODUCTION_REGRESSION_GAP', 'required receipt FAIL or INCOMPLETE')


def finish():
    global PHASE
    evidence, _, _ = driver().validate()
    assert len(evidence) == len(read('stage-plan')['regressions'])
    write('receipts', evidence)
    PHASE = 'production-certificate'
    qualified, capsule, policy = read('qualified-authority'), read('capsule'), read('certificate-policy')
    declaration = loads(ordinary('benchmark/results/phase5c/R5_71-evidence/production-declaration.json'))
    cert = modes.certificate(qualified, capsule, evidence, policy, authority(), declaration, **binding())
    write('certificate', cert)
    assert modes.validate(cert, qualified, capsule, evidence, policy, capture(), authority(), declaration, **binding())
    PHASE = 'cooperative-workspace'
    workspace = sealed.materialize(authority(), WORK, qualified)
    write('workspace', workspace)
    (OUT / 'production-gate').mkdir()
    owned = tier.Workspace(WORK, OUT / 'production-gate', EXPERIMENT)
    owned.enter()
    PHASE = 'production-static-gate'
    registry, plan = read('worker-registry'), read('stage-plan')
    worker = child.Child(ROOT, registry, plan['worker_registry'], 'safe-indexed-regressions', sorted(guard.GENERIC),
                         {'identities': ['benchmark.evaluation.test_ai_independence_r5_49.FreshIndependenceTests.test_core_direct_imports_no_provider_inference']})
    boundary = guard.Boundary(RESOURCES, lambda row: write('quarantine', row))
    gate = consumer.StaticGate(owned, cert, qualified, capsule, evidence, policy, capture, authority(), declaration,
        worker=worker, boundary=boundary, capabilities=sorted(guard.GENERIC), contamination=clean, **binding())
    assert gate.prepare()
    write('static-gate', {'status': 'PASS', 'prepared': True, 'certificate': cert['identity'],
                          'actual_observation_grants': 0, 'accounting': gate.recorder.counts()})
    PHASE = 'synthetic-production-observation'
    from benchmark.evaluation.test_observation_consumer_r5_70 import ConsumerTests
    fixture = ConsumerTests()
    fixture.setUp()
    try:
        assert fixture.gate.prepare() and fixture.sealed.store.reads == 0
        result = fixture.observe()
        assert result['successful'] and fixture.sealed.store.reads == 1
        PHASE = 'replay-rejection'
        rejected = False
        try:
            fixture.observe()
        except ProtocolFailure:
            rejected = True
        assert rejected and fixture.sealed.store.reads == 1
        for name in ('baseline', 'reservation-1', 'observation-1', 'final'):
            write('synthetic-recorder-' + name, loads(fixture.gate.recorder.path(name).read_bytes()))
        for name in ('synthetic-dispatch', 'synthetic-completion'):
            write(name, loads((fixture.workspace.evidence / (name + '.json')).read_bytes()))
        write('synthetic-opening', loads(fixture.sealed.ledger.with_suffix('.result.json').read_bytes()))
        write('synthetic-flow', {'status': 'PASS', 'counts': fixture.gate.recorder.counts(),
                               'openings': 1, 'replay_rejected': True, 'post_verification': True})
    finally:
        fixture.doCleanups()
    PHASE = 'final-independent-audit'
    assert capture() == capsule and authority().qualify() == qualified and not clean() and not ATTEMPTS
    write('qualification-complete', {'status': 'PASS', 'classification': 'R5_71_PRODUCTION_GATE_QUALIFIED'})


def stop(classification, reason, error=None):
    if (OUT / 'terminal-stop.json').exists():
        return
    write('terminal-stop', {'classification': classification, 'failed_stage': PHASE,
        'reason': reason, 'error_type': type(error).__name__ if error else None,
        'protected_read_attempts': len(ATTEMPTS), 'protected_content_reads': 0,
        'repair_permitted': False, 'retry_permitted': False, 'resume_permitted': False})
    print(read('terminal-stop'))


if __name__ == '__main__':
    try:
        {'freeze': freeze, 'start': start, 'batch': batch, 'finish': finish}[sys.argv[1]]()
    except Exception as error:
        if OUT.is_dir():
            classification = ('R5_71_PROTOCOL_HALT' if ATTEMPTS else
                'R5_71_AUTHORITY_GAP' if PHASE in ('qualified-authority', 'sealed-members', 'frozen-pins') else
                'R5_71_CAPSULE_GAP' if PHASE == 'tier2-capsule' else
                'R5_71_CERTIFICATE_GAP' if PHASE in ('production-certificate', 'production-declaration-integrity') else
                'R5_71_WORKSPACE_GAP' if PHASE == 'cooperative-workspace' else
                'R5_71_STATIC_GATE_GAP' if PHASE == 'production-static-gate' else
                'R5_71_OBSERVATION_CONTROL_GAP' if PHASE in ('synthetic-production-observation', 'replay-rejection') else
                'R5_71_PROTOCOL_HALT')
            stop(classification, 'existing frozen stage rejected; diagnostics withheld', error)
        raise SystemExit(2) from None
