"""Final preservation, publication whitespace/link checks and identity seal."""
import re
import subprocess

from audit import HERE, ROOT, load, now, save, sha, verify, verify_map


def main():
    verify()
    for name in ('FREEZE.json','PROBE-FREEZE.json'):
        verify_map(HERE,load(HERE/name)['files'])
    report = HERE.parent/'R6_13-REPORT.md'
    for target in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8')):
        if target not in ('r6_13/PUBLICATION-CHECKS.json','r6_13/PUBLICATION-IDENTITIES.json'):
            assert (report.parent/target).is_file(),target
    paths = sorted(p for p in HERE.rglob('*') if p.is_file()) + [report]
    documents = [ROOT/name for name in ('AGENTS.md','README.md','benchmark/README.md',
        'docs/agent-workflow.md','docs/project-overview.md','docs/decisions.md','docs/research-log.md')]
    for path in paths:
        if path.suffix in ('.md','.py','.json'):
            for index,line in enumerate(path.read_text(encoding='utf-8').splitlines(),1):
                assert line.rstrip()==line,f'{path}:{index}: trailing whitespace'
    check = subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True,check=True)
    save(HERE/'PUBLICATION-CHECKS.json',dict(utc=now(),protected_files=614,kernel=26,
        freeze_checks=True,report_links=True,new_file_whitespace=True,
        git_diff_check=dict(returncode=check.returncode,stdout=check.stdout,stderr=check.stderr)))
    paths += documents + [HERE/'PUBLICATION-CHECKS.json']
    save(HERE/'PUBLICATION-IDENTITIES.json',dict(utc=now(),classification='R6_13_SCORING_AND_REPLAY_QUALIFIED',
        self_hashed=False,files={p.relative_to(ROOT).as_posix():sha(p) for p in paths}))
    for target in re.findall(r'\]\(([^)]+)\)',report.read_text(encoding='utf-8')):
        assert (report.parent/target).is_file(),target
    print('R6.13 publication sealed; historical identities, freeze, links, whitespace and git diff --check pass')


if __name__ == '__main__':
    main()
