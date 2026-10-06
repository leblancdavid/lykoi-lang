"""Execute only fresh typed captures through normal authority and pipeline APIs."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import sys

from lykoi_controller import canonical
from lykoi_pipeline import Pipeline, PipelineController
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.producers import ModelAdapter

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
spec = importlib.util.spec_from_file_location('fresh_corpus', OUT/'R5_103-corpus.py')
corpus = importlib.util.module_from_spec(spec); spec.loader.exec_module(corpus)
STAGES = ('FORMALIZATION','STRUCTURAL','BDI','ADEQUACY','REPRESENTATION','AUTHORING','COMPILATION','RUNTIME','BEHAVIORAL_VERIFICATION')


def producer(record, role):
    def invoke(request):
        assert request['source']['text'] == record['source']
        rows = record['rows']; question = record.get('question')
        refs = [e['identity'] for e in request['evidence'] if e['provenance']=='human_statement']
        authority = {o['id']:refs for o in rows}
        if role == 'formalizer':
            return dict(obligations=rows, authority=authority, domains=record['domains'], lineage=[], policy_applications=[],
                        questions=[dict(id=record['id']+'/question',text=question,priority='BLOCKING',affects=[rows[0]['id']])] if question else [],
                        issues=[dict(id=record['id']+'/ambiguity',category='AMBIGUITY',description=question,affects=[rows[0]['id']],alternatives=[],witness=None,resolved=False)] if question else [])
        s = request['source']; text=s['text']
        source_record=dict(id=s['identity'],text=text,classification='SYNTHETIC',sha256=hashlib.sha256(text.encode()).hexdigest())
        inventory=dict(version='SourceObligationInventory-0.1',source_commitment=hashlib.sha256(canonical(dict(revision=s['revision'],record=source_record))).hexdigest(),extractor='R5.103-fresh-source-side-capture',context_class='SAME_AGENT_ANALYTICAL_CAPTURE',
            items=[dict(id=o['id'],spans=[dict(start=0,end=len(text),quote=text)],meaning=o['statement'],category='BEHAVIOR',material=True,dependencies=[]) for o in rows], questions=[question] if question else [],limitations=['Same-agent source extraction, not independent cognition; synthetic owner approval', 'Whole-source inventory spans account for inherited context; candidate quotes identify local authority'])
        return dict(inventory=inventory,interpretations={o['id']:{k:o[k] for k in ('statement','relation')} for o in rows},authority=authority,domains=record['domains'])
    return ModelAdapter(role,record['id']+':fresh:'+role,invoke,provider='OpenAI',model='openai/gpt-6.1-sol/active-agent-fresh-capture')


def evaluate(record, plan=None):
    with tempfile.TemporaryDirectory(prefix='r5-103-') as tmp:
        c=PipelineController(Path(tmp)/'case.sqlite',PRINCIPALS,verification_fixtures={plan['source_sha256']:plan} if plan else {})
        try:
            w=Workspace(c,'public',record['id'],CREDENTIALS); w.ingest(CREDENTIALS['owner'],record['source'])
            fid=w.formalize(producer(record,'formalizer')); soi=w.commit_inventory(producer(record,'reviewer')); rid=w.reconcile(soi)
            rec=c.artifact(rid)['content']; stages={s:'NOT_REACHED' for s in STAGES}
            result=dict(case=record['id'],stages=stages,candidate=record,formalization=c.artifact(fid)['content'],source_inventory=c.artifact(soi)['content'],reconciliation=rec,external_plan=plan)
            if rec['outcome']!='ACCEPTABLE':
                stages['FORMALIZATION']='BLOCKED'; result.update(first_blocker='FORMALIZATION',native=rec['outcome']); return result
            stages['FORMALIZATION']='PASS_ANALYTICAL_CAPTURE'; w.approve(CREDENTIALS['owner'],fid); seal=w.seal(fid)
            p=Pipeline(c,'public',CREDENTIALS); prepared=p.prepare(seal,'r5-103-'+record['id'],review_rationale='Fresh source-authorized typed local regression; complete coverage required; synthetic authority only')
            terminal=p.execute(prepared); result['terminal']=terminal; result['audit']=p.audit(terminal)
            outcome=terminal['outcome']; result['native']=outcome
            blocker={'STRUCTURAL_COVERAGE_FAILURE':'STRUCTURAL','UNSUPPORTED_BDI_SCOPE':'BDI','UNREPRESENTABLE_SOURCE':'REPRESENTATION','AUTHORING_FAILURE':'AUTHORING','COMPILATION_FAILURE':'COMPILATION','RUNTIME_FAILURE':'RUNTIME','BEHAVIORAL_VERIFICATION_FAILURE':'BEHAVIORAL_VERIFICATION','BEHAVIORALLY_VERIFIED':'SUCCESS','VERIFICATION_PLAN_COVERAGE_GAP':'VERIFICATION_PLAN'}.get(outcome,'ADEQUACY')
            result['first_blocker']=blocker
            # Artifact presence alone is not a passing receipt. Native terminal establishes the failed stage.
            if blocker=='SUCCESS':
                for s in STAGES[1:]: stages[s]='PASS'
                result['external_invocations']=sum(len(x['steps']) for x in plan['cases'])
            else:
                stop='AUTHORING' if blocker=='VERIFICATION_PLAN' else blocker
                for s in STAGES[1:]:
                    stages[s]='BLOCKED' if s==stop else 'PASS'
                    if s==stop: break
            return result
        finally: c.close()


def history_pins():
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.iterdir() if p.is_file() and p.name.startswith(('R5_101-','R5_102-','R5_97-'))}


def main():
    label=sys.argv[1] if len(sys.argv)>1 else 'INITIAL'
    assert label in ('INITIAL','FINAL')
    before=history_pins(); records=corpus.captures()
    from importlib.util import spec_from_file_location, module_from_spec
    ps=spec_from_file_location('fresh_plans',OUT/'R5_103-plans.py'); pm=module_from_spec(ps); ps.loader.exec_module(pm)
    rows=[]
    for record in records:
        row=evaluate(record,pm.plan(record)); rows.append(row)
        print(row['case'],row['first_blocker'],row['native'],flush=True)
    assert before==history_pins()
    distribution={k:sum(r['first_blocker']==k for r in rows) for k in ('FORMALIZATION','STRUCTURAL','BDI','ADEQUACY','REPRESENTATION','LYKOI_SEMANTICS','AUTHORING','COMPILATION','RUNTIME','BEHAVIORAL_VERIFICATION','SUCCESS','VERIFICATION_PLAN')}
    evidence=dict(utc_finished=datetime.datetime.now(datetime.timezone.utc).isoformat(),scope='Fresh requirement-local exposed development baseline, not held-out or cumulative',history_unchanged=True,history_pins=before,distribution=distribution,cases=rows)
    with (OUT/('R5_103-'+label+'-EVIDENCE.json')).open('x',encoding='utf-8',newline='\n') as stream: json.dump(evidence,stream,indent=2); stream.write('\n')


if __name__=='__main__': main()
