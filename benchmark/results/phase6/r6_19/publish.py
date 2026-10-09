"""Publish halted evidence and independently recheck identities; no inference."""
import hashlib
import json
import re
from pathlib import Path
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import run
ROOT=run.ROOT

def telemetry(records):
    return dict(completed_calls=len(records),input_tokens_reported=sum(x['response'].get('prompt_eval_count',0) for x in records),
                cached_input_tokens_reported=sum(x['response'].get('prompt_eval_cached_count',0) for x in records),
                output_tokens=sum(x['response'].get('eval_count',0) for x in records),
                inference_wall_seconds=sum(x['wall_seconds'] for x in records),
                generation_seconds=sum(x['response'].get('eval_duration',0)/1e9 for x in records),
                load_seconds=sum(x['response'].get('load_duration',0)/1e9 for x in records))

def collect():
    calls=[json.loads(p.read_text()) for p in sorted((HERE/'calls').glob('*.json'))]
    groups={'calibration':[x for x in calls if x['label'].startswith('calibration')],
            'discovery':[x for x in calls if x['label'].startswith('D')],
            'B_partial':[x for x in calls if x['label'].startswith('B_')]}
    rejections=[]
    for p in sorted((HERE/'sessions').glob('*.json')):
        session=json.loads(p.read_text())
        for entry in session['attempts']:
            raw=json.loads((HERE/'calls'/(entry['call']+'.json')).read_text())['response']['message']['content']
            t=time.perf_counter()
            try:
                run.seal_proposal(raw,[],session['discovery'])
                raise AssertionError('unexpected non-rejection')
            except run.c.Diagnostic as exc:
                feedback={'status':'reject','diagnostic':exc.data}
            except (KeyError,TypeError,ValueError) as exc:
                feedback={'status':'reject','diagnostic':dict(code='PROPOSAL_SHAPE',detail=str(exc))}
            assert feedback==entry['feedback']
            rejections.append(dict(call=entry['call'],feedback=feedback,posthoc_replay_seconds=time.perf_counter()-t))
    vocab=json.loads((HERE/'VOCABULARY.json').read_text())
    taskdoc=json.loads((HERE/'TASKS.json').read_text())
    summary=dict(classification='R6_19_PROTOCOL_HALT',timestamp=run.now(),telemetry={k:telemetry(v) for k,v in groups.items()},
        failed_calls=1,failed_call_tokens=None,discovery_seconds=vocab['discovery_seconds'],accepted_definitions=0,
        vocabulary_bytes=2,vocabulary_identity=vocab['canonical_sha256'],discovery_first_valid=0,discovery_tasks=3,
        development_acceptance='0/3; all nine proposals rejected before expansion',evaluation_B='E1: two invalid responses, third HTTP500; E2-E4 NOT_REACHED',
        evaluation_C='E1-E4 NOT_REACHED',generalization='NOT_REACHED',comparison='UNAVAILABLE: paired evaluation incomplete',
        original_validation_seconds=None,original_expansion_seconds=None,original_execution_seconds=None,
        timing_note='original rejection timing not instrumented; posthoc diagnostic replay is separate evidence, not substituted authoring timing',
        task_cases={x['id']:len(x['cases']) for x in taskdoc['tasks']},
        unsupported_requirements='none identified statically; no author program reached VM; no empirical coverage claim',
        rejections=rejections,efficiency='No net advantage established; all discovery cost retained even with empty vocabulary',
        total_round_time='UTC inventory observation through publication timestamp; interactive end-to-end wall interval, not active labor or local inference cost')
    run.save('RESULTS.json',summary)
    # Recover the deterministic failed request from the retained transcript, marked reconstructed.
    prior=json.loads((HERE/'calls/B_E1_2.json').read_text())
    session=json.loads((HERE/'sessions/B_E1.json').read_text())
    request=prior['request']
    request['messages'] += [prior['response']['message'],dict(role='user',content='Repair within same rules. Deterministic feedback: '+json.dumps(session['attempts'][-1]['feedback']))]
    run.save('FAILED-CALL.json',dict(label='B_E1_3',request=request,request_provenance='deterministic reconstruction from prior transcript; not original transport capture',
             response=None,error='HTTP500; see HALT.json and SERVER.log'))
    print(json.dumps({k:v for k,v in summary.items() if k!='rejections'},indent=2))

