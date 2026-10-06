"""R5.103 bounded composition, guards/clock selection and provider integration."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from air_compiler.profiles import author, generate
from lykoi_controller import Failure
from lykoi_pipeline import contracts
from lykoi_pipeline.controller import digest
from lykoi_pipeline import scalar_profile, composition_profile
from lykoi_workspace.scalar_corpus import captures, obligations
from lykoi_workspace.query_corpus import response
from lykoi_workspace.query_schema import validate_output
from test_scalar_normal_path import independent_plan, literal_record

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('r5_103_evaluate_tests', ROOT/'benchmark/results/phase5c/R5_103-evaluate.py')
evaluation = importlib.util.module_from_spec(spec); spec.loader.exec_module(evaluation)


def fixture(composed=False, guards=False, clock=False):
    record = captures()[0]
    if guards:
        record['source'] += ' Advance additionally requires class LOAN; otherwise fail invalid_class without state change, after ordinary existence and lifecycle guards.'
        record['facts']['guards'] = [dict(command='advance', field='class', value='LOAN', error='invalid_class', rejection='unchanged')]
    if clock:
        record['source'] += ' Add list-due-before: select available records whose nonnull review_at is strictly before declared current UTC clock; whole records by created_at then id ascending, read only. Equal, future, null and checked_out are excluded.'
        record['facts']['clock_queries'] = [dict(command='list-due-before',predicates=[dict(kind='field_equals',field='state',value='available'),dict(kind='field_before_clock',field='review_at',clock='utc_clock')],order=['created_at','id'],result='whole_records',effect='read_only')]
    query = None
    if composed:
        record['source'] += ' Add find-class --class VALUE: exact case-sensitive class equality without normalization or extra validation; include available and checked_out. Whole records by created_at then id ascending, empty list on no match, no writes. Bind the same registry state, preserve all other commands.'
        query = dict(id='class-query', source=record['source'], operation='find-class', facts={
            'source':dict(collection='state',fields={'id':'string','created_at':'string','class':'string','state':'string'},unique_key='id'),
            'parameters':{'class':'string'},'predicate':dict(field='class',operator='equals',operand={'parameter':'class'}),
            'comparison':dict(case='sensitive',normalization='none'), 'ordering':[dict(field='created_at',direction='ASC'),dict(field='id',direction='ASC')],
            'validation':[], 'inclusion':[dict(field='state',mode='all')], 'effect':dict(state='read_only',persistence='unchanged'),
            'result':dict(shape='collection',cardinality='zero_or_more',no_match='empty')})
    rows=obligations(record)
    if query: rows += response(query,{'text':record['source']},[])['obligations']
    candidate=dict(id=record['id'],source=record['source'],rows=rows,question=None,domains={'capability_profile':composition_profile.PROFILE if composed else scalar_profile.PROFILE})
    if composed: candidate['domains']['collection_store']=dict(kind='composed_scalar',state='state')
    plan=independent_plan(record)
    if guards or clock:
        stored=literal_record(record)
        if guards:
            rejected={**stored,'class':'REFERENCE'}
            c=dict(id='extra-guard-rejection',obligations=[o['id'] for o in rows],initial_state='fresh_directory',initial_files=[dict(path='library.json',json=dict(schema_version=2,records=[rejected]))],steps=[
                dict(argv=['advance','--id',identity],returncode=1,contains=[],preserved=['library.json'],stderr_json={'error':error},stdout_exact='') for identity,error in [('known','invalid_class'),('absent','record_not_found')]],invariants=['Guard rejection unchanged'],transitions='Rejected',rejections='Declared equality and existence errors')
        else:
            past={**stored,'review_at':'1900-01-01T00:00:00Z'}
            future={**stored,'id':'future','review_at':'9999-01-01T00:00:00Z'}
            done={**stored,'id':'done','review_at':'1900-01-01T00:00:00Z','state':'checked_out'}
            c=dict(id='clock-selection-readonly',obligations=[o['id'] for o in rows],initial_state='fresh_directory',initial_files=[dict(path='library.json',json=dict(schema_version=2,records=[future,stored,done,past]))],steps=[
                dict(argv=['list-due-before'],returncode=0,contains=[],preserved=['library.json'],stdout_json=[past],stderr_exact='')],invariants=['Declared equality/strict clock/null exclusion and readonly bytes'],transitions='None',rejections='None')
            # The null record needs a distinct identity from the past record.
            c['initial_files'][0]['json']['records'][1]['id']='null'
        c['identity']=digest(c); plan['cases'].append(c)
        for coverage in plan['coverage']:
            if coverage['obligation'].endswith(('/guards','/clock_queries')): coverage['cases']=[c['identity']]
    if composed:
        stored=literal_record(record)
        c=dict(id='mixed-query-frame',obligations=[o['id'] for o in rows],initial_state='fresh_directory',initial_files=[dict(path='library.json',json=dict(schema_version=2,records=[stored]))],steps=[
            dict(argv=['find-class','--class',v],returncode=0,contains=[],preserved=['library.json'],stdout_json=expected,stderr_exact='') for v,expected in [('LOAN',[stored]),('loan',[]),(' LOAN ',[])]],invariants=['Exact comparison and unchanged storage'],transitions='None',rejections='None')
        c['identity']=digest(c); plan['cases'].append(c)
        plan['coverage'] += [dict(obligation=o['id'],classification='EXERCISED',justification='Mixed query case',cases=[c['identity']]) for o in rows if o['id'] not in {r['obligation'] for r in plan['coverage']}]
    return record,candidate,plan


def prepared(composed=False, guards=False, clock=False):
    record,candidate,plan=fixture(composed,guards,clock)
    result=evaluation.evaluate(candidate,plan)
    assert result['first_blocker']=='SUCCESS',result.get('terminal',result['native'])
    contract=result['formalization']['contract']
    source=next(a['content']['target_source'] for a in result['audit']['artifacts'].values() if a['type']=='target')
    return record,contract,source


class ExistingCompositionTests(unittest.TestCase):
    def test_mixed_normal_pipeline_and_external_behavior(self):
        # Writable scalar/lifecycle/identity, enum/default/query, timestamp/read-only,
        # migration/default and persisted creation resources coexist in one run.
        record,candidate,plan=fixture(composed=True)
        validate_output({'obligations':candidate['rows']})
        result=evaluation.evaluate(candidate,plan)
        self.assertEqual(result['first_blocker'],'SUCCESS',result.get('terminal',result['native']))
        self.assertGreater(result['external_invocations'],17)
        c=result['formalization']['contract']; p=contracts.structural(c,'frc')
        self.assertFalse(p['unsupported']); self.assertEqual(contracts.coverage(c,p)['outcome'],'SUPPORTED')
        b=contracts.bdi(c,p); self.assertEqual(contracts.adequate(c,b)['outcome'],'ADEQUATE')
        v=contracts.faithful_v1(c)['normalized']; self.assertEqual(composition_profile.recover(v),c)
        damaged=copy.deepcopy(v); damaged['facts']['scalar']['fields'][1]['preservation']='trimmed'
        with self.assertRaises(Failure): composition_profile.recover(damaged)

    def test_conflicts_and_unsupported_composition_refuse(self):
        _,c,_=prepared(composed=True)
        for mutation in ('state','collision','mutating','nullable','extra','unselected'):
            bad=copy.deepcopy(c)
            if mutation=='state': bad['context']['domains']['collection_store']['state']='another_state'
            elif mutation=='unselected': bad['context']['domains']['capability_profile']='existing-scalar-1'
            elif mutation=='extra':
                row=copy.deepcopy(bad['obligations'][0]); row['id']='extra'; row['relation']=dict(kind='invariant',parameters={'new_semantics':True}); bad['obligations'].append(row)
            else:
                rows=[o for o in bad['obligations'] if o['relation']['kind']=='filter_order']
                if mutation=='collision':
                    for o in rows: o['relation']['parameters']['query']='list'
                elif mutation=='mutating':
                    next(o for o in rows if o['relation']['parameters']['facet']=='effect')['relation']['parameters']['value']=dict(state='mutating',persistence='write')
                else:
                    source=next(o for o in rows if o['relation']['parameters']['facet']=='source')['relation']['parameters']['value']; source['fields']['review_at']='string'
            p=contracts.structural(bad,'frc')
            with self.subTest(mutation=mutation),self.assertRaises(Failure): contracts.coverage(bad,p)

    def test_omission_and_stale_composition_coverage(self):
        _,c,_=prepared(composed=True)
        p=contracts.structural(c,'frc'); p['rows'].pop()
        with self.assertRaises(Failure): contracts.coverage(c,p)
        bad=copy.deepcopy(c); bad['obligations']=[o for o in bad['obligations'] if o['id']!='find-class/comparison']
        with self.assertRaises(Failure): contracts.coverage(bad,contracts.structural(bad,'frc'))

    def test_equality_guard_external_rejection_and_existence_order(self):
        record,contract,source=prepared(guards=True)
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'target.py'; target.write_text(source,encoding='utf-8')
            store=Path(tmp)/'library.json'
            row=literal_record(record); row['class']='REFERENCE'
            store.write_text(json.dumps(dict(schema_version=2,records=[row])),encoding='utf-8'); before=store.read_bytes()
            for identity,error in [('known','invalid_class'),('absent','record_not_found')]:
                p=subprocess.run([sys.executable,'-I','-S',str(target),'advance','--id',identity],cwd=tmp,env={},capture_output=True,text=True)
                self.assertEqual(p.returncode,1,p.stderr); self.assertEqual(json.loads(p.stderr),{'error':error}); self.assertEqual(store.read_bytes(),before)
        f=scalar_profile.facts(contract); f['guards'].append(dict(command='advance',field='state',value='checked_out',error='invalid_transition',rejection='unchanged'))
        with self.assertRaises(Failure): scalar_profile.lower(f)

    def test_existing_model_guard_amendment(self):
        record,contract,_=prepared()
        base=scalar_profile.lower(scalar_profile.facts(contract))
        record,candidate,plan=fixture(guards=True)
        candidate['domains']['scalar_base_model']=base
        result=evaluation.evaluate(candidate,plan)
        self.assertEqual(result['first_blocker'],'SUCCESS',result)
        model=scalar_profile.lower(scalar_profile.facts(result['formalization']['contract']),base)
        self.assertEqual(model['migrations'],base['migrations']); self.assertEqual(model['transitions'],base['transitions'])

    def test_clock_selection_boundary_and_provider_injection_external_api(self):
        record,contract,source=prepared(composed=True,clock=True)
        f=scalar_profile.facts(contract); model=scalar_profile.lower(f)
        # Separate process imports the public generated API to supply deterministic
        # providers; expectations are literals, not compiler-derived answers.
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'target.py'; target.write_text(source,encoding='utf-8')
            runner=Path(tmp)/'runner.py'
            runner.write_text("import runpy,json\np=runpy.run_path('target.py')\ncreate=p['by_id']('behaviors','behavior:register')\ninputs={'input:create:caption':' exact '}\nproviders={'uuid_v4':lambda:'12345678-1234-4234-8234-123456789abc','utc_clock':lambda:'2026-01-01T00:00:00Z'}\nfirst=p['execute'](create,inputs,providers=providers)\nprint(json.dumps(first))\ntry: p['execute'](create,inputs,providers=providers)\nexcept p['Failure'] as e: print(e.code)\n",encoding='utf-8')
            process=subprocess.run([sys.executable,'-I','-S',str(runner)],cwd=tmp,env={},capture_output=True,text=True)
            self.assertEqual(process.returncode,0,process.stderr)
            lines=process.stdout.splitlines(); first=json.loads(lines[0]); self.assertEqual(first['id'],'12345678-1234-4234-8234-123456789abc'); self.assertEqual(first['created_at'],'2026-01-01T00:00:00Z'); self.assertEqual(lines[1],'id_collision')
            store=Path(tmp)/'library.json'
            rows=[]
            for identity,when,state in [('past','2025-12-31T23:59:59Z','available'),('equal','2026-01-01T00:00:00Z','available'),('future','2026-01-01T00:00:01Z','available'),('null',None,'available'),('done','2025-01-01T00:00:00Z','checked_out')]:
                row=literal_record(record,identity,state); row['review_at']=when; rows.append(row)
            store.write_text(json.dumps(dict(schema_version=2,records=rows)),encoding='utf-8'); before=store.read_bytes()
            runner.write_text("import runpy,json\np=runpy.run_path('target.py')\nb=p['by_id']('behaviors','behavior:selection:list-due-before')\nprint(json.dumps(p['execute'](b,{},clock=lambda:'2026-01-01T00:00:00Z')))\n",encoding='utf-8')
            process=subprocess.run([sys.executable,'-I','-S',str(runner)],cwd=tmp,env={},capture_output=True,text=True)
            self.assertEqual(process.returncode,0,process.stderr); self.assertEqual(json.loads(process.stdout),[rows[0]]); self.assertEqual(store.read_bytes(),before)

    def test_provider_scope_bad_values_and_context_reset(self):
        _,_,source=prepared()
        # Runtime API challenge in a fresh namespace; invalid provider cannot write.
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'target.py'; target.write_text(source,encoding='utf-8')
            runner=Path(tmp)/'runner.py'
            runner.write_text("import runpy,json,pathlib\np=runpy.run_path('target.py')\nb=p['by_id']('behaviors','behavior:register')\ni={'input:create:caption':'valid'}\nfor providers in ({'write':lambda:None},{'uuid_v4':lambda:'bad'},{'utc_clock':lambda:'bad'}):\n try: p['execute'](b,i,providers=providers)\n except (ValueError,p['Failure']): pass\n else: raise AssertionError('bad provider accepted')\n assert not pathlib.Path('library.json').exists()\nr=p['execute'](b,i)\nassert r['id']!='bad'\nprint('PASS')\n",encoding='utf-8')
            p=subprocess.run([sys.executable,'-I','-S',str(runner)],cwd=tmp,env={},capture_output=True,text=True)
            self.assertEqual(p.returncode,0,p.stderr); self.assertEqual(p.stdout.strip(),'PASS')

    def test_two_existing_lifecycle_facets_compose(self):
        record,candidate,plan=fixture()
        record['source'] += ' An independent workflow enum starts queued on registration and advances queued to reviewed with advance_workflow by id; existence and repeat errors are unchanged. It existed in version 1. Neither lifecycle changes the other field.'
        record['facts']['fields'].append(dict(name='workflow',type='enum',domain=['queued','reviewed'],nullable=False,preservation='verbatim'))
        record['facts']['creation']['bindings'].append(dict(field='workflow',source='literal',value='queued',default=None))
        record['facts']['lifecycle'].append(dict(field='workflow',initial='queued',source='queued',target='reviewed',command='advance_workflow',missing_error='record_not_found',transition_error='invalid_transition',rejection='unchanged'))
        candidate.update(source=record['source'],rows=obligations(record))
        plan=independent_plan(record)
        def add_workflow(node):
            if isinstance(node,dict):
                if 'id' in node and 'class' in node: node['workflow']='queued'
                for value in node.values(): add_workflow(value)
            elif isinstance(node,list):
                for value in node: add_workflow(value)
        for c in plan['cases']:
            add_workflow(c); c['identity']=digest({k:v for k,v in c.items() if k!='identity'})
        for coverage in plan['coverage']: coverage['cases']=[c['identity'] for c in plan['cases']]
        stored={**literal_record(record),'workflow':'queued'}
        reviewed={**stored,'workflow':'reviewed'}; advanced={**reviewed,'state':'checked_out'}
        c=dict(id='independent-lifecycles',obligations=[o['id'] for o in candidate['rows']],initial_state='fresh_directory',initial_files=[dict(path='library.json',json=dict(schema_version=2,records=[stored]))],steps=[
            dict(argv=['advance_workflow','--id','known'],returncode=0,contains=[],preserved=[],stdout_json=reviewed,stderr_exact=''),
            dict(argv=['advance','--id','known'],returncode=0,contains=[],preserved=[],stdout_json=advanced,stderr_exact=''),
            dict(argv=['advance_workflow','--id','known'],returncode=1,contains=[],preserved=['library.json'],stderr_json={'error':'invalid_transition'},stdout_exact='')],invariants=['Independent lifecycle fields preserved'],transitions='Two qualified source transitions',rejections='Repeat unchanged')
        c['identity']=digest(c); plan['cases'].append(c)
        for coverage in plan['coverage']: coverage['cases'].append(c['identity'])
        result=evaluation.evaluate(candidate,plan)
        self.assertEqual(result['first_blocker'],'SUCCESS',result.get('terminal'))

    def test_required_input_guard_on_additive_field(self):
        original,contract,_=prepared()
        base=scalar_profile.lower(scalar_profile.facts(contract))
        record=copy.deepcopy(original)
        record['source'] += ' Version 3 adds required nonblank verbatim annotation on registration, rejected with invalid_annotation. Explicit migration from version 2 assigns annotation state; all other authority remains unchanged.'
        f=record['facts']; f['storage']['version']=3
        f['fields'].append(dict(name='annotation',type='string',domain=[],nullable=False,preservation='verbatim'))
        f['creation']['bindings'].append(dict(field='annotation',source='input',value=None,default=None))
        f['creation']['validation'].append(dict(field='annotation',rule='nonblank',error='invalid_annotation'))
        f['evolution'].append(dict(**{'from':2,'to':3},defaults={'annotation':'state'},boundary='explicit_migration',preservation='unrelated_fields'))
        candidate=dict(id=record['id'],source=record['source'],rows=obligations(record),question=None,domains={'capability_profile':scalar_profile.PROFILE,'scalar_base_model':base})
        plan=independent_plan(record)
        for c in plan['cases']:
            for step in c['steps']:
                if step['argv'][0]=='register': step['argv'] += ['--annotation','state']
            c['identity']=digest({k:v for k,v in c.items() if k!='identity'})
        c=plan['cases'][0]
        c['steps'].append(dict(argv=['register','--caption','valid','--annotation','  '],returncode=1,contains=[],preserved=['library.json'],stderr_json={'error':'invalid_annotation'},stdout_exact=''))
        c['identity']=digest({k:v for k,v in c.items() if k!='identity'})
        for coverage in plan['coverage']: coverage['cases']=[c['identity'] for c in plan['cases']]
        result=evaluation.evaluate(candidate,plan)
        self.assertEqual(result['first_blocker'],'SUCCESS',result.get('terminal'))

    def test_standalone_existing_model_amendments_normal_path(self):
        from lykoi_pipeline import model_profile
        record,candidate,plan=fixture(guards=True,clock=True)
        # Source-scoped amendment authority selects a validated prior registry,
        # preserving its commands/defaults/migrations without reauthoring them.
        base=scalar_profile.lower({k:v for k,v in record['facts'].items() if k in scalar_profile.FACETS})
        candidate['domains']=dict(capability_profile=model_profile.PROFILE,existing_base_model=base)
        candidate['rows']=[o for o in candidate['rows'] if o['relation']['parameters']['facet'] in model_profile.FACETS]
        for o in candidate['rows']: o['relation']['parameters']['profile']=model_profile.PROFILE
        ids=[o['id'] for o in candidate['rows']]
        # Explicitly exercise both amended operations in the sealed oracle.
        record2,_,clock_plan=fixture(clock=True)
        plan['cases'] += [clock_plan['cases'][-1]]
        for c in plan['cases']:
            c['obligations']=ids; c['identity']=digest({k:v for k,v in c.items() if k!='identity'})
        plan['coverage']=[dict(obligation=oid,classification='EXERCISED',justification='Explicit guard rejection and clock selection cases',cases=[c['identity'] for c in plan['cases'] if c['id'] in ('extra-guard-rejection','clock-selection-readonly')]) for oid in ids]
        result=evaluation.evaluate(candidate,plan)
        self.assertEqual(result['first_blocker'],'SUCCESS',result.get('terminal'))
        contract=result['formalization']['contract']; normal=contracts.faithful_v1(contract)['normalized']
        self.assertEqual(model_profile.recover(normal),contract)
        bad=copy.deepcopy(contract)
        next(o for o in bad['obligations'] if o['relation']['parameters']['facet']=='guards')['relation']['parameters']['value'][0]['field']='absent_field'
        with self.assertRaises(Failure): contracts.coverage(bad,contracts.structural(bad,'frc'))


if __name__=='__main__': unittest.main()
