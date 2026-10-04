"""Independent non-task admission and research-integrity challenges."""

import copy
import unittest

from benchmark.semantic import application_boundary_r5_39 as historical
from benchmark.semantic import application_boundary_r5_40 as admission
from benchmark.semantic import boundary_study_r5_39 as seeds
from benchmark.semantic import nullable_study_r5_38 as publications
from benchmark.semantic import profile_audit_r5_40 as audit
from benchmark.semantic import readiness_r5_39 as readiness
from benchmark.semantic.refined_generator_r5_28 import canonical, sha


def minimal(optional=True):
    app, spec, state, config = seeds.setup()
    # One read-only operation, one state alternative, one optional integer input.
    app['operations'] = {'v1_query': app['operations']['v1_query']}
    app['state']['versions'] = {'V1': app['state']['versions']['V1']}
    state['versions'] = copy.deepcopy(app['state']['versions'])
    state['alternatives'] = {'V1': state['alternatives']['V1']}
    spec['operations'] = [spec['operations'][1]]
    del spec['operations'][0]['alternatives']['V2']
    if not optional:
        app['operations']['v1_query']['input']['record']['filter'] = {'nullable': 'integer'}
        app['operations']['v1_query']['branches'][0]['value_type']['record']['filter'] = {'nullable': 'integer'}
        app['operations']['v1_query']['branches'][1]['value_type']['record']['filter'] = {'nullable': 'integer'}
        spec['operations'][0]['alternatives']['V1']['arguments'][0]['omission'] = 'required'
        for descriptor in spec['operations'][0]['alternatives']['V1']['outcomes'].values():
            descriptor['type']['record']['filter'] = {'nullable': 'integer'}
    return app, spec, state, config


def admit(setup, module=admission):
    app, spec, state, config = setup
    return module.aggregate(app, spec, state, config,
        {'application': sha(canonical(app)), 'generation': 'static-readiness-v2'})


class Admission(unittest.TestCase):
    def test_historical_minimal_defect_and_readiness_disagreement(self):
        setup = minimal()
        setup[1]['operations'][0]['alternatives']['V1']['arguments'] = []
        self.assertIsInstance(admit(setup, historical), dict)
        result = readiness.inspect(*setup)
        self.assertEqual(result['status'], 'NOT_READY')
        self.assertTrue(any(g['stage'] == 'binding' for g in result['gaps']))
        with self.assertRaisesRegex(ValueError, 'optional'):
            admit(setup)

    def test_complete_required_and_optional(self):
        for optional in (False, True):
            with self.subTest(optional=optional):
                setup = minimal(optional)
                admit(setup)
                self.assertEqual(readiness.inspect(*setup)['status'], 'READY')

    def test_required_and_optional_missing(self):
        for optional in (False, True):
            setup = minimal(optional)
            setup[1]['operations'][0]['alternatives']['V1']['arguments'] = []
            with self.assertRaises(ValueError):
                admit(setup)
            self.assertEqual(readiness.inspect(*setup)['status'], 'NOT_READY')

    def test_multiple_independent_profiles(self):
        for factory in (seeds.setup, publications.setup):
            setup = factory()
            admit(setup)
            routes = setup[1]['operations']
            item = next(item for route in routes for item in route.get('alternatives', {'state': route}).values()
                        if any(arg['omission'] == 'omit' for arg in item['arguments']))
            item['arguments'] = [arg for arg in item['arguments'] if arg['omission'] != 'omit']
            with self.assertRaises(ValueError):
                admit(setup)
            self.assertEqual(readiness.inspect(*setup)['status'], 'NOT_READY')

    def test_wrong_slot_duplicate_public_and_incompatible_decoder(self):
        for mutation in ('wrong_slot', 'duplicate_public', 'decoder', 'omission'):
            setup = minimal()
            item = setup[1]['operations'][0]['alternatives']['V1']
            if mutation == 'wrong_slot':
                item['arguments'][0]['slot'] = 'absent'
            elif mutation == 'duplicate_public':
                item['arguments'].append(copy.deepcopy(item['arguments'][0]))
            elif mutation == 'decoder':
                item['arguments'][0]['decoder'] = 'string'
            else:
                item['arguments'][0]['omission'] = 'required'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                admit(setup)

    def test_stale_binding_and_transport_identity(self):
        setup = minimal()
        profile = admit(setup)
        for field in ('binding', 'transport'):
            faulty = copy.deepcopy(profile)
            faulty[field] = {}
            with self.assertRaises(ValueError):
                admission.check_aggregate(*setup, profile['artifact'], faulty)

    def test_internal_capabilities_not_public_inputs(self):
        setup = seeds.setup()
        # Capabilities are separate CheckedPlan facts; no public mapping is required.
        profile = admit(setup)
        self.assertEqual(profile['provider']['requirements'], {})
        setup = publications.setup()
        admit(setup)
        # Explicit internal invocation inputs are not supported by this schema.
        setup = minimal()
        setup[1]['operations'][0]['alternatives']['V1']['internal'] = ['filter']
        with self.assertRaises(ValueError):
            admit(setup)

    def test_equal_codec_distinct_state_discriminators_are_configuration(self):
        setup = minimal()
        app, spec, state, config = setup
        app['state']['versions']['V2'] = copy.deepcopy(app['state']['versions']['V1'])
        state['versions'] = copy.deepcopy(app['state']['versions'])
        state['alternatives']['V2'] = copy.deepcopy(state['alternatives']['V1'])
        state['alternatives']['V2']['constraints'][0]['value'] = 2
        spec['operations'][0]['alternatives']['V2'] = copy.deepcopy(spec['operations'][0]['alternatives']['V1'])
        admit(setup)
        self.assertEqual(readiness.inspect(*setup)['status'], 'READY')


