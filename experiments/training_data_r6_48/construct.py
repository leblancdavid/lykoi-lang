"""Actual deterministic construction API traces; never labeled AI tool trajectories."""
import copy
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from prepare import ROOT, EVIDENCE, canonical, read, sha, write

sys.path.insert(0, str(ROOT / 'experiments/typed_composition_r6_18'))
import composition as c


def verify_freeze():
    freeze = read(EVIDENCE / 'SOURCE-FREEZE.json')
    for name, digest in freeze['files'].items():
        assert sha(ROOT / name) == digest, name
    return sha(EVIDENCE / 'SOURCE-FREEZE.json')


def ref(name):
    return {'ref': name}


def const(value):
    return {'const': value}


def expr(op, a, b):
    return {op: [a, b]}


def step(name, typ, deps, node):
    return {'id': name, 'type': typ, 'deps': deps, 'node': node}


def atom(name):
    return step(name, 'Int64', [], {'op': 'atom', 'codec': 'uint8'})


def value(name, deps, expression, typ='Int64'):
    return step(name, typ, deps, {'op': 'value', 'expr': expression})


def check(name, deps, test, site, code):
    return step(name, 'Unit', deps, {'op': 'check', 'test': test, 'site': ref(site), 'code': code})


def call(name, target, args):
    deps = sorted({x['ref'] for x in args.values() if 'ref' in x})
    return step(name, 'Int64', deps, {'op': 'compose', 'symbol': target['name'],
                                    'identity': target['identity'], 'args': args})


class Trace:
    def __init__(self):
        self.entries = []

    def invoke(self, name, argument):
        before = copy.deepcopy(argument)
        try:
            if name == 'load':
                result = c.load(argument)
            else:
                result = getattr(c, name)(argument)
            self.entries.append({'sequence': len(self.entries) + 1, 'tool': name,
                                 'arguments': before, 'response': copy.deepcopy(result),
                                 'status': 'returned'})
            return result
        except c.Diagnostic as exc:
            self.entries.append({'sequence': len(self.entries) + 1, 'tool': name,
                                 'arguments': before, 'response': exc.data, 'status': 'diagnostic'})
            raise

    def definition(self, name, steps, result, params=(), dependencies=None, typ='Int64'):
        return self.invoke('seal', {'name': name, 'revision': 1,
            'params': [{'name': key, 'type': kind} for key, kind in params],
            'dependencies': dependencies or {}, 'steps': steps,
            'order': [s['id'] for s in steps], 'result': result, 'result_type': typ})


def build(eid, t):
    a, b, z = ref('a'), ref('b'), ref('c')
    definitions = []
    dependencies = {}
    if eid in ('E01', 'E02'):
        steps = [atom('a'), atom('b')]
        if eid == 'E02':
            steps += [value('twice', ['a'], expr('add', a, a))]
        left = a if eid == 'E01' else ref('twice')
        steps += [value('total', ['a', 'b'] if eid == 'E01' else ['twice', 'b'], expr('add', left, b)),
                  check('capacity', ['total', 'a'], expr('le', ref('total'), const(120 if eid == 'E01' else 600)),
                        'a', 'CAPACITY' if eid == 'E01' else 'QUOTE')]
        result = ref('total')
    elif eid in ('E03', 'E04'):
        ga = check('flag_a', ['a'], expr('le', a, const(1)), 'a', 'FLAG_A')
        gb = check('flag_b', ['b'], expr('le', b, const(1)), 'b', 'FLAG_B')
        if eid == 'E03':
            steps = [atom('a'), ga, atom('b'), gb,
                     value('same', ['a', 'b'], expr('eq', a, b), 'Bool'),
                     check('agreement', ['same', 'a'], expr('eq', ref('same'), const(True)), 'a', 'DISAGREE')]
            result = a
        else:
            steps = [atom('a'), atom('b'), ga, gb,
                     value('total', ['a', 'b'], expr('add', a, b)),
                     value('exactly_one', ['total'], expr('eq', ref('total'), const(1)), 'Bool'),
                     check('agreement', ['exactly_one', 'a'], expr('eq', ref('exactly_one'), const(True)), 'a', 'INTERLOCK')]
            result = ref('total')
    elif eid == 'E05':
        steps = [atom('a'), check('version', ['a'], expr('eq', a, const(7)), 'a', 'VERSION'),
                 atom('b'), check('count', ['b'], expr('le', b, const(12)), 'b', 'COUNT')]
        result = b
    elif eid == 'E06':
        steps = [atom('a'), atom('b'), atom('c'),
                 check('window', ['a', 'b'], expr('le', a, b), 'a', 'WINDOW'),
                 check('below', ['a', 'c'], expr('le', a, z), 'c', 'BELOW'),
                 check('above', ['c', 'b'], expr('le', z, b), 'c', 'ABOVE')]
        result = z
    elif eid == 'E07':
        pair = t.definition('tally_pair', [value('sum', ['x', 'y'], expr('add', ref('x'), ref('y')))],
                            ref('sum'), [('x', 'Int64'), ('y', 'Int64')])
        aggregate = t.definition('tally_three', [
            call('first', pair, {'x': ref('x'), 'y': ref('y')}),
            call('second', pair, {'x': ref('first'), 'y': ref('z')})], ref('second'),
            [('x', 'Int64'), ('y', 'Int64'), ('z', 'Int64')], {pair['name']: pair['identity']})
        definitions = [pair, aggregate]
        dependencies = {aggregate['name']: aggregate['identity']}
        steps = [atom('a'), atom('b'), atom('c'),
                 call('total', aggregate, {'x': a, 'y': b, 'z': z}),
                 check('capacity', ['total', 'a'], expr('le', ref('total'), const(300)), 'a', 'TOTAL')]
        result = ref('total')
    elif eid == 'E08':
        double = t.definition('packing_double', [value('d', ['x'], expr('add', ref('x'), ref('x')))],
                              ref('d'), [('x', 'Int64')])
        triple = t.definition('packing_triple', [call('d', double, {'x': ref('x')}),
            value('t', ['d', 'x'], expr('add', ref('d'), ref('x')))], ref('t'),
            [('x', 'Int64')], {double['name']: double['identity']})
        definitions = [double, triple]
        dependencies = {d['name']: d['identity'] for d in definitions}
        steps = [atom('a'), atom('b'), call('d', double, {'x': a}), call('t', triple, {'x': b}),
                 value('total', ['d', 't'], expr('add', ref('d'), ref('t'))),
                 check('capacity', ['total', 'a'], expr('le', ref('total'), const(1000)), 'a', 'SCORE')]
        result = ref('total')
    else:
        raise ValueError('episode not released for implementation')
    steps.append(step('complete', 'Unit', [], {'op': 'end'}))
    program = t.definition('pilot_' + eid, steps, result, dependencies=dependencies)
    return {'version': c.VERSION, 'foundation': c.FOUNDATION,
            'definitions': definitions, 'program': program}


