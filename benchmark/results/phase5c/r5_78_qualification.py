"""R5.78 pre-access gate and health; only public sources, redacted evidence."""
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OUT = ROOT / 'benchmark/results/phase5c/R5_78-evidence'
RULE = ('docs/benchmark-source-packaging-r5-78.md',
        'benchmark/evaluation/source_packaging_r5_78.py',
        'benchmark/evaluation/test_source_packaging_r5_78.py',
        'benchmark/evaluation/benchmark_documents_v1.py',
        'schema/benchmark-document-contract-v1.schema.json',
        'docs/benchmark-document-contract-v1.md',
        'benchmark/results/phase5c/r5_78_qualification.py')


def main():
    r.require(OUT.parent.is_dir() and not OUT.exists(), 'fresh evidence directory required')
    OUT.mkdir()
    guard = r.Boundary(ROOT, [ROOT / 'benchmark/requirements/B03.md',
                            ROOT / 'benchmark/harness/profiles/B03.json',
                            ROOT / 'benchmark/harness/capabilities/B03.json',
                            ROOT / 'benchmark/results/phase5c/R5_75-evidence/opened-static-documents.json'])
    with guard.active():
        frozen = r.seal({'kind': 'GenericSourceTransformationFreeze',
                        'files': {name: r.digest((ROOT / name).read_bytes()) for name in RULE},
                        'B03_access_before_freeze': 0, 'B02_layout_used': False})
        r.persist(OUT / 'transformation-freeze.json', frozen)
        from benchmark.evaluation import test_source_packaging_r5_78 as tests
        from benchmark.evaluation import source_packaging_r5_78 as p
        suite = unittest.defaultTestLoader.loadTestsFromModule(tests)
        result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
        r.persist(OUT / 'packaging-tests.json', r.seal({'tests': result.testsRun,
            'failures': len(result.failures), 'errors': len(result.errors),
            'status': 'PASS' if result.wasSuccessful() else 'FAIL',
            'scope': 'PUBLIC_SYNTHETIC_COMPONENTS_AND_HISTORICAL_REJECTION',
            'freeze': frozen['identity'], 'protected_read_attempts': guard.attempts}))
        r.require(result.wasSuccessful(), 'pre-access qualification failed; diagnostics withheld')
        # The applicable historical source gate is separate from passing rejection tests.
        try:
            p.transform('frozen-request-bundle', tests.public_bundle())
        except p.PackagingError as exc:
            r.require(exc.code == 'UNREPRESENTABLE_SOURCE', 'unexpected public gate failure')
            gate = r.seal({'status': 'FAIL', 'error': exc.record(),
                          'interface': 'frozen-request-bundle', 'witness': 'PUBLIC_B01',
                          'protected_processing': 'NOT_STARTED', 'freeze': frozen['identity']})
        else:
            raise r.Rejected('unexpected public gate success; protocol review required')
        r.persist(OUT / 'pre-B03-gate.json', gate)
        baseline = r.current_state(ROOT)
        state = r.current_state(ROOT, RULE)
        r.persist(OUT / 'state.json', state)
        results = {}
        for stage in r.HEALTH_STAGES:
            row = r.run_health_stage(ROOT, baseline, stage)
            r.require(r.current_state(ROOT, RULE) == state, 'packaging state drift')
            r.persist(OUT / ('health-' + stage + '.json'), r.seal(row))
            results[stage] = row
        health = r.health_record(baseline, results)
        r.persist(OUT / 'health.json', health)
        argv = [sys.executable, '-B', '-S', '-m', 'benchmark.evaluation.test_benchmark_documents_v1']
        process = subprocess.run(argv, cwd=ROOT, env=r.controlled_environment(ROOT),
                                 capture_output=True, timeout=85)
        r.require(process.returncode == 0, 'document tests failed; diagnostics withheld')
        documents = json.loads(process.stdout)
        r.require(documents['status'] == 'PASS' and documents['protected_read_attempts'] == 0,
                  'document test boundary failure')
        r.persist(OUT / 'document-tests.json', r.seal({'argv': argv, **documents}))
        r.require(all(r.digest((ROOT / name).read_bytes()) == sha
                      for name, sha in frozen['files'].items()), 'frozen transformation changed')
        r.require(r.current_state(ROOT, RULE) == state, 'final state drift')
        summary = r.seal({'classification': 'R5_78_B03_PACKAGING_GAP',
            'reason': 'UNREPRESENTABLE_SOURCE', 'phase': 'PRE_B03_SOURCE_INTERFACE_GATE',
            'transformation': frozen['identity'], 'state': state['identity'],
            'health': health['identity'], 'packaging_tests': result.testsRun,
            'document_tests': documents, 'core_semantics': state['semantic_count'],
            'B03_status': ['B03_PRISTINE', 'B03_NOT_EVALUATED', 'B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT'],
            'B02_status': ['B02_EXPOSED_IN_R5_75', 'B02_STATIC_RESULT_INDETERMINATE'],
            'B03_package': 'NOT_CREATED', 'B03_package_identity': None,
            'B03_package_commitment': None, 'B03_provenance': 'NOT_ESTABLISHED',
            'B03_sealed_status': 'NO_V1_PACKAGE', 'B03_runner_eligibility': 'NOT_VERIFIED_NO_PACKAGE',
            'accounting': {name: 0 for name in ('B03_source_reads', 'B03_packaging_attempts',
                'B03_authorizations', 'B03_reservations', 'B03_openings', 'B03_observations',
                'B03_checked_plans', 'B03_readiness', 'B03_audit', 'B03_admission',
                'B03_compatibility', 'B03_whole_contract_evaluations', 'B03_generation',
                'B03_execution', 'B03_acceptance', 'B03_repair')},
            'protected_read_attempts': guard.attempts, 'publication': 'PASS',
            'next': 'INDEPENDENT_SOURCE_REPRESENTATION_AUTHORITY_REQUIRED', 'stopped': True})
        r.persist(OUT / 'summary.json', summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
