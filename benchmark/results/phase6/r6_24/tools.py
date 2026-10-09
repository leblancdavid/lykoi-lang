"""Transactional typed construction over the unchanged R6.23 adapter."""
import copy
import importlib.util
import json
from pathlib import Path
import time

import jsonschema

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r6_24_frozen_adapter', HERE.parent / 'r6_23/adapter.py')
a = importlib.util.module_from_spec(spec)
spec.loader.exec_module(a)

NAME = dict(type='string', pattern='^[A-Za-z][A-Za-z0-9_]{0,31}$')
TYPE = dict(enum=['Int64', 'Bool', 'Unit'])
ARG = dict(oneOf=[dict(type='integer', minimum=-(2**63), maximum=2**63-1),
    dict(type='boolean'), dict(type='null'), dict(type='string', pattern='^\\$[A-Za-z][A-Za-z0-9_]{0,31}$')])
EXPR = dict(oneOf=[ARG, dict(type='array', prefixItems=[dict(enum=['add', 'le', 'eq']), ARG, ARG],
    items=False, minItems=3, maxItems=3)])
DEPS = dict(type='array', items=NAME, uniqueItems=True, maxItems=8)

def obj(props):
    return dict(type='object', properties=props, required=list(props), additionalProperties=False)

def definitions(operations):
    variants = {
        'value': obj(dict(definition=NAME, alias=NAME, operation=dict(const='value'), type=TYPE,
            expression=EXPR, dependencies=DEPS)),
        'check': obj(dict(definition=NAME, alias=NAME, operation=dict(const='check'),
            expression=EXPR, site=EXPR, code=NAME, dependencies=DEPS)),
        'compose': obj(dict(definition=NAME, alias=NAME, operation=dict(const='compose'), symbol=NAME,
            arguments=dict(type='object', propertyNames=NAME, additionalProperties=ARG, maxProperties=4), dependencies=DEPS))}
    params = {
        'declare_input': obj(dict(definition=NAME, inputs=dict(type='array', maxItems=4,
            items=obj(dict(name=NAME, type=TYPE))))),
        'apply_operation': dict(oneOf=[variants[n] for n in operations]),
        'define_result': obj(dict(definition=NAME, result=EXPR, result_type=TYPE)),
        'validate_candidate': obj(dict(target=NAME))}
    descriptions = {
        'declare_input': 'Create a named definition and its exact typed input signature. Maximum3 definitions/4 inputs.',
        'apply_operation': 'Append one ordered operation. Expressions are scalar literals, $prior_alias, or [add|le|eq,operand,operand]. Exact dependencies required. Maximum8 steps/definition. compose may call only a completed definition.',
        'define_result': 'Finalize this definition with its result expression and type; no later edits.',
        'validate_candidate': 'Validate and expand the completed registry via frozen adapter/wrapper. Target must return Int64. Finish on success.'}
    return [dict(type='function', function=dict(name=n, description=descriptions[n], parameters=s)) for n, s in params.items()]

