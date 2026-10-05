"""Independent read-only audit of the terminal R5.63 prerequisite result.

This audit does not call the failed qualifier, run pending stages, or promote
the stopped candidate. Sealed preservation is metadata/Git continuity only.
"""

import ast
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.evaluation.preexposure_r5_45 import unseal

OUT = ROOT / 'benchmark/results/phase5c/R5_63-evidence'


def read(name):
    raw = (OUT / (name + '.json')).read_bytes()
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    publication.safe_bytes(value)
    return value


def audit():
    summary, failure = read('summary'), read('starting-state-failure')
    plan, identity, frozen = read('stage-plan'), read('qualification-identity'), read('freeze')
    unseal(plan)
    unseal(identity)
    assert plan['identity'] == identity['plan'] == frozen['plan'] == summary['plan']
    assert identity['identity'] == frozen['qualification'] == summary['qualification']
    assert digest(canonical(read('worker-registry'))) == identity['registry'] == plan['worker_registry']
    assert digest((ROOT / 'benchmark/results/phase5c/r5_63_qualification.py').read_bytes()) == identity['orchestration']
    resources = {r.path.relative_to(ROOT).as_posix() for r in guard.repository_resources(ROOT)}
    authorization = loads((ROOT / 'benchmark/results/phase5c/R5_55-qualified-evidence/authorization.json').read_bytes())
    assert digest(canonical(authorization)) == identity['authorization']
    manifest = loads((ROOT / authorization['manifest']).read_bytes())
    assert len(manifest['members']) == failure['manifest_members'] == 1083
    assert digest(canonical({k: v for k, v in manifest.items() if k != 'identity'})) == manifest['identity'] == identity['authority']
    assert sorted(resources & set(manifest['members'])) == failure['protected_required_members']
    assert sorted(resources & set(authorization['frozen_authority'])) == failure['protected_frozen_pins']
    # Independently inspect the AST of current code for mandatory bulk reads.
    qpath = 'benchmark/evaluation/qualified_authority_r5_55.py'
    spath = 'benchmark/evaluation/authority_r5_53.py'
    qtree = ast.parse((ROOT / qpath).read_bytes())
    stree = ast.parse((ROOT / spath).read_bytes())
    qualify = next(n for n in qtree.body if isinstance(n, ast.FunctionDef) and n.name == 'qualify')
    verify = next(n for n in stree.body if isinstance(n, ast.FunctionDef) and n.name == 'verify')
    qcalls = [ast.unparse(n.func) for n in ast.walk(qualify) if isinstance(n, ast.Call)]
    vcalls = [ast.unparse(n.func) for n in ast.walk(verify) if isinstance(n, ast.Call)]
    assert 'checkout.blobs' in qcalls and 'successor.verify' in qcalls
    assert 'member_path(root, name).read_bytes' in vcalls
    for name, pin in failure['source_sha256'].items():
        assert name not in resources and digest((ROOT / name).read_bytes()) == pin
    baseline = read('preservation-baseline')
    for name, pin in baseline['files'].items():
        assert name not in resources and digest((ROOT / name).read_bytes()) == pin
    for name, row in baseline['sealed_metadata_only'].items():
        assert name in resources
        info = (ROOT / name).stat()
        assert row == {'size': info.st_size, 'mtime_ns': info.st_mtime_ns}
    changed = subprocess.check_output(['git', 'diff', '--name-only', '--', 'benchmark/results'],
                                     cwd=ROOT, text=True).splitlines()
    assert changed == []
    for round_, expected, field in ((60, 'R5_60_PROTOCOL_HALT', 'primary_classification'),
                                    (61, 'R5_61_PROTECTED_RESOURCE_GAP', 'classification'),
                                    (62, 'R5_62_MEDIATED_CHILD_EXECUTION_QUALIFIED', 'classification')):
        row = loads((OUT.parent / f'R5_{round_}-evidence/summary.json').read_bytes())
        assert row[field] == expected
    prohibited = exclusion.index()['tests']
    ids = [i for s in plan['regressions'] if s['name'].startswith('harness-')
           for i in s.get('selection', {}).get('identities', []) if i in prohibited]
    assert len(ids) == len(set(ids)) == len(prohibited) == 36
    assert summary['classification'] == 'R5_63_QUALIFIED_AUTHORITY_GAP'
    assert summary['production_batches'] == summary['production_receipts'] == 0
    assert not list(OUT.rglob('receipt-*.json')) and not (OUT / 'batches').exists()
    assert not (OUT / 'certificate.json').exists() and not (OUT / 'capsule.json').exists()
    assert summary['synthetic_accounting'] == {'reservations': 0, 'dispatches': 0, 'completions': 0}
    assert summary['b02_accounting'] == {'exposure': 0, 'reservations': 0, 'dispatches': 0, 'completions': 0}
    assert failure['qualifier_invoked'] is failure['materializer_invoked'] is False
    assert failure['protected_read_attempts'] == 0
    assert summary['repair_occurred'] is summary['retry_occurred'] is False
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    from benchmark.results.phase5c.r5_43_qualification import contamination
    assert SCHEMA['core_constructs'] == summary['core_semantics'] == 30
    assert contamination()['findings'] == []
    evidence = {}
    for path in OUT.glob('*.json'):
        read(path.stem)
        evidence[path.name] = digest(path.read_bytes())
    publication.persist(OUT / 'independent-stopped-audit.json', {
        'status': 'PASS', 'scope': 'terminal prerequisite diagnosis and stopped-candidate integrity only',
        'production_final_audit': 'NOT_RUN', 'qualification_promoted': False,
        'manifest_metadata_identity': 'PASS', 'mandatory_bulk_read_ast': 'PASS',
        'fresh_authority': 'NOT_ISSUED', 'capsule': 'NOT_ISSUED', 'certificate': 'NOT_ISSUED',
        'receipt_set': 'EMPTY', 'cross_batch_linkage': 'NOT_RUN', 'mediated_execution': 'NOT_RUN',
        'workspace': 'NOT_MATERIALIZED', 'observation_pre_post': 'NOT_RUN',
        'exclusion_pin': exclusion.INDEX_PIN, 'prohibited_metadata_ids': 36,
        'fresh_child_skip_execution': 'NOT_RUN', 'plan_unchanged': True,
        'historical_unsealed_byte_digests_verified': len(baseline['files']),
        'sealed_result_metadata_verified': len(baseline['sealed_metadata_only']),
        'historical_results_diff': changed, 'historical_classifications_preserved': True,
        'canonical_publication_integrity': 'PASS', 'evidence_sha256': evidence,
        'contamination': 'clean', 'core_semantics': 30, 'b02_accounting': summary['b02_accounting'],
        'synthetic_accounting': summary['synthetic_accounting'], 'no_repair_or_resume': True})
    print({'independent_stopped_audit': 'PASS', 'historical_unsealed': len(baseline['files']),
           'sealed_metadata_only': len(baseline['sealed_metadata_only'])})


def publication_check():
    assert (OUT / 'independent-stopped-audit.json').exists()
    names = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--modified'],
                                   cwd=ROOT, text=True).splitlines()
    pins, dispositions = {}, {}
    for name in sorted(set(names)):
        path = ROOT / name
        if path.suffix in ('.py', '.md', '.json'):
            raw = path.read_bytes()
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
        'scope': 'new stopped-run artifacts and documentation', 'source_sha256': pins,
        'source_dispositions': dispositions, 'git_diff_check': 'PASS',
        'new_file_whitespace_check': 'PASS', 'production_security_regressions': 'NOT_RUN',
        'ai_independence_regressions': 'NOT_RUN', 'b02_exposure': 0})
    print({'publication_integrity': 'PASS', 'git_diff_check': 'PASS'})


if __name__ == '__main__':
    {'audit': audit, 'publication': publication_check}[sys.argv[1]]()
