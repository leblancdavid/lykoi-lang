"""Execution-only R5.69; frozen starting prerequisites, terminal on failure.

No new gate, certificate adapter, opening consumer or protected-content loader.
Historical V3 evidence is used only to probe the existing consumer contract,
never as a fresh production receipt or R5.69 certificate.
"""
import ast
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import bounded_driver_r5_57 as bounded
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import certificate_r5_68 as modes
from benchmark.evaluation import mediated_child_r5_62 as child
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, digest, loads

OUT = ROOT / 'benchmark/results/phase5c/R5_69-evidence'
SOURCE = 'benchmark/results/phase5c/r5_69_qualification.py'
AUDITOR = 'benchmark/results/phase5c/r5_69_independent_audit.py'
EXPERIMENT = 'R5.69-final-production-sealed-gate-qualification-v1'
PROTECTED = {r.path.resolve() for r in guard.repository_resources(ROOT)}
ATTEMPTS = []


def protect(event, args):
    if event == 'open' and isinstance(args[0], (str, bytes, os.PathLike)):
        if Path(os.fsdecode(args[0])).resolve() in PROTECTED:
            ATTEMPTS.append('DENIED_BEFORE_CONTENT')
            raise RuntimeError('R5_69_PROTOCOL_HALT')


sys.addaudithook(protect)


def ordinary(name):
    path = ROOT / name
    assert path.resolve() not in PROTECTED
    return path.read_bytes()


def context(name):
    return ({'schema': schemas.QUALIFICATION_IDENTITY,
             'schema_identity': schemas.QUALIFICATION_IDENTITY_PIN}
            if name == 'qualification-identity' else {})


def write(name, value):
    publication.persist(OUT / (name + '.json'), value, **context(name))


def read(name):
    raw = ordinary('benchmark/results/phase5c/R5_69-evidence/' + name + '.json')
    value = loads(raw)
    assert raw == canonical(value) + b'\n'
    publication.safe_bytes(value, **context(name))
    return value


def historical(round_name, name):
    return loads(ordinary('benchmark/results/phase5c/' + round_name + '-evidence/' + name + '.json'))


