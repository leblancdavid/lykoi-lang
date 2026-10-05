"""Producer-owned, content-bound publication schemas; never payload declarations."""

from dataclasses import dataclass
import json

from benchmark.evaluation.recorder_r5_43 import canonical, digest

PUBLIC_METADATA = 'PUBLIC_METADATA'
PROTOCOL_IDENTITY = 'PROTOCOL_IDENTITY'
PROTOCOL_AUTHORIZATION = str('PROTOCOL_AUTHORIZATION')
CONTENT_IDENTITY = 'CONTENT_IDENTITY'
SECRET_REFERENCE = 'SECRET_REFERENCE'
SECRET_VALUE = 'SECRET_VALUE'
CREDENTIAL_HEADER = 'CREDENTIAL_HEADER'
SYNTHETIC_SECURITY_FIXTURE = 'SYNTHETIC_SECURITY_FIXTURE'
PUBLIC = frozenset((PUBLIC_METADATA, PROTOCOL_IDENTITY, PROTOCOL_AUTHORIZATION,
                    CONTENT_IDENTITY))
CLASSES = PUBLIC | {SECRET_REFERENCE, SECRET_VALUE, CREDENTIAL_HEADER,
                    SYNTHETIC_SECURITY_FIXTURE}
TYPES = {'object': dict, 'string': str, 'boolean': bool}


@dataclass(frozen=True)
class PublicationSchema:
    definition: bytes

    @classmethod
    def declare(cls, definition):
        return cls(canonical(definition))

    @property
    def identity(self):
        return digest(self.definition)

    def resolve(self, trusted_identity):
        # The pin belongs to reviewed producer code, not the document being published.
        if self.identity != trusted_identity:
            raise ValueError('publication schema identity changed')
        tree = json.loads(self.definition)
        def validate(node):
            if (type(node) is not dict or node.get('classification') not in CLASSES or
                    node.get('type') not in TYPES):
                raise ValueError('invalid publication schema')
            if node['type'] == 'object':
                if set(node) != {'classification', 'type', 'fields', 'optional'}:
                    raise ValueError('invalid object schema')
                if (type(node['fields']) is not dict or type(node['optional']) is not list or
                        any(k not in node['fields'] for k in node['optional'])):
                    raise ValueError('invalid schema membership')
                for child in node['fields'].values():
                    validate(child)
            elif set(node) != {'classification', 'type'}:
                raise ValueError('invalid scalar schema')
        validate(tree)
        return tree


def field(classification=PUBLIC_METADATA, value_type='string'):
    return {'classification': classification, 'type': value_type}


def object_schema(fields, *, classification=PUBLIC_METADATA, optional=()):
    return {'classification': classification, 'type': 'object',
            'fields': fields, 'optional': list(optional)}


QUALIFICATION_IDENTITY = PublicationSchema.declare(object_schema({
    'experiment': field(PROTOCOL_IDENTITY),
    'authorization': field(PROTOCOL_AUTHORIZATION),
    **{name: field(CONTENT_IDENTITY) for name in
       ('plan', 'authority', 'registry', 'exclusion', 'orchestration', 'identity')},
    **{name: field(PROTOCOL_IDENTITY) for name in
       ('bounded_driver', 'mediated_worker_policy', 'resource_policy')},
    'fresh_receipts_only': field(value_type='boolean'),
    'state_binding': field(),
}, optional=('identity',)))
QUALIFICATION_IDENTITY_PIN = '7f64658a8ae32c17feecb6dcda2d5cfe4587b1663534e465274dd27c92749a9c'
