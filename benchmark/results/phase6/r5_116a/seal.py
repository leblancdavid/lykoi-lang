"""Hash and audit this finite curation batch; no network or evaluation execution."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
POLICY_COMMIT = 'c840083469efc9f94920ebce41103a51092ac915'
REPOS = ['jqlang/jq', 'curl/curl', 'redis/redis', 'pypa/pip', 'pytest-dev/pytest']
IMPLEMENTATION = ['src', 'schema', 'air', 'generated', 'tests',
                  'benchmark/harness', 'benchmark/evaluation', 'benchmark/conventional']


def load(path):
    return json.loads(path.read_bytes())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def identity(path):
    return {'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path)}


def save(path, value):
    if path.exists():
        raise RuntimeError(f'Refusing to overwrite sealed record: {path}')
    path.write_bytes((json.dumps(value, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))


def git(*args):
    return subprocess.check_output(['git', *args]).decode().strip()


def check_policy():
    committed = subprocess.check_output(['git', 'show',
        f'{POLICY_COMMIT}:benchmark/results/phase6/r5_116a/SELECTION-POLICY.md'])
    physical = (ROOT / 'SELECTION-POLICY.md').read_bytes()
    assert committed.replace(b'\r\n', b'\n') == physical.replace(b'\r\n', b'\n')
    return git('show', '-s', '--format=%cI', POLICY_COMMIT)


def check_scope():
    assert not git('diff', '185073db0667ab10cdf033c03846548f21b48fac', '--', *IMPLEMENTATION)
    assert not git('ls-files', '--others', '--exclude-standard', '--', *IMPLEMENTATION)


def build():
    policy_time = check_policy()
    check_scope()
    selection = load(ROOT / 'selection-log.json')
    entries = []
    first_times = []
    inspected = []
    for index, repo in enumerate(REPOS, 1):
        folder = ROOT / 'captures' / repo.replace('/', '__')
        metadata = load(folder / 'repository.json')
        revision = load(folder / 'default-ref.json')['object']['sha']
        candidates = [c for c in selection['candidates'] if c['repository'] == repo]
        assert [c['page'] for c in candidates] == list(range(1, len(candidates) + 1))
        assert len(candidates) <= 15
        assert candidates[-1]['disposition'] == 'SELECTED'
        assert all(c['disposition'] == 'EXCLUDED' and c['rules'] for c in candidates[:-1])
        captured = sorted(folder.glob('candidate-*-issue.json'))
        assert len(captured) == len(candidates)
        prior_created = None
        for candidate in candidates:
            prefix = f"candidate-{candidate['page']:02d}"
            issue_path = folder / (prefix + '-issue.json')
            search_path = folder / (prefix + '-search.json')
            source_path = folder / (prefix + '-source.json')
            issue = load(issue_path)
            search = load(search_path)
            source = load(source_path)
            receipt = load(issue_path.with_suffix('.receipt.json'))
            first_receipt = load(search_path.with_suffix('.receipt.json'))
            assert not search.get('incomplete_results')
            assert len(search['items']) == 1
            assert search['items'][0]['number'] == issue['number'] == candidate['issue']
            assert 'pull_request' not in issue and 'pull_request' not in search['items'][0]
            assert issue['created_at'] >= '2025-01-01T00:00:00Z'
            if prior_created:
                assert prior_created <= issue['created_at']
            prior_created = issue['created_at']
            assert source == {'title': issue['title'], 'body': issue['body']}
            assert receipt['sha256'] == digest(issue_path)
            assert first_receipt['sha256'] == digest(search_path)
            assert datetime.fromisoformat(policy_time) < datetime.fromisoformat(first_receipt['started_utc'])
            first_times.append(first_receipt['started_utc'])
            inspected.append({**candidate, 'url': issue['html_url'],
                              'retrieved_utc': receipt['retrieved_utc'],
                              'search': identity(search_path), 'issue_api': identity(issue_path),
                              'source': identity(source_path)})
            if candidate['disposition'] != 'SELECTED':
                continue
            opaque_id = f'P6-A{index:02d}'
            assert candidate['id'] == opaque_id
            acceptance = ROOT / 'acceptance' / (opaque_id + '.md')
            text = acceptance.read_text(encoding='utf-8')
            for heading in ['## Explicit requirements', '## Necessary implications',
                            '## Unresolved ambiguities', '## Assumptions requiring clarification']:
                assert heading in text
            provenance = {
                'id': opaque_id, 'selection_order': index, 'search_page': candidate['page'],
                'repository': repo, 'repository_url': metadata['html_url'],
                'repository_numeric_id': metadata['id'], 'repository_node_id': metadata['node_id'],
                'repository_created_at': metadata['created_at'],
                'repository_default_branch': metadata['default_branch'],
                'repository_revision_at_retrieval': revision,
                'repository_license_metadata': metadata.get('license'),
                'repository_capture': identity(folder / 'repository.json'),
                'repository_ref_capture': identity(folder / 'default-ref.json'),
                'issue_number': issue['number'], 'issue_numeric_id': issue['id'],
                'issue_node_id': issue['node_id'], 'issue_url': issue['html_url'],
                'author_login': issue['user']['login'], 'author_numeric_id': issue['user']['id'],
                'author_url': issue['user']['html_url'], 'author_association': issue['author_association'],
                'issue_created_at': issue['created_at'], 'issue_updated_at': issue['updated_at'],
                'retrieved_utc': receipt['retrieved_utc'],
                'source_revision_basis': 'exact retrieved title/body; creation-time revision unavailable',
                'original_title': issue['title'],
                'title_utf8_sha256': hashlib.sha256(issue['title'].encode('utf-8')).hexdigest(),
                'body_utf8_sha256': hashlib.sha256((issue['body'] or '').encode('utf-8')).hexdigest(),
                'source': identity(source_path), 'issue_api': identity(issue_path),
                'search': identity(search_path), 'acceptance': identity(acceptance),
                'readiness': 'CURATED_CLARIFICATION_REQUIRED',
                'context': 'retrieved original issue title/body and repository metadata only; no linked contexts inspected',
                'license_considerations': 'Project license metadata is not asserted to license every issue contribution. Public attributed research capture; no blanket redistribution or historical license claim. No project implementation files fetched; issue snippets retained verbatim.',
            }
            save(ROOT / (opaque_id + '-provenance.json'), provenance)
            entries.append(provenance)
    assert len(entries) == 5
    timestamp = datetime.now(timezone.utc).isoformat()
    summary = [{'id': e['id'], 'readiness': e['readiness']} for e in entries]
    save(ROOT / 'opaque-summary.json', summary)
    save(ROOT / 'candidate-audit.json', {
        'policy_commit': POLICY_COMMIT, 'policy_committed_utc': policy_time,
        'first_issue_description_request_utc': min(first_times),
        'candidate_count': len(inspected), 'selected_count': 5,
        'excluded_count': len(inspected) - 5, 'candidates': inspected,
    })
    bindings = [identity(p) for p in sorted(ROOT.rglob('*')) if p.is_file()
                and p.name not in {'manifest.json', 'manifest.sha256', 'verification.json'}
                and '__pycache__' not in p.parts]
    save(ROOT / 'manifest.json', {
        'classification': 'R5_116A_PROCEDURAL_OPEN_SOURCE_BATCH_CURATED',
        'material_description': 'Externally authored, procedurally selected evaluation material.',
        'curation_utc': timestamp, 'policy_version': selection['policy_version'],
        'policy_commit': POLICY_COMMIT, 'policy': identity(ROOT / 'SELECTION-POLICY.md'),
        'policy_committed_utc': policy_time, 'first_issue_description_request_utc': min(first_times),
        'selection': entries, 'selection_log': identity(ROOT / 'selection-log.json'),
        'candidate_audit': identity(ROOT / 'candidate-audit.json'),
        'opaque_summary': identity(ROOT / 'opaque-summary.json'), 'artifact_bindings': bindings,
        'exposure_declaration': 'Development curation agent inspected selected and excluded bodies. Not blinded, not pristine held-out. Excluded jq#3227 embeds a fixing narrative; no linked solutions opened. Stored API metadata may include later labels/state, not used for acceptance.',
        'evaluation_performed': False, 'implementation_changed': False,
        'baseline': {'proposed_core_concepts': 26, 'exposed_corpus_successes': '16/20',
                     'implementation_commit': '694c4e02f13111e65781e48e69da97c1ea6f4502'},
        'immutability': 'SHA-256-bound files; policy committed in Git. No cryptographic authentication, write protection or creation-time issue revision is claimed. Corrections require new linked records, not overwriting this batch.',
    })
    (ROOT / 'manifest.sha256').write_bytes((digest(ROOT / 'manifest.json') + '  manifest.json\n').encode())
    print(json.dumps({'curation_utc': timestamp, 'candidates': len(inspected),
                      'selected': 5, 'manifest_sha256': digest(ROOT / 'manifest.json'),
                      'sources': [{'id': e['id'], 'repo': e['repository'],
                                   'issue': e['issue_number'], 'license': e['repository_license_metadata'],
                                   'source_sha256': e['source']['sha256'],
                                   'acceptance_sha256': e['acceptance']['sha256']} for e in entries]}, indent=2))


def verify():
    check_policy()
    check_scope()
    manifest = load(ROOT / 'manifest.json')
    assert (ROOT / 'manifest.sha256').read_text().split()[0] == digest(ROOT / 'manifest.json')
    for artifact in manifest['artifact_bindings']:
        assert digest(ROOT / artifact['path']) == artifact['sha256'], artifact['path']
    summary = load(ROOT / 'opaque-summary.json')
    assert len(summary) == 5 and all(set(row) == {'id', 'readiness'} for row in summary)
    assert manifest['evaluation_performed'] is False
    assert manifest['implementation_changed'] is False
    print('PASS: manifest and all artifact hashes; five opaque entries; policy chronology; unchanged implementation scope; no evaluation calls in capture/seal tools.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['build', 'verify'])
    options = parser.parse_args()
    build() if options.action == 'build' else verify()
