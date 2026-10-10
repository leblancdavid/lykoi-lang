"""R6.53 read-only preflight and additive halt publication; no optimizer/model run."""
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'benchmark/results/phase6/r6_53'
sys.path.insert(0, str(ROOT / 'experiments/training_setup_r6_52'))
import publication as prior
from setup import STORE, PYTHON, sha


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(name, value):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n',
                            encoding='utf-8', newline='\n')


def identities(folder):
    manifest = folder / 'PUBLICATION-IDENTITIES.json'
    saved = read(manifest)
    assert sha(manifest) == read(folder / 'VERIFICATION.json')['manifest_sha256']
    for name, record in saved['files'].items():
        path = ROOT / name
        assert sha(path) == record['sha256'] and path.stat().st_size == record['bytes'], name
    return {'manifest_sha256': sha(manifest), 'payload_files': len(saved['files'])}


def preflight():
    assert Path(sys.executable).resolve() == PYTHON.resolve()
    baseline = prior.baseline()
    publication = identities(ROOT / 'benchmark/results/phase6/r6_52')
    external = prior.external()
    env = read(prior.OUT / 'ENVIRONMENT-IDENTITIES.json')
    assert prior.package_identity() == env['packages']
    python_home = STORE / 'python/cpython-3.12.11-windows-x86_64-none'
    for key, path in {
        'python_executable_sha256': python_home / 'python.exe',
        'python_dll_sha256': python_home / 'python312.dll',
        'venv_executable_sha256': PYTHON,
        'uv_executable_sha256': STORE / 'uv/uv.exe',
        'requirements_lock_sha256': prior.OUT / 'requirements-lock.txt',
    }.items():
        assert sha(path) == env[key], key
    checkpoint = read(prior.OUT / 'CHECKPOINT.json')
    assert checkpoint['repo'] == 'Qwen/Qwen2.5-Coder-1.5B-Instruct'
    assert checkpoint['revision'] == checkpoint['resolved_revision'] == '2e1fd397ee46e1388853d2af2c993145b0f1098a'
    from convert import convert_entry, strict, dump
    from mask_controls import checked_record
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(STORE / 'checkpoint', local_files_only=True, trust_remote_code=False)
    tokenization = read(prior.OUT / 'TOKENIZATION.json')
    assert hashlib.sha256(tokenizer.chat_template.encode()).hexdigest() == tokenization['chat_template_sha256']
    dataset = ROOT / 'benchmark/results/phase6/r6_51/DIRECT.jsonl'
    assert sha(dataset) == tokenization['dataset_sha256']
    selected = {'R6.48/E' + str(i).zfill(2) for i in range(1, 7)}
    rows = [strict(line) for line in dataset.read_text().splitlines()]
    rows = [row for row in rows if row['episode_id'] in selected]
    assert len(rows) == 6 and {r['episode_id'] for r in rows} == selected
    index = read(ROOT / 'benchmark/results/phase6/r6_49/DATASET-INDEX.json')
    entries = {e['episode_id']: e for e in index['entries']}
    records = []
    for row in rows:
        assert row == convert_entry(entries[row['episode_id']])
        ids, labels, measurement = checked_record(row, tokenizer, 2048)
        assert measurement == next(r for r in tokenization['records'] if r['episode_id'] == row['episode_id'])
        try:
            checked_record(row, tokenizer, len(ids) - 1)
        except ValueError as exc:
            assert str(exc) == 'REQUIRED_OUTPUT_WOULD_BE_TRUNCATED'
        else:
            raise AssertionError('overflow accepted')
        padded = labels + [-100] * (2048 - len(labels))
        assert all(v == -100 for v in padded[len(labels):])
        records.append({'episode_id': row['episode_id'], 'family_id': row['family_id'],
                        'component': row['component'], 'split': row['split'],
                        'canonical_record_sha256': hashlib.sha256(dump(row).encode()).hexdigest(),
                        'source_refs': row['provenance']['source_refs'],
                        'source_provenance': row['provenance']['source_provenance'],
                        'tokens_sha256': hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
                        'labels_sha256': hashlib.sha256(json.dumps(labels).encode()).hexdigest(),
                        'tokenization': measurement, 'padding_masked': True, 'overflow_rejected': True})
    write('DATASET-IDENTITIES.json', {'round': 'R6.53', 'source_jsonl_sha256': sha(dataset),
          'admission_index_sha256': baseline['r6_49_index_sha256'], 'selected_count': 6,
          'records': records, 'additional_training_examples': 0, 'semantic_diversity_established': False,
          'supervision': 'completion plus EOS only; prompt, post-EOS newline and padding labels -100'})
    write('PREFLIGHT.json', {'status': 'PASS', 'baseline': baseline, 'r6_52_publication': publication,
          'external_assets': external, 'installed_distributions_verified': len(env['packages']),
          'environment_identity_manifest_sha256': sha(prior.OUT / 'ENVIRONMENT-IDENTITIES.json'),
          'requirements_lock_sha256': env['requirements_lock_sha256'],
          'checkpoint_manifest_sha256': sha(prior.OUT / 'CHECKPOINT.json'),
          'python': sys.version, 'executable': sys.executable, 'model_loaded': False,
          'scope': 'prospective payload/receipt checks; historical HEAD/status assertion not reapplied',
          'optimizer_steps': 0, 'parameter_updates': 0, 'historical_acceptance_executions': 0,
          'P6_A05_content_access': False})
    print('PASS: historical publication, environment, checkpoint, tokenizer and six dataset identities')