class ConfigurationAudit(unittest.TestCase):
    def test_plain_text_nullable_and_scalar_discriminator_domain_limitations(self):
        setup = minimal()
        setup[1]['operations'][0]['alternatives']['V1']['arguments'][0]['representation'] = 'text'
        with self.assertRaisesRegex(ValueError, 'incompatible checked binding'):
            admit(setup)
        findings = audit.capability_findings({'transport': setup[1], 'state': setup[2], 'launch': setup[3]})
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]['classification'], 'MISSING_GENERIC_CAPABILITY')
        app, spec, state, config = minimal()
        state['alternatives']['V1']['constraints'].append(
            {'kind': 'domain', 'path': ['revision'], 'values': [1, 2]})
        with self.assertRaisesRegex(ValueError, 'unsupported state constraint'):
            historical.check_state(app, state)

    def test_independent_optional_population_domain_limitation(self):
        from benchmark.semantic import state_runtime_r5_39 as codec
        app, spec, state, config = minimal()
        shape = app['state']['versions']['V1']['record']['seeds']['sequence']['record']
        shape['habitat'] = {'optional': 'string'}
        state['versions'] = copy.deepcopy(app['state']['versions'])
        state['alternatives']['V1']['codec'] = copy.deepcopy(state['versions']['V1'])
        state['alternatives']['V1']['constraints'][1]['domains']['habitat'] = ['dry', 'wet']
        historical.check_state(app, state)
        # The schema admits a domain on an optional field, but decoding an absent
        # field rejects a structurally valid older row. This is preserved evidence.
        self.assertEqual(codec.decode(canonical({'revision': 1, 'seeds': [
            {'code': 'iris', 'label': 'Iris'}]}), state)['category'], 'persistence_invalid_state')
        findings = audit.capability_findings({'transport': spec, 'state': state, 'launch': config})
        self.assertEqual(findings[0]['stage'], 'state')

    def test_behavioral_fields_and_fixture_provider_reject(self):
        app, spec, state, config = minimal()
        for key in audit.FORBIDDEN:
            data = {'transport': {**spec, key: 'arbitrary'}, 'state': state, 'launch': config}
            self.assertTrue(audit.contamination(data))
        config['provider'] = {'mode': 'controlled_test', 'types': {}, 'values': {'x': 12}}
        self.assertTrue(audit.contamination({'transport': spec, 'state': state, 'launch': config}))

    def test_unknown_configuration_field_schema_rejects(self):
        setup = minimal()
        setup[1]['operations'][0]['alternatives']['V1']['fixture_output'] = 3
        with self.assertRaises(ValueError):
            admit(setup)
        with self.assertRaises(ValueError):
            audit.structure({'transport': setup[1], 'state': setup[2], 'launch': setup[3]})

    def test_traceability_missing_duplicate_stale_and_non_authority(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[2]
        artifact = 'benchmark/semantic/profile_audit_r5_40.py'
        record = {'path': ['x'], 'value': 1, 'artifact': artifact,
                  'sha256': sha((root / artifact).read_bytes()), 'clause': 'SCHEMA', 'interpretation': 'test reference'}
        self.assertTrue(audit.traceability({'x': 1}, [record], root, {artifact})['valid'])
        stale = {**record, 'sha256': 'wrong'}
        wrong_source = {**record, 'artifact': 'benchmark/conventional/task_manager.py'}
        wrong_value = {**record, 'value': 2}
        for records in ([], [record, record], [stale], [wrong_source], [wrong_value]):
            with self.assertRaises(ValueError):
                audit.traceability({'x': 1}, records, root, {artifact})

    def test_fixture_output_constant_is_not_configuration(self):
        app, spec, state, config = minimal()
        spec['failures']['binding_failure']['presentation'] = {'mode': 'object', 'coverage': 'selected',
            'fields': [{'name': 'result', 'source': 'constant', 'type': 'integer', 'value': 7}]}
        self.assertTrue(audit.contamination({'transport': spec, 'state': state, 'launch': config}))


if __name__ == '__main__':
    unittest.main()
