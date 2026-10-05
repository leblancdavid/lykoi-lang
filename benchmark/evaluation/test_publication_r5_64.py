"""Independent synthetic adversarial witnesses; no production or B02 entry."""

from dataclasses import replace
import json
from pathlib import Path
import tempfile
import unittest

from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation import tier2_r5_51 as tier
from benchmark.evaluation.recorder_r5_43 import canonical, loads


def identity_body():
    policy_id = 'experiment-authorization-policy-v2'
    return {'experiment': 'synthetic-publication-reconciliation',
        'authorization': policy_id,
        **{name: 'a' * 64 for name in ('plan', 'authority', 'registry', 'exclusion', 'orchestration')},
        'bounded_driver': 'synthetic-driver', 'mediated_worker_policy': 'synthetic-worker-policy',
        'resource_policy': 'synthetic-resource-policy', 'fresh_receipts_only': True,
        'state_binding': 'synthetic metadata only; production execution prohibited'}


def dry_run(path):
    context = {'schema': schemas.QUALIFICATION_IDENTITY,
               'schema_identity': schemas.QUALIFICATION_IDENTITY_PIN}
    identity = tier.seal(identity_body(), **context)
    publication.persist(path, identity, **context)
    reloaded = loads(Path(path).read_bytes())
    publication.safe_bytes(reloaded, **context)
    assert tier.envelopes.unseal(reloaded) == identity_body()
    assert reloaded == identity
    return identity