def main():
    freeze_hash = verify_freeze()
    tool_contract = {'version': 'r6_48-scripted-api-contract-1',
        'kind': 'Python APIs, not semantic MCP selection',
        'module': 'experiments/typed_composition_r6_18/composition.py',
        'module_sha256': sha(ROOT / 'experiments/typed_composition_r6_18/composition.py'),
        'semantic_spec': 'experiments/typed_composition_r6_18/SEMANTICS-1.md',
        'r6_23_adapter_used': False, 'r6_25_mcp_used': False,
        'available_tools': {'seal': 'definition JSON -> immutable typed definition with content identity',
                            'load': 'strict JSON text -> bounded JSON package or Diagnostic',
                            'validate': 'typed package -> validation counts or Diagnostic',
                            'expand': 'typed package -> semantic-plan-1, expansion map, identities or Diagnostic',
                            'diagnose': 'typed package -> native valid/reject envelope'},
        'selection': 'script-authored fixed calls; no model-selected semantic calls'}
    write(EVIDENCE / 'SCRIPTED-API-CONTRACT.json', tool_contract)
    for n in range(1, 9):
        eid = 'E%02d' % n
        folder = EVIDENCE / 'episodes' / eid
        t = Trace()
        package = build(eid, t)
        loaded = t.invoke('load', canonical(package).decode('ascii'))
        validation = t.invoke('validate', loaded)
        expanded = t.invoke('expand', loaded)
        diagnostic = t.invoke('diagnose', loaded)
        write(folder / 'SYMBOLIC.json', package)
        write(folder / 'EXECUTABLE.json', expanded['plan'])
        write(folder / 'EXPANSION-MAP.json', expanded['map'])
        write(folder / 'VALIDATION.json', {'validation': validation, 'diagnostic': diagnostic,
            'program_identity': expanded['program_identity'], 'plan_identity': expanded['plan_identity'],
            'source_freeze_sha256': freeze_hash})
        write(folder / 'SCRIPTED-TRAJECTORY.json', {'version': 'lykoi-scripted-trajectory-1',
            'episode_id': eid, 'kind': 'DETERMINISTIC_SCRIPTED_CONSTRUCTION',
            'ai_authored_tool_trajectory_available': False, 'corrections_observed': 0,
            'api_contract_sha256': sha(EVIDENCE / 'SCRIPTED-API-CONTRACT.json'),
            'entries': t.entries, 'final_symbolic_sha256': sha(folder / 'SYMBOLIC.json'),
            'final_artifact_identity': expanded['plan_identity']})
    paths = sorted(p for p in EVIDENCE.rglob('*.json') if p.name in (
        'SYMBOLIC.json', 'EXECUTABLE.json', 'EXPANSION-MAP.json', 'VALIDATION.json',
        'SCRIPTED-TRAJECTORY.json', 'SCRIPTED-API-CONTRACT.json'))
    write(EVIDENCE / 'CANDIDATE-FREEZE.json', {'utc': datetime.now(timezone.utc).isoformat(),
        'source_freeze_sha256': freeze_hash, 'before_acceptance_execution': True,
        'files': {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}})
    print(json.dumps({'candidates': 8, 'valid': 8, 'scripted_trajectories': 8,
                      'actual_ai_semantic_tool_trajectories': 0, 'candidate_files': len(paths)}))


if __name__ == '__main__':
    main()
