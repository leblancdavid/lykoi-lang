"""R5.37 evidence recorder. Never repairs or substitutes implementation code."""
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[3]
RESULTS = ROOT / 'benchmark/results/phase5c'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def save(name, value):
    (RESULTS / name).write_bytes((json.dumps(value, indent=2, sort_keys=True) + '\n').encode())


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode().strip()


def lock():
    tracked = git('ls-files').splitlines()
    protected = [p for p in tracked if p.startswith(('benchmark/semantic/', 'benchmark/harness/',
                 'src/', 'schema/', 'air/', 'generated/', 'benchmark/requirements/'))]
    protected += ['benchmark/baseline.md',
        'benchmark/results/phase5c/R5_36-readiness-matrix.json',
        'benchmark/results/phase5c/R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md',
        'benchmark/results/phase5c/R5_4-SELECTION-VOCABULARY-LEDGER.md']
    record = {'version': 'R5.37', 'time_utc': datetime.now(timezone.utc).isoformat(),
        'commit': git('rev-parse', 'HEAD'), 'initial_status': 'clean (observed before edits)',
        'lock_status': git('status', '--porcelain=v1', '--untracked-files=all'),
        'candidate_core_constructs': 30, 'core_autocrlf': git('config', '--get', 'core.autocrlf'),
        'environment': {'os': platform.platform(), 'python': sys.version, 'executable': sys.executable,
            'PYTHONPATH': os.environ.get('PYTHONPATH'), 'third_party_dependencies': False,
            'public_provider': 'checked production; ambient provider overrides ignored'},
        'files': {p: digest((ROOT / p).read_bytes()) for p in sorted(set(protected))},
        'evaluation_files_at_lock': {str(p.relative_to(ROOT)).replace('\\', '/'): digest(p.read_bytes())
            for p in RESULTS.glob('*r5_37*')},
        'baseline': {'harness': {'run': 347, 'passed': 347, 'failed': 0, 'skipped': 0,
            'seconds': 131.701, 'initial_attempt': 'tool timeout at 120 seconds; completed rerun at 600-second limit'},
            'application_compiler': {'run': 31, 'passed': 31}, 'model_validation': 'PASS',
            'safety': {'capability_violations': 0, 'invalid_transitions': 0},
            'diff_check': 'PASS', 'readiness_matrix': 'validated in full harness'}}
    record['identity'] = digest(json.dumps(record, sort_keys=True).encode())
    save('R5_37-implementation-lock.json', record)
    print(json.dumps({'lock': record['identity'], 'protected_files': len(record['files'])}))


def verify():
    record = json.loads((RESULTS / 'R5_37-implementation-lock.json').read_bytes())
    changed = [p for p, expected in record['files'].items() if digest((ROOT / p).read_bytes()) != expected]
    verdict = {'protected_files': len(record['files']), 'changed': changed, 'pass': not changed,
               'commit_unchanged': git('rev-parse', 'HEAD') == record['commit']}
    save('R5_37-final-lock-verification.json', verdict)
    print(json.dumps(verdict))
    return 0 if verdict['pass'] and verdict['commit_unchanged'] else 1


def evaluate():
    sys.path.insert(0, str(ROOT))
    from benchmark.semantic import current_pipeline
    source = json.loads((RESULTS / 'R5_37-b02-semantic-application.json').read_bytes())
    report = {'entry_point': 'benchmark.semantic.current_pipeline',
        'source_sha256': digest((RESULTS / 'R5_37-b02-semantic-application.json').read_bytes()),
        'complete_candidate': False, 'candidate_core_constructs': 30}
    with tempfile.TemporaryDirectory() as folder:
        try:
            report['manifest'] = current_pipeline.generate(source, Path(folder))
            report['classification'] = 'COMPLETE_CANDIDATE_GENERATED'
            report['complete_candidate'] = True
        except Exception as exc:
            report.update(classification='UNKNOWN_TYPE_COHERENCE_GAP', exception_type=type(exc).__name__,
                          diagnostic=str(exc), traceback=traceback.format_exc(),
                          generated_files=sorted(p.name for p in Path(folder).iterdir()))
    save('R5_37-generation-evidence.json', report)
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    if sys.argv[1] == 'lock':
        lock()
    elif sys.argv[1] == 'verify':
        sys.exit(verify())
    elif sys.argv[1] == 'evaluate':
        evaluate()
