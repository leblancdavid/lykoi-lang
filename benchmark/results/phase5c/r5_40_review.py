"""R5.40 configuration recorder: one locked static pass; no B02 target emission."""

import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[3]
RESULTS = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from benchmark.semantic import application_boundary_r5_39 as boundary
from benchmark.semantic import application_boundary_r5_40 as admission
from benchmark.semantic import profile_audit_r5_40 as audit
from benchmark.semantic import checked_transport_r5_35 as transport
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import readiness_r5_39 as readiness
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import refined_generator_r5_28 as emitter
from benchmark.results.phase5c.r5_38_review import run_suite

ORIGINAL_SOURCE = 'benchmark/results/phase5c/R5_37-b02-semantic-application.json'
SOURCE = 'benchmark/results/phase5c/R5_40-b02-semantic-application.json'
BASELINE = 'benchmark/baseline.md'
B01 = 'benchmark/requirements/B01.md'
B02 = 'benchmark/requirements/B02.md'
PROFILE = 'benchmark/harness/profiles/B02.json'
ORACLE = 'benchmark/results/phase5c/R5_40-frozen-regression-authority.txt'
GENERIC = 'benchmark/semantic/checked_launch_r5_36.py'
GENERIC_TRANSPORT = 'benchmark/semantic/checked_transport_r5_35.py'
AUTHORITIES = {BASELINE, B01, B02, PROFILE, ORACLE, GENERIC, GENERIC_TRANSPORT, SOURCE}


def read(name):
    return json.loads((RESULTS / name).read_bytes())


def write(name, data):
    (RESULTS / name).write_bytes(emitter.canonical(data) + b'\n')


def before_static():
    if any((RESULTS / name).exists() for name in ('R5_40-B02-static-readiness.json', 'R5_40-static-pass-start.json')):
        raise ValueError('post-static repair/reconstruction/lock replacement prohibited')


