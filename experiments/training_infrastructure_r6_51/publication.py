"""Seal/check additive R6.51 publication; never run model or functional acceptance."""
import argparse
import os
import re
import subprocess
import sys
from pathlib import Path
from convert import ROOT, OUT, read, sha, dump, write, seal_check, build, strict

HERE = Path(__file__).resolve().parent
MANIFEST = OUT / 'PUBLICATION-IDENTITIES.json'
RECEIPT = OUT / 'VERIFICATION.json'


def inventory():
    paths = [ROOT / 'benchmark/results/phase6/R6_51-REPORT.md']
    paths += [ROOT / f'docs/{name}-r6.51.md' for name in ('project-overview', 'research-log', 'decisions')]
    for folder in (HERE, OUT):
        paths += [p for p in folder.rglob('*') if p.is_file() and '__pycache__' not in p.parts
                  and p not in (MANIFEST, RECEIPT)]
    return sorted(paths)


def make_manifest():
    return {'round': 'R6.51', 'excluded': [MANIFEST.name, RECEIPT.name], 'baseline': seal_check(),
            'previous_publication_receipt_sha256': sha(ROOT / 'benchmark/results/phase6/r6_50/VERIFICATION.json'),
            'files': {p.relative_to(ROOT).as_posix(): {'bytes': p.stat().st_size, 'sha256': sha(p)} for p in inventory()}}


def qualify():
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
    args = [sys.executable, '-m', 'unittest', 'discover', '-s',
            'experiments/training_infrastructure_r6_51', '-p', 'test_convert.py', '-v']
    proc = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True, timeout=120)
    write(OUT / 'TESTS.json', {'argv': args, 'returncode': proc.returncode, 'stdout': proc.stdout,
        'stderr': proc.stderr, 'scope': 'conversion, schema, unchanged wrapper validation, identity and leakage controls; no functional acceptance or ML execution'})
    if proc.returncode:
        raise ValueError(proc.stderr)
    print(proc.stderr)


def verify():
    manifest = read(MANIFEST)
    if manifest != make_manifest():
        raise ValueError('publication/baseline mismatch')
    records, assessment = build()
    actual = [strict(line) for line in (OUT / 'DIRECT.jsonl').read_text(encoding='utf-8').splitlines()]
    if records != actual or assessment != read(OUT / 'CONVERSION-ASSESSMENT.json'):
        raise ValueError('conversion regeneration mismatch')
    if (OUT / 'TOOL.jsonl').read_bytes() != b'':
        raise ValueError('fabricated tool export')
    from jsonschema import Draft202012Validator
    for name in ('training-record-1.schema.json', 'tool-decision-1.schema.json'):
        Draft202012Validator.check_schema(read(OUT / name))
    validator = Draft202012Validator(read(OUT / 'training-record-1.schema.json'))
    for record in records:
        validator.validate(record)
    tests = read(OUT / 'TESTS.json')
    if tests['returncode'] != 0 or 'Ran 8 tests' not in tests['stderr']:
        raise ValueError('test qualification unavailable')
    links = 0
    for path in inventory():
        data = path.read_bytes()
        text = data.decode('utf-8')
        if data and (not data.endswith(b'\n') or b'\r' in data):
            raise ValueError('non-LF publication: ' + str(path))
        if any(line.endswith((' ', '\t')) for line in text.splitlines()):
            raise ValueError('trailing whitespace: ' + str(path))
        if re.search(r'(?:sk-[A-Za-z0-9_-]{32,}|ghp_[A-Za-z0-9]{32,}|hf_[A-Za-z0-9]{32,})', text):
            raise ValueError('credential-like publication string')
        if path.suffix == '.json':
            read(path)
        if path.suffix == '.py':
            compile(text, str(path), 'exec')
        if path.suffix == '.md':
            for target in re.findall(r'\[[^\]]+\]\(([^)]+)\)', text):
                if '://' in target or target.startswith('#'):
                    continue
                resolved = (path.parent / target.split('#')[0]).resolve()
                if not resolved.is_relative_to(ROOT) or not (resolved.exists() or resolved == RECEIPT):
                    raise ValueError('broken publication link: ' + target)
                links += 1
    if subprocess.check_output(['git', 'diff', '--name-only'], cwd=ROOT, text=True).strip():
        raise ValueError('unexpected tracked edit')
    allowed = set(manifest['files']) | {p.relative_to(ROOT).as_posix() for p in (MANIFEST, RECEIPT)}
    status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True)
    for line in status.splitlines():
        if not line.startswith('?? ') or line[3:].replace('\\', '/') not in allowed:
            raise ValueError('unexpected worktree file: ' + line)
    proc = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    if proc.returncode:
        raise ValueError(proc.stdout + proc.stderr)
    return {'round': 'R6.51', 'classification': 'R6_51_HARDWARE_OR_STACK_GAP', 'passed': True,
        'manifest_sha256': sha(MANIFEST), **manifest['baseline'], 'publication_payload_files': len(manifest['files']),
        'publication_payload_bytes': sum(v['bytes'] for v in manifest['files'].values()),
        'test_methods_passed': 8, 'direct_records': 10, 'genuine_semantic_tool_records': 0,
        'full_outer_json_schema_validation': True, 'target_wrapper_validations': 8, 'target_intent_schema_validations': 2,
        'relative_links_checked': links, 'conversion_regeneration_matches': True,
        'tracked_diff_empty': True, 'git_diff_check_returncode': 0, 'preservation_failures': [],
        'training_runs': 0, 'model_inference_calls': 0, 'weight_downloads': 0, 'dependency_installs': 0,
        'historical_acceptance_executions': 0, 'P6_A05_content_access': False,
        'ready_for_training': False, 'cuda_training_allocation': 'NOT_RUN'}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('qualify', 'seal', 'check'))
    args = parser.parse_args()
    if args.mode == 'qualify':
        qualify()
    elif args.mode == 'seal':
        write(MANIFEST, make_manifest())
        result = verify()
        write(RECEIPT, result)
        print(dump(result))
    else:
        result = verify()
        if result != read(RECEIPT):
            raise ValueError('receipt mismatch')
        print(dump(result))


if __name__ == '__main__':
    main()
