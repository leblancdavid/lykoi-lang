import copy
import unittest
from composition import Diagnostic, canonical, diagnose, expand, load, seal, validate, vm
from controls import SERIALIZATION, controls, scalar_program
from examples import examples, explicit_twin, const, ref, definition, step


class CompositionTests(unittest.TestCase):
    def test_adversarial(self):
        for row in controls():
            with self.subTest(row['label']):
                result = diagnose(row['package'], row['node_budget'])
                self.assertEqual(result['status'], 'reject')
                self.assertEqual(result['diagnostic']['code'], row['expected'])

    def test_serialization(self):
        for label, text, code in SERIALIZATION:
            with self.subTest(label), self.assertRaises(Diagnostic) as caught:
                load(text)
            self.assertEqual(caught.exception.data['code'], code)

    def test_reuse_and_nested_expansion(self):
        packages = examples()
        self.assertEqual(packages['pair']['definitions'][0], packages['header_increment']['definitions'][0])
        for package in packages.values():
            a = expand(package)
            b = expand(load(canonical(package).decode()))
            self.assertEqual(a, b)
            self.assertEqual(a['plan'], explicit_twin(package))
            ids = list(a['map'])
            self.assertEqual(len(ids), len(set(ids)))
            self.assertEqual(vm.validate(a['plan']), a['nodes'])

    def test_runtime_signed_and_encode_failures(self):
        for value in (-2**63, -1, 0, 65535, 65536, 2**63 - 1):
            plan = expand(scalar_program(value))['plan']
            observed = vm.execute(plan, b'')
            if 0 <= value <= 65535:
                self.assertEqual(observed['value'], value)
                self.assertIs(type(observed['value']), int)
            else:
                self.assertEqual(observed['error']['code'], 'ENCODE_RANGE')
        p = scalar_program(0)
        p['program']['steps'][0]['node']['expr'] = {'add': [const(2**63 - 1), const(1)]}
        p['program'] = seal(p['program'])
        self.assertEqual(vm.execute(expand(p)['plan'], b'')['error']['code'], 'OVERFLOW')

    def test_bool_unit_expression_types(self):
        p = scalar_program(1)
        d = definition('typed_values', [], {}, [
            step('flag', 'Bool', [], {'op': 'value', 'expr': const(True)}),
            step('unit', 'Unit', [], {'op': 'value', 'expr': const(None)}),
            step('guard', 'Unit', ['flag'], {'op': 'check', 'test': ref('flag'), 'site': ref('flag'), 'code': 'FLAG'}),
            step('result', 'Int64', [], {'op': 'value', 'expr': const(1)})], ref('result'))
        p['program'] = d
        self.assertEqual(vm.execute(expand(p)['plan'], b'')['value'], 1)

    def test_closed_shapes_mutation_sweep(self):
        original = examples()['header_increment']
        mutations = [None, [], {}, True, 0, 'bad']
        count = 0
        # Replace every nonidentity top-level header, definition and step field.
        paths = [(k,) for k in original]
        paths += [('program', k) for k in original['program']]
        paths += [('definitions', 0, k) for k in original['definitions'][0]]
        paths += [('program', 'steps', 0, k) for k in original['program']['steps'][0]]
        for path in paths:
            for value in mutations:
                p = copy.deepcopy(original)
                parent = p
                for key in path[:-1]:
                    parent = parent[key]
                old = parent[path[-1]]
                unchanged = type(old) is type(value) and old == value
                parent[path[-1]] = value
                with self.subTest(path=path, value=value):
                    self.assertEqual(diagnose(p)['status'], 'valid' if unchanged else 'reject')
                count += 1
        self.assertEqual(count, 156)

    def test_nonjson_and_host_cycles(self):
        p = examples()['pair']
        p['program']['result'] = p
        self.assertEqual(diagnose(p)['diagnostic']['code'], 'SHAPE')
        for x in (1.5, b'bytes', object()):
            self.assertEqual(diagnose(x)['diagnostic']['code'], 'SHAPE')

    def test_no_caller_mutation(self):
        p = examples()['pair']
        saved = copy.deepcopy(p)
        a = expand(p)
        a['plan']['decode']['steps'].clear()
        self.assertEqual(p, saved)
        self.assertEqual(expand(p)['plan'], explicit_twin(p))


if __name__ == '__main__':
    unittest.main(verbosity=2)