def inventory():
    paths = [ROOT / 'benchmark/results/phase6/R6_53-REPORT.md', Path(__file__).resolve()]
    paths += [ROOT / f'docs/{name}-r6.53.md' for name in ('project-overview', 'research-log', 'decisions')]
    paths += [p for p in OUT.iterdir() if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    return sorted(paths)


def manifest():
    return {'round': 'R6.53', 'files': {p.relative_to(ROOT).as_posix():
            {'sha256': sha(p), 'bytes': p.stat().st_size} for p in inventory()},
            'excluded': ['PUBLICATION-IDENTITIES.json', 'VERIFICATION.json']}


def verify():
    assert read(OUT / 'PUBLICATION-IDENTITIES.json') == manifest()
    baseline = prior.baseline()
    previous = identities(ROOT / 'benchmark/results/phase6/r6_52')
    assert baseline == read(OUT / 'PREFLIGHT.json')['baseline']
    assert previous == read(OUT / 'PREFLIGHT.json')['r6_52_publication']
    assert prior.external() == read(OUT / 'PREFLIGHT.json')['external_assets']
    assert not subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).strip()
    allowed = set(manifest()['files']) | {'benchmark/results/phase6/r6_53/' + name
              for name in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')}
    status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True)
    for line in status.splitlines():
        assert line.startswith('?? ') and line[3:].replace('\\', '/') in allowed, line
    for p in inventory():
        data = p.read_bytes()
        text = data.decode('utf-8')
        assert data.endswith(b'\n') and b'\r' not in data
        assert not any(s.endswith((' ', '\t')) for s in text.splitlines())
        assert not re.search(r'(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})', text)
        if p.suffix == '.json':
            read(p)
        if p.suffix == '.py':
            compile(text, str(p), 'exec')
        if p.suffix == '.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if '://' not in target and not target.startswith('#'):
                    resolved = (p.parent / target.split('#')[0]).resolve()
                    assert resolved.is_file() or resolved == OUT / 'VERIFICATION.json', target
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    result = read(OUT / 'RESULT.json')
    assert result['classification'] == 'R6_53_PROTOCOL_HALT' and result['actual_optimizer_steps'] == 0
    return {'round': 'R6.53', 'passed': True, 'manifest_sha256': sha(OUT / 'PUBLICATION-IDENTITIES.json'),
            'payload_files': len(inventory()), 'baseline': baseline, 'tracked_diff_empty': True,
            'git_diff_check_returncode': 0, 'publication_whitespace_links_json_source_checks': 'PASS',
            'credential_pattern_scan': 'PASS', 'preservation_failures': [], 'optimizer_steps': 0}


if __name__ == '__main__':
    os.environ['HF_HUB_OFFLINE'] = '1'
    os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
    mode = sys.argv[1]
    if mode == 'preflight':
        preflight()
    elif mode == 'seal':
        write('PUBLICATION-IDENTITIES.json', manifest())
        write('VERIFICATION.json', verify())
    elif mode == 'check':
        result = verify()
        assert result == read(OUT / 'VERIFICATION.json')
        print(json.dumps(result, sort_keys=True))
    else:
        raise ValueError('unknown mode')
