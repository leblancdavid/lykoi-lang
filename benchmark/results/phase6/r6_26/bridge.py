"""Nonsemantic stdio MCP envelope bridge over exact frozen tool schemas."""
import json
import sys
import time
from common import HERE, tools, transport, save, now

def main():
    label, mode = sys.argv[1:3]
    operations = ['value'] if label == 'CAL' else ['value', 'check', 'compose']
    session = tools.Session(operations)
    rows, seen = [], set()
    for line in sys.stdin:
        request = transport.strict_loads(line, allow_provider_numbers=True)
        method = request.get('method')
        if 'id' not in request:
            continue
        begin = time.perf_counter()
        if method == 'initialize':
            result = dict(protocolVersion=request['params']['protocolVersion'], capabilities={'tools': {}}, serverInfo={'name': 'r626-envelope-only', 'version': '1'})
        elif method == 'tools/list':
            result = {'tools': [dict(name=t['function']['name'], description=t['function']['description'], inputSchema=t['function']['parameters']) for t in tools.definitions(operations)]}
        elif method == 'tools/call':
            p = request['params']
            native = dict(id='mcp:' + str(request['id']), type='function', function=dict(name=p['name'], arguments=json.dumps(p.get('arguments'))))
            try:
                e = transport.normalize([native], 'openai-compatible', 'gpt-6.1-sol', len(rows), session.schemas, seen)[0]
                if mode == 'neutral':
                    import jsonschema
                    jsonschema.Draft202012Validator(session.schemas[e['function_name']]).validate(e['semantic_arguments'])
                    dispatch = dict(success=True, syntax_valid=True, arguments_valid=True, response=dict(ok=True, inert=True, echoed=e['semantic_arguments']))
                else:
                    dispatch = session.dispatch(transport.semantic_call(e))
                result = dict(content=[dict(type='text', text=json.dumps(dispatch['response']))], isError=not dispatch['success'])
                rows.append(dict(request=request, native=native, normalized=e, dispatch=dispatch, feedback=transport.feedback(e, dispatch['response'])))
            except Exception as exc:
                result = dict(content=[dict(type='text', text=str(exc))], isError=True)
                rows.append(dict(request=request, native=native, error=str(exc)))
            save(label + '/INTERACTION.json', dict(timestamp=now(), rows=rows, packet=session.packet, finalized=sorted(session.finalized)))
            if session.completed:
                save(label + '/SYMBOLIC-PACKET.json', session.packet)
                save(label + '/ARTIFACT.json', session.completed['artifact'])
        elif method == 'ping':
            result = {}
        else:
            response = dict(jsonrpc='2.0', id=request['id'], error={'code': -32601, 'message': 'Unsupported method'})
            print(json.dumps(response), flush=True)
            continue
        response = dict(jsonrpc='2.0', id=request['id'], result=result)
        with (HERE / label / 'MCP.jsonl').open('a', encoding='utf-8') as f:
            f.write(json.dumps(dict(request=request, response=response, seconds=time.perf_counter()-begin)) + '\n')
        print(json.dumps(response), flush=True)

if __name__ == '__main__':
    main()
