"""Scope/noninterference controls, not new migration acceptance expectations."""
import copy
import unittest
from adapter import install_list_storage_profile
from build import historical_generate, generate
from prepare import ROOT, HERE, load


class AdapterControls(unittest.TestCase):
    def setUp(self):
        self.intent = load(ROOT / 'benchmark/results/phase6/r6_44/submissions/B/final.json')
        source, _ = historical_generate(self.intent)
        self.ns = {'__name__': 'r646_control'}
        exec(compile(source, '<historical-application>', 'exec'), self.ns)
        self.profile = load(HERE / 'profile.json')
        self.state = self.ns['SPEC']['state'][0]

    def outcome(self, decoder, payload, state):
        try:
            return ('ok', decoder(copy.deepcopy(payload), state))
        except self.ns['Failure'] as exc:
            return ('error', exc.code)

    def test_absent_declaration_exact_source_and_decoder(self):
        old, ir = historical_generate(self.intent)
        new, next_ir = generate(self.intent, None)
        self.assertEqual((old, ir), (new, next_ir))
        decoder = self.ns['decode_state']
        install_list_storage_profile(self.ns, None)
        self.assertIs(decoder, self.ns['decode_state'])

    def test_conflicting_version_and_migration_reject_install_without_change(self):
        decoder = self.ns['decode_state']
        for version, migrations in [(2, []), (1, [{'state': self.state['id']}])]:
            with self.subTest(version=version, migrations=migrations):
                self.state['schema_version'] = version
                self.ns['SPEC']['migrations'] = migrations
                with self.assertRaises(ValueError):
                    install_list_storage_profile(self.ns, self.profile)
                self.assertIs(decoder, self.ns['decode_state'])

    def test_declaration_requires_exact_supported_contract(self):
        variants = [dict(self.profile, schema_version=True), dict(self.profile, format='envelope'),
                    dict(self.profile, migrations='allowed'), dict(self.profile, invalid_state_error='other'),
                    dict(self.profile, state='unknown'), dict(self.profile, extra=True)]
        for profile in variants:
            with self.subTest(profile=profile), self.assertRaises(ValueError):
                install_list_storage_profile(self.ns, profile)

    def test_other_states_and_versioned_decoding_differential(self):
        original = self.ns['decode_state']
        install_list_storage_profile(self.ns, self.profile)
        payloads = [{}, [], None, 0, 'store', {'schema_version': 1},
                    {'schema_version': 1, 'records': []}, {'schema_version': 2, 'records': []},
                    {'schema_version': 99, 'records': [dict(phase=None)]}]
        # These are equality controls only, including unresolved V03/V04-like inputs.
        # No migration-enabled success/error outcome is newly declared authoritative.
        for version in (None, 1, 2, 3):
            state = copy.deepcopy(self.state)
            if version is None:
                state.pop('schema_version')
            else:
                state['schema_version'] = version
            for payload in payloads:
                with self.subTest(version=version, payload=payload):
                    self.assertEqual(self.outcome(original, payload, state),
                        self.outcome(self.ns['decode_state'], payload, state))

    def test_only_decoder_origin_code_is_mapped_other_failures_propagate(self):
        for code in ('migration_required', 'persistence_failure', 'invalid_state', 'gate_locked'):
            with self.subTest(code=code):
                def failed(payload, state):
                    raise self.ns['Failure'](code)
                self.ns['decode_state'] = failed
                install_list_storage_profile(self.ns, self.profile)
                result = self.outcome(self.ns['decode_state'], {}, self.state)
                self.assertEqual(result, ('error', 'invalid_state' if code == 'migration_required' else code))
        # handle-level errors are never intercepted by the adapter.
        def outside(*args, **kwargs):
            raise self.ns['Failure']('migration_required')
        self.ns['execute_mutation'] = outside
        self.assertEqual(self.ns['handle']('ignite', {}, {}), {'error': 'migration_required'})

    def test_valid_list_identity_and_single_decoder_call(self):
        calls = []
        original = self.ns['decode_state']
        def counted(payload, state):
            calls.append(payload)
            return original(payload, state)
        self.ns['decode_state'] = counted
        install_list_storage_profile(self.ns, self.profile)
        payload = []
        self.assertIs(self.ns['decode_state'](payload, self.state), payload)
        self.assertEqual(len(calls), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
