"""Vocabulary freeze, fresh counterbalanced evaluations and model-free replay."""
import copy
import json
import sys
import time
from datetime import datetime,timezone
from common import ROOT,OUT,Registry,c,save,load,sha,normalize,digest
from development import DEVELOPMENT
from tasks import TASKS,score
from run import ask,GUIDE,verify_freeze

def template(entry,definitions):
    steps=[]
    def region(d,args):
        env=copy.deepcopy(args); by_id={s['id']:s for s in d['steps']}
        for key in d['order']:
            s=by_id[key]; n=s['node']; label='template'+str(len(steps))
            if n['op']=='compose':
                target=definitions[n['identity']]
                expr=region(target,{k:c.substitute(v,env) for k,v in n['args'].items()})
                node=dict(op='value',expr=expr)
                label='template'+str(len(steps))
            else:
                node={k:c.substitute(v,env) if k in ('expr','test','site') else v for k,v in n.items()}
            used=set()
            def refs(v):
                if isinstance(v,dict):
                    if set(v)=={'ref'}: used.add(v['ref'])
                    else:
                        for x in v.values(): refs(x)
                elif isinstance(v,list):
                    for x in v: refs(x)
            refs(node)
            steps.append(dict(id=label,type=s['type'],deps=sorted(used),node=node))
            env[key]={'ref':label}
        return c.substitute(d['result'],env)
    d=entry['definition']; result=region(d,{p['name']:{'ref':p['name']} for p in d['params']})
    return dict(relation=entry['relation'],params=d['params'],result_type=d['result_type'],steps=steps,
        order=[s['id'] for s in steps],result=result,semantics=entry['semantics'],
        non_applicability=entry.get('non_applicability','Different domain/order/error codes/formula require a different composition'),
        symbolic_reference_available=False)

def depth(d,ds):
    return 1+max([depth(ds[p],ds) for p in d['dependencies'].values()] or [0])

def freeze_vocabulary():
    verify_freeze(); entries=[]; proposals=[]
    for t in DEVELOPMENT:
        folder=OUT/t['id']
        entries += [load(p) for p in sorted(folder.glob('ADMITTED-*.json'))]
        for line in (folder/'MCP.jsonl').read_text().splitlines():
            e=json.loads(line)
            if e['request']['method']=='tools/call' and e['request']['params']['name']=='lykoi_propose':
                proposals.append(dict(session=t['id'],request=e['request'],response=e['response'],seconds=e['wall_seconds']))
    assert len(entries)<=3 and len(proposals)<=9
    pool=load(OUT/'B-PROXY-POOL.json')['entries']; selected=[]; matches=[]
    ds={e['definition']['identity']:e['definition'] for e in entries}
    for e in entries:
        candidate=next(p for p in pool if p['relation']==e['relation'])
        d,b=e['definition'],candidate['definition']
        valid=(d['params']==b['params'] and d['result_type']==b['result_type']
            and abs(len(d['steps'])-len(b['steps']))<=max(1,0.1*len(d['steps']))
            and depth(d,ds)==1)
        matches.append(dict(relation=e['relation'],matched=valid,AI_steps=len(d['steps']),proxy_steps=len(b['steps']),
            AI_depth=depth(d,ds),proxy_depth=1))
        selected.append(dict(candidate,non_applicability='Different domain/order/error codes/formula require a different composition'))
    templates=[template(e,ds) for e in entries]
    save(OUT/'PROPOSALS.json',proposals)
    save(OUT/'C-VOCABULARY.json',dict(entries=entries,identities=sorted(ds),frozen=True))
    save(OUT/'B-VOCABULARY.json',dict(entries=selected,human_authored=False,owner_authorized_AI_proxy=True,
        matches=matches,capacity_matched=all(m['matched'] for m in matches)))
    save(OUT/'X-TEMPLATES.json',dict(entries=templates,source_identities=sorted(ds),no_compact_pins=True))
    paths=[OUT/p for p in ['PROPOSALS.json','C-VOCABULARY.json','B-VOCABULARY.json','X-TEMPLATES.json']]
    paths += [p for t in DEVELOPMENT for p in (OUT/t['id']).rglob('*.json')]
    paths += [OUT/t['id']/'MCP.jsonl' for t in DEVELOPMENT]
    save(OUT/'VOCABULARY-FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),evaluation_calls=0,
        inputs={p.relative_to(ROOT).as_posix():sha(p) for p in paths},proposed=len(proposals),admitted=len(entries),
        no_discovery=not entries))
    print('Vocabulary frozen:',len(proposals),'proposals;',len(entries),'admitted;',len(selected),'B-proxy entries')

