"""Synthetic regression evidence; no frozen candidates imported or executed."""
import os
import subprocess
import sys
import time
import unittest
from unittest.mock import patch

from scorer import execute, score


class ScorerTests(unittest.TestCase):
    def test_duplicate_keys_all_depths_and_tracks(self):
        for track in 'ABC':
            for text in ('{"x":0,"x":1}', '{"a":[{"x":0,"x":1}]}',
                         '{"x":0,"\\u0078":1}'):
                with self.subTest(track=track, text=text):
                    self.assertEqual(score(text, 0, {})['status'], 'DUPLICATE_OUTPUT_KEY')

    def test_object_order_only_is_irrelevant(self):
        self.assertTrue(score('{"b":[1,2],"a":3}', 0, {'a': 3, 'b': [1, 2]})['passed'])
        self.assertFalse(score('{"b":[2,1],"a":3}', 0, {'a': 3, 'b': [1, 2]})['passed'])

    def test_strict_types_extra_keys_exit(self):
        for text in ('{"x":true}', '{"x":1.0}', '{"x":1,"extra":0}', '{}'):
            self.assertFalse(score(text, 0, {'x': 1})['passed'])
        self.assertEqual(score('{"x":1}', 4, {'x': 1})['status'], 'NONZERO_EXIT')

    def test_malformed_nonfinite_and_extra_stdout(self):
        for text in ('', '{', '{} {}', '{}\nnoise', '{"x":NaN}', '{"x":Infinity}'):
            self.assertEqual(score(text, 0, {})['status'], 'INVALID_OUTPUT')

    def test_actual_process_timeout_retains_raw_output(self):
        row = execute([sys.executable, '-B', '-c',
                       'import time; print("partial", flush=True); time.sleep(5)'],
                      {'input': {}, 'expected': {}}, None, os.environ,
                      time.monotonic() + 20, process_seconds=0.4)
        self.assertEqual(row['status'], 'PROCESS_TIMEOUT')
        self.assertIn('partial', row['stdout'])
        self.assertIn('completion_utc', row)

    def test_session_remaining_bounds_process_and_stops_dispatch(self):
        row = execute([sys.executable, '-B', '-c', 'import time; time.sleep(5)'],
                      {'input': {}, 'expected': {}}, None, os.environ,
                      time.monotonic() + 0.2)
        self.assertEqual(row['status'], 'SESSION_TIMEOUT')
        with patch('scorer.subprocess.run') as run:
            row = execute([], {'input': {}, 'expected': {}}, None, {}, time.monotonic() - 1)
            run.assert_not_called()
        self.assertEqual(row['status'], 'NOT_REACHED_SESSION_BUDGET')

    def test_deadline_completion_cannot_pass(self):
        with patch('scorer.time.monotonic', side_effect=[1, 3, 3]), patch(
                'scorer.subprocess.run', return_value=subprocess.CompletedProcess([], 0, b'{}', b'')):
            row = execute([], {'input': {}, 'expected': {}}, None, {}, 2)
        self.assertEqual(row['status'], 'SESSION_TIMEOUT')
        self.assertFalse(row['passed'])

    def test_scorer_error_is_distinct(self):
        with patch('scorer.subprocess.run', return_value=subprocess.CompletedProcess([], 0, b'{}', b'')):
            row = execute([], {'input': {}, 'expected': {'x': float('nan')}},
                          None, {}, time.monotonic() + 10)
        self.assertEqual(row['status'], 'SCORER_ERROR')
        self.assertIsNotNone(row['scorer_error'])

    def test_launch_error_is_distinct(self):
        with patch('scorer.subprocess.run', side_effect=OSError('synthetic launch failure')):
            row = execute([], {'input': {}, 'expected': {}}, None, {}, time.monotonic() + 10)
        self.assertEqual(row['status'], 'EXECUTION_ERROR')

    def test_invalid_utf8_is_output_failure(self):
        with patch('scorer.subprocess.run', return_value=subprocess.CompletedProcess([], 0, b'\xff', b'')):
            row = execute([], {'input': {}, 'expected': {}}, None, {}, time.monotonic() + 10)
        self.assertEqual(row['status'], 'INVALID_OUTPUT')


if __name__ == '__main__':
    unittest.main()
