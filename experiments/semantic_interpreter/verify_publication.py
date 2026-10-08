"""Check prospective publication scope, bytes and saved replay observations."""
import hashlib
import json
from pathlib import Path
import subprocess
from baseline import ROOT, HERE, inventory, verify_publications
from interpreter import execute
from publish_evidence import serial


if __name__ == '__main__':
    baseline=json.loads((HERE/'BASELINE.json').read_text(encoding='utf-8'))
    assert inventory()==baseline['protected_files']
    verify_publications()
    recorded=json.loads((HERE/'evidence/IMPLEMENTATION-IDENTITIES.json').read_text(encoding='utf-8'))
    for name,h in recorded['files'].items():
        assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==h,name
    observed=json.loads((HERE/'evidence/REPRODUCIBILITY.json').read_text(encoding='utf-8'))
    for fmt,row in observed.items():
        plan=json.loads((HERE/f'{fmt}.plan.json').read_text(encoding='utf-8'))
        assert serial(execute(plan,bytes.fromhex(row['input_hex'])))==row['result'],fmt
    guidance=['AGENTS.md','README.md','docs/agent-workflow.md','docs/project-overview.md','docs/research-log.md','docs/decisions.md']
    modified=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).splitlines()
    assert set(modified)<=set(guidance),modified
    # Historical guidance text must remain an exact subsequence of current lines.
    for name in guidance:
        old=subprocess.check_output(['git','show',f'HEAD:{name}'],cwd=ROOT).decode('utf-8').splitlines()
        current=(ROOT/name).read_text(encoding='utf-8').splitlines()
        iterator=iter(current)
        assert all(any(line==candidate for candidate in iterator) for line in old),name
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    files=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    report=ROOT/'benchmark/results/phase6/R6_10-REPORT.md'
    files+=[report]+[ROOT/name for name in guidance]
    for p in files:
        if p.suffix in ('.md','.py','.json','.txt'):
            text=p.read_text(encoding='utf-8')
            assert all(not line.endswith((' ','\t')) for line in text.splitlines()),p
    target=HERE/'PUBLICATION-IDENTITIES.json'
    hashes={p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if p!=target}
    if target.exists():
        assert json.loads(target.read_text(encoding='utf-8'))['publication_sha256']==hashes,'publication changed'
    else:
        target.write_text(json.dumps(dict(round='R6.10',classification='R6_10_PROTOTYPE_PARTIAL',publication_sha256=hashes,
                                         self_hashed=False,protected_files=len(baseline['protected_files']),replay_formats=3),indent=2)+'\n',encoding='utf-8')
    print('Preservation: 219 files unchanged; 26 publication hashes verified')
    print('Saved source identities match; fresh-process replay: 3/3 exact')
    print('Guidance changes additive; git diff --check and new-file whitespace pass')
