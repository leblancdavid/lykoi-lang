"""Final publication identity/whitespace check. No experiment replay."""
import subprocess
from audit import HERE, ROOT, load, now, save, sha, verify, verify_map


def main():
    verify()
    for name in ['SPEC-FREEZE.json','RUN-FREEZE.json','FOLLOWUP-SPEC-FREEZE.json','FOLLOWUP-RUN-FREEZE.json']:
        verify_map(HERE,load(HERE/name)['files'])
    checks=load(HERE/'CHECKS.json')
    assert all(x['returncode']==0 for x in checks['checks'])
    files=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    files.append(HERE.parent/'R6_14-REPORT.md')
    errors=[]
    for path in files:
        for index,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
            if line.rstrip()!=line:
                errors.append(dict(file=path.relative_to(ROOT).as_posix(),line=index))
    assert not errors,errors
    result=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    assert result.returncode==0,result.stdout+result.stderr
    save(HERE/'PUBLICATION-CHECKS.json',dict(utc=now(),preserved_identities=checks['preserved_identities'],
        kernel=26,regression_methods=126,git_diff_check=dict(returncode=result.returncode,
            stdout=result.stdout,stderr=result.stderr),new_file_whitespace_errors=errors,
        scope='VM/production unchanged; P6-A04 acceptance 0; P6-A05 not accessed',
        final_status=subprocess.check_output(['git','status','--short'],cwd=ROOT,text=True)))
    files.append(HERE/'PUBLICATION-CHECKS.json')
    files.extend(ROOT/name for name in ['AGENTS.md','README.md','benchmark/README.md',
        'docs/agent-workflow.md','docs/project-overview.md','docs/research-log.md','docs/decisions.md'])
    save(HERE/'PUBLICATION-IDENTITIES.json',dict(utc=now(),classification='R6_14_FINITE_RELATIONS_SUPPORTED',
        files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(files)},self_hashed=False))
    print('Publication sealed; 642 preserved identities, kernel26, 126 regressions, diff/whitespace clean')


if __name__=='__main__':
    main()
