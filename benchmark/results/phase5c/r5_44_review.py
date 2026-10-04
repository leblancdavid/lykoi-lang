"""R5.44 observation-only orchestration of frozen, qualified generic machinery.

No repair or retry entry exists. B02 is loaded only inside Recorder.observe.
"""

from datetime import datetime, timezone
import os
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
RESULTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from benchmark.evaluation.recorder_r5_43 import Recorder, ProtocolFailure, PROTOCOL, canonical, digest, equivalent, loads, persist
from benchmark.results.phase5c.r5_43_qualification import historical_lock, check_qualification_lock, contamination
from benchmark.results.phase5c.r5_42_review import authority
from benchmark.results.phase5c.r5_41_review import matrix
from benchmark.results.phase5c.r5_38_review import run_suite
from benchmark.harness.test_optional_support_r5_41 import setup
from benchmark.semantic import application_boundary_r5_41 as boundary
from benchmark.semantic import readiness_r5_41 as readiness
from benchmark.semantic import profile_audit_r5_41 as audit
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import refined_generator_r5_28 as emitter

RUN = RESULTS / 'R5_44-recorder'
DOCS = {'docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md'}


def read(name):
    return loads((RESULTS / name).read_bytes())


def write(name, value):
    persist(RESULTS / name, value)


