"""Read-only qualification/preservation checks and one additive publication seal."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
import re
import subprocess
import sys
from common import ROOT, HERE, OUT, read, save, sha, verify, git


def publication():
    verifying = '--verify' in sys.argv
    baseline = read(OUT / 'BASELINE.json')
    protected_count = verify(baseline['protected_files'])
    frozen_count = verify(read(OUT / 'FREEZE.json')['files'])
    result = read(OUT / 'RESULT.json')
    raw_path, archive = OUT / 'QUALIFICATION.json', OUT / 'QUALIFICATION.json.gz'
    if not verifying:
        assert not archive.exists()
        raw = raw_path.read_bytes()
        with archive.open('xb') as stream:
            stream.write(gzip.compress(raw, mtime=0))
        save('RAW-ARCHIVE.json', {'raw_sha256': sha(raw_path), 'raw_bytes': len(raw),
             'archive_sha256': sha(archive), 'archive_bytes': archive.stat().st_size,
             'lossless': True})
    archive_record = read(OUT / 'RAW-ARCHIVE.json')
    raw = gzip.decompress(archive.read_bytes())
    assert hashlib.sha256(raw).hexdigest() == archive_record['raw_sha256']
    assert len(raw) == archive_record['raw_bytes'] and sha(archive) == archive_record['archive_sha256']
    assert raw == raw_path.read_bytes()
    qualification = json.loads(raw)
    assert len(qualification['failures']) == result['failures']
    assert qualification['counts'] == result['counts']
    assert read(OUT / 'ADVERSARIAL.json')['passed']
    assert read(OUT / 'PREEXECUTION-REVIEW.json')['passed']
    # No tracked file may change; only these round-local additions are permitted.
    assert git('diff', '--name-only') == ''
    allowed = ('experiments/provenance_r6_43/', 'benchmark/results/phase6/r6_43/',
               'benchmark/results/phase6/R6_43-REPORT.md', 'docs/project-overview-r6.43.md',
               'docs/research-log-r6.43.md', 'docs/decisions-r6.43.md')
    status = git('status', '--porcelain', '--untracked-files=all')
    assert all(line.startswith('?? ') and line[3:].startswith(allowed) for line in status.splitlines()), status
    files = [p for p in OUT.rglob('*') if p.is_file() and p.name not in
             ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json', 'QUALIFICATION.json')]
    files += list(HERE.glob('*.py')) + list(HERE.glob('*.md'))
    files += [ROOT / 'benchmark/results/phase6/R6_43-REPORT.md']
    files += [ROOT / 'docs' / ('%s-r6.43.md' % stem) for stem in ('project-overview', 'research-log', 'decisions')]
    pending = {OUT / 'PUBLICATION-IDENTITIES.json', OUT / 'VERIFICATION.json'}
    for path in sorted(files):
        if path.suffix == '.gz':
            continue
        text = path.read_text(encoding='utf-8')
        assert text.endswith('\n'), str(path)
        assert all(line.rstrip() == line for line in text.splitlines()), str(path)
        assert not re.search(r'(?i)(?:sk-[A-Za-z0-9_-]{20,}|authorization\s*:\s*bearer\s+\S+)', text), str(path)
        if path.suffix == '.json':
            json.loads(text)
        if path.suffix == '.md':
            for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
                if re.match(r'^[a-z]+:', link) or link.startswith('#'):
                    continue
                target = (path.parent / link.split('#', 1)[0]).resolve()
                if not verifying and target in pending:
                    continue
                assert target.exists(), str(path) + ': ' + link
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    manifest = {'round': 'R6.43', 'files': {p.relative_to(ROOT).as_posix():
                 {'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(files)},
                 'excluded': ['PUBLICATION-IDENTITIES.json', 'VERIFICATION.json', 'QUALIFICATION.json'],
                 'raw_evidence': 'lossless gzip plus RAW-ARCHIVE.json, original preserved locally'}
    if verifying:
        assert read(OUT / 'PUBLICATION-IDENTITIES.json') == manifest
        assert read(OUT / 'VERIFICATION.json')['manifest_sha256'] == sha(OUT / 'PUBLICATION-IDENTITIES.json')
        assert read(OUT / 'VERIFICATION.json')['passed']
    else:
        save('PUBLICATION-IDENTITIES.json', manifest)
        save('VERIFICATION.json', {'round': 'R6.43', 'passed': True, 'classification': result['classification'],
             'manifest_sha256': sha(OUT / 'PUBLICATION-IDENTITIES.json'), 'files': len(files),
             'protected_count': protected_count, 'frozen_files': frozen_count,
             'kernel': 26, 'kernel_method': 'unchanged preserved accounting; no new recount',
             'historical_acceptance_rescored': False, 'tracked_files_unchanged': True,
             'production_VM_wrapper_adapter_contracts_registry_unchanged': True,
             'lossless_archive_recovery': True, 'JSON_whitespace_links_credential_pattern_check': True,
             'git_diff_check': {'returncode': diff.returncode, 'stdout': diff.stdout, 'stderr': diff.stderr},
             'new_file_whitespace_checked_separately': True, 'verification_plan_executions': 0,
             'verified_utc': datetime.now(timezone.utc).isoformat()})
    verify(manifest['files'])
    print('R6.43 publication verified:', len(files), 'published;', protected_count, 'protected;', frozen_count, 'frozen')


if __name__ == '__main__':
    publication()
