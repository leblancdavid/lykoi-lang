"""Check publication bytes, protected baseline and deterministic saved observations."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
from composition import HERE, canonical, diagnose, expand, load, vm
from examples import explicit_twin
from preservation import ROOT, inventory, sha, verify
from run_evidence import serial, traced

GUIDANCE = ['AGENTS.md', 'README.md', 'benchmark/README.md', 'docs/agent-workflow.md',
            'docs/project-overview.md', 'docs/research-log.md', 'docs/decisions.md']
REPORT = 'benchmark/results/phase6/R6_18-REPORT.md'


def files():
    own = [p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts
           and p.name not in {'PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'}]
    return sorted(own + [ROOT / p for p in GUIDANCE + [REPORT]])


def check(replay=False):
    verify()
    results = json.loads((HERE / 'RESULTS.json').read_text())
    for row in results['controls']:
        assert diagnose(load(canonical(row['package']).decode()), row['node_budget']) == row['observed']
    for context, row in results['contexts'].items():
        p = load((HERE / (context + '.symbolic.json')).read_text())
        expanded = expand(p)
        plan = json.loads((HERE / (context + '.expanded.json')).read_text())
        explicit = json.loads((HERE / (context + '.explicit.json')).read_text())
        mapping = json.loads((HERE / (context + '.expansion-map.json')).read_text())
        assert plan == explicit == explicit_twin(p) == expanded['plan']
        assert mapping == {k: v for k, v in expanded.items() if k != 'plan'}
        assert expanded['plan_identity'] == row['plan_identity']
        if replay:
            digest = hashlib.sha256()
            counts = {'success': 0, 'BOUND': 0}
            total_work = 0
            for x in range(256):
                for y in range(256):
                    data = bytes([x, y]) if context == 'pair' else bytes([7, x, y])
                    out = vm.execute(plan, data)
                    assert out == vm.execute(explicit, data)
                    counts['success' if out['status'] == 'success' else out['error']['code']] += 1
                    total_work += out['work']
                    digest.update(canonical({'input': data.hex(), 'result': serial(out)}))
            assert all(digest.hexdigest() == run['complete_observation_sha256']
                       and counts == run['counts'] and total_work == run['work_total'] for run in row['passes'])
    for row in results['runtime_controls']:
        plan = json.loads((HERE / (row['context'] + '.expanded.json')).read_text())
        out, events = traced(plan, bytes.fromhex(row['input_hex']), row['limits'])
        assert serial(out) == row['result'] and events == row['ordered_entry_trace']
    # Only current prose and the isolated new experiment/report may change.
    allowed = set(GUIDANCE + [REPORT])
    changed = subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).splitlines()
    assert all(p in allowed or p.startswith('experiments/typed_composition_r6_18/') for p in changed), changed
    untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    assert all(p == REPORT or p.startswith('experiments/typed_composition_r6_18/') for p in untracked), untracked
    for p in GUIDANCE:
        old = subprocess.check_output(['git', 'show', 'HEAD:' + p], cwd=ROOT).decode().splitlines()
        current = iter((ROOT / p).read_text(encoding='utf-8').splitlines())
        assert all(any(line == candidate for candidate in current) for line in old), p
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    links = 0
    for p in files():
        if p.suffix in {'.md', '.py', '.json'}:
            text = p.read_text(encoding='utf-8')
            assert all(not line.endswith((' ', '\t')) for line in text.splitlines()), p
            if p.suffix == '.json':
                json.loads(text)
            if p.suffix == '.md':
                for link in re.findall(r'\]\(([^)]+)\)', text):
                    if '://' not in link and not link.startswith('#'):
                        destination = (p.parent / link.split('#')[0]).resolve()
                        pending = '--publish' in sys.argv and destination in {
                            HERE / 'PUBLICATION-IDENTITIES.json', HERE / 'VERIFICATION.json'}
                        assert destination.exists() or pending, (p, link)
                        links += 1
    hashes = {p.relative_to(ROOT).as_posix(): {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size} for p in files()}
    target = HERE / 'PUBLICATION-IDENTITIES.json'
    if target.exists():
        assert json.loads(target.read_text())['files'] == hashes, 'publication identity changed'
    else:
        assert '--publish' in sys.argv, 'publication manifest not yet created'
        target.write_text(json.dumps({'round': 'R6.18', 'classification': results['summary']['classification'],
            'files': hashes, 'self_hashed': False, 'protected_files': len(inventory()),
            'verification_receipt_excluded': True}, indent=2) + '\n', encoding='utf-8')
    receipt = {'classification': results['summary']['classification'], 'protected_files': len(inventory()),
               'publication_files': len(hashes), 'relative_links_checked': links,
               'kernel': 26, 'git_diff_check': 'PASS', 'scope': 'PASS', 'guidance_additive': 'PASS',
               'runtime_trace_replays': len(results['runtime_controls']), 'adversarial_replays': len(results['controls']),
               'fresh_process_exhaustive_replay_pairs': 131072 if replay else 0,
               'p6_a04_acceptance_checks': 0, 'p6_a05_access': False}
    if '--publish' in sys.argv:
        receipt['manifest_sha256'] = sha(target.read_bytes())
        (HERE / 'VERIFICATION.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    else:
        saved = json.loads((HERE / 'VERIFICATION.json').read_text())
        assert saved['manifest_sha256'] == sha(target.read_bytes())
        assert saved['protected_files'] == receipt['protected_files']
        assert saved['publication_files'] == receipt['publication_files']
    print(receipt)


if __name__ == '__main__':
    check('--replay' in sys.argv)
