"""Verify public normal-path behavior, preserve history and lock before transfer."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess

from lykoi_workspace.input_corpus import captures, plan

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]


def load(name, filename):
    s = importlib.util.spec_from_file_location(name, OUT / filename)
    m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
    return m


def implementation_pins():
    paths = list((ROOT / 'src').rglob('*.py')) + list((ROOT / 'tests').glob('test_*.py')) + [ROOT / 'docs/typed-input-values-v1.md', ROOT / 'docs/typed-mutable-values-v1.md']
    return {str(p.relative_to(ROOT)).replace('\\','/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(paths)}


def history_pins():
    old = load('history104', 'R5_104-generic.py')
    pins = old.history_pins()
    pins.update({str(p.relative_to(ROOT)).replace('\\','/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob('R5_104-*') if p.is_file()})
    return pins


def publish(name, value):
    with (OUT / name).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(value, f, indent=2); f.write('\n')


def main():
    v = OUT / 'R5_105-GENERIC-FINAL-VERIFICATION.json'
    assert json.loads(v.read_text(encoding='utf-8'))['all_pass']
    pins, history = implementation_pins(), history_pins()
    ev = load('generic105_evaluator', 'R5_103-evaluate.py')
    rows = []
    for r in captures():
        row = ev.evaluate(r['candidate'], plan(r)); rows.append(row)
        print(row['case'],row['first_blocker'],row.get('external_invocations',0),flush=True)
    assert all(r['first_blocker'] == 'SUCCESS' for r in rows)
    assert pins == implementation_pins() and history == history_pins()
    publish('R5_105-SYNTHETIC-FINAL-EVIDENCE.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),cases=rows,
        external_invocations=sum(r['external_invocations'] for r in rows),limitations=['Same-agent source/inventory/oracles; synthetic approval; exposed development only']))
    publish('R5_105-GENERIC-LOCK-2.json',dict(utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),implementation=pins,history=history,
        git_head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),verification_sha256=hashlib.sha256(v.read_bytes()).hexdigest(),
        rule='Implementation/spec/tests immutable through R5.105 transfer; no outcome-driven repairs'))


if __name__ == '__main__': main()
