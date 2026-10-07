"""Fresh source captures and fixed plans after generic closure; no product edits."""
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

from lykoi_pipeline import mutable_profile
from lykoi_workspace.input_corpus import parameters, explicit, staged

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name, filename):
    s = importlib.util.spec_from_file_location(name, OUT / filename)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


generic = load('pins105', 'R5_105-generic.py')
prior = load('capture104', 'R5_104-transfer.py')
ev = load('evaluate105', 'R5_103-evaluate.py')


def captures():
    # Every source bundle is read freshly by the source builder, not a saved FRC
    # replay. Unchanged authoritative demands remain beyond this bounded profile.
    records = prior.captures()
    for r in records:
        r['capture_round'] = 'R5.105 fresh current typed source interpretation after generic lock 2'
        r['capture_note'] = 'Exact frozen source bundle freshly read; current typed facts and unsupported demands retained; source authority unchanged'
        if r['id'] not in ('B02','B03','B06','B07','B10'):
            continue
        rows = r['rows']
        def fact(facet):
            return next(o['relation']['parameters']['value'] for o in rows if o['relation']['parameters'].get('facet') == facet)
        f = {facet:copy.deepcopy(fact(facet)) for facet in mutable_profile.scalar.FACETS}
        m = {facet:copy.deepcopy(fact(facet)) for facet in mutable_profile.FACETS}
        r['rows'] = [o for o in rows if o['relation']['parameters'].get('profile') == 'existing-scalar-1' or o['relation']['kind'] == 'filter_order']
        if r['id'] == 'B06':
            m['creation_pipelines'][0]['pipeline'] = [dict(kind='transform',operation='trim'), staged(stage='TRANSFORMED',predicate='nonempty',error='invalid_category')]
        if r['id'] == 'B07':
            f['storage']['version'] = 4
            for o in r['rows']:
                if o['relation']['parameters'].get('facet') == 'storage': o['relation']['parameters']['value']['version'] = 4
            m['collections'] = [dict(name='notes',element=dict(type='string',domain=[]),ordering='insertion',duplicates='allow',equality='exact',
                creation=dict(source='literal',value=[]),migration=[{'from':3,'to':4,'value':[]}])]
            # CLI-required text has external rejection authority, not an invented
            # application error. The temporary builder value is never published.
            m['mutations'] = [dict(command='append-note',lookup='id',missing_error='task_not_found',
                changes=[dict(field='notes',input='text',operation='append',omitted='reject',missing_error='builder_only',
                    pipeline=[dict(kind='transform',operation='trim'),staged(stage='TRANSFORMED',error='invalid_note')],invalid_error='invalid_note')],
                guards=[],effect=dict(atomicity='single_record',persistence='atomic',rejection='unchanged'))]
        for c in m['collections']:
            explicit(c['creation'].get('pipeline',[]))
        for c in m['creation_pipelines']:
            # B06's conditional stage was explicitly authored above.
            if r['id'] != 'B06': explicit(c['pipeline'])
        for op in m['mutations']:
            for w in op['changes']: explicit(w['pipeline'])
        sf = copy.deepcopy(f); sf['storage']['version'] = max([1]+[x['to'] for x in sf['evolution']])
        base = mutable_profile.scalar.lower(sf)
        m['input_contracts'] = parameters(base,m)
        for p in m['input_contracts']:
            if p['presence'] == 'required': p['missing'] = dict(kind='cli_rejection')
        if r['id'] == 'B07': m['mutations'][0]['changes'][0]['missing_error'] = None
        for facet,value in m.items():
            r['rows'].append(dict(id=r['id']+'/'+facet,basis='STATED',derived_from=[],source_quote=r['source'],statement='R5.105 source-authorized '+facet,
                relation=dict(kind='crud',parameters=dict(profile=mutable_profile.PROFILE,facet=facet,value=value))))
        r['domains']['input_value_profile'] = 'typed-input-values-1'
        r['interpretation_notes'] = ['Required CLI notation authorizes missing-input external rejection only; no application missing-input identity invented.',
            'Normal closure stages/conditions and literal/input/default distinctions are source-derived; no new precursor family is presumed.']
    return records


