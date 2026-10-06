"""Fresh active-agent source captures, R5.103. No historical capture imports.

Structured unsupported demands are retained WHAT, not executable new semantics.
All source bundles contain only frozen requirements, common authority and baseline.
"""
import copy
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODEL = json.loads((ROOT / 'air/task_manager.json').read_text(encoding='utf-8'))
QUESTIONS = {
    'B17': 'Which role must explicit migration assign to an existing non-system user? The creation default USER does not authorize a migration value.',
    'B20': 'Which application error must add-project-member return for a nonexistent member user? The missing-ID common rule has historically task-specific scope; confirm whether it applies to users here.',
}


def scalar_facts():
    fields = [('id', 'identifier', [], False), ('title', 'string', [], False),
              ('description', 'string', [], False), ('status', 'enum', ['pending', 'completed'], False),
              ('priority', 'enum', ['LOW', 'NORMAL', 'HIGH'], False),
              ('created_at', 'timestamp', [], False), ('due_date', 'timestamp', [], True)]
    return {
        'storage': {'path': 'tasks.json', 'version': 3, 'missing': 'empty_collection', 'write': 'atomic', 'rejection': 'unchanged'},
        'fields': [dict(name=n, type=t, domain=d, nullable=z, preservation='verbatim') for n, t, d, z in fields],
        'creation': {'command': 'create', 'bindings': [
            dict(field=n, source=s, value=v, default=None if default == '@required' else dict(value=default, trigger='omitted', boundary='creation'))
            for n, s, v, default in [('id', 'uuid_v4', None, '@required'), ('title', 'input', None, '@required'),
                ('description', 'input', None, '@required'), ('status', 'literal', 'pending', '@required'),
                ('priority', 'input', None, 'NORMAL'), ('created_at', 'utc_clock', None, '@required'), ('due_date', 'input', None, None)]],
            'validation': [dict(field='title', rule='nonblank', error='invalid_title'), dict(field='due_date', rule='timestamp_utc', error='invalid_due_date')]},
        'listing': dict(command='list', order=['created_at', 'id'], result='whole_records'),
        'lifecycle': [dict(field='status', initial='pending', source='pending', target='completed', command='complete', missing_error='task_not_found', transition_error='invalid_transition', rejection='unchanged')],
        'evolution': [dict(**{'from': 1, 'to': 2}, defaults={'priority': 'NORMAL'}, boundary='explicit_migration', preservation='unrelated_fields'),
                      dict(**{'from': 2, 'to': 3}, defaults={'due_date': None}, boundary='explicit_migration', preservation='unrelated_fields')],
    }


def query_facts(field, parameter, kind='string', archived=False):
    fields = {'id': 'string', 'created_at': 'string', field: kind}
    if field != 'status': fields['status'] = 'string'
    if archived: fields['archived'] = 'boolean'
    return {
        'source': dict(collection='state_tasks', fields=fields, unique_key='id'),
        'parameters': {parameter: 'string'},
        'predicate': dict(field=field, operator='contains' if kind == 'strings' else 'equals', operand={'parameter': parameter}),
        'comparison': dict(case='sensitive', normalization='none'),
        'ordering': [dict(field='created_at', direction='ASC'), dict(field='id', direction='ASC')],
        'validation': [dict(parameter=parameter, rule='nonblank', error='invalid_tag')] if kind == 'strings' else [],
        'inclusion': ([] if field == 'status' else [dict(field='status', mode='all')]) + ([dict(field='archived', mode='equals', value=False)] if archived else []),
        'effect': dict(state='read_only', persistence='unchanged'),
        'result': dict(shape='collection', cardinality='zero_or_more', no_match='empty'),
    }


