"""Evidence reconciliation; correct sequence attribution without changing any oracle."""
import copy
from datetime import datetime
import difflib
import json
import sys
from run import ROOT, HERE, OUT, load, save, text, sha, digest, now, verify, equal
from author import export, usage


def key(case, step):
    return digest(dict(case=case['id'], op=step['op'], args=step['args'], expected=step['expected'],
                       state=step['state'], unchanged=step['unchanged']))


def main():
    original = load(OUT / 'ORIGINAL-EXPECTATIONS-v2.json')
    modified = load(OUT / 'MODIFIED-EXPECTATIONS-v2.json')
    successor_sites = {}
    for c in modified:
        for i, s in enumerate(c['steps']):
            successor_sites.setdefault(key(c, s), []).append((c['id'], i))
    result = copy.deepcopy(load(OUT / 'RESULT.json'))
    for track in ('A', 'B'):
        functional = load(OUT / f'FUNCTIONAL-{track}-final.json')
        actual = {(r['case'], r['step']): r for r in functional['observations']}
        retained, superseded = [], []
        for c in original:
            for i, s in enumerate(c['steps']):
                sites = successor_sites.get(key(c, s), [])
                if not sites:
                    superseded.append(dict(case=c['id'], original_step=i, op=s['op']))
                    continue
                observations = [actual[site] for site in sites]
                retained.append(dict(case=c['id'], original_step=i, modified_steps=[site[1] for site in sites],
                    op=s['op'], passed=all(r['passed'] for r in observations)))
        assert len(retained) == 177 and len(superseded) == 5
        failures = [r for r in retained if not r['passed']]
        save(OUT / f'REGRESSION-v2-{track}.json', dict(retained=retained, superseded=superseded,
            retained_count=177, superseded_count=5, observed_regressions=len(failures), regressions=failures,
            authority='same frozen requirements and v2 expectations; exact retained-step mapping already pre-author reviewed',
            correction='REGRESSION-v1 ran incompatible old emergency sequence after superseded ignite. Its rescue false regression is a changed-prior-state cascade, not a behavior regression. Preserve original-on-modified diagnostics.'))
        result['tracks'][track]['regressions'] = len(failures)
    # Cross-track equality is observable records/results, not serialized file bytes.
    def observable(track):
        return [{k: r[k] for k in ('case', 'step', 'op', 'args', 'observed', 'persisted', 'returncode', 'stderr', 'rejection_or_read_bytes_ok')}
                for r in load(OUT / f'FUNCTIONAL-{track}-final.json')['observations']]
    result.update(utc_correction=now(), supersedes_summary='RESULT.json', oracle_or_candidate_changed=False,
        identical_cross_track_functional_projection=equal(observable('A'), observable('B')),
        matched_functional_observations=188, all_required_starting_contract_equivalence=False,
        outcome_scope='182 frozen baseline observations equivalent; 188 modified observations equivalent; inherited {} malformed-store diagnostic disproves full error-contract equivalence',
        reason='Successful finite modification and deterministic persistence/replay for both tracks; inherited starting error-contract divergence, incomplete total billing/configuration and no reliability superiority support an inconclusive practical advantage verdict')
    save(OUT / 'RESULT-v2.json', result)
    for track in ('A', 'B'):
        name = 'application.py' if track == 'A' else 'intent.json'
        suffix = 'py' if track == 'A' else 'json'
        before = (OUT / f'start/{track}/accepted/{name}').read_text().splitlines(keepends=True)
        after = (OUT / f'submissions/{track}/final.{suffix}').read_text().splitlines(keepends=True)
        text(OUT / f'authoring/{track}/modification.diff', ''.join(difflib.unified_diff(before, after, fromfile='accepted-baseline', tofile='submitted-final')))
    # Semantic change audit B: replacing the two policy guards reconstructs baseline.
    base = load(OUT / 'start/B/accepted/intent.json')
    final = load(OUT / 'submissions/B/final.json')
    restored = copy.deepcopy(final)
    for op in ('ignite', 'set_gate'):
        restored['operations'][op]['guards'] = copy.deepcopy(base['operations'][op]['guards'])
    assert restored == base
    save(OUT / 'SEMANTIC-AUDIT.json', dict(production_generator='unchanged R6.16 C generator',
        production_path=['lykoi_pipeline.scalar_profile.lower', 'air_compiler.mutable_values.compose', 'air_compiler.profiles.generate_mutable',
                         'production typed predicates/mutation runtime and atomic storage'],
        modified_declarative_policies=['ignite guard[1]', 'set_gate guard[0]'], other_intent_unchanged=True,
        generated_behavior_hand_edited=False, transport_computes_policy=False,
        actual_candidate_validation_rejections=0, uniquely_prevented_scored_defects=0,
        capability_gap='Inherited {} invalid-state classification uses production migration_required; no declarative decoder-error override exposed',
        limitations=['No seeded defect campaign', 'Types/bindings/effects validated; runtime policy checks not proof of requirements', 'No crash/concurrency qualification']))
    # Capture measurable shared effort; this coordinator is still running, so label as snapshot.
    exp, data = export('ses_ed9b3d117ffeGxlrS39tes3mPw')
    if data:
        complete = [m for m in data.get('messages', []) if m.get('info', {}).get('role') != 'assistant' or
                    ('finish' in m.get('info', {}) and 'completed' in m.get('info', {}).get('time', {}))]
        data = dict(messages=complete)
    save(OUT / 'COORDINATOR-TELEMETRY-SNAPSHOT.json', dict(utc=now(), session='ses_ed9b3d117ffeGxlrS39tes3mPw',
        export=exp, telemetry=usage(data), coverage='completed coordinator messages through this export; excludes current incomplete turn and later publication/final response',
        full_workflow_token_total=None))
    stage_rows = []
    for kind in ('BASELINE-ORIGINAL', 'BASELINE-ACCEPTED', 'BASELINE-ACCEPTED-v2'):
        for track in ('A', 'B'):
            r = load(OUT / f'{kind}-{track}.json')
            stage_rows.append(dict(stage=kind, track=track, test_seconds=r['seconds'],
                validation_lowering_seconds=r.get('validation_lowering_seconds'), already_compiled=kind.endswith('v2')))
    for track in ('A', 'B'):
        a = load(OUT / f'AUTHOR-{track}.json')
        t = a['telemetry']
        stage_rows.append(dict(stage='participant', track=track, seconds=a['participant_wall_seconds'],
            includes_nested_tools_selftests_generation=True, tool_seconds_nested=t['tool_seconds_nested'], export_seconds=a['export']['seconds']))
    stage_rows.append(dict(stage='external_scoring_replay_install_diagnostic_and_export',
        seconds=result['evaluation_wall_seconds'], includes_nested_test_intervals=True))
    save(OUT / 'MEASUREMENTS.json', dict(utc=now(), stages=stage_rows,
        participant_usage={t: {k: v for k, v in load(OUT / f'AUTHOR-{t}.json')['telemetry'].items() if k != 'metadata'} for t in ('A', 'B')},
        shared_reviewer_usage={k: v for k, v in load(OUT / 'REVIEWER-TELEMETRY.json')['telemetry'].items() if k != 'metadata'},
        shared_coordinator_snapshot={k: v for k, v in load(OUT / 'COORDINATOR-TELEMETRY-SNAPSHOT.json')['telemetry'].items() if k != 'metadata'},
        workflow_start_utc='2026-10-10T14:51:29.384000+00:00',
        workflow_start_authority='OpenCode coordinator session created timestamp 1791643889384; session-list observation',
        api_billing_usd=None, total_workflow_tokens=None, complete_publication_wall_seconds=None,
        overlapping_intervals_not_added=True, reported_cost_zero_is_not_free_billing=True,
        missing=['actual API billing', 'hidden provider retries', 'effective reasoning configuration', 'context capacity',
                 'complete coordinator final/publication token usage', 'per-stage reading/thinking/review/publication active-time attribution'],
        totals_must_not_add_cache_or_reasoning_twice='Export total = input + cache read/write + output + reasoning on these records; fields retained separately'))
    print(json.dumps(result, indent=2))
    print('Shared reviewer:', json.dumps(load(OUT / 'MEASUREMENTS.json')['shared_reviewer_usage']))
    print('Coordinator snapshot:', json.dumps(load(OUT / 'MEASUREMENTS.json')['shared_coordinator_snapshot']))


if __name__ == '__main__':
    main()
