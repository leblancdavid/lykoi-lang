"""Synthetic-only worker implementations for independent boundary witnesses."""

from pathlib import Path
import os
import subprocess
import sys
import time
import unittest


def probe(context):
    selection = context['selection']
    action = selection.get('action', 'pass')
    if action == 'protected':
        Path(selection['path']).read_bytes()
    if action == 'ordinary':
        return {'successful': Path(selection['path']).read_text() == 'ordinary'}
    if action == 'subprocess':
        subprocess.run([sys.executable, '-c', 'pass'], check=True)
    if action == 'interrupt':
        Path(selection['marker']).write_text('worker started')
        time.sleep(30)
    if action == 'secret':
        raise RuntimeError('sk-' + 'A' * 24)
    if action == 'environment':
        return {'successful': not any(k in os.environ for k in
            ('OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'OPENCODE_CONFIG', 'PYTHONPATH', 'PATH')),
            'environment_names': sorted(os.environ)}
    if action == 'payload':
        return selection['result']
    if action == 'sut':
        result = subprocess.run([sys.executable, str(Path(context['root']) /
            'benchmark/evaluation/synthetic_sut_r5_62.py'), *selection.get('argv', [])],
            cwd=context['root'], text=True, capture_output=True)
        return {'successful': result.returncode == 0, 'sut_exit': result.returncode}
    return {'successful': action != 'fail', 'startup_order': context['order'] + ['execution']}


class OrdinaryTest(unittest.TestCase):
    def test_ordinary(self):
        self.assertEqual(os.environ.get('PYTHONHASHSEED'), '0')
