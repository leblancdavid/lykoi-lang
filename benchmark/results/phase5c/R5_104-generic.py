"""Publish source-bound generic behavior, then lock implementation before transfer."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from lykoi_workspace.mutable_corpus import captures, plan

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name, filename):
    spec = importlib.util.spec_from_file_location(name, OUT / filename)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    return module


def implementation_pins():
    paths = list((ROOT / 'src').rglob('*.py')) + [ROOT / 'tests/test_mutable_values.py', ROOT / 'docs/typed-mutable-values-v1.md']
    return {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def history_pins():
    paths = [p for p in OUT.iterdir() if p.is_file() and p.name.startswith(('R5_97-', 'R5_101-', 'R5_102-', 'R5_103-'))]
    paths += list((ROOT / 'benchmark/requirements').rglob('*'))
    paths += list((ROOT / 'generated').rglob('*')) + [ROOT / 'air/task_manager.json']
    return {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths) if p.is_file()}


def publish(name, value):
    with (OUT / name).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(value, stream, indent=2); stream.write('\n')


def main():
    verification = json.loads((OUT / 'R5_104-GENERIC-FINAL-VERIFICATION.json').read_text(encoding='utf-8'))
    assert verification['all_pass']
    pins, history = implementation_pins(), history_pins()
    evaluator = load('generic_evaluator', 'R5_103-evaluate.py')
    rows = []
    for record in captures():
        row = evaluator.evaluate(record['candidate'], plan(record)); rows.append(row)
        print(row['case'], row['first_blocker'], row.get('external_invocations', 0), flush=True)
    assert all(r['first_blocker'] == 'SUCCESS' for r in rows)
    assert pins == implementation_pins() and history == history_pins()
    publish('R5_104-SYNTHETIC-EVIDENCE.json', dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), cases=rows,
        external_invocations=sum(r['external_invocations'] for r in rows), limitations=['Same-agent captured interpretations/inventory/literal oracles; synthetic owner approval; no held-out claim']))
    publish('R5_104-GENERIC-LOCK.json', dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), implementation=pins, history=history,
        git_head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        verification_sha256=hashlib.sha256((OUT / 'R5_104-GENERIC-FINAL-VERIFICATION.json').read_bytes()).hexdigest(),
        rule='No implementation edits after this lock or inspection of individual transfer outcomes during R5.104'))


if __name__ == '__main__': main()
