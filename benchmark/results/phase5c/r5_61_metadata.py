"""Extract only safe frozen-plan test IDs; never open/import sealed test sources."""
import sys
from pathlib import Path
from benchmark.evaluation.recorder_r5_43 import loads

ROOT = Path(__file__).resolve().parents[3]


def prohibited_ids():
    plan = loads((ROOT / 'benchmark/results/phase5c/R5_60-evidence/stage-plan.json').read_bytes())
    modules = ('test_b02_retry_r5_17', 'test_b02_retry_r5_19',
               'test_b02_retry_r5_21', 'test_b02_integration_r5_23')
    found = set()
    for row in plan['regressions']:
        definition = row['definition']
        if definition[0] != 'suite' or definition[1] != 'benchmark/harness':
            continue
        for identity in definition[4]:
            if identity.split('.')[0] in modules or identity.split('.')[-1] == 'test_read_only_validation_of_both_continuation_states':
                found.add(identity)
    return sorted(found)


if __name__ == '__main__':
    ids = prohibited_ids()
    if '--write-index' in sys.argv:
        from benchmark.evaluation.publication_r5_59 import persist
        persist(ROOT / 'benchmark/evaluation/prohibited_test_index_r5_61.json', {
            'policy': 'lykoi-safe-prohibited-test-index-r5.61-v1',
            'source': 'R5_60-evidence/stage-plan.json',
            'source_identity': 'e86148eab0122d9af7c2fe91ba69ead57f0746d9aa8620f10cf7fd34b67ad150',
            'tests': {identity: {'capabilities': ['B02_ACCEPTANCE'], 'status': 'PROHIBITED'}
                      for identity in ids}})
        print('Safe index written:', len(ids))
        sys.exit(0)
    print('\n'.join(ids))
    print('COUNT', len(ids))
