"""Independent optional boundary matrix: no frozen request material."""

import copy
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.semantic import application_boundary_r5_41 as boundary
from benchmark.semantic import boundary_study_r5_39 as seeds
from benchmark.semantic import checked_transport_r5_41 as transport
from benchmark.semantic import checked_launch_r5_36 as launch
from benchmark.semantic import current_pipeline as pipeline
from benchmark.semantic import input_binding_r5_32 as scalar
from benchmark.semantic import optional_support_r5_41 as support
from benchmark.semantic import readiness_r5_41 as readiness
from benchmark.semantic import profile_audit_r5_41 as audit
from benchmark.semantic import state_runtime_r5_41 as codec
from benchmark.semantic import transport_runtime_r5_41 as runtime
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


def setup(base='integer', optional=True, representation='text', domain=None):
    app, _, state, config = seeds.setup()
    shape = {'nullable': base}
    declared = {'optional': shape} if optional else shape
    state_shape = {'record': {'revision': 'integer', 'samples': {'sequence': {'record': {'code': 'string', 'value': declared}}}}}
    # A generic insertion built from the already validated seed-bank constructor.
    operation = copy.deepcopy(app['operations']['v1_create'])
    operation['input'] = {'record': {'code': 'string', 'value': declared}}
    operation['state'] = {'pre': state_shape, 'post': state_shape}
    operation['requires'] = {'literal': {'value': True, 'type': 'boolean'}}
    for branch in operation['branches']:
        branch['value'] = {'record': {field: {'ref': ['input', field]} for field in ('code', 'value')}}
        branch['value_type'] = operation['input']
        # Keep the existing exact insertion relation, replacing only its typed
        # collection/constructor identities.
        branch['transition'] = {'relations': [{'exact_frame': {
            'collection': 'samples', 'identity': 'code', 'record': {'record': {
                field: {'ref': ['input', field]} for field in ('code', 'value')}}}}]}
    app = {'id': 'measurement.optional.boundaries', 'state': {'versions': {'V1': state_shape}},
           'operations': {'store': operation}}
    state = {'version': 'R5.39', 'versions': copy.deepcopy(app['state']['versions']),
             'alternatives': {'V1': {'codec': state_shape, 'constraints': [
                 {'kind': 'equals', 'path': ['revision'], 'value': 1},
                 {'kind': 'population', 'path': ['samples'], 'identity': None, 'nonblank': [],
                  'domains': {'value': domain} if domain is not None else {}}]}},
             'initial': {'empty': {'version': 'V1', 'value': {'revision': 1, 'samples': []}}}}
    plans = pipeline.checked(app)
    spec = transport.specification(plans)
    item = spec['operations'][0]
    next(arg for arg in item['arguments'] if arg['slot'] == 'value')['representation'] = representation
    spec['operations'] = [{'public': 'store', 'alternatives': {'V1': {k: v for k, v in item.items() if k != 'public'}}}]
    spec['persistence'] = {'missing': 'INITIALIZE_DECLARED_STATE', 'initial': 'empty'}
    config = launch.configuration(app['id'], 'measurements.json')
    return app, spec, state, config


def admitted(setup):
    app, spec, state, config = setup
    return boundary.aggregate(app, spec, state, config, {'application': sha(canonical(app)), 'generation': 'static'})