def checks(qualification=False):
    result = {'historical_lock': historical_lock('R5_40-implementation-profile-lock.json'),
              'prospective_lock': historical_lock('R5_41-implementation-lock.json'),
              'infrastructure_lock': check_qualification_lock(), 'frozen_authority': authority(),
              'implementation_contamination': contamination(), 'core_constructs': boundary.SCHEMA['core_constructs'],
              'suites': [], 'commands': []}
    suites = [('benchmark/harness', 'test*.py', True), ('tests', 'test*.py', False),
              ('benchmark/harness', 'test_optional_support_r5_41.py', True)]
    if qualification:
        suites.insert(0, ('benchmark/harness', 'test_canonical_evidence_r5_43.py', True))
    for directory, pattern, restrictions in suites:
        suite = run_suite(directory, pattern, restrictions)
        for skip in suite['skipped']:
            skip['reason'] = skip['reason'].replace('R5.38', 'R5.44')
        result['suites'].append(suite)
    for command in ([sys.executable, '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
                    ['git', 'diff', '--check']):
        p = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'}, capture_output=True, text=True)
        result['commands'].append({'command': command, 'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr})
    saved = read('R5_41-independent-coherence-matrix.json')
    fresh = matrix()
    result['matrix'] = {'profiles': len(fresh['profiles']), 'rows': len(fresh['rows']),
                        'canonical_equal': equivalent(fresh, saved), 'sha256': digest(canonical(fresh)),
                        'coherent_profiles': len(fresh['profiles'])}
    app, spec, state, config = setup()
    configuration = {'transport': spec, 'state': state, 'launch': config}
    reference = 'benchmark/harness/test_optional_support_r5_41.py'
    traces = [{'path': path, 'value': value, 'artifact': reference,
               'sha256': digest((ROOT / reference).read_bytes()), 'clause': 'setup',
               'interpretation': 'Independent declared shape and public mapping.'}
              for path, value in audit.leaves(configuration)]
    result['independent_structure'] = audit.structure(configuration)
    result['independent_traceability'] = audit.traceability(configuration, traces, ROOT, {reference})
    result['independent_profile_contamination'] = audit.contamination(configuration)
    result['successful'] = (all(s['successful'] for s in result['suites']) and
                            all(c['exit'] == 0 for c in result['commands']) and
                            result['matrix']['canonical_equal'] and len(fresh['profiles']) == 16 and
                            len(fresh['rows']) == 84 and result['core_constructs'] == 30 and
                            result['independent_structure']['valid'] and result['independent_traceability']['valid'] and
                            not result['independent_profile_contamination'] and
                            all(len(s['skipped']) == 36 for s in result['suites'] if s['directory'] == 'benchmark/harness' and s['pattern'] == 'test*.py'))
    return result


def prepass():
    if RUN.exists() or (RESULTS / 'R5_44-prepass.json').exists():
        raise ProtocolFailure('R5.44 already started; replacement/retry prohibited')
    result = checks(True)
    inherited = read('R5_43-qualification.json')
    result.update({'inherited_classification': inherited['primary_classification'], 'protocol': PROTOCOL,
                   'recorder_version': 'recorder_r5_43.py',
                   'recorder_sha256': digest((ROOT / 'benchmark/evaluation/recorder_r5_43.py').read_bytes()),
                   'protocol_sha256': digest((ROOT / 'docs/canonical-evidence-r5.43.md').read_bytes()),
                   'r5_42_classification': read('R5_42-halt-verification.json')['primary_classification'],
                   'b02_static_dispatches': 0, 'b03_prospectively_touched': False,
                   'b17_exposed': False, 'b17_classified': False, 'phase5c': 'paused'})
    result['successful'] = (result['successful'] and inherited['successful'] and
                           inherited['primary_classification'] == 'R5_43_EVALUATION_INFRASTRUCTURE_QUALIFIED' and
                           result['r5_42_classification'] == 'R5_42_PROTOCOL_HALT')
    write('R5_44-prepass.json', result)
    if not result['successful']:
        write('R5_44-classification.json', {'primary_classification': 'R5_44_PROTOCOL_HALT', 'stage': 'before exposure', 'dispatches': 0})
        raise ProtocolFailure('qualified starting state not established')
    RUN.mkdir(exist_ok=False)
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    protected = [ROOT / n for n in sorted(set(names)) if n not in DOCS and
                 '/R5_44-' not in n]
    protected.append(RESULTS / 'R5_44-prepass.json')
    r = Recorder(RUN)
    baseline = {'experiment': 'R5.44', 'pre_exposure': result,
                'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
                'time': datetime.now(timezone.utc).isoformat(),
                'authorization': {'whole_contract_static_dispatches': 1, 'generation': False, 'execution': False,
                                  'frozen_acceptance': False, 'repair': False, 'retry': False,
                                  'source': 'user R5.44 newly authorized locked whole-contract transfer instruction'}}
    r.freeze(baseline, protected)
    r.verify(baseline)
    r.write('authorization', {'baseline': r.read('baseline')['identity'], **baseline['authorization']})
    r.write('counts-before', r.counts())
    print({'prepass': 'PASS', 'baseline': r.read('baseline')['identity'], 'lock': r.integrity(), 'counts': r.counts()})


def observation():
    # The qualified recorder has durably reserved dispatch before entering here.
    app = read('R5_40-b02-semantic-application.json')
    config = read('R5_40-B02-profiles.json')
    obligations = read('R5_40-B02-obligations.json')
    with (patch.object(pipeline, 'generate', side_effect=AssertionError('generation prohibited')),
          patch.object(emitter, 'generated_unit', side_effect=AssertionError('rendering prohibited')),
          patch.object(boundary, 'generate', side_effect=AssertionError('bundle generation prohibited'))):
        prediction = readiness.inspect(app, config['transport'], config['state'], config['launch'], obligations['readiness'])
        supplemental = audit.inspect(app, config)
        formed = {name: row['digest'] for name, row in prediction['operations'].items() if row['status'] == 'SUPPORTED'}
        rejected = {name: row for name, row in prediction['operations'].items() if row['status'] != 'SUPPORTED'}
        manifest = {'application': emitter.sha(emitter.canonical(app)), 'generation': 'static-readiness-r541', 'units': formed}
        compatible = boundary.support_report(app, config['transport'], config['state'], config['launch'], manifest)
        try:
            aggregate = boundary.aggregate(app, config['transport'], config['state'], config['launch'], manifest)
            admission = {'status': 'ADMITTED', 'aggregate': aggregate}
        except (ValueError, KeyError, TypeError) as exc:
            admission = {'status': 'REJECTED', 'reason': str(exc)}
        from benchmark.results.phase5c.r5_40_review import AUTHORITIES
        traces = audit.traceability(config, read('R5_40-profile-source-traceability.json'), ROOT, AUTHORITIES)
    views = {'readiness': prediction['status'] == 'READY', 'audit': supplemental['status'] == 'SUPPORTED',
             'admission': admission['status'] == 'ADMITTED', 'compatible_path': compatible['status'] == 'SUPPORTED'}
    coherent = len(set(views.values())) == 1
    complete = all(views.values()) and len(formed) == len(app['operations']) and not rejected
    classification = ('R5_44_SUPPORT_COHERENCE_GAP' if not coherent else
                      'R5_44_STATIC_SUPPORT_TRANSFER_READY' if complete else 'R5_44_GENERIC_CAPABILITY_GAP')
    if not supplemental['structure']['valid'] or supplemental['contamination'] or not traces['valid']:
        classification = 'R5_44_PROTOCOL_HALT'
    return {'primary_classification': classification, 'total_contracts': len(app['operations']),
            'checked_plans_formed': len(formed), 'plans': formed, 'rejected_plans': rejected,
            'readiness': prediction, 'supplemental_audit': supplemental, 'admission': admission,
            'compatible_path': compatible, 'support_views': views, 'support_coherent': coherent,
            'whole_contract_supported': complete, 'traceability': traces,
            'public_state_pairs': obligations['public_state_pairs'],
            'unsupported_requirements': prediction['gaps'] + supplemental['findings'] + compatible['findings'],
            'static_prediction_only': True, 'b02_generated': False, 'b02_executed': False,
            'frozen_acceptance_ran': False, 'post_exposure_repairs': 0, 'core_constructs': 30}


def dispatch():
    r = Recorder(RUN)
    try:
        r.open_run()
        r.integrity()
        authorization = r.read('authorization')
        baseline = r.read('baseline')
        if not equivalent(authorization, {'baseline': baseline['identity'], **baseline['evidence']['authorization']}):
            raise ProtocolFailure('authorization mismatch')
        result = r.observe(observation)
        r.write('counts-after', r.counts())
        r.verify(baseline['evidence'])
        post = checks()
        write('R5_44-postpass-verification.json', post)
        if not post['successful']:
            raise ProtocolFailure('post-exposure integrity/regression failure')
        r.integrity()
        classification = result['primary_classification']
    except Exception as exc:
        r.halt(exc)
        counts = r.read('halt')['counts']
        classification = ('R5_44_OBSERVATION_INDETERMINATE' if counts.get('disposition') == 'indeterminate' else 'R5_44_PROTOCOL_HALT')
    final = r.finish()
    write('R5_44-classification.json', {'primary_classification': classification, 'recorder': final,
          'b02_generated': False, 'b02_executed': False, 'frozen_acceptance_ran': False,
          'post_exposure_repairs': 0, 'core_constructs': boundary.SCHEMA['core_constructs'],
          'b03_prospectively_touched': False, 'b17_exposed': False, 'b17_classified': False, 'phase5c': 'paused'})
    print({'primary_classification': classification, 'final': final})


def final_integrity():
    r = Recorder(RUN)
    report = {'sealed_integrity': r.integrity(), 'counts': r.counts(),
              'historical_lock': historical_lock('R5_40-implementation-profile-lock.json'),
              'prospective_lock': historical_lock('R5_41-implementation-lock.json'),
              'infrastructure_lock': check_qualification_lock(), 'contamination': contamination()}
    p = subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True, text=True)
    report['diff_check'] = {'exit': p.returncode, 'stdout': p.stdout, 'stderr': p.stderr}
    report['artifact_sha256'] = {p.relative_to(ROOT).as_posix(): digest(p.read_bytes())
                                for p in sorted(RESULTS.glob('R5_44-*')) if p.is_file()}
    report['recorder_sha256'] = {p.name: digest(p.read_bytes()) for p in sorted(RUN.glob('*.json'))}
    write('R5_44-final-integrity.json', report)
    print(report)
    if p.returncode:
        raise ProtocolFailure('final diff check failed')


if __name__ == '__main__':
    {'prepass': prepass, 'dispatch': dispatch, 'final-integrity': final_integrity}[sys.argv[1]]()