def plan(r):
    if r['id'] not in ('B06','B07'):
        return prior.plan(r)
    case = r['id']; field = 'category' if case == 'B06' else 'notes'; ids = [o['id'] for o in r['rows']]
    def task(identity,value,status='pending',priority='NORMAL'):
        return dict(id=identity,title=identity,description='  preserved  ',status=status,priority=priority,created_at='2020-01-01T00:00:00Z',due_date=None,**{field:value})
    def fixture(rows): return dict(schema_version=4,records=rows)
    def step(argv,expected=None,error=None,preserve=True,contains=None):
        s=dict(argv=argv,returncode=1 if error else 0,contains=contains or [])
        if preserve: s['preserved']=['tasks.json']
        if error: s.update(stdout_exact='',stderr_json={'error':error})
        else:
            s['stderr_exact']=''
            if expected is not None: s['stdout_json']=copy.deepcopy(expected)
        return s
    def scenario(name,payload,steps):
        c=dict(id=name,obligations=ids,initial_state='fresh_directory',initial_files=[] if payload is None else [dict(path='tasks.json',json=payload)],steps=steps,
            invariants=['Exact whole records, atomic rejection and readonly byte preservation'],transitions='Independent subprocess reload',rejections='Source-authorized errors and required CLI-input rejection')
        c['identity']=hashlib.sha256(ev.canonical(c)).hexdigest(); return c
    a=task('a','Work' if case=='B06' else [],priority='HIGH'); b=task('b','work' if case=='B06' else ['Old'],status='completed')
    cases=[]
    if case=='B06':
        cases.append(scenario('stage-sensitive-creation',None,[
            step(['create','--title','trimmed','--description','kept','--category','  Work  '],preserve=False,contains=['"category": "Work"']),
            step(['create','--title','omitted','--description','kept'],preserve=False,contains=['"category": ""']),
            step(['create','--title','raw-empty','--description','kept','--category',''],preserve=False,contains=['"category": ""']),
            step(['create','--title','bad','--description','kept','--category','   '],error='invalid_category'),
            step(['create','--title','bad','--description','kept','--category','\t'],error='invalid_category'),
            step(['list'],contains=['trimmed','omitted','raw-empty']),
            step(['list-category','--category',''],contains=['omitted','raw-empty'])]))
        empty=task('c','')
        cases.append(scenario('exact-category-query',fixture([empty,b,a]),[step(['list-category','--category',v],expected) for v,expected in [('Work',[a]),('work',[b]),('',[empty]),(' Work ',[]),('   ',[]),('missing',[])]]))
    else:
        cases.append(scenario('literal-initialization',None,[
            step(['create','--title','literal','--description','kept'],preserve=False,contains=['"notes": []']),step(['list'],contains=['"notes": []','literal'])]))
        current=copy.deepcopy(a); steps=[]
        for raw,stored in [(' B ','B'),('A','A'),('B','B'),('b','b')]:
            current['notes'].append(stored); steps.append(step(['append-note','--id','a','--text',raw],current,preserve=False))
        steps += [step(['list'],[current,b]),step(['append-note','--id','a','--text',''],error='invalid_note'),
            step(['append-note','--id','a','--text','   '],error='invalid_note'),step(['append-note','--id','a','--text','\t'],error='invalid_note'),
            step(['append-note','--id','absent','--text','X'],error='task_not_found'),
            dict(argv=['append-note','--id','a'],returncode=2,contains=[],stdout_exact='',stderr_exact='missing required input: --text\n',preserved=['tasks.json'])]
        completed={**current,'status':'completed'}
        steps += [step(['complete','--id','a'],completed,preserve=False),step(['append-note','--id','a','--text',' After '],{**completed,'notes':completed['notes']+['After']},preserve=False)]
        cases.append(scenario('ordered-atomic-append',fixture([b,a]),steps))
    complete={**a,'status':'completed'}
    cases.append(scenario('baseline-composition',fixture([b,a]),[
        step(['list'],[a,b]),step(['list-high'],[a]),step(['list-overdue'],[]),step(['complete','--id','a'],complete,preserve=False),
        step(['complete','--id','a'],error='invalid_transition'),step(['delete','--id','a'],complete,preserve=False),step(['list'],[b])]))
    older={k:v for k,v in a.items() if k!=field}; migrated={**older,field:'' if case=='B06' else []}
    cases.append(scenario('explicit-additive-migration',dict(schema_version=3,records=[older]),[
        step(['list'],error='migration_required'),step(['migrate'],{'migrated':1},preserve=False),step(['list'],[migrated]),step(['migrate'],{'migrated':0})]))
    legacy={k:v for k,v in older.items() if k not in ('priority','due_date')}; result={**legacy,'priority':'NORMAL','due_date':None,field:'' if case=='B06' else []}
    cases.append(scenario('legacy-migration',[legacy],[step(['migrate'],{'migrated':1},preserve=False),step(['list'],[result])]))
    cases += [scenario('invalid-state',fixture([{'id':'bad'}]),[step(['list'],error='invalid_state')]),scenario('missing-store',None,[step(['list'],[])])]
    return dict(version='external-cli-plan-1',outcome='READY',producer='R5.105 source-first literal oracle',source_sha256=hashlib.sha256(r['source'].encode()).hexdigest(),cases=cases,
        coverage=[dict(obligation=oid,classification='EXERCISED',justification='Source-derived input stages, literals, append/query, migration and baseline observations',cases=[c['identity'] for c in cases]) for oid in ids],
        limitations=['Same-agent interpretation/inventory/oracle and synthetic owner approval; exposed requirement-local regression, not cumulative/held-out'])


