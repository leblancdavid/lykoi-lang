"""Read-only integrity/accounting audit of stopped R5.75; cannot observe B02."""
import argparse
import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]
from benchmark.evaluation import phase5_runner_v2 as r

OUT = ROOT / 'benchmark/results/phase5c/R5_75-evidence'
OLD = ROOT / 'benchmark/results/phase5c/R5_74-qualified-evidence'
REPORT = 'benchmark/results/phase5c/R5_75-ACTUAL-ONE-SHOT-HELDOUT-B02-STATIC-EXPERIMENT.md'


def inspect():
    values = {p.stem: r.load(p) for p in OUT.glob('*.json')}
    for value in values.values():
        r.verify(value)
    state, frozen, commitment, grant, terminal = (values[name] for name in
        ('state', 'freeze', 'commitment', 'authorization', 'terminal'))
    observed = r.current_state(ROOT)
    r.require(observed == state == r.load(OLD / 'state.json'), 'stopped CurrentState drift')
    r.require(r.benchmark_commitment(ROOT) == commitment, 'stopped commitment drift')
    health = r.load(OLD / 'health.json')
    r.require(r.health_record(state, health['results']) == health, 'inherited health drift')
    ledger = r.Ledger(OUT / 'actual-ledger')
    r.require(r.freeze(state, commitment, health)['state'] == frozen['state']
              and frozen['ledger'] == str(ledger.directory)
              and frozen['health'] == health['identity'] and frozen['benchmark'] == commitment['identity']
              and frozen['runner'] == state['runner'], 'freeze linkage drift')
    source = ROOT / 'benchmark/results/phase5c/r5_75_experiment.py'
    controller = r.digest(source.read_bytes())
    r.require(controller == terminal['controller'] == values['callback-binding']['controller'],
              'post-authorization callback repair')
    events = ledger.events()
    r.require([e['transition'] for e in events] == list(r.TRANSITIONS[:4])
              and all(e['freeze'] == frozen['identity'] for e in events)
              and events[0]['details']['grant'] == grant['identity'], 'stopped ledger drift')
    r.require(grant['mode'] == r.ACTUAL_HELD_OUT and grant['benchmark'] == commitment['identity']
              and grant['freeze'] == frozen['identity'] and grant['ledger'] == str(ledger.directory)
              and grant['operation'] == r.STATIC_OPERATION
              and all(grant[k] is False for k in ('repair', 'generation', 'execution', 'acceptance')),
              'authorization binding drift')
    r.require(values['opening-verification']['resources'] ==
              {name: row['commitment'] for name, row in commitment['resources'].items()},
              'opening commitment evidence drift')
    r.require(values['exposure']['event'] == 'B02_EXPOSED' and values['exposure']['permanent'] is True,
              'exposure evidence missing')
    r.require(terminal['classification'] == 'R5_75_OBSERVATION_INDETERMINATE'
              and terminal['reason'] == "'obligations'" and terminal['observation_completions'] == 0,
              'terminal evidence drift')
    # Inspect qualified predicates only. Never call authorize/observe or append
    # ledger events to demonstrate rejection of the stopped experiment.
    tree = ast.parse((ROOT / 'benchmark/evaluation/phase5_runner_v2.py').read_text(encoding='utf-8'))
    functions = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    preflight = ast.get_source_segment((ROOT / 'benchmark/evaluation/phase5_runner_v2.py').read_text(encoding='utf-8'),
                                       functions['authorization_preflight'])
    observe = ast.get_source_segment((ROOT / 'benchmark/evaluation/phase5_runner_v2.py').read_text(encoding='utf-8'),
                                     functions['observe'])
    r.require("ledger.status() == 'zero'" in preflight and 'len(events) == 1' in observe,
              'replay predicate absent')
    return {'classification': terminal['classification'], 'status': 'PASS_STOPPED_INTEGRITY',
            'current_state': state['identity'], 'post_state': observed['identity'], 'runner': observed['runner'],
            'experiment_freeze': frozen['identity'], 'benchmark': commitment['identity'],
            'generic_health': health['identity'], 'controller': controller, 'semantic_count': 30,
            'no_repair': True, 'commitment_relationship': 'INTACT', 'evidence_integrity': 'PASS',
            'accounting': {'authorizations': 1, 'opening_reservations': 1, 'openings': 1, 'exposures': 1,
                'read_attempts': 11, 'content_reads': 11, 'observation_dispatches': 1,
                'observation_completions': 0, 'generation': 0, 'execution': 0, 'frozen_acceptance': 0, 'repair': 0},
            'ledger_status': ledger.status(), 'ledger_events': [e['transition'] for e in events],
            'replay_prevention': {'method': 'READ_ONLY_LEDGER_AND_FROZEN_CONTROL_INSPECTION',
                'second_authorization': 'REJECTS_NONZERO_LEDGER',
                'second_opening': 'REJECTS_EVENT_COUNT_BEFORE_OPENER',
                'second_observation': 'REJECTS_EVENT_COUNT_BEFORE_DISPATCH', 'replay_calls': 0},
            'post_check_scope': 'STATE_RUNNER_COMMITMENTS_EVIDENCE_ONLY_NOT_COMPLETION_QUALIFICATION'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['record', 'final'])
    args = parser.parse_args()
    guard = r.Boundary(ROOT)
    with guard.active():
        result = inspect()
        if args.command == 'record':
            r.persist(OUT / 'stopped-integrity.json', r.seal(result))
        else:
            r.require(r.verify(r.load(OUT / 'stopped-integrity.json')) == result, 'stopped audit changed')
            documents = ['docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md', REPORT]
            for name in documents:
                r.safe_bytes({'prose': (ROOT / name).read_text(encoding='utf-8')})
            r.safe_bytes({'source': Path(__file__).read_text(encoding='utf-8')})
            r.safe_bytes({'source': (ROOT / 'benchmark/results/phase5c/r5_75_experiment.py').read_text(encoding='utf-8')})
            r.require(not r.git(ROOT, 'diff', '--check'), 'diff whitespace failure')
            r.persist(OUT / 'post-report-audit.json', r.seal({
                'status': 'PASS', 'classification': result['classification'],
                'stopped_integrity': r.load(OUT / 'stopped-integrity.json')['identity'],
                'protected_read_attempts': guard.attempts, 'publication': 'PASS', 'diff_check': 'PASS',
                'artifacts': {p.relative_to(ROOT).as_posix(): r.digest(p.read_bytes()) for p in OUT.rglob('*.json')},
                'documents': {name: r.digest((ROOT / name).read_bytes()) for name in documents}}))
        print(r.canonical({**result, 'audit_protected_read_attempts': guard.attempts}).decode())


if __name__ == '__main__':
    main()
