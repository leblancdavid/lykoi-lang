"""Unscored generic witness; verifies dispatch and independent schema boundaries."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from generate import generate, lower
from schema_check import check


def witness():
    fields = dict(id=dict(type='identifier', domain=[]), created_at=dict(type='timestamp', domain=[]),
                  label=dict(type='string', domain=[]), mode=dict(type='enum', domain=['a', 'b']))
    def operand(kind, v):
        return dict(kind=kind, value=v, type='enum', domain=['a', 'b'])
    guard = dict(op='eq', left=operand('field', 'mode'), right=operand('literal', 'a'))
    return dict(version=1, storage='records.json', fields=fields,
        create=dict(bindings=dict(id=dict(source='uuid_v4', value=None), created_at=dict(source='utc_clock', value=None),
            label=dict(source='input', value=None), mode=dict(source='literal', value='a')), nonblank=['label']),
        operations=dict(advance=dict(guards=[dict(condition=guard, error='invalid_transition')],
                                     writes=dict(mode=dict(source='literal', value='b')))), invariants=[])


class Infrastructure(unittest.TestCase):
    def test_schema_rejects_unknown_and_bool_version(self):
        for key, value in [('unknown', 1), ('version', True)]:
            x = witness()
            x[key] = value
            with self.assertRaises(ValueError):
                check(x)

    def test_deterministic_generators_and_actual_c_dispatch(self):
        for track in ('B', 'C'):
            source, ir = generate(witness(), track)
            self.assertEqual(source, generate(witness(), track)[0])
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'application.py'
                path.write_text(source, encoding='utf-8')
                request = dict(op='create', args={'label': ' retained '}, providers=dict(
                    uuid_v4='00000000-0000-4000-8000-000000000001', utc_clock='2026-01-01T00:00:00Z'))
                for op in ('create', 'advance', 'advance', 'list'):
                    request['op'] = op
                    if op != 'create':
                        request['args'] = {'id': request['providers']['uuid_v4']}
                    p = subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('transport.py')), str(path)],
                        cwd=tmp, input=json.dumps(request), text=True, capture_output=True, timeout=30)
                    self.assertEqual(p.returncode, 0, p.stderr)
                    result = json.loads(p.stdout)
                    if op == 'advance' and result.get('error'):
                        self.assertEqual(result, {'error': 'invalid_transition'})
                    else:
                        self.assertIn('ok', result)
            if track == 'C':
                self.assertEqual(ir['version'], 'typed-mutable-values-1')

    def test_semantic_type_mismatch_is_not_schema_check(self):
        x = witness()
        x['operations']['advance']['guards'][0]['condition']['left']['type'] = 'string'
        x['operations']['advance']['guards'][0]['condition']['left']['domain'] = []
        check(x)
        generate(x, 'B')
        with self.assertRaises(Exception):
            lower(x)


if __name__ == '__main__':
    unittest.main()
