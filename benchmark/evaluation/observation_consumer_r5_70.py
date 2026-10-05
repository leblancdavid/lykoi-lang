"""Prospective V3 preparation and synthetic two-object observation consumer.

Historical StaticGate remains historical. No actual protected-resource opener,
observation authorization issuer, or arbitrary callback dispatch is provided.
"""
from pathlib import Path
import time

from benchmark.evaluation import certificate_r5_68 as certificates
from benchmark.evaluation import mediated_child_r5_62 as mediated
from benchmark.evaluation import capability_guard_r5_61 as guard
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import sealed_authority_r5_66 as sealed
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, digest

PROTOCOL = 'lykoi-observation-consumer-r5.70-v1'
SUPPORTED = (certificates.PROTOCOL, 3)
OBSERVE = 'SYNTHETIC_ONE_TIME_OBSERVATION'


def fail():
    raise ProtocolFailure('R5.70 observation consumer rejected; details withheld')


class StaticGate:
    """Explicit V3 interface using the qualified producer and mediated workers.

    Owner-supplied pins and reviewed capture/authority/contamination adapters
    retain the cooperative Tier-2 trust boundary. Preparation grants no opening.
    """
    def __init__(self, workspace, cert, qualified, capsule, evidence, policy,
                 capture_state, authority, declaration, *, trusted_declaration_identity,
                 qualification, worker, boundary, capabilities, contamination,
                 mode=certificates.PRODUCTION, seconds=30):
        self.workspace, self.cert, self.qualified = workspace, cert, qualified
        self.capsule, self.evidence, self.policy = capsule, evidence, policy
        self.capture, self.authority, self.declaration = capture_state, authority, declaration
        self.binding = dict(trusted_declaration_identity=trusted_declaration_identity,
                            qualification=qualification, mode=mode)
        self.worker, self.boundary = worker, boundary
        self.capabilities = list(guard.authorize(capabilities))
        self.contamination, self.seconds = contamination, seconds
        self.recorder = publication.PublicationRecorder(workspace.evidence)

    def validate(self, current):
        # No latest-wins fallback, legacy reconstruction, or implicit V2 mode.
        if (type(self.cert) is not dict or type(self.cert.get('version')) is not int or
                (self.cert.get('protocol'), self.cert.get('version')) != SUPPORTED or
                self.binding['mode'] not in certificates.OPERATIONS):
            fail()
        certificates.require_operation(self.cert, certificates.OPERATIONS[self.binding['mode']],
            self.qualified, self.capsule, self.evidence, self.policy, current,
            self.authority, self.declaration, **self.binding)
        if self.contamination() != []:
            fail()

    def worker_check(self):
        if (type(self.worker) is not mediated.Child or type(self.boundary) is not guard.Boundary or
                self.worker.boundary is not self.boundary or self.boundary.denied or
                self.worker.value['parent'] != self.parent):
            fail()
        mediated.validate(self.worker.value, self.worker.expected)

    def prepare(self):
        """Production preparation always requires PRODUCTION_SEALED."""
        if self.binding['mode'] != certificates.PRODUCTION:
            fail()
        return self._prepare()

    def prepare_synthetic(self):
        """Explicit authorized synthetic qualification, never production prepare."""
        if (self.binding['mode'] != certificates.SYNTHETIC or
                any(row['classification'] == 'SEALED' and
                    (not row['resource'].startswith('synthetic:') or
                     row['source'] != 'synthetic-immutable-object')
                    for row in self.authority.policy['members'].values())):
            fail()
        return self._prepare()

    def _prepare(self):
        self.workspace.verify()
        self.validate(self.capture())
        if (type(self.worker) is not mediated.Child or type(self.boundary) is not guard.Boundary or
                type(self.authority) is not sealed.Authority or
                not set(self.worker.capabilities) <= set(self.capabilities)):
            fail()
        # Every sealed authority member must also be registered with the guard.
        resources = {(r.identity, r.path.resolve()) for r in self.boundary.resources}
        for name, row in self.authority.policy['members'].items():
            if row['classification'] == 'SEALED' and (
                    row['resource'], (self.authority.root / name).resolve()) not in resources:
                fail()
        self.parent = {'protocol': PROTOCOL, 'certificate': self.cert['identity'],
            'certificate_qualification': self.binding['qualification'],
            'authority': self.qualified['identity'], 'resource_policy': self.boundary.identity(),
            'capability_guard': self.boundary.implementation(),
            'stages': [{'name': 'observation', 'capability_binding': guard.binding(self.capabilities),
                        'child': self.worker.descriptor}]}
        self.worker.bind(self.parent, 'observation', self.boundary)
        self.worker_check()
        items = [('capsule', self.capsule), ('certificate', self.cert),
                 ('qualified-authority', self.qualified), ('execution', self.parent),
                 *self.evidence.items()]
        for name, item in items:
            publication.persist(self.workspace.evidence / (name + '-staged.json'), item)
        self.recorder.freeze({'certificate': self.cert['identity'], 'capsule': self.capsule['identity'],
            'experiment': self.policy['experiment'], 'execution': digest(canonical(self.parent))},
            [self.workspace.evidence / (n + '-staged.json') for n, _ in items] + [self.workspace.marker])
        return True

    def authorization_check(self, authorization, pin, reference, ledger):
        publication.safe_bytes(authorization)
        if (type(authorization) is not dict or not pin or sealed.identity(authorization) != pin or
                set(authorization) != {'protocol', 'operation', 'certificate', 'qualification', 'opening'}):
            fail()
        opening = authorization['opening']
        expected = {'protocol': PROTOCOL, 'operation': OBSERVE, 'certificate': self.cert['identity'],
                    'qualification': self.binding['qualification'], 'opening': opening}
        if authorization != expected or type(opening) is not dict:
            fail()
        if opening != {'capability': sealed.OPEN, 'scope': 'SYNTHETIC_ONLY',
                'resource': reference.get('resource'), 'commitment': reference.get('commitment'),
                'qualified_authority': self.qualified['identity'], 'one_time': True,
                'ledger_binding': sealed.identity(str(Path(ledger).resolve()))}:
            fail()
        if (not opening['resource'].startswith('synthetic:') or
                self.worker.inputs != {'opening_result': str(Path(ledger).with_suffix('.result.json').resolve()),
                                       'commitment': opening['commitment']}):
            fail()
        return opening

    def observe_synthetic(self, reference, store, authorization, *, trusted_observation_identity, ledger):
        # No generic actual-resource method exists. No certificate alone is a grant.
        self.validate(self.capture())
        self.worker_check()
        opening = self.authorization_check(authorization, trusted_observation_identity, reference, ledger)
        if type(store) is not sealed.SyntheticStore:
            fail()
        try:
            started = time.monotonic()
            self.recorder.open_run()
            self.workspace.verify()
            self.recorder.integrity()
            if self.recorder.counts()['disposition'] != 'zero':
                fail()
            # Recorder owns observation-*.json; protocol evidence uses another namespace.
            publication.persist(self.workspace.evidence / 'separate-authorization.json', authorization)
            self.validate(self.capture())
            baseline = self.recorder.read('baseline')['evidence']
            self.recorder.verify(baseline)
            if time.monotonic() - started > self.seconds:
                fail()
            def dispatch():
                # Durable recorder reservation/dispatch precede durable seal reservation.
                publication.persist(self.workspace.evidence / 'synthetic-dispatch.json', {
                    'protocol': PROTOCOL, 'certificate': self.cert['identity'],
                    'observation_binding': trusted_observation_identity,
                    'reservation': digest(self.recorder.path('reservation-1').read_bytes()),
                    'execution': self.worker.expected, 'ledger_binding': opening['ledger_binding']})
                data = sealed.open_synthetic(self.authority, self.qualified, reference, store, opening,
                    trusted_grant_identity=sealed.identity(opening), ledger=ledger)
                with self.boundary.stage(self.capabilities):
                    result = self.worker(self.seconds)
                if result.get('successful') is not True or digest(data) != reference['commitment']:
                    fail()
                return result
            result = self.recorder.observe(dispatch)
            # First post-completion action independently captures current state.
            post = time.monotonic()
            after = self.capture()
            self.validate(after)
            self.workspace.verify()
            self.worker_check()
            self.recorder.integrity()
            self.recorder.verify(baseline)
            if self.recorder.counts()['disposition'] != 'one' or time.monotonic() - post > self.seconds:
                fail()
            publication.persist(self.workspace.evidence / 'synthetic-completion.json', {
                'protocol': PROTOCOL, 'certificate': self.cert['identity'],
                'observation_binding': trusted_observation_identity,
                'dispatch': digest((self.workspace.evidence / 'synthetic-dispatch.json').read_bytes()),
                'observation': digest(self.recorder.path('observation-1').read_bytes()),
                'successful': True})
            self.recorder.finish()
            return result
        except Exception:
            self.recorder.halt('R5.70 synthetic observation failed; details withheld')
            if not self.recorder.path('final').exists():
                self.recorder.finish()
            fail()
