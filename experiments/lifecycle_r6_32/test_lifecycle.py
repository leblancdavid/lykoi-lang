"""Stateful durability/type/migration regression controls, standard library only."""
import copy
from pathlib import Path
import tempfile
import unittest
from lifecycle import Registry, Journal, c, publish, digest
from qualify import simple, caller
from edit import revise
import fixture


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = Registry(self.root / 'registry')

    def rejects(self, code, fn):
        with self.assertRaises(c.Diagnostic) as caught:
            fn()
        self.assertEqual(caught.exception.data['code'], code)

    def test_exact_retrieval_survives_successor_and_restart(self):
        original = simple('Stable')
        token = self.registry.admit([original], None)['token']
        successor = simple('Stable', 2)
        self.registry.admit([successor], token, original['identity'])
        restarted = Registry(self.registry.path)
        self.assertEqual(restarted.retrieve(pin=original['identity']), [original])
        self.rejects('AMBIGUOUS_REFERENCE', lambda: restarted.resolve('Stable'))
        fetched = restarted.retrieve(pin=original['identity'])
        fetched[0]['result'] = {'const': 44}
        self.assertEqual(restarted.retrieve(pin=original['identity']), [original])

    def test_batch_missing_dependency_publishes_nothing(self):
        old = simple('Old')
        dependent = caller('Caller', simple('Absent'))
        self.rejects('MISSING_DEPENDENCY', lambda: self.registry.admit([old, dependent], None))
        self.assertEqual(self.registry.read()['generation'], 0)

    def test_invalid_parameter_schema_has_structured_diagnostic(self):
        for malformed in (None, {}, 1):
            candidate = simple('Malformed')
            candidate['params'] = malformed
            candidate = c.seal(candidate)
            self.rejects('SHAPE', lambda: self.registry.admit([candidate], None))
        self.assertEqual(self.registry.read()['generation'], 0)

    def test_stale_writers_cannot_lose_an_admission(self):
        stale = Registry(self.registry.path)
        token = stale.read()['token']
        admitted = simple('First')
        self.registry.admit([admitted], token)
        self.rejects('STALE_READ', lambda: stale.admit([simple('Second')], token))
        self.assertEqual(stale.retrieve(pin=admitted['identity']), [admitted])

    def test_existing_writer_lock_refuses_commit(self):
        with (self.registry.path / 'writer.lock').open('x'):
            pass
        self.rejects('WRITER_BUSY', lambda: self.registry.admit([simple('Locked')], None))
        self.assertEqual(self.registry.read()['generation'], 0)

    def test_interrupted_registry_commit_preserves_old_generation(self):
        old = simple('Old')
        token = self.registry.admit([old], None)['token']
        with self.assertRaises(InterruptedError):
            self.registry.admit([simple('New')], token, interrupt=True)
        restarted = Registry(self.registry.path)
        self.assertEqual(restarted.read()['token'], token)
        self.assertEqual(restarted.retrieve(pin=old['identity']), [old])
        self.assertEqual(restarted.read()['pending'], ['000002.json.pending'])
        self.rejects('INCOMPLETE_WRITE', lambda: restarted.admit([simple('Next')], token))

    def test_caller_migration_cannot_change_behavior_beyond_pin(self):
        old, new = simple('Shared'), simple('Shared', 2)
        user = caller('User', old)
        token = self.registry.admit([old, user], None)['token']
        token = self.registry.admit([new], token, old['identity'])['token']
        wrong_user = caller('User', new)
        wrong_user['result'] = {'const': 99}
        wrong_user = c.seal(wrong_user)
        token = self.registry.admit([wrong_user], token, user['identity'])['token']
        self.rejects('INVALID_MIGRATION', lambda: self.registry.migrate(old['identity'], new['identity'],
            {user['identity']: wrong_user['identity']}, token))
        self.assertEqual(self.registry.read()['state']['migrations'], [])

    def test_transitive_callers_remain_pinned_until_explicit_update(self):
        old = simple('Root')
        mid = caller('Middle', old)
        top = caller('Top', mid)
        token = self.registry.admit([old, mid, top], None)['token']
        new = simple('Root', 2)
        self.registry.admit([new], token, old['identity'])
        users = self.registry.dependents(old['identity'])
        self.assertEqual(users['direct'], [mid['identity']])
        self.assertEqual(users['transitive'], sorted([mid['identity'], top['identity']]))
        self.assertEqual({d['identity'] for d in self.registry.retrieve(pin=top['identity'])},
                         {old['identity'], mid['identity'], top['identity']})

    def test_incomplete_telemetry_and_pending_bytes_are_not_completion(self):
        journal = Journal(self.root / 'journal')
        journal.record('start', dict(stage='work', inputs={'exact': 'pin'}))
        with self.assertRaises(InterruptedError):
            journal.record('complete', dict(stage='work', wall_seconds=None), interrupt=True)
        recovered = Journal(journal.path).recover()
        self.assertEqual(recovered['completed'], [])
        self.assertEqual(recovered['incomplete'], ['work'])
        self.assertEqual(recovered['pending'], ['000002.json.pending'])
        self.rejects('INCOMPLETE_WRITE', lambda: journal.record('complete', dict(stage='work')))

    def test_orphan_and_duplicate_stage_events_are_rejected(self):
        journal = Journal(self.root / 'journal')
        self.rejects('TELEMETRY_STAGE', lambda: journal.record('complete', dict(stage='orphan')))
        journal.record('start', dict(stage='stage', inputs={}))
        self.rejects('TELEMETRY_STAGE', lambda: journal.record('start', dict(stage='stage', inputs={})))
        journal.record('complete', dict(stage='stage', wall_seconds=None))
        self.rejects('TELEMETRY_STAGE', lambda: journal.record('complete', dict(stage='stage')))

    def test_removed_journal_event_is_detected_by_recovery(self):
        journal = Journal(self.root / 'journal')
        journal.record('start', dict(stage='work', inputs={}))
        journal.record('complete', dict(stage='work', wall_seconds=None))
        (journal.path / '000001.json').unlink()
        self.rejects('TELEMETRY_INTEGRITY', journal.recover)

    def test_snapshot_deletion_and_tampering_reject(self):
        token = self.registry.admit([simple('A')], None)['token']
        self.registry.admit([simple('B')], token)
        (self.registry.path / '000001.json').unlink()
        self.rejects('REGISTRY_INTEGRITY', self.registry.read)

    def test_no_clobber_publication_retains_interrupted_bytes(self):
        path = self.root / 'object.json'
        publish(path, {'before': 1})
        with self.assertRaises(FileExistsError):
            publish(path, {'after': 2})
        self.assertEqual(path.read_bytes(), c.canonical({'before': 1}))
        self.assertEqual(path.with_name('object.json.pending').read_bytes(), c.canonical({'after': 2}))

    def test_application_edit_requires_exact_consumer_disposition(self):
        original, modified = fixture.copies()
        self.rejects('PARTIAL_MIGRATION', lambda: revise(original, modified, digest(original),
            ['ignite', 'ignite', 'set_gate', 'invariant:0'], []))
        modified['operations']['new_endpoint'] = copy.deepcopy(original['operations']['ignite'])
        self.rejects('UNAUTHORIZED_MUTATION', lambda: revise(original, modified, digest(original),
            ['ignite', 'set_gate', 'invariant:0'], []))


if __name__ == '__main__':
    unittest.main(verbosity=2)
