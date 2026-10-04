"""Publish environment metadata without publishing credential values."""

import json
from pathlib import Path
import re


REDACTED = '[REDACTED]'
# Unknown application variables are private by default. This is metadata,
# not a complete effective-environment identity or runtime attestation.
PUBLIC_VARIABLES = frozenset({
    'OS', 'PATH', 'PATHEXT', 'PYTHONPATH', 'PYTHONDONTWRITEBYTECODE',
    'PYTHONHASHSEED', 'PYTHONUTF8', 'PYTHONIOENCODING',
    'PROCESSOR_ARCHITECTURE', 'PROCESSOR_IDENTIFIER', 'PROCESSOR_LEVEL',
    'PROCESSOR_REVISION', 'NUMBER_OF_PROCESSORS',
    'SYSTEMROOT', 'SYSTEMDRIVE', 'TEMP', 'TMP',
})
SENSITIVE_NAME = re.compile(r'key|token|secret|password|credential|authorization', re.I)


def public_environment(environment):
    return {name: value if name.upper() in PUBLIC_VARIABLES else REDACTED
            for name, value in sorted(environment.items())}


def redact_snapshot(path):
    """Redact historical credential fields without resealing historical evidence.

    The original identity is deliberately retained: this edited snapshot must
    fail integrity verification rather than impersonate the original evidence.
    """
    path = Path(path)
    text = path.read_text(encoding='utf-8')
    snapshot = json.loads(text)
    environment = snapshot['configuration']['environment']
    names = [name for name, value in environment.items()
             if SENSITIVE_NAME.search(name) and value != REDACTED]
    # Replace only the environment member's serialized key/value pair so all
    # other bytes, including historical identities, remain untouched.
    for name in names:
        old = json.dumps(name) + ':' + json.dumps(environment[name])
        new = json.dumps(name) + ':' + json.dumps(REDACTED)
        if text.count(old) != 1:
            raise ValueError('expected one canonical environment member: ' + name)
        text = text.replace(old, new, 1)
    path.write_bytes(text.encode('utf-8'))
    return names


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('snapshot', type=Path)
    args = parser.parse_args()
    print({'redacted_fields': redact_snapshot(args.snapshot)})
