"""One-round public-source capture; no semantic pipeline or evaluation calls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

ROOT = Path(__file__).resolve().parent
REPOS = ['jqlang/jq', 'curl/curl', 'redis/redis', 'pypa/pip', 'pytest-dev/pytest']
POLICY_COMMIT = 'c840083469efc9f94920ebce41103a51092ac915'


def now():
    return datetime.now(timezone.utc).isoformat()


def save_json(path, value):
    path.write_bytes((json.dumps(value, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))


def fetch(url, path):
    if path.exists():
        raise RuntimeError(f'Refusing to overwrite capture: {path}')
    failures = []
    for attempt in range(3):
        started = now()
        try:
            request = Request(url, headers={
                'Accept': 'application/vnd.github+json',
                'X-GitHub-Api-Version': '2022-11-28',
                'User-Agent': 'Lykoi-R5.116A-procedural-research-capture',
            })
            with urlopen(request, timeout=45) as response:
                raw = response.read()
                headers = dict(response.headers.items())
                status = response.status
            path.write_bytes(raw)
            save_json(path.with_suffix('.receipt.json'), {
                'url': url, 'started_utc': started, 'retrieved_utc': now(),
                'http_status': status, 'headers': headers,
                'sha256': hashlib.sha256(raw).hexdigest(), 'prior_failures': failures,
                'policy_commit': POLICY_COMMIT,
            })
            return json.loads(raw)
        except (HTTPError, URLError, TimeoutError) as error:
            failures.append({'utc': now(), 'attempt': attempt + 1, 'error': str(error)})
            save_json(path.with_suffix('.failures.json'), failures)
            if attempt == 2:
                raise
            time.sleep(5)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('repository', choices=REPOS)
    parser.add_argument('page', type=int, choices=range(1, 16))
    parser.add_argument('--show', action='store_true', help='Display an existing capture without network access')
    args = parser.parse_args()
    sys.stdout.reconfigure(encoding='utf-8')
    committed = subprocess.check_output([
        'git', 'show', f'{POLICY_COMMIT}:benchmark/results/phase6/r5_116a/SELECTION-POLICY.md'
    ])
    if committed.replace(b'\r\n', b'\n') != (ROOT / 'SELECTION-POLICY.md').read_bytes().replace(b'\r\n', b'\n'):
        raise RuntimeError('Policy differs from precommitted policy')
    directory = ROOT / 'captures' / args.repository.replace('/', '__')
    directory.mkdir(parents=True, exist_ok=True)
    if args.show:
        source = json.loads((directory / f'candidate-{args.page:02d}-source.json').read_bytes())
        print(source['title'] + '\n\n' + (source['body'] or ''))
        return
    base = 'https://api.github.com/repos/' + args.repository
    if args.page == 1:
        repo = fetch(base, directory / 'repository.json')
        fetch(base + '/git/ref/heads/' + quote(repo['default_branch'], safe=''), directory / 'default-ref.json')
    query = f'repo:{args.repository} is:issue created:>=2025-01-01'
    url = 'https://api.github.com/search/issues?' + urlencode({
        'q': query, 'sort': 'created', 'order': 'asc', 'per_page': 1, 'page': args.page,
    })
    prefix = f'candidate-{args.page:02d}'
    search = fetch(url, directory / (prefix + '-search.json'))
    if search.get('incomplete_results'):
        raise RuntimeError('Incomplete search results; stop without bypass')
    if not search['items']:
        print('NO_MORE_CANDIDATES')
        return
    found = search['items'][0]
    issue = fetch(base + '/issues/' + str(found['number']), directory / (prefix + '-issue.json'))
    save_json(directory / (prefix + '-source.json'), {'title': issue['title'], 'body': issue['body']})
    print(json.dumps({
        'repository': args.repository, 'page': args.page, 'number': issue['number'],
        'url': issue['html_url'], 'author': issue['user']['login'],
        'created_at': issue['created_at'], 'updated_at': issue['updated_at'],
        'state': issue['state'], 'title': issue['title'], 'body': issue['body'],
    }, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
