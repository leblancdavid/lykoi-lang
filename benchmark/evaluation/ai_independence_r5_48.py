"""Subprocess-only core probes: absent providers, no site/OpenCode, denied network.

No actual credentials are read. Audit hooks are defense-in-depth observations,
not a native-code sandbox. Semantic output is compared independently of authors.
"""

import ast
from contextlib import redirect_stdout
import io
from pathlib import Path
import runpy
import sys
import tempfile


def probe(root):
    root = Path(root).resolve()
    sys.path.insert(0, str(root / 'src'))
    denied = []
    def audit(event, args):
        if event in {'socket.connect', 'socket.connect_ex', 'socket.getaddrinfo',
                     'socket.bind', 'subprocess.Popen', 'os.system'}:
            denied.append(event)
            raise RuntimeError('external request/process prohibited during core probe')
    sys.addaudithook(audit)
    from air_compiler.parser import load
    from air_compiler.validator import validate
    from air_compiler.generator import generate
    from air_compiler.semantics import safety
    from benchmark.evaluation.recorder_r5_43 import canonical, digest

    source = root / 'air/task_manager.json'
    program = validate(load(source))
    target = generate(program)
    # Test independently determined invalidity, not only a valid happy path.
    invalid = load(source)
    invalid.document['axiom_version'] = 'not-a-language-version'
    rejected = False
    try:
        validate(invalid)
    except ValueError:
        rejected = True
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'application.py'
        path.write_text(target, encoding='utf-8')
        import os
        previous, argv = Path.cwd(), sys.argv
        os.chdir(directory)
        stream = io.StringIO()
        try:
            sys.argv = [str(path), 'list']
            with redirect_stdout(stream):
                try:
                    runpy.run_path(str(path), run_name='__main__')
                except SystemExit as exc:
                    if exc.code not in (None, 0):
                        raise
        finally:
            os.chdir(previous)
            sys.argv = argv
    return {'successful': rejected and not denied, 'validation': 'valid',
            'invalid_rejected': rejected, 'lowering_sha256': digest(target.encode()),
            'safety_sha256': digest(canonical(safety(program))),
            'execution_stdout_sha256': digest(stream.getvalue().encode()),
            'denied_events': denied, 'site_enabled': not bool(sys.flags.no_site)}


def imports(root):
    """Static direct imports, supplementing the dynamic network-denial probe."""
    result = {}
    for path in sorted((Path(root) / 'src/air_compiler').glob('*.py')):
        nodes = ast.walk(ast.parse(path.read_text(encoding='utf-8')))
        names = set()
        for node in nodes:
            if isinstance(node, ast.Import):
                names.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                names.add('.' * node.level + (node.module or ''))
        result[path.name] = sorted(names)
    return result
