"""Prospective transport wrapper reusing the exact frozen R6.33 broker/scorer."""
import importlib.util
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from preflight import ROOT, HERE, OUT, TEMP, EXE, load, save, raw, sha, sanitize, environment

SOURCE = ROOT / 'experiments/ai_lifecycle_r6_33/pilot.py'
spec = importlib.util.spec_from_file_location('r633_frozen_pilot', SOURCE)
pilot = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pilot)
pilot.OUT = OUT
pilot.TEMP = TEMP


def verify_inputs():
    for name, pin in load(OUT / 'BASELINE.json')['protected_files'].items():
        assert sha(ROOT / name) == pin, name
    for name, pin in load(OUT / 'LIFECYCLE-FREEZE.json')['inputs'].items():
        assert sha(ROOT / name) == pin, name
    return load(OUT / 'BASELINE.json')['protected_files']


def freeze():
    assert load(OUT / 'PREFLIGHT-RESULT.json')['passed']
    inherited = ROOT / 'benchmark/results/phase6/r6_33'
    for name in ('BASE-PROMPT.txt', 'SYNTAX.txt', 'MODIFICATION.txt'):
        raw(OUT / name, (inherited / name).read_text(encoding='utf-8'))
        assert sha(OUT / name) == sha(inherited / name)
    cfg = load(OUT / 'PREFLIGHT-CONFIG.json')
    save(OUT / 'MODEL.json', dict(provider=cfg['provider'], model=cfg['model'],
        variant=cfg['variant'], opencode_version=cfg['opencode_version'], config=cfg['config'],
        tool_schemas=cfg['tools'], requested_reasoning=cfg['requested_reasoning'],
        effective_reasoning=None, effective_authentication=None,
        budget=dict(max_CLI_invocations=15, max_proposals_per_stage=3, correction_turns_per_stage=2,
            max_participant_tool_calls=24, seconds_per_invocation=600, total_authoring_seconds=1200),
        execution_mode='Frozen R6.33 explicit JSON action broker over unchanged R6.32; '
                       'callable adapters discoverable but base syntax requests no tool invocation',
        no_configuration_change_after_results=True))
    paths = [HERE / 'PROTOCOL.md', HERE / 'tools.py', HERE / 'preflight.py',
        HERE / 'lifecycle_run.py', SOURCE, OUT / 'MODEL.json', OUT / 'PREFLIGHT-CONFIG.json',
        OUT / 'ENVIRONMENT-CHANGE.json', OUT / 'BASE-PROMPT.txt', OUT / 'SYNTAX.txt', OUT / 'MODIFICATION.txt']
    inherited_pins = load(inherited / 'FREEZE.json')['inputs']
    inputs = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    inputs.update(inherited_pins)
    receipt = dict(utc=datetime.now(timezone.utc).isoformat(), lifecycle_model_calls=0,
        inputs=inputs, R6_33_FREEZE_sha256=sha(inherited / 'FREEZE.json'),
        acceptance_source_sha256=sha(SOURCE), frozen_requirements_unchanged=True,
        tool_schema_sha256=pilot.digest(cfg['tools']), configuration=cfg['config'],
        requirement_disclosure='Base only initially; modification after original acceptance')
    save(OUT / 'LIFECYCLE-FREEZE.json', receipt)
    # Exact input keys expected by unchanged R6.33 runner.
    save(OUT / 'FREEZE.json', receipt)
    print('R6.36 lifecycle freeze verified; no participant lifecycle response yet')


