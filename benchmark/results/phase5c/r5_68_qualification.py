"""Bounded certificate promotion only; metadata Git commands and safe suites.

prepare freezes public declarations; qualify consumes the independently pinned
declaration. No complete production plan, reservation or B02 opener exists here.
"""
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import certificate_r5_68 as modes
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation import preexposure_r5_45 as envelopes
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.results.phase5c.r5_66_inventory import inventory
from benchmark.evaluation.test_certificate_modes_r5_68 import declaration

OUT = ROOT / 'benchmark/results/phase5c/R5_68-evidence'
EXPERIMENT = 'R5.68-production-sealed-certificate-promotion-v1'
# Independently selected by the reviewed control plane after prepare and before
# issuance. Never loaded from the declaration payload or a caller registration.
TRUSTED_DECLARATION = '1e3a26664e6d9082ee9c8f7766dd86df2354c986928bdd30c48dcbe84b3e75e2'
PROTECTED = {r.path.resolve() for r in guard.repository_resources(ROOT)}
ATTEMPTS = []


def protect(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        if Path(os.fsdecode(args[0])).resolve() in PROTECTED:
            ATTEMPTS.append('DENIED_BEFORE_CONTENT')
            raise RuntimeError('R5_68_PROTOCOL_HALT')


sys.addaudithook(protect)


def write(name, value):
    path = OUT / (name + '.json')
    if path.exists():
        assert path.read_bytes() == canonical(value) + b'\n'
    else:
        publication.persist(path, value)


def read(name):
    raw = (OUT / (name + '.json')).read_bytes()
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    return value


def names(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).splitlines()


def baseline():
    files, protected = {}, {}
    for name in sorted(set(names('ls-files', '--cached', '--others', '--exclude-standard', 'benchmark/results'))):
        if 'R5_68' in name or '/r5_68_' in name:
            continue
        path = ROOT / name
        if path.resolve() in PROTECTED:
            s = path.stat()
            protected[name] = {'size': s.st_size, 'mtime_ns': s.st_mtime_ns}
        else:
            files[name] = digest(path.read_bytes())
    return {'files': files, 'protected_metadata_only': protected}


def preserve():
    history = read('preservation-baseline')
    for name, pin in history['files'].items():
        assert digest((ROOT / name).read_bytes()) == pin
    for name, row in history['protected_metadata_only'].items():
        s = (ROOT / name).stat()
        assert row == {'size': s.st_size, 'mtime_ns': s.st_mtime_ns}
    old = loads((OUT.parent / 'R5_67-evidence/terminal-stop.json').read_bytes())
    assert old['classification'] == 'R5_67_PRODUCTION_CERTIFICATE_GAP'
    assert not (OUT.parent / 'R5_67-evidence/certificate.json').exists()
    return {'unsealed_byte_preserved': len(history['files']),
        'protected_metadata_preserved': len(history['protected_metadata_only']),
        'r567_classification': old['classification'], 'r567_resumed': False}


def actual():
    value = inventory()
    policy = {k: value[k] for k in ('authority', 'policy_binding', 'members')}
    policy['frozen_authority'] = {n: r['sha256'] for n, r in value['members'].items() if r['frozen']}
    authority = sealed.Authority(ROOT, policy, trusted_policy_identity=sealed.identity(policy),
                                 observer=sealed.GitMetadata(ROOT))
    return value, policy, authority, authority.qualify()


def capsule_policy():
    # Explicit safe individual files, never a benchmark directory/discovery root.
    return {'scopes': {'subject': ['air/task_manager.json'],
        'compiler': ['src/air_compiler/validator.py'], 'semantics': ['schema/axiom-v0.3.schema.json'],
        'profiles': ['benchmark/harness/test_optional_support_r5_41.py'],
        'authority': ['benchmark/results/phase5c/R5_68-evidence/sealed-authority.json'],
        'evaluator': ['benchmark/evaluation/certificate_r5_68.py',
                      'benchmark/evaluation/sealed_authority_r5_66.py',
                      'benchmark/evaluation/publication_r5_59.py',
                      'benchmark/evaluation/publication_schema_r5_64.py',
                      'benchmark/evaluation/security_r5_47.py',
                      'benchmark/evaluation/tier2_r5_51.py',
                      'benchmark/evaluation/preexposure_r5_45.py',
                      'benchmark/evaluation/recorder_r5_43.py']},
        'unknown': [], 'recorder': 'r568-candidate-recorder',
        'qualification_scope': 'certificate promotion; not complete production qualification'}


def capture():
    return tier.capture(ROOT, capsule_policy(), tier.controlled_environment({}, ROOT))


def prepare():
    assert not OUT.exists()
    history = baseline()
    OUT.mkdir()
    write('preservation-baseline', history)
    value, policy, authority, qualified = actual()
    write('sealed-inventory', value)
    write('sealed-policy', policy)
    write('sealed-authority', qualified)
    workspace = sealed.materialize(authority, OUT / 'cooperative-workspace', qualified)
    write('workspace', workspace)
    identity = tier.seal({'protocol': 'lykoi-r5.68-qualification-v1', 'experiment': EXPERIMENT,
        'purpose': 'production-sealed certificate promotion only', 'authority': qualified['identity'],
        'mode': modes.PRODUCTION, 'b02_accounting': [0, 0, 0, 0], 'core_semantics': 30,
        'full_production_qualification': False})
    write('qualification', identity)
    capsule = capture()
    assert capture() == capsule
    write('capsule', capsule)
    cert_policy = {'experiment': EXPERIMENT, 'stages': {n: 'r568-non-B02-' + n for n in modes.v2.REQUIRED},
        'qualified_authority': qualified['identity'], 'authority_role': capsule['roles']['authority'],
        'semantic_count': 30, 'canonical_protocol': tier.CANONICAL_PROTOCOL,
        'recorder': capsule['policy']['recorder'],
        'observation_state': {'reservations': 0, 'dispatches': 0, 'completions': 0}}
    write('certificate-policy', cert_policy)
    clean = contamination_schema()
    results = {'identity': {'successful': True, 'semantic_count': 30, 'qualification': identity['identity']},
        'authority': {'successful': True, 'qualified_authority': qualified['identity']},
        'contamination': {'successful': True, 'findings': clean['contamination']['findings']},
        'workspace': {'successful': True, 'dedicated': workspace['dedicated'], 'workspace': workspace['identity'],
                      'sealed_materialized': workspace['sealed_materialized']}}
    receipts = {n: tier.receipt(capsule, capture(), EXPERIMENT, n, cert_policy['stages'][n], 'PASS', results[n])
                for n in results}
    assert all(r['status'] == 'PASS' for r in receipts.values())
    write('non-b02-receipts', receipts)
    owner = declaration(qualified, capsule, cert_policy, identity['identity'], modes.PRODUCTION)
    write('production-declaration', owner)
    write('declaration-schema', loads(modes.DECLARATION_SCHEMA.definition))
    write('prepare', {'status': 'PASS', 'declaration_identity': digest(canonical(owner)),
        'certificate_issued': False, 'sealed_members': 11, 'frozen_pins': 2,
        'scope': '11-member sealed authority / narrow actual Tier-2 capture / non-B02 receipts',
        'protected_read_attempts': len(ATTEMPTS)})
    assert not ATTEMPTS
    print({'prepared': True, 'declaration_identity': digest(canonical(owner))})


def contamination_schema():
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
    row = {'structure': structure, 'traceability': traceability, 'leaves': len(traces),
           'contamination': clean, 'core_semantics': 30}
    write('schema-traceability-contamination', row)
    return row


SUITES = ('benchmark.evaluation.test_certificate_modes_r5_68',
    'benchmark.evaluation.test_sealed_authority_r5_66',
    'benchmark.evaluation.test_capability_guard_r5_61',
    'benchmark.evaluation.test_mediated_child_r5_62',
    'benchmark.evaluation.test_continuity_r5_59',
    'benchmark.evaluation.test_publication_r5_59',
    'benchmark.evaluation.test_publication_r5_64',
    'benchmark.evaluation.test_security_r5_47',
    'benchmark.evaluation.test_ai_independence_r5_49',
    'benchmark.harness.test_optional_support_r5_41')


def qualify():
    assert not (OUT / 'summary.json').exists()
    preserve()
    suites = {}
    # Historical test_certificate_r5_55 copies/reads all sealed subjects in its
    # setUpClass, so use the no-read V2/linkage witnesses in the R5.66 suite.
    for module in SUITES:
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
        write(module.rsplit('.', 1)[1], row)
        print(module, row['passed'], '/', row['tests'], flush=True)
        if not result.wasSuccessful():
            print(stream.getvalue())
        assert result.wasSuccessful()
        suites[module] = row
    value, policy, authority, qualified = actual()
    assert qualified == read('sealed-authority') and policy == read('sealed-policy')
    capsule, cert_policy, evidence = read('capsule'), read('certificate-policy'), read('non-b02-receipts')
    owner = read('production-declaration')
    binding = {'trusted_declaration_identity': TRUSTED_DECLARATION, 'mode': modes.PRODUCTION,
               'qualification': read('qualification')['identity']}
    current = capture()
    assert current == capsule
    cert = modes.certificate(qualified, capsule, evidence, cert_policy, authority, owner, **binding)
    write('certificate-candidate', cert)
    cert = read('certificate-candidate')
    assert modes.validate(cert, qualified, capsule, evidence, cert_policy, capture(), authority, owner, **binding)
    assert cert == modes.certificate(qualified, capsule, evidence, cert_policy, authority, owner, **binding)
    for operation in ('SEALED_RESOURCE_OPEN', 'B02_SEAL_OPEN_AUTHORIZED', 'SYNTHETIC_GATE_QUALIFIED'):
        rejected = False
        try:
            modes.require_operation(cert, operation, qualified, capsule, evidence, cert_policy,
                                    current, authority, owner, **binding)
        except modes.ProtocolFailure:
            rejected = True
        assert rejected
    workspace = read('workspace')
    assert workspace['sealed_materialized'] == 0 and not workspace['git_database_present']
    for resource, reference in workspace['references'].items():
        path = OUT / 'cooperative-workspace/.sealed' / (sealed.identity(resource) + '.json')
        assert loads(path.read_bytes()) == reference
    assert not (OUT / 'cooperative-workspace/.git').exists()
    assert not any((OUT / name).exists() for name in ('opening.json', 'opening.result.json', 'observation-authorization.json'))
    commands = []
    for command in ([sys.executable, '-B', '-m', 'air_compiler.cli', 'validate', 'air/task_manager.json'],
                    [sys.executable, '-B', '-m', 'air_compiler.cli', 'safety', 'air/task_manager.json'],
                    ['git', 'diff', '--check']):
        result = subprocess.run(command, cwd=ROOT, env={**os.environ, 'PYTHONPATH': 'src'},
                                capture_output=True, timeout=30)
        commands.append({'command': command, 'exit': result.returncode})
        assert result.returncode == 0
    write('commands', {'successful': True, 'commands': commands})
    write('historical-preservation', preserve())
    assert not ATTEMPTS
    write('summary', {'classification': 'R5_68_PRODUCTION_SEALED_CERTIFICATE_QUALIFIED',
        'focused_tests': sum(r['tests'] for r in suites.values()),
        'focused_passed': sum(r['passed'] for r in suites.values()),
        'protected_read_attempts': 0, 'protected_content_reads': 0,
        'b02_accounting': [0, 0, 0, 0], 'b02_open_grants': 0, 'b02_openings': 0,
        'opening_ledger_reservations': 0, 'opening_ledger_consumptions': 0,
        'sealed_members': 11, 'sealed_frozen_pins': 2, 'production_certificate_candidates': 1,
        'full_production_batches': 0, 'full_production_receipts': 0, 'full_production_certificates': 0,
        'non_b02_candidate_receipts': 4, 'synthetic_observations': [0, 0, 0],
        'full_production_qualification_started': False, 'core_semantics': 30,
        'phase5c': 'paused', 'r567_resumed': False, 'future_observation_authorization_created': False})


def final():
    preserve()
    paths = [ROOT / n for n in names('ls-files', '--modified', '--others', '--exclude-standard')
        if ('r5_68' in n or 'R5_68' in n or n in ('docs/decisions.md',
            'docs/research-log.md', 'docs/project-overview.md', 'docs/certificate-modes-r5.68.md'))]
    pins, dispositions = {}, {}
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
        'dispositions': dispositions, 'historical_preservation': 'PASS', 'new_file_whitespace': 'PASS',
        'git_diff_check': 'PASS', 'protected_read_attempts': 0})
    print({'publication_integrity': 'PASS', 'protected_read_attempts': 0})


if __name__ == '__main__':
    try:
        {'prepare': prepare, 'qualify': qualify, 'final': final}[sys.argv[1]]()
    except Exception:
        if ATTEMPTS:
            write('quarantine', {'classification': 'R5_68_PROTOCOL_HALT',
                                 'protected_read_attempts': len(ATTEMPTS)})
        raise
