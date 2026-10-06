"""Fixed exposed transfer after the verified generic implementation lock.

Only source captures and literal external plans change here. No product repair.
"""
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, OUT / filename)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


generic = load('r104_pins', 'R5_104-generic.py')
old = load('r103_source_builder', 'R5_103-corpus.py')
old_plans = load('r103_literal_plans', 'R5_103-plans.py')
evaluator = load('r104_evaluator', 'R5_103-evaluate.py')
PROFILE = 'typed-mutable-values-1'


def captures():
    records = old.captures()
    for r in records:
        case = r['id']
        r['capture_round'] = 'R5.104 source reexpression after generic lock'
        if case not in ('B02', 'B03', 'B06', 'B07', 'B10'):
            r['capture_note'] = 'R5.103 current typed vocabulary remains faithful; exact sources reloaded and demands retained'
            continue
        prior_rows = copy.deepcopy(r['rows'])
        r['rows'] = []
        r['domains'] = dict(evaluation_scope='requirement-local against canonical scalar baseline; no cumulative success claim',
            capability_profile=PROFILE, scalar_base_model=copy.deepcopy(old.MODEL), baseline_model_sha256=hashlib.sha256((ROOT/'air/task_manager.json').read_bytes()).hexdigest())
        def add(facet, value, profile='existing-scalar-1'):
            r['rows'].append(dict(id=case+'/'+facet, basis='STATED', derived_from=[], source_quote=r['source'], statement='R5.104 source-authorized '+facet,
                relation=dict(kind='crud', parameters=dict(profile=profile, facet=facet, value=copy.deepcopy(value)))))
        f = old.scalar_facts(); f['storage']['version'] = 4
        collections, mutations, pipelines = [], [], []
        if case in ('B02', 'B03'):
            collections = [dict(name='tags', element=dict(type='string', domain=[]), ordering='insertion', duplicates='unique', equality='exact',
                creation=dict(input='tag', encoding='repeated', default=[], pipeline=[dict(kind='map_elements',pipeline=[dict(kind='transform',operation='trim'),dict(kind='validate',rule='nonempty',error='invalid_tag')]),dict(kind='transform',operation='stable_deduplicate')],error='invalid_tag'),
                migration=[{'from':3,'to':4,'value':[]}])]
        elif case in ('B06', 'B10'):
            name = 'category' if case == 'B06' else 'owner'
            f['fields'].append(dict(name=name, type='string', domain=[], nullable=False, preservation='verbatim'))
            f['creation']['bindings'].append(dict(field=name, source='input', value=None, default=dict(value='', trigger='omitted', boundary='creation')))
            f['evolution'].append(dict(**{'from':3,'to':4}, defaults={name:''}, boundary='explicit_migration', preservation='unrelated_fields'))
            pipeline = [dict(kind='transform', operation='trim')]
            if case == 'B10': pipeline.append(dict(kind='validate', rule='nonempty', error='invalid_owner'))
            pipelines = [dict(field=name, pipeline=pipeline, error='invalid_'+name)]
        else:
            # Do not fabricate a create --notes input: source requires literal []
            # initialization and authorizes only append-note as its write interface.
            f['storage']['version'] = 3
            # No application missing-text error is invented from the blank-text
            # error. The legacy required-CLI-input refusal is a separate profile
            # seam, retained with the source demand below.
            mutations = []
        for facet, value in f.items(): add(facet,value)
        for facet, value in dict(collections=collections, mutations=mutations, creation_pipelines=pipelines).items(): add(facet,value,PROFILE)
        if case in ('B03','B06','B10'):
            r['domains']['collection_store'] = dict(kind='composed_scalar',state='state_tasks')
            r['rows'] += [o for o in prior_rows if o['relation']['kind']=='filter_order']
        if case == 'B06':
            r['rows'].append(dict(id='B06/raw-empty-validation-authority',basis='STATED',derived_from=[],source_quote=(ROOT/'benchmark/requirements/B06.md').read_text(encoding='utf-8'),
                statement='Explicit raw empty accepted; supplied nonempty input trimmed then rejected if empty',relation=dict(kind='invariant',parameters=dict(required_capability='presence_and_raw_value_conditional_validation',specification={'raw_empty':'accept_empty','raw_nonempty':['trim','validate_nonempty'],'error':'invalid_category','rejection':'unchanged'}))))
        if case == 'B07':
            r['rows'] += prior_rows
            r['rows'].append(dict(id='B07/literal-collection-initialization',basis='STATED',derived_from=[],source_quote=(ROOT/'benchmark/requirements/B07.md').read_text(encoding='utf-8'),
                statement='Ordered duplicate-permitted string collection notes initialized literally empty on create and explicit migration, with no creation input invented',
                relation=dict(kind='crud',parameters=dict(required_capability='literal_collection_creation_binding',specification=dict(field='notes',element='string',ordering='insertion',duplicates='allow',equality='exact',creation_literal=[],migration_default=[])))))
            r['capture_note']='Generic append/trim/atomic semantics work synthetically, but literal collection creation and required CLI-input binding remain outside the frozen profile; source demand retained without guessed error'
    return records


