"""CPU-only frozen-gold/negative controls and fresh-process publication verifier."""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys

import scorer

ROOT = scorer.ROOT
OUT = ROOT / 'benchmark/results/phase6/r6_65'
HERE = Path(__file__).resolve().parent
PYTHON = Path(r'C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52\venv\Scripts\python.exe')
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', CUDA_VISIBLE_DEVICES='', HF_HUB_OFFLINE='1')


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1048576), b''):
            h.update(block)
    return h.hexdigest()


def write(name, value):
    path = OUT / name
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + '\n', encoding='utf-8', newline='\n')


def publication(round_name):
    base = ROOT / 'benchmark/results/phase6' / round_name
    manifest = read(base / 'PUBLICATION-IDENTITIES.json')
    for path, entry in manifest['files'].items():
        assert sha(ROOT / path) == entry['sha256'], path
        assert (ROOT / path).stat().st_size == entry['bytes'], path
    assert sha(base / 'PUBLICATION-IDENTITIES.json') == read(base / 'VERIFICATION.json')['manifest_sha256']
    return dict(manifest_sha256=sha(base / 'PUBLICATION-IDENTITIES.json'), payload_files=len(manifest['files']))


def evaluate():
    assert Path(sys.executable).resolve() == PYTHON.resolve()
    rows = read(ROOT / 'benchmark/results/phase6/r6_64/DATASET.json')['records']
    gold = []
    for row in rows:
        folder = ROOT / 'benchmark/results/phase6/r6_63/episodes' / row['episode_id'].split('/')[-1]
        assert scorer.c.load(row['completion'][0]['content']) == read(folder / 'ACTION.json')
        assert row['before'] == read(folder / 'BEFORE.json')
        assert row['cases'] == read(folder / 'ACCEPTANCE.json')['cases']
        result = scorer.score(row['completion'][0]['content'], row)
        assert result['accepted'], result
        after, validation = scorer.assembly.apply(row['before'], read(folder / 'ACTION.json'))
        assert after == read(folder / 'AFTER.json')
        assert validation == read(folder / 'VALIDATION.json')['native']
        gold.append(dict(episode_id=row['episode_id'], scores=result))

    controls = []

    def control(name, index, mutate=None, text=None, classification='SCHEMA_FAILURE', flags=None, code=None):
        row = rows[index]
        action = scorer.c.load(row['completion'][0]['content'])
        if mutate:
            mutate(action)
        if text is None:
            text = json.dumps(action, separators=(',', ':'), allow_nan=False)
        result = scorer.score(text, row)
        assert not result['accepted'] and result['classification'] == classification, (name, result)
        for key, value in (flags or {}).items():
            assert result[key] is value, (name, key, result)
        if code:
            assert result['error']['code'] == code, (name, result)
        controls.append(dict(name=name, episode_id=row['episode_id'], input=text,
                             expected_classification=classification, expected_flags=flags or {}, expected_code=code, scores=result))

    control('malformed_json', 0, text='{', classification='SERIALIZATION_FAILURE')
    control('duplicate_key', 0, text='{"id":"selected","id":"selected"}', classification='SERIALIZATION_FAILURE')
    control('float_literal', 1, text=rows[1]['completion'][0]['content'].replace('"const":1', '"const":1.0'), classification='SERIALIZATION_FAILURE')
    control('nonfinite_number', 0, text='{"const":NaN}', classification='SERIALIZATION_FAILURE')
    control('fenced_json', 0, text='```json\n'+rows[0]['completion'][0]['content']+'\n```', classification='SERIALIZATION_FAILURE')
    control('trailing_json', 0, text=rows[0]['completion'][0]['content']+' {}', classification='SERIALIZATION_FAILURE')
    control('out_of_range_integer', 0, text='{"const":9223372036854775808}', classification='SERIALIZATION_FAILURE', code='TYPE')
    for text in ('[]', 'null', 'true', '1'):
        control('nonobject_'+text, 0, text=text)
    for key in ('id', 'type', 'deps', 'node'):
        control('missing_'+key, 0, lambda a, key=key: a.pop(key))
    control('extra_top_field', 0, lambda a: a.update(extra=1))
    control('extra_node_field', 0, lambda a: a['node'].update(extra=1))
    control('extra_operand_field', 0, lambda a: a['node']['expr']['add'][0].update(extra=1))
    control('missing_node_expr', 0, lambda a: a['node'].pop('expr'))
    control('wrong_id', 0, lambda a: a.update(id='other'))
    control('wrong_node_operation', 0, lambda a: a['node'].update(op='check'))
    control('unknown_operation', 0, lambda a: a['node'].update(expr={'mul':[{'ref':'arrivals'},{'ref':'reserve'}]}))
    control('two_operations', 0, lambda a: a['node']['expr'].update(eq=[{'ref':'arrivals'},{'ref':'reserve'}]))
    control('wrong_arity', 0, lambda a: a['node']['expr']['add'].pop())
    control('nested_operand', 0, lambda a: a['node']['expr']['add'].__setitem__(0, {'add':[{'ref':'arrivals'},{'ref':'reserve'}]}))
    control('ref_and_const', 0, lambda a: a['node']['expr']['add'][0].update(const=1))
    control('numeric_reference', 0, lambda a: a['node']['expr']['add'][0].update(ref=1))
    control('string_literal', 1, lambda a: a['node']['expr']['add'][0].update(const='1'))
    control('array_literal', 1, lambda a: a['node']['expr']['add'][0].update(const=[]))
    control('unit_result_type', 0, lambda a: a.update(type='Unit'))
    control('duplicate_dependencies', 0, lambda a: a.update(deps=['arrivals','arrivals']))
    control('nonstring_dependency', 0, lambda a: a.update(deps=[1]))
    control('too_many_dependencies', 0, lambda a: a.update(deps=['a','b','c']))
    control('nonarray_dependencies', 0, lambda a: a.update(deps='arrivals'))

    assembly_flags = dict(schema_valid=True, deterministic_assembly=False)
    for name, mutate in (
        ('missing_dependency', lambda a: a.update(deps=['arrivals'])),
        ('wrong_dependency', lambda a: a.update(deps=['arrivals','decoy'])),
        ('unsorted_dependencies', lambda a: a.update(deps=['reserve','arrivals'])),
        ('transitive_dependencies', lambda a: a.update(deps=['base','delta']))):
        control(name, 3 if name == 'transitive_dependencies' else 0, mutate,
                classification='ASSEMBLY_FAILURE', flags=assembly_flags, code='DEPENDENCY')
    control('wrong_result_type', 0, lambda a: a.update(type='Bool'), classification='ASSEMBLY_FAILURE', flags=assembly_flags, code='TYPE')
    control('unknown_reference', 0, lambda a: a['node']['expr']['add'][0].update(ref='absent'), classification='ASSEMBLY_FAILURE', flags=assembly_flags, code='UNKNOWN_REFERENCE')
    control('self_reference', 0, lambda a: a['node']['expr']['add'][0].update(ref='selected'), classification='ASSEMBLY_FAILURE', flags=assembly_flags, code='UNKNOWN_REFERENCE')
    control('malformed_identifier', 0, lambda a: a['node']['expr']['add'][0].update(ref='bad name'), classification='ASSEMBLY_FAILURE', flags=assembly_flags, code='REFERENCE')
    control('bool_not_integer_literal', 1, lambda a: a['node']['expr']['add'][0].update(const=True), classification='ASSEMBLY_FAILURE', flags=assembly_flags, code='LITERAL')
    control('unavailable_literal', 1, lambda a: a['node']['expr']['add'][0].update(const=2), classification='ASSEMBLY_FAILURE', flags=assembly_flags, code='LITERAL')
    control('invalid_operand_type', 0, lambda a: (a['node']['expr']['add'][0].update(ref='decoy'), a.update(deps=['decoy','reserve'])), classification='ASSEMBLY_FAILURE', flags=assembly_flags, code='TYPE')
    control('unit_literal_unavailable', 1, lambda a: a['node']['expr']['add'][0].update(const=None), classification='ASSEMBLY_FAILURE', flags=assembly_flags, code='LITERAL')

    valid_wrong = dict(schema_valid=True, deterministic_assembly=True, behavioral_acceptance=False)
    control('valid_wrong_operation', 7, lambda a: a['node'].update(expr={'le':a['node']['expr']['eq']}), classification='SEMANTIC_MISMATCH', flags=dict(valid_wrong, operation_correct=False))
    control('valid_wrong_operands', 4, lambda a: a['node']['expr']['le'].reverse(), classification='SEMANTIC_MISMATCH', flags=dict(valid_wrong, operands_correct=False))
    control('valid_wrong_literal', 1, lambda a: a['node']['expr']['add'][0].update(const=7), classification='SEMANTIC_MISMATCH', flags=dict(valid_wrong, operands_correct=False))
    control('commutative_swap_selection', 0, lambda a: a['node']['expr']['add'].reverse(), classification='SEMANTIC_MISMATCH', flags=dict(schema_valid=True, deterministic_assembly=True, behavioral_acceptance=True, operands_correct=False))

    # Direct checker preserves exact type distinctions even for host inputs.
    checker_controls = []
    for literal in (1.0, '1', [], {}, 2**63, -(2**63)-1):
        action = scorer.c.load(rows[1]['completion'][0]['content'])
        action['node']['expr']['add'][0]['const'] = literal
        try:
            scorer.validate_action(action)
        except scorer.c.Diagnostic as exc:
            checker_controls.append(dict(literal=literal, rejected=True, error=exc.data))
        else:
            raise AssertionError(literal)
    for literal in (True, False, None, -(2**63), 2**63-1):
        action = scorer.c.load(rows[1]['completion'][0]['content'])
        action['node']['expr']['add'][0]['const'] = literal
        scorer.validate_action(action)  # schema domain, not scope/assembly acceptance

    assert len(gold) == 10
    return dict(gold=gold, negative_controls=controls, checker_controls=checker_controls,
                summary=dict(gold_acceptance=10, dimensions={k:sum(r['scores'][k] for r in gold) for k in scorer.DIMENSIONS},
                             behavioral_fixtures=sum(len(r['scores']['observations']) for r in gold),
                             negative_controls=len(controls), negative_rejected=len(controls),
                             direct_checker_rejections=len(checker_controls)),
                environment=dict(executable=sys.executable, version=sys.version, jsonschema_available=importlib.util.find_spec('jsonschema') is not None,
                                 model_modules_loaded=[n for n in ('torch','transformers','peft','bitsandbytes') if n in sys.modules],
                                 cpu_only=True))


