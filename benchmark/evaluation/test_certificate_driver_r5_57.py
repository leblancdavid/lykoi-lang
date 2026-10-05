"""Fresh linkage regression on an explicitly selected canonical synthetic fixture.

Inherits unchanged CertificateV2 adversarial assertions; preserves the older
fixture's raw-manifest setup failure. No production receipts or B02 subjects.
"""

from pathlib import Path
import tempfile

from benchmark.evaluation import test_certificate_r5_55 as previous
from benchmark.evaluation import checkout_r5_52 as checkout
from benchmark.evaluation import qualified_authority_r5_55 as authority
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation import bounded_driver_r5_57 as budgeting
from benchmark.evaluation.recorder_r5_43 import canonical, digest, loads
from benchmark.results.phase5c import r5_55_qualification as source


class DriverCertificateTests(previous.SuccessorCertificateTests):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name) / 'qualified-fixture'
        tier.Workspace.materialize(source.ROOT, cls.root, source.boundary()['scopes'])
        path = cls.root / 'benchmark/results/phase5c/R5_53-authority-successor-v1.json'
        baseline = loads(path.read_bytes())
        # Explicit prospective canonical materialization before policy pin/capture.
        # Baseline semantic identity and the original source bytes stay unchanged.
        path.write_bytes(canonical(baseline) + b'\n')
        blobs = checkout.blobs(cls.root, [r['blob'] for r in baseline['members'].values() if r['blob']])
        for name, row in baseline['members'].items():
            if row['blob'] is None and row['kind'] == 'utf8-lf-text':
                member = cls.root / name
                selected = member.read_bytes().replace(b'\r\n', b'\n')
                assert digest(selected) == row['sha256']
                member.write_bytes(selected)
            if row['blob'] and name in {'docs/project-overview.md', 'docs/decisions.md', 'docs/research-log.md'}:
                (cls.root / name).write_bytes(blobs[row['blob']])
        cls.auth = source.authorization(cls.root)
        for row in baseline['predecessors']:
            member = cls.root / cls.auth['predecessor_root'] / row['path']
            if digest(member.read_bytes()) != row['raw_sha256']:
                selected = checkout.git(cls.root, 'show', 'HEAD:' + member.relative_to(cls.root).as_posix())
                if digest(selected) != row['raw_sha256']:
                    selected = selected.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
                assert digest(selected) == row['raw_sha256']
                member.write_bytes(selected)
        cls.auth = source.authorization(cls.root)
        cls.pin = digest(canonical(cls.auth))
        cls.qualified = authority.qualify(cls.root, cls.auth, trusted_policy_identity=cls.pin)
        cls.capsule = tier.capture(cls.root, source.boundary(), tier.controlled_environment({}, cls.root))

    def test_scheduler_receipts_certificate_linkage(self):
        with tempfile.TemporaryDirectory() as output:
            now = [0]
            self.policy['experiment'] = 'synthetic:r557-certificate-continuation'
            stages = {}
            for name in self.policy['stages']:
                def run(timeout, name=name):
                    now[0] += 10
                    return self.results[name]
                stages[name] = {'mechanism': self.policy['stages'][name],
                               'capabilities': ['REGRESSION_EVIDENCE'],
                               'cost': budgeting.Cost(1, 1, 2, 1, 1, 1, 1, 1), 'run': run}
            driver = budgeting.Driver(output, self.policy['experiment'], self.capsule,
                self.qualified['identity'], stages, lambda: self.capsule,
                lambda: self.qualified['identity'], clock=lambda: now[0])
            driver.initialize()
            rows = [driver.batch(n) for n in (29, 39, 29)]
            self.assertEqual([len(r['receipts']) for r in rows], [1, 2, 1])
            self.evidence = driver.validate()[0]
            certificate = self.assemble()
            self.assertTrue(previous.certs.validate(certificate, self.qualified, self.capsule,
                self.evidence, self.policy, self.capsule, self.root, self.auth, trusted_policy_identity=self.pin))