def profiles():
    """Application metadata only: no semantic predicates, transformations or code."""
    before_static()
    # The live oracle has a later Phase 5D edit. Retrieve the original Phase 5B
    # shared oracle and verify the FROZEN.md byte hash before using its clauses.
    # No application internals or generated historical target is read.
    revision = '5064950:benchmark/harness/regression.py'
    data = subprocess.check_output(['git', 'show', revision], cwd=ROOT)
    (ROOT / ORACLE).write_bytes(data)
    write('R5_40-frozen-authority.json', {'revision': revision, 'member_sha256': emitter.sha(data),
        'copied_authority': ORACLE, 'executed': False,
        'live_oracle_difference': 'Phase 5D historical change; frozen member used as authority'})
    for artifact, digest in {B01: 'b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d',
                            B02: '8a76e276240fa840c473be60a8e7ed0e10bd0c165426b1bfc84741e69872032b',
                            PROFILE: '46ff02e3ff6ea48a7990c2f522fb9fa7bbefcab3c88550be007e0c2c1b75972f',
                            ORACLE: '16d55bac4dc1efa3debc6764ddde9dc27c16b7538de476a0fae9cf7db7519596'}.items():
        if emitter.sha((ROOT / artifact).read_bytes()) != digest:
            raise ValueError('frozen authority hash mismatch: ' + artifact)
    app = json.loads((ROOT / ORIGINAL_SOURCE).read_bytes())
    # State registry metadata only: equal typed legacy shapes can have distinct
    # version identities/discriminators. All 15 operation contracts stay identical.
    legacy = app['state']['versions'].pop('legacy_envelope')
    app['state']['versions']['V2'] = copy.deepcopy(legacy)
    app['state']['versions']['V3'] = copy.deepcopy(legacy)
    write(Path(SOURCE).name, app)
    plans = pipeline.checked(app)
    original = json.loads((ROOT / ORIGINAL_SOURCE).read_bytes())
    if original['operations'] != app['operations']:
        raise ValueError('behavioral source changed while constructing profiles')
    write('R5_40-source-registration.json', {'original': ORIGINAL_SOURCE, 'configured': SOURCE,
        'original_sha256': emitter.sha((ROOT / ORIGINAL_SOURCE).read_bytes()),
        'configured_sha256': emitter.sha((ROOT / SOURCE).read_bytes()),
        'operation_contracts_unchanged': True, 'checked_plans': len(plans),
        'units': {name: plan.digest for name, plan in plans.items()},
        'registry_change': 'legacy_envelope replaced by equal-codec V2/V3 identities',
        'authority': BASELINE + ':27-32; frozen regression oracle:120-133,178-194',
        'core_constructs': 30})
    # CheckedPlan shapes supply slot/decoder references, never task algorithms.
    default = transport.specification(plans)
    entries = {item['semantic']: item for item in default['operations']}
    errors = {'invalid_title', 'invalid_tag', 'invalid_priority', 'task_not_found',
              'invalid_transition', 'migration_required', 'migration_required_otherwise'}
    for name, item in entries.items():
        for arg in item['arguments']:
            if arg['slot'] == 'due_date':
                arg['public'], arg['representation'] = 'due-date', 'text'
            elif arg['slot'] == 'tags':
                arg['public'], arg['mode'], arg['representation'] = 'tag', 'repeat', 'text'
        item['argument_codes'] = {'due-date': {'malformed_scalar': 'invalid_due_date'}} if name == 'create' else {}
        for tag, desc in item['outcomes'].items():
            if tag in errors:
                desc.update({'status': 'SEMANTIC_FAILURE', 'stream': 'stderr', 'exit': 1,
                    'presentation': {'mode': 'object', 'coverage': 'full', 'fields': [
                        {'name': 'error', 'source': 'payload', 'type': 'string', 'path': []}]}})
    routes = []
    for public in ('list', 'list-high', 'list-overdue', 'create', 'complete', 'delete', 'migrate'):
        choices = {'V4': 'migrate_current' if public == 'migrate' else public}
        if public in ('list', 'list-high', 'list-overdue'):
            choices.update({'V1': public + '_legacy_v1', 'V2': public + '_legacy_envelope',
                            'V3': public + '_legacy_envelope'})
        elif public == 'migrate':
            choices.update({'V1': 'migrate_v1', 'V2': 'migrate_envelope', 'V3': 'migrate_envelope'})
        routes.append({'public': public, 'alternatives': {variant: {
            key: copy.deepcopy(value) for key, value in entries[name].items() if key != 'public'}
            for variant, name in choices.items()}})
    failure = transport.output(transport.ERROR_TYPE, 'BOUNDARY_FAILURE')
    failure['presentation'] = {'mode': 'object', 'coverage': 'full', 'fields': [
        {'name': 'error', 'source': 'payload', 'type': 'string', 'path': ['code']}]}
    failures = {name: copy.deepcopy(failure) for name in transport.FAILURES}
    for name in ('persistence_invalid_json', 'persistence_invalid_state'):
        failures[name]['presentation'] = {'mode': 'object', 'coverage': 'selected', 'fields': [
            {'name': 'error', 'source': 'constant', 'type': 'string', 'value': 'invalid_state'}]}
    spec = {'operations': routes, 'failures': failures,
            'persistence': {'missing': 'INITIALIZE_DECLARED_STATE', 'initial': 'empty'}}
    alternatives = {}
    for variant, shape in app['state']['versions'].items():
        population = {'kind': 'population', 'path': [] if variant == 'V1' else ['records'],
            'identity': 'id', 'nonblank': ['id', 'title'], 'domains': {
                'status': ['pending', 'completed'], 'priority': ['LOW', 'NORMAL', 'HIGH', 'CRITICAL']}}
        alternatives[variant] = {'codec': copy.deepcopy(shape), 'constraints': [population]}
        if variant != 'V1':
            alternatives[variant]['constraints'].insert(0, {'kind': 'equals', 'path': ['schema_version'], 'value': int(variant[1:])})
    state = {'version': 'R5.39', 'versions': copy.deepcopy(app['state']['versions']),
        'alternatives': alternatives, 'initial': {'empty': {'version': 'V4', 'value': {'schema_version': 4, 'records': []}}}}
    config = launch.configuration(app['id'], 'tasks.json')
    config['provider']['types'] = launch.requirements(app)
    configuration = {'transport': spec, 'state': state, 'launch': config}
    requirements = {variant: copy.deepcopy(desc['constraints']) for variant, desc in alternatives.items()}
    obligations = [
        {'kind': 'public_state_alternatives', 'public': ['list', 'list-high', 'list-overdue', 'migrate'],
         'reference': 'baseline.md:18-32; regression.py:122-135,180-196'},
        {'kind': 'durable_content_constraints', 'requirements': requirements,
         'reference': 'baseline.md:34-36; B01.md:3-6; profiles/B02.json:1'}]
    coverage = []
    for route in routes:
        for variant in alternatives:
            item = route['alternatives'].get(variant)
            coverage.append({'public': route['public'], 'state': variant,
                'classification': ('NOT_APPLICABLE' if item is None else
                    'MIGRATION_TRANSITION' if route['public'] == 'migrate' and variant != 'V4' else
                    'ROUTABLE_BUT_SEMANTICALLY_GUARDED' if variant != 'V4' else 'AVAILABLE'),
                'semantic': None if item is None else item['semantic'],
                'authority': 'baseline.md:18-32',
                'interpretation': 'legacy writes unspecified; no availability invented' if item is None else
                                  'declared operation-family binding; requires retained in semantic source'})
    traces = []
    for path, value in audit.leaves(configuration):
        text = '/'.join(map(str, path))
        artifact, clause = BASELINE, '3-36'
        interpretation = 'Interface/state/binding relationship derived from inherited public contract and CheckedPlan; no behavior added.'
        if path[0] == 'launch' and path[1] in ('trace', 'runtime', 'provider'):
            artifact, clause = GENERIC, '16-39'
            interpretation = 'Unchanged generic infrastructure default/capability reference; not a B02-specific requirement.'
        elif path[0] == 'launch' and path[1] == 'id':
            artifact, clause = SOURCE, '/id'
            interpretation = 'Opaque application identity reference, not a frozen request special case.'
        elif 'tag' in text or isinstance(value, str) and value in ('tag', 'tags'):
            artifact, clause = B02, '3-7'
        elif 'priority' in text:
            artifact, clause = B01, '3-6'
        elif 'codec' in text or 'versions' in text or 'decoder' in text or 'type' in text or 'initial' in text:
            artifact, clause = PROFILE, '1 (baseline.md:9-32 for inherited shapes)'
            interpretation = 'Frozen public shape/default mapped to existing typed shape/codec references; legacy optional shape follows baseline migration clauses.'
        if path[0] == 'transport' and 'semantic' in text:
            artifact, clause = SOURCE, '/operations/' + str(value)
            interpretation = 'CheckedPlan operation identity reference; public meaning traced to baseline.md:13-32/B02.md:3-7.'
        elif path[0] == 'transport' and ('error_codes' in text or 'failures' in text and
                path[2] not in ('persistence_invalid_json', 'persistence_invalid_state', 'binding_failure')):
            artifact, clause = GENERIC_TRANSPORT, '18-46'
            interpretation = 'Unchanged generic policy for unspecified infrastructure errors, not B02 behavior or an expected acceptance output.'
        elif 'argument_codes' in text:
            artifact, clause = BASELINE, '13-17'
            interpretation = 'Public invalid_due_date label for malformed supplied due-date, before semantics; no transform.'
        elif path[0] == 'launch' and path[1] == 'store':
            artifact, clause = BASELINE, '3-7'
        elif 'presentation' in text or '/stream' in text or '/exit' in text or '/status' in text:
            artifact, clause = BASELINE, '3-5,34-36'
            interpretation = 'Bare success JSON / public error envelope and stdout/stderr/exit mapping; invalid_state is the specified error label, not a fixture value.'
        traces.append({'path': path, 'value': value, 'artifact': artifact,
            'sha256': emitter.sha((ROOT / artifact).read_bytes()), 'clause': clause,
            'interpretation': interpretation})
    write('R5_40-B02-profiles.json', configuration)
    write('R5_40-profile-source-traceability.json', traces)
    write('R5_40-B02-obligations.json', {'readiness': obligations, 'public_state_pairs': coverage,
        'unresolved_requirements': [
            {'id': 'plain_text_nullable', 'classification': 'MISSING_GENERIC_CAPABILITY',
             'authority': BASELINE + ':13-17; regression.py:94-98',
             'reason': 'Nullable instant semantic slot requires JSON representation; frozen flag supplies plain text.'},
            {'id': 'optional_population_domain', 'classification': 'MISSING_GENERIC_CAPABILITY',
             'authority': BASELINE + ':27-36; ' + B01 + ':5-6',
             'reason': 'Admitted population domain requires row[field] even when the typed field is optional; absence is incorrectly rejected.'}]})
    write('R5_40-profile-schemas.json', {'admission': admission.SCHEMA, 'audit': audit.SCHEMA,
        'existing': {'state': 'application_boundary_r5_39.check_state', 'transport': 'checked_transport_r5_35.validate',
                     'launch': 'launch_runtime_r5_36.validate'}})
    return configuration


