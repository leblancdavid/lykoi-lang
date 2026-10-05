"""Fresh execution-only R5.67 candidate; first failed prerequisite is terminal.

No subject loader, real seal opener, adapter override, repair or retry entry.
"""
import ast
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import bounded_driver_r5_57 as bounded
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import mediated_child_r5_62 as child
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.results.phase5c.r5_66_inventory import inventory, POLICY_PIN, AUTHORITY_PIN

OUT = ROOT / 'benchmark/results/phase5c/R5_67-evidence'
SOURCE = 'benchmark/results/phase5c/r5_67_qualification.py'
AUDITOR = 'benchmark/results/phase5c/r5_67_independent_audit.py'
EXPERIMENT = 'R5.67-fresh-production-tier2-sealed-authority-v1'
PROTECTED = {r.path.resolve() for r in guard.repository_resources(ROOT)}
ATTEMPTS = []


def protect(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        if Path(os.fsdecode(args[0])).resolve() in PROTECTED:
            ATTEMPTS.append('DENIED_BEFORE_CONTENT')
            raise RuntimeError('R5_67_PROTOCOL_HALT')


sys.addaudithook(protect)


def ordinary(name):
    path = ROOT / name
    assert path.resolve() not in PROTECTED
    return path.read_bytes()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).splitlines()


def context(name):
    return ({'schema': schemas.QUALIFICATION_IDENTITY,
             'schema_identity': schemas.QUALIFICATION_IDENTITY_PIN}
            if name == 'qualification-identity' else {})


def write(name, value):
    publication.persist(OUT / (name + '.json'), value, **context(name))


def read(name):
    raw = ordinary('benchmark/results/phase5c/R5_67-evidence/' + name + '.json')
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    publication.safe_bytes(value, **context(name))
    return value


