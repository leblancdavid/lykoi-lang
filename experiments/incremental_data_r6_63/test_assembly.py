"""Adversarial state/serialization controls for the experiment-local boundary."""
import copy
import unittest
from freeze import OUT, c, read, pin
from assembly import apply


class AssemblyControls(unittest.TestCase):
    def setUp(self):
        self.before=read(OUT/'episodes/D04/BEFORE.json')
        self.action=read(OUT/'episodes/D04/ACTION.json')

    def repin(self):
        self.before['identity']=pin({k:v for k,v in self.before.items() if k!='identity'})

    def rejects(self,code):
        original=copy.deepcopy(self.before)
        with self.assertRaises(c.Diagnostic) as caught:
            apply(self.before,self.action)
        self.assertEqual(caught.exception.data['code'],code)
        self.assertEqual(self.before,original)

    def test_rehashed_invalid_prefix_is_not_trusted(self):
        self.before['steps'][0]['deps']=['base']
        self.repin()
        self.rejects('DEPENDENCY')

    def test_rehashed_prefix_order_is_not_trusted(self):
        self.before['order'].reverse()
        self.repin()
        self.rejects('ORDER')

    def test_selected_identifier_cannot_capture_prefix(self):
        self.before['steps'][0]['id']='selected'
        self.before['order'][0]='selected'
        self.action['node']['expr']['add'][0]={'ref':'selected'}
        self.action['deps']=['adjustment','selected']
        self.repin()
        self.rejects('CAPTURE')

    def test_experiment_bounds(self):
        self.before['params'] += [dict(name='extra1',type='Int64'),dict(name='extra2',type='Int64')]
        self.repin()
        self.rejects('RESOURCE')

    def test_native_strict_serialization(self):
        for text in ('{"type":"Int64","type":"Bool"}','{"const":1.0}'):
            with self.assertRaises(c.Diagnostic) as caught:
                c.load(text)
            self.assertEqual(caught.exception.data['code'],'SERIALIZATION')


if __name__=='__main__':
    unittest.main()
