"""Production scheduler integration and bounded non-B02 dry qualification.

Future callers supply freshly captured state/authority and fixed stage definitions.
No import or entry point resumes R5.56 or creates an observation gate.
"""

from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import bounded_driver_r5_57 as bounded
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import digest, canonical


def production_driver(output, experiment, capsule, qualified_authority, stages, capture, live_authority, **options):
    return bounded.Driver(output, experiment, capsule, qualified_authority, stages,
                          capture, live_authority, **options)


def dry(output, batch_budget=None):
    output = Path(output)
    if batch_budget is None:
        assert output.parent.is_dir() and not output.exists()
        output.mkdir()
    names = ['benchmark/evaluation/bounded_driver_r5_57.py',
             'benchmark/results/phase5c/r5_57_driver.py']
    policy = {'scopes': {r: ['README.md'] for r in tier.ROLES}, 'unknown': [],
              'recorder': 'synthetic:r557-driver-only', 'consumer': 'synthetic worker only',
              'native_materiality': [], 'exclusions': 'development authoring state'}
    policy['scopes']['evaluator'] = names
    environment = tier.controlled_environment({}, ROOT)
    captures = []
    def capture():
        started = time.monotonic()
        value = tier.capture(ROOT, policy, environment)
        captures.append(time.monotonic() - started)
        return value
    capsule = capture() if batch_budget is None else bounded.reload(output / 'capsule.json')
    authority_path = ROOT / 'benchmark/results/phase5c/R5_53-authority-successor-v1.json'
    live = lambda: digest(authority_path.read_bytes())
    authority = live()
    now, workers = [0], []
    stages = {}
    for i in range(6):
        path = output / f'worker-{i}.json'
        callback = bounded.child([sys.executable, '-B', '-S', str(Path(__file__).resolve()),
                                  'worker', str(path)], ROOT, environment, path)
        def run(timeout, callback=callback):
            started = time.monotonic()
            result = callback(timeout)
            workers.append(time.monotonic() - started)
            now[0] += 10  # Artificial test budget debit, not a claimed wall measurement.
            return result
        stages[f'synthetic-{i}'] = {'mechanism': digest(canonical(['synthetic', i, bounded.VERSION])),
                                   'cost': bounded.Cost(1, 1, 2, 1, 1, 1, 1, 1), 'run': run}
    driver = production_driver(output, 'synthetic:r557-dry-fresh', capsule, authority,
                               stages, capture, live, clock=lambda: now[0])
    if batch_budget is None:
        driver.initialize()
        security.persist(output / 'capsule.json', capsule)
        print({'dry_initialization': 'PASS', 'b02_exposure': 0})
        return
    row = driver.batch(batch_budget)
    receipts, _, _ = driver.validate()
    number = len(list(output.glob('batch-*.json')))
    security.persist(output / f'dry-result-{number}.json', tier.seal({'successful': True,
        'batch': row['identity'], 'new_receipts': len(row['receipts']), 'total_receipts': len(receipts),
        'disposition': row['disposition'],
        'capsule': capsule['identity'], 'authority': authority,
        'capture_wall_seconds': captures, 'child_wall_seconds': workers,
        'clock': 'artificial ten-second per-stage debit; actual wall timings separately recorded',
        'production_scheduler': bounded.VERSION, 'real_child_processes': len(workers),
        'b02_exposure': 0, 'reservations': 0, 'dispatches': 0, 'completions': 0,
        'production_qualification': False, 'semantic_count': 30, 'phase5c': 'paused'}))
    print({'dry_qualification': 'PASS', 'new_receipts': len(row['receipts']),
           'disposition': row['disposition'], 'b02_exposure': 0})


if __name__ == '__main__':
    if sys.argv[1] == 'worker':
        security.persist(Path(sys.argv[2]), {'successful': True, 'synthetic_only': True})
    elif sys.argv[1] == 'dry':
        dry(sys.argv[2])
    elif sys.argv[1] == 'dry-batch':
        dry(sys.argv[2], float(sys.argv[3]))
    else:
        raise SystemExit('only synthetic dry qualification permitted')
