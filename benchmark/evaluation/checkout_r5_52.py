"""Read-only checkout diagnostics; historical raw byte locks retain their meaning.

No subject loader, readiness call, observation reservation or production gate.
Authority reconstruction is accepted only when its SHA-256 equals the saved pin.
"""

import hashlib
import subprocess
from pathlib import Path


PROTOCOL = 'lykoi-checkout-reconciliation-r5.52-v1'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def normalize(data):
    return data.replace(b'\r\n', b'\n').replace(b'\r', b'\n')


def text(data):
    try:
        data.decode('utf-8')
        return b'\0' not in data
    except UnicodeDecodeError:
        return False


def endings(data):
    crlf = data.count(b'\r\n')
    lf = data.count(b'\n') - crlf
    cr = data.count(b'\r') - crlf
    forms = [name for name, count in [('CRLF', crlf), ('LF', lf), ('CR', cr)] if count]
    return {'form': '+'.join(forms) or 'NONE', 'crlf': crlf, 'lf': lf, 'cr': cr}


def classify(authority, checkout, *, unexpected=False):
    if unexpected:
        return 'UNEXPECTED'
    if checkout is None:
        return 'MISSING'
    if authority is None:
        return 'UNCLASSIFIED'
    if authority == checkout:
        return 'BYTE_IDENTICAL'
    if text(authority) and text(checkout) and normalize(authority) == normalize(checkout):
        return 'LINE_ENDING_ONLY'
    return 'CONTENT_DIFFERENT'


def git(root, *args, input=None):
    return subprocess.check_output(['git', '--no-replace-objects', '-c', 'core.fsmonitor=false',
                                   *args], cwd=root, input=input, timeout=60)


def blobs(root, identities):
    identities = sorted(set(identities))
    raw = git(root, 'cat-file', '--batch', input=('\n'.join(identities) + '\n').encode())
    result, offset = {}, 0
    for identity in identities:
        end = raw.index(b'\n', offset)
        header = raw[offset:end].split()
        if len(header) != 3 or header[1] != b'blob':
            raise ValueError('authority blob unavailable')
        length = int(header[2])
        result[identity] = raw[end + 1:end + 1 + length]
        offset = end + 2 + length
    if offset != len(raw):
        raise ValueError('invalid blob framing')
    return result


def tree(root, revision):
    result = {}
    for row in git(root, 'ls-tree', '-r', '-z', revision).split(b'\0'):
        if row:
            meta, name = row.split(b'\t', 1)
            mode, kind, identity = meta.decode().split()
            if kind == 'blob':
                result[name.decode()] = {'mode': mode, 'blob': identity}
    return result


def recover(expected, candidates):
    """Recover physical authority from versioned blobs, proving the *raw* pin.

    Trying known Git LF/CRLF representations does not qualify or rewrite a lock.
    No arbitrary content repair or fuzzy diff is permitted.
    """
    for reference, data in candidates:
        forms = [('repository', data)]
        if text(data):
            forms += [('LF materialization', normalize(data)),
                      ('CRLF materialization', normalize(data).replace(b'\n', b'\r\n'))]
        for representation, value in forms:
            if sha(value) == expected:
                return value, {'reference': reference, 'representation': representation,
                               'exact_pin_recovered': True}
    return None, {'exact_pin_recovered': False}


def recover_mixed(expected, candidates):
    """Diagnose mixed newline materialization, still requiring exact pinned hash.

    Historical incremental patches can leave old lines CRLF and new lines LF.
    A digest match proves recovered content; the reconstruction is NOT evidence
    that a particular editing tool produced it.
    """
    import difflib
    for reference, data in candidates:
        if not text(data):
            continue
        lines = normalize(data).splitlines(keepends=True)
        for empty_crlf in (False, True):
            for nonempty_crlf in (False, True):
                value = b''.join(line.replace(b'\n', b'\r\n') if
                    (nonempty_crlf if line.strip() else empty_crlf) else line for line in lines)
                if sha(value) == expected:
                    return value, {'reference': reference, 'representation': 'mixed blank-line representation',
                        'empty_crlf': empty_crlf, 'nonempty_crlf': nonempty_crlf, 'exact_pin_recovered': True}
        for split in range(len(lines) + 1):
            for prefix_crlf in (True, False):
                value = b''.join(line.replace(b'\n', b'\r\n') if (i < split) == prefix_crlf else line
                                 for i, line in enumerate(lines))
                if sha(value) == expected:
                    return value, {'reference': reference, 'representation': 'mixed LF/CRLF',
                        'split': split, 'prefix_crlf': prefix_crlf, 'exact_pin_recovered': True}
    # Reconstruct successive textual patches, preserving equal-line terminators.
    chronological = list(reversed(candidates))
    for context in (0, 1, 2, 3, 4, 5):
        for start in range(len(chronological)):
            previous = None
            for reference, data in chronological[start:]:
                lines = normalize(data).splitlines(keepends=True)
                if previous is None:
                    value = normalize(data).replace(b'\n', b'\r\n')
                else:
                    old = previous.splitlines(keepends=True)
                    matcher = difflib.SequenceMatcher(None, [normalize(x) for x in old], lines, autojunk=False)
                    parts, offset = [], 0
                    for group in matcher.get_grouped_opcodes(context):
                        a, c = group[0][1], group[0][3]
                        b, d = group[-1][2], group[-1][4]
                        parts.extend(old[offset:a])
                        parts.extend(lines[c:d])
                        offset = b
                    parts.extend(old[offset:])
                    value = b''.join(parts)
                if sha(value) == expected:
                    return value, {'reference': reference, 'representation': 'mixed incremental patch reconstruction',
                                   'base': chronological[start][0], 'context_lines': context, 'exact_pin_recovered': True}
                previous = value
    return None, {'exact_pin_recovered': False}


def attributes(root, names):
    raw = git(root, 'check-attr', '-z', '--stdin', 'text', 'eol', 'filter',
              'working-tree-encoding', input=b'\0'.join(n.encode() for n in names) + b'\0')
    fields = raw.rstrip(b'\0').decode().split('\0')
    result = {}
    for offset in range(0, len(fields), 3):
        name, key, value = fields[offset:offset + 3]
        result.setdefault(name, {})[key] = value
    return result


def disposition(category, *, decision=None, before=None, after=None):
    """Explicit decision + identities required for successor acceptance."""
    if category == 'AUTHORIZED_SUCCESSOR_CHANGE':
        if not decision or not before or not after:
            raise ValueError('untraced successor change')
    elif category not in {'EXPECTED_GENERATED_CHANGE', 'LINE_ENDING_MATERIALIZATION',
                          'UNAUTHORIZED_CHANGE', 'UNKNOWN'}:
        raise ValueError('unknown disposition')
    return {'category': category, 'decision': decision, 'before': before, 'after': after}


def candidate_identity(repository, checkout, frozen):
    """Synthetic design witness only; NOT a production successor lock issuer."""
    import json
    value = {'protocol': 'lykoi-repository-checkout-lock-r5.52-design-v1',
             'repository_content': repository, 'checkout_materialization': checkout,
             'historical_frozen_pins': frozen}
    return sha(json.dumps(value, sort_keys=True, separators=(',', ':')).encode())
