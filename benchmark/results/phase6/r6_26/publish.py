"""Terminal compatibility-gap publication; no inference or executable repair."""
import json
import re
import subprocess
import sys
from common import HERE, ROOT, now, save, read, sha, tools

CLASSIFICATION = 'R6_26_PROVIDER_COMPATIBILITY_GAP'

def collect():
    assert not read('PROVIDER-QUALIFICATION.json')['passed']
    assert not (HERE / 'RESULT.json').exists()
    events = [json.loads(s) for s in (HERE / 'NEUTRAL/EVENTS.jsonl').read_text().splitlines()]
    steps = [e for e in events if e['type']=='step_finish']
    assert len(steps)==1 and not any(e['type']=='tool_use' for e in events)
    schemas = tools.definitions(['value','check','compose'])
    mcp = [json.loads(s) for s in (HERE / 'NEUTRAL/MCP.jsonl').read_text().splitlines()]
    actual = next(e['response']['result']['tools'] for e in mcp if e['request']['method']=='tools/list')
    expected = [dict(name=t['function']['name'],description=t['function']['description'],inputSchema=t['function']['parameters']) for t in schemas]
    assert actual==expected
    qualification = read('PROVIDER-QUALIFICATION.json')
    qualification.update(exact_observed_diagnostic='lykoi failed: Failed to get tools',
        location='OpenCode MCP tools/list discovery before any construction call',
        root_schema_observation='apply_operation has oneOf as its only root key and no root type; other three roots have type object',
        root_cause_status='Candidate schema-shape incompatibility; precise SDK validation exception not exposed. Do not attribute exclusively to this key.',
        envelope_normalization_repair='Not attempted: discovery failure precedes tool-call envelopes; changing tool inputSchema is outside unchanged-schema boundary',
        track_B='UNAVAILABLE through tested SDK/MCP route; live text inference available')
    save('PROVIDER-QUALIFICATION.json',qualification)
    tasks = read('TASKS.json')['tasks']
    cal = read('CALIBRATION.json')
    outcomes = [dict(id='CAL', scored=False, frozen_observations=len(cal['cases']))] + [dict(id=t['id'],scored=True,frozen_observations=len(t['cases'])) for t in tasks]
    for row in outcomes:
        row.update(status='NOT_REACHED',model_calls=0,tool_calls=0,completed_artifacts=0,executed_observations=0,
            validation='NOT_REACHED',expansion='NOT_REACHED',execution='NOT_REACHED',acceptance='NOT_REACHED',
            reason='Neutral construction-tool discovery prerequisite failed; participant not exposed')
    save('FUNCTIONAL-RESULTS.json',dict(classification=CLASSIFICATION, outcomes=outcomes, functional_correctness='UNMEASURED',AI_independent_execution_preserved=True))
    save('MODEL-REPRESENTATIONS.json',dict(completed_artifacts=[],partial_packets=[],reason='No construction tool invoked; no model semantic decisions to repair'))
    save('FAILURES.json',dict(classification=CLASSIFICATION,observations=[dict(track='B',phase='neutral compatibility',category='Provider transport incompatibility',
        diagnostic='OpenCode reports lykoi: Failed to get tools; model reports tools unavailable',semantic_failure=False)],
        unobserved=['Invalid tool-call arguments','Invalid symbolic dependencies','Invalid semantic composition','Incorrect functional behavior','Budget exhaustion'],
        preparation_incident=dict(phase='model-free diagnostic console output',exception='UnicodeEncodeError printing the MCP status checkmark to cp1252',
            impact='Diagnostic files were already saved. No model rerun or semantic effect. Exact command failure recorded in PREPARATION-NOTES.md.')))
    save('MEASUREMENTS.json',dict(classification=CLASSIFICATION,neutral_model_completion_steps=len(steps),
        actual_upstream_model_requests=None,neutral_sessions=len({e['sessionID'] for e in events}),
        calibration_model_calls=0,fresh_model_calls=0,neutral_tokens=steps[0]['part']['tokens'],
        SDK_reported_cost=steps[0]['part']['cost'],API_billing_cost=None,cost_note='SDK/catalog zero is retained as returned; billing is unavailable, not inferred zero',
        client_wall_seconds=read('NEUTRAL/STATUS.json')['wall_seconds'],inference_seconds=None,
        construction_seconds=None,validation_seconds=None,expansion_seconds=None,execution_seconds=None,
        selection_accuracy=dict(numerator=0,denominator=0,status='UNMEASURED: no tools exposed'),
        argument_validity=dict(numerator=0,denominator=0,status='NOT_REACHED'),successful_operations=0,
        calibration_completed_programs=0,fresh_completed_programs=0,fresh_frozen_tasks=4,fresh_tasks_attempted=0,
        fresh_acceptance_observations_frozen=25,fresh_acceptance_observations_executed=0,
        correction_turns=0,manual_repairs=0,provider_text_inference_failure_events=0,tool_discovery_failures=1,
        reasoning_configuration='high requested; token counter returned; effective effort not independently attested',
        unavailable=['Raw upstream HTTP envelopes','Isolated inference time','API billing','Effective context/output delivery','Hidden context exclusion','Upstream automatic retries']))
    save('RESULT.json',dict(timestamp=now(),classification=CLASSIFICATION,track_A='Historical R6.25 calibration evidence retained, no paired score',
        track_B='openai/gpt-6.1-sol: neutral text inference reached, construction track unavailable',
        track_C='Not selected',calibration='NOT_REACHED',fresh_tasks='0/4 attempted; all NOT_REACHED',
        capability_effect='UNDETERMINED',stopped=True,next_experiment='Separately authorize neutral exact-schema native-tool exposure qualification; if a schema-envelope representation change is proposed, prove preserved argument acceptance and freeze before a new comparison'))
    prep = read('PREPARATION-FREEZE.json')
    assert all(sha(HERE / p)==h for p,h in prep['files'].items())
    save('FREEZE.json',dict(timestamp=now(),scored_exposure=False,compatibility_passed=False,
        repaired_adapter=None,status='Terminal pre-score freeze, no scoring authorized through failed route',
        files={p:sha(HERE / p) for p in prep['files']},preparation_freeze_sha256=sha(HERE / 'PREPARATION-FREEZE.json')))
    print(CLASSIFICATION,'calibration/fresh NOT_REACHED; one neutral model completion; no semantic calls')