class Author:
    def __init__(self, journal):
        self.journal = journal
        self.session = None
        self.calls = []
        self.started = time.perf_counter()
        self.cfg = load(OUT / 'MODEL.json')['config']

    def ask(self, stage, prompt):
        verify_inputs()
        number = len(self.calls) + 1
        assert number <= 15, 'MODEL_CALL_BUDGET'
        remaining = 1200 - (time.perf_counter() - self.started)
        assert remaining > 0, 'AUTHORING_TIME_BUDGET'
        folder = OUT / 'calls' / f'{number:02}'
        folder.mkdir(parents=True, exist_ok=False)
        raw(folder / 'prompt.txt', prompt)
        command = [EXE, 'run', '--format', 'json', '--model', 'openai/gpt-6.1-sol',
            '--variant', 'high', '--agent', 'r636-author', '--title', 'R6.36 bounded lifecycle author']
        if self.session:
            command += ['--session', self.session]
        command.append(prompt)
        self.journal.record('model_start', dict(stage=stage, call=number, prompt_sha256=sha(folder / 'prompt.txt')))
        start = time.perf_counter()
        timed_out = False
        try:
            child = subprocess.run(command, cwd=TEMP, env=environment(self.cfg), capture_output=True,
                                   timeout=min(600, remaining))
            stdout, stderr, code = child.stdout, child.stderr, child.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, code = exc.stdout or b'', exc.stderr or b'', None
            timed_out = True
        events = [sanitize(json.loads(line)) for line in stdout.decode('utf-8', errors='replace').splitlines()
                  if line.startswith('{')]
        raw(folder / 'stdout.jsonl', ''.join(json.dumps(e) + '\n' for e in events))
        for event in events:
            if event.get('sessionID'):
                self.session = event['sessionID']
        finishes = [e['part'] for e in events if e.get('type') == 'step_finish']
        texts = [e['part']['text'] for e in events if e.get('type') == 'text']
        errors = [e for e in events if e.get('type') == 'error']
        record = dict(call=number, stage=stage, session=self.session, returncode=code, timeout=timed_out,
            wall_seconds=time.perf_counter()-start, step_finishes=finishes, errors=errors,
            participant_tool_calls=sum(e.get('type') == 'tool_use' for e in events),
            stderr_bytes=len(stderr), stderr_raw_published=False)
        self.calls.append(record)
        save(folder / 'MEASUREMENT.json', record)
        self.journal.record('model_complete', record)
        if timed_out or code or errors or not texts or not finishes:
            raise RuntimeError('MODEL_TRANSPORT_OR_EMPTY_RESPONSE')
        # Frozen JSON broker requires explicit JSON requests, preventing double dispatch.
        if record['participant_tool_calls']:
            raise RuntimeError('PROTOCOL_UNEXPECTED_TOOL_DISPATCH_IN_JSON_BROKER_MODE')
        text = '\n'.join(texts).strip()
        if text.startswith('```'):
            text = '\n'.join(text.splitlines()[1:-1])
        return pilot.c.load(text)

    def close(self):
        if self.session:
            start = time.perf_counter()
            child = subprocess.run([EXE, 'export', self.session], cwd=TEMP,
                env=environment(self.cfg), capture_output=True, timeout=60)
            if child.returncode == 0:
                save(OUT / 'SESSION-EXPORT.json', sanitize(json.loads(child.stdout)))
            save(OUT / 'SESSION-EXPORT-STATUS.json', dict(returncode=child.returncode,
                wall_seconds=time.perf_counter()-start, stderr_bytes=len(child.stderr),
                stderr_raw_published=False))
        save(OUT / 'AUTHORING-CLOSED.json', dict(session=self.session, calls=self.calls,
            utc=datetime.now(timezone.utc).isoformat(), child_processes_terminated=True,
            no_further_inference_authorized=True))


pilot.Author = Author
pilot.protected = verify_inputs


def run():
    verify_inputs()
    pilot.run()


def replay():
    verify_inputs()
    pilot.replay()
    # Independently reconstruct saved registry/journal and dependency assertions.
    registry = pilot.Registry(OUT / 'registry')
    state = registry.read()['state']
    artifacts = {k: load(OUT / (k + '.json')) for k in ('old', 'new', 'a', 'b', 'a_new')}
    expectation = load(OUT / 'DEPENDENCY-IMPACT.json')['expectation']
    assert state['successors'] == expectation['expected_successors']
    assert state['migrations'][0]['decisions'] == expectation['expected_decisions']
    for caller, target in (('a', 'old'), ('b', 'old'), ('a_new', 'new')):
        assert artifacts[caller]['dependencies'] == {'BoundedScore': artifacts[target]['identity']}
    assert all(d['identity'] == pilot.c.identity(d) for d in artifacts.values())
    telemetry = pilot.Journal(OUT / 'telemetry').recover()
    assert not telemetry['pending'] and not telemetry['incomplete']
    save(OUT / 'REPLAY-INTEGRITY.json', dict(model_calls=0, predecessor_successor_identities=True,
        selective_migration=True, CallerB_retains_predecessor=True, registry_reconstructed=True,
        telemetry_hash_chain_verified=True, telemetry_events=len(telemetry['events']),
        dependency_expectation_matched=True, passed=True))


if __name__ == '__main__':
    {'freeze': freeze, 'run': run, 'replay': replay}[sys.argv[1]]()