def plan(r):
    if r['id'] not in ('B02','B03','B10'): return old_plans.plan(r)
    case = r['id']; ids = [o['id'] for o in r['rows']]
    field = 'owner' if case == 'B10' else 'tags'
    def task(identity, value, status='pending', priority='NORMAL', due=None):
        return dict(id=identity,title=identity,description='  preserved  ',status=status,priority=priority,created_at='2020-01-01T00:00:00Z',due_date=due,**{field:value})
    def step(argv, expected=None, error=None, preserve=True, contains=None):
        s = dict(argv=argv,returncode=1 if error else 0,contains=contains or [])
        if preserve: s['preserved']=['tasks.json']
        if error: s.update(stderr_json={'error':error},stdout_exact='')
        else:
            s['stderr_exact']=''
            if expected is not None: s['stdout_json']=copy.deepcopy(expected)
        return s
    def scenario(name,payload,steps):
        c=dict(id=name,obligations=ids,initial_state='fresh_directory',initial_files=[] if payload is None else [dict(path='tasks.json',json=payload)],steps=steps,
            invariants=['Whole-record results and state-preserving rejected/read operations'],transitions='Independent processes reload declared store',rejections='Source-declared errors')
        c['identity']=hashlib.sha256(evaluator.canonical(c)).hexdigest(); return c
    def fixture(rows): return dict(schema_version=4,records=rows)
    a = task('a','Work' if case=='B10' else ['Work','home'],priority='HIGH')
    b = task('b','work' if case=='B10' else ['work'],status='completed')
    empty = task('c','' if case=='B10' else [])
    cases=[]
    if case=='B10':
        cases.append(scenario('trim-owner-and-presence',None,[
            step(['create','--title','owned','--description','kept','--owner','  Work  '],preserve=False,contains=['"owner": "Work"']),
            step(['create','--title','unowned','--description','kept'],preserve=False,contains=['"owner": ""']),
            step(['create','--title','rejected','--description','kept','--owner',''],error='invalid_owner'),
            step(['create','--title','rejected','--description','kept','--owner','   '],error='invalid_owner'),
            step(['list'],contains=['owned','unowned','"owner": "Work"'])]))
    else:
        cases.append(scenario('typed-tags-creation',None,[
            step(['create','--title','tagged','--description','kept','--tag',' Work ','--tag','home','--tag','Work','--tag','work'],preserve=False,contains=['"tags": ["Work", "home", "work"]']),
            step(['create','--title','omitted','--description','kept'],preserve=False,contains=['"tags": []']),
            step(['create','--title','bad','--description','kept','--tag',''],error='invalid_tag'),
            step(['create','--title','bad','--description','kept','--tag','   '],error='invalid_tag'),
            step(['list'],contains=['tagged','omitted','"tags": ["Work", "home", "work"]'])]))
    if case in ('B03','B10'):
        command,param = ('list-owner','owner') if case=='B10' else ('list-tag','tag')
        tests=[('Work',[a]),('work',[b]),(' Work ',[]),('missing',[])]
        if case=='B10': tests.append(('',[empty]))
        steps=[step([command,'--'+param,v],expected) for v,expected in tests]
        if case=='B03': steps += [step([command,'--tag',v],error='invalid_tag') for v in ('','  ')]
        cases.append(scenario('exact-readonly-query',fixture([empty,b,a]),steps))
    completed={**a,'status':'completed'}
    cases.append(scenario('baseline-composition',fixture([b,a]),[
        step(['list'],[a,b]),step(['list-high'],[a]),step(['list-overdue'],[]),
        step(['complete','--id','a'],completed,preserve=False),step(['complete','--id','a'],error='invalid_transition'),
        step(['delete','--id','a'],completed,preserve=False),step(['list'],[b]),
        step(['complete','--id','absent'],error='task_not_found')]))
    older={k:v for k,v in a.items() if k!=field}; migrated={**older,field:'' if case=='B10' else []}
    cases.append(scenario('explicit-additive-migration',dict(schema_version=3,records=[older]),[
        step(['list'],error='migration_required'),step(['migrate'],{'migrated':1},preserve=False),step(['list'],[migrated]),step(['migrate'],{'migrated':0})]))
    legacy={k:v for k,v in older.items() if k not in ('priority','due_date')}
    legacy_migrated={**legacy,'priority':'NORMAL','due_date':None,field:'' if case=='B10' else []}
    cases.append(scenario('legacy-migration-preservation',[legacy],[step(['migrate'],{'migrated':1},preserve=False),step(['list'],[legacy_migrated])]))
    cases.append(scenario('invalid-state',fixture([{'id':'bad'}]),[step(['list'],error='invalid_state')]))
    cases.append(scenario('missing-store',None,[step(['list'],[])]))
    return dict(version='external-cli-plan-1',outcome='READY',producer='R5.104 source-first literal external oracle',source_sha256=hashlib.sha256(r['source'].encode()).hexdigest(),cases=cases,
        coverage=[dict(obligation=oid,classification='EXERCISED',justification='Source-derived typed values, query, baseline and explicit migration checks',cases=[c['identity'] for c in cases]) for oid in ids],
        limitations=['Same-agent source/oracle and synthetic owner; requirement-local exposed regression, not cumulative or held-out'])


