"""Additive R6.66 publication sealing and fresh-process integrity verification."""
import ast
import json
import re
import subprocess
import sys
import run


def seal(check=False):
    r = run
    assert r.Path(sys.executable).resolve() == r.PYTHON.resolve()
    r.frozen_check()
    assert r.read(r.OUT/'CPU-REPLAY.json')['passed']
    assert r.read(r.OUT/'TRAINING-READINESS.json')['ready']
    assert not r.ARTIFACTS.exists() and not list(r.OUT.glob('*DISPATCH-CLAIM.json'))
    if not check:
        audit = r.baseline()
        assert audit == r.read(r.OUT/'BASELINE.json')
    paths = sorted(list(r.HERE.glob('*.py')) + [r.ROOT/'benchmark/results/phase6/R6_66-REPORT.md',
                   r.ROOT/'benchmark/results/phase6/R6_66-PROTOCOL.md', r.ROOT/'docs/research-log-r6.66.md'] +
                   [p for p in r.OUT.iterdir() if p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')])
    for path in paths:
        text = path.read_text(encoding='utf-8')
        assert '\r' not in text and all(line == line.rstrip() for line in text.splitlines()), path
        if path.suffix == '.json':
            json.loads(text)
        if path.suffix == '.py':
            ast.parse(text)
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|'+'-----BEGIN '+r'[A-Z ]*'+'PRIVATE KEY-----', text), path
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if link.startswith(('https:', '#')):
                    continue
                assert (path.parent/link.split('#')[0]).resolve().exists(), (path,link)
    status = subprocess.check_output(['git','status','--porcelain','--untracked-files=all'], cwd=r.ROOT, text=True)
    allowed = ('experiments/incremental_training_r6_66/', 'benchmark/results/phase6/r6_66/',
               'benchmark/results/phase6/R6_66-REPORT.md', 'benchmark/results/phase6/R6_66-PROTOCOL.md',
               'docs/research-log-r6.66.md')
    assert all(line[3:].replace('\\','/').startswith(allowed) for line in status.splitlines()), status
    subprocess.run(['git','diff','--check'], cwd=r.ROOT, check=True)
    manifest = dict(version='r6.66-publication-1', files={p.relative_to(r.ROOT).as_posix():
                    dict(sha256=r.sha(p), bytes=p.stat().st_size) for p in paths})
    if check:
        assert manifest == r.read(r.OUT/'PUBLICATION-IDENTITIES.json')
        assert r.sha(r.OUT/'PUBLICATION-IDENTITIES.json') == r.read(r.OUT/'VERIFICATION.json')['manifest_sha256']
    else:
        assert not (r.OUT/'PUBLICATION-IDENTITIES.json').exists()
        r.write('PUBLICATION-IDENTITIES.json', manifest)
        r.write('VERIFICATION.json', dict(passed=True, manifest_sha256=r.sha(r.OUT/'PUBLICATION-IDENTITIES.json'),
                inherited_history_environment_checkpoint_adapter='PASS fresh full audit before qualification and publication',
                json_python_links_whitespace_credentials='PASS', additive_scope='PASS', git_diff_check='PASS',
                kernel_constructs=26, model_calls=0, optimizer_updates=0, scheduler_updates=0, fine_tuning=0,
                dataset_expansion=0, execution_semantic_changes=0, P6_A04_acceptance=0, P6_A05_access=False))
    print('PASS R6.66 publication integrity; history preserved; zero model/training dispatch')


if __name__ == '__main__':
    assert sys.argv[1] in ('seal','check')
    seal(check=sys.argv[1] == 'check')
