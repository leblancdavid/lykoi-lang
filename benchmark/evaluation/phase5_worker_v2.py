"""Pinned small worker selections; boundary installed before test imports."""
import ast
from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import runpy
import sys
import tempfile
import unittest

from benchmark.evaluation import phase5_runner_v2 as runner

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = ('test_semantic_operation_contract_prototype',
           'test_semantic_invariants_prototype', 'test_semantic_relationships_prototype',
           'test_semantic_selection_prototype', 'test_semantic_state_relations_prototype',
           'test_refined_plan_r5_28', 'test_current_pipeline_r5_30',
           'test_semantic_authority_r5_31', 'test_input_binding_r5_32',
           'test_state_evolution_r5_33', 'test_checked_transport_r5_34',
           'test_transport_boundary_r5_35', 'test_public_launch_r5_36',
           'test_nullable_coherence_r5_38', 'test_whole_readiness_r5_38',
           'test_boundary_closure_r5_39', 'test_profile_admission_r5_40',
           'test_optional_support_r5_41')


class Prohibited(unittest.TestCase):
    def __init__(self, identity):
        super().__init__('runTest')
        self.identity = identity

    def id(self):
        return self.identity

    @unittest.skip('sealed benchmark: metadata-only pre-import exclusion')
    def runTest(self):
        raise AssertionError('prohibited')


def restricted_suite(root, allowed=()):
    index = runner.metadata(root, 'benchmark/evaluation/prohibited_test_index_r5_61.json')
    runner.require(len(index['tests']) == 36 and all(v == {
        'capabilities': ['B02_ACCEPTANCE'], 'status': 'PROHIBITED'} for v in index['tests'].values()),
        'invalid exclusion index')
    prohibited_modules = {identity.split('.')[0] for identity in index['tests']}
    tests = [Prohibited(identity) for identity in sorted(index['tests'])]
    # Only explicit generic modules are discoverable. No scan/import of protected
    # module trees and no construction of prohibited test objects.
    for module in allowed:
        runner.require(module not in prohibited_modules, 'R5_72_PROTOCOL_HALT')
        tests.append(unittest.defaultTestLoader.loadTestsFromName('benchmark.harness.' + module))
    return unittest.TestSuite(tests)


def run_suite(suite):
    stream = io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=1).run(suite)
    runner.require(result.wasSuccessful(), 'generic tests failed: ' + ', '.join(
        test.id() for test, _ in [*result.failures, *result.errors]))
    return {'tests': result.testsRun, 'passed': result.testsRun - len(result.skipped),
            'skipped': [test.id() for test, _ in result.skipped], 'failures': 0, 'errors': 0}


def generic_checks():
    from benchmark.harness.test_optional_support_r5_41 import setup, admitted
    from benchmark.semantic import application_boundary_r5_41 as boundary
    from benchmark.semantic import readiness_r5_41 as readiness
    from benchmark.semantic import profile_audit_r5_41 as audit
    from benchmark.semantic import state_runtime_r5_41 as codec
    from benchmark.semantic import transport_runtime_r5_41 as transport
    profiles, rows = 0, 0
    values = {'integer': ('17', 17, 'bad', True, 19),
              'string': ('north', 'north', None, 17, 'south'),
              'instant': ('2030-01-02T03:04:05Z', '2030-01-02T03:04:05Z', 'yesterday', 17, '2031-01-02T03:04:05Z'),
              'boolean': ('true', True, 'bad', 17, False)}
    for base, (text, value, invalid, wrong, outside) in values.items():
        for optional in (True, False):
            for representation in ('text', 'json'):
                current = setup(base, optional, representation, [None, value])
                app, spec, state, config = current
                configuration = {'transport': spec, 'state': state, 'launch': config}
                predicted = readiness.inspect(*current)['status'] == 'READY'
                audited = audit.inspect(app, configuration)['status'] == 'SUPPORTED'
                try:
                    profile = admitted(current)
                except ValueError:
                    profile = None
                runner.require(predicted == audited == (profile is not None), 'support incoherence')
                profiles += 1
                if profile is None:
                    continue
                route = profile['transport']['operations']['store']['alternatives']['V1']
                cases = [('omitted', {}, optional), ('null', {'value': None}, True),
                         ('valid', {'value': value if representation == 'json' else text}, True),
                         ('invalid', {'value': invalid}, base == 'string'),
                         ('wrong', {'value': wrong}, False), ('outside', {'value': outside}, True)]
                for label, raw, expected in cases:
                    bound = transport.bind('store', {'code': 'sample', **raw}, route)['input']
                    runner.require((bound is not None) == expected, 'generic binding mismatch')
                    decoded = None if bound is None else codec.decode(runner.canonical({
                        'revision': 1, 'samples': [bound]}), state)
                    valid = decoded is not None and decoded['category'] is None
                    runner.require(valid == (expected and label != 'outside'), 'generic domain mismatch')
                    rows += 1
    current = setup()
    configuration = {'transport': current[1], 'state': current[2], 'launch': current[3]}
    reference = 'benchmark/harness/test_optional_support_r5_41.py'
    pin = runner.digest((ROOT / reference).read_bytes())
    traces = [{'path': path, 'value': value, 'artifact': reference, 'sha256': pin,
               'clause': 'setup', 'interpretation': 'Independent generic measurement profile.'}
              for path, value in audit.leaves(configuration)]
    structure = audit.structure(configuration)
    traceability = audit.traceability(configuration, traces, ROOT, {reference})
    runner.require(structure['valid'] and traceability['valid'] and not audit.contamination(configuration),
                   'schema/traceability/contamination failure')
    forbidden = ('B02', 'B03', 'B17', 'due_date', 'due-date', 'task_manager', 'invalid_due_date')
    implementations = sorted((ROOT / 'benchmark/semantic').glob('*r5_41.py'))
    runner.require(not any(word in path.read_text() for path in implementations for word in forbidden),
                   'support implementation contamination')
    runner.require(boundary.SCHEMA['core_constructs'] == 30 and profiles == 16 and rows == 84, 'semantic/matrix count')
    return {'profiles': profiles, 'rows': rows, 'core_semantics': 30,
            'schema': structure, 'traceability': traceability, 'trace_leaves': len(traces),
            'contamination': 'clean', 'implementation_files': len(implementations)}


