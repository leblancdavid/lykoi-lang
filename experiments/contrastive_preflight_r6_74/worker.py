"""Generate frozen inherited mechanics; never execute during CPU qualification."""
from integration import ROOT, OUT


def effective_source():
    source = (ROOT/'benchmark/results/phase6/r6_66/EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    source = source[:source.index('\ndef reload():')]
    replacements = {
        'from run import ': 'from runtime import ',
        "__import__('run')": "__import__('runtime')",
        "'round': 'R6.66'": "'round': 'R6.74'",
        "ARTIFACTS / 'step20/adapter'": "ARTIFACTS / 'step54/adapter'",
        'num_warmup_steps=2, num_training_steps=20': 'num_warmup_steps=6, num_training_steps=54',
        "read(ROOT / 'benchmark/results/phase6/r6_54/LEARNING-RATE-SCHEDULE.json')['sequence']": "read(OUT / 'SCHEDULER-SIMULATION.json')['sequence']",
        'range(1, 21)': 'range(1, 55)',
        'step in (10, 20)': 'step in (27, 54)',
        'len(steps) == 20 and len(records_seen) == 80': 'len(steps) == 54 and len(records_seen) == 216',
        "'successful_optimizer_steps': 20, 'scheduler_updates': 20": "'successful_optimizer_steps': 54, 'scheduler_updates': 54",
        "'presentations': 80": "'presentations': 216",
    }
    for old, new in replacements.items():
        assert old in source, old
        source = source.replace(old,new)
    source = source.replace('    frozen_check()\n    # Exclusive claim',
        "    frozen_check()\n    assert read(OUT/'BASE-DIAGNOSTIC.json')['sealed'], 'BASE_DIAGNOSTIC_REQUIRED'\n    # Exclusive claim")
    return source


if __name__ == '__main__':
    import os
    import sys
    assert os.environ.get('LYKOI_R6_74_EXECUTION_AUTHORIZED') == '1', 'Separate explicit owner authorization required'
    from integration import frozen_check
    frozen_check()
    source = (OUT/'EFFECTIVE-WORKER.py.txt').read_text(encoding='utf-8')
    assert source == effective_source()
    if sys.argv[1] == 'train':
        exec(compile(source,'r674-frozen-worker','exec'),globals())
        train()
    elif sys.argv[1] in ('base','adapter'):
        from runtime import diagnostic
        diagnostic(sys.argv[1])
    else:
        raise ValueError(sys.argv[1])
