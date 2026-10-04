"""Audit collected R5.38 observations without repeating the B02 static pass."""

import collections
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from benchmark.results.phase5c.r5_38_review import verify_lock
from benchmark.semantic.refined_generator_r5_28 import canonical, sha

RESULTS = Path(__file__).resolve().parent


def read(name):
    return json.loads((RESULTS / name).read_bytes())


def audit():
    locked = verify_lock()
    evidence = read('R5_38-nullable-evidence.json')
    matrix = read('R5_38-domain-refinement-matrix.json')
    transferred = read('R5_38-domain-pipeline-evidence.json')
    public = read('R5_38-whole-contract-execution.json')
    verification = read('R5_38-verification.json')
    static = read('R5_38-B02-static-readiness.json')
    assert static['lock_before'] == static['lock_after'] == locked
    assert static['source_sha256'] == sha((RESULTS / 'R5_37-b02-semantic-application.json').read_bytes())
    assert not static['generated'] and not static['executed'] and not static['retry_recommended']
    assert len(static['operations']) == 15 and static['semantic_status'] == 'READY'
    assert all(c['verdict'] == {'provenance_valid': True, 'grounded': True, 'conformant': True}
               for c in [*evidence['calls'].values(), *evidence['mutations'].values()])
    assert all(c['verdict'] == {'provenance_valid': True, 'grounded': True, 'conformant': False}
               for c in evidence['faults'].values())
    assert all(all(c['verdict'].values()) for c in public)
    assert all(s['successful'] and not s['failures'] and not s['errors'] for s in verification['suites'])
    assert all(c['exit'] == 0 for c in verification['commands'])
    assert not any(r['status'] == 'FAILED' for r in transferred)
    counts = dict(collections.Counter(r['status'] for r in transferred))
    audit_path = RESULTS / 'R5_38-redundant-guard-audit.json'
    regression = json.loads(audit_path.read_bytes()) if audit_path.exists() else None
    if regression is not None:
        assert regression['baseline_accepts'] and not regression['current_accepts']
        assert not regression['nullable_redundant_guard']['current_accepts']
        assert regression['lock'] == locked
        assert not regression['generated'] and not regression['b02_analyzed_again']
    optional_modules = ('test_optional_refinement_r5_25', 'test_type_integration_r5_26',
        'test_unified_types_r5_27', 'test_refined_plan_r5_28', 'test_current_pipeline_r5_29',
        'test_current_pipeline_r5_30', 'test_semantic_authority_r5_31')
    harness = verification['suites'][0]
    summary = {'version': 'R5.38', 'lock': locked, 'matrix_rows': len(matrix['rows']),
        'matrix_pipeline_statuses': counts,
        'matrix_grounded_calls': sum(len(r.get('verdicts', [])) for r in transferred),
        'nullable_normal_calls': len(evidence['calls']), 'semantic_mutations': len(evidence['mutations']),
        'grounded_nonconformant_faults': len(evidence['faults']), 'whole_contract_public_calls': len(public),
        'optional_regression': {m: harness['modules'][m] for m in optional_modules},
        'verification': [{k: s[k] for k in ('directory', 'discovered', 'passed', 'skipped', 'seconds')} for s in verification['suites']],
        'b02_static': {k: static[k] for k in ('status', 'semantic_status', 'gaps', 'source_sha256')},
        'core_constructs': 30, 'new_core_constructs': 0,
        'post_lock_regression': regression,
        'gate': 'R5_38_NULLABLE_COHERENCE_PARTIAL' if regression and not regression['current_accepts'] else
                'R5_38_NULLABLE_COHERENCE_AND_READINESS_VALIDATED'}
    names = [p for p in RESULTS.glob('R5_38-*.json') if p.name != 'R5_38-summary.json']
    summary['evidence_hashes'] = {p.name: sha(p.read_bytes()) for p in sorted(names)}
    (RESULTS / 'R5_38-summary.json').write_bytes((json.dumps(summary, indent=2) + '\n').encode())
    print(json.dumps({k: summary[k] for k in ('lock', 'matrix_rows', 'matrix_pipeline_statuses',
        'matrix_grounded_calls', 'nullable_normal_calls', 'semantic_mutations',
        'grounded_nonconformant_faults', 'whole_contract_public_calls', 'optional_regression', 'gate')}, indent=2))


if __name__ == '__main__':
    audit()
