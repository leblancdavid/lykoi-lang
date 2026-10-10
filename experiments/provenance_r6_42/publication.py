"""Hash/structure/publication checks only; no historical rescoring or plan executions."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
import re
import subprocess
import sys
from common import ROOT, HERE, OUT, c, read, save, sha, git, verify_files, verify_freeze


def implementation_index(protected):
    groups = {
        'production': {k: v for k, v in protected.items() if k.startswith(('src/', 'air/', 'schema/', 'generated/'))},
        'R6_10_VM': {k: v for k, v in protected.items() if k.startswith('experiments/semantic_interpreter/')},
        'R6_18_wrapper': {k: v for k, v in protected.items() if k.startswith('experiments/typed_composition_r6_18/')},
        'R6_23_adapter': {k: v for k, v in protected.items() if k.startswith('benchmark/results/phase6/r6_23/')
                         and (k.endswith(('.py', '.md', '.schema.json', '/CONTRACT.txt')))},
        'R6_25_contracts': {k: v for k, v in protected.items() if k.startswith('benchmark/results/phase6/r6_25/')
                           and k.endswith(('.py', '/ENVELOPE-1.md', '/REQUIREMENT.json', '/TOOLS.json'))},
        'R6_32_registry': {k: v for k, v in protected.items() if k.startswith('experiments/lifecycle_r6_32/')},
        'historical_R6_40_acceptance': {k: v for k, v in protected.items() if k.startswith('benchmark/results/phase6/r6_40/')
                                    and 'ACCEPTANCE' in k},
    }
    assert all(groups.values()), {k: len(v) for k, v in groups.items()}
    return {'groups': groups, 'counts': {k: len(v) for k, v in groups.items()},
            'method': 'exact baseline SHA256 identities; no semantic implementation edits or historical acceptance execution'}


def check_text(path, raw):
    text = raw.decode('utf-8')
    if path.parent == OUT / 'registry':
        assert c.canonical(json.loads(text)) == raw, str(path) + ': noncanonical registry bytes'
    else:
        assert text.endswith('\n'), str(path) + ': missing final newline'
    assert all(line.rstrip() == line for line in text.splitlines()), str(path) + ': trailing whitespace'
    assert not re.search(r'(?i)(?:sk-[A-Za-z0-9_-]{20,}|authorization\s*:\s*bearer\s+\S+)', text), str(path) + ': credential pattern'
    if path.suffix == '.json':
        json.loads(text)
    if path.suffix == '.md':
        for link in re.findall(r'\[[^\]]*\]\(([^)]+)\)', text):
            if re.match(r'^[a-z]+:', link) or link.startswith('#'):
                continue
            target = link.split('#', 1)[0]
            resolved = (path.parent / target).resolve()
            pending_receipt = resolved in {OUT / 'PUBLICATION-IDENTITIES.json', OUT / 'VERIFICATION.json'}
            if pending_receipt and '--verify' not in sys.argv:
                continue  # generated later in this call; subsequent --verify checks existence
            assert resolved.exists(), str(path) + ': broken link ' + link


def publication():
    protected = read(OUT / 'BASELINE.json')['protected_files']
    protected_count = verify_files(protected)
    frozen_count = verify_freeze()
    index = implementation_index(protected)
    if not (OUT / 'IMPLEMENTATION-IDENTITIES.json').exists():
        save(OUT / 'IMPLEMENTATION-IDENTITIES.json', index)
    else:
        assert read(OUT / 'IMPLEMENTATION-IDENTITIES.json') == index
    assert read(OUT / 'REGRESSIONS.json')['all_passed']
    result = read(OUT / 'RESULT.json')
    assert result['classification'] == 'R6_42_PROVENANCE_PARTIAL'
    assert result['discrepancies'] == 3067
    audit = read(OUT / 'DISCREPANCY-ANALYSIS.json')
    assert audit['all_default_envelopes_equal_frozen']
    assert audit['cutoff_matches']['envelope'] == result['cutoff_observations']
    assert audit['compact_exact_cutoff_pairs_equal'] == 1169
    archives = read(OUT / 'RAW-ARCHIVES.json')['files']
    for name, record in archives.items():
        archive = ROOT / record['archive']
        assert sha(archive) == record['archive_sha256']
        raw = gzip.decompress(archive.read_bytes())
        assert hashlib.sha256(raw).hexdigest() == record['raw_sha256']
        assert len(raw) == record['raw_bytes']
        json.loads(raw)
        assert (OUT / name).read_bytes() == raw  # local originals remain unchanged
    files = [p for p in OUT.rglob('*') if p.is_file() and p.name not in
             {'PUBLICATION-IDENTITIES.json', 'VERIFICATION.json', 'DIFFERENTIAL.json', 'ADVERSARIAL.json'}]
    files += [p for p in HERE.iterdir() if p.is_file() and p.suffix in ('.py', '.md')]
    files += [ROOT / 'benchmark/results/phase6/R6_42-REPORT.md']
    files += [ROOT / 'docs' / name for name in
              ('project-overview-r6.42.md', 'research-log-r6.42.md', 'decisions-r6.42.md')]
    files = sorted(set(files))
    for path in files:
        if path.suffix in ('.json', '.py', '.md') or path.name == '.gitignore':
            check_text(path, path.read_bytes())
    manifest = {'round': 'R6.42', 'excluded_self_referential_files': ['PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'],
                'raw_JSON_publication': 'lossless gzip archives bind original bytes in RAW-ARCHIVES.json',
                'files': {p.relative_to(ROOT).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in files}}
    manifest_path = OUT / 'PUBLICATION-IDENTITIES.json'
    if '--verify' in sys.argv:
        assert read(manifest_path) == manifest
    else:
        save(manifest_path, manifest)
    verify_files(read(manifest_path)['files'])
    assert git('diff', '--name-only') == '', 'unexpected tracked-file changes'
    status = git('status', '--porcelain', '--untracked-files=all')
    allowed = ('benchmark/results/phase6/r6_42/', 'experiments/provenance_r6_42/',
               'benchmark/results/phase6/R6_42-REPORT.md', 'docs/project-overview-r6.42.md',
               'docs/research-log-r6.42.md', 'docs/decisions-r6.42.md')
    assert all(line.startswith('?? ') and line[3:].startswith(allowed) for line in status.splitlines()), status
    diff = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    assert diff.returncode == 0, diff.stdout + diff.stderr
    receipt = {'round': 'R6.42', 'passed': True, 'integrity_passed_is_not_acceptance_passed': True,
               'frozen_acceptance_passed': False, 'classification': result['classification'],
               'manifest_sha256': sha(manifest_path), 'publication_files': len(files),
               'protected_count': protected_count, 'frozen_files': frozen_count, 'kernel': 26,
               'protected_and_frozen_hashes_passed': True, 'production_and_experimental_semantics_unchanged': True,
               'historical_acceptance_rescored': False, 'lossless_archive_recovery_passed': True,
               'JSON_whitespace_relative_links_credential_scan_passed': True,
               'registry_uses_unchanged_canonical_JSON_without_newline': True,
               'untracked_publication_whitespace_checked_separately': True, 'tracked_files_unchanged': True,
               'git_diff_check': {'command': ['git', 'diff', '--check'], 'returncode': diff.returncode,
                                  'stdout': diff.stdout, 'stderr': diff.stderr},
               'implementation_group_counts': index['counts'], 'regressions_passed': True,
               'verification_plan_executions': 0, 'verified_utc': datetime.now(timezone.utc).isoformat()}
    if '--verify' in sys.argv:
        old = read(OUT / 'VERIFICATION.json')
        assert old['manifest_sha256'] == sha(manifest_path) and old['passed']
    else:
        save(OUT / 'VERIFICATION.json', receipt)
    print('R6.42 publication integrity verified:', len(files), 'files;', protected_count, 'protected;', frozen_count, 'frozen')
    print('Implementation identity groups:', index['counts'])
    print('Acceptance remains partial; no plan executed by publication verification.')


if __name__ == '__main__':
    publication()
