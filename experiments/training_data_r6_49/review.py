"""Read-only successor review: historical contracts, symbols and frozen suites."""
import copy
import hashlib
import sys
import time
from prepare import ROOT, OUT, OLD, read, write, canonical, ref, now, sha

sys.path.insert(0, str(ROOT / 'experiments/typed_composition_r6_18'))
import composition as c


MEANINGS = {
    'E01': 'two byte sum; capacity120; reads before capacity before end',
    'E02': '2*fragile+ordinary; ceiling600; reads before quote before end',
    'E03': 'binary agreement; first flag validation precedes second read; returns a',
    'E04': 'binary exactly-one; both reads precede flag validation; returns sum',
    'E05': 'version7 before count read; count<=12; returns count',
    'E06': 'three reads; low<=high then low<=reading then reading<=high',
    'E07': 'nested pair-add tally of three bytes; ceiling300',
    'E08': 'shared double/triple compositions; 2*a+3*b; ceiling1000',
}


def observations(eid):
    folder = OLD / 'episodes' / eid
    package = c.load((folder / 'SYMBOLIC.json').read_text())
    diag = c.diagnose(package)
    assert diag == read(folder / 'VALIDATION.json')['diagnostic']
    expanded = c.expand(package)
    assert expanded['plan'] == read(folder / 'EXECUTABLE.json')
    root = 'program/' + package['program']['identity']
    rows = []
    for case in read(folder / 'ACCEPTANCE.json')['cases']:
        actual = copy.deepcopy(c.vm.execute(expanded['plan'], bytes.fromhex(case['input_hex']), case.get('limits')))
        if 'output' in actual:
            actual['output_hex'] = actual.pop('output').hex()
        expected = copy.deepcopy(case['expected'])
        if 'error' in expected:
            role = expected['error'].pop('role')
            expected['error']['node'] = root if role == 'program' else root + '/' + role
        assert all(k in actual and type(actual[k]) is type(v) and actual[k] == v for k, v in expected.items())
        rows.append(actual)
    return rows, package


def main():
    start = time.perf_counter()
    ledger, evidence = [], []
    old_ledger = read(OLD / 'ADMISSION-LEDGER.json')
    assert read(OLD / 'TRAINING-READY-EXPORT-MANIFEST.json')['admitted_episode_count'] == 0
    for n in range(1, 9):
        eid = 'E%02d' % n
        folder = OLD / 'episodes' / eid
        source, frc = read(folder / 'SOURCE.json'), read(folder / 'FRC.json')
        assert frc['status'] == 'FROZEN' and not frc['ambiguities']
        assert frc['source_sha256'] == sha(folder / 'SOURCE.json')
        first, package = observations(eid)
        second, _ = observations(eid)
        assert first == second
        for pass_id in (1, 2, 3):
            historical = next(r for r in read(OLD / ('REPLAY-%d.json' % pass_id))['results'] if r['episode_id'] == eid)
            assert [o['actual'] for o in historical['observations']] == first
        original = next(e for e in old_ledger['entries'] if e['episode_id'] == eid)
        row = {'episode_id': eid, 'family_id': original['family_id'],
            'historical_status': original['admission_status'], 'successor_tier_t': 'T_CANDIDATE_ADMITTED',
            'tier_e': 'NOT_QUALIFIED', 'meaning_review': MEANINGS[eid],
            'source_authority': 'preserved owner-authorized synthetic fixture source; not independent human approval',
            'training_authorization': 'R6.49 explicit review as training candidates; research-preparation scope',
            'third_party_requirement_material': False, 'same_coordinator': True,
            'independent_commissioning': False, 'independent_review': False,
            'correctness_scope': 'finite frozen suite plus explicit source/ordered-symbol inspection; no universal proof',
            'known_correctness_defects': [], 'known_evaluation_set_leakage': False,
            'exposure': 'training-development F1-F4; exposed quarantine F5/F6 excluded, not qualified evaluation',
            'near_duplicate_group': 'STATELESS_READ_CHECK_ENCODE', 'semantic_duplicate_of': None,
            'semantic_ai_trajectory': None, 'direct_representation_available': True,
            'gates': {g: True for g in ('source_and_frc', 'validated_target', 'frozen_acceptance',
                'deterministic_replay', 'stable_provenance', 'no_known_contradiction',
                'no_known_evaluation_leakage', 'owner_authorized_candidate_preparation')},
            'identities': {name: ref(folder / name) for name in ('SOURCE.json', 'FRC.json',
                'ACCEPTANCE.json', 'SYMBOLIC.json', 'EXECUTABLE.json', 'VALIDATION.json')},
            'program_identity': package['program']['identity'], 'cases_per_replay': len(first)}
        ledger.append(row)
        evidence.append({'episode_id': eid, 'first_replay': first, 'second_replay': second,
                         'matches_three_historical_replays': True})
    write(OUT / 'R6_48-SUCCESSOR-LEDGER.json', {'policy': ref(ROOT / 'docs/training-data-admission-r6.49.md'),
        'historical_ledger': ref(OLD / 'ADMISSION-LEDGER.json'), 'historical_admitted_count': 0,
        'successor_tier_t_candidates': 8, 'tier_e_count': 0, 'entries': ledger,
        'not_reassessed': ['E09', 'E10', 'E11', 'E12'], 'historical_classification_unchanged': True})
    write(OUT / 'R6_48-REASSESSMENT-REPLAY.json', {'utc': now(), 'ai_calls': 0,
        'execution_ms': round((time.perf_counter() - start) * 1000), 'results': evidence,
        'replays_per_episode': 2, 'observations': sum(len(e['first_replay']) * 2 for e in evidence),
        'passed': True})
    print('Eight successor Tier T candidates; zero Tier E; 162 new replay observations')


if __name__ == '__main__':
    main()