def verify():
    baseline=json.loads((HERE/'BASELINE.json').read_text())
    assert all(run.sha(ROOT/p)==h for p,h in baseline['protected_files'].items())
    frozen=json.loads((HERE/'FREEZE.json').read_text())
    assert all(run.sha(HERE/p)==h for p,h in frozen['files'].items())
    vocab=json.loads((HERE/'VOCABULARY.json').read_text())
    assert hashlib.sha256(run.c.canonical(vocab['definitions'])).hexdigest()==vocab['canonical_sha256']
    assert len(baseline['kernel_ledger']['baseline_kernel'])+len(baseline['kernel_ledger']['preserved_additions'])==26
    paths=list(HERE.rglob('*'))+[ROOT/'benchmark/results/phase6/R6_19-REPORT.md']
    paths += [ROOT/p for p in ['AGENTS.md','README.md','benchmark/README.md','docs/agent-workflow.md','docs/project-overview.md','docs/research-log.md','docs/decisions.md']]
    files={}
    for p in paths:
        if not p.is_file() or '__pycache__' in p.parts or p.name in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json'):
            continue
        if p.suffix=='.json':
            json.loads(p.read_text())
        files[p.relative_to(ROOT).as_posix()]={'sha256':run.sha(p),'bytes':p.stat().st_size}
    diff=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    assert diff.returncode==0,diff.stdout+diff.stderr
    # New untracked text is not covered by git diff --check.
    whitespace=[]
    for p in HERE.rglob('*'):
        if p.is_file() and p.suffix in ('.py','.md','.txt','.json'):
            for i,line in enumerate(p.read_text().splitlines(),1):
                if line.rstrip()!=line:
                    whitespace.append((str(p),i))
    assert not whitespace,whitespace
    report=ROOT/'benchmark/results/phase6/R6_19-REPORT.md'
    for link in re.findall(r'\]\(([^)]+)\)',report.read_text()):
        if not link.startswith(('http:','https:','#')):
            assert (report.parent/link.split('#')[0]).exists(),link
    run.save('PUBLICATION-IDENTITIES.json',dict(round='R6.19',classification='R6_19_PROTOCOL_HALT',files=files,
             exclusions='manifest and verification receipt exclude themselves; Python bytecode is disposable'))
    # Fresh reads, independent of constructed manifest dictionary.
    saved=json.loads((HERE/'PUBLICATION-IDENTITIES.json').read_text())
    assert all(run.sha(ROOT/p)==v['sha256'] and (ROOT/p).stat().st_size==v['bytes'] for p,v in saved['files'].items())
    end=run.now()
    elapsed=(run.datetime.fromisoformat(end)-run.datetime.fromisoformat('2026-10-09T00:26:53.614718+00:00')).total_seconds()
    run.save('VERIFICATION.json',dict(timestamp=end,classification='R6_19_PROTOCOL_HALT',
         inventory_start_utc='2026-10-09T00:26:53.614718+00:00',total_round_elapsed_seconds=elapsed,
         elapsed_definition='first inventory observation through publication verification; includes interactive setup/publication, not active labor',
         protected_identities=len(baseline['protected_files']),protected_mismatches=0,
         publication_files=len(files),publication_mismatches=0,kernel=26,
         freeze_verified=True,vocabulary_verified=True,json_parse='PASS',new_text_whitespace='PASS',
         git_diff_check='PASS',report_links='PASS',manifest_sha256=run.sha(HERE/'PUBLICATION-IDENTITIES.json'),
         inference_replay='NOT_RUN',acceptance_execution='NOT_REACHED',P6_A04_acceptance='NOT_RUN',P6_A05_access='NOT_ACCESSED'))
    print('Verified',len(files),'publication identities and',len(baseline['protected_files']),'protected identities; kernel26.')

if __name__=='__main__':
    if sys.argv[1]=='collect':
        collect()
    elif sys.argv[1]=='verify':
        verify()
    else:
        raise ValueError(sys.argv[1])
