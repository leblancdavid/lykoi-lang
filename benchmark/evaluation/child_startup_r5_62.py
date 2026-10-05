"""Isolated startup: validate -> install boundary/exclusion -> import worker."""

from pathlib import Path
import importlib.machinery
import sys
import math
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / 'src')]


def source_code(loader, fullname):
    # -B alone does not prevent stale/substituted .pyc reads. Execute source whose
    # physical identity is bound, rather than trusting a bytecode timestamp.
    return compile(loader.get_data(loader.path), loader.path, 'exec', dont_inherit=True)


importlib.machinery.SourceFileLoader.get_code = source_code
from benchmark.evaluation import mediated_child_r5_62 as mediated
from benchmark.evaluation import restricted_harness_r5_61 as exclusion
from benchmark.evaluation.recorder_r5_43 import canonical, loads


def main():
    import contextlib
    import importlib
    import io
    expected = sys.argv[1]
    status, result = 'REJECTED', {'successful': False, 'reason': 'child rejected; details withheld'}
    denied = []
    worker_started = False
    try:
        value = loads(sys.stdin.buffer.read())
        boundary, definition = mediated.validate(value, expected)
        deadline = float(sys.argv[2])
        if not math.isfinite(deadline) or deadline <= time.monotonic():
            mediated.reject()
        boundary.record = denied.append
        with boundary.stage(value['capabilities']):
            # Pin verified before any selected test/module factory can be invoked.
            policy = exclusion.index()
            permitted = {**value['selection']['runtime'], **definition['implementation']}
            def qualified_source(loader, fullname):
                path = Path(loader.path).resolve()
                if path.is_relative_to(ROOT):
                    name = path.relative_to(ROOT).as_posix()
                    if name not in permitted:
                        mediated.reject()
                    raw = loader.get_data(loader.path)
                    if mediated.digest(raw) != permitted[name]:
                        mediated.reject()
                    return compile(raw, loader.path, 'exec', dont_inherit=True)
                return source_code(loader, fullname)
            importlib.machinery.SourceFileLoader.get_code = qualified_source
            mediated.install_descendants(value, boundary, deadline)
            context = {'selection': value['selection']['inputs'], 'safe_suite': exclusion.suite,
                       'exclusion': policy, 'root': value['root'],
                       'order': ['binding-validation', 'safe-exclusion-installation']}
            if any(sys.modules.get(name) is not None for name in
                   ('benchmark.harness.test_b02_retry_r5_17', 'benchmark.harness.test_b02_retry_r5_19',
                    'benchmark.harness.test_b02_retry_r5_21', 'benchmark.harness.test_b02_integration_r5_23')):
                mediated.reject()
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                worker_started = True
                module = importlib.import_module(definition['module'])
                context['order'].append('worker-discovery')
                result = getattr(module, definition['function'])(context)
            mediated.security.safe_bytes(result)
        status = 'PASS' if result.get('successful') is True else 'FAIL'
    except Exception:
        result = {'successful': False, 'reason': 'child failed; details withheld'}
        status = 'SECURITY_FAILURE' if denied else ('INCOMPLETE' if worker_started else 'REJECTED')
    sys.stdout.buffer.write(canonical({'binding': expected, 'status': status, 'result': result}) + b'\n')


if __name__ == '__main__':
    main()
