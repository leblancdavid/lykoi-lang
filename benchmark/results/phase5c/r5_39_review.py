"""R5.39 recorder: independent validation first; one locked static-only B02 pass."""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import types as python_types
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
RESULTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from benchmark.semantic import boundary_study_r5_39 as study
from benchmark.semantic import boundary_faults_r5_39 as faults
from benchmark.semantic import application_boundary_r5_39 as boundary
from benchmark.semantic import readiness_r5_39 as readiness
from benchmark.semantic import readiness_r5_38 as previous
from benchmark.semantic import nullable_study_r5_38 as nullable
from benchmark.semantic import unified_types_r5_27 as authority
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import refined_generator_r5_28 as emitter
from benchmark.results.phase5c.r5_38_review import run_suite


def write(name, data):
    (RESULTS / name).write_bytes(emitter.canonical(data) + b'\n')


def reconstruction():
    import copy
    source = subprocess.check_output(['git', 'show',
        '4dc980f:benchmark/semantic/unified_types_r5_27.py'], cwd=ROOT, text=True)
    module = python_types.ModuleType('r539_locked_r538_analyzer')
    sys.modules[module.__name__] = module
    exec(compile(source, '<R5.38 locked analyzer>', 'exec'), module.__dict__)
    optional_source = subprocess.check_output(['git', 'show',
        '428a340:benchmark/semantic/unified_types_r5_27.py'], cwd=ROOT, text=True)
    optional_baseline = python_types.ModuleType('r539_historical_optional_analyzer')
    sys.modules[optional_baseline.__name__] = optional_baseline
    exec(compile(optional_source, '<historical optional analyzer>', 'exec'), optional_baseline.__dict__)
    report = []
    for field, declaration in [('x', {'optional': 'instant'}), ('x', {'nullable': 'instant'}),
                               ('x', {'optional': {'nullable': 'instant'}})]:
        state = {'sequence': {'record': {'x': declaration}}}
        optional = 'optional' in declaration
        inner = declaration.get('optional', declaration)
        guards = ([{'present': nullable.ref('item', field)}] if optional else [])
        if isinstance(inner, dict) and 'nullable' in inner:
            guards.append(nullable.non_null(field))
        p = {'before': [nullable.ref('item', field), nullable.lit(nullable.CUTOFF, 'instant')]}
        for parts in [guards + copy.deepcopy(guards) + [p], guards + [p] + copy.deepcopy(guards),
                      [p] + guards + copy.deepcopy(guards)]:
            where = {'and': parts}
            expression = {'order': {'source': {'select': {'source': nullable.ref('pre'), 'where': where}}, 'keys': ['x']}}
            contract = {'id': 'independent.minimal', 'version': 'R5.27', 'input': {'record': {}}, 'state': state,
                'branches': [{'tag': 'ok', 'when': nullable.lit(True, 'boolean'), 'value': expression,
                              'value_type': state, 'transition': {'preserve': True}},
                             {'tag': 'other', 'when': None, 'value': nullable.lit('other'),
                              'value_type': 'string', 'transition': {'preserve': True}}]}
            try:
                module.checked_plan(contract)
                old = None
            except ValueError as exc:
                old = str(exc)
            plan = authority.checked_plan(contract)
            baseline_accepts = None
            if declaration == {'optional': 'instant'}:
                optional_baseline.checked_plan(contract).assert_invariants()
                baseline_accepts = True
            report.append({'source': contract, 'R5_38_diagnostic': old, 'current_valid': True,
                           'historical_optional_accepts': baseline_accepts,
                           'facts': list(plan.refinement_facts.values())})
    return {'historical_source': emitter.sha(source.encode()), 'cases': report}


