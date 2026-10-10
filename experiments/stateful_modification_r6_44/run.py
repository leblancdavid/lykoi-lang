"""Single-round preparation, external scoring, evidence and publication utilities."""
import copy
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = ROOT / 'benchmark/results/phase6/r6_44'
OLD = ROOT / 'benchmark/results/phase6/r6_16'
R43 = ROOT / 'benchmark/results/phase6/r6_43'
TEMP = Path(r'C:\Users\lblan\AppData\Local\Temp\opencode') / 'lykoi-r6-44'
UID = '00000000-0000-4000-8000-000000000001'
UID2 = '00000000-0000-4000-8000-000000000002'
TIME = '2026-01-01T00:00:00Z'


def now():
    return datetime.now(timezone.utc).isoformat()


def load(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def save(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


def text(p, value):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(value)


def verify(files):
    for name, v in files.items():
        assert sha(ROOT / name) == (v if isinstance(v, str) else v['sha256']), name
    return len(files)


def generate(intent):
    folder = ROOT / 'experiments/value_added_r6_16'
    sys.path.insert(0, str(folder))
    spec = importlib.util.spec_from_file_location('r644_generator', folder / 'generate.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.generate(intent, 'C')


def build(track, candidate, destination):
    start = time.perf_counter()
    if track == 'A':
        source, ir = candidate.read_text(encoding='utf-8'), None
        compile(source, str(candidate), 'exec')
    else:
        source, ir = generate(load(candidate))
    validation = time.perf_counter() - start
    text(destination / 'application.py', source)
    if ir is not None:
        save(destination / 'ir.json', ir)
    return destination / 'application.py', validation


def record(phase='cold', vent='open', load_='ordinary', **kw):
    return dict(id=UID, created_at=TIME, label='  Batch A  ', phase=phase,
                vent=vent, load=load_, **kw)


def step(op, args, result, state, unchanged=False):
    return dict(op=op, args=args, expected=result, state=copy.deepcopy(state), unchanged=unchanged)


def cases(changed):
    """Requirement truth table; imports no participant or production executable."""
    result = []
    def case(name, initial, steps, group='retained'):
        result.append(dict(id=name, initial=initial, steps=steps, group=group))
    case('absent-list', None, [step('list', {}, {'ok': []}, None, True)])
    case('blank-label', None, [step('create', dict(label=' \t ', vent='open', load='ordinary'),
         {'error': 'invalid_label'}, None, True)])
    for phase in ('cold', 'firing'):
        for vent in ('open', 'closed'):
            for category in ('ordinary', 'emergency'):
                r = record(phase, vent, category)
                valid = phase != 'firing' or vent == 'open' or category == 'emergency'
                prefix = '/'.join((phase, vent, category))
                for op in ('list', 'ignite', 'cool', 'rescue'):
                    code, after = None, copy.deepcopy(r)
                    if not valid:
                        code = 'invalid_state'
                    elif op == 'ignite':
                        if phase != 'cold': code = 'invalid_transition'
                        elif vent != 'open' and not (changed and category == 'emergency'): code = 'gate_required'
                        else: after['phase'] = 'firing'
                    elif op == 'cool':
                        if phase != 'firing': code = 'invalid_transition'
                        else: after['phase'] = 'cold'
                    elif op == 'rescue':
                        if phase != 'cold': code = 'invalid_transition'
                        elif vent != 'closed' or category != 'emergency': code = 'exception_denied'
                        else: after['phase'] = 'firing'
                    expected = {'error': code} if code else {'ok': [r] if op == 'list' else after}
                    state = [r] if code or op == 'list' else [after]
                    group = 'changed' if op == 'ignite' and phase == 'cold' and vent == 'closed' and category == 'emergency' else 'retained'
                    case(prefix + '/' + op, [r], [step(op, {} if op == 'list' else {'id': UID}, expected, state, bool(code) or op == 'list')], group)
                for value in ('open', 'closed', 'bad', None, 5, False, ['closed'], '__MISSING__'):
                    args = {'id': UID}
                    if value != '__MISSING__': args['value'] = value
                    code, after = None, copy.deepcopy(r)
                    if not valid: code = 'invalid_state'
                    elif phase == 'firing' and value == 'closed' and not (changed and category == 'emergency'): code = 'gate_locked'
                    elif type(value) is not str or value not in ('open', 'closed'): code = 'invalid_input'
                    else: after['vent'] = value
                    group = 'changed' if valid and phase == 'firing' and category == 'emergency' and value == 'closed' else 'retained'
                    case(prefix + '/gate/' + str(value), [r], [step('set_gate', args, {'error': code} if code else {'ok': after}, [r] if code else [after], bool(code))], group)
    for op in ('ignite', 'set_gate', 'cool', 'rescue'):
        for value in ('closed', 'bad', '__MISSING__'):
            args = {'id': UID2}
            if value != '__MISSING__': args['value'] = value
            case('missing/' + op + '/' + value, [record('firing')], [step(op, args, {'error': 'not_found'}, [record('firing')], True)])
    for name, invalid in [('blank', [dict(record(), label=' ')]), ('duplicate', [record(), record()]),
                          ('domain', [dict(record(), vent='bad')]), ('extra', [dict(record(), extra=True)]),
                          ('missing-field', [{k: v for k, v in record().items() if k != 'load'}]),
                          ('type', [dict(record(), phase=True)]), ('invariant', [record('firing', 'closed')])]:
        for op in ('list', 'ignite', 'set_gate', 'cool', 'rescue', 'create'):
            args = dict(id=UID2, value='bad', label=' ', vent='open', load='ordinary')
            case('invalid-store/' + name + '/' + op, invalid, [step(op, args, {'error': 'invalid_state'}, invalid, True)])
    for vent in ('open', 'closed'):
        for category in ('ordinary', 'emergency'):
            r = record(vent=vent, load_=category)
            case('create/' + vent + '/' + category, None, [step('create', {k: r[k] for k in ('label', 'vent', 'load')}, {'ok': r}, [r]),
                step('list', {}, {'ok': [r]}, [r], True),
                step('create', {k: r[k] for k in ('label', 'vent', 'load')}, {'error': 'id_collision'}, [r], True)])
    # Genuine cross-operation sequence; seed has another record that must survive.
    e = record(vent='closed', load_='emergency')
    other = dict(record(), id=UID2, label='Other', created_at='2025-12-31T00:00:00Z')
    on = dict(e, phase='firing')
    opened = dict(on, vent='open')
    if changed:
        steps = [step('ignite', {'id': UID}, {'ok': on}, [on, other]),
                 step('ignite', {'id': UID}, {'error': 'invalid_transition'}, [on, other], True),
                 step('set_gate', {'id': UID, 'value': 'open'}, {'ok': opened}, [opened, other]),
                 step('set_gate', {'id': UID, 'value': 'closed'}, {'ok': on}, [on, other]),
                 step('set_gate', {'id': UID, 'value': 'closed'}, {'ok': on}, [on, other]),
                 step('rescue', {'id': UID}, {'error': 'invalid_transition'}, [on, other], True),
                 step('cool', {'id': UID}, {'ok': e}, [e, other]),
                 step('list', {}, {'ok': [other, e]}, [e, other], True),
                 step('rescue', {'id': UID}, {'ok': on}, [on, other]),
                 step('set_gate', {'id': UID, 'value': 'closed'}, {'ok': on}, [on, other]),
                 step('list', {}, {'ok': [other, on]}, [on, other], True)]
    else:
        steps = [step('ignite', {'id': UID}, {'error': 'gate_required'}, [e, other], True),
                 step('rescue', {'id': UID}, {'ok': on}, [on, other]),
                 step('set_gate', {'id': UID, 'value': 'closed'}, {'error': 'gate_locked'}, [on, other], True),
                 step('cool', {'id': UID}, {'ok': e}, [e, other]),
                 step('list', {}, {'ok': [other, e]}, [e, other], True)]
    case('multi-operation-emergency', [e, other], steps, 'interaction')
    # Ordinary cycle stays completely unchanged.
    r, on, closed = record(), record('firing'), record(vent='closed')
    case('ordinary-cycle', [r], [step('ignite', {'id': UID}, {'ok': on}, [on]),
        step('set_gate', {'id': UID, 'value': 'closed'}, {'error': 'gate_locked'}, [on], True),
        step('cool', {'id': UID}, {'ok': r}, [r]),
        step('set_gate', {'id': UID, 'value': 'closed'}, {'ok': closed}, [closed]),
        step('ignite', {'id': UID}, {'error': 'gate_required'}, [closed], True),
        step('list', {}, {'ok': [closed]}, [closed], True)], 'interaction-retained')
    invalid_mixed = [record(), dict(record('firing', 'closed'), id=UID2)]
    for op in ('list', 'ignite', 'set_gate', 'cool', 'rescue', 'create'):
        case('invalid-unrelated/' + op, invalid_mixed, [step(op,
            dict(id=UID, value='closed', label=' ', vent='open', load='ordinary'),
            {'error': 'invalid_state'}, invalid_mixed, True)])
    second = dict(record(), id=UID2)
    case('timestamp-tie-id-order', [second, record()],
         [step('list', {}, {'ok': [record(), second]}, [second, record()], True)])
    return result


def equal(a, b):
    if type(a) is not type(b): return False
    if isinstance(a, dict): return set(a) == set(b) and all(equal(a[k], b[k]) for k in a)
    if isinstance(a, list): return len(a) == len(b) and all(equal(x, y) for x, y in zip(a, b))
    return a == b


def pairs(items):
    d = {}
    for k, v in items:
        if k in d: raise ValueError('duplicate output key')
        d[k] = v
    return d


def evaluate(application, expectations):
    start = time.perf_counter()
    rows = []
    for case in expectations:
        with tempfile.TemporaryDirectory(prefix='r644-', dir=TEMP) as tmp:
            store = Path(tmp) / 'records.json'
            if case['initial'] is not None:
                store.write_text(json.dumps(case['initial'], indent=1) + '\n', encoding='utf-8')
            for i, s in enumerate(case['steps']):
                before = store.read_bytes() if store.exists() else None
                t = time.perf_counter()
                p = subprocess.run([sys.executable, '-B', str(ROOT / 'experiments/value_added_r6_16/transport.py'), str(application)],
                    input=json.dumps(dict(op=s['op'], args=s['args'], providers=dict(uuid_v4=UID, utc_clock=TIME))),
                    text=True, capture_output=True, cwd=tmp, timeout=30,
                    env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
                elapsed = time.perf_counter() - t
                after = store.read_bytes() if store.exists() else None
                try:
                    observed = json.loads(p.stdout, object_pairs_hook=pairs)
                    persisted = json.loads(after, object_pairs_hook=pairs) if after is not None else None
                except (ValueError, TypeError):
                    observed, persisted = None, None
                result_ok = p.returncode == 0 and equal(observed, s['expected'])
                state_ok = equal(persisted, s['state'])
                byte_ok = not s['unchanged'] or before == after
                rows.append(dict(case=case['id'], group=case['group'], step=i, op=s['op'], args=s['args'], expected=s['expected'],
                    observed=observed, stdout=p.stdout, stderr=p.stderr, returncode=p.returncode, seconds=elapsed,
                    persisted=persisted, expected_state=s['state'], before_hex=None if before is None else before.hex(),
                    after_hex=None if after is None else after.hex(), result_ok=result_ok, state_ok=state_ok,
                    rejection_or_read_bytes_ok=byte_ok, passed=result_ok and state_ok and byte_ok))
    return dict(utc=now(), application_sha256=sha(application), seconds=time.perf_counter()-start,
        observations=rows, passed=sum(r['passed'] for r in rows), total=len(rows), accepted=all(r['passed'] for r in rows))


def prepare():
    assert TEMP.parent.is_dir() and not OUT.exists()
    started = now()
    protected = dict(load(R43 / 'BASELINE.json')['protected_files'])
    manifest = load(R43 / 'PUBLICATION-IDENTITIES.json')
    verify(manifest['files'])
    receipt = load(R43 / 'VERIFICATION.json')
    assert receipt['passed'] and receipt['manifest_sha256'] == sha(R43 / 'PUBLICATION-IDENTITIES.json')
    protected.update({k: v['sha256'] for k, v in manifest['files'].items()})
    for p in (R43 / 'PUBLICATION-IDENTITIES.json', R43 / 'VERIFICATION.json', R43 / 'QUALIFICATION.json'):
        protected[p.relative_to(ROOT).as_posix()] = sha(p)
    verify(protected)
    kernel = ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json'
    assert load(kernel)['final_count'] == 26
    TEMP.mkdir()
    save(OUT / 'BASELINE.json', dict(utc=started, head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        initial_status='R6.43 publication untracked; preserved', protected_files=protected, protected_count=len(protected),
        r6_43_publication_files=len(manifest['files']), r6_43_manifest_sha256=sha(R43 / 'PUBLICATION-IDENTITIES.json'),
        r6_43_receipt_sha256=sha(R43 / 'VERIFICATION.json'), kernel=26, kernel_accounting_sha256=sha(kernel)))
    originals = {}
    for track, historical in [('A', 'A'), ('B', 'C')]:
        filename = 'application.py' if track == 'A' else 'intent.json'
        src = OLD / f'submissions/{historical}/kiln/s2/{filename}'
        dest = OUT / f'start/{track}/original/{filename}'
        dest.parent.mkdir(parents=True)
        shutil.copyfile(src, dest)
        originals[track] = dict(source=src.relative_to(ROOT).as_posix(), sha256=sha(src))
    save(OUT / 'ORIGINAL-EXPECTATIONS.json', cases(False))
    save(OUT / 'MODIFIED-EXPECTATIONS.json', cases(True))
    raw_results = {}
    for track in ('A', 'B'):
        filename = 'application.py' if track == 'A' else 'intent.json'
        app, overhead = build(track, OUT / f'start/{track}/original/{filename}', OUT / f'build/baseline-original/{track}')
        r = evaluate(app, cases(False)); r['validation_lowering_seconds'] = overhead
        save(OUT / f'BASELINE-ORIGINAL-{track}.json', r)
        raw_results[track] = dict(passed=r['passed'], total=r['total'], accepted=r['accepted'])
    # Correct only the previously documented Python blank-label error, unscored.
    source = (OUT / 'start/A/original/application.py').read_text(encoding='utf-8')
    anchor = '        if (not isinstance(label, str) or not label.strip()\n'
    assert source.count(anchor) == 1
    corrected = source.replace(anchor, '        if isinstance(label, str) and not label.strip():\n            return {"error": "invalid_label"}\n' + anchor)
    text(OUT / 'start/A/accepted/application.py', corrected)
    text(OUT / 'start/B/accepted/intent.json', (OUT / 'start/B/original/intent.json').read_text(encoding='utf-8'))
    accepted = {}
    for track in ('A', 'B'):
        filename = 'application.py' if track == 'A' else 'intent.json'
        candidate = OUT / f'start/{track}/accepted/{filename}'
        app, overhead = build(track, candidate, OUT / f'build/baseline-accepted/{track}')
        r = evaluate(app, cases(False)); r['validation_lowering_seconds'] = overhead
        save(OUT / f'BASELINE-ACCEPTED-{track}.json', r)
        accepted[track] = dict(candidate_sha256=sha(candidate), executable_sha256=sha(app), passed=r['passed'], total=r['total'], accepted=r['accepted'])
    save(OUT / 'STARTING-APPLICATION.json', dict(utc=now(), originals=originals, original_results=raw_results, accepted=accepted,
        baseline_only_correction='Python blank string label error invalid_input -> invalid_label; three added lines; no scored modification',
        selection_bias='Previously exposed synthetic kiln; implementation-aware record-local profile selection favors Lykoi supported capability; not random or independent sourcing',
        state_fixtures_sha256=sha(OUT / 'ORIGINAL-EXPECTATIONS.json'), absent_store_identity=None))
    print(json.dumps(dict(original=raw_results, accepted=accepted), indent=2))
    assert all(x['accepted'] for x in accepted.values()), 'Baseline not equivalent; halt before authoring'


def revise_expectations():
    assert not (OUT / 'FREEZE.json').exists()
    save(OUT / 'ORIGINAL-EXPECTATIONS-v2.json', cases(False))
    save(OUT / 'MODIFIED-EXPECTATIONS-v2.json', cases(True))
    for track in ('A', 'B'):
        r = evaluate(OUT / f'build/baseline-accepted/{track}/application.py', cases(False))
        save(OUT / f'BASELINE-ACCEPTED-v2-{track}.json', r)
        print(track, r['passed'], r['total'])
        assert r['accepted']


def freeze():
    assert not (OUT / 'FREEZE.json').exists()
    for track in ('A', 'B'):
        assert load(OUT / f'BASELINE-ACCEPTED-v2-{track}.json')['accepted']
    # Install observation expectations are projections of already reviewed steps.
    e = record(vent='closed', load_='emergency')
    other = dict(record(), id=UID2, label='Other', created_at='2025-12-31T00:00:00Z')
    on = dict(e, phase='firing')
    save(OUT / 'INSTALL-EXPECTATIONS.json', dict(initial=[e, other], stages=[
        dict(version='baseline', steps=[step('list', {}, {'ok': [other, e]}, [e, other], True),
            step('ignite', {'id': UID}, {'error': 'gate_required'}, [e, other], True)]),
        dict(version='modified', steps=[step('ignite', {'id': UID}, {'ok': on}, [on, other]),
            step('set_gate', {'id': UID, 'value': 'closed'}, {'ok': on}, [on, other]),
            step('list', {}, {'ok': [other, on]}, [on, other], True)])]))
    for track in ('A', 'B'):
        work = TEMP / track
        work.mkdir()
        filename = 'application.py' if track == 'A' else 'intent.json'
        shutil.copyfile(OUT / f'start/{track}/accepted/{filename}', work / filename)
        shutil.copyfile(HERE / 'CONTRACT.md', work / 'CONTRACT.md')
        prompt = f'''You are R6.44 Track {track}, an AI software modification participant in a single bounded comparison.
Read CONTRACT.md and your own accepted {filename}. Implement its shared-policy modification by editing existing behavior.
Use only your own directory {work}. Do not inspect any other application implementation, comparison acceptance/results or historical application sources. Do not use network or spawn another AI. Do not inspect credentials or OpenCode configuration.
Budget: 480 seconds from invocation, <=16 tool calls, <=2 self-test batches <=60 seconds each, initial candidate plus at most ONE self-directed repair. No external acceptance feedback is available. Save first candidate as {'first.py' if track == 'A' else 'first.json'} BEFORE self-testing; final as {'final.py' if track == 'A' else 'final.json'}. Preserve the provided baseline as baseline.{'py' if track == 'A' else 'json'}. Write EFFORT.json listing revisions, self-tests with durations/results and any unsupported requirement. Return final authored path and effort. Rejections must preserve bytes, unrelated behavior/state must survive.
'''
        if track == 'A':
            prompt += 'Standard-library Python only, handle(op,args,providers) interface. Ordinary Python/file tools allowed. Do not add endpoints instead of modifying ignite and set_gate.\n'
        else:
            schema = ROOT / 'experiments/value_added_r6_16/intent-2.schema.json'
            shutil.copyfile(schema, work / 'intent.schema.json')
            prompt += f'''Edit ONLY declarative intent; use existing schema in intent.schema.json. Generation helper build.py uses unchanged production generator and writes generated Python/IR with validation timing to a new named output directory. Run python build.py first.json build-first (or final.json build-final). Generated code is read-only. No handwritten runtime logic. You may read ONLY existing generation/schema dependencies under {ROOT / 'experiments/value_added_r6_16'} (generate.py, schema_check.py, intent schemas) and {ROOT / 'src'} as needed. No other repository files.\n'''
            text(work / 'build.py', f'''import importlib.util, json, pathlib, sys, time
folder = pathlib.Path({str(ROOT / 'experiments/value_added_r6_16')!r})
sys.path.insert(0, str(folder))
spec = importlib.util.spec_from_file_location('generator', folder / 'generate.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
start = time.perf_counter()
source, ir = module.generate(json.loads(pathlib.Path(sys.argv[1]).read_text()), 'C')
elapsed = time.perf_counter() - start
out = pathlib.Path(sys.argv[2]); out.mkdir()
(out / 'application.py').write_text(source, encoding='utf-8')
(out / 'ir.json').write_text(json.dumps(ir, indent=2), encoding='utf-8')
(out / 'timing.json').write_text(json.dumps({{'validation_lowering_seconds': elapsed}}))
print(json.dumps({{'validation_lowering_seconds': elapsed, 'generated': str(out / 'application.py')}}))
''')
        prompt += 'Tool access is cooperative scope-restricted, not OS sandboxed. Do not change tooling, kernel, compiler, lowerer/runtime or any experimental wrapper. Stop after submission.\n'
        text(OUT / f'prompts/{track}.txt', prompt)
        shutil.copyfile(work / filename, work / ('baseline.py' if track == 'A' else 'baseline.json'))
        for p in work.iterdir():
            if p.is_file():
                dst = OUT / f'participant-inputs/{track}/{p.name}'
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(p, dst)
    paths = [HERE / 'CONTRACT.md', HERE / 'EXPECTED-IMPACT.json', HERE / 'PROTOCOL.md', HERE / 'run.py']
    paths += [OUT / name for name in ('ORIGINAL-EXPECTATIONS-v2.json', 'MODIFIED-EXPECTATIONS-v2.json',
        'INSTALL-EXPECTATIONS.json', 'STARTING-APPLICATION.json', 'PREAUTHOR-REVIEW-1.md', 'PREAUTHOR-REVIEW-2.md')]
    paths += list((OUT / 'prompts').glob('*')) + list((OUT / 'participant-inputs').rglob('*'))
    files = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths if p.is_file()}
    save(OUT / 'FREEZE.json', dict(utc=now(), files=files, candidate_authoring_started=False,
        participant_model='openai/gpt-6.1-sol', requested_reasoning='high', order=['A', 'B'],
        context_limit=None, effective_reasoning_attested=False, attested_os_isolation=False,
        reviewer_session='ses_ed9aec6cbffe1ZXGXwUyKmCiRw'))
    print('Frozen', len(files), 'identities; authoring has not started')


if __name__ == '__main__':
    globals()[sys.argv[1]]()
