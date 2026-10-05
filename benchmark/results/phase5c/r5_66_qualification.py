"""Bounded prospective qualification; no production entry or real seal opener."""
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.results.phase5c.r5_66_inventory import inventory, OUT

PROTECTED = {r.path.resolve() for r in guard.repository_resources(ROOT)}
ATTEMPTS = []


def protect(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        path = Path(os.fsdecode(args[0])).resolve()
        if path in PROTECTED:
            ATTEMPTS.append('DENIED_BEFORE_CONTENT')
            raise RuntimeError('R5_66_PROTOCOL_HALT')


sys.addaudithook(protect)


def write(name, value):
    path = OUT / (name + '.json')
    if path.exists():
        assert path.read_bytes() == canonical(value) + b'\n'
    else:
        publication.persist(path, value)


def names(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).splitlines()


def baseline():
    files, protected = {}, {}
    for name in sorted(set(names('ls-files', '--cached', '--others', '--exclude-standard',
                                 'benchmark/results'))):
        if 'R5_66' in name or '/r5_66_' in name:
            continue
        path = ROOT / name
        if path.resolve() in PROTECTED:
            s = path.stat()
            protected[name] = {'size': s.st_size, 'mtime_ns': s.st_mtime_ns}
        else:
            files[name] = digest(path.read_bytes())
    return {'files': files, 'protected_metadata_only': protected}


def preserve(value):
    for name, pin in value['files'].items():
        assert digest((ROOT / name).read_bytes()) == pin
    for name, row in value['protected_metadata_only'].items():
        s = (ROOT / name).stat()
        assert row == {'size': s.st_size, 'mtime_ns': s.st_mtime_ns}
    old = loads((OUT.parent / 'R5_65-evidence/summary.json').read_bytes())
    assert old['classification'] == 'R5_65_QUALIFIED_AUTHORITY_GAP'
    assert not (OUT.parent / 'R5_65-evidence/certificate.json').exists()
    return {'unsealed_byte_preserved': len(value['files']),
            'protected_metadata_preserved': len(value['protected_metadata_only']),
            'r565_classification': old['classification'], 'r565_resumed': False}


def qualify(tag=''):
    assert not (OUT / ('summary' + tag + '.json')).exists()
    path = OUT / 'preservation-baseline.json'
    history = loads(path.read_bytes()) if path.exists() else baseline()
    preserve(history)
    OUT.mkdir(exist_ok=True)
    write('preservation-baseline', history)
    value = inventory()
    write('sealed-inventory', value)
    policy = {'authority': value['authority'], 'policy_binding': value['policy_binding'],
        'members': value['members'], 'frozen_authority': {
            n: r['sha256'] for n, r in value['members'].items() if r['frozen']}}
    # The derivation is anchored in the hard-coded historical pins, not a new
    # current content digest or a caller's untrusted inventory.
    pin = sealed.identity(policy)
    write('derived-sealed-policy', {'policy': policy, 'derived_policy_identity': pin,
        'trust_root': 'externally pinned R5.55 authorization / R5.53 successor',
        'scope': '11 sealed members only; not full production authority'})
    authority = sealed.Authority(ROOT, policy, trusted_policy_identity=pin, observer=sealed.GitMetadata(ROOT))
    qualified = authority.qualify()
    assert all(r['mode'] == sealed.SEALED and not r['current_content_read']
               for r in qualified['verification'].values())
    write('sealed-authority', qualified)
    write('placeholder-examples', {'references': [sealed.placeholder(r, qualified)
        for r in value['members'].values()], 'actual_workspace_materialized': False})
    suites = {}
    # Exact safe modules, no broad discovery and no historical certificate
    # fixture that would materialize/read protected resources.
    for module in ('benchmark.evaluation.test_sealed_authority_r5_66',
                   'benchmark.evaluation.test_capability_guard_r5_61',
                   'benchmark.evaluation.test_mediated_child_r5_62',
                   'benchmark.evaluation.test_continuity_r5_59',
                   'benchmark.evaluation.test_publication_r5_59',
                   'benchmark.evaluation.test_publication_r5_64',
                   'benchmark.evaluation.test_security_r5_47',
                   'benchmark.evaluation.test_ai_independence_r5_49',
                   'benchmark.harness.test_optional_support_r5_41'):
        if tag and module != 'benchmark.evaluation.test_sealed_authority_r5_66':
            row = loads((OUT / (module.rsplit('.', 1)[1] + '.json')).read_bytes())
            assert row['successful']
            suites[module] = row
            continue
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName(module)
        assert not loader.errors
        stream = io.StringIO()
        result = unittest.TextTestRunner(stream=stream).run(suite)
        row = {'tests': result.testsRun,
            'passed': result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
            'failures': [t.id() for t, _ in result.failures],
            'errors': [t.id() for t, _ in result.errors],
            'skipped': [t.id() for t, _ in result.skipped], 'successful': result.wasSuccessful()}
        suites[module] = row
        write(module.rsplit('.', 1)[1] + tag, row)
        print(module, row['passed'], '/', row['tests'], flush=True)
        if not result.wasSuccessful():
            print(stream.getvalue())
        assert result.wasSuccessful()
    # One durable, separate synthetic demonstration. Unit tests above use their
    # own isolated fixtures and do not count as this demonstration's openings.
    from benchmark.evaluation.test_sealed_authority_r5_66 import SealedAuthorityTests
    fixture = SealedAuthorityTests()
    fixture.setUp()
    try:
        workspace = sealed.materialize(fixture.auth, fixture.root / 'workspace', fixture.qualified)
        fixture.ledger = OUT / ('synthetic-opening' + tag + '.json')
        fixture.grant['ledger_binding'] = sealed.identity(str(fixture.ledger.resolve()))
        fixture.grant_pin = sealed.identity(fixture.grant)
        content = fixture.open()
        assert digest(content) == fixture.reference['commitment']
        rejected = False
        try:
            fixture.open()
        except sealed.ProtocolFailure:
            rejected = True
        assert rejected and fixture.store.reads == 1
        write('synthetic-lifecycle' + tag, {'qualified_authority': fixture.qualified,
            'workspace': workspace, 'placeholder': fixture.reference, 'grant': fixture.grant,
            'synthetic_openings': 1, 'second_open_rejected': rejected,
            'opened_commitment': digest(content), 'content_published': False,
            'ordinary_worker_denial': 'fresh tests 11 and 29', 'real_open_grants': 0})
        cert, capsule, evidence, cert_policy = fixture.fixture_certificate()
        write('synthetic-certificate-v2' + tag, {'certificate': cert, 'capsule': capsule,
            'evidence': evidence, 'policy': cert_policy, 'production_certificate': False})
    finally:
        fixture.doCleanups()
    from benchmark.results.phase5c.r5_43_qualification import contamination
    from benchmark.harness.test_optional_support_r5_41 import setup
    from benchmark.semantic import profile_audit_r5_41 as audit
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    _, spec, state, config = setup()
    configuration = {'transport': spec, 'state': state, 'launch': config}
    reference = 'benchmark/harness/test_optional_support_r5_41.py'
    traces = [{'path': p, 'value': v, 'artifact': reference,
        'sha256': digest((ROOT / reference).read_bytes()), 'clause': 'setup',
        'interpretation': 'Independent generic declaration; no protected contents.'}
        for p, v in audit.leaves(configuration)]
    structure = audit.structure(configuration)
    traceability = audit.traceability(configuration, traces, ROOT, {reference})
    clean = contamination()
    assert structure['valid'] and traceability['valid'] and not audit.contamination(configuration)
    assert not clean['findings'] and SCHEMA['core_constructs'] == 30
    write('schema-traceability-contamination', {'structure': structure, 'traceability': traceability,
        'leaves': len(traces), 'contamination': clean, 'core_semantics': 30})
    commands = []
    for command in ([sys.executable, '-B', '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-B', '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
                    ['git', 'diff', '--check']):
        result = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'},
                                capture_output=True, timeout=30)
        commands.append({'command': command, 'exit': result.returncode})
        assert result.returncode == 0
    write('commands', {'successful': True, 'commands': commands})
    write('historical-preservation', preserve(history))
    assert not ATTEMPTS
    write('summary' + tag, {'classification': 'R5_66_SEALED_AUTHORITY_QUALIFIED',
        'focused_tests': sum(r['tests'] for r in suites.values()),
        'focused_passed': sum(r['passed'] for r in suites.values()),
        'sealed_members': 11, 'sealed_frozen_pins': 2, 'b02_accounting': [0, 0, 0, 0],
        'protected_read_attempts': 0, 'synthetic_demonstration_openings': 1,
        'synthetic_unit_openings': 'isolated fixture openings; not benchmark observations',
        'production_batches': 0, 'production_receipts': 0, 'production_certificates': 0,
        'full_production_authority': 'NOT_RUN', 'production_qualification_started': False,
        'core_semantics': 30, 'phase5c': 'paused', 'r565_resumed': False})


def final():
    preserve(loads((OUT / 'preservation-baseline.json').read_bytes()))
    paths = [ROOT / n for n in names('ls-files', '--modified', '--others', '--exclude-standard')
        if ('r5_66' in n or 'R5_66' in n or n in ('docs/decisions.md',
            'docs/research-log.md', 'docs/project-overview.md'))]
    dispositions, pins = {}, {}
    for path in paths:
        raw = path.read_bytes()
        name = path.relative_to(ROOT).as_posix()
        dispositions[name] = publication.check_source(name, raw)
        pins[name] = digest(raw)
        if path.suffix == '.json':
            assert raw == canonical(loads(raw)) + b'\n'
        result = subprocess.run(['git', 'diff', '--no-index', '--check', '--', 'NUL', str(path)],
                                cwd=ROOT, capture_output=True, timeout=10)
        assert result.returncode in (0, 1) and not result.stdout
    assert subprocess.run(['git', 'diff', '--check'], cwd=ROOT, capture_output=True).returncode == 0
    assert not ATTEMPTS
    write('publication-integrity', {'status': 'PASS', 'source_and_evidence_sha256': pins,
        'dispositions': dispositions, 'historical_preservation': 'PASS',
        'new_file_whitespace': 'PASS', 'git_diff_check': 'PASS', 'protected_read_attempts': 0})
    print({'publication_integrity': 'PASS', 'protected_read_attempts': 0})


def security_witness():
    suite = unittest.TestLoader().loadTestsFromName(
        'benchmark.evaluation.test_sealed_authority_r5_66.SealedAuthorityTests.test_19_publication_metadata')
    result = unittest.TextTestRunner().run(suite)
    assert result.wasSuccessful() and result.testsRun == 1 and not ATTEMPTS
    write('security-witness-final', {'tests': 1, 'passed': 1, 'credential_field_retained': 'api_key',
        'input': 'existing content-pinned synthetic-security fixture',
        'publication_guard_changed': False, 'protected_content_reads': 0})


if __name__ == '__main__':
    try:
        {'qualify': qualify, 'verify-final-mechanism': lambda: qualify('-final-mechanism'),
         'security-witness': security_witness, 'final': final}[sys.argv[1]]()
    except Exception:
        if ATTEMPTS:
            write('quarantine', {'classification': 'R5_66_PROTOCOL_HALT', 'quarantine': True,
                                'protected_attempts': len(ATTEMPTS)})
        raise
