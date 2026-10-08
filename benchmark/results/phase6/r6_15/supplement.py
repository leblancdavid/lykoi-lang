"""Additive disclosure identities; preserve original publication and results."""
import subprocess
from evidence import HERE, ROOT, load, save, sha, verify, now


if __name__=='__main__':
    verify(load(HERE/'BASELINE.json')['preserved'])
    verify(load(HERE/'PUBLICATION-IDENTITIES.json')['files'])
    p=subprocess.run(['git','diff','--check'],cwd=ROOT,capture_output=True,text=True)
    assert p.returncode==0
    names=['INHERITED-CONTEXT-SUPPLEMENT.md','supplement.py']
    for name in names:
        assert all(line==line.rstrip() for line in (HERE/name).read_text(encoding='utf-8').splitlines())
    save(HERE/'SUPPLEMENT-IDENTITIES.json',dict(utc=now(),classification='R6_15_EXPLORATORY_COMPARISON_ONLY',
        original_publication_manifest_sha256=sha(HERE/'PUBLICATION-IDENTITIES.json'),
        original_publication_and_687_preserved_identities_verified=True,
        git_diff_check_returncode=p.returncode,new_scored_executions=0,
        files={p.relative_to(ROOT).as_posix():sha(p) for p in [HERE/name for name in names]}))
    verify(load(HERE/'SUPPLEMENT-IDENTITIES.json')['files'])
    print('Additive inherited-context disclosure identities verified; original publication unchanged')
