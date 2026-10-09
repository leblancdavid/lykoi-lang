import copy
import tempfile
import unittest
from pathlib import Path
from common import ROOT, Registry, c, load, digest
from snapshot import generate, verify, retrieve


class SnapshotTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.registry=Registry(Path(self.temp.name)/'registry')
        # Historical saved artifacts are unscored infrastructure fixtures only.
        ds=[load(ROOT/'benchmark/results/phase6/r6_37'/f'{key}.json') for key in ('old','a','b')]
        self.registry.admit(ds,None)
        self.bindings={'CallerA':ds[1]['identity'],'CallerB':ds[2]['identity']}
        self.args=('requirement-hash','explicit objective',self.bindings,'verbatim constraints')
        self.snapshot=generate(self.registry,*self.args)

    def test_deterministic_complete_closure(self):
        self.assertEqual(self.snapshot,generate(self.registry,*self.args))
        self.assertTrue(verify(self.snapshot,self.registry,*self.args))
        self.assertEqual(len(self.snapshot['definitions']),3)
        for pin,d in self.snapshot['definitions'].items():
            self.assertEqual(d,next(x for x in retrieve(self.registry,pin,'definition') if x['identity']==pin))
            for kind in ('dependencies','validation','history','identity'):
                self.assertTrue(retrieve(self.registry,pin,kind))

    def test_tamper_and_resealed_omission(self):
        for field in ('definitions','dependencies','caller_bindings','constraints','validation','retrieval_references'):
            bad=copy.deepcopy(self.snapshot); bad[field]={}
            with self.assertRaises(c.Diagnostic): verify(bad,self.registry,*self.args)
            bad['identity']=digest({k:v for k,v in bad.items() if k!='identity'})
            with self.assertRaises(c.Diagnostic): verify(bad,self.registry,*self.args)

    def test_stale_and_successor_records(self):
        new=load(ROOT/'benchmark/results/phase6/r6_37/new.json')
        old=next(d for d in self.snapshot['definitions'].values() if d['name']=='WindowCharge')
        self.registry.admit([new],self.registry.read()['token'],old['identity'])
        with self.assertRaises(c.Diagnostic): verify(self.snapshot,self.registry,*self.args)
        current=generate(self.registry,*self.args)
        self.assertEqual(current['successors'],{new['identity']:old['identity']})
        self.assertIn(new['identity'],current['retrieval_references'])

    def test_required_state_and_unknown_identity(self):
        with self.assertRaises(c.Diagnostic): generate(self.registry,'r','o',{'CallerA':self.bindings['CallerA']},'c')
        with self.assertRaises(c.Diagnostic): retrieve(self.registry,'0'*64,'definition')
        with self.assertRaises(c.Diagnostic): retrieve(self.registry,self.bindings['CallerA'],'execute')


if __name__=='__main__': unittest.main()
