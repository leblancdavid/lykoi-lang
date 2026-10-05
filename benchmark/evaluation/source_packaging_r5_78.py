"""Pure, deterministic structural packaging; no protected I/O or evaluation."""
import hashlib

from benchmark.evaluation import benchmark_documents_v1 as v1


class PackagingError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)

    def record(self):
        return {'code': self.code}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def transform(interface, resources):
    """Return package bytes and safe receipt; caller keeps bytes contained."""
    if interface not in ('explicit-components', 'frozen-request-bundle'):
        raise PackagingError('UNSUPPORTED_SOURCE_INTERFACE')
    expected = {'components'} if interface == 'explicit-components' else {'request', 'profile', 'capability'}
    if type(resources) is not dict or set(resources) != expected or any(
            type(raw) is not bytes for raw in resources.values()):
        raise PackagingError('MALFORMED_SOURCE')
    provenance = v1.identity({'interface': interface,
                             'resources': {name: digest(raw) for name, raw in sorted(resources.items())}})
    try:
        if interface == 'frozen-request-bundle':
            if not resources['request'].decode('utf-8').strip() or any(
                    type(v1.parse(resources[name])) is not dict for name in ('profile', 'capability')):
                raise PackagingError('MALFORMED_SOURCE')
            raise PackagingError('UNREPRESENTABLE_SOURCE')
        source = v1.parse(resources['components'])
    except (v1.DocumentError, UnicodeError):
        raise PackagingError('MALFORMED_SOURCE') from None
    try:
        payload = v1.normalize_payload(source)
        document = {'schema_version': v1.VERSION,
                    'document_id': 'behavioral-' + v1.identity(payload),
                    'role': 'behavioral', 'payload': payload}
        document_commitment = v1.validate_document(document)
        body = {'schema_version': v1.CONTRACT, **payload}
        raw = v1.canonical([document])
    except (v1.DocumentError, TypeError, ValueError, RecursionError):
        raise PackagingError('INVALID_V1_STRUCTURE') from None
    return raw, {'schema_version': v1.VERSION, 'package_identity': digest(raw),
                 'package_commitment': digest(raw), 'behavioral_commitment': v1.identity(body),
                 'document_commitment': document_commitment, 'provenance_identity': provenance,
                 'behavioral_documents': 1, 'metadata_documents': 0,
                 'status': 'VALIDATED_NOT_SEALED'}
