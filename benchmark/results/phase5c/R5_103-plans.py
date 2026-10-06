"""Fresh source-side literal external oracles, prepared before authoring."""
import hashlib
from lykoi_pipeline.controller import digest
from lykoi_pipeline.plans import VERSION


def plan(record):
    case=record['id']
    if case not in ('B01','B04','B05'): return None
    ids=[o['id'] for o in record['rows']]
    version=4 if case=='B04' else 3
    def task(identity,priority='NORMAL',status='pending',due=None):
        t=dict(id=identity,title=identity,description='  unchanged  ',status=status,priority=priority,created_at='2026-01-01T00:00:00Z',due_date=due)
        if case=='B04': t['source']='  supplied verbatim  '
        return t
    def step(argv,expected=None,error=None,preserve=True,contains=None,absent=None):
        s=dict(argv=argv,returncode=1 if error else 0,contains=contains or [],preserved=['tasks.json'] if preserve else [],absent=absent or [])
        if expected is not None or error: s['stderr_json' if error else 'stdout_json']={'error':error} if error else expected
        s['stdout_exact' if error else 'stderr_exact']=''
        return s
    def scenario(name,payload,steps):
        c=dict(id=name,obligations=ids,initial_state='fresh_directory',initial_files=[] if payload is None else [dict(path='tasks.json',json=payload)],steps=steps,invariants=['Exact whole records; rejected/read bytes or absence unchanged'],transitions='Declared baseline lifecycle',rejections='Source-authorized error envelopes')
        c['identity']=digest(c); return c
    def fixture(rows): return dict(schema_version=version,records=rows)
    a,b,c=task('a','LOW'),task('b','HIGH'),task('c','NORMAL','completed')
    cases=[]
    if case=='B01':
        critical=task('d','CRITICAL','completed'); current=[a,b,c,critical]
        cases += [scenario('enum-partition',fixture(list(reversed(current))),[
            step(['list'],current),step(['list-high'],[b]),step(['list-overdue'],[]),step(['migrate'],{'migrated':0}),
            step(['create','--title','new critical','--description','  exact  ','--priority','CRITICAL'],preserve=False,contains=['"priority": "CRITICAL"','  exact  ']),
            step(['create','--title','default','--description','kept'],preserve=False,contains=['"priority": "NORMAL"']),
            step(['list'],contains=['new critical','default','CRITICAL'])])]
        old=[{k:v for k,v in t.items() if k!='due_date'} for t in (a,b,c)]
        migrated=[{**t,'due_date':None} for t in old]
        cases += [scenario('old-values-preserved',dict(schema_version=2,records=old),[
            step(['list'],error='migration_required'),step(['migrate'],{'migrated':3},preserve=False),step(['list'],migrated),step(['migrate'],{'migrated':0})])]
        legacy={k:v for k,v in a.items() if k not in ('priority','due_date')}
        cases += [scenario('missing-priority-authorized-baseline-migration',[legacy],[step(['migrate'],{'migrated':1},preserve=False),step(['list'],[{**legacy,'priority':'NORMAL','due_date':None}])])]
    elif case=='B04':
        completed={**a,'status':'completed'}
        cases += [scenario('verbatim-creation',None,[
            step(['create','--title','supplied','--description','kept','--source','  supplied verbatim  '],preserve=False,contains=['  supplied verbatim  ']),
            step(['create','--title','omitted','--description','kept'],preserve=False,contains=['"source": ""']),
            step(['create','--title','empty','--description','kept','--source',''],preserve=False,contains=['"source": ""']),
            step(['list'],contains=['supplied','omitted','empty','  supplied verbatim  ']),
            step(['create','--title','  ','--description','bad','--source','bad'],error='invalid_title')]),
            scenario('all-reads-mutations',fixture([b,a]),[step(['list'],[a,b]),step(['list-high'],[b]),step(['list-overdue'],[]),
                step(['complete','--id','a'],completed,preserve=False),step(['complete','--id','a'],error='invalid_transition'),step(['delete','--id','a'],completed,preserve=False),step(['list'],[b])])]
        old={k:v for k,v in a.items() if k!='source'}
        cases += [scenario('source-migration',dict(schema_version=3,records=[old]),[step(['list'],error='migration_required'),step(['migrate'],{'migrated':1},preserve=False),step(['list'],[{**old,'source':''}]),step(['migrate'],{'migrated':0})])]
    else:
        current=[a,b,c]
        cases += [scenario('status-partition',fixture([c,b,a]),[step(['list-status','--status','pending'],[a,b]),step(['list-status','--status','completed'],[c]),step(['list'],current)]),
                  scenario('empty',fixture([]),[step(['list-status','--status','pending'],[]),step(['list-status','--status','completed'],[])]),
                  scenario('no-match',fixture([a]),[step(['list-status','--status','completed'],[])])]
    missing_commands=['list-status','--status','completed'] if case=='B05' else ['list']
    cases += [scenario('missing-store',None,[step(missing_commands,[])]),
              scenario('invalid-state',fixture([{'id':'bad'}]),[step(missing_commands,error='invalid_state')])]
    if case!='B05':
        cases += [scenario('baseline-rejections',fixture([a]),[step(['complete','--id','absent'],error='task_not_found'),step(['delete','--id','absent'],error='task_not_found'),step(['create','--title','bad due','--description','kept','--due-date','invalid'],error='invalid_due_date')])]
    return dict(version=VERSION,outcome='READY',producer='R5.103-fresh-source-side-literal-oracle',source_sha256=hashlib.sha256(record['source'].encode()).hexdigest(),cases=cases,
        coverage=[dict(obligation=oid,classification='EXERCISED',justification='Source-derived enum/default/verbatim/query/migration/baseline regression observations',cases=[c['identity'] for c in cases]) for oid in ids],
        limitations=['Same-agent finite source-side oracle and synthetic owner authority; not independent cognition or cumulative achievement'])
