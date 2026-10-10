"""Direct existing-runtime controls, avoiding unrelated full workflow evaluation."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from adapter import install_list_storage_profile
from air_compiler.mutable_values import compose
from air_compiler.references import compose as references
from air_compiler.atomic_state import compose as atomic
from air_compiler.authorization import compose as authorization
from air_compiler.profiles import generate_mutable
from lykoi_pipeline import mutable_profile
from lykoi_workspace.authorization_corpus import captures


class RuntimeControls(unittest.TestCase):
    def test_versioned_authorization_runtime_and_exact_no_profile_source(self):
        r = captures()[1]
        base = mutable_profile.scalar.lower({**r['scalar'], 'storage': {**r['scalar']['storage'], 'version': 1}})
        ir = compose(base, {k: v for k, v in r['mutable'].items()
                           if k not in ('atomic_state_semantics', 'authorization_semantics')})
        ri = references(ir, r['references'])
        ai = atomic(ir, ri, r['mutable']['atomic_state_semantics'])
        au = authorization(ir, ri, r['mutable']['authorization_semantics'])
        source = generate_mutable(ir, [], ri, ai, au)
        ns = {'__name__': 'r646_versioned_runtime'}
        exec(compile(source, '<production-versioned-runtime>', 'exec'), ns)
        decoder = ns['decode_state']
        install_list_storage_profile(ns, None)
        self.assertIs(decoder, ns['decode_state'])
        self.assertEqual(source, generate_mutable(ir, [], ri, ai, au))
        op = next(o for o in ns['REFERENCE']['facts']['operations'] if o['command'] == 'trusted-adjust')
        initial = dict(schema_version=2, records=[r['record']], entities=r['entities'])
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / r['path']
            storage = next(c for c in ns['SPEC']['capabilities'] if c['kind'] == 'json_file')
            storage['path'] = str(path)
            for mode, error in [('forge', 'invalid_actor'), ('source', 'invalid_actor'),
                                ('wrong_role', 'permission_denied'), ('owner', 'permission_denied'),
                                ('persist', 'persistence_failure'), ('success', None)]:
                with self.subTest(mode=mode):
                    path.write_text(json.dumps(initial, indent=1) + '\n', encoding='utf-8')
                    before = path.read_bytes()
                    inputs = dict(id='a', adjustment=1, record='h', successor='b', successor_history='sh')
                    context = dict(source='controlled_host', actor='operator')
                    if mode == 'forge': inputs['actor'] = 'other'
                    if mode == 'source': context['source'] = 'cli'
                    if mode == 'wrong_role': context['actor'] = 'viewer'
                    if mode == 'owner': context['actor'] = 'other'
                    original_replace = ns['os'].replace
                    if mode == 'persist':
                        def fail(*args): raise OSError('injected replacement failure')
                        ns['os'].replace = fail
                    try:
                        if error:
                            with self.assertRaises(ns['Failure']) as caught:
                                ns['reference_operation'](op, inputs, execution_context=context)
                            self.assertEqual(caught.exception.code, error)
                            self.assertEqual(path.read_bytes(), before)
                        else:
                            result = ns['reference_operation'](op, inputs, execution_context=context)
                            self.assertEqual(result['quantity'], 11)
                            persisted = json.loads(path.read_bytes())
                            self.assertEqual(len(persisted['records']), 2)
                            self.assertEqual(len(persisted['entities'][r['history']]), 2)
                    finally:
                        ns['os'].replace = original_replace


if __name__ == '__main__':
    unittest.main(verbosity=2)