def run():
    assert Path(sys.executable).resolve() == PYTHON.resolve()
    write('SOURCE-FREEZE.json', dict(files={p.relative_to(ROOT).as_posix():sha(p) for p in sorted(HERE.glob('*.py'))},
          schema_sha256=sha(ROOT/'benchmark/results/phase6/r6_63/step-1.schema.json'), model_calls=0, training_updates=0))
    processes, results = [], []
    for _ in range(2):
        args = [str(PYTHON), str(HERE/'qualify.py'), 'evaluate']
        proc = subprocess.run(args, cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=120)
        processes.append(dict(argv=args, returncode=proc.returncode, stdout=proc.stdout, stderr=proc.stderr))
        write(f'PROCESS-{len(processes)}.json', processes[-1])
        assert proc.returncode == 0, proc.stderr
        results.append(json.loads(proc.stdout))
    assert results[0] == results[1]
    assert results[0]['environment']['model_modules_loaded'] == []
    assert not results[0]['environment']['jsonschema_available']
    write('GOLD-ACCEPTANCE.json', dict(records=results[0]['gold'], summary=results[0]['summary']))
    write('NEGATIVE-CONTROLS.json', dict(records=results[0]['negative_controls'], direct_checker=results[0]['checker_controls']))
    write('EXACT-ENVIRONMENT.json', dict(environment=results[0]['environment'], fresh_processes=2,
          results_identical=True, scorer_import_and_execution='PASS', dependency_installations=0,
          installed_package_modifications=0, package_integrity='checked by final inherited baseline audit'))
    print(json.dumps(results[0]['summary'], indent=2))


