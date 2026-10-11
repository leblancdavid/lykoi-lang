"""Dependency-free successor diagnostic scorer; no training dispatch or new semantics."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/incremental_data_r6_63'))
import assembly
from freeze import c

DIMENSIONS = ('strict_serialization', 'schema_valid', 'operation_correct',
              'operands_correct', 'result_type_correct', 'dependencies_correct',
              'deterministic_assembly', 'behavioral_acceptance')


def validate_action(action):
    """Exact finite projection of frozen step-1.schema.json after strict c.load.

    This is not a general JSON Schema interpreter. Scope, expression types and
    exact dependencies are separately validated by the unchanged assembler.
    """
    c._tree_bound(action)
    c.shape(action, {'id', 'type', 'deps', 'node'}, '$/action')
    if action['id'] != 'selected' or type(action['type']) is not str or action['type'] not in ('Int64', 'Bool'):
        c.fail('SHAPE', '$/action', 'selected id and Int64/Bool type required')
    deps = action['deps']
    if (type(deps) is not list or len(deps) > 2 or any(type(d) is not str for d in deps)
            or len(set(deps)) != len(deps)):
        c.fail('SHAPE', '$/action/deps', 'at most two distinct strings required')
    c.shape(action['node'], {'op', 'expr'}, '$/action/node')
    if action['node']['op'] != 'value':
        c.fail('SHAPE', '$/action/node/op', 'value required')
    expr = action['node']['expr']
    if type(expr) is not dict or len(expr) != 1 or next(iter(expr)) not in ('add', 'le', 'eq'):
        c.fail('SHAPE', '$/action/node/expr', 'one add/le/eq operation required')
    operands = next(iter(expr.values()))
    if type(operands) is not list or len(operands) != 2:
        c.fail('SHAPE', '$/action/node/expr', 'two ordered operands required')
    for i, operand in enumerate(operands):
        path = '$/action/node/expr/' + str(i)
        if type(operand) is not dict or set(operand) not in ({'ref'}, {'const'}):
            c.fail('SHAPE', path, 'exact ref or const object required')
        if 'ref' in operand:
            if type(operand['ref']) is not str:
                c.fail('SHAPE', path, 'string reference required')
        else:
            # Existing authoritative literal domain: bool differs from int;
            # Int64 range and Unit null are exact. No floats or host coercion.
            c.expression(operand, {}, path)


def score(text, row):
    result = dict.fromkeys(DIMENSIONS, False)
    result.update(exact_target_reproduction=False, repair_count=0, observations=[],
                  classification='NOT_REACHED', stage='serialization')
    try:
        action = c.load(text)
        result['strict_serialization'] = type(action) is dict
        result['stage'] = 'schema'
        validate_action(action)
        result['schema_valid'] = True
        gold = c.load(row['completion'][0]['content'])
        expr, expected = action['node']['expr'], gold['node']['expr']
        result.update(operation_correct=list(expr) == list(expected),
                      operands_correct=c.canonical(next(iter(expr.values()))) == c.canonical(next(iter(expected.values()))),
                      result_type_correct=action['type'] == gold['type'],
                      dependencies_correct=action['deps'] == gold['deps'],
                      exact_target_reproduction=c.canonical(action) == c.canonical(gold))
        result['stage'] = 'assembly'
        after, validation = assembly.apply(row['before'], action)
        again, again_validation = assembly.apply(c.load(c.canonical(row['before']).decode()), c.load(text))
        result['deterministic_assembly'] = after == again and validation == again_validation
        result['stage'] = 'behavior'
        for fixture in row['cases']:
            actual = assembly.behavior(after, fixture['arguments'])
            result['observations'].append(dict(actual=actual, expected=fixture['expected'],
                                               passed=assembly.agrees(actual, fixture['expected'])))
        result['behavioral_acceptance'] = all(x['passed'] for x in result['observations'])
        result['classification'] = 'ACCEPTED' if all(result[k] for k in DIMENSIONS) else 'SEMANTIC_MISMATCH'
        result['stage'] = 'complete'
    except c.Diagnostic as exc:
        result['classification'] = {'serialization': 'SERIALIZATION_FAILURE', 'schema': 'SCHEMA_FAILURE',
                                    'assembly': 'ASSEMBLY_FAILURE'}.get(result['stage'], 'EXECUTION_FAILURE')
        result['error'] = exc.data
    except Exception as exc:
        result['classification'] = 'INFRASTRUCTURE_FAILURE'
        result['error'] = dict(type=type(exc).__name__, detail=str(exc))
    result['accepted'] = result['classification'] == 'ACCEPTED'
    return result
