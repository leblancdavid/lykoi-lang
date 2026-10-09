"""Versioned provider-neutral envelope; atomic, nonsemantic normalization."""
import copy
import json
import re

class TransportError(ValueError):
    pass

def strict_loads(text, allow_provider_numbers=False):
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out:
                raise TransportError('duplicate JSON key: ' + k)
            out[k] = v
        return out
    def bad(value):
        raise TransportError('noninteger JSON number: ' + value)
    return json.loads(text, object_pairs_hook=pairs, parse_float=float if allow_provider_numbers else bad, parse_constant=bad)

def normalize(calls, provider, model, turn, authorized, seen):
    if provider not in ('ollama', 'openai-compatible'):
        raise TransportError('unsupported provider profile')
    if type(model) is not str or not model or type(turn) is not int or turn < 0:
        raise TransportError('invalid invocation context')
    if type(calls) is not list or not 1 <= len(calls) <= 24:
        raise TransportError('nonempty bounded call array required')
    # Check JSON representation, depth/size and cycles before retaining metadata.
    try:
        encoded = json.dumps(calls, allow_nan=False)
        if len(encoded) > 65536:
            raise TransportError('envelope size limit')
        strict_loads(encoded, allow_provider_numbers=True)
    except (ValueError, TypeError, RecursionError) as e:
        raise TransportError(str(e)) from e
    pending, identities, indices = [], set(), []
    for position, call in enumerate(calls):
        if type(call) is not dict or 'function' not in call:
            raise TransportError('function object required')
        if set(call) & {'name', 'arguments', 'semantic_arguments', 'provider', 'model', 'ordering'}:
            raise TransportError('ambiguous envelope fields')
        f = call['function']
        if type(f) is not dict or not {'name', 'arguments'} <= set(f):
            raise TransportError('name and arguments required')
        if type(f['name']) is not str or not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,63}', f['name']):
            raise TransportError('malformed function name')
        if f['name'] not in authorized:
            raise TransportError('unauthorized function: ' + f['name'])
        if 'type' in call and call['type'] != 'function':
            raise TransportError('unsupported call type')
        if provider == 'openai-compatible' and (call.get('type') != 'function' or 'id' not in call or 'index' in f):
            raise TransportError('openai-compatible profile requires type/id; no Ollama function.index')
        supplied = call.get('id')
        if 'id' in call and (type(supplied) is not str or not supplied or len(supplied) > 256):
            raise TransportError('invalid tool-call identity')
        identity = supplied if supplied is not None else f'host:{turn}:{position}'
        key = (provider, model, identity)
        if key in seen or key in identities:
            raise TransportError('duplicate call identity')
        identities.add(key)
        if 'index' in f:
            if type(f['index']) is not int or f['index'] < 0:
                raise TransportError('invalid function.index')
            indices.append((position, f['index']))
        args = f['arguments']
        if provider == 'openai-compatible':
            if type(args) is not str:
                raise TransportError('openai-compatible arguments must be JSON string')
            args = strict_loads(args)
        elif type(args) is not dict:
            raise TransportError('Ollama arguments must be object')
        if type(args) is not dict:
            raise TransportError('semantic argument object required')
        pending.append(dict(version='tool-envelope-1', provider=provider, model=model,
            call_id=identity, provider_call_id=supplied, function_name=f['name'],
            semantic_arguments=copy.deepcopy(args),
            provider_metadata=dict(envelope={k: copy.deepcopy(v) for k, v in call.items() if k not in ('id', 'function')},
                function={k: copy.deepcopy(v) for k, v in f.items() if k not in ('name', 'arguments')}),
            ordering=dict(turn=turn, position=position, provider_index=f.get('index'))))
    if indices and (len(indices) != len(calls) or any(p != i for p, i in indices)):
        raise TransportError('partial, duplicate or contradictory provider indices')
    seen.update(identities)
    return pending

def semantic_call(envelope):
    return {'function': {'name': envelope['function_name'], 'arguments': copy.deepcopy(envelope['semantic_arguments'])}}

def feedback(envelope, response):
    result = dict(role='tool', tool_name=envelope['function_name'], content=json.dumps(response, separators=(',', ':')))
    if envelope['provider_call_id'] is not None:
        result['tool_call_id'] = envelope['provider_call_id']
    return result
