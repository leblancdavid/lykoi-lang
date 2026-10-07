"""Prospective closure checks; exclusive publication preserves prior evidence."""
import importlib.util
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location('checks105', OUT / 'R5_103-verify.py')
checks = importlib.util.module_from_spec(s); s.loader.exec_module(checks)
checks.COMMANDS[:0] = [['-m','unittest','discover','-s','tests','-p',p,'-v'] for p in ('test_input_values.py','test_mutable_values.py')]


def main():
    from concurrent.futures import ThreadPoolExecutor
    import datetime
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(checks.run, checks.COMMANDS))
    result = dict(utc_started=start, utc_finished=datetime.datetime.now(datetime.timezone.utc).isoformat(), commands=rows,
        tests=sum(r['tests'] for r in rows), all_pass=all(r['exit'] == 0 for r in rows), scope='R5.105 current semantic/pipeline/application/external verification')
    label = sys.argv[1] if len(sys.argv) > 1 else 'GENERIC-VERIFICATION'
    assert checks.re.fullmatch(r'[A-Z0-9-]+', label)
    with (OUT / ('R5_105-' + label + '.json')).open('x', encoding='utf-8', newline='\n') as f:
        json.dump(result, f, indent=2); f.write('\n')
    return int(not result['all_pass'])


if __name__ == '__main__': sys.exit(main())
