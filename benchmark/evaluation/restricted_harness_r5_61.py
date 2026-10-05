"""Content-free exclusion before import, construction, fixtures or SUT access.

The index is trusted protocol metadata. Callers cannot override its prohibitions.
Exact IDs select already indexed cases; discovery does not import sealed modules.
"""

from pathlib import Path
import unittest

from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads, ProtocolFailure

INDEX = Path(__file__).with_name('prohibited_test_index_r5_61.json')
INDEX_PIN = '0ff387f592dc61ac40a3d7c4c9372ab43c85a017fa6ff577c1bc2b7140b6df55'


def index():
    raw = INDEX.read_bytes()
    value = loads(raw)
    if raw != canonical(value) + b'\n' or digest(canonical(value)) != INDEX_PIN:
        raise ProtocolFailure('prohibited test index not canonical')
    for entry in value['tests'].values():
        if entry != {'capabilities': ['B02_ACCEPTANCE'], 'status': 'PROHIBITED'}:
            raise ProtocolFailure('prohibited test index invalid')
    return value


class Prohibited(unittest.TestCase):
    def __init__(self, identity):
        super().__init__('runTest')
        self.identity = identity

    def id(self):
        return self.identity

    @unittest.skip('sealed B02 restriction: safe metadata exclusion')
    def runTest(self):
        raise AssertionError('prohibited placeholder executed')


def suite(identities, allowed_factory):
    prohibited = index()['tests']
    if len(identities) != len(set(identities)):
        raise ProtocolFailure('duplicate test selection')
    selected = []
    for identity in identities:
        if identity in prohibited:
            selected.append(Prohibited(identity))
        else:
            selected.append(allowed_factory(identity))
    return unittest.TestSuite(selected)


def authorization():
    return guard.binding(['HARNESS_EXECUTION', 'TEST_DISCOVERY', 'REGRESSION_EVIDENCE'])


def accounting():
    value = index()
    return {'prohibited_b02_skips': len(value['tests']), 'index_sha256': digest(canonical(value)),
            'protected_content_loaded': False}
