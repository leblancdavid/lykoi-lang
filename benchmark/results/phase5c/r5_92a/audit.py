"""R5.92A non-protected evidence reproduction; never an admission service.

Run with the designated interpreter and explicit root/src sys.path bootstrap.
Only named public/synthetic tests and ordinary frozen component files are read.
New evidence is exclusive-create; historical drivers are not executed.
"""
import copy
import hashlib
import io
import json
from pathlib import Path
import tempfile
import time
import unittest
import sys

from lykoi_controller import Failure
from lykoi_pipeline.controller import ROOT, digest
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_rehearsal.public_freeze_r5_91 import configurations, integrity, eligibility, snapshot
from lykoi_rehearsal.public_service_r5_91 import PublicController, ACTIVATION
from lykoi_rehearsal.service import public_author_seed
from benchmark.evaluation.formal_requirements_r5_80 import validate, ContractError
from rehearsal.verify_r5_91 import SELECTIONS

DESTINATION = Path(__file__).resolve().parent
DIRECTORY = ROOT / 'benchmark/results/phase5c/r5_91'
REPORTS = [
    'R5_83-HELD-OUT-EXPOSURE-READINESS.md',
    'R5_84-INDEPENDENT-COVERAGE-AUTHORITY.md',
    'R5_85-PRODUCTION-FORMALIZATION-AND-EVALUATION-ARCHITECTURE.md',
    'R5_86-AUTHORITY-AND-ARTIFACT-CONTROLLER.md',
    'R5_87-AI-REQUIREMENTS-WORKSPACE.md',
    'R5_88-SEALED-AUTHORING-AND-INDEPENDENT-VERIFICATION.md',
    'R5_89-PUBLIC-REHEARSAL-CAPABILITY-CLOSURE.md',
    'R5_90-LIVE-AI-WORKER-QUALIFICATION.md',
    'R5_91-LIVE-AI-INTEGRATION-AND-PUBLIC-REHEARSAL-FREEZE.md',
    'R5_93-PREACCESS-HALT.md',
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_new(name, value):
    with (DESTINATION / name).open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + '\n')


def run_tests():
    sys.path.insert(0, str(ROOT / 'tests'))
    summary = {'version': 'r5.92a-mechanical-verification-1', 'suites': {}}
    known = {
        'benchmark.evaluation.test_formal_requirements_r5_80.FormalRequirementQualification.test_reproducible_results_and_exact_coverage_locators',
        'benchmark.evaluation.test_source_coverage_r5_84.CoverageTests.test_independent_disagreement_and_public_b01_calibration',
    }
    for name, modules in SELECTIONS.items():
        stream = io.StringIO()
        start = time.monotonic()
        suite = unittest.TestSuite(unittest.defaultTestLoader.loadTestsFromName(m) for m in modules)
        result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
        ids = [test.id() for test, _ in result.failures]
        record = {'modules': modules, 'tests': result.testsRun,
                  'passed': result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped),
                  'failures': len(result.failures), 'errors': len(result.errors),
                  'skipped': len(result.skipped), 'failure_ids': ids,
                  'elapsed_ms': int((time.monotonic() - start) * 1000)}
        record['expected_result'] = result.wasSuccessful() or (
            name == 'guarded_historical' and set(ids) == known and not result.errors and not result.skipped)
        summary['suites'][name] = record
        with (DESTINATION / (name + '.txt')).open('x', encoding='utf-8', newline='\n') as log:
            log.write(stream.getvalue())
        print(json.dumps({'suite': name, **record}), flush=True)
    summary['checks_passed_with_known_crlf_failures'] = all(r['expected_result'] for r in summary['suites'].values())
    # Diagnose only the two named PUBLIC files; do not normalize or rewrite either.
    summary['public_crlf_diagnostics'] = {}
    for relative, expected in (
        ('benchmark/requirements/B01.md', 'b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d'),
        ('benchmark/results/phase5c/r5_84/independent-soi.json', 'ff124b66301901a9e945338ccad1a354f8e393d8fe9175f06d1fbf3068d29d44'),
    ):
        raw = (ROOT / relative).read_bytes()
        normalized = hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()
        summary['public_crlf_diagnostics'][relative] = {
            'physical_sha256': hashlib.sha256(raw).hexdigest(), 'crlf_sequences': raw.count(b'\r\n'),
            'read_only_lf_sha256': normalized, 'historical_pin': expected, 'lf_matches': normalized == expected}
    write_new('verification.json', summary)
    return summary


