"""Transport-only MCP lifecycle facade over unchanged R6.32 operations."""
import json
import os
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/lifecycle_r6_32'))
from lifecycle import Registry, Journal, c
OUT = ROOT / 'benchmark/results/phase6/r6_37'
PHASE = os.environ.get('R637_PHASE', 'qualification')
assert PHASE in ('qualification', 'authoring')
STORE = OUT / PHASE


def schema(name, description, props, required):
    return dict(name=name, description=description, inputSchema=dict(type='object',
        properties=props, required=required, additionalProperties=False))


PIN = {'type': 'string', 'pattern': '^[0-9a-f]{64}$'}
TOOLS = [
    schema('lykoi_admit', 'Persist immutable typed definitions, or record explicit total caller migration. '
           'Admission mechanically seals omitted identities, validates with unchanged R6.32/R6.18 '
           'contracts, and returns pins. A successor preserves exact name and signature. '
           'Migration changes only selected caller dependency pins; null means retain.',
           {'action': {'type': 'object', 'oneOf': [
               dict(type='object', properties={'action': {'const': 'admit'},
                    'definitions': {'type': 'array', 'minItems': 1, 'maxItems': 8, 'items': {'type': 'object'}},
                    'predecessor': {'anyOf': [PIN, {'type': 'null'}]}},
                    required=['action', 'definitions', 'predecessor'], additionalProperties=False),
               dict(type='object', properties={'action': {'const': 'migrate'}, 'predecessor': PIN,
                    'successor': PIN, 'decisions': {'type': 'object', 'additionalProperties':
                        {'anyOf': [PIN, {'type': 'null'}]}}},
                    required=['action', 'predecessor', 'successor', 'decisions'], additionalProperties=False)
           ]}}, ['action']),
    schema('lykoi_retrieve', 'Read exact admitted immutable definition closure and dependency impact by pin. '
           'Returns registry token and successor/migration records; does not rewrite any binding.',
           {'identity': PIN}, ['identity']),
    schema('lykoi_validate', 'Read admitted closed root, expand via unchanged R6.18 and validate frozen VM plan. '
           'Returns structured validation identity, node count and provenance map. No execution.',
           {'identity': PIN}, ['identity']),
    schema('lykoi_execute', 'Read, validate and execute admitted closed root on exact input bytes through '
           'unchanged R6.10 VM. Returns structured values, errors, spans, trace and logical work.',
           {'identity': PIN, 'input_hex': {'type': 'string', 'pattern': '^(?:[0-9a-f]{2})*$'}},
           ['identity', 'input_hex'])]


