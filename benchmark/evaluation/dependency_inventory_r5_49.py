"""Fresh non-B02 core/deployment observations, with explicit closure limits."""

import importlib
import os
from pathlib import Path
import sys
import tempfile

from benchmark.evaluation import dependency_provenance_r5_49 as provenance
from benchmark.evaluation import ai_independence_r5_48 as independence


def observe(root):
    root = Path(root).resolve()
    paths = [p.relative_to(root).as_posix() for directory in ('src', 'benchmark', 'generated')
             for p in (root / directory).rglob('*.py') if '__pycache__' not in p.parts]
    resolver = provenance.Resolver(provenance.members(root, paths), installed={})
    core_result = independence.probe(root)
    rows, native = [], []
    # The command driver has no module spec; its source is bound by stage identity.
    for name, module in sorted(sys.modules.items()):
        if name == '__main__' or module is None:
            continue
        row = resolver.module(module)
        rows.append({'name': name, **row})
        if row.get('implementation') == 'native-extension':
            path = module.__spec__.origin
            native.append({'name': name, 'sha256': provenance.digest(Path(path).read_bytes()),
                           'imports': provenance.pe_imports(path) if os.name == 'nt' else
                           {'complete': False, 'unresolved': ['non-PE loader inspection unimplemented']}})
    if os.name == 'nt':
        native.append({'name': 'python-executable', **provenance.external(sys.executable),
                       'imports': provenance.pe_imports(sys.executable)})
    return {'successful': core_result['successful'] and not any(r['category'] == 'UNKNOWN' for r in rows),
            'core': core_result, 'resolved_modules': rows, 'native_images': native,
            'graph': {'root': 'validate/lower/read-only core probe',
                      'observed_reachable_modules': [r['name'] for r in rows],
                      'edge_authority': 'process observation, not exhaustive import edges',
                      'complete': False},
            'closure_complete': False,
            'gaps': ['native loader descendants not transitively resolved or owned',
                     'late imports/bytecode and all execution branches not closed',
                     'Git/configuration/context and filesystem ownership not qualified']}


def deployment(root):
    """Generate an independent acoustic fixture; import actual copied helpers.

    Run in a separate worker: the core probe's subprocess-denying audit hook is
    permanent and the deployment intentionally has a different material slice.
    """
    root = Path(root).resolve()
    from benchmark.harness.test_optional_support_r5_41 import setup
    from benchmark.semantic import application_boundary_r5_41 as boundary
    app, spec, state, config = setup()
    source_paths = [p.relative_to(root).as_posix() for p in (root / 'benchmark/semantic').glob('*.py')]
    bound = provenance.members(root, source_paths)
    with tempfile.TemporaryDirectory() as directory:
        target = Path(directory)
        boundary.generate(app, target, spec, state, config)
        # Generic content mapping: no helper-name exceptions or alias table.
        copies = {}
        for path in target.glob('*.py'):
            matching = [p for p, row in bound.items() if row['sha256'] == provenance.digest(path.read_bytes())]
            if matching:
                copies[path.resolve()] = sorted(matching)[0]
        resolver = provenance.Resolver(bound, installed={}, copies=copies)
        sys.path.insert(0, str(target))
        rows = []
        for path in sorted(copies):
            module = importlib.import_module(path.stem)
            rows.append({'name': path.stem, **resolver.module(module)})
        return {'successful': bool(rows) and all(r['category'] == 'REPOSITORY_OWNED' for r in rows),
                'application': app['id'], 'resolved_deployment_helpers': rows,
                'mapping': 'copied artifact bytes verified against qualified source members',
                'complete_execution_closure': False}
