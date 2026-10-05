"""Terminal recording only for the interrupted R5.56 candidate; no retry."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.results.phase5c import r5_56_qualification as run


def main():
    assert not (run.OUT / 'summary.json').exists()
    frozen = run.read('capsule')
    after = run.capture()
    assert after == frozen
    definitions = run.read('definitions')
    assert (run.OUT / 'certificate-v2-attempt.json').exists()
    assert not (run.OUT / 'receipt-certificate-v2.json').exists()
    assert not (run.OUT / 'certificate-v2-fresh-worker.json').exists()
    run.write('interruption', {
        'status': 'INCOMPLETE', 'stage': 'certificate-v2',
        'cause': 'parent shell terminated bounded batch at 120000 ms',
        'worker_result_persisted': False, 'receipt_persisted_before_interruption': False,
        'completed_before_interruption': 5, 'capsule_unchanged': True,
        'batch_budget_defect': '70-second loop admission excludes cost of next captures and up-to-65-second child',
        'retry_permitted': False, 'repair_permitted': False,
        'production_certificate_issued': False, 'synthetic_reservations': 0,
        'synthetic_dispatches': 0, 'synthetic_completions': 0, 'b02_exposure': 0})
    for name, definition in definitions.items():
        if (run.OUT / ('receipt-' + name + '.json')).exists():
            continue
        interrupted = name == 'certificate-v2'
        result = {'successful': False,
                  'reason': 'tool-boundary interruption' if interrupted else 'unrun after required stage interruption',
                  'attempted': interrupted, 'retry_permitted': False}
        run.write('receipt-' + name, tier.receipt(frozen, after, run.EXPERIMENT, name,
                  run.mechanism(name, definition), 'INCOMPLETE', result))
    run.qualify()


if __name__ == '__main__':
    main()
