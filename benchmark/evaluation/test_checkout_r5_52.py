"""Synthetic challenges for reconciliation; no benchmark subject evaluation."""

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from benchmark.evaluation import checkout_r5_52 as check
from benchmark.evaluation import infrastructure_lock_r5_47 as historical
from benchmark.evaluation import security_r5_47 as security


class ClassificationTests(unittest.TestCase):
    def test_byte_identical(self):
        self.assertEqual(check.classify(b'alpha\n', b'alpha\n'), 'BYTE_IDENTICAL')

    def test_crlf_counterpart(self):
        self.assertEqual(check.classify(b'alpha\n', b'alpha\r\n'), 'LINE_ENDING_ONLY')

    def test_lf_counterpart(self):
        self.assertEqual(check.classify(b'alpha\r\n', b'alpha\n'), 'LINE_ENDING_ONLY')

    def test_crlf_presence_is_not_proof(self):
        self.assertEqual(check.classify(b'alpha\n', b'omega\r\n'), 'CONTENT_DIFFERENT')

    def test_binary_mutation(self):
        self.assertEqual(check.classify(b'\x00\n', b'\x00\r\n'), 'CONTENT_DIFFERENT')
        self.assertEqual(check.classify(b'\xffa', b'\xffb'), 'CONTENT_DIFFERENT')

    def test_missing(self):
        self.assertEqual(check.classify(b'alpha', None), 'MISSING')

    def test_unexpected(self):
        self.assertEqual(check.classify(None, b'new', unexpected=True), 'UNEXPECTED')

    def test_unknown_authority_is_not_normalized_pass(self):
        self.assertEqual(check.classify(None, b'alpha\r\n'), 'UNCLASSIFIED')

    def test_pin_recovery_requires_exact_raw_hash(self):
        value, evidence = check.recover(check.sha(b'alpha\r\n'), [('fixture', b'alpha\n')])
        self.assertEqual(value, b'alpha\r\n')
        self.assertTrue(evidence['exact_pin_recovered'])
        self.assertIsNone(check.recover(check.sha(b'omega\n'), [('fixture', b'alpha\n')])[0])

    def test_mixed_pin_recovery(self):
        authority = b'old\r\nnew\n'
        value, evidence = check.recover_mixed(check.sha(authority), [('fixture', b'old\nnew\n')])
        self.assertEqual(value, authority)
        self.assertTrue(evidence['exact_pin_recovered'])

    def test_frozen_pin_diagnosis(self):
        frozen = b'{"frozen":true}\n'
        current = b'{"frozen":true}\r\n'
        recovered, _ = check.recover(check.sha(frozen), [('frozen-object', frozen)])
        self.assertEqual(check.classify(recovered, current), 'LINE_ENDING_ONLY')
        self.assertNotEqual(check.sha(current), check.sha(frozen))

    def test_semantic_non_interference(self):
        source = b'def compute(x):\n    return x * 7 + 2\n'
        outputs = []
        for data in (source, source.replace(b'\n', b'\r\n')):
            namespace = {}
            exec(compile(data, '<synthetic>', 'exec'), namespace)
            outputs.append([namespace['compute'](x) for x in (-3, 0, 8)])
        self.assertEqual(outputs, [[-19, 2, 58], [-19, 2, 58]])

    def test_authorized_successor_requires_explicit_decision(self):
        result = check.disposition('AUTHORIZED_SUCCESSOR_CHANGE', decision='R5.synthetic explicit policy',
                                   before=check.sha(b'old'), after=check.sha(b'new'))
        self.assertEqual(result['category'], 'AUTHORIZED_SUCCESSOR_CHANGE')
        with self.assertRaises(ValueError):
            check.disposition('AUTHORIZED_SUCCESSOR_CHANGE', before='old', after='new')

    def test_unauthorized_change_rejected_as_successor(self):
        result = check.disposition('UNAUTHORIZED_CHANGE', before='old', after='new')
        self.assertNotEqual(result['category'], 'AUTHORIZED_SUCCESSOR_CHANGE')
        with self.assertRaises(ValueError):
            check.disposition('reasonable-current-file')

    def test_security_successor_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / '.gitignore'
            path.write_bytes(b'.env\n.env.*\n!.env.example\n!.env.sample\n')
            lock = historical.manifest(root, ['.gitignore'], {'protocol': 'synthetic-security-successor'})
            path.write_bytes(b'')
            with self.assertRaises(ValueError):
                historical.verify(root, lock)

    def test_historical_lock_preservation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / 'source.txt'
            path.write_bytes(b'alpha\n')
            lock = historical.manifest(root, ['source.txt'], {'protocol': 'exact-physical'})
            before = json.dumps(lock, sort_keys=True)
            path.write_bytes(b'alpha\r\n')
            with self.assertRaises(ValueError):
                historical.verify(root, lock)
            self.assertEqual(json.dumps(lock, sort_keys=True), before)
            self.assertEqual(check.classify(b'alpha\n', path.read_bytes()), 'LINE_ENDING_ONLY')

    def test_candidate_successor_determinism(self):
        repo = {'a': check.sha(b'alpha\n'), 'b': check.sha(b'\x00b')}
        checkout = {'a': {'form': 'CRLF'}, 'b': {'form': 'binary'}}
        self.assertEqual(check.candidate_identity(repo, checkout, {'pin': 'exact'}),
                         check.candidate_identity(dict(reversed(list(repo.items()))), checkout, {'pin': 'exact'}))
        self.assertNotEqual(check.candidate_identity(repo, checkout, {'pin': 'exact'}),
                            check.candidate_identity(repo, checkout, {'pin': 'different'}))


class GitTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        check.git(self.root, 'init', '-q')
        (self.root / 'source.py').write_bytes(b'value = 7\n')
        check.git(self.root, '-c', 'core.autocrlf=false', 'add', 'source.py')

    def checkout(self, autocrlf):
        (self.root / 'source.py').unlink()
        check.git(self.root, '-c', 'core.autocrlf=' + autocrlf, 'checkout-index', '--all', '--force')
        return (self.root / 'source.py').read_bytes()

    def test_git_attribute_interpretation(self):
        (self.root / '.gitattributes').write_bytes(b'*.py text eol=lf\n')
        attrs = check.attributes(self.root, ['source.py'])['source.py']
        self.assertEqual(attrs['text'], 'set')
        self.assertEqual(attrs['eol'], 'lf')
        self.assertEqual(self.checkout('true'), b'value = 7\n')

    def test_checkout_conversion_reproduction(self):
        self.assertEqual(self.checkout('true'), b'value = 7\r\n')
        self.assertEqual(self.checkout('false'), b'value = 7\n')

    def test_repository_vs_working_tree(self):
        repository = check.git(self.root, 'show', ':source.py')
        current = self.checkout('true')
        self.assertNotEqual(check.sha(repository), check.sha(current))
        self.assertEqual(check.normalize(current), repository)
        self.assertEqual(check.git(self.root, 'diff', '--name-only'), b'')

    def test_clean_materialization_comparison(self):
        clean = self.checkout('false')
        converted = self.checkout('true')
        self.assertEqual(check.classify(clean, converted), 'LINE_ENDING_ONLY')
        self.assertEqual(check.sha(clean), check.sha(check.git(self.root, 'show', ':source.py')))

    def test_effective_ignore_exceptions(self):
        (self.root / '.gitignore').write_bytes(b'.env\n.env.*\n!.env.example\n!.env.sample\n')
        for name, expected in (('.env', True), ('.env.example', False), ('.env.sample', False)):
            process = subprocess.run(['git', 'check-ignore', '--no-index', '--quiet', name],
                                     cwd=self.root, capture_output=True)
            verbose = subprocess.run(['git', 'check-ignore', '-v', '--no-index', name],
                                     cwd=self.root, capture_output=True)
            # Git 2.25 returns success even for a negated match in quiet mode.
            # The strongest observable check: does Git include it as unignored?
            (self.root / name).write_bytes(b'synthetic\n')
            unignored = check.git(self.root, 'ls-files', '--others', '--exclude-standard').decode().splitlines()
            self.assertEqual(name not in unignored, expected)
            self.assertIn('!' if not expected else '.env', verbose.stdout.decode())
            self.assertIn(process.returncode, (0, 1))


if __name__ == '__main__':
    unittest.main()
