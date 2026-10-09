"""Minimal stdio MCP server: one inert, literal-only preflight tool."""
import json
import sys

TOOL = dict(name='inert_echo', description='Echo the literal neutral; no effects.',
    inputSchema=dict(type='object', properties={'value': {'type': 'string', 'enum': ['neutral']}},
                     required=['value'], additionalProperties=False))

for line in sys.stdin:
    request = json.loads(line)
    if 'id' not in request:
        continue
    method = request.get('method')
    if method == 'initialize':
        result = dict(protocolVersion=request['params']['protocolVersion'],
                      capabilities={'tools': {}}, serverInfo={'name': 'r634-inert', 'version': '1'})
    elif method == 'tools/list':
        result = {'tools': [TOOL]}
    elif method == 'tools/call':
        args = request.get('params', {})
        ok = args.get('name') == 'inert_echo' and args.get('arguments') == {'value': 'neutral'}
        result = dict(content=[{'type': 'text', 'text': 'neutral' if ok else 'INVALID_INERT_ARGUMENTS'}],
                      isError=not ok)
    else:
        print(json.dumps(dict(jsonrpc='2.0', id=request['id'], error={'code': -32601, 'message': 'Unknown method'})), flush=True)
        continue
    print(json.dumps(dict(jsonrpc='2.0', id=request['id'], result=result)), flush=True)