def configuration_audit():
    configuration = read('R5_40-B02-profiles.json')
    app = json.loads((ROOT / SOURCE).read_bytes())
    trace = audit.traceability(configuration, read('R5_40-profile-source-traceability.json'), ROOT, AUTHORITIES)
    structural = audit.structure(configuration)
    contamination = audit.contamination(configuration)
    schema = audit.schema_findings(app, configuration)
    result = {'traceability': trace, 'structural_schema': structural, 'contamination': contamination,
        'classification': 'CONFIGURATION_ONLY' if not contamination else 'CONTAMINATED',
        'schema_status': 'REJECTED' if schema else 'ADMITTED', 'schema_findings': schema,
        'capability_findings': audit.capability_findings(configuration),
        'scope': 'bounded closed-schema/source review; not a proof that prose interpretations are correct'}
    write('R5_40-configuration-audit.json', result)
    return result


def independent_evidence():
    from benchmark.harness.test_profile_admission_r5_40 import minimal, admit
    setup = minimal()
    app, spec, state, config = setup
    spec['operations'][0]['alternatives']['V1']['arguments'] = []
    historical = admit(setup, boundary)
    prediction = readiness.inspect(*setup)
    try:
        admit(setup)
    except ValueError as exc:
        rejection = str(exc)
    else:
        raise ValueError('independent repair failed')
    write('R5_40-admission-reconstruction.json', {'application': app, 'transport': spec, 'state': state,
        'launch': config, 'historical_admitted': True, 'historical_profile': historical,
        'readiness': prediction, 'prospective_rejection': rejection,
        'cause': 'R5.35 only checks required <= mapped; readiness v2 checks all input slots == mapped.'})
    from benchmark.semantic import state_runtime_r5_39 as codec
    app, spec, state, config = minimal()
    app['state']['versions']['V1']['record']['seeds']['sequence']['record']['habitat'] = {'optional': 'string'}
    state['versions'] = copy.deepcopy(app['state']['versions'])
    state['alternatives']['V1']['codec'] = copy.deepcopy(state['versions']['V1'])
    state['alternatives']['V1']['constraints'][1]['domains']['habitat'] = ['dry', 'wet']
    boundary.check_state(app, state)
    content = {'revision': 1, 'seeds': [{'code': 'iris', 'label': 'Iris'}]}
    decoded = codec.decode(emitter.canonical(content), state)
    write('R5_40-independent-capability-witnesses.json', {'optional_population_domain': {
        'state': state, 'content': content, 'schema_admitted': True, 'structurally_valid': True,
        'decoded': decoded, 'diagnosis': 'population domains index an absent optional field; decode rejects',
        'B02_content_or_execution': False},
        'plain_text_nullable': {'independent_test': 'ConfigurationAudit.test_plain_text_nullable_and_scalar_discriminator_domain_limitations',
            'schema_diagnostic': 'incompatible checked binding', 'reason': 'nullable element requires JSON representation'},
        'version_discrimination': {'independent_test': 'Admission.test_equal_codec_distinct_state_discriminators_are_configuration',
            'resolution': 'distinct version identities with equal codecs and existing equals constraints; no scalar domain algorithm needed'}})


