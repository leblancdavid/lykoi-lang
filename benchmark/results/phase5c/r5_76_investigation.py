"""Bounded non-B02 investigation; no actual grants, openers or observations.

No historical production framework is a prerequisite. Evidence is exclusive-create.
Synthetic direct inputs are diagnostics, not generic envelope qualification.
"""
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OUT = ROOT / 'benchmark/results/phase5c/R5_76-evidence'
EXTRA = ('benchmark/results/phase5c/r5_76_investigation.py',
         'benchmark/evaluation/test_document_envelope_r5_76.py')


def main():
    r.require(OUT.parent.is_dir() and not OUT.exists(), 'fresh investigation evidence required')
    OUT.mkdir()
    guard = r.Boundary(ROOT, [ROOT / 'benchmark/requirements/B03.md',
                             ROOT / 'benchmark/harness/profiles/B03.json',
                             ROOT / 'benchmark/harness/capabilities/B03.json',
                             ROOT / 'benchmark/results/phase5c/R5_75-evidence/opened-static-documents.json'])
    results = {}
    with guard.active():
        baseline = r.current_state(ROOT)
        state = r.current_state(ROOT, EXTRA)
        r.persist(OUT / 'state.json', state)
        for stage in r.HEALTH_STAGES:
            row = r.run_health_stage(ROOT, baseline, stage)
            # Retain the actual worker binding, do not pretend the worker hashed
            # the additional diagnostic files. Outer before/after checks bind them.
            r.require(r.current_state(ROOT, EXTRA) == state, 'diagnostic state drift')
            r.persist(OUT / ('health-' + stage + '.json'), r.seal(row))
            results[stage] = row
        command = [sys.executable, '-B', '-S', '-m', 'benchmark.evaluation.test_document_envelope_r5_76']
        process = subprocess.run(command, cwd=ROOT, env=r.controlled_environment(ROOT),
                                 capture_output=True, timeout=85)
        r.require(process.returncode == 0, 'document diagnostics failed; output withheld')
        envelope = json.loads(process.stdout)
        r.require(envelope['status'] == 'PASS' and envelope['protected_read_attempts'] == 0,
                  'document diagnostic boundary failure')
        r.persist(OUT / 'document-diagnostics.json', r.seal({'argv': command, **envelope}))
        health = r.health_record(baseline, results)
        r.persist(OUT / 'health.json', health)
        from benchmark.evaluation.test_document_envelope_r5_76 import fixture, explicit_fixture_consumer
        # Separate published demonstrations, with real fresh health binding.
        for outcome, contents in (
                ('supported', {'synthetic:explicit-fixture': r.canonical(fixture())}),
                ('unsupported', {'synthetic:explicit-fixture': r.canonical(fixture(True))}),
                ('malformed', {'synthetic:explicit-fixture': b'{invalid'}),
                ('incomplete', {'synthetic:unrelated': b'{}'})):
            directory = OUT / (outcome + '-synthetic-ledger')
            directory.mkdir()
            ledger = r.Ledger(directory)
            commitment = r.seal({'kind': 'synthetic', 'authority_class': r.SYNTHETIC_TEST,
                'expected_benchmark': 'independent-' + outcome + '-diagnostic',
                'resources': {name: {'commitment': r.digest(raw), 'seal': 'CLOSED', 'frozen': True,
                                     'provenance': 'non-task synthetic constructor'}
                              for name, raw in contents.items()}})
            frozen = r.freeze(baseline, commitment, health, ledger)
            grant = r.authorize_synthetic(frozen, commitment, ledger, baseline)
            result = r.observe(frozen, commitment, grant, ledger, lambda: r.current_state(ROOT),
                               lambda: commitment, lambda: contents, explicit_fixture_consumer)
            post = r.post_check(frozen, commitment, ledger, lambda: r.current_state(ROOT), lambda: commitment)
            r.require(r.current_state(ROOT, EXTRA) == state, 'diagnostic post-state drift')
            r.persist(OUT / (outcome + '.json'), r.seal({'scope': 'EXPLICIT_SYNTHETIC_FIXTURE_ONLY',
                'commitment': commitment, 'freeze': frozen, 'authorization': grant,
                'result': result, 'post_check': post,
                'events': [e['transition'] for e in ledger.events()]}))
        # Publication rejects recognizable secret values without printing them.
        rejected = False
        try:
            r.safe_bytes({'value': 'SECRET[' + 'synthetic-publication-witness]'} )
        except r.Rejected:
            rejected = True
        r.require(rejected, 'publication value guard missing')
        r.require(r.current_state(ROOT, EXTRA) == state, 'final state drift')
        summary = r.seal({'classification': 'R5_76_DOCUMENT_ENVELOPE_GAP',
            'generic_envelope_authority': 'NOT_IDENTIFIED_IN_INSPECTED_GENERIC_PROTOCOLS',
            'generic_extractor': 'NOT_IMPLEMENTED_WITHOUT_AUTHORITY',
            'generic_assembly': 'NOT_QUALIFIED', 'generic_static_interface': 'NOT_QUALIFIED',
            'synthetic_direct_interface': 'PASS', 'core_semantics': state['semantic_count'],
            'health': health['identity'], 'state': state['identity'],
            'document_diagnostics': envelope, 'protected_read_attempts': guard.attempts,
            'new_actual_authorizations': 0, 'new_actual_openings': 0, 'new_actual_observations': 0,
            'B02_status': ['B02_EXPOSED_IN_R5_75', 'B02_STATIC_RESULT_INDETERMINATE'],
            'B03_status': 'PRESERVED_NO_CONTENT_ACCESS', 'publication': 'PASS',
            'runner_modified': False, 'synthetic_observations': 4})
        r.persist(OUT / 'summary.json', summary)
    print(json.dumps({'classification': summary['classification'], 'health': 'PASS',
                      'diagnostic_tests': envelope['detail']['passed'], 'core_semantics': 30,
                      'protected_read_attempts': guard.attempts}, sort_keys=True))


if __name__ == '__main__':
    main()