def freeze():
    assert OUT.parent.is_dir() and not OUT.exists()
    assert not git('diff', '--name-only', '--', 'benchmark/results')
    files, metadata = {}, {}
    for name in sorted(set(git('ls-files', '--cached', '--others', '--exclude-standard',
                               'benchmark/results')) - {SOURCE, AUDITOR}):
        path = ROOT / name
        if path.resolve() in PROTECTED:
            stat = path.stat()
            metadata[name] = {'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns}
        else:
            files[name] = digest(ordinary(name))
    OUT.mkdir()
    write('preservation-baseline', {'files': files, 'sealed_metadata_only': metadata,
        'prospective_sources_excluded_before_capture': [SOURCE, AUDITOR],
        'initial_git_status': 'clean before R5.67 edits'})
    inherited = loads(ordinary('benchmark/results/phase5c/R5_65-evidence/stage-plan.json'))
    safe_inventory = inventory()
    authorization = loads(ordinary('benchmark/results/phase5c/R5_55-qualified-evidence/authorization.json'))
    manifest = loads(ordinary(authorization['manifest']))
    members = {}
    for name, row in manifest['members'].items():
        if name in safe_inventory['members']:
            members[name] = safe_inventory['members'][name]
        else:
            members[name] = {'resource': 'ordinary:' + digest(name.encode()),
                'classification': 'ORDINARY', 'role': 'AUTHORITY_LINKAGE',
                'sha256': row['sha256'], 'blob': row['blob'], 'mode': row['mode'],
                'representation_kind': row['kind'], 'frozen': name in authorization['frozen_authority'],
                'authority': AUTHORITY_PIN, 'policy_binding': POLICY_PIN,
                'provenance': {'historical_head': manifest['head'],
                    'qualification': authorization['qualification_sha256'],
                    'audit': authorization['audit_sha256'], 'successor': AUTHORITY_PIN},
                'source': 'immutable-git-object', 'worktree_content_verified': False,
                'checkout_observation': 'DEFERRED_UNTIL_OPEN'}
    policy = {'authority': AUTHORITY_PIN, 'policy_binding': POLICY_PIN,
              'members': members, 'frozen_authority': authorization['frozen_authority']}
    assert len(members) == 1083 and sum(r['classification'] == 'SEALED' for r in members.values()) == 11
    write('authority-policy', policy)
    closure = sorted(p.relative_to(ROOT).as_posix()
        for directory in ('src', 'benchmark/semantic', 'benchmark/evaluation', 'benchmark/harness', 'tests')
        for p in (ROOT / directory).rglob('*.py')
        if p.resolve() not in PROTECTED and '__pycache__' not in p.parts)
    registry = child.registry(ROOT, {'safe-indexed-regressions': (
        'benchmark.evaluation.safe_workers_r5_62', 'harness', closure)})
    registry_pin = digest(canonical(registry))
    write('worker-registry', registry)
    stages = inherited['regressions']
    filename = 'test_sealed_authority_r5_66.py'
    tree = ast.parse(ordinary('benchmark/evaluation/' + filename))
    ids = [filename[:-3] + '.' + cls.name + '.' + method.name
           for cls in tree.body if isinstance(cls, ast.ClassDef)
           for method in cls.body if isinstance(method, ast.FunctionDef) and method.name.startswith('test_')]
    assert len(ids) == 31
    for offset in range(0, len(ids), 4):
        stages.append({'name': f'sealed-authority-{offset // 4:02d}', 'required': True,
            'definition': ['suite', 'benchmark/evaluation', filename, False, ids[offset:offset + 4]],
            'cost': vars(bounded.production_cost(35)), 'capabilities': sorted(guard.GENERIC)})
    for i, row in enumerate(stages):
        row['dependencies'] = [stages[i - 1]['name']] if i else ['starting-state']
        if row['definition'][0] == 'suite':
            directory, identities = row['definition'][1], row['definition'][4]
            prefix = directory.replace('/', '.') + '.'
            row.update(worker_registry=registry_pin,
                worker_identity=child.worker_identity(registry['workers']['safe-indexed-regressions']),
                selection={'identities': [t if t in exclusion.index()['tests'] else prefix + t for t in identities]},
                worker='safe-indexed-regressions', mediated_policy=child.VERSION,
                exclusion=exclusion.INDEX_PIN, execution_class='R5.62 mediated safe-indexed worker')
    selected = [t for r in stages if r['name'].startswith('harness-')
                for t in r.get('selection', {}).get('identities', []) if t in exclusion.index()['tests']]
    assert len(selected) == len(set(selected)) == 36
    pins = {name: digest(ordinary(name)) for name in inherited['implementation_sha256']}
    for filename in ('sealed_authority_r5_66.py', 'certificate_r5_66.py'):
        name = 'benchmark/evaluation/' + filename
        pins[name] = digest(ordinary(name))
    preflight = ['mechanism-continuity', 'production-certificate-eligibility',
                 'qualified-authority', 'sealed-members', 'frozen-pins', 'tier2-capsule', 'starting-state']
    integration = []
    for name in ('production-certificate', 'cooperative-workspace-linkage',
                 'production-pre-observation', 'synthetic-reservation', 'synthetic-seal-open',
                 'synthetic-dispatch', 'synthetic-completion', 'immediate-post-verification',
                 'second-observation-rejection', 'alternate-ledger-replay-rejection',
                 'historical-preservation', 'publication-security', 'final-independent-audit'):
        integration.append({'name': name, 'required': True,
            'dependencies': [integration[-1]['name']] if integration else [stages[-1]['name']],
            'execution_class': 'unchanged qualified production APIs; synthetic observation authorization only'})
    plan = tier.seal({**{k: v for k, v in inherited.items() if k not in ('identity', 'experiment')},
        'experiment': EXPERIMENT, 'regressions': stages, 'integration': integration,
        'preflight': [{'name': n, 'required': True, 'dependencies': [preflight[i - 1]] if i else []}
                      for i, n in enumerate(preflight)],
        'worker_registry': registry_pin, 'implementation_sha256': pins,
        'authority_policy': sealed.identity(policy), 'sealed_policy': sealed.PROTOCOL,
        'authority_adapter': 'benchmark.evaluation.sealed_authority_r5_66.Authority',
        'certificate_adapter': 'benchmark.evaluation.certificate_r5_66',
        'workspace_adapter': 'benchmark.evaluation.sealed_authority_r5_66.materialize',
        'workspace_policy': 'ordinary copies; 11 opaque references; no Git database or protected bytes',
        'capsule_policy': 'sealed commitments and permitted metadata only; no protected content',
        'observation_policy': 'synthetic authorization only; exactly 1/1/1; B02 closed; reject second and alternate ledger',
        'coverage': inherited['coverage'] + ['R5.66 sealed authority, frozen pins, deferred workspace and opening'],
        'production_experiment_must_not_be_reclassified_as_synthetic': True})
    write('stage-plan', plan)
    identity = tier.seal({'experiment': EXPERIMENT, 'plan': plan['identity'], 'authority': AUTHORITY_PIN,
        'authorization': POLICY_PIN, 'bounded_driver': bounded.VERSION,
        'mediated_worker_policy': child.VERSION, 'registry': registry_pin,
        'exclusion': exclusion.INDEX_PIN, 'resource_policy': guard.POLICY,
        'orchestration': digest(ordinary(SOURCE)), 'fresh_receipts_only': True,
        'state_binding': 'fresh full ordinary/sealed authority and capsule before production receipts'},
        **context('qualification-identity'))
    write('qualification-identity', identity)
    assert read('qualification-identity') == identity and read('stage-plan') == plan
    tier.envelopes.unseal(read('qualification-identity'))
    write('freeze', {'status': 'PASS', 'plan': plan['identity'], 'qualification': identity['identity'],
        'regression_stages': len(stages), 'preflight_stages': len(preflight),
        'integration_stages': len(integration), 'constructed': True, 'sealed': True,
        'persisted': True, 'schema_revalidation': True, 'canonical_reload': True,
        'prohibited_metadata_skips': 36, 'protected_read_attempts': len(ATTEMPTS)})
    print({'freeze': 'PASS', 'regression_stages': len(stages), 'qualification': identity['identity']})


def start():
    assert not (OUT / 'terminal-stop.json').exists()
    plan, identity = read('stage-plan'), read('qualification-identity')
    tier.envelopes.unseal(plan)
    tier.envelopes.unseal(identity)
    assert identity['plan'] == plan['identity'] and identity['orchestration'] == digest(ordinary(SOURCE))
    assert digest(canonical(read('worker-registry'))) == identity['registry'] == plan['worker_registry']
    assert sealed.identity(read('authority-policy')) == plan['authority_policy']
    for name, pin in plan['implementation_sha256'].items():
        assert digest(ordinary(name)) == pin
    inherited = loads(ordinary('benchmark/results/phase5c/R5_66-evidence/summary-final-mechanism.json'))
    assert inherited['classification'] == 'R5_66_SEALED_AUTHORITY_QUALIFIED'
    assert inherited['core_semantics'] == 30 and inherited['b02_accounting'] == [0, 0, 0, 0]
    qualified_pins = loads(ordinary('benchmark/results/phase5c/R5_66-evidence/publication-integrity.json'))
    for name, pin in qualified_pins['source_and_evidence_sha256'].items():
        if name.startswith('benchmark/evaluation/'):
            assert digest(ordinary(name)) == pin
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    from benchmark.results.phase5c.r5_43_qualification import contamination
    clean = contamination()
    assert SCHEMA['core_constructs'] == 30 and not clean['findings'] and not ATTEMPTS
    write('mechanism-continuity', {'status': 'PASS', 'inherited': inherited['classification'],
        'implementation_sha256': plan['implementation_sha256'], 'contamination': clean,
        'semantic_count': 30, 'b02_read_attempts': 0, 'b02_content_reads': 0,
        'scope': 'implementation pins and metadata prerequisites; no behavioral receipt reuse'})
    # Evaluate the exact immutable eligibility predicate, without calling any
    # content-reading legacy qualifier or creating pretend production receipts.
    filename = 'benchmark/evaluation/certificate_r5_66.py'
    tree = ast.parse(ordinary(filename))
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'certificate')
    predicate = next(n for n in ast.walk(function) if isinstance(n, ast.UnaryOp)
        and ast.unparse(n) == "not policy['experiment'].startswith('synthetic:')")
    blocked = eval(compile(ast.Expression(predicate), filename, 'eval'),
                   {'__builtins__': {}}, {'policy': {'experiment': EXPERIMENT}})
    assert blocked is True
    assert any(isinstance(n, ast.Constant) and n.value == 'SYNTHETIC_ONLY' for n in ast.walk(function))
    failure = {'status': 'FAIL', 'stage': 'production-certificate-eligibility',
        'component': filename, 'implementation_sha256': plan['implementation_sha256'][filename],
        'predicate': ast.unparse(predicate), 'production_experiment': EXPERIMENT,
        'predicate_result': blocked, 'issuance_scope': 'SYNTHETIC_ONLY',
        'reason': 'qualified sealed-evidence CertificateV2 adapter rejects production experiment identity',
        'verification': 'exact eligibility predicate evaluated from pinned adapter AST',
        'certificate_assembly_invoked': False, 'legacy_authority_invoked': False,
        'protected_read_attempts': len(ATTEMPTS), 'protected_content_reads': 0}
    write('starting-state-failure', failure)
    classification = 'R5_67_PRODUCTION_CERTIFICATE_GAP'
    write('terminal-stop', {'classification': classification, 'failed_stage': failure['stage'],
        'repair_permitted': False, 'retry_permitted': False, 'resume_permitted': False})
    states = {r['name']: 'NOT_RUN' for r in plan['preflight'] + plan['regressions'] + plan['integration']}
    states.update({'mechanism-continuity': 'PASS', failure['stage']: 'FAIL'})
    write('summary', {'classification': classification, 'failed_stage': failure['stage'],
        'plan': plan['identity'], 'qualification': identity['identity'], 'stages': states,
        'starting_state': 'FAIL', 'production_gate_qualified': False,
        'production_batches': 0, 'production_receipts': 0, 'production_certificates': 0,
        'fresh_qualified_authority': 'NOT_RUN', 'sealed_member_verification': 'NOT_RUN',
        'frozen_pin_verification': 'NOT_RUN', 'capsule': 'NOT_RUN', 'workspace': 'NOT_RUN',
        'synthetic_accounting': [0, 0, 0], 'b02_accounting': [0, 0, 0, 0],
        'b02_read_attempts': len(ATTEMPTS), 'b02_content_reads': 0, 'core_semantics': 30,
        'contamination': 'clean', 'historical_receipts_reused': 0,
        'repair_occurred': False, 'retry_occurred': False, 'resume_occurred': False,
        'production_final_audit': 'NOT_RUN', 'ai_independence_regressions': 'NOT_RUN', 'phase5c': 'paused'})
    print({'classification': classification, 'failed_stage': failure['stage'], 'b02_content_reads': 0})


if __name__ == '__main__':
    try:
        {'freeze': freeze, 'start': start}[sys.argv[1]]()
    except Exception as error:
        if OUT.is_dir() and not (OUT / 'terminal-stop.json').exists():
            write('terminal-stop', {'classification': 'R5_67_PROTOCOL_HALT',
                'invocation': sys.argv[1], 'error_type': type(error).__name__, 'diagnostics': 'withheld',
                'protected_read_attempts': len(ATTEMPTS), 'protected_content_reads': 0,
                'repair_permitted': False, 'retry_permitted': False, 'resume_permitted': False})
        raise SystemExit('R5_67_PROTOCOL_HALT: stopped; diagnostics withheld') from None
