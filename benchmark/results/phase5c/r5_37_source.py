"""Declarative R5.37 source authoring; contains no executable task behavior.

The resulting operation family is an attempted current-format encoding, not a
claim that the locked public profile can dispatch all version alternatives.
The companion reconstruction is authoritative for obligations beyond the
current format. Do not weaken nullable types to make the compiler accept them.
"""
import copy
import json
from pathlib import Path


def ref(*parts):
    return {'ref': list(parts)}


def lit(value, shape='string'):
    return {'literal': {'type': shape, 'value': value}}


def eq(a, b):
    return {'equals': [a, b]}


def fallback(name, value, shape='string'):
    return {'fallback': {'value': ref('input', name), 'default': lit(value, shape)}}


def select(side, predicate):
    return {'select': {'source': ref(side, 'records'), 'where': predicate}}


def branch(tag, when, value, shape='string', transition=None):
    return {'tag': tag, 'when': when, 'value': value, 'value_type': shape,
            'transition': transition or {'preserve': True}}


def source():
    nullable = {'nullable': 'instant'}
    tags = {'sequence': 'string'}
    row = {'record': {'id': 'string', 'title': 'string', 'description': 'string',
        'status': 'string', 'priority': 'string', 'created_at': 'instant',
        'due_date': nullable, 'tags': tags}}
    rows = {'sequence': row}
    current = {'record': {'schema_version': 'integer', 'records': rows}}
    old_row = {'record': {**row['record'], **{name: {'optional': row['record'][name]}
        for name in ('priority', 'due_date', 'tags')}}}
    bare = {'sequence': old_row}
    legacy = {'record': {'schema_version': 'integer', 'records': bare}}
    versions = {'V1': bare, 'legacy_envelope': legacy, 'V4': current}
    yes = eq(lit(1, 'integer'), lit(1, 'integer'))
    at4 = eq(ref('pre', 'schema_version'), lit(4, 'integer'))
    operations = {}

    def op(name, inp, branches, pre=current, post=current, requires=at4):
        operations[name] = {'id': 'r5.37.b02.' + name, 'version': 'R5.33',
            'input': {'record': inp}, 'state': {'pre': pre, 'post': post},
            'requires': requires, 'branches': branches}

    for name, predicate in [('list', None), ('list-high', eq(ref('item', 'priority'), lit('HIGH'))),
            ('list-overdue', {'and': [eq(ref('item', 'status'), lit('pending')),
                {'not': eq(ref('item', 'due_date'), lit(None, nullable))},
                {'before': [ref('item', 'due_date'), {'external': {'source': 'utc_clock'}}]}]})]:
        selected = ref('pre', 'records') if predicate is None else select('pre', predicate)
        value = {'order': {'source': selected, 'keys': ['created_at', 'id']}}
        op(name, {}, [branch('listed', yes, value, rows), branch('listed_otherwise', None, value, rows)])

    created = {'record': {'id': {'external': {'source': 'fresh_unique_id'}},
        'title': ref('input', 'title'), 'description': ref('input', 'description'),
        'status': lit('pending'), 'priority': fallback('priority', 'NORMAL'),
        'created_at': {'external': {'source': 'utc_clock'}},
        'due_date': fallback('due_date', None, nullable),
        'tags': {'stable_unique': {'sequence': {'map': {
            'sequence': fallback('tags', [], tags), 'transform': 'trim'}},
            'equality': 'case_sensitive_string'}}}}
    invalid_priority = {'and': [{'not': eq(fallback('priority', 'NORMAL'), lit(p))}
                               for p in ('LOW', 'NORMAL', 'HIGH', 'CRITICAL')]}
    op('create', {'title': 'string', 'description': 'string', 'priority': {'optional': 'string'},
        'due_date': {'optional': nullable}, 'tags': {'optional': tags}}, [
        branch('invalid_title', {'not': {'nonblank': {'trim': ref('input', 'title')}}}, lit('invalid_title')),
        branch('invalid_tag', {'not': {'for_each': {'sequence': fallback('tags', [], tags),
            'bind': 'tag', 'property': {'nonblank': {'trim': ref('tag')}}}}}, lit('invalid_tag')),
        branch('invalid_priority', invalid_priority, lit('invalid_priority')),
        branch('created', None, created, row, {'relations': [{'exact_frame': {
            'collection': 'records', 'identity': 'id', 'record': created}}]})])

    match = eq(ref('item', 'id'), ref('input', 'id'))
    matches = select('pre', match)
    count = {'cardinality': matches}
    no_match = eq(count, lit(0, 'integer'))
    already = eq({'cardinality': select('pre', {'and': [match,
        eq(ref('item', 'status'), lit('completed'))]})}, lit(1, 'integer'))
    op('complete', {'id': 'string'}, [
        branch('task_not_found', no_match, lit('task_not_found')),
        branch('invalid_transition', already, lit('invalid_transition')),
        branch('completed', None, {'sole': select('post', match)}, row,
            {'relations': [{'replace_field': {'collection': 'records', 'key': 'id',
                'match': ref('input', 'id'), 'field': 'status', 'value': lit('completed')}}]})])
    op('delete', {'id': 'string'}, [branch('task_not_found', no_match, lit('task_not_found')),
        branch('deleted', None, {'sole': matches}, row, {'relations': [{'remove': {
            'collection': 'records', 'identity': 'id', 'match': ref('input', 'id')}}]})])
    result_shape = {'record': {'migrated': 'integer'}}
    zero = {'record': {'migrated': lit(0, 'integer')}}
    op('migrate_current', {}, [branch('current', yes, zero, result_shape),
        branch('current_otherwise', None, zero, result_shape)])
    for name, pre, path, requires in [('migrate_v1', bare, [], yes),
            ('migrate_envelope', legacy, ['records'], {'not': at4})]:
        transition = {'relations': [{'default_missing': {'source': path, 'target': ['records'],
            'identity': 'id', 'field': field, 'value': lit(value, shape)}}
            for field, value, shape in [('priority', 'NORMAL', 'string'),
                ('due_date', None, nullable), ('tags', [], tags)]] + [
            {'post_equals': {'field': 'schema_version', 'value': lit(4, 'integer')}}]}
        value = {'record': {'migrated': {'cardinality': ref('pre', *path)}}}
        op(name, {}, [branch('migrated', yes, value, result_shape, transition),
            branch('migrated_otherwise', None, value, result_shape, transition)], pre, current, requires)
    for version, pre, requires in [('v1', bare, yes), ('envelope', legacy, {'not': at4})]:
        for command in ('list', 'list-high', 'list-overdue'):
            op(command + '_legacy_' + version, {}, [
                branch('migration_required', yes, lit('migration_required')),
                branch('migration_required_otherwise', None, lit('migration_required'))], pre, pre, requires)
    # Serialized trees give each scoped expression its own identity. Sharing a
    # Python object between pre/post scopes is not part of the semantic source.
    return json.loads(json.dumps({'id': 'r5.37.frozen-b02.attempt',
        'state': {'versions': versions}, 'operations': operations}))


if __name__ == '__main__':
    path = Path(__file__).with_name('R5_37-b02-semantic-application.json')
    path.write_bytes((json.dumps(source(), indent=2) + '\n').encode())
    print(str(path))
