"""Admission and connected-family dataset records; no training execution."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from prepare import ROOT, OUT, OLD, read, write, ref, sha, now

GATES = ('source_and_frc', 'validated_target', 'frozen_acceptance', 'deterministic_replay',
         'stable_provenance', 'no_known_contradiction', 'no_known_evaluation_leakage',
         'owner_authorized_candidate_preparation')


def admit(gates, partition):
    return set(gates) == set(GATES) and all(type(gates[g]) is bool and gates[g] for g in GATES) and partition == 'training_development'


def main():
    replays = [read(OUT / ('REPLAY-%d.json' % i)) for i in (1, 2)]
    assert all(r['passed'] for r in replays) and replays[0]['results'] == replays[1]['results']
    entries = []
    ledger = read(OUT / 'R6_48-SUCCESSOR-LEDGER.json')
    for old in ledger['entries']:
        assert admit(old['gates'], 'training_development')
        entries.append({'episode_id': 'R6.48/' + old['episode_id'], 'family_id': 'R6.48/' + old['family_id'],
            'tier_t': old['successor_tier_t'], 'tier_e': 'NOT_QUALIFIED',
            'partition': 'training_development', 'component': 'STATELESS_READ_CHECK_ENCODE',
            'direct': old['identities'], 'actual_semantic_tool_trajectory': None,
            'actual_ai_edit_trajectory': None,
            'scripted_trajectory': ref(OLD / 'episodes' / old['episode_id'] / 'SCRIPTED-TRAJECTORY.json'),
            'admission_gates': old['gates'], 'successor_of': 'R6.48 original blocked admission entry',
            'limitations': ['same coordinator', 'capability-aware synthetic source', 'finite scope',
                            'no independent acceptance', 'no actual AI construction trace']})
    for eid in ('S01', 'S02'):
        folder = OUT / 'episodes' / eid
        gates = dict.fromkeys(GATES, True)
        assert admit(gates, 'training_development')
        entry = {'episode_id': 'R6.49/' + eid, 'family_id': 'R6.49/LOCAL_RELEASE',
            'tier_t': 'T_CANDIDATE_ADMITTED', 'tier_e': 'NOT_QUALIFIED',
            'partition': 'training_development', 'component': 'PRODUCTION_LOCAL_STATE',
            'direct': {n: ref(folder / n) for n in ('SOURCE.json', 'FRC.json', 'ACCEPTANCE.json',
                'AI-INTENT.json', 'SYMBOLIC-IR.json', 'APPLICATION.py', 'VALIDATION.json')},
            'acceptance_evidence': [ref(OUT / ('REPLAY-%d.json' % i)) for i in (1, 2)],
            'actual_semantic_tool_trajectory': None,
            'actual_ai_edit_trajectory': ref(OUT / 'AI-CONSTRUCTION-TRANSCRIPT.json'),
            'tool_exposure': ref(OUT / 'TOOL-EXPOSURE.json'),
            'scripted_lowering': ref(folder / 'SCRIPTED-LOWERING.json'),
            'admission_gates': gates, 'successor_of': None,
            'limitations': ['same-coordinator source/FRC/oracle/AI selection', 'inherited context',
                'finite single-writer normal-restart scope', 'no independent review',
                'no semantic MCP trajectory', 'no concurrency/crash/power-loss qualification']}
        write(folder / 'DATASET-RECORD.json', entry)
        entries.append(entry)
    # These controls challenge erroneous admission, not the accepted candidates.
    controls = []
    good = dict.fromkeys(GATES, True)
    for missing in GATES:
        bad = dict(good, **{missing: False})
        controls.append({'control': 'failed-' + missing, 'rejected': not admit(bad, 'training_development')})
    controls += [{'control': 'evaluation-export', 'rejected': not admit(good, 'evaluation')},
                 {'control': 'missing-gate', 'rejected': not admit({k: v for k, v in good.items() if k != GATES[0]}, 'training_development')}]
    sys.path.insert(0, str(ROOT / 'experiments/value_added_r6_16'))
    from generate import generate
    from replay import run
    invalid = copy.deepcopy(read(OUT / 'episodes/S01/AI-INTENT.json'))
    invalid['operations']['release']['writes']['phase']['value'] = 'alien'
    try:
        generate(invalid, 'C')
    except Exception as exc:
        controls.append({'control': 'invalid-symbolic-domain', 'rejected': True,
                         'diagnostic': str(exc), 'exception_type': type(exc).__name__})
    else:
        raise AssertionError('invalid domain was admitted')
    wrong = copy.deepcopy(read(OUT / 'episodes/S01/AI-INTENT.json'))
    wrong['operations']['release']['writes']['phase']['value'] = 'queued'
    source, _ = generate(wrong, 'C')
    with tempfile.TemporaryDirectory(prefix='lykoi-r649-control-') as tmp:
        app = Path(tmp) / 'wrong-transition.py'
        app.write_text(source, encoding='utf-8', newline='\n')
        result = run('S01', app)
    assert not result['passed']
    write(OUT / 'WRONG-TRANSITION-CONTROL.json', {'seeded': True, 'not_ai_failure': True,
        'intent': wrong, 'validation_passed': True, 'observations': result,
        'admission': 'REJECTED_CORRECTNESS', 'training_example': False})
    controls.append({'control': 'well-typed-wrong-transition', 'rejected': not result['passed']})
    assert all(c['rejected'] for c in controls)
    write(OUT / 'ADMISSION-CONTROLS.json', {'utc': now(), 'controls': controls, 'all_passed': True})
    write(OUT / 'DATASET-INDEX.json', {'version': 'lykoi-tier-t-pilot-1',
        'policy': ref(ROOT / 'docs/training-data-admission-r6.49.md'), 'entries': entries,
        'tier_t_count': 10, 'tier_e_count': 0, 'requirements_count': 10,
        'training_performed': False, 'distribution_rights': 'owner-authorized research candidate preparation only'})
    write(OUT / 'DEDUPLICATION-AND-PARTITIONS.json', {
        'method': 'source obligations, input/output/error order, domain, pinned abstraction ancestry and scaffold review',
        'semantic_duplicates_within_counted_cohort': [],
        'nominal_requirement_families': 5, 'broad_scaffold_components': 2,
        'components': [
            {'id': 'STATELESS_READ_CHECK_ENCODE', 'families': ['R6.48/F1', 'R6.48/F2', 'R6.48/F3', 'R6.48/F4'],
             'episodes': ['R6.48/E%02d' % n for n in range(1, 9)],
             'shared': ['byte atoms', 'ordered checks', 'UInt16BE output', 'add/le/eq', 'F4 nested pinned definitions'],
             'related_auxiliary': 'R6.47 arithmetic cohort; not newly admitted or counted'},
            {'id': 'PRODUCTION_LOCAL_STATE', 'families': ['R6.49/LOCAL_RELEASE'],
             'episodes': ['R6.49/S01', 'R6.49/S02'],
             'shared': ['R6.16 C scalar/mutable generator', 'typed enum state', 'ordered guards',
                        'release invariant', 'atomic store', 'common acceptance sequence prefix'],
             'related_auxiliary': 'R6.16 kiln/custody state-machine skeletons; not newly admitted or counted',
             'difference': 'S02 rejects ready release, requires held, can reset to queued and opens seal atomically; S01 releases directly from ready'}],
        'all_counted_partitions': 'training_development', 'evaluation_qualified_families': [],
        'excluded': ['R6.48/F5', 'R6.48/F6', 'all future independent evaluation solutions'],
        'quarantine_not_evaluation_qualification': True,
        'renamed_programs_or_replay_observations_counted_as_episodes': False,
        'template_derived': ['S01/S02 share a profile and family; distinct behavior, not independent commissions'],
        'claim_limit': 'manual cohort semantic review, not exhaustive equivalence of all historical artifacts'})
    write(OUT / 'READINESS.json', {'classification': 'R6_49_TRAINING_DATA_PILOT_QUALIFIED',
        'tier_t_candidates': 10, 'tier_e_examples': 0, 'nominal_requirement_families': 5,
        'broad_scaffolds': 2, 'stateful_accepted': 2, 'new_stateful_family': 1,
        'stateful_acceptance_steps_per_pass': 59, 'final_restart_reads_per_pass': 2,
        'fresh_process_requests_two_passes': 122, 'reassessment_observations': 162,
        'direct_records': 10, 'actual_ai_edit_trajectory_episodes': 2,
        'actual_ai_semantic_mcp_trajectory_episodes': 0,
        'semantic_coverage': ['typed arithmetic', 'Bool checks', 'explicit error precedence',
            'pinned composition', 'enum lifecycle transitions', 'prewrite guards', 'record invariants',
            'input replacement', 'atomic local persistence', 'AI-free normal restarts'],
        'production_kernel': 26, 'all_26_construct_coverage_claim': False,
        'gaps': ['independent commissioning/review', 'withheld evaluation families', 'semantic stateful MCP authoring',
                 'broad domain/scaffold diversity', 'authority/relations/migrations/time semantics training coverage',
                 'full coordinator billing', 'trainable checkpoint/dependency qualification'],
        'small_lora_smoke_test_justified': False,
        'reason': 'admission mechanics now qualified; 10 correlated candidates with no independent evaluation do not justify allocating a training run yet',
        'next_experiment': 'separately authorize one independently human-commissioned local-stateful family with source-authoritative acceptance review and a withheld sibling; qualify existing-semantics stateful authoring interface before training',
        'training_runs': 0, 'stop': 'after publication; wait for explicit authorization'})
    print(json.dumps({'tier_t': 10, 'tier_e': 0, 'stateful': 2, 'admission_controls': len(controls),
        'classification': 'R6_49_TRAINING_DATA_PILOT_QUALIFIED'}))


if __name__ == '__main__':
    main()
