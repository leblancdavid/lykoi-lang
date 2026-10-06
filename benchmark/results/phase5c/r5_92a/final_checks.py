"""Read-only ordinary-evidence checks; publish a new final receipt, no admission."""
import hashlib
import json
from pathlib import Path
import subprocess

from lykoi_pipeline.controller import ROOT, digest
from lykoi_rehearsal.public_freeze_r5_91 import integrity

DIRECTORY = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    readiness = json.loads((DIRECTORY / 'readiness.json').read_text())
    assert readiness['identity'] == digest({k: v for k, v in readiness.items() if k != 'identity'})
    assert all(sha(ROOT / p) == pin for p, pin in readiness['sources'].items())
    for name in ('verification', 'preaccess'):
        assert sha(DIRECTORY / (name + '.json')) == readiness[name + '_sha256']
    assert sha(DIRECTORY / 'audit.py') == readiness['audit_script_sha256']
    frozen = ROOT / 'benchmark/results/phase5c/r5_91'
    candidate = json.loads((frozen / 'public-freeze-final.json').read_text())
    assert integrity(candidate)
    check = json.loads((DIRECTORY / 'preaccess.json').read_text())
    assert sha(frozen / 'public-controller-final.sqlite') == check['public_database_sha256']
    assert check['controller_revision'] == 2 and check['admission_order']['no_requirement_admitted']
    assert not check['eligible_for_protected_B03_admission'] and check['protected_authorization'] is None
    assert not readiness['R5_92_B03_EXPOSURE_READY']
    assert all(n == 0 for n in check['B03_round_counters'].values())
    changed = subprocess.run(['git', 'diff', '--name-only'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    assert set(changed) <= {'docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md'}, changed
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    paths = ['docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md',
             'benchmark/results/phase5c/R5_92A-READINESS-AND-PROTECTED-AUTHORIZATION.md']
    paths += ['benchmark/results/phase5c/r5_92a/' + name for name in (
        'audit.py', 'final_checks.py', 'readiness.json', 'preaccess.json', 'verification.json', 'model-checks.json',
        'live_public_freeze.txt', 'r5_89.txt', 'r5_86.txt', 'r5_87.txt', 'r5_88.txt',
        'compiler_application.txt', 'guarded_historical.txt')]
    for relative in paths:
        text = (ROOT / relative).read_text(encoding='utf-8')
        assert all(line == line.rstrip() for line in text.splitlines()), relative
    # New links are limited to named ordinary public reports/evidence; no protected lookup.
    for relative in ('benchmark/results/phase5c/R5_93-PREACCESS-HALT.md',
                     'benchmark/results/phase5c/r5_92a/readiness.json',
                     'benchmark/results/phase5c/r5_92a/preaccess.json'):
        assert (ROOT / relative).is_file()
    body = {'version': 'r5.92a-final-checks-1', 'readiness_evidence_identity': readiness['identity'],
            'classification': readiness['classification'], 'source_hashes_match': True,
            'freeze_integrity': True, 'public_controller_database_bytes_unchanged': True,
            'R5_93_halt_bytes_preserved': True, 'tracked_change_scope': changed,
            'whitespace': 'PASS', 'protected_authorization_created': False,
            'eligible_for_protected_B03_admission': False, 'B03_counter_basis': check['counter_basis'],
            'B03_round_counters': check['B03_round_counters'], 'B03_state': check['B03_state'],
            'ordinary_evidence_hashes': {p: sha(ROOT / p) for p in paths}}
    record = {**body, 'identity': digest(body)}
    with (DIRECTORY / 'final-checks.json').open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(record, indent=2, sort_keys=True) + '\n')
    print(json.dumps({'classification': readiness['classification'], 'final_evidence_identity': record['identity'],
                      'checks': 'PASS', 'eligible_for_protected_B03_admission': False,
                      'B03_round_counters_all_zero': True}))


if __name__ == '__main__':
    main()