def entries(condition):
    return [] if condition=='A' else load(OUT/({'B':'B-VOCABULARY.json','C':'C-VOCABULARY.json','X':'X-TEMPLATES.json'}[condition]))['entries']

def index(library):
    rows=[]
    for e in library:
        d=e.get('definition',e)
        rows.append(dict(relation=e['relation'],name=d.get('name'),identity=d.get('identity'),params=d['params'],
            result_type=d['result_type'],semantics=e['semantics'],non_applicability=e.get('non_applicability')))
    return rows

def evaluate(task_id):
    verify_freeze()
    for name,pin in load(OUT/'VOCABULARY-FREEZE.json')['inputs'].items(): assert sha(ROOT/name)==pin,name
    t=next(t for t in TASKS if t['id']==task_id)
    for condition in t['order']:
        folder=OUT/(task_id+'-'+condition); folder.mkdir(exist_ok=False)
        library=entries(condition); reg=Registry(folder/'registry')
        if condition in ('B','C') and library: reg.admit([e['definition'] for e in library],reg.read()['token'])
        save(folder/'SESSION.json',dict(phase='evaluation',condition=condition,library=library))
        prompt=GUIDE+'\nRequirement: '+t['requirement']+'\nAll additions are checked Int64. Construct Entry()->Int64 and emit UInt16BE. '
        prompt+='Use assigned library only if appropriate. Task-local definitions are permitted but never enter reusable vocabulary. '
        prompt+='Read-only assigned library index: '+json.dumps(index(library),sort_keys=True)
        prompt+='\nFetch full assigned definitions/templates using lykoi_library(relation). A has an empty reusable library. '
        prompt+='Expanded templates provide underlying primitive steps for inlining; they have no reusable pins. '
        prompt+='Use actual admission/validation tools; selftest only author-chosen inputs (max12). Seal first complete candidate with lykoi_submit. '
        prompt+='You may self-correct and seal up to two more submissions. No acceptance feedback will be given. Stop after final submission.'
        rec=ask(task_id+'-'+condition,prompt)
        save(folder/'CLOSED.json',dict(provider_halt=rec['returncode']!=0 or rec['timeout'] or bool(rec['errors']),
            budget_exceeded=rec['token_cap_exceeded'] or rec['budget_stop'],submissions=len(list(folder.glob('SUBMISSION-*.json'))),
            coordinator_semantic_repairs=0))

def score_all(replay=False):
    results={}
    for t in TASKS:
        for condition in ['A','B','C','X']:
            folder=OUT/(t['id']+'-'+condition)
            if not folder.exists():
                results[t['id']+'-'+condition]=dict(status='NOT_REACHED'); continue
            submissions=sorted(folder.glob('SUBMISSION-*.json')); scores=[]
            for i,p in enumerate(submissions):
                s=load(p); started=time.perf_counter()
                try:
                    result=normalize(score(Registry(folder/'registry'),s['root'],t,load(OUT/(t['id']+'-EXPECTATIONS.json'))))
                    assert result['expansion']==s['expansion']
                except (AssertionError,c.Diagnostic,ValueError) as exc:
                    result=dict(all_passed=False,passed=0,total=0,error=str(exc),wall_seconds=time.perf_counter()-started)
                target=folder/(('REPLAY-' if replay else 'ACCEPTANCE-')+str(i+1)+'.json')
                if replay:
                    original=load(folder/('ACCEPTANCE-'+str(i+1)+'.json'))
                    result['exact_match']=all(result.get(k)==original.get(k) for k in ('rows','expansion','root','closure','error'))
                    assert result['exact_match']
                save(target,result); scores.append(result)
            results[t['id']+'-'+condition]=dict(status='SCORED' if scores else 'NO_SUBMISSION',
                first_passed=bool(scores and scores[0]['all_passed']),final_passed=bool(scores and scores[-1]['all_passed']),
                observations=scores[-1]['total'] if scores else 0,passed=scores[-1]['passed'] if scores else 0,
                first_root=scores[0].get('root') if scores else None,final_root=scores[-1].get('root') if scores else None)
    save(OUT/('REPLAY.json' if replay else 'RESULTS.json'),dict(model_calls=0,results=results))
    print(json.dumps(results,indent=2))

if __name__=='__main__':
    if sys.argv[1]=='freeze': freeze_vocabulary()
    elif sys.argv[1]=='score': score_all()
    elif sys.argv[1]=='replay': score_all(True)
    else: evaluate(sys.argv[1])
