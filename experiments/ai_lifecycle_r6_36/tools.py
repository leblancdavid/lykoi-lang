"""Four transport-only construction adapters; unchanged R6.32 semantics."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'benchmark/results/phase6/r6_36'
sys.path.insert(0, str(ROOT / 'experiments/lifecycle_r6_32'))
from lifecycle import Registry, Journal, c


def schema(name, description, properties, required):
    return dict(name=name, description=description, inputSchema=dict(type='object',
        properties=properties, required=required, additionalProperties=False))


TOOLS = [
    schema('lykoi_validate', 'Validate and expand a closed typed symbolic package.',
           {'package': {'type': 'object'}}, ['package']),
    schema('lykoi_admit', 'Explicit immutable admission or explicit caller migration.',
           {'action': {'type': 'object'}}, ['action']),
    schema('lykoi_retrieve', 'Retrieve exact immutable definition closure by SHA256 identity.',
           {'identity': {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}}, ['identity']),
    schema('lykoi_execute', 'Validate and execute a closed symbolic package on input bytes.',
           {'package': {'type': 'object'}, 'input_hex': {'type': 'string', 'pattern': '^(?:[0-9a-f]{2})*$'}},
           ['package', 'input_hex']),
]


def normalize(value):
    if isinstance(value, bytes):
        return {'bytes_hex': value.hex()}
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    return value


def dispatch(name, args):
    # Neutral preflight cannot invoke semantic operations or initialize a registry.
    if not (OUT / 'LIFECYCLE-FREEZE.json').exists():
        raise ValueError('LIFECYCLE_NOT_AUTHORIZED_BEFORE_PREFLIGHT')
    journal = Journal(OUT / 'telemetry')
    registry = Registry(OUT / 'registry', journal)
    if name == 'lykoi_validate':
        return c.expand(args['package'])
    if name == 'lykoi_retrieve':
        return registry.retrieve(pin=args['identity'])
    if name == 'lykoi_execute':
        expanded = c.expand(args['package'])
        return c.vm.execute(expanded['plan'], bytes.fromhex(args['input_hex']))
    if name == 'lykoi_admit':
        action = args['action']
        if action['action'] == 'admit':
            c.shape(action, {'action', 'definitions', 'predecessor'}, '$/action')
            for definition in action['definitions']:
                if 'identity' in definition:
                    raise ValueError('OMIT_IDENTITY_FOR_MECHANICAL_SEAL')
            return registry.admit([c.seal(d) for d in action['definitions']],
                                  registry.read()['token'], action['predecessor'])
        if action['action'] == 'migrate':
            c.shape(action, {'action', 'predecessor', 'successor', 'decisions'}, '$/action')
            return registry.migrate(action['predecessor'], action['successor'],
                                    action['decisions'], registry.read()['token'])
    raise ValueError('UNKNOWN_ACTION_OR_TOOL')


def main():
    for line in sys.stdin:
        request = json.loads(line)
        if 'id' not in request:
            continue
        method = request.get('method')
        if method == 'initialize':
            result = dict(protocolVersion=request['params']['protocolVersion'],
                capabilities={'tools': {}}, serverInfo={'name': 'lykoi-r636', 'version': '1'})
        elif method == 'tools/list':
            result = {'tools': TOOLS}
            with (OUT / 'MCP-DISCOVERY.jsonl').open('a', encoding='utf-8') as log:
                log.write(json.dumps(dict(method=method, tools=TOOLS)) + '\n')
        elif method == 'tools/call':
            try:
                value = normalize(dispatch(request['params']['name'], request['params']['arguments']))
                result = dict(content=[{'type': 'text', 'text': json.dumps(value)}], isError=False)
            except Exception as exc:
                result = dict(content=[{'type': 'text', 'text': json.dumps(
                    getattr(exc, 'data', {'code': type(exc).__name__, 'detail': str(exc)}))}], isError=True)
        else:
            print(json.dumps(dict(jsonrpc='2.0', id=request['id'],
                error={'code': -32601, 'message': 'Unknown method'})), flush=True)
            continue
        print(json.dumps(dict(jsonrpc='2.0', id=request['id'], result=result)), flush=True)


if __name__ == '__main__':
    main()
