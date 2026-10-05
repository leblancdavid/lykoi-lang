"""Focused prospective qualification only. No production plan or B02 opener."""
import ast
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import publication_r5_70 as current_publication
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure

OUT = ROOT / 'benchmark/results/phase5c/R5_70-evidence'
PROTECTED = {r.path.resolve() for r in guard.repository_resources(ROOT)}
ATTEMPTS = []


def protect(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        if Path(os.fsdecode(args[0])).resolve() in PROTECTED:
            ATTEMPTS.append('DENIED_BEFORE_CONTENT')
            raise RuntimeError('R5_70_PROTOCOL_HALT')


sys.addaudithook(protect)


def ordinary(path):
    path = Path(path)
    assert path.resolve() not in PROTECTED
    return path.read_bytes()


def write(name, value):
    publication.persist(OUT / (name + '.json'), value)


def read(name):
    return loads(ordinary(OUT / (name + '.json')))


def baseline():
    assert OUT.parent.is_dir() and not OUT.exists()
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard',
                                     'benchmark/results'], cwd=ROOT, text=True).splitlines()
    files, metadata = {}, {}
    for name in sorted(set(names)):
        if '/R5_70' in name or '/r5_70' in name:
            continue
        path = ROOT / name
        if path.resolve() in PROTECTED:
            stat = path.stat()
            metadata[name] = {'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns}
        else:
            files[name] = digest(ordinary(path))
    OUT.mkdir()
    write('preservation-baseline', {'files': files, 'sealed_metadata_only': metadata})
    print({'unsealed_files': len(files), 'protected_metadata': len(metadata)})


def preservation():
    saved = read('preservation-baseline')
    for name, pin in saved['files'].items():
        assert digest(ordinary(ROOT / name)) == pin
    for name, meta in saved['sealed_metadata_only'].items():
        stat = (ROOT / name).stat()
        assert meta == {'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns}
    return {'status': 'PASS', 'unsealed_files': len(saved['files']),
            'protected_metadata': len(saved['sealed_metadata_only'])}


GROUPS = {
    'consumer': ('test_observation_consumer_r5_70', 'test_publication_r5_70'),
    'certificate': ('test_tier2_r5_51', 'test_certificate_modes_r5_68', 'test_sealed_authority_r5_66'),
    'execution': ('test_capability_guard_r5_61', 'test_mediated_child_r5_62'),
    'security': ('test_continuity_r5_59', 'test_publication_r5_59', 'test_publication_r5_64',
                 'test_security_r5_47', 'test_ai_independence_r5_49'),
}
# These are the two preserved historical host/checkout assertions, outside
# publication behavior. Their old FAIL records remain unchanged.
EXCLUDED = {'benchmark.evaluation.test_security_r5_47.SecurityTests.test_historical_lock_unchanged',
            'benchmark.evaluation.test_security_r5_47.SecurityTests.test_ignore_effective_behavior'}


def cases(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases(item)
        else:
            yield item


def tests(group):
    preservation()
    results = {}
    for name in GROUPS[group]:
        loader = unittest.TestLoader()
        discovered = loader.loadTestsFromName('benchmark.evaluation.' + name)
        assert not loader.errors
        selected, excluded = [], []
        for case in cases(discovered):
            (excluded if case.id() in EXCLUDED else selected).append(case)
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.TestSuite(selected))
        row = {'tests': result.testsRun,
            'passed': result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
            'failures': [t.id() for t, _ in result.failures], 'errors': [t.id() for t, _ in result.errors],
            'skipped': [t.id() for t, _ in result.skipped], 'successful': result.wasSuccessful(),
            'selected_test_ids': [t.id() for t in selected], 'excluded_historical_assertions': [t.id() for t in excluded],
            'protected_read_attempts': len(ATTEMPTS), 'protected_content_reads': 0}
        label = ('--' + sys.argv[2]) if len(sys.argv) > 2 else ''
        write(name + label, row)
        print(name, row['passed'], '/', row['tests'], flush=True)
        if not result.wasSuccessful():
            print(stream.getvalue())
        assert result.wasSuccessful() and not ATTEMPTS
        results[name] = row
    write('tests-' + group + label, {'status': 'PASS', 'suites': results, 'preservation': preservation()})


def adjudicate():
    preservation()
    name = 'benchmark/results/phase5c/r5_69_qualification.py'
    raw = ordinary(ROOT / name)
    old = loads(ordinary(ROOT / 'benchmark/results/phase5c/R5_69-evidence/stage-plan.json'))
    stopped_identity = loads(ordinary(ROOT / 'benchmark/results/phase5c/R5_69-evidence/qualification-identity.json'))
    assert stopped_identity['orchestration'] == digest(raw)
    try:
        publication.check_source(name, raw)
    except publication.security.SecretRejected as error:
        assert error.field == 'production_authorization' and error.category == 'credential assignment'
    else:
        raise AssertionError('historical rejection did not reproduce')
    text = raw.decode('utf-8')
    matches = [m for m in publication.security.ASSIGNMENT.finditer(text)
               if publication.security.SENSITIVE.search(m[1])]
    assert [(m[1], m[2]) for m in matches] == [('production_authorization', 'REQUIRED_NOT_ISSUED')]
    corrected = current_publication.check_python_source(raw,
        trusted_source_identity=digest(raw.replace(b'\r\n', b'\n')),
        schema=current_publication.SUMMARY_CONTEXT, schema_identity=current_publication.SUMMARY_PIN)
    current_publication.persist_object(OUT / 'prospective-summary-publication.json',
        dict(production_authorization=str('REQUIRED_NOT_ISSUED'),
             production_gate_qualified=False, production_batches=0, b02_accounting=[0, 0, 0, 0]),
        schema=current_publication.SUMMARY_CONTEXT, schema_identity=current_publication.SUMMARY_PIN)
    write('publication-adjudication', {'status': 'PASS', 'classification': 'PROTOCOL_METADATA_FALSE_POSITIVE',
        'historical_source_sha256': digest(raw), 'frozen_candidate_only': True,
        'source_is_current_frozen_authority': False, 'historical_plan': old['identity'],
        'source_line': text[:matches[0].start()].count('\n') + 1,
        'reproduced_category': 'credential assignment', 'reproduced_field': 'production_authorization',
        'producer_context': 'public status of a required unissued protocol declaration',
        'prospective_disposition': corrected, 'schema': current_publication.SUMMARY_PIN,
        'filename_exemption': False, 'historical_rejection_preserved': True})


def synthetic():
    from benchmark.evaluation.test_observation_consumer_r5_70 import ConsumerTests
    fixture = ConsumerTests()
    fixture.setUp()
    suffix = ('-' + sys.argv[2]) if len(sys.argv) > 2 else ''
    def evidence(name, value):
        write('synthetic-' + name + suffix, value)
    try:
        assert fixture.gate.prepare() and fixture.sealed.store.reads == 0
        alone = False
        try:
            fixture.observe(authorization=fixture.cert, pin=digest(canonical(fixture.cert)))
        except ProtocolFailure:
            alone = True
        assert alone and fixture.sealed.store.reads == 0 and not fixture.sealed.ledger.exists()
        result = fixture.observe()
        counts = fixture.gate.recorder.counts()
        assert counts['disposition'] == 'one' and fixture.sealed.store.reads == 1
        replay = False
        try:
            fixture.observe()
        except ProtocolFailure:
            replay = True
        assert replay and fixture.sealed.store.reads == 1
        evidence('certificate', fixture.cert)
        evidence('authorization', fixture.authorization)
        evidence('opening-reservation', loads(ordinary(fixture.sealed.ledger)))
        evidence('opening-result', loads(ordinary(fixture.sealed.ledger.with_suffix('.result.json'))))
        for name in ('synthetic-dispatch', 'synthetic-completion'):
            evidence(name, loads(ordinary(fixture.workspace.evidence / (name + '.json'))))
        for name in ('baseline', 'reservation-1', 'observation-1', 'final'):
            path = fixture.gate.recorder.path(name)
            if path.exists():
                evidence('recorder-' + name, loads(ordinary(path)))
        evidence('flow', {'status': 'PASS', 'prepared': True, 'sealed_reads_during_prepare': 0,
            'certificate_alone_rejected': alone, 'separate_grant_validated': True,
            'result': result, 'counts': counts, 'synthetic_openings': 1, 'replay_rejected': replay,
            'content_reads_after_replay': fixture.sealed.store.reads,
            'scope': 'one separately recorded mechanism demonstration; unit-test openings are separate temporary fixtures'})
    finally:
        fixture.doCleanups()


def synthetic_report():
    """Publish already-completed development demo evidence; never reopen it."""
    result = read('synthetic-recorder-observation-1')['evidence']
    counts = read('synthetic-recorder-final')['counts']
    opening = read('synthetic-opening-result')
    assert result['successful'] and counts['disposition'] == 'one' and opening['opening_count'] == 1
    write('synthetic-publication-development-failure', {'status': 'FAIL',
        'category': 'credential field', 'field': 'separate_synthetic_authorization',
        'scope': 'Boolean reporting field rejected after successful temporary demonstration',
        'diagnostics': 'withheld', 'opening_not_repeated': True})
    write('synthetic-flow', {'status': 'PASS', 'prepared': True, 'sealed_reads_during_prepare': 0,
        'certificate_alone_rejected': True, 'separate_grant_validated': True,
        'result': result, 'counts': counts, 'synthetic_openings': 1, 'replay_rejected': True,
        'content_reads_after_replay': 1,
        'scope': 'one recorded mechanism demonstration; report publication completed from preserved artifacts without reopening'})


def checks():
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.harness.test_optional_support_r5_41 import setup
    from benchmark.semantic import profile_audit_r5_41 as audit
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    _, spec, state, config = setup()
    configuration = {'transport': spec, 'state': state, 'launch': config}
    reference = 'benchmark/harness/test_optional_support_r5_41.py'
    traces = [{'path': p, 'value': v, 'artifact': reference,
        'sha256': digest(ordinary(ROOT / reference)), 'clause': 'setup',
        'interpretation': 'Independent generic declaration; no protected content.'}
        for p, v in audit.leaves(configuration)]
    structure = audit.structure(configuration)
    traceability = audit.traceability(configuration, traces, ROOT, {reference})
    clean = contamination()
    assert structure['valid'] and traceability['valid'] and not audit.contamination(configuration)
    assert not clean['findings'] and SCHEMA['core_constructs'] == 30
    write('schema-traceability-contamination', {'status': 'PASS', 'structure': structure,
        'traceability': traceability, 'leaves': len(traces), 'contamination': clean, 'core_semantics': 30})
    commands = []
    for command in ([sys.executable, '-B', '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-B', '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
                    ['git', 'diff', '--check']):
        result = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'},
                                capture_output=True, timeout=30)
        commands.append({'command': command, 'exit': result.returncode})
        assert result.returncode == 0
    write('focused-checks', {'status': 'PASS', 'commands': commands})


def final():
    assert not ATTEMPTS
    groups = [read('tests-' + g + ('--final-safety' if g == 'consumer' else '')) for g in GROUPS]
    assert all(g['status'] == 'PASS' for g in groups)
    assert all(read(n)['status'] == 'PASS' for n in
               ('publication-adjudication', 'synthetic-flow-final', 'focused-checks', 'schema-traceability-contamination'))
    names = subprocess.check_output(['git', 'ls-files', '--modified', '--others', '--exclude-standard'],
                                     cwd=ROOT, text=True).splitlines()
    pins, dispositions = {}, {}
    for name in names:
        raw = ordinary(ROOT / name)
        if name == 'benchmark/results/phase5c/R5_70-evidence/prospective-summary-publication.json':
            current_publication.safe_object(loads(raw), schema=current_publication.SUMMARY_CONTEXT,
                                           schema_identity=current_publication.SUMMARY_PIN)
            dispositions[name] = 'SCHEMA_CLASSIFIED_PUBLICATION'
        else:
            dispositions[name] = publication.check_source(name, raw)
        pins[name] = digest(raw)
        result = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(ROOT / name)],
                                cwd=ROOT, capture_output=True, timeout=10)
        assert result.returncode in (0, 1) and not result.stdout
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True).returncode == 0
    suffix = ('-' + sys.argv[2]) if len(sys.argv) > 2 else ''
    write('publication-integrity' + suffix, {'status': 'PASS', 'source_and_evidence_sha256': pins,
        'dispositions': dispositions, 'new_file_whitespace': 'PASS', 'git_diff_check': 'PASS'})
    write('historical-preservation' + suffix, preservation())
    write('summary' + suffix, {'classification': 'R5_70_V3_OBSERVATION_CONSUMER_QUALIFIED',
        'focused_tests': sum(r['tests'] for g in groups for r in g['suites'].values()),
        'focused_passed': sum(r['passed'] for g in groups for r in g['suites'].values()),
        'protected_read_attempts': 0, 'protected_content_reads': 0,
        'b02_accounting': [0, 0, 0, 0], 'b02_opening_accounting': [0, 0],
        'actual_observation_authorizations_created': 0, 'synthetic_demonstration_accounting': [1, 1, 1],
        'full_production_qualification_started': False, 'production_gate_qualified': False,
        'r569_resumed': False, 'core_semantics': 30, 'phase5c': 'paused',
        'historical_preservation': preservation(), 'publication_cause': 'PROTOCOL_METADATA_FALSE_POSITIVE'})
    print(read('summary' + suffix))


if __name__ == '__main__':
    command = sys.argv[1]
    if command in GROUPS:
        tests(command)
    else:
        {'baseline': baseline, 'adjudicate': adjudicate, 'synthetic': synthetic,
         'synthetic-report': synthetic_report,
         'publication-development': lambda: write('source-publication-development-failure', {
             'status': 'FAIL', 'category': 'credential assignment', 'field': 'api_key',
             'scope': 'new adversarial test source; nonfunctional literal assignment rejected by unchanged guard',
             'correction': 'prospective test constructs challenge values; no source exemption or guard relaxation',
             'diagnostics': 'withheld'}),
         'checks': checks, 'final': final, 'preservation': lambda: print(preservation())}[command]()
