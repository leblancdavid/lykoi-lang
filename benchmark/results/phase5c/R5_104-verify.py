"""Current semantic checks with separately versioned R5.104 evidence."""
import importlib.util
import json
from pathlib import Path
import sys

OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('current_checks', OUT / 'R5_103-verify.py')
checks = importlib.util.module_from_spec(spec); spec.loader.exec_module(checks)
checks.COMMANDS.insert(0, ['-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_mutable_values.py', '-v'])


def main():
    from concurrent.futures import ThreadPoolExecutor
    import datetime
    start = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with ThreadPoolExecutor(max_workers=2) as pool:
        rows = list(pool.map(checks.run, checks.COMMANDS))
    result = dict(utc_started=start, utc_finished=datetime.datetime.now(datetime.timezone.utc).isoformat(), commands=rows,
        tests=sum(r['tests'] for r in rows), all_pass=all(r['exit'] == 0 for r in rows), scope='R5.104 current semantic/pipeline/application/external checks; no infrastructure qualification')
    label = sys.argv[1] if len(sys.argv) > 1 else 'GENERIC-VERIFICATION'
    assert checks.re.fullmatch(r'[A-Z0-9-]+', label)
    with (OUT / ('R5_104-' + label + '.json')).open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2); stream.write('\n')
    return int(not result['all_pass'])


if __name__ == '__main__': sys.exit(main())