# Fresh structured descriptions of demands beyond executable typed vocabulary.
# These keys have NO product interpreter. Coverage must refuse them.
DEMANDS = {
 'B02': [('crud', 'mutable_values', dict(field='tags', type='ordered_strings', command='create', flag='--tag', repeated=True, transform='strip', validate='nonblank', error='invalid_tag', deduplicate='stable_first_case_sensitive', omission=[], migration=[], result='all_task_results', rejection='unchanged'))],
 'B06': [('crud', 'write_transform', dict(field='category', type='string', command='create', flag='--category', transform='strip_nonempty', omitted='', explicit_empty='', whitespace_error='invalid_category', migration='', result='all_task_results', rejection='unchanged'))],
 'B07': [('crud', 'mutable_values', dict(field='notes', type='ordered_strings', command='append-note', lookup='id', input='text', transform='strip', validate='nonblank', error='invalid_note', missing_error='task_not_found', update='append', order='insertion', initial=[], migration=[], result='updated_whole_record', frame='notes_only', rejection='unchanged'))],
 'B08': [('transition', 'writable_boolean', dict(field='archived', type='boolean', initial=False, migration=False, command='archive', lookup='id', source=False, target=True, error='invalid_transition', missing_error='task_not_found', frame='status_unchanged', rejection='unchanged')),
         ('filter_order', 'query_amendments', dict(commands=['list', 'list-high', 'list-overdue', 'list-tag', 'list-status', 'list-category'], exclude={'archived': True}, add='list-archived', select={'archived': True}, ordering=['created_at', 'id'], effect='read_only'))],
 'B09': [('filter_order', 'temporal_range', dict(command='list-due', parameters={'start':'utc_timestamp','end':'utc_timestamp'}, predicate={'all':[{'archived':False},{'status':'pending'},{'due_date':{'nonnull':True,'gte':'start','lte':'end'}}]}, validate={'start_lte_end':'invalid_window','utc':'invalid_due_date'}, ordering=['created_at','id'], result='whole_records_or_empty', effect='read_only'))],
 'B10': [('crud', 'write_transform', dict(field='owner', type='string', command='create', flag='--owner', omitted='', transform='strip', supplied_validation='nonblank', error='invalid_owner', migration='', user_existence=False, result='all_task_results', rejection='unchanged'))],
 'B11': [('invariant', 'predicate_composition', dict(command='delete', permit={'any':[{'status':'pending'},{'all':[{'status':'completed'},{'archived':True}]}]}, error='delete_requires_archive', result='removed_whole_record', rejection='unchanged'))],
 'B12': [('filter_order', 'scalar_in_set', dict(command='list-urgent', predicates={'all':[{'archived':False},{'status':'pending'},{'due_date':{'before_clock':'utc_clock','null':'exclude'}},{'priority':{'in':['HIGH','CRITICAL']}}]}, ordering=['created_at','id'], effect='read_only', preserve='list-overdue_all_priorities'))],
 'B13': [('invariant', 'guard_amendment', dict(commands=['complete','append-note'], require={'archived':False}, error='invalid_transition', rejection='unchanged', absent_operations=['unarchive','reopen'], preserve=['B11_delete','list-archived']))],
 'B14': [('invariant', 'relationships', dict(field='dependencies', type='ordered_identifiers', initial=[], migration=[], command='add-dependency', inputs=['id','depends-on'], update='append', target='existing_task_including_archived', reject={'self':'invalid_dependency','duplicate':'invalid_dependency','cycle':'invalid_dependency','unknown':'task_not_found','referenced_delete':'dependency_in_use'}, result='updated_whole_record', rejection='both_records_unchanged'))],
 'B15': [('invariant', 'relationship_quantification', dict(command='complete', quantify='all', collection='dependencies', predicate={'related_status':'completed'}, archived_completed=True, empty='permit', error='incomplete_dependencies', preserve=['dependencies','B13','prior_transitions'], rejection='unchanged'))],
 'B16': [('crud', 'multiple_entities', dict(entity='users', fields={'id':'nonblank_case_sensitive_string'}, builtin={'id':'system'}, create='create-user', errors={'blank':'invalid_user','duplicate':'user_exists'}, listing='list-users', ordering=['id'], result_fields=['id'])),
         ('invariant', 'cross_entity_existence', dict(command='create', owner='required_existing_user', error='invalid_owner', migration={'empty_owner':'system','nonempty_owner':'require_existing_user','error':'invalid_owner'}, retry='after_create_user', rejection='unchanged', preserve='list-owner'))],
 'B17': [('crud', 'roles', dict(entity='users', field='role', domain=['ADMIN','USER'], builtin_system='ADMIN', create_default='USER', old_user_migration=None, results='include_role')),
         ('invariant', 'authorization', dict(commands='all_mutating_task_commands', actor='required_existing_user', permit={'ADMIN':'any_owner','USER':'self_owned'}, errors={'missing':'actor_required','unknown':'unknown_actor','forbidden':'permission_denied'}, before='mutation', reads='unrestricted', rejection='unchanged'))],
 'B18': [('effects', 'durable_atomic_events', dict(commands=['create','complete','delete','archive','append-note','add-dependency'], on='successful_task_mutation', cardinality=1, fields={'sequence':'monotonic_integer','timestamp':'utc_clock','actor':'actor_id','operation':'command','task':'task_id'}, reject_entries=0, excluded=['create-user'], listing='list-audit', ordering=['sequence'], migration=[], atomic=['task_mutation','audit_append']))],
 'B19': [('transition', 'atomic_successor', dict(field='recurrence_days', type='nullable_positive_integer', create_flag='--recurrence-days', omitted=None, migration=None, require='due_date', error='invalid_recurrence', on='successful_complete', count=1, identity='fresh_uuid_v4', created_at='utc_clock', status='pending', copy=['title','description','priority','tags','source','category','owner','notes','project','recurrence_days'], dependencies=[], due_date={'add_utc_calendar_days':'recurrence_days'}, rejection='no_successor', response='ordinary_completion', atomic=['completion','successor','audit_complete','audit_create'], audit_order=['complete','create'], actor='completing_actor'))],
 'B20': [('crud', 'project_relationships', dict(entity='projects', fields={'id':'unique_nonblank_case_sensitive_string','owner':'existing_user','members':'set_existing_users'}, owner_member=True, create='create-project', add='add-project-member', idempotent=True, listing='list-projects', ordering=['id'], member_ordering=['id'], results='whole_project', task_field='project', task_omitted='', task_migration='', query='list-project', query_include={'archived':False}, query_order=['created_at','id'])),
         ('invariant', 'project_authorization', dict(create_project={'any':['owner','ADMIN']}, add_member={'any':['project_owner','ADMIN']}, mutate_task={'any':['ADMIN','project_owner',{'all':['task_owner','member']}]}, create_task={'all':[{'any':['ADMIN','project_owner','member']},'B17_ownership']}, errors={'duplicate':'project_exists','owner':'invalid_owner','project':'project_not_found','forbidden':'permission_denied','unknown_member':None}, rejection='unchanged'))],
}


