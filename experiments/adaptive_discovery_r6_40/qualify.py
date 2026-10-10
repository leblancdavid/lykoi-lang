"""Unscored synthetic checks of round-local control plumbing."""
import copy
from common import OUT,Registry,save,load,c,normalize
from development import proxy_pool,development_check,witnesses,DEVELOPMENT
from evaluate import template

def main():
    pool=proxy_pool(); rows=[]
    for e,t in zip(pool,DEVELOPMENT):
        d=e['definition']; flat=template(e,{d['identity']:d})
        twin=c.seal(dict(name='ExpandedTwin',revision=1,params=flat['params'],dependencies={},
            steps=flat['steps'],order=flat['order'],result=flat['result'],result_type=flat['result_type']))
        reg=Registry(OUT/'synthetic-control-registry')
        if d['identity'] not in reg.read()['state']['definitions']: reg.admit([d],reg.read()['token'])
        reg.admit([twin],reg.read()['token'])
        a=development_check(d,e['relation'],[d],witnesses(t))
        b=development_check(twin,e['relation'],[twin],witnesses(t))
        assert a['passed'] and b['passed']
        assert [r['actual'].get('value') for r in a['rows']]==[r['actual'].get('value') for r in b['rows']]
        assert [r['actual'].get('error',{}).get('code') for r in a['rows']]==[r['actual'].get('error',{}).get('code') for r in b['rows']]
        wrong=copy.deepcopy(twin); wrong['result']={'const':1}; wrong=c.seal(wrong)
        failed=development_check(wrong,e['relation'],[wrong],witnesses(t))
        assert not failed['passed'],'wrong behavior must fail despite valid typing'
        rows.append(dict(relation=e['relation'],template_equivalent_finite=True,observations=a['observations'],
            type_valid_wrong_behavior_rejected=True))
    save(OUT/'CONTROL-QUALIFICATION.json',dict(model_calls=0,unscored_synthetic=True,rows=rows,
        task_candidates_used=False,execution_semantics_changed=False))
    print(rows)

if __name__=='__main__': main()
