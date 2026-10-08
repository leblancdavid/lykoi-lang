"""Write-once evidence and identifier-only metadata; no provider dependencies."""
import datetime
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(value, indent=2, ensure_ascii=True) + '\n')


def cli(args):
    start = time.perf_counter()
    p = subprocess.run(['pwsh', '-NoProfile', '-Command', 'opencode ' + args],
                       capture_output=True, text=True, timeout=60)
    return p, time.perf_counter() - start


def export(session):
    p, seconds = cli('export ' + session + ' --sanitize --pure')
    result = dict(session=session, export_seconds=seconds, returncode=p.returncode,
                  metadata=[], api_cost_usd=None)
    if p.returncode == 0:
        data = json.loads(p.stdout)
        for message in data.get('messages', []):
            info = message.get('info', {})
            if info.get('role') == 'assistant':
                row = {k: info[k] for k in ('id', 'modelID', 'providerID', 'tokens',
                       'cost', 'time', 'finish') if k in info}
                # No transcript/tool arguments, paths or credentials are retained here.
                row['tools'] = [dict(tool=x.get('tool'), status=x.get('state', {}).get('status'),
                    time=x.get('state', {}).get('time')) for x in message.get('parts', [])
                    if x.get('type') == 'tool']
                result['metadata'].append(row)
    return result


def verify(files):
    for name, digest in files.items():
        if sha(ROOT / name) != digest:
            raise ValueError('identity mismatch: ' + name)


def baseline():
    old = HERE.parent / 'r6_14'
    preserved = load(old / 'BASELINE.json')['preserved']
    verify(preserved)
    verify(load(old / 'PUBLICATION-IDENTITIES.json')['files'])
    vm = load(ROOT / 'experiments/semantic_interpreter/PUBLICATION-IDENTITIES.json')['publication_sha256']
    # Later guidance intentionally supersedes R6.10 entry points; executable
    # and dedicated experiment publication identities remain immutable.
    verify({name: digest for name, digest in vm.items()
            if name.startswith('experiments/semantic_interpreter/')
            or name == 'benchmark/results/phase6/R6_10-REPORT.md'})
    assert load(ROOT / 'benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json')['final_count'] == 26
    for folder in (old, ROOT / 'experiments/semantic_interpreter'):
        for path in sorted(folder.rglob('*')):
            if path.is_file() and '__pycache__' not in path.parts:
                preserved[path.relative_to(ROOT).as_posix()] = sha(path)
    report = HERE.parent / 'R6_14-REPORT.md'
    preserved[report.relative_to(ROOT).as_posix()] = sha(report)
    p, seconds = cli('models --pure')
    identifiers = [s.strip() for s in p.stdout.splitlines() if '/' in s and ' ' not in s.strip()
                   and '\\' not in s and not s.startswith('http')]
    probe = export('ses_ee29b7b0fffeN2wEsLELSrbi10')
    save(HERE / 'BASELINE.json', dict(utc=now(), kernel=26, preserved=preserved,
        r6_14_publication_verified=True, vm_publication_verified=True,
        vm_sha256=sha(ROOT / 'experiments/semantic_interpreter/interpreter.py'),
        head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        initial_status='', python=sys.version, platform=platform.platform(),
        model_inventory=dict(returncode=p.returncode, seconds=seconds, identifiers=identifiers,
            credential_and_routing_attestation=None),
        telemetry_probe=dict(export_available=probe['returncode'] == 0,
            token_fields_available=bool(probe['metadata']), api_cost_usd=None,
            basis='targeted historical own-session metadata export, not new scored usage'),
        session_controls=dict(fresh_context=True, shared_filesystem=True,
            inherited_guidance=True, reasoning_configuration_attested=False,
            independent_sessions_established=False),
        protocol_sha256=sha(HERE / 'PROTOCOL.md')))
    print('Baseline verified:', len(preserved), 'identities; token metadata available:', bool(probe['metadata']))


if __name__ == '__main__':
    if sys.argv[1] == 'baseline':
        baseline()
    elif sys.argv[1] == 'verify':
        verify(load(HERE / 'BASELINE.json')['preserved'])
        print('Preservation verified')