def captures():
    result = []
    common_paths = ['benchmark/baseline.md', 'benchmark/requirements/README.md']
    for i in range(1, 21):
        case = f'B{i:02d}'
        paths = common_paths + [f'benchmark/requirements/{case}.md']
        # Explicit prior requirement authority, without invented precursor models.
        if i > 1: paths += [f'benchmark/requirements/B{j:02d}.md' for j in range(1, i)]
        texts = {p: (ROOT / p).read_text(encoding='utf-8') for p in paths}
        source = '\n\n'.join('## Source: ' + p + '\n' + text for p, text in texts.items())
        primary = texts[f'benchmark/requirements/{case}.md']
        r = dict(id=case, source=source, source_files={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}, rows=[], question=QUESTIONS.get(case),
                 domains={'evaluation_scope':'requirement-local against canonical baseline; precursor demands explicit, not achieved', 'baseline_model_sha256':hashlib.sha256((ROOT/'air/task_manager.json').read_bytes()).hexdigest()})
        def add(oid, kind, p, quote=primary):
            r['rows'].append(dict(id=case+'/'+oid, basis='STATED', source_quote=quote, derived_from=[], statement='Fresh source-authorized '+oid, relation=dict(kind=kind, parameters=copy.deepcopy(p))))
        if case in ('B01','B04'):
            f = scalar_facts()
            if case == 'B01': f['fields'][4]['domain'].append('CRITICAL')
            else:
                f['storage']['version'] = 4
                f['fields'].append(dict(name='source',type='string',domain=[],nullable=False,preservation='verbatim'))
                f['creation']['bindings'].append(dict(field='source',source='input',value=None,default=dict(value='',trigger='omitted',boundary='creation')))
                f['evolution'].append(dict(**{'from':3,'to':4},defaults={'source':''},boundary='explicit_migration',preservation='unrelated_fields'))
            r['domains'].update(capability_profile='existing-scalar-1', scalar_base_model=MODEL)
            for facet,value in f.items(): add(facet,'crud',dict(profile='existing-scalar-1',facet=facet,value=value),source)
            # enum order is rank authority; no task sort by priority is requested.
            r['interpretation_notes'] = ['CRITICAL above HIGH means accepted enum order, not list priority sorting; missing priority creation/legacy rules remain baseline authority.'] if case=='B01' else []
        if case in ('B03','B05','B06','B10'):
            field,param,typ = {'B03':('tags','tag','strings'),'B05':('status','status','string'),'B06':('category','category','string'),'B10':('owner','owner','string')}[case]
            r['domains'].update(capability_profile='collection-query-1',collection_store=dict(kind='model_state',model=MODEL,state='state_tasks'))
            for facet,value in query_facts(field,param,typ).items(): add('list-'+param+'/'+facet,'filter_order',dict(query='list-'+param,facet=facet,value=value))
        for kind,family,value in DEMANDS.get(case,[]): add(family,kind,dict(required_capability=family, specification=value))
        if case in ('B12', 'B13'):
            r['domains'].update(capability_profile='existing-model-1',existing_base_model=MODEL)
            if case == 'B13':
                r['rows'] = []
                add('guards','crud',dict(profile='existing-model-1',facet='guards',value=[dict(command=command,field='archived',value=False,error='invalid_transition',rejection='unchanged') for command in ('complete','append-note')]))
                add('precursor-store','invariant',dict(required_capability='precursor_store',specification=dict(fields={'archived':'boolean','notes':'ordered_strings'},preserve=['B11_delete','list-archived'],absent_operations=['unarchive','reopen'])))
            else:
                r['rows'] = []
                add('clock_queries','crud',dict(profile='existing-model-1',facet='clock_queries',value=[dict(command='list-urgent',predicates=[dict(kind='field_equals',field='archived',value=False),dict(kind='field_equals',field='status',value='pending'),dict(kind='field_before_clock',field='due_date',clock='utc_clock')],order=['created_at','id'],result='whole_records',effect='read_only')]))
                add('scalar-in-set','filter_order',dict(required_capability='scalar_in_set',specification=dict(command='list-urgent',field='priority',operator='in',values=['HIGH','CRITICAL'],composition='conjoin_with_clock_selection',preserve='list-overdue_all_priorities')))
        result.append(r)
    return result