def evidence():
    import copy
    matrix = readiness.closure_matrix()
    write('R5_39-refinement-reconstruction.json', reconstruction())
    write('R5_39-domain-refinement-matrix.json', matrix)
    write('R5_39-aggregate-profile-schema.json', boundary.SCHEMA)
    base = previous.validate_matrix_pipeline()
    duplicate = [row for row in matrix['rows'] if row['provider_dimension'] == 'duplicate_equivalent']
    with patch.object(previous, 'closure_matrix', return_value={'rows': duplicate}):
        transfer = previous.validate_matrix_pipeline()
    write('R5_39-domain-pipeline-evidence.json', {'base': base, 'duplicate_equivalent': transfer})
    app, spec, state, config = study.setup()
    with (patch.object(pipeline, 'generate', side_effect=AssertionError('static emission forbidden')),
          patch.object(emitter, 'generated_unit', side_effect=AssertionError('static rendering forbidden'))):
        ready = readiness.inspect(app, spec, state, config)
        broken = copy.deepcopy(spec)
        broken['operations'][0]['alternatives']['V1']['semantic'] = 'absent'
        broken['operations'][1]['alternatives']['V2']['arguments'] = []
        bad_state = copy.deepcopy(state)
        del bad_state['alternatives']['V2']
        bad_config = copy.deepcopy(config)
        bad_config['store']['path'] = '../wrong'
        negative = readiness.inspect(app, broken, bad_state, bad_config)
    if ready['status'] != 'READY' or negative['status'] != 'NOT_READY':
        raise ValueError('independent prediction failure')
    write('R5_39-independent-readiness.json', ready)
    write('R5_39-negative-readiness.json', {'application': app, 'transport': broken, 'state': bad_state,
                                         'launch': bad_config, 'readiness': negative})
    write('R5_39-whole-boundary-evidence.json', study.study())
    write('R5_39-boundary-fault-evidence.json', faults.faults())
    # A source-only migration change composes unchanged metadata infrastructure.
    app['operations']['migrate']['branches'][0]['transition']['relations'][0]['default_missing']['value'] = study.lit('cold')
    app['operations']['migrate']['branches'][1]['transition']['relations'][0]['default_missing']['value'] = study.lit('cold')
    with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as directory:
        root, cwd = Path(bundle), Path(directory)
        boundary.generate(app, root, spec, state, config)
        (cwd / config['store']['path']).write_bytes(emitter.canonical({'revision': 1, 'seeds': [{'code': 'S1', 'label': 'Iris'}]}))
        call = study.capture(app, root, cwd, spec, state, config, ['migrate'])
        write('R5_39-semantic-mutation.json', {'source': app, 'call': call})
    print(json.dumps({'matrix_rows': len(matrix['rows']), 'base_transfers': len(base), 'duplicate_transfers': len(transfer),
                      'independent_status': ready['status'], 'negative_gaps': len(negative['gaps'])}))


def verify():
    import os
    report = {'version': 'R5.39', 'python': sys.version, 'suites': [], 'commands': [],
              'b02_generated': False, 'b02_executed': False, 'frozen_acceptance_ran': False}
    for directory, pattern, restricted in [('benchmark/harness', 'test*.py', True), ('tests', 'test*.py', False),
                                           ('benchmark/results/phase5c', 'test_r5_37_evaluation.py', True)]:
        result = run_suite(directory, pattern, restricted)
        for item in result['skipped']:
            item['reason'] = item['reason'].replace('R5.38', 'R5.39')
        report['suites'].append(result)
    for command in [[sys.executable, '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'], ['git', 'diff', '--check']]:
        completed = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'}, capture_output=True, text=True)
        report['commands'].append({'command': command, 'exit': completed.returncode,
                                  'stdout': completed.stdout, 'stderr': completed.stderr})
        print(json.dumps(report['commands'][-1]))
    write('R5_39-verification.json', report)
    return all(s['successful'] for s in report['suites']) and all(c['exit'] == 0 for c in report['commands'])


def audit_evidence():
    def read(name):
        return json.loads((RESULTS / name).read_bytes())
    reconstruction = read('R5_39-refinement-reconstruction.json')
    assert len(reconstruction['cases']) == 9
    assert all(c['current_valid'] and 'ordering refinement' in c['R5_38_diagnostic'] for c in reconstruction['cases'])
    assert sum(c['historical_optional_accepts'] is True for c in reconstruction['cases']) == 3
    matrix = read('R5_39-domain-refinement-matrix.json')
    assert len(matrix['rows']) == 336 and matrix['base_rows'] == 84
    transfer = read('R5_39-domain-pipeline-evidence.json')
    counts = {}
    for name, rows in transfer.items():
        assert len(rows) == 84
        accepted = [row for row in rows if row['status'] == 'VALIDATED']
        rejected = [row for row in rows if row['status'] == 'REJECTED_BEFORE_GENERATION']
        assert len(accepted) == 64 and len(rejected) == 20
        verdicts = [v for row in accepted for v in row['verdicts']]
        assert len(verdicts) == 128 and all(v['grounded'] and v['conformant'] for v in verdicts)
        counts[name] = {'accepted': 64, 'rejected': 20, 'grounded_calls': 128}
    normal = read('R5_39-whole-boundary-evidence.json')
    assert len(normal['calls']) == 14 and len(normal['invalid_populations']) == 7
    assert all(False not in call['verdict'].values() for call in normal['calls'] + list(normal['invalid_populations'].values()))
    assert all(call['pre'] == call['post'] and call['evidence']['semantic'] is None for call in normal['invalid_populations'].values())
    injected = read('R5_39-boundary-fault-evidence.json')
    assert set(injected) == set('ABCDEFGHIJKL') and all(False in call['verdict'].values() for call in injected.values())
    mutated = read('R5_39-semantic-mutation.json')['call']
    assert all(mutated['verdict'].values()) and json.loads(mutated['post'])['seeds'][0]['storage'] == 'cold'
    assert read('R5_39-independent-readiness.json')['status'] == 'READY'
    negative = read('R5_39-negative-readiness.json')['readiness']
    assert negative['status'] == 'NOT_READY'
    assert {'binding', 'state', 'transport', 'launch', 'application_profile'} <= {g['stage'] for g in negative['gaps']}
    result = {'valid': True, 'matrix_rows': 336, 'transfers': counts, 'public_calls': 21, 'fault_calls': 12,
              'semantic_mutations': 1, 'reconstruction_cases': 9,
              'evidence_hashes': {p.name: emitter.sha(p.read_bytes()) for p in sorted(RESULTS.glob('R5_39-*.json'))
                if p.name not in ('R5_39-implementation-lock.json', 'R5_39-B02-static-readiness.json', 'R5_39-evidence-audit.json')}}
    write('R5_39-evidence-audit.json', result)
    print(json.dumps({key: value for key, value in result.items() if key != 'evidence_hashes'}))
    return result


