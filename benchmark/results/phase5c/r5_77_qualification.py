"""Fresh V1 qualification, public/synthetic inputs only, exclusive evidence writes."""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OUT = ROOT / 'benchmark/results/phase5c/R5_77-evidence'
EXTRA = ('benchmark/evaluation/benchmark_documents_v1.py',
         'benchmark/evaluation/test_benchmark_documents_v1.py',
         'schema/benchmark-document-contract-v1.schema.json',
         'docs/benchmark-document-contract-v1.md',
         'benchmark/results/phase5c/r5_77_qualification.py')


def main():
    r.require(OUT.parent.is_dir() and not OUT.exists(), 'fresh evidence directory required')
    OUT.mkdir()
    guard = r.Boundary(ROOT, [ROOT / 'benchmark/requirements/B03.md',
                            ROOT / 'benchmark/harness/profiles/B03.json',
                            ROOT / 'benchmark/harness/capabilities/B03.json',
                            ROOT / 'benchmark/results/phase5c/R5_75-evidence/opened-static-documents.json'])
    with guard.active():
        baseline = r.current_state(ROOT)
        state = r.current_state(ROOT, EXTRA)
        r.persist(OUT / 'state.json', state)
        results = {}
        for stage in r.HEALTH_STAGES:
            row = r.run_health_stage(ROOT, baseline, stage)
            r.require(r.current_state(ROOT, EXTRA) == state, 'V1 state drift')
            r.persist(OUT / ('health-' + stage + '.json'), r.seal(row))
            results[stage] = row
        argv = [sys.executable, '-B', '-S', '-m', 'benchmark.evaluation.test_benchmark_documents_v1']
        process = subprocess.run(argv, cwd=ROOT, env=r.controlled_environment(ROOT),
                                 capture_output=True, timeout=85)
        r.require(process.returncode == 0, 'document qualification failed; output withheld')
        tests = json.loads(process.stdout)
        r.require(tests['status'] == 'PASS' and tests['protected_read_attempts'] == 0, 'document boundary failure')
        r.persist(OUT / 'document-tests.json', r.seal({'argv': argv, **tests}))
        health = r.health_record(baseline, results)
        r.persist(OUT / 'health.json', health)
        from benchmark.evaluation.test_benchmark_documents_v1 import fixture, metadata, lifecycle
        from benchmark.evaluation import benchmark_documents_v1 as d
        incomplete = fixture()
        del incomplete['payload']['obligations']
        cases = {
            'supported': {'opaque-1': d.canonical(fixture()), 'opaque-2': d.canonical(metadata())},
            'unsupported': {'opaque-1': d.canonical(fixture(True))},
            'malformed': {'opaque-1': b'{invalid'},
            'incomplete': {'opaque-1': d.canonical(incomplete)},
            'public-seed-bank': {'opaque-1': d.canonical(fixture(real=True))}}
        outcomes = {}
        for name, contents in cases.items():
            ledger = OUT / (name + '-ledger')
            ledger.mkdir()
            row = lifecycle(ledger, contents, baseline, health, lambda: r.current_state(ROOT))
            r.require(row['post_check']['status'] == 'PASS' and row['events'] == list(r.TRANSITIONS), 'lifecycle failure')
            r.require(r.current_state(ROOT, EXTRA) == state, 'V1 lifecycle drift')
            r.persist(OUT / (name + '.json'), r.seal(row))
            outcomes[name] = row['result']
            if name not in ('malformed', 'incomplete'):
                r.persist(OUT / (name + '-representation.json'), r.seal({
                    'scope': 'PROSPECTIVE_V1_ADAPTER_VALIDATION_ONLY',
                    'documents': [d.parse(raw) for raw in contents.values()],
                    'contract': d.from_opened(contents)}))
        r.require(outcomes['supported']['classification'] == outcomes['public-seed-bank']['classification']
                  == 'STATIC_SUPPORTED' and outcomes['unsupported']['classification'] == 'STATIC_UNSUPPORTED',
                  'support qualification mismatch')
        r.require(outcomes['malformed']['error']['code'] == 'MALFORMED_DOCUMENT'
                  and outcomes['incomplete']['error']['code'] == 'INCOMPLETE_CONTRACT', 'failure mismatch')
        try:
            r.safe_bytes({'value': 'SECRET[' + 'publication-witness]'})
        except r.Rejected:
            pass
        else:
            raise r.Rejected('publication rejection missing')
        r.require(r.current_state(ROOT, EXTRA) == state, 'final state drift')
        summary = r.seal({'classification': 'R5_77_BENCHMARK_DOCUMENT_CONTRACT_V1_QUALIFIED',
            'scope': 'PROSPECTIVE_V1_NOT_HISTORICAL_ACCEPTANCE', 'core_semantics': state['semantic_count'],
            'state': state['identity'], 'health': health['identity'], 'tests': tests,
            'document_roles': 2, 'required_top_level_fields': 4, 'optional_top_level_fields': 1,
            'references': False, 'adapter_modules': 1, 'completed_lifecycles': 5,
            'outcomes': {name: result['classification'] for name, result in outcomes.items()},
            'protected_read_attempts': guard.attempts, 'actual_authorizations': 0,
            'actual_openings': 0, 'actual_observations': 0, 'publication': 'PASS',
            'B02_status': ['B02_EXPOSED_IN_R5_75', 'B02_STATIC_RESULT_INDETERMINATE'],
            'B03_status': 'PRISTINE_NO_ACCESS', 'future_packaging': 'DEFINED_NOT_EXECUTED'})
        r.persist(OUT / 'summary.json', summary)
    print(json.dumps(summary, sort_keys=True))


if __name__ == '__main__':
    main()
