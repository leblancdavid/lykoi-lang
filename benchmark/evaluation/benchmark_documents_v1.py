"""Prospective V1 document adapter. No support decisions, I/O or AI inference."""
import hashlib
import json

from benchmark.semantic import profile_audit_r5_41 as component_schema

VERSION = 'BenchmarkDocumentContractV1'
CONTRACT = 'BehavioralContractV1'
ROLES = ('behavioral', 'metadata')


class DocumentError(ValueError):
    def __init__(self, code, path=()):
        self.code, self.path = code, list(path)
        super().__init__(code)

    def record(self):
        return {'code': self.code, 'path': self.path}


def require(condition, code, path=()):
    if not condition:
        raise DocumentError(code, path)


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'),
                          ensure_ascii=False, allow_nan=False).encode('utf-8')
    except (ValueError, TypeError, UnicodeError, RecursionError):
        raise DocumentError('MALFORMED_DOCUMENT') from None


def identity(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def parse(raw):
    def pairs(items):
        require(len(dict(items)) == len(items), 'MALFORMED_DOCUMENT')
        return dict(items)
    try:
        if type(raw) is bytes:
            raw = raw.decode('utf-8')
        require(type(raw) is str, 'MALFORMED_DOCUMENT')
        value = json.loads(raw, object_pairs_hook=pairs,
                           parse_constant=lambda _: require(False, 'MALFORMED_DOCUMENT'))
        canonical(value)
        return value
    except (ValueError, TypeError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, DocumentError):
            raise
        raise DocumentError('MALFORMED_DOCUMENT') from None


def text(value):
    return type(value) is str and bool(value.strip())


def json_value(value):
    # Dict keys must be strings even for the object API; no Python-only values.
    require(type(value) in (dict, list, str, int, float, bool, type(None)), 'MALFORMED_DOCUMENT')
    if type(value) is dict:
        for key, child in value.items():
            require(type(key) is str, 'MALFORMED_DOCUMENT')
            json_value(child)
    elif type(value) is list:
        for child in value:
            json_value(child)


def normalize_payload(payload):
    require(type(payload) is dict and set(payload) == {'application', 'configuration', 'obligations'},
            'INCOMPLETE_CONTRACT' if type(payload) is dict and
            set(payload) < {'application', 'configuration', 'obligations'} else 'MALFORMED_PAYLOAD')
    app, config, entries = (payload[k] for k in ('application', 'configuration', 'obligations'))
    require(type(app) is dict and set(app) == {'id', 'state', 'operations'} and text(app.get('id'))
            and type(app.get('state')) is dict and set(app['state']) == {'versions'}
            and type(app['state']['versions']) is dict and bool(app['state']['versions'])
            and type(app.get('operations')) is dict and bool(app['operations'])
            and all(text(k) and type(v) is dict for k, v in app['operations'].items()),
            'MALFORMED_PAYLOAD', ('application',))
    try:
        component_schema.structure(config)
    except (KeyError, IndexError, AttributeError, TypeError, ValueError):
        raise DocumentError('MALFORMED_PAYLOAD', ('configuration',)) from None
    require(type(entries) is list, 'MALFORMED_PAYLOAD', ('obligations',))
    obligations = {}
    for index, entry in enumerate(entries):
        path = ('obligations', index)
        require(type(entry) is dict and set(entry) == {'id', 'requirement'} and text(entry.get('id')),
                'MALFORMED_OBLIGATION', path)
        req = entry['requirement']
        require(type(req) is dict and text(req.get('kind')), 'MALFORMED_OBLIGATION', path)
        if req['kind'] == 'public_state_alternatives':
            require(set(req) == {'kind', 'public'} and type(req['public']) is list
                    and all(text(n) for n in req['public']) and len(set(req['public'])) == len(req['public']),
                    'MALFORMED_OBLIGATION', path)
        elif req['kind'] == 'durable_content_constraints':
            require(set(req) == {'kind', 'requirements'} and type(req['requirements']) is dict
                    and all(text(k) and type(v) is list and all(type(r) is dict for r in v)
                            for k, v in req['requirements'].items()), 'MALFORMED_OBLIGATION', path)
        name = entry['id']
        if name in obligations:
            raise DocumentError('DUPLICATE_OBLIGATION' if obligations[name] == req
                                else 'CONFLICTING_OBLIGATIONS', path)
        obligations[name] = req
    return {'application': app, 'configuration': config,
            'obligations': [{'id': name, 'requirement': obligations[name]} for name in sorted(obligations)]}


def validate_document(document):
    try:
        json_value(document)
    except RecursionError:
        raise DocumentError('MALFORMED_DOCUMENT') from None
    canonical(document)
    require(type(document) is dict, 'MALFORMED_DOCUMENT')
    require(document.get('schema_version') == VERSION, 'UNSUPPORTED_SCHEMA_VERSION')
    require(set(document) in ({'schema_version', 'document_id', 'role', 'payload'},
                             {'schema_version', 'document_id', 'role', 'payload', 'metadata'}),
            'MALFORMED_DOCUMENT')
    require(text(document['document_id']), 'MALFORMED_DOCUMENT', ('document_id',))
    require(document['role'] in ROLES, 'UNKNOWN_REQUIRED_ROLE', ('role',))
    require('metadata' not in document or type(document['metadata']) is dict, 'MALFORMED_DOCUMENT')
    require(type(document['payload']) is dict, 'MALFORMED_PAYLOAD')
    if document['role'] == 'behavioral':
        normalize_payload(document['payload'])
    return identity(document)


def assemble(documents):
    """One adapter, accepting a complete set of explicit decoded V1 documents."""
    require(type(documents) is list, 'MALFORMED_DOCUMENT_SET')
    # Detach caller-owned objects and reject Python-only/noncanonical JSON values.
    for document in documents:
        validate_document(document)
    documents = [parse(canonical(d)) for d in documents]
    documents.sort(key=lambda d: d['document_id'])
    ids = [d['document_id'] for d in documents]
    require(len(ids) == len(set(ids)), 'DUPLICATE_DOCUMENT_ID')
    behavioral = [d for d in documents if d['role'] == 'behavioral']
    require(bool(behavioral), 'MISSING_REQUIRED_ROLE')
    require(len(behavioral) == 1, 'AMBIGUOUS_ASSEMBLY')
    body = {'schema_version': CONTRACT, **normalize_payload(behavioral[0]['payload'])}
    return {**body, 'identity': identity(body)}


def from_opened(opened):
    """Resource names are opaque. Every opened resource must be a V1 document."""
    require(type(opened) is dict and all(type(k) is str for k in opened), 'MALFORMED_DOCUMENT_SET')
    return assemble([parse(raw) for _, raw in sorted(opened.items())])


def verify_contract(contract):
    require(type(contract) is dict and set(contract) ==
            {'schema_version', 'application', 'configuration', 'obligations', 'identity'},
            'MALFORMED_CONTRACT')
    require(contract['schema_version'] == CONTRACT, 'UNSUPPORTED_SCHEMA_VERSION')
    payload = normalize_payload({k: contract[k] for k in ('application', 'configuration', 'obligations')})
    body = {'schema_version': CONTRACT, **payload}
    require(contract == {**body, 'identity': identity(body)}, 'MALFORMED_CONTRACT')
    return contract
