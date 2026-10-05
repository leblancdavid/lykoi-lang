"""Prospective workers: exact indexed tests and content-bound Python SUT entry.

Worker closures and their selected inputs must be pinned in the qualification.
No import-all discovery, shell command, AI service or network inference is used.
"""

import contextlib
import io
import os
import runpy
import sys
import unittest
from pathlib import Path

from benchmark.evaluation.recorder_r5_43 import digest, ProtocolFailure


def harness(context):
    loader = unittest.TestLoader()
    identities = context['selection']['identities']
    def factory(identity):
        return loader.loadTestsFromName(identity)
    suite = context['safe_suite'](identities, factory)
    if loader.errors:
        raise ProtocolFailure('safe test selection failed; details withheld')
    result = unittest.TextTestRunner(stream=io.StringIO()).run(suite)
    return {'successful': result.wasSuccessful(), 'discovered': result.testsRun,
            'skipped': len(result.skipped), 'errors': len(result.errors), 'failures': len(result.failures),
            'startup_order': context['order'] + ['execution']}


def sut(context):
    """Standalone Python entry in its already mediated child process.

    The SUT source is a required member of the qualified worker closure. Native
    or further arbitrary subprocess execution remains denied by the child guard.
    """
    selection = context['selection']
    path = Path(context['root']) / selection['path']
    if digest(path.read_bytes()) != selection['sha256']:
        raise ProtocolFailure('SUT substitution rejected')
    sys.argv = [str(path), *selection['argv']]
    if 'cwd' in selection:
        os.chdir(selection['cwd'])
    output, error, code = io.StringIO(), io.StringIO(), 0
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error):
        try:
            runpy.run_path(str(path), run_name='__main__')
        except SystemExit as exit:
            code = exit.code or 0
    # Raw SUT diagnostics are private. Qualification receipts publish only status.
    result = {'successful': code == 0, 'exit': code if type(code) is int else 1}
    if selection.get('capture') is True:
        result.update(stdout=output.getvalue(), stderr=error.getvalue())
    return result
