"""Sanitized route audit and publication; never reads credential stores or dispatches inference."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'benchmark/results/phase6/r6_35'
HERE = Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def save(p, obj):
    with p.open('x', encoding='utf-8', newline='\n') as f:
        f.write(json.dumps(obj, indent=2, sort_keys=True) + '\n')


def audit():
    start = time.perf_counter()
    assert OUT.parent.is_dir()
    OUT.mkdir(exist_ok=False)
    prior = ROOT / 'benchmark/results/phase6/r6_34'
    pins = dict(load(prior / 'BASELINE.json')['protected_files'])
    manifest = prior / 'PUBLICATION-IDENTITIES.json'
    assert sha(manifest) == load(prior / 'VERIFICATION.json')['manifest_sha256']
    for name, meta in load(manifest)['files'].items():
        assert sha(ROOT / name) == meta['sha256'], name
        pins[name] = meta['sha256']
    for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json'):
        pins[(prior / name).relative_to(ROOT).as_posix()] = sha(prior / name)
    for name, pin in pins.items():
        assert 'p6_a05' not in name.lower().replace('-', '_')
        assert sha(ROOT / name) == pin, name
    save(OUT / 'BASELINE.json', {'protected_files': pins, 'protected_count': len(pins),
        'kernel': 26, 'initial_git_status': 'clean',
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()})
    exe = Path(os.environ['APPDATA']) / 'npm/node_modules/opencode-ai/bin/opencode.exe'
    run = subprocess.run([str(exe), 'debug', 'config'], cwd=ROOT, capture_output=True, timeout=30)
    # Never print or retain raw config/stdout/stderr. Only allowlisted metadata survives.
    config = json.loads(run.stdout) if run.returncode == 0 else {}
    providers = {}
    for name, value in config.get('provider', {}).items():
        options = value.get('options', {})
        url = options.get('baseURL')
        endpoint = None
        if isinstance(url, str):
            from urllib.parse import urlsplit
            parsed = urlsplit(url)
            endpoint = {'scheme': parsed.scheme, 'host': parsed.hostname,
                        'path': parsed.path, 'query_omitted': bool(parsed.query)}
        providers[name] = {'api_key_option_present': 'apiKey' in options,
                           'base_endpoint': endpoint,
                           'header_override_present': bool(options.get('headers'))}
    env_names = sorted(k for k in os.environ if re.search('OPENAI|OPENCODE|CHATGPT|CODEX|PROXY|AZURE', k))
    agents = {name: {'model': value.get('model'), 'variant': value.get('variant')}
              for name, value in config.get('agent', {}).items() if isinstance(value, dict)}
    save(OUT / 'ROUTE-AUDIT.json', {
        'opencode_version': '1.18.32', 'resolved_config_command_returncode': run.returncode,
        'configured_default_model': config.get('model'), 'agents': agents,
        'provider_overrides': providers, 'environment_variable_names_only': env_names,
        'plugin_count': len(config.get('plugin', [])),
        'credential_listing': {'openai': 'oauth', 'environment_openai_api_key_present': 'OPENAI_API_KEY' in os.environ},
        'credential_listing_source': 'opencode auth list; provider names/types only',
        'credential_store_read': False, 'credential_values_exported': False,
        'current_harness_model_identity': 'openai/gpt-6.1-sol',
        'current_harness_identity_source': 'Injected harness model name; not authentication attestation',
        'working_session_endpoint': None, 'working_session_authentication_route': None,
        'working_session_oauth_match': 'UNVERIFIED',
        'R6_33_R6_34_selected_route': 'openai/gpt-6.1-sol',
        'R6_33_R6_34_effective_auth_route': 'UNATTESTED',
        'R6_34_environment_openai_api_key_present': True,
        'historical_plugin_overrides': ['OPENCODE_PURE=1', 'OPENCODE_DISABLE_DEFAULT_PLUGINS=1'],
        'historical_override_source': 'Preserved R6.34 preflight.py lines 114-117; R6.33 route from report',
        'inference_dispatched': False, 'audit_script_wall_seconds': time.perf_counter() - start,
        'decision': 'STOP: selected model identity and stored OAuth do not identify effective working-session authentication/endpoint; API-key bypass remains unresolved'
    })
    print('Sanitized audit saved; protected identities:', len(pins))


def paths():
    return sorted([p for base in (HERE, OUT) for p in base.rglob('*')
                   if p.is_file() and '__pycache__' not in p.parts
                   and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
                  + [ROOT / 'benchmark/results/phase6/R6_35-REPORT.md']
                  + [ROOT / ('docs/' + s + '-r6.35.md') for s in ('project-overview', 'research-log', 'decisions')])


def verify(publish=False):
    base = load(OUT / 'BASELINE.json')
    for name, pin in base['protected_files'].items():
        assert sha(ROOT / name) == pin, name
    for name, pin in load(ROOT / 'benchmark/results/phase6/r6_33/FREEZE.json')['inputs'].items():
        assert sha(ROOT / name) == pin, name
    for p in paths():
        text = p.read_text(encoding='utf-8')
        assert not any(line.endswith((' ', '\t')) for line in text.splitlines()), p
        if p.suffix == '.json':
            json.loads(text)
        if p.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if '://' not in link and not link.startswith('#'):
                    assert (p.parent / link.split('#')[0]).resolve().exists(), (p, link)
        assert not re.search(r'\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}', text)
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True).strip()
    result = load(OUT / 'RESULT.json')
    assert result['classification'] == 'R6_35_PROTOCOL_HALT'
    assert result['participant_model_calls'] == 0
    manifest_path = OUT / 'PUBLICATION-IDENTITIES.json'
    if publish:
        save(manifest_path, {'round': 'R6.35', 'files': {
            p.relative_to(ROOT).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in paths()}})
        save(OUT / 'VERIFICATION.json', {'passed': True, 'kernel': 26,
            'protected_identities_verified': len(base['protected_files']),
            'publication_files': len(paths()), 'manifest_sha256': sha(manifest_path),
            'R6_33_freeze_verified': True, 'tracked_files_unchanged': True,
            'git_diff_check': True, 'relative_links': True, 'additive_whitespace': True,
            'credential_store_read': False})
    receipt = load(OUT / 'VERIFICATION.json')
    assert receipt['manifest_sha256'] == sha(manifest_path)
    entries = load(manifest_path)['files']
    assert set(entries) == {p.relative_to(ROOT).as_posix() for p in paths()}
    for name, meta in entries.items():
        assert sha(ROOT / name) == meta['sha256'] and (ROOT / name).stat().st_size == meta['bytes']
    print('R6.35 publication verified:', len(base['protected_files']), 'protected identities;', len(paths()), 'published files')


if __name__ == '__main__':
    if sys.argv[1] == 'audit':
        audit()
    else:
        verify(publish=sys.argv[1] == 'publish')