class OptionalSupport(unittest.TestCase):
    def test_scalar_nullable_decoder_is_already_compositional(self):
        for base, raw, value in [('integer', '17', 17), ('string', 'null', 'null'),
                                 ('instant', '2030-01-02T03:04:05Z', '2030-01-02T03:04:05Z')]:
            self.assertEqual(scalar.decode(raw, {'nullable': base}), (True, value))
            self.assertEqual(scalar.decode(None, {'nullable': base}), (True, None))
        for base, raw in [('integer', '17.5'), ('instant', 'yesterday'), ('string', 17)]:
            self.assertEqual(scalar.decode(raw, {'nullable': base}), (False, None))

    def test_independent_readiness_and_audit_supported(self):
        for base in ('integer', 'string', 'instant', 'boolean'):
            current = setup(base, representation='json' if base == 'boolean' else 'text')
            admitted(current)
            self.assertEqual(readiness.inspect(*current)['status'], 'READY')
            self.assertEqual(audit.inspect(current[0], {'transport': current[1], 'state': current[2], 'launch': current[3]})['status'], 'SUPPORTED')
            self.assertEqual(support.capability_findings({'transport': current[1], 'state': current[2]}), [])

    def test_unsupported_compositions(self):
        for shape, representation in [({'nullable': {'record': {'x': 'string'}}}, 'json'),
                                      ({'nullable': 'boolean'}, 'text'), ({'nullable': 'integer'}, 'binary'),
                                      ({'nullable': {'nullable': 'integer'}}, 'json')]:
            self.assertFalse(support.decoder_supported(shape, representation))
        current = setup('boolean', representation='text')
        self.assertEqual(readiness.inspect(*current)['status'], 'NOT_READY')
        self.assertTrue(support.capability_findings({'transport': current[1], 'state': current[2]}))
        self.assertEqual(audit.inspect(current[0], {'transport': current[1], 'state': current[2], 'launch': current[3]})['status'], 'UNSUPPORTED')
        with self.assertRaises(ValueError):
            admitted(current)

    def test_optional_required_durable_matrix(self):
        for optional in (True, False):
            current = setup(optional=optional, domain=[None, 17])
            for row, expected in [({}, optional), ({'value': None}, True), ({'value': 17}, True),
                                  ({'value': 19}, False), ({'value': True}, False), ({'value': '17'}, False)]:
                with self.subTest(optional=optional, row=row):
                    result = codec.decode(canonical({'revision': 1, 'samples': [{'code': 's', **row}]}), current[2])
                    self.assertEqual(result['category'] is None, expected)
            self.assertEqual(readiness.inspect(*current)['status'], 'READY')
            admitted(current)

    def test_null_requires_both_nullable_type_and_domain(self):
        for declaration, domain in [({'optional': 'integer'}, [17]),
                                    ({'optional': {'nullable': 'integer'}}, [17])]:
            self.assertTrue(support.domain_conforms({}, 'value', declaration, domain))
            self.assertFalse(support.domain_conforms({'value': None}, 'value', declaration, domain))
        self.assertFalse(support.domain_supported('integer', [True]))

    def test_public_omission_null_and_text_are_distinct(self):
        current = setup(domain=[None, 17])
        profile = admitted(current)
        route = profile['transport']['operations']['store']['alternatives']['V1']
        route = {**route, 'arguments': {'value': route['arguments']['value']}}
        self.assertEqual(runtime.bind('store', {}, route)['input'], {})
        self.assertEqual(runtime.bind('store', {'value': None}, route)['input'], {'value': None})
        self.assertEqual(runtime.bind('store', runtime.raw_arguments(['--value', '17'], route), route)['input'], {'value': 17})
        self.assertIsNone(runtime.bind('store', runtime.raw_arguments(['--value', 'null'], route), route)['input'])
        for raw in ('17.5', 'bad'):
            self.assertEqual(runtime.bind('store', {'value': raw}, route)['failures'][0]['category'], 'malformed_scalar')
        self.assertEqual(runtime.bind('store', {'value': True}, route)['failures'][0]['category'], 'malformed_scalar')
        required = admitted(setup(optional=False))['transport']['operations']['store']['alternatives']['V1']
        self.assertEqual(runtime.bind('store', {}, required)['failures'][0]['category'], 'missing_required')

    def test_initial_absent_optional_and_present_invalid(self):
        current = setup(domain=[None, 17])
        current[2]['initial']['empty']['value']['samples'] = [{'code': 's'}]
        admitted(current)
        current[2]['initial']['empty']['value']['samples'] = [{'code': 's', 'value': 19}]
        with self.assertRaises(ValueError):
            admitted(current)
        self.assertEqual(readiness.inspect(*current)['status'], 'NOT_READY')

    def test_missing_mapping_wrong_decoder_and_stale_provenance(self):
        for mutation in ('missing', 'decoder', 'provider'):
            current = setup()
            argument = current[1]['operations'][0]['alternatives']['V1']['arguments']
            if mutation == 'missing':
                argument.clear()
            elif mutation == 'decoder':
                next(arg for arg in argument if arg['slot'] == 'value')['decoder'] = 'string'
            else:
                current[3]['provider']['types'] = {'unknown': 'integer'}
            with self.assertRaises(ValueError):
                admitted(current)
            self.assertEqual(readiness.inspect(*current)['status'], 'NOT_READY')
        current = setup()
        report = readiness.inspect(*current, aggregate={})
        self.assertEqual(report['status'], 'NOT_READY')

    def test_generated_public_lifecycle(self):
        for base, text, expected in [('integer', '17', 17), ('string', 'north', 'north'),
                                     ('instant', '2030-01-02T03:04:05Z', '2030-01-02T03:04:05Z')]:
            current = setup(base)
            app, spec, state, config = current
            with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as directory:
                root, cwd = Path(bundle), Path(directory)
                boundary.generate(app, root, spec, state, config)
                for argv, row in [(['store', '--code', 'a'], {'code': 'a'}),
                                  (['store', '--code', 'b', '--value', text], {'code': 'b', 'value': expected})]:
                    event, public, before, after = launch.observe(root, cwd, config, argv)
                    self.assertEqual(public['exit'], 0, public)
                    self.assertIsNotNone(event)
                    self.assertEqual(event['semantic']['input'], row)
                    self.assertTrue(event['transport']['semantic_invoked'])
                    self.assertEqual(event['transport']['binding']['input'], row)
                    self.assertEqual(json.loads(after)['samples'][-1], row)
                self.assertEqual(codec.decode(after, state)['category'], None)

    def test_generated_null_invalid_binding_and_durable_rejection(self):
        current = setup(representation='json', domain=[None, 17])
        app, spec, state, config = current
        with tempfile.TemporaryDirectory() as bundle, tempfile.TemporaryDirectory() as directory:
            root, cwd = Path(bundle), Path(directory)
            boundary.generate(app, root, spec, state, config)
            for index, token in enumerate(('null', '17')):
                event, public, before, after = launch.observe(root, cwd, config,
                    ['store', '--code', str(index), '--value', token])
                self.assertEqual(public['exit'], 0, public)
                self.assertEqual(json.loads(after)['samples'][-1]['value'], None if token == 'null' else 17)
            for token, category, invoked in [('"bad"', 'binding_failure', False), ('19', 'persistence_invalid_state', True)]:
                event, public, before, after = launch.observe(root, cwd, config,
                    ['store', '--code', 'rejected', '--value', token])
                self.assertEqual(public['exit'], 1)
                self.assertEqual(event['transport']['category'], category)
                self.assertEqual(event['transport']['semantic_invoked'], invoked)
                self.assertEqual(before, after)
            (cwd / config['store']['path']).write_bytes(canonical({'revision': 1, 'samples': [{'code': 'x', 'value': 19}]}))
            event, public, before, after = launch.observe(root, cwd, config, ['store', '--code', 'y'])
            self.assertEqual(event['transport']['category'], 'persistence_invalid_state')
            self.assertFalse(event['transport']['semantic_invoked'])
            self.assertEqual(before, after)

    def test_state_alternatives_identity_nonblank_and_domain_not_bypassed(self):
        current = setup(domain=[None, 17])
        app, spec, state, config = current
        app['state']['versions']['V2'] = copy.deepcopy(app['state']['versions']['V1'])
        state['versions'] = copy.deepcopy(app['state']['versions'])
        state['alternatives']['V2'] = copy.deepcopy(state['alternatives']['V1'])
        state['alternatives']['V2']['constraints'][0]['value'] = 2
        spec['operations'][0]['alternatives']['V2'] = copy.deepcopy(spec['operations'][0]['alternatives']['V1'])
        for descriptor in state['alternatives'].values():
            descriptor['constraints'][1]['identity'] = 'code'
            descriptor['constraints'][1]['nonblank'] = ['code']
        admitted(current)
        self.assertEqual(readiness.inspect(*current)['status'], 'READY')
        self.assertEqual(codec.decode(canonical({'revision': 2, 'samples': [{'code': 's'}]}), state)['variant'], 'V2')
        for rows in [[{'code': ' '}], [{'code': 's'}, {'code': 's'}], [{'code': 's', 'value': 19}]]:
            self.assertEqual(codec.decode(canonical({'revision': 1, 'samples': rows}), state)['category'], 'persistence_invalid_state')

    def test_sealed_runtime_support_bytes(self):
        current = setup()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            boundary.generate(current[0], root, *current[1:])
            helper = root / 'optional_support_r5_41.py'
            helper.write_bytes(helper.read_bytes() + b'\n# altered\n')
            with self.assertRaisesRegex(ValueError, 'corrupt'):
                runtime.load(root)

    def test_finite_public_text_domain_failure_and_collection_composition(self):
        current = setup('string')
        argument = next(arg for arg in current[1]['operations'][0]['alternatives']['V1']['arguments'] if arg['slot'] == 'value')
        argument['domain'] = [None, 'north']
        route = admitted(current)['transport']['operations']['store']['alternatives']['V1']
        failure = runtime.bind('store', {'code': 's', 'value': 'south'}, route)
        self.assertEqual(failure['failures'][0]['category'], 'outside_domain')
        self.assertIsNone(failure['input'])
        collection = {'arguments': {'readings': {'slot': 'readings', 'type': {'sequence': {'nullable': 'integer'}},
            'optional': True, 'domain': None, 'representation': 'text', 'mode': 'repeat', 'order': 'encounter'}}}
        raw = runtime.raw_arguments(['--readings', '17', '--readings', '19'], collection)
        self.assertEqual(runtime.bind('read', raw, collection)['input'], {'readings': [17, 19]})
        collection['arguments']['readings'].update({'representation': 'json', 'mode': 'collection'})
        raw = runtime.raw_arguments(['--readings', '[17, null, 19]'], collection)
        self.assertEqual(runtime.bind('read', raw, collection)['input'], {'readings': [17, None, 19]})
        raw = runtime.raw_arguments(['--readings', '[17, "bad"]'], collection)
        self.assertIsNone(runtime.bind('read', raw, collection)['input'])

    def test_unsupported_durable_path_coherence(self):
        current = setup()
        current[2]['alternatives']['V1']['constraints'].append({'kind': 'domain', 'path': ['revision'], 'values': [1]})
        self.assertEqual(readiness.inspect(*current)['status'], 'NOT_READY')
        with self.assertRaises(ValueError):
            admitted(current)
        # A supported rule with incompatible members fails both admission and
        # the shared supplemental capability assessment.
        current = setup(domain=['wrong type'])
        self.assertEqual(readiness.inspect(*current)['status'], 'NOT_READY')
        self.assertEqual(audit.inspect(current[0], {'transport': current[1], 'state': current[2], 'launch': current[3]})['status'], 'UNSUPPORTED')


if __name__ == '__main__':
    unittest.main()
