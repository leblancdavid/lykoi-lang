"""Additive content-identity publication; protected semantics/history unchanged."""
import json
import re
import subprocess
import sys
from common import ROOT,HERE,OUT,save,load,sha

def paths():
    excluded={'PUBLICATION-IDENTITIES.json','VERIFICATION.json'}
    return sorted([p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts]+
        [p for p in OUT.rglob('*') if p.is_file() and p.name not in excluded]+
        [ROOT/'benchmark/results/phase6/R6_40-REPORT.md']+
        [ROOT/'docs'/name for name in ['project-overview-r6.40.md','research-log-r6.40.md','decisions-r6.40.md']])

def verify(publish=False):
    pins=load(OUT/'BASELINE.json')['protected_files']
    for name,pin in pins.items():
        assert 'p6_a05' not in name.lower().replace('-','_')
        assert sha(ROOT/name)==pin,name
    components=['src/air_compiler/','experiments/semantic_interpreter/',
        'experiments/typed_composition_r6_18/','r6_23','r6_25','r6_27',
        'experiments/lifecycle_r6_32/','r6_36','r6_37','r6_38','r6_39']
    for component in components: assert any(component in name for name in pins),component
    for filename in ['DEVELOPMENT-FREEZE.json','TASK-FREEZE.json','VOCABULARY-FREEZE.json']:
        for name,pin in load(OUT/filename)['inputs'].items(): assert sha(ROOT/name)==pin,name
    result=load(OUT/'RESULT.json'); assert result['classification']=='R6_40_COMPARISON_INCONCLUSIVE'
    assert result['correctness']=={'A':6,'B':4,'C':4,'X':6}
    assert load(OUT/'SUPPLEMENTAL-AUDIT.json')['total_repeated_replay_observations']==52252
    assert load(OUT/'SUPPLEMENTAL-AUDIT.json')['budget_stop']['sealed_before_cap']
    for p in paths():
        text=p.read_text(encoding='utf-8')
        assert not any(line.endswith((' ','\t')) for line in text.splitlines()),p
        if p.suffix=='.json': json.loads(text)
        elif p.suffix=='.jsonl':
            for line in text.splitlines(): json.loads(line)
        assert not re.search(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}',text),p
        assert not re.search(r'\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',text),p
        if p.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',text):
                if '://' in link or link.startswith('#'): continue
                target=(p.parent/link.split('#')[0]).resolve()
                if publish and target==OUT/'VERIFICATION.json': continue
                assert target.exists(),(p,link)
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).strip()
    manifest=OUT/'PUBLICATION-IDENTITIES.json'
    if publish:
        save(manifest,dict(round='R6.40',files={p.relative_to(ROOT).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in paths()}))
        save(OUT/'VERIFICATION.json',dict(passed=True,kernel=26,protected_count=len(pins),publication_files=len(paths()),
            manifest_sha256=sha(manifest),tracked_files_unchanged=True,git_diff_check=True,
            all_three_freezes_preserved=True,credentials_pattern_scan_passed=True,
            production_VM_wrapper_adapter_contracts_registry_telemetry_unchanged=True,
            R6_39_publication_and_inherited_history_preserved=True,relative_links_passed=True,
            JSON_and_whitespace_passed=True,publication_artifact_hashes_passed=True,
            actual_API_billing=None,complete_efficiency_claim=False))
    receipt=load(OUT/'VERIFICATION.json'); assert receipt['manifest_sha256']==sha(manifest)
    entries=load(manifest)['files']; assert set(entries)=={p.relative_to(ROOT).as_posix() for p in paths()}
    for name,meta in entries.items():
        assert sha(ROOT/name)==meta['sha256'] and (ROOT/name).stat().st_size==meta['bytes'],name
    print('R6.40 publication verified:',len(pins),'protected identities;',len(entries),'publication files')

if __name__=='__main__': verify(len(sys.argv)>1 and sys.argv[1]=='publish')
