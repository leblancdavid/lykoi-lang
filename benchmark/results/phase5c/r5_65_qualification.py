"""Fresh R5.65 plan/identity and prerequisite verification; no B02 loader.

Existing mandatory read sets are checked before invoking production APIs.
A failed prerequisite is terminal; no repair, retry or continuation entry exists.
"""

import ast
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
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

RESULTS = ROOT / 'benchmark/results/phase5c'
OUT = RESULTS / 'R5_65-evidence'
SOURCE = 'benchmark/results/phase5c/r5_65_qualification.py'
EXPERIMENT = 'R5.65-fresh-production-gate-qualification-v1'
AUTHORIZATION_PIN = '31d4b3632cfcdbf1e928ddf3cbeaf2b88fad97e50ba502b78cf1434d09a114b8'
AUTHORITY = '5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea'
MECHANISMS = (
    'qualified_authority_r5_55.py', 'authority_r5_53.py', 'certificate_r5_55.py',
    'tier2_r5_51.py', 'bounded_driver_r5_57.py', 'continuity_r5_59.py',
    'publication_r5_59.py', 'security_r5_47.py', 'publication_schema_r5_64.py',
    'capability_guard_r5_61.py', 'mediated_child_r5_62.py', 'child_startup_r5_62.py',
    'safe_workers_r5_62.py', 'restricted_harness_r5_61.py')


def protected():
    return {r.path.resolve() for r in guard.repository_resources(ROOT)}


def ordinary(name):
    path = ROOT / name
    assert path.resolve() not in protected()
    return path.read_bytes()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).splitlines()


def write(name, value, *, typed=False):
    context = {'schema': schemas.QUALIFICATION_IDENTITY,
               'schema_identity': schemas.QUALIFICATION_IDENTITY_PIN} if typed else {}
    publication.persist(OUT / (name + '.json'), value, **context)


def read(name, *, typed=False):
    raw = ordinary(f'benchmark/results/phase5c/R5_65-evidence/{name}.json')
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    context = {'schema': schemas.QUALIFICATION_IDENTITY,
               'schema_identity': schemas.QUALIFICATION_IDENTITY_PIN} if typed else {}
    publication.safe_bytes(value, **context)
    return value