def verification():
    before_static()
    report = {'environment': {'python': sys.version, 'platform': platform.platform(),
        'executable': sys.executable, 'shell': 'PowerShell 7',
        'autocrlf': subprocess.check_output(['git', 'config', '--get', 'core.autocrlf'], cwd=ROOT, text=True).strip()},
        'suites': [], 'commands': [], 'b02_generated': False, 'b02_executed': False, 'frozen_acceptance_ran': False}
    for directory, pattern, restrictions in [('benchmark/harness', 'test*.py', True), ('tests', 'test*.py', False),
        ('benchmark/results/phase5c', 'test_r5_37_evaluation.py', True),
        ('benchmark/harness', 'test_profile_admission_r5_40.py', False)]:
        suite = run_suite(directory, pattern, restrictions)
        for skip in suite['skipped']:
            skip['reason'] = skip['reason'].replace('R5.38', 'R5.40')
        report['suites'].append(suite)
    for command in ([sys.executable, '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'], ['git', 'diff', '--check']):
        completed = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'}, capture_output=True, text=True)
        report['commands'].append({'command': command, 'exit': completed.returncode,
                                  'stdout': completed.stdout, 'stderr': completed.stderr})
    report['configuration_audit'] = configuration_audit()
    independent_evidence()
    write('R5_40-verification.json', report)
    return all(s['successful'] for s in report['suites']) and all(c['exit'] == 0 for c in report['commands'])