def lock():
    if (RESULTS / 'R5_39-B02-static-readiness.json').exists():
        raise ValueError('post-static lock replacement prohibited')
    tracked = subprocess.check_output(['git', 'ls-files'], cwd=ROOT, text=True).splitlines()
    untracked = subprocess.check_output(['git', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    files = [name for name in tracked + untracked if name.startswith(('benchmark/', 'src/', 'schema/', 'generated/'))]
    files += ['docs/boundary-closure-r5.39.md']
    excluded = ('R5_39-implementation-lock.json', 'R5_39-B02-static-readiness.json',
                'R5_39-REFINEMENT-DEPENDENCY-WHOLE-CONTRACT-BOUNDARY-CLOSURE.md')
    files = [name for name in files if not name.endswith(excluded)]
    verification = json.loads((RESULTS / 'R5_39-verification.json').read_bytes())
    if not all(s['successful'] for s in verification['suites']) or not all(c['exit'] == 0 for c in verification['commands']):
        raise ValueError('cannot lock failed verification')
    record = {'version': 'R5.39', 'time': datetime.now(timezone.utc).isoformat(),
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'status': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
        'matrix_identity': emitter.sha((RESULTS / 'R5_39-domain-refinement-matrix.json').read_bytes()),
        'aggregate_schema_identity': boundary.SCHEMA_ID,
        'files': {name: emitter.sha((ROOT / name).read_bytes()) for name in sorted(set(files))}}
    record['identity'] = emitter.sha(emitter.canonical(record))
    write('R5_39-implementation-lock.json', record)
    return record


def verify_lock():
    record = json.loads((RESULTS / 'R5_39-implementation-lock.json').read_bytes())
    identity = record.pop('identity')
    mismatches = [name for name, digest in record['files'].items() if emitter.sha((ROOT / name).read_bytes()) != digest]
    if mismatches or identity != emitter.sha(emitter.canonical(record)) or record['head'] != subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip():
        raise ValueError({'lock_mismatches': mismatches})
    return {'identity': identity, 'protected_files': len(record['files']), 'valid': True}


def frozen_static():
    output = RESULTS / 'R5_39-B02-static-readiness.json'
    if output.exists():
        raise ValueError('one frozen static pass already recorded')
    before = verify_lock()
    path = RESULTS / 'R5_37-b02-semantic-application.json'
    application = json.loads(path.read_bytes())
    obligations = [{'kind': 'public_state_alternatives', 'reference': 'R5.37 C18-C23',
                    'public': ['list', 'list-high', 'list-overdue', 'migrate']},
                   {'kind': 'durable_content_constraints', 'reference': 'R5.37 C07/C18-C23',
                    'constraints': ['unique identities', 'nonblank identities/titles', 'status domain', 'priority domain']}]
    with (patch.object(pipeline, 'generate', side_effect=AssertionError('B02 generation prohibited')),
          patch.object(emitter, 'generated_unit', side_effect=AssertionError('B02 rendering prohibited'))):
        result = readiness.inspect(application, obligations=obligations)
    result.update({'source_sha256': emitter.sha(path.read_bytes()), 'lock_before': before,
                   'lock_after': verify_lock(), 'obligations': obligations, 'retry_recommended': result['status'] == 'READY'})
    write(output.name, result)
    print(json.dumps({'status': result['status'], 'operations': len(result['operations']), 'gaps': result['gaps']}, indent=2))


if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'evidence':
        evidence()
    elif command == 'verify':
        sys.exit(0 if verify() else 1)
    elif command == 'lock':
        print(json.dumps({'identity': lock()['identity']}))
    elif command == 'lock-check':
        print(json.dumps(verify_lock()))
    elif command == 'static':
        frozen_static()
    elif command == 'audit':
        audit_evidence()
    else:
        raise ValueError('unknown command')
