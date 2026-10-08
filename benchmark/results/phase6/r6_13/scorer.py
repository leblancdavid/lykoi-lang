"""Provider/track-neutral, exact externally observable scorer, r6.13-scorer-1."""
import json
import subprocess
import time

from audit import now

VERSION = 'r6.13-scorer-1'


class DuplicateKey(ValueError):
    pass


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f'Nonfinite JSON: {value}')


def parse(text):
    return json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)


def exact(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def score(stdout, returncode, expected):
    # Invalid expected observations are scorer errors, never candidate failures.
    canonical_expected = exact(expected)
    try:
        actual = parse(stdout)
        canonical_actual = exact(actual)
    except DuplicateKey as exc:
        return dict(status='DUPLICATE_OUTPUT_KEY', actual=None, detail=str(exc), passed=False)
    except (ValueError, TypeError) as exc:
        return dict(status='INVALID_OUTPUT', actual=None, detail=str(exc), passed=False)
    status = ('NONZERO_EXIT' if returncode != 0 else
              'PASS' if canonical_actual == canonical_expected else 'OUTPUT_MISMATCH')
    return dict(status=status, actual=actual, passed=status == 'PASS')


def raw_text(value):
    if isinstance(value, bytes):
        return value.decode('utf-8', errors='replace')
    return value or ''


def execute(command, case, cwd, env, session_deadline, process_seconds=10):
    started = time.monotonic()
    row = dict(start_utc=now(), command=command, input=case['input'],
               expected=case['expected'], stdout='', stderr='', returncode=None,
               scorer_version=VERSION, process_budget_seconds=process_seconds,
               passed=False, scorer_error=None)
    remaining = session_deadline - started
    row['effective_timeout_seconds'] = max(0, min(process_seconds, remaining))
    if remaining <= 0:
        row['status'] = 'NOT_REACHED_SESSION_BUDGET'
    else:
        try:
            proc = subprocess.run(command, input=json.dumps(case['input']).encode('utf-8'),
                                  capture_output=True, cwd=cwd, env=env,
                                  timeout=row['effective_timeout_seconds'])
            row.update(stdout=raw_text(proc.stdout), stderr=raw_text(proc.stderr),
                       returncode=proc.returncode)
            try:
                row.update(score(proc.stdout.decode('utf-8'), proc.returncode, case['expected']))
            except UnicodeDecodeError as exc:
                row.update(status='INVALID_OUTPUT', detail=str(exc), actual=None)
            except Exception as exc:
                row.update(status='SCORER_ERROR', scorer_error=repr(exc))
            if time.monotonic() > session_deadline:
                row.update(status='SESSION_TIMEOUT', passed=False)
        except subprocess.TimeoutExpired as exc:
            row.update(stdout=raw_text(exc.stdout), stderr=raw_text(exc.stderr),
                       status='SESSION_TIMEOUT' if remaining <= process_seconds else 'PROCESS_TIMEOUT')
        except OSError as exc:
            row.update(status='EXECUTION_ERROR', detail=repr(exc))
    row.update(completion_utc=now(), execution_seconds=time.monotonic() - started)
    return row