def ai_probe():
    # Provider independence is tested on fixed-source validation/lowering/execution.
    # No provider library, endpoint, credential or OpenCode import is used.
    from air_compiler.parser import load
    from air_compiler.validator import validate
    from air_compiler.generator import generate
    from air_compiler.semantics import safety
    import os
    from unittest.mock import patch
    denied = []
    def offline(event, args):
        if event in ('socket.connect', 'socket.connect_ex', 'socket.getaddrinfo'):
            denied.append(event)
            raise runner.Rejected('network inference denied')
    sys.addaudithook(offline)
    forbidden = {'openai', 'anthropic', 'opencode', 'requests', 'httpx'}
    for path in (ROOT / 'src/air_compiler').glob('*.py'):
        for node in ast.walk(ast.parse(path.read_text())):
            names = ([a.name for a in node.names] if isinstance(node, ast.Import) else
                     [node.module or ''] if isinstance(node, ast.ImportFrom) else [])
            runner.require(not any(n.split('.')[0] in forbidden for n in names), 'AI dependency')
    def probe():
        program = validate(load(ROOT / 'air/task_manager.json'))
        target = generate(program)
        invalid = load(ROOT / 'air/task_manager.json')
        invalid.document['axiom_version'] = 'invalid-version'
        rejected = False
        try:
            validate(invalid)
        except ValueError:
            rejected = True
        runner.require(rejected, 'invalid model accepted')
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'application.py'
            path.write_text(target, encoding='utf-8')
            cwd, argv = Path.cwd(), sys.argv
            stream = io.StringIO()
            try:
                os.chdir(directory)
                sys.argv = [str(path), 'list']
                with redirect_stdout(stream):
                    try:
                        runpy.run_path(str(path), run_name='__main__')
                    except SystemExit as exc:
                        runner.require(exc.code in (None, 0), 'readonly application failed')
            finally:
                os.chdir(cwd)
                sys.argv = argv
        return {'lowering': runner.digest(target.encode()), 'safety': runner.digest(runner.canonical(safety(program))),
                'execution': runner.digest(stream.getvalue().encode())}
    state = runner.current_state(ROOT)
    first = probe()
    with patch.dict(os.environ, {'OPENAI_API_KEY': 'synthetic-development-state',
                                'OPENCODE_MODEL': 'different-author', 'OPENAI_BASE_URL': 'http://127.0.0.1:1'}):
        runner.require(probe() == first and runner.current_state(ROOT) == state, 'AI state changes meaning')
    runner.require(not denied and sys.flags.no_site, 'core not isolated')
    return {'offline': True, 'provider_imports': False, 'development_mutation_invariant': True, **first}


def execute(stage):
    boundary = runner.Boundary(ROOT)
    with boundary.active():
        if stage == 'application':
            detail = run_suite(unittest.defaultTestLoader.discover(str(ROOT / 'tests')))
        elif stage == 'support':
            detail = run_suite(restricted_suite(ROOT, SUPPORT))
        elif stage == 'safe-exclusion':
            detail = run_suite(restricted_suite(ROOT, ('test_optional_support_r5_41',)))
            runner.require(len(detail['skipped']) == 36, 'missing prohibited skips')
        elif stage == 'matrix-schema-trace-contamination':
            detail = generic_checks()
        elif stage in ('validate', 'safety'):
            from air_compiler.parser import load
            from air_compiler.validator import validate
            program = validate(load(ROOT / 'air/task_manager.json'))
            if stage == 'safety':
                from air_compiler.semantics import safety
                detail = {'result': safety(program)}
            else:
                detail = {'valid': True}
        elif stage == 'ai-independence':
            detail = ai_probe()
        elif stage == 'runner':
            detail = run_suite(unittest.defaultTestLoader.loadTestsFromName('benchmark.evaluation.test_phase5_runner_v2'))
        else:
            raise runner.Rejected('unknown worker')
    return {'status': 'PASS', 'detail': detail, 'protected_read_attempts': boundary.attempts}


if __name__ == '__main__':
    print(json.dumps(execute(sys.argv[1]), sort_keys=True))
