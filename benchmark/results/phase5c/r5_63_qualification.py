"""Fresh R5.63 freeze and starting-state verification; no protected-content API.

The prerequisite check stops before calling an existing API whose mandatory
read set intersects the sealed resource registry. No replacement qualifier,
materializer, certificate or observation implementation is introduced.
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
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

RESULTS = ROOT / 'benchmark/results/phase5c'
OUT = RESULTS / 'R5_63-evidence'
EXPERIMENT = 'R5.63-fresh-complete-production-tier2-qualification-v1'
SOURCE = 'benchmark/results/phase5c/r5_63_qualification.py'
AUTHORITY_PIN = '31d4b3632cfcdbf1e928ddf3cbeaf2b88fad97e50ba502b78cf1434d09a114b8'
AUTHORITY = '5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea'


def write(name, value):
    publication.persist(OUT / (name + '.json'), value)


def read(name):
    return loads((OUT / (name + '.json')).read_bytes())


def sealed_paths():
    return {r.path.resolve() for r in guard.repository_resources(ROOT)}


def ordinary_bytes(path):
    assert path.resolve() not in sealed_paths()
    return path.read_bytes()


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).splitlines()


def freeze():
    assert OUT.parent.is_dir() and not OUT.exists()
    assert not git('diff', '--name-only', '--', 'benchmark/results')
    prospective = {SOURCE, 'benchmark/results/phase5c/r5_63_independent_audit.py'}
    names = git('ls-files', '--cached', '--others', '--exclude-standard', 'benchmark/results')
    historical, sealed = {}, {}
    for name in sorted(set(names) - prospective):
        path = ROOT / name
        if path.resolve() in sealed_paths():
            info = path.stat()
            sealed[name] = {'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
        else:
            historical[name] = digest(ordinary_bytes(path))
    OUT.mkdir()
    write('preservation-baseline', {'files': historical, 'sealed_metadata_only': sealed,
        'prospective_sources_excluded_before_capture': sorted(prospective),
        'initial_git_status': 'clean before R5.63 edits', 'protected_content_read': False})
    # Prior plans supply membership metadata only; no prior receipt supplies PASS.
    old = loads(ordinary_bytes(RESULTS / 'R5_60-evidence/stage-plan.json'))
    prohibited = exclusion.index()['tests']
    safe = 'benchmark.evaluation.safe_workers_r5_62'
    closure = sorted({p.relative_to(ROOT).as_posix()
        for directory in ('src', 'benchmark/semantic', 'benchmark/evaluation',
                          'benchmark/harness', 'tests')
        for p in (ROOT / directory).rglob('*.py')
        if p.resolve() not in sealed_paths() and '__pycache__' not in p.parts})
    registry = child.registry(ROOT, {'safe-indexed-regressions': (safe, 'harness', closure)})
    registry_pin = digest(canonical(registry))
    write('worker-registry', registry)
    stages = []
    def add(name, definition):
        row = {'name': name, 'definition': definition, 'required': True,
            'dependencies': [stages[-1]['name']] if stages else [],
            'capabilities': sorted(guard.GENERIC), 'cost': vars(bounded.production_cost(35))}
        if definition[0] == 'suite':
            _, directory, pattern, restricted, identities = definition
            prefix = directory.replace('/', '.') + '.'
            ids = [i if i in prohibited else prefix + i for i in identities]
            row.update(execution_class='R5.62 qualified_child / safe_workers.harness',
                worker='safe-indexed-regressions', worker_identity=child.worker_identity(
                    registry['workers']['safe-indexed-regressions']),
                worker_registry=registry_pin, selection={'identities': ids},
                exclusion=exclusion.INDEX_PIN, mediated_policy=child.VERSION)
        else:
            row['execution_class'] = 'existing qualified control-plane API; no raw child launch'
        stages.append(row)
    for row in old['regressions']:
        add(row['name'], row['definition'])
    # Current requirements absent from the earlier stopped plan are prospective
    # exact-method metadata, obtained without importing or discovering tests.
    for label, filename in (('qualified-authority-v1', 'test_certificate_r5_55.py'),
                            ('capability-resource-guard', 'test_capability_guard_r5_61.py'),
                            ('mediated-child-sut', 'test_mediated_child_r5_62.py')):
        tree = ast.parse(ordinary_bytes(ROOT / 'benchmark/evaluation' / filename))
        ids = [filename[:-3] + '.' + cls.name + '.' + method.name
               for cls in tree.body if isinstance(cls, ast.ClassDef)
               for method in cls.body if isinstance(method, ast.FunctionDef)
               and method.name.startswith('test_')]
        assert ids
        for offset in range(0, len(ids), 4):
            add(f'{label}-{offset // 4:02d}', ['suite', 'benchmark/evaluation', filename, False,
                                            ids[offset:offset + 4]])
    selected_prohibited = [identity for row in stages if row['name'].startswith('harness-')
                          for identity in row.get('selection', {}).get('identities', [])
                          if identity in prohibited]
    assert len(selected_prohibited) == len(set(selected_prohibited)) == 36
    preflight = ['mechanism-continuity', 'sealed-resource-compatibility', 'qualified-authority',
                 'authority-workspace-materialization', 'tier2-capsule', 'starting-state']
    plan = tier.seal({'experiment': EXPERIMENT, 'regressions': stages,
        'preflight': [{'name': n, 'required': True} for n in preflight],
        'integration': old['integration'], 'budget_seconds': 110, 'boundary_reserve': 5,
        'bounded_driver': bounded.VERSION, 'mediated_policy': child.VERSION,
        'resource_policy': guard.POLICY, 'exclusion_policy': exclusion.INDEX_PIN,
        'worker_registry': registry_pin, 'core_semantics': 30, 'b02_authorized': False,
        'stage_granularity': 'inherited at most eight methods/four certificate methods; new suites four',
        'cost_basis': 'existing production_cost(35); admission forbidden until starting-state verification',
        'policy': 'immutable; no result-driven edits; terminal FAIL/INCOMPLETE; no historical receipt reuse',
        'coverage': ['restricted harness', 'compiler/application', 'R5.41 support', 'recorder/canonical evidence',
            'QualifiedAuthority', 'ProductionCertificateV2', 'security', 'methodology', 'Tier-2',
            'bounded driver', 'continuity', 'publication', 'capability/resource guard', 'mediated child/SUT',
            'AI independence', 'matrix/coherence', 'schema', 'traceability', 'contamination',
            'validation', 'safety', 'authority', 'publication/integrity', 'git diff --check'],
        'synthetic_observation_only': True, 'protected_skips': 36})
    write('stage-plan', plan)
    identity = tier.seal({'experiment': EXPERIMENT, 'plan': plan['identity'],
        'authority': AUTHORITY, 'authorization': AUTHORITY_PIN, 'bounded_driver': bounded.VERSION,
        'mediated_worker_policy': child.VERSION, 'registry': registry_pin,
        'exclusion': exclusion.INDEX_PIN, 'resource_policy': guard.POLICY,
        'orchestration': digest(ordinary_bytes(ROOT / SOURCE)), 'fresh_receipts_only': True,
        'state_binding': 'fresh qualified authority/capsule required before driver initialization'})
    write('qualification-identity', identity)
    write('freeze', {'status': 'PASS', 'plan': plan['identity'], 'qualification': identity['identity'],
        'regression_stages': len(stages), 'integration_stages': len(plan['integration']),
        'preflight_stages': len(preflight), 'metadata_only_prohibited_ids': 36,
        'protected_modules_imported': False, 'production_execution_started': False})
    print({'freeze': 'PASS', 'plan': plan['identity'], 'qualification': identity['identity'],
           'regression_stages': len(stages)})


def start():
    assert not (OUT / 'summary.json').exists()
    plan, identity = read('stage-plan'), read('qualification-identity')
    tier.envelopes.unseal(plan)
    tier.envelopes.unseal(identity)
    assert identity['plan'] == plan['identity']
    assert identity['orchestration'] == digest(ordinary_bytes(ROOT / SOURCE))
    assert digest(canonical(read('worker-registry'))) == identity['registry']
    r562 = loads(ordinary_bytes(RESULTS / 'R5_62-evidence/summary.json'))
    assert r562['classification'] == 'R5_62_MEDIATED_CHILD_EXECUTION_QUALIFIED'
    # Fresh physical/repository-text continuity against the qualified R5.62
    # records, without inspecting any protected blob through Git.
    pins = loads(ordinary_bytes(RESULTS / 'R5_62-evidence/mediated-child-published.json'))['implementation_sha256']
    current = {}
    for name in ('benchmark/evaluation/bounded_driver_r5_57.py',
                 'benchmark/evaluation/capability_guard_r5_61.py',
                 'benchmark/evaluation/mediated_child_r5_62.py',
                 'benchmark/evaluation/child_startup_r5_62.py',
                 'benchmark/evaluation/safe_workers_r5_62.py'):
        raw = ordinary_bytes(ROOT / name)
        assert pins[name] in {digest(raw), digest(raw.replace(b'\r\n', b'\n')),
                             digest(raw.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n'))}
        current[name] = digest(raw)
    prior = loads(ordinary_bytes(RESULTS / 'R5_62-evidence/checks.json'))['continuity']
    for name, row in prior.items():
        raw = ordinary_bytes(ROOT / name)
        assert digest(raw.replace(b'\r\n', b'\n')) == row['continuity_identity']
        current[name] = digest(raw)
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    from benchmark.results.phase5c.r5_43_qualification import contamination
    assert SCHEMA['core_constructs'] == 30
    clean = contamination()
    write('mechanism-continuity', {'status': 'PASS', 'mechanisms': current,
        'core_semantics': 30, 'contamination': clean, 'inherited_r562': r562['classification'],
        'exclusion': exclusion.accounting(), 'receipts_reused': False})
    authorization = loads(ordinary_bytes(RESULTS / 'R5_55-qualified-evidence/authorization.json'))
    assert digest(canonical(authorization)) == AUTHORITY_PIN
    raw = ordinary_bytes(ROOT / authorization['manifest'])
    manifest = loads(raw)
    assert manifest['identity'] == AUTHORITY and len(manifest['members']) == 1083
    assert digest(canonical({k: v for k, v in manifest.items() if k != 'identity'})) == AUTHORITY
    resources = guard.repository_resources(ROOT)
    protected_members = sorted({r.path.relative_to(ROOT).as_posix() for r in resources
        if r.path.relative_to(ROOT).as_posix() in manifest['members']})
    frozen_protected = sorted(set(protected_members) & set(authorization['frozen_authority']))
    assert protected_members and frozen_protected
    # Verify the mandatory call chain from current implementation, not an old
    # failure/receipt. Never call qualify: checkout.blobs would extract protected
    # Git content even before successor.verify opens the physical files.
    qualifier = ordinary_bytes(ROOT / 'benchmark/evaluation/qualified_authority_r5_55.py').decode()
    successor = ordinary_bytes(ROOT / 'benchmark/evaluation/authority_r5_53.py').decode()
    materializer = ordinary_bytes(ROOT / 'benchmark/evaluation/tier2_r5_51.py').decode()
    assert "checkout.blobs(root, [r['blob'] for r in baseline['members'].values() if r['blob']])" in qualifier
    assert 'successor.verify(root, baseline, repository' in qualifier
    assert 'physical = member_path(root, name).read_bytes()' in successor
    assert 'names = sorted(set(tracked) | set(scoped))' in materializer
    assert 'before = {n: regular(source / n) for n in names}' in materializer
    failure = {'status': 'FAIL', 'stage': 'sealed-resource-compatibility',
        'authority_identity': AUTHORITY, 'manifest_members': 1083,
        'authorization_identity': AUTHORITY_PIN, 'manifest_identity_verified': True,
        'protected_required_members': protected_members, 'protected_frozen_pins': frozen_protected,
        'qualifier': 'QualifiedAuthority v1 -> checkout.blobs(all members) -> successor.verify(all physical members)',
        'materializer': 'Workspace.materialize -> regular(all tracked files) -> read_bytes',
        'reason': 'existing mandatory fresh authority/materialization read sets intersect sealed B02 resources',
        'qualifier_invoked': False, 'materializer_invoked': False, 'protected_read_attempts': 0,
        'protected_content_loaded': False, 'repair_permitted': False, 'retry_permitted': False,
        'source_sha256': {n: digest(ordinary_bytes(ROOT / n)) for n in (
            'benchmark/evaluation/qualified_authority_r5_55.py',
            'benchmark/evaluation/authority_r5_53.py', 'benchmark/evaluation/tier2_r5_51.py')}}
    write('starting-state-failure', failure)
    write('terminal-stop', {'classification': 'R5_63_QUALIFIED_AUTHORITY_GAP',
        'before_first_batch': True, 'repair_permitted': False, 'retry_permitted': False,
        'resume_permitted': False, 'protected_access_denied_by_preflight': True})
    states = {s['name']: 'NOT_RUN' for s in plan['regressions'] + plan['integration']}
    states.update({s['name']: 'NOT_RUN' for s in plan['preflight']})
    states.update({'mechanism-continuity': 'PASS', 'sealed-resource-compatibility': 'FAIL'})
    write('summary', {'classification': 'R5_63_QUALIFIED_AUTHORITY_GAP',
        'failed_stage': 'sealed-resource-compatibility', 'stages': states,
        'qualification': identity['identity'], 'plan': plan['identity'], 'plan_unchanged': True,
        'starting_state': 'FAIL', 'fresh_qualified_authority_issued': False,
        'fresh_capsule_issued': False, 'production_certificate_issued': False,
        'cooperative_workspace_materialized': False, 'production_gate_qualified': False,
        'production_batches': 0, 'production_receipts': 0, 'historical_receipts_reused': 0,
        'synthetic_accounting': {'reservations': 0, 'dispatches': 0, 'completions': 0},
        'b02_accounting': {'exposure': 0, 'reservations': 0, 'dispatches': 0, 'completions': 0},
        'core_semantics': 30, 'contamination': 'clean', 'phase5c': 'paused',
        'repair_occurred': False, 'retry_occurred': False,
        'next': 'owner adjudication of mandatory authority/materialization reads versus sealed-B02 prohibition; no B02 authorization'})
    print({'classification': 'R5_63_QUALIFIED_AUTHORITY_GAP', 'production_batches': 0,
           'protected_read_attempts': 0, 'protected_required_members': len(protected_members)})


if __name__ == '__main__':
    {'freeze': freeze, 'start': start}[sys.argv[1]]()