def lock():
    before_static()
    verification = read('R5_40-verification.json')
    if not all(s['successful'] for s in verification['suites']) or not all(c['exit'] == 0 for c in verification['commands']):
        raise ValueError('verification failed')
    if configuration_audit()['classification'] != 'CONFIGURATION_ONLY':
        raise ValueError('contaminated configuration')
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard'], cwd=ROOT, text=True).splitlines()
    excluded = ('R5_40-implementation-profile-lock.json', 'R5_40-B02-static-readiness.json', 'R5_40-static-pass-start.json',
                'R5_40-BOUNDARY-PROFILE-ADMISSION-B02-CONFIGURATION.md')
    names = sorted({name for name in names if name.startswith(('benchmark/', 'src/', 'schema/', 'generated/', 'air/'))
                    and not name.endswith(excluded)})
    names += ['docs/boundary-profile-admission-r5.40.md']
    record = {'version': 'R5.40', 'time': datetime.now(timezone.utc).isoformat(),
        'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'status': subprocess.check_output(['git', 'status', '--short'], cwd=ROOT, text=True),
        'readiness': emitter.sha((ROOT / 'benchmark/semantic/readiness_r5_39.py').read_bytes()),
        'semantic_source': emitter.sha((ROOT / SOURCE).read_bytes()), 'admission_schema': admission.SCHEMA_ID,
        'files': {name: emitter.sha((ROOT / name).read_bytes()) for name in names}}
    record['identity'] = emitter.sha(emitter.canonical(record))
    write('R5_40-implementation-profile-lock.json', record)
    return {'identity': record['identity'], 'protected_files': len(names)}


