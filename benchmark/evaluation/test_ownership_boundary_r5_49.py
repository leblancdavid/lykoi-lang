"""Fresh synthetic counterexample to precheck-only ownership, never production.

Passing this test establishes a gap, not an ownership guarantee. It observes a
material input changed after authorization capture and restored before final
integrity. The historical synthetic bridge deliberately provides no OS seal.
"""

import unittest

from benchmark.evaluation import test_execution_identity_r5_48 as fixtures
from benchmark.evaluation import execution_identity_r5_48 as previous


class OwnershipBoundaryTests(unittest.TestCase):
    def test_check_then_observe_aba_does_not_establish_ownership(self):
        fixture = fixtures.IdentityTests(methodName='test_deterministic_capture')
        fixture.setUp()
        self.addCleanup(fixture.doCleanups)
        recorder = fixture.recorder()
        certified = fixture.source.read_bytes()
        observations = []

        def callback():
            try:
                fixture.source.write_bytes(b'uncertified material input')
                observations.append(fixture.source.read_bytes())
                return {'synthetic': 'uncertified input was readable'}
            finally:
                fixture.source.write_bytes(certified)

        previous.authorize_synthetic(fixture.certificate(), fixture.frozen, fixture.evidence,
                                     fixture.policy, fixture.capture, recorder, callback)
        self.assertEqual(fixture.capture(), fixture.frozen)
        self.assertNotEqual(observations, [certified])
        self.assertEqual(recorder.counts()['completed_observations'], 1)


if __name__ == '__main__':
    unittest.main()
