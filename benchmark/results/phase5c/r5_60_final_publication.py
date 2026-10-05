"""Finalize halted-candidate publication; no production-stage or observation API."""

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads

OUT = ROOT / 'benchmark/results/phase5c/R5_60-evidence'


def main():
    prior = loads((OUT / 'independent-final-audit.json').read_bytes())
    assert prior['independent_audit'] == 'PASS' and not prior['production_qualified']
    assert all(digest((OUT / n).read_bytes()) == pin for n, pin in prior['evidence_sha256'].items())
    baseline = loads((OUT / 'preservation-baseline.json').read_bytes())['files']
    assert all(digest((ROOT / n).read_bytes()) == pin for n, pin in baseline.items())
    summary = loads((OUT / 'summary.json').read_bytes())
    assert summary['primary_classification'] == 'R5_60_PROTOCOL_HALT'
    evidence = {}
    for path in OUT.rglob('*.json'):
        raw = path.read_bytes()
        value = loads(raw)
        assert raw == canonical(value) + b'\n'
        publication.safe_bytes(value)
        if 'identity' in value:
            tier.envelopes.unseal(value)
        evidence[path.relative_to(OUT).as_posix()] = digest(raw)
    names = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard', '--modified'],
                                     cwd=ROOT, text=True).splitlines()
    sources, dispositions = {}, {}
    for n in sorted(set(names)):
        path = ROOT / n
        if path.suffix in ('.py', '.md', '.txt', '.json'):
            dispositions[n] = publication.check_source(n, path.read_bytes())
            sources[n] = digest(path.read_bytes())
            result = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(path)],
                                    cwd=ROOT, capture_output=True, timeout=10)
            assert result.returncode in (0, 1) and not result.stdout
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, timeout=10).returncode == 0
    publication.persist(OUT / 'publication-integrity.json', {
        'status': 'PASS', 'qualification_result': summary['primary_classification'],
        'production_qualified': False, 'historical_files_unchanged': len(baseline),
        'independent_stopped_audit_preserved': True, 'evidence_sha256': evidence,
        'source_sha256': sources, 'source_dispositions': dispositions,
        'report_clean': True, 'capsule_clean': True, 'production_receipts': 0,
        'certificate_issued': False, 'diagnostics': 'redacted categories only',
        'git_diff_check': 'PASS', 'new_file_whitespace_check': 'PASS',
        'b02_exposure': 0, 'production_b02_accounting': summary['production_b02_accounting'],
        'core_semantics': 30, 'phase5c': 'paused'})
    print({'publication_integrity': 'PASS', 'historical_files_unchanged': len(baseline),
           'classification': summary['primary_classification'], 'production_qualified': False})


if __name__ == '__main__':
    main()