def freeze():
    assert OUT.parent.is_dir() and not OUT.exists()
    assert not subprocess.check_output(['git', 'diff', '--name-only', '--', 'benchmark/results'], cwd=ROOT)
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard',
                                    'benchmark/results'], cwd=ROOT, text=True).splitlines()
    files, metadata = {}, {}
    for name in sorted(set(names) - {SOURCE, AUDITOR}):
        path = ROOT / name
        if path.resolve() in PROTECTED:
            stat = path.stat()
            metadata[name] = {'size': stat.st_size, 'mtime_ns': stat.st_mtime_ns}
        else:
            files[name] = digest(ordinary(name))
    OUT.mkdir()
    write('preservation-baseline', {'files': files, 'sealed_metadata_only': metadata,
        'prospective_sources_excluded_before_capture': [SOURCE, AUDITOR]})
    inherited = historical('R5_67', 'stage-plan')
    policy = historical('R5_67', 'authority-policy')
    assert len(policy['members']) == 1083
    assert sum(r['classification'] == 'SEALED' for r in policy['members'].values()) == 11
    write('authority-policy', policy)
    closure = sorted(p.relative_to(ROOT).as_posix()
        for directory in ('src', 'benchmark/semantic', 'benchmark/evaluation', 'benchmark/harness', 'tests')
        for p in (ROOT / directory).rglob('*.py')
        if p.resolve() not in PROTECTED and '__pycache__' not in p.parts)
    registry = child.registry(ROOT, {'safe-indexed-regressions': (
        'benchmark.evaluation.safe_workers_r5_62', 'harness', closure)})
    registry_pin = digest(canonical(registry))
    write('worker-registry', registry)
    stages = inherited['regressions']
    filename = 'test_certificate_modes_r5_68.py'
    tree = ast.parse(ordinary('benchmark/evaluation/' + filename))
    ids = [filename[:-3] + '.' + cls.name + '.' + method.name
           for cls in tree.body if isinstance(cls, ast.ClassDef)
           for method in cls.body if isinstance(method, ast.FunctionDef) and method.name.startswith('test_')]
    assert len(ids) == 28
    for offset in range(0, len(ids), 4):
        stages.append({'name': f'certificate-v3-modes-{offset // 4:02d}', 'required': True,
            'definition': ['suite', 'benchmark/evaluation', filename, False, ids[offset:offset + 4]],
            'cost': vars(bounded.production_cost(35)), 'capabilities': sorted(guard.GENERIC)})
    for i, row in enumerate(stages):
        row['dependencies'] = [stages[i - 1]['name']] if i else ['starting-state']
        if row['definition'][0] == 'suite':
            prefix = row['definition'][1].replace('/', '.') + '.'
            row.update(worker_registry=registry_pin,
                worker_identity=child.worker_identity(registry['workers']['safe-indexed-regressions']),
                selection={'identities': [t if t in exclusion.index()['tests'] else prefix + t
                                         for t in row['definition'][4]]},
                worker='safe-indexed-regressions', mediated_policy=child.VERSION,
                exclusion=exclusion.INDEX_PIN, execution_class='R5.62 mediated safe-indexed worker')
    selected = [t for r in stages if r['name'].startswith('harness-')
                for t in r.get('selection', {}).get('identities', []) if t in exclusion.index()['tests']]
    assert len(selected) == len(set(selected)) == 36
    pins = {n: digest(ordinary(n)) for n in inherited['implementation_sha256']}
    pins['benchmark/evaluation/certificate_r5_68.py'] = digest(ordinary('benchmark/evaluation/certificate_r5_68.py'))
    preflight = ['mechanism-continuity', 'production-gate-consumer-compatibility',
                 'qualified-authority', 'sealed-members', 'frozen-pins', 'tier2-capsule',
                 'production-declaration-integrity', 'starting-state']
    integration = ['production-certificate', 'cooperative-workspace-linkage', 'production-gate',
        'certificate-alone-b02-opening-rejection', 'synthetic-reservation',
        'synthetic-combined-authorization-opening', 'synthetic-dispatch', 'synthetic-completion',
        'immediate-post-verification', 'second-observation-rejection', 'alternate-ledger-replay-rejection',
        'historical-preservation', 'publication-security', 'ai-independence', 'final-independent-audit']
    plan = tier.seal({**{k: v for k, v in inherited.items() if k not in ('identity', 'experiment')},
        'experiment': EXPERIMENT, 'regressions': stages,
        'preflight': [{'name': n, 'required': True, 'dependencies': [preflight[i - 1]] if i else []}
                      for i, n in enumerate(preflight)],
        'integration': [{'name': n, 'required': True,
            'dependencies': [integration[i - 1]] if i else [stages[-1]['name']]}
            for i, n in enumerate(integration)],
        'worker_registry': registry_pin, 'implementation_sha256': pins,
        'authority_policy': sealed.identity(policy), 'certificate_adapter': 'benchmark.evaluation.certificate_r5_68',
        'production_gate_adapter': 'benchmark.evaluation.tier2_r5_51.StaticGate',
        'mode': modes.PRODUCTION, 'declaration_schema': modes.DECLARATION_SCHEMA_PIN,
        'production_declaration_policy': 'canonical external pin; exact fresh qualification/authority/capsule/receipt-policy bindings',
        'gate_preflight': 'existing consumer must accept V3 without adapter replacement; historical candidate is compatibility input only',
        'combined_consumer_policy': 'existing qualified consumer only; no new two-object consumer or opening API',
        'sealed_resource_policy': '11 closed commitment/provenance members; two frozen pins; no content reads',
        'resources': {r.identity: r.capability for r in guard.repository_resources(ROOT)},
        'forbidden_operations': ['B02_CONTENT_READ', 'B02_SEAL_OPEN', 'B02_CHECKED_PLAN', 'B02_READINESS',
            'B02_AUDIT', 'B02_ADMISSION', 'B02_RESERVATION', 'B02_DISPATCH', 'B02_GENERATION',
            'B02_EXECUTION', 'B02_ACCEPTANCE', 'B02_OBSERVATION_AUTHORIZATION'],
        'coverage': inherited['coverage'] + ['CertificateV3 production-sealed mode and separate observation boundary']})
    write('stage-plan', plan)
    identity = tier.seal({'experiment': EXPERIMENT, 'plan': plan['identity'], 'authority': policy['authority'],
        'authorization': policy['policy_binding'], 'bounded_driver': bounded.VERSION,
        'mediated_worker_policy': child.VERSION, 'registry': registry_pin,
        'exclusion': exclusion.INDEX_PIN, 'resource_policy': guard.POLICY,
        'orchestration': digest(ordinary(SOURCE)), 'fresh_receipts_only': True,
        'state_binding': 'explicit PRODUCTION_SEALED; canonical externally pinned V3 declaration required before issuance'},
        **context('qualification-identity'))
    write('qualification-identity', identity)
    assert read('qualification-identity') == identity and read('stage-plan') == plan
    tier.envelopes.unseal(read('qualification-identity'))
    write('freeze', {'status': 'PASS', 'plan': plan['identity'], 'qualification': identity['identity'],
        'regression_stages': len(stages), 'preflight_stages': len(preflight), 'integration_stages': len(integration),
        'constructed': True, 'sealed': True, 'persisted': True, 'schema_revalidation': True,
        'canonical_reload': True, 'mode': modes.PRODUCTION, 'prohibited_metadata_skips': 36,
        'production_declaration_issued': False, 'protected_read_attempts': len(ATTEMPTS)})
    print({'freeze': 'PASS', 'regression_stages': len(stages), 'qualification': identity['identity']})