def verify():
    pins = read('BASELINE.json')['protected_files']
    mismatches = [p for p,h in pins.items() if sha(ROOT / p)!=h]
    assert not mismatches
    assert all(sha(HERE / p)==h for p,h in read('FREEZE.json')['files'].items())
    # The original test suite runs from its own directory, avoiding rebound fixtures.
    test = subprocess.run([sys.executable,'-m','unittest','discover','-s','.','-p','test_transport.py','-v'],cwd=HERE.parent / 'r6_25',capture_output=True,text=True)
    assert test.returncode==0 and 'Ran 17 tests' in test.stderr
    save('REGRESSION.json',dict(methods=17,passed=True,model_calls=0,stdout=test.stdout,stderr=test.stderr))
    events = [json.loads(s) for s in (HERE / 'NEUTRAL/EVENTS.jsonl').read_text().splitlines()]
    assert sum(e['type']=='step_finish' for e in events)==1
    for name in ('NEUTRAL','DIAGNOSTIC','SDK-DIAGNOSTIC'):
        rows=[json.loads(s) for s in (HERE / name / 'MCP.jsonl').read_text().splitlines()]
        assert not any(r['request']['method']=='tools/call' for r in rows)
        actual=next(r['response']['result']['tools'] for r in rows if r['request']['method']=='tools/list')
        assert actual==[dict(name=t['function']['name'],description=t['function']['description'],inputSchema=t['function']['parameters']) for t in tools.definitions(['value','check','compose'])]
    sources=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name not in ('VERIFICATION.json','PUBLICATION-IDENTITIES.json')]
    sources += [HERE.parent / 'R6_26-REPORT.md']
    sources += [ROOT / 'docs' / n for n in ('project-overview-r6.26.md','research-log-r6.26.md','decisions-r6.26.md')]
    files={}
    for p in sorted(sources):
        text=p.read_text(encoding='utf-8')
        if p.suffix=='.json': json.loads(text)
        if p.suffix=='.jsonl':
            for line in text.splitlines(): json.loads(line)
        if p.suffix in ('.md','.py'):
            assert all(s==s.rstrip() for s in text.splitlines()),str(p)
            if p.suffix=='.md':
                for link in re.findall(r'\]\(([^)]+)\)',text):
                    if not link.startswith(('http:','https:')):
                        target=(p.parent / link.split('#')[0]).resolve()
                        if target.name not in ('VERIFICATION.json','PUBLICATION-IDENTITIES.json'): assert target.exists(),str(target)
        files[p.relative_to(ROOT).as_posix()]=dict(sha256=sha(p),bytes=p.stat().st_size)
    diff=subprocess.run(['git','diff','--check'],capture_output=True,text=True)
    assert diff.returncode==0
    save('PUBLICATION-IDENTITIES.json',dict(timestamp=now(),files=files))
    save('VERIFICATION.json',dict(timestamp=now(),passed=True,kernel=26,protected_count=len(pins),protected_mismatches=[],
        frozen_preparation_verified=True,semantic_tool_schema_identity_verified=True,neutral_model_completions=1,
        calibration_and_scored_exposure=False,MCP_calls=0,regression_methods=17,JSON_links_whitespace=True,
        inference_calls_during_publication=0,git_diff_check=dict(returncode=diff.returncode,stdout=diff.stdout,stderr=diff.stderr),
        publication_files=len(files),publication_manifest_sha256=sha(HERE / 'PUBLICATION-IDENTITIES.json'),stopped=True))
    assert all(sha(ROOT / p)==x['sha256'] for p,x in read('PUBLICATION-IDENTITIES.json')['files'].items())
    print('Publication verified:',len(files),'files;',len(pins),'protected identities preserved; kernel26')

if __name__=='__main__':
    {'collect':collect,'verify':verify}[sys.argv[1]]()