def verify_lock():
    record = read('R5_40-implementation-profile-lock.json')
    identity = record.pop('identity')
    mismatches = [name for name, digest in record['files'].items() if emitter.sha((ROOT / name).read_bytes()) != digest]
    if mismatches or emitter.sha(emitter.canonical(record)) != identity:
        raise ValueError({'lock_mismatches': mismatches})
    if record['head'] != subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip():
        raise ValueError('HEAD changed')
    return {'valid': True, 'identity': identity, 'protected_files': len(record['files'])}


def static():
    before_static()
    before = verify_lock()
    app = json.loads((ROOT / SOURCE).read_bytes())
    config = read('R5_40-B02-profiles.json')
    obligations = read('R5_40-B02-obligations.json')
    write('R5_40-static-pass-start.json', {'time': datetime.now(timezone.utc).isoformat(),
                                        'lock': before, 'one_pass': True})
    with (patch.object(pipeline, 'generate', side_effect=AssertionError('B02 generation prohibited')),
          patch.object(emitter, 'generated_unit', side_effect=AssertionError('B02 rendering prohibited'))):
        result = readiness.inspect(app, config['transport'], config['state'], config['launch'], obligations['readiness'])
        schema = audit.schema_findings(app, config)
        capabilities = audit.capability_findings(config)
    complete = list(capabilities)
    for gap in result['gaps']:
        causal = gap['reason'] in ('incompatible checked binding', 'checked public state-alternative coverage missing')
        classified = {**gap, 'classification': ('MISSING_GENERIC_CAPABILITY'
            if causal and capabilities else 'UNKNOWN')}
        if gap['reason'] == 'checked public state-alternative coverage missing':
            classified['downstream_of'] = 'transport admission fails on plain-text nullable input; route metadata exists'
        complete.append(classified)
    if any(gap['stage'] == 'state' for gap in capabilities):
        complete.append({'path': ['readiness', 'durable_content_constraints'], 'stage': 'readiness',
            'classification': 'READINESS_ANALYZER_DEFECT',
            'reason': 'v2 checks presence/equality of declared rules, not the supported optional-domain composition; independent static capability audit required'})
    result.update({'lock_before': before, 'lock_after': verify_lock(), 'profile_schema_findings': schema,
        'complete_requirement_gap_set': complete, 'source_requirement_references': obligations['unresolved_requirements'],
        'contamination': read('R5_40-configuration-audit.json')['classification'],
        'retry_recommended': False, 'frozen_acceptance_ran': False,
        'decision': ('R5_40_GENERIC_CAPABILITY_GAP' if any(
            gap['classification'] == 'MISSING_GENERIC_CAPABILITY'
            for gap in complete) else 'R5_40_B02_CONFIGURATION_INCOMPLETE')})
    # Supplemented requirement checks are explicit; do not silently bless a
    # READY v2 result when an independently evidenced boundary gap exists.
    if result['status'] == 'READY':
        raise ValueError('readiness v2 unexpectedly missed declared incomplete boundary')
    write('R5_40-B02-static-readiness.json', result)
    return {key: result[key] for key in ('status', 'gaps', 'complete_requirement_gap_set', 'lock_after', 'decision')}


if __name__ == '__main__':
    command = sys.argv[1]
    if command == 'profiles':
        profiles()
        print(json.dumps(configuration_audit(), indent=2))
    elif command == 'verify':
        sys.exit(0 if verification() else 1)
    elif command == 'lock':
        print(json.dumps(lock()))
    elif command == 'lock-check':
        print(json.dumps(verify_lock()))
    elif command == 'static':
        print(json.dumps(static(), indent=2))
    else:
        raise ValueError('unknown command')
