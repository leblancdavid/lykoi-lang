"""Budgeted experiment facade; delegates semantic admission/execution unchanged."""
import json
import os
import time
import sys
from common import ROOT,OUT,module,Registry,Journal,c,save,load,normalize,package,digest
from development import development_check

legacy=module('r640_legacy',ROOT/'experiments/ai_lifecycle_r6_37/tools.py')
original_dispatch=legacy.dispatch
RUN=os.environ.get('R640_RUN','qualification')
assert RUN.replace('-','').isalnum()
STORE=OUT/RUN
legacy.STORE=STORE; legacy.PHASE='qualification'
TOOLS=legacy.TOOLS+[
    legacy.schema('lykoi_library','Read only the assigned frozen library or expanded templates. Index or exact relation fetch. No other condition accessible.',
        {'relation':{'type':['string','null']}},['relation']),
    legacy.schema('lykoi_propose','Development only. Propose a reusable typed definition implementing one frozen development relation. Semantics and non-applicability must be explicit. Only identities are mechanically sealed; finite development checks precede reusable admission.',
        {'relation':{'type':'string'},'semantics':{'type':'string'},'non_applicability':{'type':'string'},'definition':{'type':'object'}},
        ['relation','semantics','non_applicability','definition']),
    legacy.schema('lykoi_submit','Evaluation only. Seal complete Entry artifact by immutable pin. First and final submissions preserved. No acceptance feedback. At most three submissions.',
        {'identity':legacy.PIN},['identity'])]

def history():
    path=STORE/'MCP.jsonl'
    return [json.loads(x) for x in path.read_text().splitlines()] if path.exists() else []

def dispatch(name,args):
    assert (OUT/'TASK-FREEZE.json').exists()
    spec=load(STORE/'SESSION.json'); prior=[e for e in history() if e['request']['method']=='tools/call']
    if len(prior)>=36: c.fail('CALL_BUDGET','$','36 MCP calls reached')
    if sum(e['wall_seconds'] for e in prior)>120: c.fail('TOOL_BUDGET','$','120 tool seconds reached')
    if name=='lykoi_execute' and sum(e['request']['params']['name']==name for e in prior)>=12:
        c.fail('EXECUTION_BUDGET','$','twelve selftests reached')
    known=next((t for t in TOOLS if t['name']==name),None)
    if not known: c.fail('ARGUMENT_SCHEMA','$','unknown tool')
    c.shape(args,known['inputSchema']['required'],'$/arguments')
    reg=Registry(STORE/'registry',Journal(STORE/'telemetry'))
    if name=='lykoi_library':
        entries=spec['library']
        if args['relation'] is not None: entries=[e for e in entries if e['relation']==args['relation']]
        return dict(entries=entries,mode=spec['condition'],frozen=True)
    if name=='lykoi_propose':
        if spec['phase']!='discovery': c.fail('PHASE','$','no vocabulary modification during evaluation')
        count=sum(e['request']['params']['name']==name for e in prior)
        if count>=3: c.fail('PROPOSAL_BUDGET','$','three proposals reached')
        if len(spec['library'])+len(list(STORE.glob('ADMITTED-*.json')))>=3:
            c.fail('LIBRARY_BUDGET','$','three accepted entries reached')
        if args['relation']!=spec['relation']: c.fail('RELATION','$','this session has only the supplied development relation')
        if not all(type(args[k]) is str and args[k].strip() for k in ('semantics','non_applicability')):
            c.fail('SEMANTICS','$','explicit semantics and non-applicability required')
        d=args['definition']
        c.shape(d,{'name','revision','params','dependencies','steps','order','result','result_type'},'$/definition')
        d=c.seal(d)
        existing=reg.read()['state']['definitions']
        if sum(len(x['steps']) for x in existing.values())+len(d['steps'])>24:
            c.fail('LIBRARY_BUDGET','$','24 authored library steps')
        # Probe registry is separate: valid-but-functionally-failed candidates cannot enter reusable store.
        probe=Registry(STORE/f'proposal-probe-{count+1}',Journal(STORE/f'proposal-telemetry-{count+1}'))
        if existing: probe.admit(list(existing.values()),probe.read()['token'])
        probe.admit([d],probe.read()['token'])
        checks=[]
        for repeat in range(2):
            fresh=Registry(probe.path)
            checks.append(development_check(d,args['relation'],fresh.retrieve(pin=d['identity']),
                load(OUT/'DEVELOPMENT-EXPECTATIONS.json')[args['relation']]))
        check_path=STORE/f'PROPOSAL-CHECK-{count+1}.json'; save(check_path,normalize(checks))
        if not all(x['passed'] for x in checks):
            c.fail('DEVELOPMENT_BEHAVIOR','$',json.dumps([r['case'] for r in checks[0]['rows'] if not r['passed']][:4]))
        entry=dict(definition=d,relation=args['relation'],semantics=args['semantics'],non_applicability=args['non_applicability'])
        admitted=[load(p) for p in sorted(STORE.glob('ADMITTED-*.json'))]
        if len(c.canonical(spec['library']+admitted+[entry]))>16384: c.fail('LIBRARY_BUDGET','$','16KiB library')
        result=reg.admit([d],reg.read()['token'])
        # Append-only per-entry receipts; ADMITTED is not a mutable vocabulary file.
        save(STORE/f'ADMITTED-{count+1}.json',entry)
        return dict(status='admitted',identity=d['identity'],relation=args['relation'],checks=len(checks[0]['rows']),
            reloads=2,registry=result)
    if name=='lykoi_submit':
        if spec['phase']!='evaluation': c.fail('PHASE','$','submit only in evaluation')
        count=len(list(STORE.glob('SUBMISSION-*.json')))
        if count>=3: c.fail('SUBMISSION_BUDGET','$','three submissions reached')
        p=package(reg,args['identity']); root=p['program']
        if root['name']!='Entry' or root['params'] or root['result_type']!='Int64':
            c.fail('ENTRY','$','Entry() -> Int64 required')
        ex=c.expand(p)
        save(STORE/f'SUBMISSION-{count+1:03}.json',dict(package=p,expansion=ex,root=args['identity']))
        return dict(status='sealed',submission=count+1,identity=args['identity'],acceptance_feedback=False)
    if name=='lykoi_admit' and args['action'].get('action')=='migrate':
        c.fail('PHASE','$','no migration in this construction pilot')
    if name=='lykoi_admit' and spec['phase']=='discovery':
        c.fail('PHASE','$','discovery definitions must use propose for behavioral admission')
    return original_dispatch(name,args)

legacy.TOOLS=TOOLS; legacy.dispatch=dispatch
if __name__=='__main__': legacy.main()