class Session:
    def __init__(self, operations):
        self.schemas = {t['function']['name']: t['function']['parameters'] for t in definitions(operations)}
        self.packet = dict(version='construct-1', definitions=[], target='Pending')
        self.finalized = set()
        self.calls = 0
        self.completed = None

    def dispatch(self, call):
        begin = time.perf_counter()
        self.calls += 1
        syntax = arguments = False
        before = copy.deepcopy(self.packet)
        finalized = self.finalized.copy()
        try:
            if self.calls > 24:
                a.c.fail('RESOURCE', '$/calls', '24 tool calls maximum')
            if type(call) is not dict or set(call) != {'function'}:
                a.c.fail('TOOL_SYNTAX', '$', 'exact function envelope required')
            f = call['function']
            if type(f) is not dict or set(f) != {'name', 'arguments'} or f['name'] not in self.schemas:
                a.c.fail('TOOL_SYNTAX', '$/function', 'known name and object arguments required')
            syntax = True
            x = f['arguments']
            if len(json.dumps(x)) > 4096:
                a.c.fail('RESOURCE', '$/arguments', '4096 serialized characters maximum')
            jsonschema.Draft202012Validator(self.schemas[f['name']]).validate(x)
            arguments = True
            if self.completed:
                a.c.fail('CLOSED', '$', 'candidate already completed')
            name = f['name']
            registry = {d['name']: d for d in self.packet['definitions']}
            if name == 'declare_input':
                if x['definition'] in registry or x['definition'] == 'HostEntry':
                    a.c.fail('CAPTURE', '$/definition', 'duplicate or reserved name')
                if len(registry) >= 3:
                    a.c.fail('RESOURCE', '$/definitions', 'maximum3 definitions')
                self.packet['definitions'].append(dict(name=x['definition'],
                    inputs=[[p['name'], p['type']] for p in x['inputs']], ops=[], result=0, result_type='Int64'))
                # Temporary result0 is an internal type-check sentinel, never a submitted candidate.
                a.compact_defs(self.packet)
            elif name in ('apply_operation', 'define_result'):
                if x['definition'] not in registry:
                    a.c.fail('UNKNOWN_SYMBOL', '$/definition', x['definition'])
                d = registry[x['definition']]
                if d['name'] in self.finalized:
                    a.c.fail('CLOSED', '$/definition', 'definition finalized')
                if name == 'define_result':
                    if not d['ops']:
                        a.c.fail('SHAPE', '$/ops', 'at least one operation required')
                    d.update(result=x['result'], result_type=x['result_type'])
                    self.finalized.add(d['name'])
                else:
                    if len(d['ops']) >= 8:
                        a.c.fail('RESOURCE', '$/ops', 'maximum8 steps')
                    head = [x['alias'], x['operation']]
                    if x['operation'] == 'value':
                        op = head + [x['type'], x['expression'], x['dependencies']]
                    elif x['operation'] == 'check':
                        op = head + [x['expression'], x['site'], x['code'], x['dependencies']]
                    else:
                        if x['symbol'] not in self.finalized:
                            a.c.fail('UNKNOWN_SYMBOL', '$/symbol', 'callee must be completed first')
                        op = head + [x['symbol'], x['arguments'], x['dependencies']]
                    d['ops'].append(op)
                a.compact_defs(self.packet)
            else:
                if self.finalized != set(registry):
                    a.c.fail('INCOMPLETE', '$/definitions', 'all declared definitions must be finalized')
                self.packet['target'] = x['target']
                result = a.construct(json.dumps(self.packet), 'B')
                if not result['typed_valid']:
                    e = result['diagnostic']
                    a.c.fail(e['code'], e.get('path', '$'), e.get('detail', 'construction rejected'))
                target = next(d for d in result['artifact']['definitions'] if d['name'] == x['target'])
                dummy = {p['name']: {'Int64': 0, 'Bool': False, 'Unit': None}[p['type']] for p in target['params']}
                expanded = a.c.expand(a.package(result['artifact'], dummy))
                self.completed = result
                return dict(syntax_valid=True, arguments_valid=True, success=True,
                    response=dict(ok=True, completed=True, target=x['target'], expanded_nodes=expanded['nodes']),
                    seconds=time.perf_counter() - begin)
            return dict(syntax_valid=syntax, arguments_valid=arguments, success=True,
                response=dict(ok=True, definition=x['definition'], finalized=x['definition'] in self.finalized),
                seconds=time.perf_counter() - begin)
        except (a.c.Diagnostic, jsonschema.ValidationError, ValueError, TypeError) as e:
            self.packet, self.finalized = before, finalized
            diagnostic = e.data if isinstance(e, a.c.Diagnostic) else dict(code='ARGUMENT_SCHEMA', detail=str(e)[:500])
            return dict(syntax_valid=syntax, arguments_valid=arguments, success=False,
                response=dict(ok=False, error=diagnostic), seconds=time.perf_counter() - begin)