def main():
    lock_path=OUT/'R5_105-GENERIC-LOCK-2.json'; lock=json.loads(lock_path.read_text(encoding='utf-8'))
    assert generic.implementation_pins()==lock['implementation'] and generic.history_pins()==lock['history']
    records=captures(); plans={r['id']:plan(r) for r in records}
    for r in records:
        generic.publish('R5_105-'+r['id']+'-CANDIDATE.json',dict(case=r['id'],producer_capture=r,external_plan=plans[r['id']]))
    generic.publish('R5_105-CORPUS-LOCK.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
        cases={r['id']:hashlib.sha256((OUT/('R5_105-'+r['id']+'-CANDIDATE.json')).read_bytes()).hexdigest() for r in records},
        implementation_lock_sha256=hashlib.sha256(lock_path.read_bytes()).hexdigest(),rule='All twenty captures/plans fixed before first transfer outcome'))
    results=[]
    for r in records:
        x=ev.evaluate(r,plans[r['id']]); results.append(x); print(x['case'],x['first_blocker'],x['native'],flush=True)
    assert generic.implementation_pins()==lock['implementation'] and generic.history_pins()==lock['history']
    before={x['case']:x for x in json.loads((OUT/'R5_104-TRANSFER-EVIDENCE.json').read_text(encoding='utf-8'))['cases']}
    comparison=[dict(case=x['case'],r5_104_first_blocker=before[x['case']]['first_blocker'],r5_105_first_blocker=x['first_blocker'],native=x['native'],
        newly_reached=[s for s in ev.STAGES if before[x['case']]['stages'][s]=='NOT_REACHED' and x['stages'][s]!='NOT_REACHED'],
        stages=x['stages'],behaviorally_verified=x['first_blocker']=='SUCCESS',next_blocker=None if x['first_blocker']=='SUCCESS' else x.get('terminal',{}).get('failure',x['native'])) for x in results]
    distribution={k:sum(x['first_blocker']==k for x in results) for k in ('FORMALIZATION','STRUCTURAL','BDI','ADEQUACY','REPRESENTATION','AUTHORING','COMPILATION','RUNTIME','BEHAVIORAL_VERIFICATION','SUCCESS')}
    generic.publish('R5_105-TRANSFER-EVIDENCE.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Fresh typed exposed local regression; no cumulative or held-out claim',
        implementation_unchanged=True,history_unchanged=True,distribution=distribution,cases=results))
    generic.publish('R5_105-COMPARISON.json',dict(distribution=distribution,cases=comparison,external_invocations=sum(x.get('external_invocations',0) for x in results)))
    lines=['# R5.105 — fixed fresh typed exposed transfer','','R5.104 is the preserved baseline. Exposed local regression only; no held-out/cumulative claim.','',
        '| Case | R5.104 first blocker | R5.105 first blocker | Newly reached stages | Behavioral success |','| --- | --- | --- | --- | --- |']
    for x in comparison:
        lines.append('| '+x['case']+' | '+x['r5_104_first_blocker']+' | '+x['r5_105_first_blocker']+' | '+(', '.join(x['newly_reached']) or 'None')+' | '+('Yes' if x['behaviorally_verified'] else 'No')+' |')
    lines += ['','Full native blockers and all stages: `R5_105-COMPARISON.json`. Source, inventory, reconciliation, normal pipeline receipts and external observations: `R5_105-TRANSFER-EVIDENCE.json`.']
    with (OUT/'R5_105-CAPABILITY-MATRIX.md').open('x',encoding='utf-8',newline='\n') as f: f.write('\n'.join(lines)+'\n')


if __name__=='__main__': main()
