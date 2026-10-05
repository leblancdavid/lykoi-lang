"""Content-pinned synthetic test inputs, separate from secret-safe publication.

No caller-supplied designation, filename exemption, or mutable registration API.
Only sensitive assignment values explicitly marked synthetic/nonfunctional may
be consumed as test input. Every other byte remains subject to R5.47 scanning.
"""

from pathlib import Path
from types import MappingProxyType

from benchmark.evaluation import security_r5_47 as security
from benchmark.evaluation.recorder_r5_43 import digest, persist as historical_persist

SYNTHETIC_SECURITY_FIXTURE = 'SYNTHETIC_SECURITY_FIXTURE'
PUBLISHABLE_SOURCE_OR_EVIDENCE = 'PUBLISHABLE_SOURCE_OR_EVIDENCE'
ROOT = Path(__file__).resolve().parents[2]
# Reviewed, immutable repository-content designations, fixed before qualification.
DESIGNATIONS = MappingProxyType({
    'benchmark/evaluation/synthetic_fixture_r5_59.txt': '8ec35af16ec19b601c3b53aef4a0f5cdad97c276d0330c02289cfed9a220ab42',
})


def _fixture(content):
    try:
        text = content.decode('utf-8')
    except UnicodeDecodeError:
        raise security.SecretRejected('invalid synthetic fixture') from None
    values = []
    def replace(match):
        if not security.SENSITIVE.search(match[1]) or match[2] == security.REDACTED:
            return match[0]
        value = match[2]
        if not value.startswith('synthetic-') or security.TOKEN.search(value):
            raise security.SecretRejected('non-synthetic fixture assignment')
        values.append(value)
        return match[0].replace(value, security.REDACTED)
    sanitized = security.ASSIGNMENT.sub(replace, text)
    security.check_text(sanitized)
    return tuple(values)


def check_source(name, content):
    """Return input disposition; never a permission to publish fixture bytes."""
    pin = DESIGNATIONS.get(name)
    if pin is None:
        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            raise security.SecretRejected('invalid source encoding') from None
        check_text(text)
        return PUBLISHABLE_SOURCE_OR_EVIDENCE
    repository = content.replace(b'\r\n', b'\n')
    if digest(repository) != pin:
        raise security.SecretRejected('synthetic designation content mismatch')
    _fixture(repository)
    return SYNTHETIC_SECURITY_FIXTURE


def _values():
    values = []
    for name, pin in DESIGNATIONS.items():
        try:
            content = (ROOT / name).read_bytes().replace(b'\r\n', b'\n')
        except OSError:
            raise security.SecretRejected('synthetic designation unavailable') from None
        if digest(content) != pin:
            raise security.SecretRejected('synthetic designation content mismatch')
        values.extend(_fixture(content))
    return tuple(values)


def check_text(text):
    security.check_text(text)
    if any(value in text for value in _values()):
        raise security.SecretRejected('synthetic fixture leak')


def safe_bytes(value, *, schema=None, schema_identity=None):
    content = security.safe_bytes(value, schema=schema, schema_identity=schema_identity)
    if schema is None:
        check_text(content.decode('utf-8'))
    elif any(value in content.decode('utf-8') for value in _values()):
        # Typed traversal inspected every key/value. Assignment scanning of the
        # serialized document would discard context; fixture protection stays active.
        raise security.SecretRejected('synthetic fixture leak')
    return content


def persist(path, value, *, schema=None, schema_identity=None):
    safe_bytes(value, schema=schema, schema_identity=schema_identity)
    historical_persist(path, value)


def report(path, text):
    check_text(text)
    with Path(path).open('xb') as stream:
        stream.write(text.encode('utf-8'))


class PublicationRecorder(security.PublicationRecorder):
    def write(self, name, value):
        persist(self.path(name), value)
