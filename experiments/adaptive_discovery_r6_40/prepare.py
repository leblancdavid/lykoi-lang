"""Preservation and development/control freeze; no evaluation module imported."""
import subprocess
import time
from datetime import datetime, timezone
from common import ROOT,HERE,OUT,TEMP,Registry,save,load,sha,normalize
from development import DEVELOPMENT,proxy_pool,witnesses,development_check

def main():
    assert OUT.parent.is_dir() and TEMP.parent.is_dir()
    OUT.mkdir(exist_ok=False); TEMP.mkdir(exist_ok=False)
    prior=ROOT/'benchmark/results/phase6/r6_39'
    receipt=load(prior/'VERIFICATION.json')
    assert receipt['passed'] and receipt['kernel']==26
    assert sha(prior/'PUBLICATION-IDENTITIES.json')==receipt['manifest_sha256']
    pins=dict(load(prior/'BASELINE.json')['protected_files'])
    publication=load(prior/'PUBLICATION-IDENTITIES.json')['files']
    for name,meta in publication.items():
        assert 'p6_a05' not in name.lower().replace('-','_')
        assert sha(ROOT/name)==meta['sha256'] and (ROOT/name).stat().st_size==meta['bytes'],name
        pins[name]=meta['sha256']
    for name in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json'):
        pins[(prior/name).relative_to(ROOT).as_posix()]=sha(prior/name)
    for name,pin in pins.items():
        assert 'p6_a05' not in name.lower().replace('-','_')
        assert sha(ROOT/name)==pin,name
    save(OUT/'BASELINE.json',dict(kernel=26,protected_count=len(pins),protected_files=pins,
        R6_39_publication_verified=True,kernel_inherited_accounting_not_recount=True,
        initial_git_status=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True),
        head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()))
    save(OUT/'DEVELOPMENT-TASKS.json',DEVELOPMENT)
    cases={t['relation']:witnesses(t) for t in DEVELOPMENT}
    save(OUT/'DEVELOPMENT-EXPECTATIONS.json',cases)
    started=time.perf_counter(); pool=proxy_pool(); reg=Registry(OUT/'proxy-pool-registry')
    results={}
    for entry in pool:
        d=entry['definition']; reg.admit([d],reg.read()['token'])
        result=development_check(d,entry['relation'],reg.retrieve(pin=d['identity']),cases[entry['relation']])
        assert result['passed'],entry['relation']
        results[d['identity']]=normalize(result)
    save(OUT/'B-PROXY-POOL.json',dict(entries=pool,authorship='Coordinator GPT-6.1 Sol, explicitly authorized AI proxy',
        human_authored=False,AI_discovery_seen=False,evaluation_results_seen=False,
        evaluation_files_imported=False,coordinator_knows_planned_design=True,
        timing_seconds=time.perf_counter()-started,coordinator_tokens=None,billing=None))
    save(OUT/'B-POOL-CHECKS.json',results)
    paths=[HERE/'common.py',HERE/'development.py',HERE/'prepare.py',HERE/'PROTOCOL.md']+list(OUT.glob('*.json'))
    save(OUT/'DEVELOPMENT-FREEZE.json',dict(utc=datetime.now(timezone.utc).isoformat(),participant_calls=0,
        inputs={p.relative_to(ROOT).as_posix():sha(p) for p in paths}))
    print('Protected',len(pins),'identities; froze',len(pool),'B-proxy pool entries before participant discovery.')

if __name__=='__main__': main()
