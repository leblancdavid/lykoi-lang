"""Read-only terminal diagnosis; never constructs a driver or reruns a stage."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import bounded_driver_r5_57 as bounded
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import qualified_authority_r5_55 as authority
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.results.phase5c import r5_60_qualification as experiment


def main():
    read, out = experiment.read, experiment.OUT
    failure, summary, plan = [read(n) for n in ('starting-state-failure', 'summary', 'stage-plan')]
    assert summary['primary_classification'] == 'R5_60_PROTOCOL_HALT'
    assert failure['exception_class'] == 'ProtocolFailure' and failure['stage'] == 'starting-state'
    assert not (out / 'batches/qualification.json').exists()
    assert not list((out / 'batches').iterdir())
    forbidden = [s['name'] for s in plan['regressions'] if 'b02' in s['name'].casefold()]
    assert forbidden and all(bounded.NAME.fullmatch(s['name']) for s in plan['regressions'])
    assert 'b02' not in experiment.EXPERIMENT.casefold()
    capsule, qualified, policy = [read(n) for n in ('capsule', 'qualified-authority', 'authority-policy')]
    assert experiment.capture() == capsule
    assert authority.qualify(experiment.WORK, policy,
        trusted_policy_identity=experiment.prior.inherited.PIN) == qualified
    starting = read('starting-state')
    assert starting['capsule'] == capsule['identity'] and starting['qualified_authority'] == qualified['identity']
    assert starting['status'] == 'PASS'
    baseline = read('preservation-baseline')['files']
    assert all(digest((ROOT / n).read_bytes()) == pin for n, pin in baseline.items())
    for value in (capsule, qualified, plan):
        assert value == loads(canonical(value))
        tier.envelopes.unseal(value)
        publication.safe_bytes(value)
    publication.persist(out / 'stopped-diagnostic.json', {
        'status': 'PASS', 'scope': 'read-only diagnosis; no qualification retry',
        'failed_component': 'bounded_driver_r5_57.Driver.__init__',
        'failed_predicate': 'any stage identifier contains b02, case insensitive',
        'source_reference': 'benchmark/evaluation/bounded_driver_r5_57.py:68-70',
        'rejected_stage_ids': forbidden, 'qualification_binding_issued': False,
        'starting_state_record_scope': 'prerequisites passed before driver initialization; not an overall qualification PASS',
        'qualified_authority': qualified['identity'], 'members': 1083,
        'capsule': capsule['identity'], 'capsule_unchanged': True,
        'continuity': 'PASS', 'publication': 'PASS',
        'plan': plan['identity'], 'historical_files_unchanged': len(baseline),
        'new_infrastructure_defect_proven': False,
        'interpretation': 'frozen orchestration stage names incompatible with existing prohibited-name driver contract',
        'material_behavioral_or_language_regression_proven': False,
        'repair_permitted': False, 'retry_permitted': False,
        'b02_exposure': 0, 'production_receipts': 0, 'core_semantics': 30})
    print({'diagnosis': 'PASS', 'rejected_stage_ids': forbidden, 'authority': 'PASS', 'capsule_unchanged': True})


if __name__ == '__main__':
    main()
