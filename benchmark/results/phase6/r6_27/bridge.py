"""Neutral stdio MCP server; never constructs or executes a symbolic program."""
import json
import sys
import traceback
from common import HERE, save, tools, transport
from adapter import publish, validate

def obj(props, required=None):
    return dict(type='object', properties=props, required=list(props) if required is None else required,
                additionalProperties=False)

A = obj({'kind': {'const': 'alpha'}, 'count': {'type': 'integer'}})
B = obj({'kind': {'const': 'beta'}, 'text': {'type': 'string'}})
SCHEMAS = {
    'simple': obj({'text': {'type': 'string'}}),
    'nested': obj({'payload': obj({'count': {'type': 'integer'}})}),
    'required': obj({'count': {'type': 'integer'}}),
    'optional': obj({'text': {'type': 'string'}, 'note': {'type': 'string'}}, ['text']),
    'enum': obj({'color': {'enum': ['red', 'blue']}}),
    'root_union': {'oneOf': [A, B]},
    'typed_root_union': {'type': 'object', 'oneOf': [A, B]},
    'nested_union': obj({'payload': {'oneOf': [A, B]}}),
    'discriminator': {'type': 'object', 'oneOf': [A, B], 'discriminator': {'propertyName': 'kind'}},
}

def definitions(mode):
    if mode in ('exact', 'original', 'exact-neutral'):
        prefix = 'R6.27 inert qualification endpoint: ONLY validates arguments and returns an echo. No construction, mutation, finalization, expansion or execution occurs. Historical semantic description follows as a read-only fixture, not sandbox behavior: ' if mode == 'exact-neutral' else ''
        return [dict(name=t['function']['name'], description=prefix + t['function']['description'],
                     inputSchema=publish(t['function']['parameters']) if mode != 'original' else t['function']['parameters'])
                for t in tools.definitions(['value', 'check', 'compose'])]
    keys = ['simple', 'nested', 'required', 'optional', 'enum', 'typed_root_union', 'nested_union', 'discriminator'] if mode == 'synthetic' else [mode]
    return [dict(name=k, description='Inert echo; validates exact synthetic arguments. No effects.', inputSchema=SCHEMAS[k]) for k in keys]

def handle(request, mode, seen):
    method = request.get('method')
    if method == 'initialize':
        return dict(protocolVersion=request['params']['protocolVersion'], capabilities={'tools': {}}, serverInfo={'name': 'r627-neutral', 'version': '1'})
    if method == 'tools/list':
        return {'tools': definitions(mode)}
    if method == 'ping':
        return {}
    if method != 'tools/call':
        raise ValueError('Unsupported method')
    p = request['params']
    schemas = {t['name']: t['inputSchema'] for t in definitions(mode)}
    if mode in ('exact', 'exact-neutral'):
        schemas = {t['function']['name']: t['function']['parameters'] for t in tools.definitions(['value', 'check', 'compose'])}
    native = dict(id='mcp:' + str(request['id']), type='function', function=dict(name=p['name'], arguments=json.dumps(p.get('arguments'))))
    try:
        envelope = transport.normalize([native], 'openai-compatible', 'gpt-6.1-sol', len(seen), schemas, seen)[0]
        validate(schemas[envelope['function_name']], envelope['semantic_arguments'])
        response = dict(ok=True, inert=True, tool=p['name'], echoed=envelope['semantic_arguments'])
        error = False
    except Exception as exc:
        response = dict(ok=False, error={'code': 'ARGUMENT_SCHEMA', 'exception': type(exc).__name__, 'detail': str(exc)[:700]})
        error = True
    return dict(content=[dict(type='text', text=json.dumps(response))], structuredContent=response, isError=error)

def main():
    label, mode = sys.argv[1:3]
    directory = HERE / label
    assert directory.is_dir()
    seen = set()
    for line in sys.stdin:
        request = transport.strict_loads(line, allow_provider_numbers=True)
        if 'id' not in request:
            continue
        try:
            response = dict(jsonrpc='2.0', id=request['id'], result=handle(request, mode, seen))
        except Exception as exc:
            response = dict(jsonrpc='2.0', id=request['id'], error={'code': -32602, 'message': str(exc)})
        with (directory / 'MCP.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(dict(request=request, response=response)) + '\n')
        print(json.dumps(response), flush=True)

if __name__ == '__main__':
    main()