def seal(check=False):
    assert Path(sys.executable).resolve() == PYTHON.resolve()
    if not check:
        args = [str(PYTHON), str(ROOT/'experiments/incremental_data_r6_63/publish.py'), 'baseline-check']
        proc = subprocess.run(args, cwd=ROOT, env=ENV, capture_output=True, text=True, timeout=600)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        rounds = {name:publication(name) for name in ('r6_59','r6_63','r6_64')}
        supplement = read(ROOT/'benchmark/results/phase6/r6_59/EXECUTABLE-IDENTITY-SUPPLEMENT.json')
        store = PYTHON.parents[2]
        home = store/'python/cpython-3.12.11-windows-x86_64-none'
        paths = dict(python_executable_sha256=home/'python.exe', python_dll_sha256=home/'python312.dll',
                     venv_executable_sha256=PYTHON, uv_executable_sha256=store/'uv/uv.exe',
                     requirements_lock_sha256=ROOT/'benchmark/results/phase6/r6_52/requirements-lock.txt')
        assert {k:sha(p) for k,p in paths.items()} == supplement['identities']
        assert not (ROOT/'benchmark/results/phase6/r6_64/PREFLIGHT.json').exists()
        assert not (store/'r6-64').exists()
        write('BASELINE.json', dict(rounds=rounds, inherited_audit=dict(argv=args,returncode=proc.returncode,stdout=proc.stdout,stderr=proc.stderr),
              executable_identities=supplement['identities'], kernel_constructs=26,
              kernel_basis='unchanged inherited accounting/implementation, not a fresh recount',
              initial_terminal_verifier='PASS before edits under pinned Python; first invocation timed out at120s, unchanged retry passed at600s',
              protected_history_environment_checkpoint_adapter='PASS inherited full identity audit; no packages installed or changed'))
    paths = sorted(list(HERE.glob('*.py')) + [ROOT/'benchmark/results/phase6/R6_65-REPORT.md',
                   ROOT/'docs/research-log-r6.65.md'] + [p for p in OUT.iterdir() if p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')])
    for path in paths:
        text = path.read_text(encoding='utf-8')
        assert '\r' not in text and all(line == line.rstrip() for line in text.splitlines()), path
        if path.suffix == '.json': json.loads(text)
        if path.suffix == '.py': ast.parse(text)
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|'+'-----BEGIN '+r'[A-Z ]*'+'PRIVATE KEY-----', text), path
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                assert (path.parent/link.split('#')[0]).resolve().exists(), (path,link)
    status = subprocess.check_output(['git','status','--porcelain','--untracked-files=all'], cwd=ROOT, text=True)
    allowed = ('experiments/incremental_scorer_r6_65/', 'benchmark/results/phase6/r6_65/',
               'benchmark/results/phase6/R6_65-REPORT.md', 'docs/research-log-r6.65.md')
    assert all(line[3:].replace('\\','/').startswith(allowed) for line in status.splitlines()), status
    subprocess.run(['git','diff','--check'], cwd=ROOT, check=True)
    frozen = read(OUT/'SOURCE-FREEZE.json')
    assert all(sha(ROOT/path)==digest for path,digest in frozen['files'].items())
    assert sha(ROOT/'benchmark/results/phase6/r6_63/step-1.schema.json') == frozen['schema_sha256']
    manifest = dict(version='r6.65-publication-1', files={p.relative_to(ROOT).as_posix():dict(sha256=sha(p),bytes=p.stat().st_size) for p in paths})
    if check:
        assert manifest == read(OUT/'PUBLICATION-IDENTITIES.json')
        assert sha(OUT/'PUBLICATION-IDENTITIES.json') == read(OUT/'VERIFICATION.json')['manifest_sha256']
        for name in ('r6_59','r6_63','r6_64'): publication(name)
    else:
        write('PUBLICATION-IDENTITIES.json', manifest)
        write('VERIFICATION.json', dict(passed=True,manifest_sha256=sha(OUT/'PUBLICATION-IDENTITIES.json'),
              historical_publications='PASS', installed_packages_checkpoint_adapter='PASS full inherited audit',
              json_python_links_whitespace_credentials='PASS', additive_scope='PASS', git_diff_check='PASS',
              model_calls=0, optimizer_updates=0, scheduler_updates=0, fine_tuning=0,
              kernel_constructs=26, execution_semantic_changes=0, dataset_expansion=0,
              P6_A04_acceptance=0, P6_A05_access=False))
    print('PASS R6.65 publication integrity; preserved history; zero model/training dispatch')


if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'evaluate': print(json.dumps(evaluate(), sort_keys=True, allow_nan=False))
    elif mode == 'run': run()
    elif mode == 'seal': seal()
    elif mode == 'check': seal(check=True)
    else: raise ValueError(mode)
