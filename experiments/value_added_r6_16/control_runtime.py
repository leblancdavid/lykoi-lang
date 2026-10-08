"""Execute seeded diagnostic mutations separately from scored applications."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from evidence import HERE, OUT, load, now, save
from generate import generate


def main():
    rows = []
    for control in ('operand-type-mismatch', 'unbound-field', 'out-of-domain-write', 'well-typed-wrong-transition'):
        for track in ('B', 'C'):
            row = dict(control=control, track=track)
            try:
                source, _ = generate(load(OUT / f'controls/{control}.json'), track)
            except Exception as e:
                row.update(status='REJECTED_BEFORE_EXECUTION', exception=type(e).__name__, diagnostic=str(e))
                rows.append(row)
                continue
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'application.py'
                path.write_text(source, encoding='utf-8')
                store = Path(tmp) / 'records.json'
                request = dict(op='create', args=dict(label='Control', vent='open', load='ordinary'),
                    providers=dict(uuid_v4='00000000-0000-4000-8000-000000000001', utc_clock='2026-01-01T00:00:00Z'))
                observations = []
                for op in ('create', 'ignite'):
                    request['op'] = op
                    if op == 'ignite':
                        request['args'] = {'id': request['providers']['uuid_v4']}
                    before = store.read_bytes() if store.exists() else None
                    p = subprocess.run([sys.executable, '-B', str(HERE / 'transport.py'), str(path)], cwd=tmp,
                        input=json.dumps(request), capture_output=True, text=True, timeout=30)
                    observed = json.loads(p.stdout) if p.returncode == 0 else None
                    after = store.read_bytes() if store.exists() else None
                    observations.append(dict(op=op, observed=observed, returncode=p.returncode,
                        stderr=p.stderr, storage_bytes_unchanged=before == after))
                row.update(status='EXECUTED', observations=observations)
                if control == 'well-typed-wrong-transition':
                    row['requirement_defect_observed'] = observations[-1]['observed'].get('ok', {}).get('phase') != 'firing'
            rows.append(row)
    save(OUT / 'CONTROL-RUNTIME.json', dict(utc=now(), seeded_only=True, rows=rows,
        scored_repairs=0, note='B rejects invalid domain write at runtime; both miss well-typed wrong target before execution'))
    print('Eight seeded pipeline outcomes recorded')


if __name__ == '__main__':
    main()