class PublicationTests(unittest.TestCase):
    def schema(self, fields, **kwargs):
        return schemas.PublicationSchema.declare(schemas.object_schema(fields, **kwargs))

    def publish(self, value, schema):
        return publication.safe_bytes(value, schema=schema, schema_identity=schema.identity)

    def reject(self, value, schema, raw):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'rejected.json'
            with self.assertRaises(security.SecretRejected) as caught:
                publication.persist(path, value, schema=schema, schema_identity=schema.identity)
            self.assertNotIn(raw, str(caught.exception))
            self.assertFalse(path.exists())

    def test_protocol_authorization_allowed(self):
        schema = self.schema({'authorization': schemas.field(schemas.PROTOCOL_AUTHORIZATION)})
        policy_id = 'experiment-allow-static-qualification-v2'
        value = {'authorization': policy_id}
        self.assertEqual(self.publish(value, schema), canonical(value))

    def test_second_independent_protocol_schema(self):
        schema = self.schema({'process': schemas.object_schema({
            'authorization': schemas.field(schemas.PROTOCOL_AUTHORIZATION),
            'stage_class': schemas.field()})})
        policy_id = 'calibration-policy-v7'
        self.publish({'process': {'authorization': policy_id,
                                 'stage_class': 'synthetic'}}, schema)

    def test_bearer_in_protocol_authorization_rejected(self):
        schema = self.schema({'authorization': schemas.field(schemas.PROTOCOL_AUTHORIZATION)})
        for raw in ('Bearer ' + 'A' * 30, 'Bearer ' + 'short', 'Basic ' + 'tiny'):
            self.reject({'authorization': raw}, schema, raw)

    def test_http_authorization_rejected(self):
        schema = self.schema({'headers': schemas.object_schema({
            'Authorization': schemas.field(schemas.CREDENTIAL_HEADER)})})
        raw = 'Bearer ' + 'B' * 30
        self.reject({'headers': {'Authorization': raw}}, schema, raw)

    def test_credential_object_authorization_rejected(self):
        schema = self.schema({'authorization': schemas.field(schemas.SECRET_VALUE)},
                             classification=schemas.SECRET_VALUE)
        raw = 'synthetic-opaque'
        self.reject({'authorization': raw}, schema, raw)

    def test_explicit_public_authorization_metadata(self):
        schema = self.schema({'authorization': schemas.field()})
        policy_id = 'reviewed-public-policy-version'
        self.publish({'authorization': policy_id}, schema)

    def test_api_key_under_innocent_field(self):
        schema = self.schema({'description': schemas.field()})
        raw = 'ghp_' + 'C' * 30
        self.reject({'description': raw}, schema, raw)

    def test_password_under_innocent_field(self):
        schema = self.schema({'description': schemas.field()})
        raw = 'synthetic-hidden-password'
        self.reject({'description': 'PASSWORD' + '="' + raw + '"'}, schema, raw)

    def test_unknown_authorization_safe_fallback(self):
        policy_id = 'ordinary-but-unclassified'
        with self.assertRaises(security.SecretRejected):
            publication.safe_bytes({'authorization': policy_id})
        publication.safe_bytes({'authorization': {'present': True}})
        publication.safe_bytes({'unrelated': 'ordinary-public-metadata'})

    def test_synthetic_fixture_preserved(self):
        name = next(iter(publication.DESIGNATIONS))
        content = (publication.ROOT / name).read_bytes()
        self.assertEqual(publication.check_source(name, content), publication.SYNTHETIC_SECURITY_FIXTURE)
        raw = publication._values()[0]
        schema = self.schema({'authorization': schemas.field(schemas.PROTOCOL_AUTHORIZATION)})
        self.reject({'authorization': raw}, schema, raw)

    def test_diagnostics_redacted_even_for_unsafe_key(self):
        raw = 'ghp_' + 'D' * 30
        schema = self.schema({raw: schemas.field()})
        self.reject({raw: 'metadata'}, schema, raw)

    def test_qualification_identity_publication(self):
        with tempfile.TemporaryDirectory() as directory:
            identity = dry_run(Path(directory) / 'identity.json')
            self.assertEqual(identity['authorization'], identity_body()['authorization'])

    def test_canonical_identity_reload(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'identity.json'
            identity = dry_run(path)
            self.assertEqual(path.read_bytes(), canonical(identity) + b'\n')
            self.assertEqual(loads(path.read_bytes()), identity)

    def test_schema_mutation_invalidates_classification(self):
        original = self.schema({'authorization': schemas.field(schemas.SECRET_VALUE)})
        changed = replace(original, definition=self.schema({
            'authorization': schemas.field(schemas.PROTOCOL_AUTHORIZATION)}).definition)
        raw = 'synthetic-opaque'
        with self.assertRaises(security.SecretRejected):
            publication.safe_bytes({'authorization': raw},
                schema=changed, schema_identity=original.identity)

    def test_credential_rename_cannot_downgrade(self):
        for name in ('authorization', 'innocent_description'):
            schema = self.schema({name: schemas.field(schemas.CREDENTIAL_HEADER)})
            self.reject({name: 'synthetic-opaque'}, schema, 'synthetic-opaque')

    def test_protocol_schema_cannot_bypass_value_detection(self):
        schema = self.schema({'authorization': schemas.field(schemas.PROTOCOL_AUTHORIZATION)})
        for raw in ('Basic ' + 'E' * 24, 'ghp_' + 'F' * 30,
                    '-----BEGIN ' + 'PRIVATE KEY-----', 'PASSWORD' + '="synthetic-hidden"'):
            self.reject({'authorization': raw}, schema, raw)

    def test_marked_secret_remains_rejected_in_public_schema(self):
        schema = self.schema({'sensitive': schemas.field(value_type='boolean'), 'value': schemas.field()})
        self.reject({'sensitive': True, 'value': 'synthetic-marked'}, schema, 'synthetic-marked')

    def test_schema_missing_pin_and_extra_fields_reject(self):
        schema = self.schema({'authorization': schemas.field(schemas.PROTOCOL_AUTHORIZATION)})
        policy_id = 'ordinary'
        with self.assertRaises(security.SecretRejected):
            publication.safe_bytes({'authorization': policy_id}, schema=schema)
        with self.assertRaises(security.SecretRejected):
            self.publish({'authorization': policy_id, 'extra': 'ordinary'}, schema)

    def test_fixture_class_never_publishable(self):
        schema = self.schema({'input': schemas.field(schemas.SYNTHETIC_SECURITY_FIXTURE)})
        self.reject({'input': 'synthetic-ordinary'}, schema, 'synthetic-ordinary')


if __name__ == '__main__':
    unittest.main()
