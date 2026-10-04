"""Prospective secret-safe publication boundary, separate from historical writers."""

import hashlib
import hmac
import json
from pathlib import Path
import re

from benchmark.evaluation.recorder_r5_43 import Recorder, canonical, persist as historical_persist

REDACTED = '[REDACTED]'
PROTOCOL = 'lykoi-secret-publication-r5.47'
SENSITIVE = re.compile(r'(?:^|[_-])(?:api[_-]?key|token|access[_-]?token|refresh[_-]?token|password|passwd|secret|credentials?|authorization|connection[_-]?string|private[_-]?key)$', re.I)
TOKEN = re.compile(r'(?:\b(?:sk|ghp|github_pat|xox[baprs]|AKIA)[-_A-Za-z0-9]{16,}|\beyJ[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}\.[A-Za-z0-9_-]{12,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|\b(?:Bearer|Basic)\s+[A-Za-z0-9+/=_-]{12,}|[a-z][a-z0-9+.-]*://[^\s/:]+:[^\s/@]+@)', re.I)
ASSIGNMENT = re.compile(r'(?im)["\']?([A-Za-z_][A-Za-z0-9_.-]*)["\']?\s*[:=]\s*["\']([^"\'\r\n]+)["\']')
UNQUOTED = re.compile(r'(?im)^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*([^\s\'"()\[\]{},]+)\s*$')
SAFE_FIELD = re.compile(r'^[A-Za-z_][A-Za-z0-9_.-]{0,79}$')


class SecretRejected(ValueError):
    """Diagnostics never contain the rejected value or arbitrary user key/path."""

    def __init__(self, category, field=None):
        self.category = category
        self.field = field if field and SAFE_FIELD.fullmatch(field) and not TOKEN.search(field) else '[REDACTED]'
        super().__init__('SECRET_VALUE_REJECTED: ' + category + ' field ' + self.field)


def safe_representation(value):
    if value == REDACTED or value is None:
        return True
    if type(value) is not dict:
        return False
    if set(value) == {'present'}:
        return type(value['present']) is bool
    return (set(value) == {'present', 'scheme', 'key_id', 'fingerprint'} and
            value['present'] is True and value['scheme'] == 'hmac-sha256-r5.47' and
            type(value['key_id']) is str and SAFE_FIELD.fullmatch(value['key_id']) is not None and
            type(value['fingerprint']) is str and re.fullmatch('[0-9a-f]{64}', value['fingerprint']) is not None)


def check_text(text):
    if TOKEN.search(text):
        raise SecretRejected('credential-shaped text')
    for match in ASSIGNMENT.finditer(text):
        if SENSITIVE.search(match[1]) and match[2] != REDACTED:
            raise SecretRejected('credential assignment', match[1])
    for match in UNQUOTED.finditer(text):
        if SENSITIVE.search(match[1]) and match[2].strip().strip('"\'') != REDACTED:
            raise SecretRejected('credential assignment', match[1])


def inspect(value):
    """Reject credential fields, marked structures and credential-bearing text.

    This is a contextual detector, not an entropy classifier or omniscient DLP.
    Producers must still use typed publication/presence metadata, never raw dumps.
    """
    if type(value) is dict:
        marked = value.get('secret') is True or value.get('sensitive') is True
        for key, child in value.items():
            if type(key) is not str:
                raise SecretRejected('invalid publication key')
            check_text(key)
            if (SENSITIVE.search(key) and not (key == 'secret' and child is True)) or (marked and key == 'value'):
                if not safe_representation(child):
                    raise SecretRejected('secret-marked structure' if marked else 'credential field', key)
            inspect(child)
    elif type(value) in (list, tuple):
        for child in value:
            inspect(child)
    elif type(value) is str:
        check_text(value)


def safe_bytes(value):
    # Validate canonical types/cycles before recursive inspection. Do not publish
    # canonicalizer exception details, which may originate in arbitrary input.
    try:
        content = canonical(value)
    except ValueError:
        raise SecretRejected('invalid canonical publication') from None
    inspect(value)
    return content


def persist(path, value):
    safe_bytes(value)  # Check before creating even an empty output file.
    historical_persist(path, value)


def report(path, value):
    content = safe_bytes(value)
    with Path(path).open('xb') as stream:
        stream.write(content + b'\n')


class PublicationRecorder(Recorder):
    """R5.43 lifecycle with prospective publication checks, not a certificate."""

    def write(self, name, value):
        persist(self.path(name), value)

    def halt(self, reason):
        # Callback/OSError exception text is untrusted and can contain a secret.
        # Keep only the violation category, not arbitrary exception strings.
        category = str(reason) if isinstance(reason, SecretRejected) else 'publication operation failed; details withheld'
        super().halt(category)

    def observe(self, callback):
        try:
            return super().observe(callback)
        except Exception:
            raise SecretRejected('observation rejected; details withheld') from None


def secret_identity(name, value, *, material=False, key=None, key_id=None):
    """Presence by default; keyed identity only for explicitly material secrets.

    Key custody/worker propagation are future qualification obligations. Never
    persist key bytes. A public salt or plain digest is not an accepted scheme.
    """
    if value is None or not material:
        return {'present': value is not None}
    if (type(key) is not bytes or len(key) < 32 or type(key_id) is not str or
            not SAFE_FIELD.fullmatch(key_id) or TOKEN.search(key_id)):
        raise SecretRejected('external identity key required')
    message = canonical([PROTOCOL, name, value])
    return {'present': True, 'scheme': 'hmac-sha256-r5.47', 'key_id': key_id,
            'fingerprint': hmac.new(key, message, hashlib.sha256).hexdigest()}


def publication_environment(environment):
    # Narrow public enum/control values only; PATH and other free text are not
    # automatically public just because a variable name is familiar.
    controls = {'PYTHONDONTWRITEBYTECODE': {'0', '1'}, 'PYTHONUTF8': {'0', '1'},
                'OS': {'Windows_NT'}, 'PROCESSOR_ARCHITECTURE': {'AMD64', 'ARM64', 'x86'}}
    result = {}
    for name, value in environment.items():
        if name in controls and value in controls[name]:
            result[name] = value
        else:
            result[name] = secret_identity(name, value)
    safe_bytes(result)
    return result


def scan_content(content):
    """Return only redacted diagnostic categories; used on Git blobs in memory."""
    text = content.decode('utf-8', errors='replace')
    findings = []
    try:
        check_text(text)
    except SecretRejected as exc:
        findings.append(str(exc))
    try:
        value = json.loads(text)
    except (ValueError, RecursionError):
        value = None
    if value is not None:
        try:
            safe_bytes(value)
        except SecretRejected as exc:
            findings.append(str(exc))
    return sorted(set(findings))
