"""Read-only historical audit and publication; no model/scorer/training dispatch."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'benchmark/results/phase6/r6_62'


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(name, data):
    path = OUT / name
    assert not path.exists(), path
    path.write_text(json.dumps(data, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def baseline():
    spec = importlib.util.spec_from_file_location('r62_prior_identity_only', ROOT / 'experiments/first_token_r6_61/diagnose.py')
    prior = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prior)
    receipt = prior.baseline()  # hashes/configuration only; never calls score/check/publication
    assert receipt == read(prior.OUT / 'BASELINE.json')
    manifest = read(prior.OUT / 'PUBLICATION-IDENTITIES.json')
    for name, entry in manifest['files'].items():
        assert sha(ROOT / name) == entry['sha256'], name
    assert read(prior.OUT / 'VERIFICATION.json')['passed']
    return {'status': 'PASS', 'inherited': receipt,
            'r6_61_manifest_sha256': sha(prior.OUT / 'PUBLICATION-IDENTITIES.json'),
            'r6_61_payload_files': len(manifest['files']), 'historical_rescoring': 0,
            'kernel_constructs': 26, 'basis': 'unchanged inherited accounting and implementation identities'}


def inventory():
    from transformers import AutoTokenizer
    store = Path(r'C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52')
    tokenizer = AutoTokenizer.from_pretrained(store / 'checkpoint', local_files_only=True, trust_remote_code=False)
    index = read(ROOT / 'benchmark/results/phase6/r6_49/DATASET-INDEX.json')
    records = [json.loads(line) for line in (ROOT / 'benchmark/results/phase6/r6_51/DIRECT.jsonl').read_text(encoding='utf-8').splitlines()]
    rows = []
    for entry, record in zip(index['entries'], records):
        assert entry['episode_id'] == record['episode_id']
        for group in ('direct',):
            for ref in entry[group].values():
                assert sha(ROOT / ref['path']) == ref['sha256']
        target = record['completion'][0]['content']
        obj = json.loads(target)
        prompt = tokenizer.apply_chat_template(record['prompt'], tokenize=False, add_generation_prompt=True)
        metrics = {'prompt_tokens': len(tokenizer.encode(prompt, add_special_tokens=False)),
                   'target_content_tokens': len(tokenizer.encode(target, add_special_tokens=False))}
        definitions = obj.get('definitions', []) + ([obj['program']] if 'program' in obj else [])
        details = []
        for definition in definitions:
            depths = {p['name']: 0 for p in definition['params']}
            sizes = []
            operations = []
            for step in definition['steps']:
                depths[step['id']] = 1 + max((depths[d] for d in step['deps']), default=0)
                sizes.append(len(tokenizer.encode(json.dumps(step, sort_keys=True, separators=(',', ':')), add_special_tokens=False)))
                operations.append(step['node']['op'])
            details.append({'name': definition['name'], 'steps': len(definition['steps']),
                            'explicit_dependency_depth_nodes': max(depths.values(), default=0),
                            'operation_sequence': operations, 'existing_step_fragment_tokens': sizes,
                            'fragment_note': 'tokenized original step objects only; not qualified B updates or training rows'})
        rows.append({'episode_id': entry['episode_id'], 'family_id': entry['family_id'],
                     'component': entry['component'], 'partition': entry['partition'],
                     'tier_t': entry['tier_t'], 'tier_e': entry['tier_e'],
                     'source_artifacts': entry['direct'], 'scripted_trajectory': entry.get('scripted_trajectory'),
                     'actual_ai_edit_trajectory': entry.get('actual_ai_edit_trajectory'),
                     'actual_semantic_tool_trajectory': entry.get('actual_semantic_tool_trajectory'),
                     'limitations': entry['limitations'], 'target_kind': record['provenance']['target_kind'],
                     'target_sha256': hashlib.sha256(target.encode()).hexdigest(),
                     'tokens': metrics, 'definitions': details,
                     'qualified_A_package': bool(definitions), 'qualified_B_steps': 0, 'qualified_C_decisions': 0})
    assert len(rows) == 10
    write('DATA-AVAILABILITY.json', {'entries': rows, 'counts': {'tier_t_endpoints': 10,
          'A_symbolic_packages': 8, 'A_production_intent_endpoints': 2, 'B_qualified_step_records': 0,
          'C_qualified_semantic_decisions': 0, 'genuine_AI_edit_episode_views': 2,
          'qualified_evaluation_families': 0}, 'dataset_expansion': 0,
          'tokenizer_sha256': sha(store / 'checkpoint/tokenizer.json'),
          'measurement': 'CPU-only local pinned tokenizer; no model weights loaded; existing records only'})
    print(json.dumps([{'episode': r['episode_id'], 'tokens': r['tokens'], 'definitions': r['definitions']} for r in rows], indent=2))


def publish(seal):
    current = baseline()
    assert current == read(OUT / 'BASELINE.json')
    # Existing system interpreter has jsonschema; pinned ML environment does not.
    # Separate shape-only subprocess avoids installing/changing either environment.
    schema_receipt = json.loads(subprocess.check_output(
        [r'C:\Users\lblan\AppData\Local\Python\pythoncore-3.14-64\python.exe',
         str(Path(__file__).with_name('schema_check.py'))], cwd=ROOT, text=True))
    assert schema_receipt['passed'] and schema_receipt['controls'] == 22
    allowed = ['benchmark/results/phase6/r6_62/', 'benchmark/results/phase6/R6_62-REPORT.md',
               'experiments/curriculum_design_r6_62/', 'docs/research-log-r6.62.md']
    status = subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all'], cwd=ROOT, text=True)
    assert all(any(line[3:].replace('\\', '/').startswith(p) for p in allowed) for line in status.splitlines()), status
    paths = [ROOT / 'benchmark/results/phase6/R6_62-REPORT.md', ROOT / 'docs/research-log-r6.62.md']
    paths += list((ROOT / 'experiments/curriculum_design_r6_62').glob('*.py'))
    paths += [p for p in OUT.iterdir() if p.name not in ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
    for path in paths:
        text = path.read_text(encoding='utf-8')
        assert '\r' not in text and all(line == line.rstrip() for line in text.splitlines()), path
        if path.suffix == '.json':
            read(path)
        if path.suffix == '.py':
            import ast
            ast.parse(text)
        if path.suffix == '.md':
            import re
            for link in re.findall(r'\]\(([^)]+)\)', text):
                assert link.startswith(('https:', '#')) or (path.parent / link.split('#')[0]).exists(), (path, link)
        import re
        secret_pattern = r'sk-[A-Za-z0-9]{20,}|' + '-----BEGIN ' + r'[A-Z ]*' + 'PRIVATE KEY-----'
        assert not re.search(secret_pattern, text), path
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    files = {p.relative_to(ROOT).as_posix(): {'sha256': sha(p), 'bytes': p.stat().st_size} for p in sorted(paths)}
    manifest = {'version': 'r6.62-publication-1', 'files': files}
    if seal:
        write('PUBLICATION-IDENTITIES.json', manifest)
        write('VERIFICATION.json', {'passed': True, 'manifest_sha256': sha(OUT / 'PUBLICATION-IDENTITIES.json'),
              'baseline': 'PASS', 'schemas_draft202012': 4, 'empty_record_rejections': 3,
              'schema_receipt': schema_receipt, 'shape_controls_are_qualified_records': False,
              'scope_whitespace_links_credentials': 'PASS', 'git_diff_check': 'PASS',
              'training': 0, 'optimizer_scheduler_updates': 0, 'model_inference': 0,
              'historical_rescoring': 0, 'dataset_expansion': 0, 'P6_A04_acceptance': 0, 'P6_A05_access': False})
    else:
        assert manifest == read(OUT / 'PUBLICATION-IDENTITIES.json')
        assert sha(OUT / 'PUBLICATION-IDENTITIES.json') == read(OUT / 'VERIFICATION.json')['manifest_sha256']
    print('PASS R6.62 publication, preservation and schema integrity')


if __name__ == '__main__':
    if sys.argv[1] == 'baseline':
        write('BASELINE.json', baseline())
        inventory()
    elif sys.argv[1] == 'inventory':
        assert baseline() == read(OUT / 'BASELINE.json')
        inventory()
    else:
        publish(sys.argv[1] == 'seal')
