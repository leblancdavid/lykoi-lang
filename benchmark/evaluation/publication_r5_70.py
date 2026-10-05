"""Pinned typed Python literal publication, independent of path or filename.

Only reviewed literal dictionary metadata receives schema context. Dynamic
assignments and undeclared literals retain the existing publication guard.
"""
import ast
from pathlib import Path
from benchmark.evaluation import publication_r5_59 as publication
from benchmark.evaluation import publication_schema_r5_64 as schemas
from benchmark.evaluation.recorder_r5_43 import canonical, digest, persist as historical_persist

SUMMARY_CONTEXT = schemas.PublicationSchema.declare(schemas.object_schema({
    'production_authorization': schemas.field(schemas.PROTOCOL_AUTHORIZATION)}))
SUMMARY_PIN = '8a6e9d02ba69e6b8cb9e69d265828b9722bc894d4c8aaa1a3471aa5ecc89329d'


def safe_object(value, *, schema, schema_identity):
    """Typed fields plus normally guarded remainder; no serialized context loss."""
    try:
        content = canonical(value)
        definition = schema.resolve(schema_identity)
        if type(schema) is not schemas.PublicationSchema or type(value) is not dict or definition['type'] != 'object':
            raise ValueError()
    except (ValueError, AttributeError):
        raise publication.security.SecretRejected('invalid object publication context') from None
    if value.get('secret') is True or value.get('sensitive') is True:
        publication.safe_bytes(value)  # Marked structures cannot gain public context.
    classified = {k: v for k, v in value.items() if k in definition['fields']}
    publication.safe_bytes(classified, schema=schema, schema_identity=schema_identity)
    publication.safe_bytes({k: v for k, v in value.items() if k not in definition['fields']})
    if any(v in content.decode('utf-8') for v in publication._values()):
        raise publication.security.SecretRejected('synthetic fixture leak')
    return content


def persist_object(path, value, **context):
    safe_object(value, **context)
    historical_persist(Path(path), value)


def check_python_source(content, *, trusted_source_identity, schema, schema_identity):
    raw = content.replace(b'\r\n', b'\n')
    if digest(raw) != trusted_source_identity:
        raise publication.security.SecretRejected('source context content mismatch')
    try:
        text = raw.decode('utf-8')
        tree = ast.parse(text)
        definition = schema.resolve(schema_identity)
        if (type(schema) is not schemas.PublicationSchema or definition['type'] != 'object' or
                definition['classification'] not in schemas.PUBLIC):
            raise ValueError()
    except (ValueError, SyntaxError, UnicodeError, AttributeError):
        raise publication.security.SecretRejected('invalid source publication context') from None
    # Never mask recognizable credentials or immutable fixture values, even with
    # a public schema. Inspect literals as values before context-aware masking.
    if publication.security.TOKEN.search(text) or any(v in text for v in publication._values()):
        raise publication.security.SecretRejected('credential or fixture text')
    lines = text.splitlines(keepends=True)
    def offset(node, end=False):
        line = node.end_lineno if end else node.lineno
        column = node.end_col_offset if end else node.col_offset
        return sum(len(s) for s in lines[:line - 1]) + len(lines[line - 1].encode('utf-8')[:column].decode('utf-8'))
    spans = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        marked = any(isinstance(k, ast.Constant) and k.value in ('secret', 'sensitive') and
                     isinstance(v, ast.Constant) and v.value is True
                     for k, v in zip(node.keys, node.values))
        if marked:
            for key, value in zip(node.keys, node.values):
                if isinstance(key, ast.Constant) and key.value == 'value':
                    if not isinstance(value, ast.Constant) or not publication.security.safe_representation(value.value):
                        raise publication.security.SecretRejected('secret-marked source structure')
        for key, value in zip(node.keys, node.values):
            if not (isinstance(key, ast.Constant) and type(key.value) is str and
                    publication.security.SENSITIVE.search(key.value) and
                    key.value in definition['fields'] and isinstance(value, ast.Constant)):
                continue
            field = definition['fields'][key.value]
            if field['classification'] not in schemas.PUBLIC:
                continue
            publication.safe_bytes(value.value, schema=schemas.PublicationSchema.declare(field),
                                   schema_identity=digest(schemas.canonical(field)))
            spans.append((offset(key), offset(value, True)))
    def replace(match):
        if any(start <= match.start() and match.end() <= end for start, end in spans):
            return match[0].replace(match[2], publication.security.REDACTED)
        return match[0]
    publication.check_text(publication.security.ASSIGNMENT.sub(replace, text))
    return publication.PUBLISHABLE_SOURCE_OR_EVIDENCE