def main():
    lock=json.loads((OUT/'R5_104-GENERIC-LOCK.json').read_text(encoding='utf-8'))
    assert generic.implementation_pins()==lock['implementation'] and generic.history_pins()==lock['history']
    records=captures(); plans={r['id']:plan(r) for r in records}
    for r in records: generic.publish('R5_104-'+r['id']+'-CANDIDATE.json',dict(case=r['id'],producer_capture=r,external_plan=plans[r['id']]))
    corpus_pins={r['id']:hashlib.sha256((OUT/('R5_104-'+r['id']+'-CANDIDATE.json')).read_bytes()).hexdigest() for r in records}
    generic.publish('R5_104-CORPUS-LOCK.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cases=corpus_pins,implementation_lock_sha256=hashlib.sha256((OUT/'R5_104-GENERIC-LOCK.json').read_bytes()).hexdigest(),rule='All captures and source-side plans fixed before the first transfer execution'))
    results=[]
    for r in records:
        row=evaluator.evaluate(r,plans[r['id']]); results.append(row)
        print(row['case'],row['first_blocker'],row['native'],flush=True)
    assert generic.implementation_pins()==lock['implementation'] and generic.history_pins()==lock['history']
    baseline=json.loads((OUT/'R5_103-FINAL-EVIDENCE.json').read_text(encoding='utf-8'))
    before={r['case']:r for r in baseline['cases']}
    comparison=[]
    for r in results:
        b=before[r['case']]
        comparison.append(dict(case=r['case'],r5_103_first_blocker=b['first_blocker'],r5_104_first_blocker=r['first_blocker'],
            newly_reached=[s for s in evaluator.STAGES if b['stages'][s]=='NOT_REACHED' and r['stages'][s]!='NOT_REACHED'],behaviorally_verified=r['first_blocker']=='SUCCESS',stages=r['stages'],native=r['native'],
            next_blocker=None if r['first_blocker']=='SUCCESS' else r.get('terminal',{}).get('failure',r['native'])))
    distribution={k:sum(r['first_blocker']==k for r in results) for k in ('FORMALIZATION','STRUCTURAL','BDI','ADEQUACY','REPRESENTATION','AUTHORING','COMPILATION','RUNTIME','BEHAVIORAL_VERIFICATION','SUCCESS')}
    generic.publish('R5_104-TRANSFER-EVIDENCE.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Fixed exposed requirement-local transfer; no held-out generalization or cumulative achievement',implementation_unchanged=True,history_unchanged=True,distribution=distribution,cases=results))
    generic.publish('R5_104-COMPARISON.json',dict(distribution=distribution,cases=comparison,external_invocations=sum(r.get('external_invocations',0) for r in results)))
    lines=['# R5.104 — fixed exposed transfer matrix','','R5.103 remains the pre-R5.104 baseline. No held-out/cumulative achievement claim.','',
        '| Case | R5.103 first blocker | R5.104 first blocker | Newly reached stages | Externally verified |','| --- | --- | --- | --- | --- |']
    for r in comparison: lines.append('| '+r['case']+' | '+r['r5_103_first_blocker']+' | '+r['r5_104_first_blocker']+' | '+(', '.join(r['newly_reached']) or 'None')+' | '+('Yes' if r['behaviorally_verified'] else 'No')+' |')
    lines += ['', 'See `R5_104-COMPARISON.json` for every stage and exact next native blocker; `R5_104-TRANSFER-EVIDENCE.json` retains full source/reconciliation/audit/external observations.']
    with (OUT/'R5_104-CAPABILITY-MATRIX.md').open('x',encoding='utf-8',newline='\n') as stream: stream.write('\n'.join(lines)+'\n')


if __name__=='__main__': main()
