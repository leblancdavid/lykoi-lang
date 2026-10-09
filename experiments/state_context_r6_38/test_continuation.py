"""Post-authoring supplemental qualification; no scored oracle changes."""
import copy
import tempfile
import unittest
from pathlib import Path
from common import ROOT, OUT, Registry, c, load, digest
from snapshot import generate, verify, retrieve


class ContinuationTests(unittest.TestCase):
    def test_selective_migration_snapshot_and_restart(self):
        with tempfile.TemporaryDirectory() as temp:
            registry=Registry(Path(temp)/'registry')
            ds={key:load(ROOT/'benchmark/results/phase6/r6_37'/f'{key}.json') for key in ('old','new','a','b','a_new')}
            registry.admit([ds[k] for k in ('old','a','b')],None)
            registry.admit([ds['new']],registry.read()['token'],ds['old']['identity'])
            registry.admit([ds['a_new']],registry.read()['token'],ds['a']['identity'])
            registry.migrate(ds['old']['identity'],ds['new']['identity'],{ds['a']['identity']:ds['a_new']['identity'],ds['b']['identity']:None},registry.read()['token'])
            args=('r','o',{'CallerA':ds['a_new']['identity'],'CallerB':ds['b']['identity']},'frozen constraints')
            snap=generate(registry,*args)
            self.assertEqual(len(snap['definitions']),4)
            self.assertEqual(snap['migrations'],registry.read()['state']['migrations'])
            self.assertTrue(verify(snap,Registry(registry.path),*args))
            self.assertEqual(retrieve(registry,ds['a']['identity'],'definition'),registry.retrieve(pin=ds['a']['identity']))
            before=registry.read()
            for kind in ('definition','dependencies','validation','history','identity'):
                retrieve(registry,ds['a_new']['identity'],kind)
            self.assertEqual(before,registry.read())

    def test_actual_scored_snapshot_exact_authoritative_generation(self):
        for task in ('T1','T2','T3'):
            folder=OUT/(task+'-B'); snap=load(folder/'SNAPSHOT.json')
            with tempfile.TemporaryDirectory() as temp:
                registry=Registry(Path(temp)/'registry')
                for source in sorted((folder/'registry').glob('*.json'))[:snap['generation']]:
                    (registry.path/source.name).write_bytes(source.read_bytes())
                self.assertTrue(verify(snap,registry,snap['requirement'],snap['objective'],snap['caller_bindings'],snap['constraints']))
                self.assertEqual(snap['registry_token'],registry.read()['token'])


if __name__=='__main__': unittest.main()