def freeze():
    assert OUT.parent.is_dir() and not OUT.exists()
    assert not git('diff', '--name-only', '--', 'benchmark/results')
    prospective = {SOURCE, 'benchmark/results/phase5c/r5_65_independent_audit.py'}
    historical, sealed = {}, {}
    for name in sorted(set(git('ls-files', '--cached', '--others', '--exclude-standard',
                               'benchmark/results')) - prospective):
        path = ROOT / name
        if path.resolve() in protected():
            info = path.stat()
            sealed[name] = {'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
        else:
            historical[name] = digest(ordinary(name))
    OUT.mkdir()
    write('preservation-baseline', {'files': historical, 'sealed_metadata_only': sealed,
        'prospective_sources_excluded_before_capture': sorted(prospective),
        'initial_git_status': 'clean before R5.65 edits', 'protected_content_read': False})
    # Membership metadata is inherited; no historical receipt is reused.
    old = loads(ordinary('benchmark/results/phase5c/R5_63-evidence/stage-plan.json'))
    closure = sorted({p.relative_to(ROOT).as_posix()
        for directory in ('src', 'benchmark/semantic', 'benchmark/evaluation',
                          'benchmark/harness', 'tests')
        for p in (ROOT / directory).rglob('*.py')
        if p.resolve() not in protected() and '__pycache__' not in p.parts})
    registry = child.registry(ROOT, {'safe-indexed-regressions': (
        'benchmark.evaluation.safe_workers_r5_62', 'harness', closure)})
    registry_pin = digest(canonical(registry))
    write('worker-registry', registry)
    definitions = [(r['name'], r['definition']) for r in old['regressions']]
    filename = 'test_publication_r5_64.py'
    tree = ast.parse(ordinary('benchmark/evaluation/' + filename))
    ids = [filename[:-3] + '.' + cls.name + '.' + method.name
           for cls in tree.body if isinstance(cls, ast.ClassDef)
           for method in cls.body if isinstance(method, ast.FunctionDef)
           and method.name.startswith('test_')]
    assert len(ids) == 19
    for offset in range(0, len(ids), 4):
        definitions.append((f'context-publication-{offset // 4:02d}',
            ['suite', 'benchmark/evaluation', filename, False, ids[offset:offset + 4]]))
    stages = []
    for name, definition in definitions:
        row = {'name': name, 'definition': definition, 'required': True,
            'dependencies': [stages[-1]['name']] if stages else ['starting-state'],
            'capabilities': sorted(guard.GENERIC), 'cost': vars(bounded.production_cost(35))}
        if definition[0] == 'suite':
            _, directory, pattern, restricted, identities = definition
            prefix = directory.replace('/', '.') + '.'
            selected = [i if i in exclusion.index()['tests'] else prefix + i for i in identities]
            row.update(execution_class='R5.62 qualified_child / safe_workers.harness',
                worker='safe-indexed-regressions', worker_identity=child.worker_identity(
                    registry['workers']['safe-indexed-regressions']),
                worker_registry=registry_pin, selection={'identities': selected},
                exclusion=exclusion.INDEX_PIN, mediated_policy=child.VERSION)
        else:
            row['execution_class'] = 'existing qualified control-plane API; mediated child/SUT only'
        stages.append(row)
    prohibited = exclusion.index()['tests']
    selected = [i for row in stages if row['name'].startswith('harness-')
                for i in row.get('selection', {}).get('identities', []) if i in prohibited]
    assert len(selected) == len(set(selected)) == 36
    pins = {'benchmark/evaluation/' + n: digest(ordinary('benchmark/evaluation/' + n))
            for n in MECHANISMS}
    preflight = ['mechanism-continuity', 'sealed-resource-compatibility', 'qualified-authority',
                 'tier2-capsule', 'starting-state']
    integration = old['integration']
    integration[0]['dependencies'] = [stages[-1]['name']]
    plan = tier.seal({'experiment': EXPERIMENT, 'regressions': stages,
        'preflight': [{'name': n, 'required': True,
                      'dependencies': [preflight[i - 1]] if i else []}
                     for i, n in enumerate(preflight)],
        'integration': integration, 'budget_seconds': 110, 'boundary_reserve': 5,
        'bounded_driver': bounded.VERSION, 'mediated_policy': child.VERSION,
        'resource_policy': guard.POLICY, 'resource_binding': guard.Boundary(
            guard.repository_resources(ROOT), lambda event: None).identity(),
        'exclusion_policy': exclusion.INDEX_PIN, 'worker_registry': registry_pin,
        'publication_schema': schemas.QUALIFICATION_IDENTITY_PIN, 'implementation_sha256': pins,
        'core_semantics': 30, 'b02_authorized': False, 'protected_skips': 36,
        'coverage': old['coverage'] + ['R5.64 context-aware publication'],
        'stage_granularity': 'inherited bounded method groups; R5.64 at most four methods',
        'cost_basis': 'existing production_cost(35), full lifecycle plus qualified margin',
        'batch_rules': ['validate identity/plan/authority/state/prior fresh receipts',
            'full-lifecycle admission', 'persist receipts', 'clean budget PENDING continues',
            'FAIL or INCOMPLETE terminal; no repair/retry/resume'],
        'integration_rules': ['fresh deterministic canonical CertificateV2 after all required PASS',
            'materialize cooperative workspace and verify linkage',
            'production gate using synthetic non-B02 authorization',
            'exactly one reservation/dispatch/completion', 'immediate unchanged-state post-verification',
            'reject protocol-equivalent second observation without reset',
            'independent final audit; B02 0/0/0/0; semantic count 30'],
        'ai_independence': 'development AI/provider/model/credential state excluded from execution identity',
        'policy': 'immutable; no result-driven edits; fresh receipts only; terminal failure',
        'synthetic_observation_only': True})
    write('stage-plan', plan)
    context = {'schema': schemas.QUALIFICATION_IDENTITY,
               'schema_identity': schemas.QUALIFICATION_IDENTITY_PIN}
    identity = tier.seal({'experiment': EXPERIMENT, 'plan': plan['identity'],
        'authority': AUTHORITY, 'authorization': AUTHORIZATION_PIN, 'bounded_driver': bounded.VERSION,
        'mediated_worker_policy': child.VERSION, 'registry': registry_pin,
        'exclusion': exclusion.INDEX_PIN, 'resource_policy': guard.POLICY,
        'orchestration': digest(ordinary(SOURCE)), 'fresh_receipts_only': True,
        'state_binding': 'fresh qualified authority/capsule required before driver initialization'}, **context)
    write('qualification-identity', identity, typed=True)
    assert read('qualification-identity', typed=True) == identity
    tier.envelopes.unseal(read('qualification-identity', typed=True))
    assert read('stage-plan') == plan
    write('freeze', {'status': 'PASS', 'plan': plan['identity'], 'qualification': identity['identity'],
        'schema': schemas.QUALIFICATION_IDENTITY_PIN, 'regression_stages': len(stages),
        'preflight_stages': len(preflight), 'integration_stages': len(integration),
        'constructed': True, 'sealed': True, 'persisted': True, 'schema_revalidation': True,
        'canonical_reload': True, 'authorization_field_retained': True,
        'production_execution_started': False, 'metadata_only_prohibited_ids': 36})
    print({'freeze': 'PASS', 'regression_stages': len(stages), 'qualification': identity['identity']})


def start():
    assert not (OUT / 'terminal-stop.json').exists()
    plan, identity = read('stage-plan'), read('qualification-identity', typed=True)
    tier.envelopes.unseal(plan)
    tier.envelopes.unseal(identity)
    assert identity['plan'] == plan['identity'] and identity['orchestration'] == digest(ordinary(SOURCE))
    assert digest(canonical(read('worker-registry'))) == plan['worker_registry'] == identity['registry']
    for name, pin in plan['implementation_sha256'].items():
        assert digest(ordinary(name)) == pin
    prior = loads(ordinary('benchmark/results/phase5c/R5_64-evidence/summary.json'))
    assert prior['classification'] == 'R5_64_CONTEXT_AWARE_PUBLICATION_QUALIFIED'
    assert prior['b02_accounting'] == [0, 0, 0, 0] and prior['core_semantics'] == 30
    qualified_pins = loads(ordinary('benchmark/results/phase5c/R5_64-evidence/publication-integrity-checked.json'))
    for name, pin in qualified_pins['source_and_evidence_sha256'].items():
        if name.startswith('benchmark/evaluation/'):
            assert digest(ordinary(name)) == pin
    mediated = loads(ordinary('benchmark/results/phase5c/R5_62-evidence/mediated-child-published.json'))
    for name, pin in mediated['implementation_sha256'].items():
        if name in qualified_pins['source_and_evidence_sha256']:
            pin = qualified_pins['source_and_evidence_sha256'][name]
        raw = ordinary(name)
        assert pin in {digest(raw), digest(raw.replace(b'\r\n', b'\n')),
                       digest(raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))}
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    from benchmark.results.phase5c.r5_43_qualification import contamination
    clean = contamination()
    assert SCHEMA['core_constructs'] == 30 and clean['findings'] == []
    write('mechanism-continuity', {'status': 'PASS', 'implementation_sha256': plan['implementation_sha256'],
        'r564': prior['classification'], 'core_semantics': 30, 'contamination': clean,
        'exclusion': exclusion.accounting(), 'protected_content_read': False,
        'scope': 'implementation continuity and metadata prerequisites; no behavioral receipt reuse'})
    policy = loads(ordinary('benchmark/results/phase5c/R5_55-qualified-evidence/authorization.json'))
    assert digest(canonical(policy)) == identity['authorization'] == AUTHORIZATION_PIN
    manifest = loads(ordinary(policy['manifest']))
    assert manifest['identity'] == AUTHORITY and len(manifest['members']) == 1083
    assert digest(canonical({k: v for k, v in manifest.items() if k != 'identity'})) == AUTHORITY
    resource_names = {r.path.relative_to(ROOT).as_posix() for r in guard.repository_resources(ROOT)}
    intersection = sorted(resource_names & set(manifest['members']))
    frozen = sorted(resource_names & set(policy['frozen_authority']))
    tracked = set(git('ls-files'))
    materialized = sorted(resource_names & tracked)
    assert intersection and frozen and materialized
    q = ordinary('benchmark/evaluation/qualified_authority_r5_55.py').decode()
    s = ordinary('benchmark/evaluation/authority_r5_53.py').decode()
    t = ordinary('benchmark/evaluation/tier2_r5_51.py').decode()
    assert "checkout.blobs(root, [r['blob'] for r in baseline['members'].values() if r['blob']])" in q
    assert 'successor.verify(root, baseline, repository' in q
    assert 'physical = member_path(root, name).read_bytes()' in s
    assert 'names = sorted(set(tracked) | set(scoped))' in t
    assert 'before = {n: regular(source / n) for n in names}' in t
    failure = {'status': 'FAIL', 'stage': 'sealed-resource-compatibility',
        'authority_identity': AUTHORITY, 'manifest_members': 1083,
        'manifest_metadata_identity': 'PASS', 'authorization_identity': AUTHORIZATION_PIN,
        'protected_required_members': intersection, 'protected_frozen_pins': frozen,
        'protected_tracked_materialization_members': materialized,
        'reason': 'mandatory fresh authority and workspace read sets intersect sealed B02 resources',
        'qualifier_invoked': False, 'materializer_invoked': False, 'protected_read_attempts': 0,
        'source_sha256': {n: plan['implementation_sha256'][n] for n in (
            'benchmark/evaluation/qualified_authority_r5_55.py',
            'benchmark/evaluation/authority_r5_53.py', 'benchmark/evaluation/tier2_r5_51.py')}}
    write('starting-state-failure', failure)
    classification = 'R5_65_QUALIFIED_AUTHORITY_GAP'
    write('terminal-stop', {'classification': classification, 'before_first_batch': True,
        'repair_permitted': False, 'retry_permitted': False, 'resume_permitted': False,
        'protected_access_prevented_by_prerequisite': True})
    states = {r['name']: 'NOT_RUN' for r in plan['preflight'] + plan['regressions'] + plan['integration']}
    states.update({'mechanism-continuity': 'PASS', 'sealed-resource-compatibility': 'FAIL'})
    write('summary', {'classification': classification, 'failed_stage': failure['stage'],
        'plan': plan['identity'], 'qualification': identity['identity'], 'stages': states,
        'starting_state': 'FAIL', 'plan_unchanged': True, 'fresh_qualified_authority_issued': False,
        'fresh_capsule_issued': False, 'production_certificate_issued': False,
        'cooperative_workspace_materialized': False, 'production_gate_qualified': False,
        'production_batches': 0, 'production_receipts': 0, 'historical_receipts_reused': 0,
        'synthetic_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'b02_accounting': {'exposure': 0, 'reservations': 0, 'dispatches': 0, 'completions': 0},
        'core_semantics': 30, 'contamination': 'clean', 'phase5c': 'paused',
        'repair_occurred': False, 'retry_occurred': False, 'resume_occurred': False,
        'production_final_audit': 'NOT_RUN', 'ai_independence_regressions': 'NOT_RUN'})
    print({'classification': classification, 'protected_required_members': len(intersection),
           'protected_read_attempts': 0, 'production_batches': 0})


if __name__ == '__main__':
    try:
        {'freeze': freeze, 'start': start}[sys.argv[1]]()
    except Exception as error:
        if OUT.is_dir() and not (OUT / 'terminal-stop.json').exists():
            write('terminal-stop', {'classification': 'R5_65_PROTOCOL_HALT',
                'invocation': sys.argv[1], 'error_type': type(error).__name__,
                'diagnostics': 'withheld', 'repair_permitted': False,
                'retry_permitted': False, 'resume_permitted': False})
        raise SystemExit('R5_65_PROTOCOL_HALT: qualification stopped; diagnostics withheld') from None
