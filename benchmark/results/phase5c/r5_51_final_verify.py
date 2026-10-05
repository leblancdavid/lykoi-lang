"""Read-only stopped-run diagnostics and final evidence integrity, no dispatch."""

import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]

from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure
from benchmark.evaluation.preexposure_r5_45 import unseal

RESULTS = ROOT / 'benchmark/results/phase5c'
OUTPUT = RESULTS / 'R5_51-evidence'
REPORT = 'R5_51-TIER2-EXPERIMENTAL-CAPSULE-AND-STATIC-GATE-QUALIFICATION.md'
MECHANISMS = ('benchmark/evaluation/tier2_r5_51.py',
              'benchmark/evaluation/test_tier2_r5_51.py',
              'benchmark/results/phase5c/r5_51_qualification.py')


def read(path):
    content = Path(path).read_bytes()
    value = loads(content)
    if content != canonical(value) + b'\n':
        raise ProtocolFailure('noncanonical evidence')
    security.safe_bytes(value)
    return value


def diagnose():
    capsule = read(OUTPUT / 'capsule.json')
    workspace = Path(capsule['context']['root'])
    rows = {}
    for name in ('historical', 'prospective', 'infrastructure'):
        receipt = read(OUTPUT / ('lock-' + name + '.json'))
        result = receipt['result']
        filenames = {'historical': 'R5_40-implementation-profile-lock.json',
                     'prospective': 'R5_41-implementation-lock.json',
                     'infrastructure': 'R5_47-infrastructure-lock-v2.json'}
        lock = loads((workspace / 'benchmark/results/phase5c' / filenames[name]).read_bytes())
        crlf_only, other = [], []
        for relative in result['differences']:
            path = workspace / relative
            # Diagnostic comparison only. Neither workspace nor lock is changed;
            # no normalized bytes qualify identity, authority or stage evidence.
            if path.is_file() and digest(path.read_bytes().replace(b'\r\n', b'\n')) == lock['files'][relative]:
                crlf_only.append(relative)
            else:
                other.append(relative)
        rows[name] = {'members': result['members'], 'matching': result['matching'],
                      'identity_valid': result['identity_valid'],
                      'ancestry_valid': result['historical_ancestry_valid'],
                      'crlf_only_count': len(crlf_only), 'other_differences': other,
                      'status': receipt['status']}
    definitions = read(OUTPUT / 'definitions.json')
    suites = {}
    statuses = {'PASS': 0, 'FAIL': 0, 'INCOMPLETE': 0}
    for name in definitions:
        row = read(OUTPUT / (name + '.json'))
        statuses[row['status']] += 1
        result = row['result']
        if 'discovered' in result:
            suites[name] = {k: result[k] for k in ('discovered', 'passed', 'skipped', 'failures', 'errors', 'seconds')}
    value = {'purpose': 'stopped qualification diagnosis only; no normalization or receipt promotion',
             'locks': rows, 'stage_status_counts': statuses, 'suites': suites,
             'capsule': capsule['identity'], 'b02_exposure': 0}
    security.persist(RESULTS / 'R5_51-diagnostics.json', value)
    print({'locks': rows, 'stage_status_counts': statuses})


def verify():
    summary = read(OUTPUT / 'summary.json')
    capsule = read(OUTPUT / 'capsule.json')
    unseal(capsule)
    definitions = read(OUTPUT / 'definitions.json')
    receipts = {}
    for name, definition in definitions.items():
        row = read(OUTPUT / (name + '.json'))
        unseal(row)
        if (row['capsule'] != capsule['identity'] or row['stage'] != name or
                row['mechanism'] != digest(canonical(definition)) or
                row['identity'] != summary['receipts'][name]):
            raise ProtocolFailure('mixed final evidence')
        receipts[name] = row
    if (summary['receipt_count'] != len(definitions) or summary['production_certificate_issued'] is not False or
            summary['primary_classification'] != 'R5_51_TIER2_CERTIFICATE_GAP' or
            summary['b02_exposure'] != 0 or summary['core_semantics'] != 30 or
            receipts['tier2']['result']['passed'] != 43 or
            receipts['synthetic-lifecycle']['result']['counts']['disposition'] != 'one'):
        raise ProtocolFailure('final accounting mismatch')
    mechanisms = {}
    for name in MECHANISMS:
        actual = digest((ROOT / name).read_bytes())
        if actual != capsule['repository'][name]['physical']['sha256']:
            raise ProtocolFailure('published mechanism differs from observed copy')
        mechanisms[name] = actual
    # Recompute actual relevant state from the dedicated copy, not author checkout.
    from benchmark.results.phase5c import r5_51_qualification as driver
    driver.ROOT = Path(capsule['context']['root'])
    os.environ['LYKOI_R551_EVIDENCE'] = str(OUTPUT)
    if driver.capture() != capsule:
        raise ProtocolFailure('dedicated workspace changed after qualification')
    publication = read(RESULTS / 'R5_51-diagnostics.json')
    report = (RESULTS / REPORT).read_text(encoding='utf-8')
    if 'R5_51_TIER2_CERTIFICATE_GAP' not in report:
        raise ProtocolFailure('report classification missing')
    checked = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10)
    if checked.returncode:
        raise ProtocolFailure('diff check failed')
    files = [REPORT, 'R5_51-diagnostics.json', 'R5_51-materialization.json', 'r5_51_final_verify.py']
    artifacts = {n: digest((RESULTS / n).read_bytes()) for n in files}
    evidence = {p.name: digest(p.read_bytes()) for p in sorted(OUTPUT.glob('*.json'))}
    security.persist(RESULTS / 'R5_51-final-integrity.json', {
        'status': 'PASS', 'purpose': 'integrity of failed qualification; does not qualify production',
        'capsule': capsule['identity'], 'receipt_count': len(receipts),
        'mechanisms': mechanisms, 'artifacts': artifacts, 'canonical_evidence': evidence,
        'stage_status_counts': publication['stage_status_counts'],
        'dedicated_workspace_unchanged': True, 'diff_check': 'PASS',
        'production_certificate_issued': False, 'b02_exposure': 0, 'core_semantics': 30})
    print({'integrity': 'PASS', 'receipt_count': len(receipts)})


if __name__ == '__main__':
    {'diagnose': diagnose, 'verify': verify}[sys.argv[1]]()
