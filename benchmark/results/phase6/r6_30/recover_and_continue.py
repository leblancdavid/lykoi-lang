"""Preserve terminal timeout; recover native SDK evidence without author rerun."""
import json
import subprocess
import sys
import experiment as e

def recover():
    run='T2-B'
    session='ses_ede7c55aaffeJfBmmzBY7A17Uv'
    p=subprocess.run([str(e.h.EXE),'export',session],capture_output=True,encoding='utf-8',timeout=30,cwd=e.h.TEMP)
    assert p.returncode==0
    data=json.loads(p.stdout)
    e.save(run+'/SESSION.json',data)
    users=[p['text'] for m in data['messages'] if m['info']['role']=='user' for p in m['parts'] if p['type']=='text']
    e.save(run+'/DELIVERY.json',dict(session=session,matches_requested=users==[e.read(run+'/REQUEST.json')['prompt']],fresh_process=True,hidden_context_exclusion='UNATTESTED'))
    rows=[json.loads(l) for l in (e.HERE/run/'MCP.jsonl').read_text().splitlines()]
    completed=[r['complete'] for r in rows if 'complete' in r]
    assert completed
    e.save(run+'/FINAL-CANDIDATE.json',completed[-1])
    e.save(run+'/PROCESS.json',dict(timestamp=e.h.now(),returncode=None,termination='OUTER_TERMINAL_TIMEOUT',wall_seconds=None,
        author_process_terminated=True,verification='Get-Process after outer timeout showed no Python or opencode CLI processes; existing capital-OpenCode UI processes predate experiment.',
        candidate_retained=True,author_rerun=False,raw_stdout_stderr_lost=True))
    e.save('ORCHESTRATION-INTERRUPTION.json',dict(timestamp=e.h.now(),run=run,
        outer_command_timeout_seconds=120,affected_author_process_wall_seconds=None,
        raw_event_stream_available=False,native_session_export_available=True,rerun=False,
        remedy='Recover exact submitted candidate and native session export; continue unexecuted frozen order. Use successor telemetry collector for missing wall data; no acceptance or authoring edits.'))
    print('T2-B recovered without rerun; process wall unavailable')

def continue_run():
    e.verify()
    for run in e.read('FREEZE.json')['order'][4:]: e.author(run)
    e.save('BASE-COMPLETE.json',dict(timestamp=e.h.now(),all_processes_terminated=True,
        records={run:e.read(run+'/PROCESS.json') for run in e.read('FREEZE.json')['order']},modifications_disclosed=False,
        interrupted_stage='T2-B, compiled candidate retained, no outcome-informed rerun'))
    e.save('MODIFICATION-DISCLOSURE.json',dict(timestamp=e.h.now(),base_complete_sha256=e.digest(e.HERE/'BASE-COMPLETE.json'),
        withholding='Explicit prompts omit modifications before this timestamp; all base processes terminated. Hidden-context isolation remains CONTAMINATED_UNENFORCED.',tasks_sha256=e.digest(e.HERE/'TASKS.json')))
    for run in e.read('FREEZE.json')['modification_order']: e.author(run+'-M')

if __name__=='__main__':
    {'recover':recover,'continue':continue_run}[sys.argv[1]]()
