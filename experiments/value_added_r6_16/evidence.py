"""Write-once provider-neutral evidence; never reads external acceptance sources."""
import datetime
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / 'benchmark/results/phase6/r6_16'


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def save(p, value):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2, ensure_ascii=True)
        f.write('\n')


def verify(files):
    for n, digest in files.items():
        if sha(ROOT / n) != digest:
            raise ValueError('Identity mismatch: ' + n)


def baseline():
    old = ROOT / 'benchmark/results/phase6/r6_15'
    preserved = load(old / 'BASELINE.json')['preserved']
    verify(preserved)
    # Current guidance is already locally modified by R6.15; snapshot separately.
    guidance = ['AGENTS.md', 'benchmark/README.md', 'docs/agent-workflow.md',
                'docs/project-overview.md', 'docs/research-log.md', 'docs/decisions.md']
    for manifest in ('PUBLICATION-IDENTITIES.json', 'SUPPLEMENT-IDENTITIES.json'):
        verify({n: h for n, h in load(old / manifest)['files'].items() if n not in guidance})
    for folder in (old, ROOT / 'src', ROOT / 'schema', ROOT / 'air', ROOT / 'generated',
                   ROOT / 'experiments/semantic_interpreter'):
        for p in sorted(folder.rglob('*')):
            if p.is_file() and '__pycache__' not in p.parts:
                preserved[p.relative_to(ROOT).as_posix()] = sha(p)
    report = ROOT / 'benchmark/results/phase6/R6_15-REPORT.md'
    preserved[report.relative_to(ROOT).as_posix()] = sha(report)
    accounting = load(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')
    assert accounting['final_count'] == 26
    save(OUT / 'BASELINE.json', dict(utc=now(), kernel=26, preserved=preserved,
        historical_identity_basis='R6.15 transitive preservation plus original publication and supplement',
        initial_guidance={n: sha(ROOT / n) for n in guidance},
        initial_status=subprocess.check_output(['git', 'status', '--short'], text=True),
        head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        python=sys.version, platform=platform.platform(), model='openai/gpt-6.1-sol',
        reasoning='harness default, unattested', api_cost_usd=None,
        author_telemetry='attempt sanitized metadata export after author sessions',
        coordinator_usage=None, protocol_sha256=sha(HERE / 'PROTOCOL.md')))
    print('Baseline verified:', len(preserved), 'protected/history identities; kernel 26')


if __name__ == '__main__':
    baseline()
