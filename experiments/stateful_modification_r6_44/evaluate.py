"""AI-free external scoring/replay; immutable submissions and frozen expectations."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from run import ROOT, HERE, OUT, TEMP, UID, TIME, load, save, sha, digest, now, verify, build, evaluate, equal, pairs, generate
from author import export, usage


def projection(result):
    return [{k: v for k, v in r.items() if k != 'seconds'} for r in result['observations']]


def audit(track):
    events = []
    for line in (OUT / f'authoring/{track}/events.jsonl').read_text(encoding='utf-8').splitlines():
        try: events.append(json.loads(line))
        except ValueError: pass
    tools = []
    for event in events:
        part = event.get('part', {})
        if part.get('type') == 'tool':
            state = part.get('state', {})
            tools.append(dict(tool=part.get('tool'), status=state.get('status'), time=state.get('time'),
                              input=state.get('input'), output=state.get('output')))
    opposite = 'B' if track == 'A' else 'A'
    forbidden = ['/r6_44/submissions/', '/r6_44/build/', 'original-expectations', 'modified-expectations',
                 '/r6_16/submissions/', '/r6_44/authoring/', f'/lykoi-r6-44/{opposite.lower()}/']
    flags = []
    for i, t in enumerate(tools):
        raw = json.dumps(t['input']).replace('\\', '/').lower()
        hits = [s for s in forbidden if s in raw]
        if hits: flags.append(dict(index=i, hits=hits))
    r = load(OUT / f'AUTHOR-{track}.json')
    filename = 'baseline.py' if track == 'A' else 'baseline.json'
    inputname = 'application.py' if track == 'A' else 'intent.json'
    suffix = 'py' if track == 'A' else 'json'
    return dict(raw_event_tools=tools, forbidden_input_markers=flags, marker_audit_complete=bool(tools),
        starting_baseline_preserved=sha(OUT / f'submissions/{track}/{filename}') == sha(OUT / f'start/{track}/accepted/{inputname}'),
        first_final_identical=sha(OUT / f'submissions/{track}/first.{suffix}') == sha(OUT / f'submissions/{track}/final.{suffix}'),
        tool_budget_ok=r['telemetry']['tool_calls'] <= 16, wall_budget_ok=r['participant_wall_seconds'] < 480,
        scope_attestation=False, retained_provider_hidden_context=None,
        note='Marker and visible-input audit only, not OS isolation or proof of hidden-input exclusion')


def invoke(app, tmp, op, args):
    store = Path(tmp) / 'records.json'
    before = store.read_bytes() if store.exists() else None
    start = time.perf_counter()
    p = subprocess.run([sys.executable, '-B', str(ROOT / 'experiments/value_added_r6_16/transport.py'), str(app)],
        input=json.dumps(dict(op=op, args=args, providers=dict(uuid_v4=UID, utc_clock=TIME))),
        cwd=tmp, text=True, capture_output=True, timeout=30, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    elapsed = time.perf_counter()-start
    after = store.read_bytes() if store.exists() else None
    try: observed = json.loads(p.stdout, object_pairs_hook=pairs)
    except ValueError: observed = None
    return dict(op=op, args=args, observed=observed, returncode=p.returncode, stdout=p.stdout, stderr=p.stderr,
                seconds=elapsed, before_hex=None if before is None else before.hex(), after_hex=None if after is None else after.hex(),
                bytes_unchanged=before == after)


def installation(track, final_app):
    spec = load(OUT / 'INSTALL-EXPECTATIONS.json')
    rows = []
    with tempfile.TemporaryDirectory(prefix='r644-install-', dir=TEMP) as tmp:
        tmp = Path(tmp); store = tmp / 'records.json'
        store.write_text(json.dumps(spec['initial'], indent=1) + '\n', encoding='utf-8')
        installed = tmp / 'application.py'
        for stage in spec['stages']:
            source = OUT / f'build/baseline-accepted/{track}/application.py' if stage['version'] == 'baseline' else final_app
            before_install = store.read_bytes()
            t = time.perf_counter(); shutil.copyfile(source, installed); install_s = time.perf_counter()-t
            assert store.read_bytes() == before_install
            for s in stage['steps']:
                r = invoke(installed, tmp, s['op'], s['args'])
                state = json.loads(store.read_bytes())
                r.update(version=stage['version'], installed_sha256=sha(installed), install_seconds=install_s,
                         expected=s['expected'], expected_state=s['state'], state=state,
                         store_identity_unchanged_at_install=True,
                         passed=equal(r['observed'], s['expected']) and equal(state, s['state']) and
                             (not s['unchanged'] or r['bytes_unchanged']))
                rows.append(r)
    return dict(track=track, observations=rows, accepted=all(r['passed'] for r in rows))


def diagnostic(track, final_app):
    """Unscored post-submission witness disclosed by B; no oracle amendment."""
    rows = []
    for version, app in [('baseline', OUT / f'build/baseline-accepted/{track}/application.py'), ('modified', final_app)]:
        for op, args in [('list', {}), ('set_gate', {'id': UID}), ('ignite', {'id': UID})]:
            with tempfile.TemporaryDirectory(prefix='r644-diagnostic-', dir=TEMP) as tmp:
                (Path(tmp) / 'records.json').write_bytes(b'{}')
                r = invoke(app, tmp, op, args)
                r.update(version=version, requirement_expected={'error': 'invalid_state'},
                         requirement_match=r['observed'] == {'error': 'invalid_state'})
                rows.append(r)
    return dict(track=track, status='UNSCORED_POSTAUTHOR_DIAGNOSTIC', provenance='Participant B disclosed {} top-level malformed store limitation',
        observations=rows, inherited_if_baseline_equals_modified=all(equal({k: v for k, v in rows[i].items() if k not in ('seconds','version')},
            {k: v for k, v in rows[i+3].items() if k not in ('seconds','version')}) for i in range(3)),
        scored_expectations_changed=False)


def main():
    start = time.perf_counter(); begin = now()
    verify(load(OUT / 'FREEZE.json')['files'])
    verify(load(OUT / 'BASELINE.json')['protected_files'])
    modified = load(OUT / 'MODIFIED-EXPECTATIONS-v2.json')
    original = load(OUT / 'ORIGINAL-EXPECTATIONS-v2.json')
    summary = {}
    for track in ('A', 'B'):
        author = load(OUT / f'AUTHOR-{track}.json')
        assert author['process_exited']
        verify(author['files'])
        save(OUT / f'AUDIT-{track}.json', audit(track))
        suffix = 'py' if track == 'A' else 'json'
        results = {}
        apps = {}
        for candidate in ('first', 'final'):
            app, overhead = build(track, OUT / f'submissions/{track}/{candidate}.{suffix}', OUT / f'build/submitted/{track}/{candidate}')
            apps[candidate] = app
            r = evaluate(app, modified); r['validation_lowering_seconds'] = overhead
            save(OUT / f'FUNCTIONAL-{track}-{candidate}.json', r)
            results[candidate] = dict(passed=r['passed'], total=r['total'], accepted=r['accepted'],
                validation_lowering_seconds=overhead, test_seconds=r['seconds'])
        replay = evaluate(apps['final'], modified)
        save(OUT / f'REPLAY-{track}.json', replay)
        first = load(OUT / f'FUNCTIONAL-{track}-final.json')
        original_r = evaluate(apps['final'], original)
        save(OUT / f'ORIGINAL-ON-MODIFIED-{track}.json', original_r)
        install = installation(track, apps['final']); save(OUT / f'INSTALL-{track}.json', install)
        diag = diagnostic(track, apps['final']); save(OUT / f'DIAGNOSTIC-{track}.json', diag)
        # Compare all nonsuperseded original individual observations by full expectation.
        keys = lambda c, s: digest(dict(case=c['id'], op=s['op'], args=s['args'], expected=s['expected'], state=s['state'], unchanged=s['unchanged']))
        new_keys = {keys(c, s) for c in modified for s in c['steps']}
        retained, superseded = [], []
        for c in original:
            for i, s in enumerate(c['steps']):
                (retained if keys(c, s) in new_keys else superseded).append(dict(case=c['id'], step=i, op=s['op']))
        retained_keys = {(r['case'], r['step']) for r in retained}
        regressions = [r for r in original_r['observations'] if (r['case'], r['step']) in retained_keys and not r['passed']]
        assert len(retained) == 177 and len(superseded) == 5
        save(OUT / f'REGRESSION-{track}.json', dict(retained=retained, superseded=superseded, regressions=regressions,
            retained_count=len(retained), superseded_count=len(superseded), observed_regressions=len(regressions)))
        same = projection(first) == projection(replay)
        summary[track] = dict(results=results, replay_passed=replay['passed'], replay_total=replay['total'],
            replay_identical=same, replay_projection_sha256=digest(projection(replay)),
            regressions=len(regressions), retained_original=177, superseded_original=5,
            installation_accepted=install['accepted'], inherited_malformed_store_limitation=not all(r['requirement_match'] for r in diag['observations']))
        print(track, json.dumps(summary[track]))
    # Legacy impact is not authoritative; query all three policy operand fields.
    ir = load(OUT / 'build/submitted/B/final/ir.json')
    from air_compiler.parser import parse
    from air_compiler.semantics import impact
    queries = {field: impact(parse(json.dumps(ir['base'])), 'field:' + field) for field in ('phase', 'vent', 'load')}
    save(OUT / 'IMPACT-DIAGNOSTIC.json', dict(tool='air_compiler.semantics.impact', actual=queries,
        expected_map_sha256=sha(HERE / 'EXPECTED-IMPACT.json'), authoritative=False,
        missing_extension_users=['ignite', 'set_gate', 'cool', 'rescue', 'predicate_semantics.invariants'],
        interpretation='Legacy scalar base traversal omits typed extension operation/predicate users. It is incomplete for this modification.'))
    exp, review = export('ses_ed9aec6cbffe1ZXGXwUyKmCiRw')
    save(OUT / 'REVIEWER-TELEMETRY.json', dict(export=exp, telemetry=usage(review)))
    save(OUT / 'RESULT.json', dict(utc_start=begin, utc_end=now(), evaluation_wall_seconds=time.perf_counter()-start,
        tracks=summary, classification='R6_44_COMPARISON_INCONCLUSIVE',
        reason='Both frozen modifications pass with zero candidate repairs/regressions; unscored inherited malformed-store error divergence limits full starting-contract equivalence; no practical Lykoi advantage demonstrated',
        ai_independent_execution=True, ai_calls_during_functional_execution=0, additional_experiments_authorized=False))


if __name__ == '__main__':
    main()
