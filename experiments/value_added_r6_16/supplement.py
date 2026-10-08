"""Additive provenance publication only; zero scored executions or authoring."""
import subprocess
from evidence import HERE, OUT, ROOT, load, now, save, sha, verify

guidance = ['AGENTS.md', 'benchmark/README.md', 'docs/agent-workflow.md',
            'docs/project-overview.md', 'docs/research-log.md', 'docs/decisions.md']
manifest = OUT / 'PUBLICATION-IDENTITIES.json'
verify({n: h for n, h in load(manifest)['files'].items() if n not in guidance})
verify(load(OUT / 'BASELINE.json')['preserved'])
p = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, text=True, capture_output=True)
assert p.returncode == 0, p.stderr
paths = [OUT / 'INHERITED-CONTEXT-SUPPLEMENT.md', HERE / 'supplement.py'] + [ROOT / n for n in guidance]
for path in paths:
    assert all(line.rstrip() == line for line in path.read_text(encoding='utf-8').splitlines())
save(OUT / 'SUPPLEMENT-IDENTITIES.json', dict(utc=now(), classification='R6_16_ARCHITECTURAL_COMPARISON_INCONCLUSIVE',
    original_publication_manifest_sha256=sha(manifest), original_dedicated_publication_verified=True,
    preserved_identities=775, new_scored_executions=0, git_diff_check_returncode=p.returncode,
    context_class='INHERITED_R6_16_OUTCOME_PRIMING',
    files={path.relative_to(ROOT).as_posix(): sha(path) for path in paths}))
verify(load(OUT / 'SUPPLEMENT-IDENTITIES.json')['files'])
print('Additive provenance supplement published; original dedicated/history hashes preserved; new executions0; stop')
