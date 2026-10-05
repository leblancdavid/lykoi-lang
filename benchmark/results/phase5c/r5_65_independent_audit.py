"""Independent stopped-candidate audit, not continuation or production qualification."""

import ast
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.evaluation.preexposure_r5_45 import unseal

OUT = ROOT / 'benchmark/results/phase5c/R5_65-evidence'
RESOURCES = {r.path.resolve() for r in guard.repository_resources(ROOT)}


def ordinary(path):
    assert path.resolve() not in RESOURCES
    return path.read_bytes()


def read(name):
    raw = ordinary(OUT / (name + '.json'))
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    context = {'schema': schemas.QUALIFICATION_IDENTITY,
               'schema_identity': schemas.QUALIFICATION_IDENTITY_PIN} if name == 'qualification-identity' else {}
    publication.safe_bytes(value, **context)
    return value


def audit():
    summary, failure = read('summary'), read('starting-state-failure')
    plan, identity, frozen = read('stage-plan'), read('qualification-identity'), read('freeze')
    unseal(plan)
    unseal(identity)
    assert plan['identity'] == identity['plan'] == frozen['plan'] == summary['plan']
    assert identity['identity'] == frozen['qualification'] == summary['qualification']
    assert digest(canonical(read('worker-registry'))) == identity['registry'] == plan['worker_registry']
    assert digest(ordinary(ROOT / 'benchmark/results/phase5c/r5_65_qualification.py')) == identity['orchestration']
    for name, pin in plan['implementation_sha256'].items():
        assert digest(ordinary(ROOT / name)) == pin
    policy = loads(ordinary(ROOT / 'benchmark/results/phase5c/R5_55-qualified-evidence/authorization.json'))
    assert digest(canonical(policy)) == identity['authorization']
    manifest = loads(ordinary(ROOT / policy['manifest']))
    assert len(manifest['members']) == failure['manifest_members'] == 1083
    assert digest(canonical({k: v for k, v in manifest.items() if k != 'identity'})) == manifest['identity'] == identity['authority']
    resources = {p.relative_to(ROOT).as_posix() for p in RESOURCES}
    assert sorted(resources & set(manifest['members'])) == failure['protected_required_members']
    assert sorted(resources & set(policy['frozen_authority'])) == failure['protected_frozen_pins']
    # Inspect current AST independently; do not extract any protected Git blob.
    def calls(filename, function, class_name=None):
        tree = ast.parse(ordinary(ROOT / ('benchmark/evaluation/' + filename)))
        nodes = tree.body if class_name is None else next(
            n.body for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name)
        node = next(n for n in nodes if isinstance(n, ast.FunctionDef) and n.name == function)
        return [ast.unparse(n.func) for n in ast.walk(node) if isinstance(n, ast.Call)]
    assert {'checkout.blobs', 'successor.verify'} <= set(calls('qualified_authority_r5_55.py', 'qualify'))
    assert 'member_path(root, name).read_bytes' in calls('authority_r5_53.py', 'verify')
    assert 'regular' in calls('tier2_r5_51.py', 'materialize', 'Workspace')
    assert 'path.read_bytes' in calls('tier2_r5_51.py', 'regular')
    tracked = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
    assert sorted(resources & set(tracked)) == failure['protected_tracked_materialization_members']
    baseline = read('preservation-baseline')
    for name, pin in baseline['files'].items():
        assert digest(ordinary(ROOT / name)) == pin
    for name, row in baseline['sealed_metadata_only'].items():
        assert (ROOT / name).resolve() in RESOURCES
        info = (ROOT / name).stat()
        assert row == {'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
    changed = subprocess.check_output(['git', 'diff', '--name-only', '--', 'benchmark/results'],
                                     cwd=ROOT, text=True).splitlines()
    assert changed == []
    r563 = loads(ordinary(OUT.parent / 'R5_63-evidence/summary.json'))
    r564 = loads(ordinary(OUT.parent / 'R5_64-evidence/summary.json'))
    assert r563['classification'] == 'R5_63_PROTOCOL_HALT'
    assert not (OUT.parent / 'R5_63-evidence/qualification-identity.json').exists()
    assert r564['classification'] == 'R5_64_CONTEXT_AWARE_PUBLICATION_QUALIFIED'
    prohibited = exclusion.index()['tests']
    selected = [i for r in plan['regressions'] if r['name'].startswith('harness-')
                for i in r.get('selection', {}).get('identities', []) if i in prohibited]
    assert len(selected) == len(set(selected)) == len(prohibited) == 36
    assert summary['classification'] == 'R5_65_QUALIFIED_AUTHORITY_GAP'
    assert summary['production_batches'] == summary['production_receipts'] == 0
    assert not list(OUT.rglob('receipt-*.json')) and not (OUT / 'batches').exists()
    assert not (OUT / 'certificate.json').exists() and not (OUT / 'capsule.json').exists()
    assert summary['synthetic_accounting'] == {'reservations': 0, 'dispatches': 0, 'completions': 0}
    assert summary['b02_accounting'] == {'exposure': 0, 'reservations': 0, 'dispatches': 0, 'completions': 0}
    assert failure['qualifier_invoked'] is failure['materializer_invoked'] is False
    assert failure['protected_read_attempts'] == 0
    assert all(summary[n] is False for n in ('repair_occurred', 'retry_occurred', 'resume_occurred'))
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    from benchmark.results.phase5c.r5_43_qualification import contamination
    assert SCHEMA['core_constructs'] == summary['core_semantics'] == 30
    assert contamination()['findings'] == []
    evidence = {}
    for path in OUT.glob('*.json'):
        read(path.stem)
        evidence[path.name] = digest(ordinary(path))
    publication.persist(OUT / 'independent-stopped-audit.json', {
        'status': 'PASS', 'scope': 'terminal prerequisite diagnosis and stopped-candidate integrity',
        'production_final_audit': 'NOT_RUN', 'qualification_promoted': False,
        'manifest_metadata_identity': 'PASS', 'mandatory_bulk_read_ast': 'PASS',
        'qualification_schema_revalidation': 'PASS', 'plan_unchanged': True,
        'fresh_authority': 'NOT_ISSUED', 'capsule': 'NOT_ISSUED', 'certificate': 'NOT_ISSUED',
        'receipt_set': 'EMPTY', 'mediated_execution': 'NOT_RUN', 'workspace': 'NOT_MATERIALIZED',
        'observation_pre_post': 'NOT_RUN', 'second_observation_rejection': 'NOT_RUN',
        'exclusion_pin': exclusion.INDEX_PIN, 'prohibited_metadata_ids': 36,
        'fresh_child_skip_execution': 'NOT_RUN', 'historical_unsealed_byte_digests_verified': len(baseline['files']),
        'sealed_result_metadata_verified': len(baseline['sealed_metadata_only']),
        'historical_results_diff': changed, 'historical_classifications_preserved': True,
        'canonical_publication_integrity': 'PASS', 'evidence_sha256': evidence,
        'contamination': 'clean', 'core_semantics': 30, 'b02_accounting': summary['b02_accounting'],
        'synthetic_accounting': summary['synthetic_accounting'], 'no_repair_or_resume': True,
        'ai_execution_identity_policy': plan['ai_independence'], 'ai_independence_regressions': 'NOT_RUN'})
    print({'independent_stopped_audit': 'PASS', 'historical_unsealed': len(baseline['files']),
           'sealed_metadata_only': len(baseline['sealed_metadata_only'])})


def publication_check():
    assert (OUT / 'independent-stopped-audit.json').exists()
    names = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--modified'],
                                   cwd=ROOT, text=True).splitlines()
    dispositions, pins = {}, {}
    for name in sorted(set(names)):
        path = ROOT / name
        if path.suffix not in ('.py', '.md', '.json'):
            continue
        raw = ordinary(path)
        if path == OUT / 'qualification-identity.json':
            read('qualification-identity')
            dispositions[name] = 'SCHEMA_CLASSIFIED_PUBLICATION'
        else:
            dispositions[name] = publication.check_source(name, raw)
        pins[name] = digest(raw)
        check = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(path)],
                               cwd=ROOT, capture_output=True, timeout=10)
        assert check.returncode in (0, 1) and not check.stdout
    check = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10)
    assert check.returncode == 0
    for path in OUT.glob('*.json'):
        read(path.stem)
    publication.persist(OUT / 'publication-integrity.json', {'status': 'PASS',
        'scope': 'new stopped-candidate artifacts and documentation', 'source_sha256': pins,
        'source_dispositions': dispositions, 'git_diff_check': 'PASS', 'new_file_whitespace_check': 'PASS',
        'production_security_regressions': 'NOT_RUN', 'ai_independence_regressions': 'NOT_RUN',
        'b02_exposure': 0})
    print({'publication_integrity': 'PASS', 'git_diff_check': 'PASS'})


if __name__ == '__main__':
    {'audit': audit, 'publication': publication_check}[sys.argv[1]]()