def start():
    assert not (OUT / 'terminal-stop.json').exists()
    plan, identity = read('stage-plan'), read('qualification-identity')
    tier.envelopes.unseal(plan)
    tier.envelopes.unseal(identity)
    assert identity['plan'] == plan['identity'] and identity['orchestration'] == digest(ordinary(SOURCE))
    assert digest(canonical(read('worker-registry'))) == identity['registry'] == plan['worker_registry']
    assert sealed.identity(read('authority-policy')) == plan['authority_policy']
    for name, pin in plan['implementation_sha256'].items():
        assert digest(ordinary(name)) == pin
    inherited = historical('R5_68', 'summary')
    assert inherited['classification'] == 'R5_68_PRODUCTION_SEALED_CERTIFICATE_QUALIFIED'
    assert inherited['b02_accounting'] == [0, 0, 0, 0] and inherited['core_semantics'] == 30
    assert inherited['protected_read_attempts'] == inherited['protected_content_reads'] == 0
    assert inherited['opening_ledger_reservations'] == inherited['opening_ledger_consumptions'] == 0
    pins = historical('R5_68', 'publication-integrity')['source_and_evidence_sha256']
    for name, pin in pins.items():
        if name.startswith('benchmark/evaluation/'):
            assert digest(ordinary(name)) == pin
    from benchmark.semantic.application_boundary_r5_41 import SCHEMA
    from benchmark.results.phase5c.r5_43_qualification import contamination
    clean = contamination()
    assert SCHEMA['core_constructs'] == 30 and not clean['findings'] and not ATTEMPTS
    write('mechanism-continuity', {'status': 'PASS', 'inherited': inherited['classification'],
        'implementation_sha256': plan['implementation_sha256'], 'contamination': clean,
        'semantic_count': 30, 'b02_read_attempts': 0, 'b02_content_reads': 0,
        'b02_accounting': [0, 0, 0, 0], 'opening_accounting': [0, 0],
        'scope': 'implementation continuity and inherited accounting; no behavioral receipt reuse'})
    # Invoke the exact unchanged validator called by StaticGate.prepare. No
    # ownership marker, observation recorder, worker or opener is entered.
    cert, capsule, evidence, policy = [historical('R5_68', n) for n in
        ('certificate-candidate', 'capsule', 'non-b02-receipts', 'certificate-policy')]
    assert cert['mode'] == modes.PRODUCTION and cert['protocol'] == modes.PROTOCOL
    rejected = False
    try:
        tier.validate(cert, capsule, evidence, policy, capsule)
    except (ProtocolFailure, KeyError) as error:
        rejected = True
        error_type = type(error).__name__
    assert rejected
    failure = {'status': 'FAIL', 'stage': 'production-gate-consumer-compatibility',
        'component': 'benchmark/evaluation/tier2_r5_51.py',
        'implementation_sha256': plan['implementation_sha256']['benchmark/evaluation/tier2_r5_51.py'],
        'call_chain': 'StaticGate.prepare -> tier2.validate -> tier2.certificate (R5.51)',
        'input_protocol': cert['protocol'], 'input_mode': cert['mode'],
        'input_certificate': cert['identity'], 'input_scope': 'historical qualified mechanism compatibility probe only',
        'validator_invoked': True, 'rejected': True, 'error_type': error_type, 'diagnostics': 'withheld',
        'reason': 'existing observation gate validates R5.51 certificate policy, not CertificateV3 production-sealed policy',
        'fresh_certificate_issued': False, 'historical_receipt_reuse': False,
        'protected_read_attempts': len(ATTEMPTS), 'protected_content_reads': 0}
    write('starting-state-failure', failure)
    classification = 'R5_69_OBSERVATION_CONTROL_GAP'
    write('terminal-stop', {'classification': classification, 'failed_stage': failure['stage'],
        'repair_permitted': False, 'retry_permitted': False, 'resume_permitted': False})
    states = {r['name']: 'NOT_RUN' for r in plan['preflight'] + plan['regressions'] + plan['integration']}
    states.update({'mechanism-continuity': 'PASS', failure['stage']: 'FAIL'})
    write('summary', {'classification': classification, 'failed_stage': failure['stage'],
        'plan': plan['identity'], 'qualification': identity['identity'], 'stages': states,
        'starting_state': 'FAIL', 'production_gate_qualified': False,
        'production_batches': 0, 'production_receipts': 0, 'production_certificates': 0,
        'fresh_qualified_authority': 'NOT_RUN', 'sealed_member_verification': 'NOT_RUN',
        'frozen_pin_verification': 'NOT_RUN', 'capsule': 'NOT_RUN', 'workspace': 'NOT_RUN',
        'production_authorization': 'REQUIRED_NOT_ISSUED', 'synthetic_accounting': [0, 0, 0],
        'b02_accounting': [0, 0, 0, 0], 'b02_read_attempts': len(ATTEMPTS), 'b02_content_reads': 0,
        'opening_accounting': [0, 0], 'b02_observation_authorizations': 0, 'core_semantics': 30,
        'contamination': 'clean', 'historical_receipts_reused': 0,
        'repair_occurred': False, 'retry_occurred': False, 'resume_occurred': False,
        'production_final_audit': 'NOT_RUN', 'ai_independence_regressions': 'NOT_RUN', 'phase5c': 'paused'})
    print({'classification': classification, 'failed_stage': failure['stage'], 'protected_content_reads': 0})


if __name__ == '__main__':
    try:
        {'freeze': freeze, 'start': start}[sys.argv[1]]()
    except Exception as error:
        if OUT.is_dir() and not (OUT / 'terminal-stop.json').exists():
            write('terminal-stop', {'classification': 'R5_69_PROTOCOL_HALT', 'invocation': sys.argv[1],
                'error_type': type(error).__name__, 'diagnostics': 'withheld',
                'protected_read_attempts': len(ATTEMPTS), 'protected_content_reads': 0,
                'repair_permitted': False, 'retry_permitted': False, 'resume_permitted': False})
        raise SystemExit('R5_69_PROTOCOL_HALT: stopped; diagnostics withheld') from None
