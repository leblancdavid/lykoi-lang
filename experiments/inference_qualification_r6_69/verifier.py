"""Strict namespace-aware comparison of byte-exact frozen tensor fingerprints."""
import re


class IdentityError(ValueError):
    pass


def normalize_name(name, wrapped):
    if type(name) is not str:
        raise IdentityError('non-string tensor name')
    marker = ''
    for prefix in ('buffer:', 'quant_state:'):
        if name.startswith(prefix):
            marker, name = prefix, name[len(prefix):]
            break
    if wrapped:
        if not name.startswith('base_model.model.'):
            raise IdentityError('missing explicit PEFT wrapper namespace: ' + name)
        name = name[len('base_model.model.'):]
        # Only the two frozen LoRA target module families may introduce base_layer.
        name = re.sub(r'^(model\.layers\.[0-9]+\.self_attn\.(?:q_proj|v_proj))\.base_layer\.', r'\1.', name)
    if 'base_layer' in name or 'base_model' in name or 'lora_' in name:
        raise IdentityError('unexpected/ambiguous wrapper namespace: ' + name)
    if not name.startswith(('model.', 'lm_head.')):
        raise IdentityError('unexpected base module name: ' + name)
    return marker + name


def normalize(manifest, wrapped):
    entries = manifest.items() if type(manifest) is dict else manifest
    result, mappings = {}, []
    for name, record in entries:
        normalized = normalize_name(name, wrapped)
        if normalized in result:
            raise IdentityError('duplicate normalized tensor: ' + normalized)
        result[normalized] = record
        mappings.append(dict(original=name, normalized=normalized))
    if not result:
        raise IdentityError('empty manifest')
    return result, mappings


def compare(actual, expected, actual_wrapped, expected_wrapped=True):
    current, mappings = normalize(actual, actual_wrapped)
    reference, _ = normalize(expected, expected_wrapped)
    if current.keys() != reference.keys():
        raise IdentityError('tensor mapping coverage differs: missing=' + str(sorted(reference.keys()-current.keys())) +
                            ' unexpected=' + str(sorted(current.keys()-reference.keys())))
    for name in reference:
        # Frozen tensor records contain raw-byte SHA256, exact shape and dtype.
        # Quantization-state records additionally include their nested tensors/scalars.
        if current[name] != reference[name]:
            raise IdentityError('tensor shape/dtype/byte-content or quantization state differs: ' + name)
    return dict(passed=True, entries=len(current), mappings=mappings,
                comparison='Exact record equality: tensor shape, dtype, raw-byte SHA256 and complete quantization state; no tolerance or count-only acceptance')


def compare_adapter(actual, expected):
    if not actual or actual.keys() != expected.keys() or actual != expected:
        raise IdentityError('adapter tensor identity differs')
    if any('lora_' not in name for name in actual):
        raise IdentityError('unexpected non-adapter tensor')
    return dict(passed=True, tensors=len(actual), namespace_normalized=False)