def preaccess():
    candidate = json.loads((DIRECTORY / 'public-freeze-final.json').read_text(encoding='utf-8'))
    database = DIRECTORY / 'public-controller-final.sqlite'
    before = sha(database)
    c = PublicController(database, PRINCIPALS, candidate=candidate,
                         model_configurations=configurations(), author_seed=public_author_seed())
    try:
        c.check_integrity()
        result = {'version': 'r5.92a-preaccess-check-1', 'frozen_identity': candidate['identity'],
                  'freeze_integrity': integrity(candidate), 'public_infrastructure': eligibility(candidate, c),
                  'controller_integrity': 'PASS', 'controller_revision': c.revision,
                  'public_activation': c.activation(), 'admission_order': c.prove_admission_order()}
    finally:
        c.close()
    result['public_database_sha256'] = before
    result['public_database_bytes_unchanged'] = before == sha(database)
    current = snapshot()
    result['changed_pinned_files'] = [p for p, pin in candidate['files'].items() if current['files'].get(p) != pin]
    result['changed_snapshot_sections'] = [k for k in current if current[k] != candidate.get(k)]
    # Hypothetical NON-B03 authorization probe, in a disposable controller only.
    with tempfile.TemporaryDirectory(prefix='r5_92a_nonprotected_probe_') as tmp:
        probe = PublicController(Path(tmp) / 'probe.sqlite', PRINCIPALS, candidate=candidate,
                                 model_configurations=configurations(), author_seed=public_author_seed())
        try:
            try:
                probe.execute(CREDENTIALS['owner'], 'public', 'register', expected_revision=probe.revision,
                              kind='context', content={'version': ACTIVATION,
                              'purpose': 'SYNTHETIC_PROTECTED_EVALUATION_ONLY',
                              'candidate_identity': candidate['identity'], 'active': True})
            except Failure as exc:
                result['nonpublic_activation_probe'] = exc.as_dict()
            else:
                raise AssertionError('Unexpected nonpublic activation acceptance')
            result['probe_activation'] = probe.activation()
            result['probe_registered_artifacts'] = probe.db.execute('SELECT COUNT(*) FROM artifacts').fetchone()[0]
        finally:
            probe.close()
    # Empty-obligation synthetic bookkeeping record, no benchmark source.
    contract = {'schema_version': 'FormalRequirementContract-0.1', 'contract_id': 'nonprotected-probe',
                'revision': 1, 'source': {'id': 'synthetic-probe', 'text': 'Synthetic probe.',
                'sha256': hashlib.sha256(b'Synthetic probe.').hexdigest(), 'classification': 'SYNTHETIC'},
                'context': {'scope': 'synthetic bookkeeping only', 'domains': {}, 'assumptions': [], 'component_authority': None},
                'obligations': [], 'issues': [], 'unspecified': [], 'implementation_choices': [],
                'lineage': [], 'formalizer': 'probe', 'review': None}
    validate(contract)
    protected = copy.deepcopy(contract)
    protected['source']['classification'] = 'PROTECTED'
    try:
        validate(protected)
    except ContractError as exc:
        result['protected_provenance_probe'] = {'synthetic_control_valid': True, 'protected_rejected': True, 'code': exc.code}
    else:
        raise AssertionError('Unexpected protected provenance acceptance')
    result.update(eligible_for_protected_B03_admission=False, protected_authorization=None,
                  blockers=['FROZEN_CONTROLLER_PUBLIC_ONLY', 'FROZEN_FRC_PROTECTED_PROVENANCE_UNSUPPORTED',
                            'NO_ENFORCED_B03_SINGLE_EVALUATION_ADMISSION'],
                  B03_state=['B03_PRISTINE', 'B03_NOT_EVALUATED', 'B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT'],
                  counter_basis='Inherited r5_91/final-audit.json plus scoped R5.92A activity; no protected ledger inspected',
                  B03_round_counters={k: 0 for k in ('source_access_attempts', 'source_reads', 'content_revealing_metadata',
                      'openings', 'admissions', 'observations', 'formalizer_dispatches', 'reviewer_dispatches',
                      'author_dispatches', 'static_consumer_accesses', 'development_exposures', 'authorizations',
                      'frc_creations', 'projections', 'compilations', 'verification_runs')})
    write_new('preaccess.json', result)
    return result


def main():
    sources = {str((ROOT / 'benchmark/results/phase5c' / name).relative_to(ROOT)).replace('\\', '/'): sha(ROOT / 'benchmark/results/phase5c' / name)
               for name in REPORTS}
    sources.update({str((DIRECTORY / name).relative_to(ROOT)).replace('\\', '/'): sha(DIRECTORY / name)
                    for name in ('public-freeze-final.json', 'activation.json', 'final-audit.json', 'verification.json')})
    verification = run_tests()
    check = preaccess()
    body = {'version': 'r5.92a-readiness-reassessment-1',
            'classification': 'R5_92A_B03_READINESS_NOT_REPRODUCED',
            'authorization_blocker': 'R5_92A_PROTECTED_ADMISSION_REQUIRES_FROZEN_MACHINERY_CHANGE',
            'R5_92_B03_EXPOSURE_READY': False, 'sources': sources,
            'verification_sha256': sha(DESTINATION / 'verification.json'),
            'preaccess_sha256': sha(DESTINATION / 'preaccess.json'),
            'audit_script_sha256': sha(Path(__file__)), 'frozen_identity': check['frozen_identity'],
            'mechanical_checks_passed_with_known_crlf_failures': verification['checks_passed_with_known_crlf_failures'],
            'protected_evaluation_authorization_created': False,
            'B03_access_in_this_round': False, 'R5_93_halt_preserved_sha256': sources['benchmark/results/phase5c/R5_93-PREACCESS-HALT.md']}
    write_new('readiness.json', {**body, 'identity': digest(body)})
    assert verification['checks_passed_with_known_crlf_failures']
    assert check['freeze_integrity'] and check['public_database_bytes_unchanged']
    assert not check['changed_pinned_files'] and not check['changed_snapshot_sections']
    print(json.dumps({'classification': body['classification'], 'evidence_identity': digest(body),
                      'eligible_for_protected_B03_admission': False}), flush=True)


if __name__ == '__main__':
    main()
