"""Identical semantic facade for both tracks; bounded read-only detail retrieval."""
import json
import os
import sys
import time
from common import ROOT, HERE, OUT, module, normalize, Registry, Journal, c
from snapshot import retrieve

legacy = module('r638_legacy_tools', ROOT / 'experiments/ai_lifecycle_r6_37/tools.py')
STORE = OUT / os.environ.get('R638_RUN', 'qualification')
legacy.STORE = STORE
legacy.PHASE = 'qualification'
TOOLS = legacy.TOOLS + [legacy.schema('lykoi_detail', 'Bounded read-only exact registry retrieval. No execution or binding changes.',
    {'identity': legacy.PIN, 'kind': {'type': 'string', 'enum': ['definition', 'dependencies', 'validation', 'history', 'identity']}}, ['identity', 'kind'])]


def main():
    STORE.mkdir(parents=True, exist_ok=True)
    for line in sys.stdin:
        request = json.loads(line)
        if 'id' not in request:
            continue
        start = time.perf_counter()
        method = request.get('method')
        if method == 'initialize':
            result = dict(protocolVersion=request['params']['protocolVersion'], capabilities={'tools': {}}, serverInfo={'name': 'lykoi-r638', 'version': '1'})
        elif method == 'tools/list':
            result = {'tools': TOOLS}
        elif method == 'tools/call':
            try:
                assert (OUT / 'TASK-FREEZE.json').exists(), 'freeze required'
                name, args = request['params']['name'], request['params']['arguments']
                if name == 'lykoi_detail':
                    c.shape(args, {'identity', 'kind'}, '$/arguments')
                    value = retrieve(Registry(STORE / 'registry', Journal(STORE / 'telemetry')), args['identity'], args['kind'])
                else:
                    value = legacy.dispatch(name, args)
                value = normalize(value)
                result = dict(content=[{'type': 'text', 'text': json.dumps(value)}], structuredContent=value if isinstance(value, dict) else {'value': value}, isError=False)
            except c.Diagnostic as exc:
                result = dict(content=[{'type': 'text', 'text': json.dumps(exc.data)}], structuredContent=exc.data, isError=True)
            except Exception as exc:
                value = dict(code='INFRASTRUCTURE', detail=type(exc).__name__ + ': ' + str(exc))
                result = dict(content=[{'type': 'text', 'text': json.dumps(value)}], structuredContent=value, isError=True)
        else:
            result = None
        response = dict(jsonrpc='2.0', id=request['id'], result=result)
        with (STORE / 'MCP.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(dict(request=request, response=response, wall_seconds=time.perf_counter()-start)) + '\n')
        print(json.dumps(response), flush=True)


if __name__ == '__main__':
    main()