def normalize(value):
    if isinstance(value, bytes):
        return {'bytes_hex': value.hex()}
    if isinstance(value, dict):
        return {k: normalize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [normalize(v) for v in value]
    return value


def package(registry, pin):
    closure = registry.retrieve(pin=pin)
    root = next(d for d in closure if d['identity'] == pin)
    return dict(version=c.VERSION, foundation=c.FOUNDATION,
        definitions=[d for d in closure if d['identity'] != pin], program=root)


def dispatch(name, args):
    if PHASE == 'authoring' and not (OUT / 'TASK-FREEZE.json').exists():
        c.fail('PROTOCOL', '$', 'task freeze required')
    known = next((t for t in TOOLS if t['name'] == name), None)
    if known is None:
        c.fail('ARGUMENT_SCHEMA', '$', 'unknown tool')
    c.shape(args, known['inputSchema']['required'], '$/arguments')
    c._tree_bound(args)
    if 'identity' in args:
        c.digest(args['identity'], '$/arguments/identity')
    if 'input_hex' in args and (type(args['input_hex']) is not str or
            not re.fullmatch(r'(?:[0-9a-f]{2})*', args['input_hex'])):
        c.fail('ARGUMENT_SCHEMA', '$/arguments/input_hex', 'lowercase even hexadecimal required')
    registry = Registry(STORE / 'registry', Journal(STORE / 'telemetry'))
    if name == 'lykoi_admit':
        action = args['action']
        if type(action) is not dict:
            c.fail('ARGUMENT_SCHEMA', '$/action', 'object required')
        if action.get('action') == 'admit':
            c.shape(action, {'action', 'definitions', 'predecessor'}, '$/action')
            if type(action['definitions']) is not list or not 1 <= len(action['definitions']) <= 8:
                c.fail('ARGUMENT_SCHEMA', '$/action/definitions', 'one to eight definitions required')
            if action['predecessor'] is not None:
                c.digest(action['predecessor'], '$/action/predecessor')
            for d in action['definitions']:
                c.shape(d, {'name', 'revision', 'params', 'dependencies', 'steps',
                    'order', 'result', 'result_type'}, '$/action/definition')
            return registry.admit([c.seal(d) for d in action['definitions']],
                registry.read()['token'], action['predecessor'])
        if action.get('action') == 'migrate':
            c.shape(action, {'action', 'predecessor', 'successor', 'decisions'}, '$/action')
            for field in ('predecessor', 'successor'):
                c.digest(action[field], '$/action/' + field)
            if type(action['decisions']) is not dict:
                c.fail('ARGUMENT_SCHEMA', '$/action/decisions', 'object required')
            for old, new in action['decisions'].items():
                c.digest(old, '$/action/decisions')
                if new is not None:
                    c.digest(new, '$/action/decisions')
            return {'status': 'migrated', 'token': registry.migrate(action['predecessor'],
                action['successor'], action['decisions'], registry.read()['token'])}
        c.fail('ARGUMENT_SCHEMA', '$/action', 'admit or migrate required')
    if name == 'lykoi_retrieve':
        definitions = registry.retrieve(pin=args['identity'])
        state = registry.read()
        return dict(definitions=definitions, token=state['token'],
            dependents=registry.dependents(args['identity']),
            successors=state['state']['successors'], migrations=state['state']['migrations'])
    expanded = c.expand(package(registry, args['identity']))
    if name == 'lykoi_validate':
        return dict(status='valid', plan_identity=expanded['plan_identity'],
            program_identity=expanded['program_identity'], nodes=expanded['nodes'], map=expanded['map'])
    return c.vm.execute(expanded['plan'], bytes.fromhex(args['input_hex']))


def main():
    STORE.mkdir(parents=True, exist_ok=True)
    for line in sys.stdin:
        request = json.loads(line)
        if 'id' not in request:
            continue
        started = time.perf_counter()
        method = request.get('method')
        if method == 'initialize':
            result = dict(protocolVersion=request['params']['protocolVersion'], capabilities={'tools': {}},
                serverInfo={'name': 'lykoi-r637-lifecycle', 'version': '1'})
        elif method == 'tools/list':
            result = {'tools': TOOLS}
        elif method == 'tools/call':
            try:
                value = normalize(dispatch(request['params']['name'], request['params']['arguments']))
                result = dict(content=[{'type': 'text', 'text': json.dumps(value)}],
                    structuredContent=value if isinstance(value, dict) else {'value': value}, isError=False)
            except c.Diagnostic as exc:
                result = dict(content=[{'type': 'text', 'text': json.dumps(exc.data)}],
                    structuredContent=exc.data, isError=True)
            except Exception as exc:
                value = dict(code='INFRASTRUCTURE', detail=type(exc).__name__ + ': ' + str(exc))
                result = dict(content=[{'type': 'text', 'text': json.dumps(value)}],
                    structuredContent=value, isError=True)
        else:
            result = None
        response = dict(jsonrpc='2.0', id=request['id'], result=result)
        with (STORE / 'MCP.jsonl').open('a', encoding='utf-8') as log:
            log.write(json.dumps(dict(request=request, response=response,
                wall_seconds=time.perf_counter()-started)) + '\n')
        print(json.dumps(response), flush=True)


if __name__ == '__main__':
    main()
