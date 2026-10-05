"""Manually authored candidates, not an automatic natural-language formalizer.

Only the explicit public allowlist below is read. Materialization is qualification
evidence generation; it never opens protected resources or queries support.
"""
import copy
import hashlib
import json
from pathlib import Path

from benchmark.evaluation import formal_requirements_r5_80 as frc

ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent


def candidates():
    corpus = json.loads((HERE / 'corpus.json').read_text(encoding='utf-8'))
    sources = {s['id']: s['text'] for s in corpus['sources']}
    sources['B01'] = (ROOT / 'benchmark/requirements/B01.md').read_text(encoding='utf-8')
    result = {}
    for name, text in sources.items():
        result[name] = {'schema_version': frc.VERSION, 'contract_id': 'R5.80.' + name,
            'revision': 1, 'source': {'id': name, 'text': text,
                'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
                'classification': 'PUBLIC' if name == 'B01' else 'SYNTHETIC'},
            'context': {'scope': 'Requirement-local abstract observable behavior; no imported baseline.',
                        'domains': {}, 'assumptions': [], 'component_authority': None},
            'obligations': [], 'issues': [], 'unspecified': [],
            'implementation_choices': ['Algorithms, internal representations and storage mechanisms remain open unless explicitly constrained by the source.'],
            'lineage': [], 'formalizer': 'R5.80.coordinator', 'review': None}

    def add(name, kind, parameters, statement, quote, parents=()):
        c = result[name]
        oid = name + '.O' + str(len(c['obligations']) + 1).zfill(2)
        c['obligations'].append({'id': oid, 'basis': 'NECESSARY_IMPLICATION' if parents else 'STATED',
            'source_quote': quote, 'derived_from': list(parents),
            'relation': {'kind': kind, 'parameters': parameters}, 'statement': statement})
        return oid

    def issue(name, category, description, alternatives, witness=None):
        c = result[name]
        c['issues'].append({'id': name + '.I' + str(len(c['issues']) + 1),
            'category': category, 'description': description,
            'affects': [o['id'] for o in c['obligations']], 'alternatives': alternatives,
            'witness': witness, 'resolved': False})

    add('S01', 'sum', {'inputs': {'x': 'integer', 'y': 'integer'}, 'output': 'x+y'},
        'For every pair of mathematical integers x,y, result equals x+y exactly.', 'Given two integers x and y, return their sum.')
    add('S01', 'effects', {'state_changes': 0, 'external_effects': 0},
        'No state changes or external effects occur on the specified domain.', 'No state or external effects are permitted.')
    result['S01']['unspecified'] = ['Invalid/noninteger input behavior, transport and result encoding.']
    for operation, post, quote in (
        ('create', 'key maps to supplied text', 'Create a note with a caller-supplied unique key and text.'),
        ('read', 'return text of supplied existing key', 'Reading that key returns its text.'),
        ('update', 'key maps to replacement text', 'Updating that key replaces only its text.'),
        ('delete', 'key is absent', 'Deleting that key makes it absent.')):
        add('S02', 'crud', {'operation': operation, 'postcondition': post,
            'domain': 'unique new key for create; existing key otherwise'},
            operation + ': ' + post + '; applies only to the stated key domain.', quote)
    add('S02', 'invariant', {'frame': 'all other notes unchanged'},
        'Every specified operation preserves every other note.', 'Other notes remain unchanged.')
    result['S02']['unspecified'] = ['Absent and duplicate key behavior, validation, persistence and response encoding.']
    add('S03', 'filter_order', {'membership': 'exact active input occurrences',
        'order': 'ascending lexicographic Unicode code points of name', 'ties': 'input occurrence order', 'frame': 'input unchanged'},
        'Return each active input occurrence once, unchanged, ordered by name code points with stable ties; preserve input.', sources['S03'])
    issue('S03', 'AMBIGUITY', 'The active field has no type or activation interpretation.',
          ['Boolean true only', 'A domain-specific activation predicate'])
    result['S03']['unspecified'] = ['Malformed records, unrelated state/effects, copying and wire representation.']
    add('S04', 'normalize_ascii', {'domain': 'ASCII strings', 'trim': 'U+0020 at both ends',
        'case': 'A-Z to a-z', 'preserve': 'internal spaces and all other characters'},
        'For every ASCII string, trim only endpoint ASCII spaces and lowercase only A-Z, preserving internal spaces and other characters.', sources['S04'])
    result['S04']['unspecified'] = ['Non-ASCII/invalid inputs, state/effects and encoding.']
    add('S05', 'transition', {'initial': 'OPEN', 'operation': 'close', 'pre': 'OPEN', 'post': 'CLOSED', 'result': 'CLOSED'},
        'A ticket initially is OPEN; closing OPEN changes it to CLOSED and returns CLOSED.',
        'A ticket starts OPEN. Closing an OPEN ticket changes it to CLOSED and returns CLOSED.')
    add('S05', 'transition', {'operation': 'close', 'pre': 'CLOSED', 'post': 'unchanged', 'result': 'ALREADY_CLOSED'},
        'Closing CLOSED returns ALREADY_CLOSED and changes no state.', 'Closing a CLOSED ticket returns ALREADY_CLOSED and changes no state.')
    add('S05', 'invariant', {'domain': ['OPEN', 'CLOSED'], 'frame': 'other tickets unchanged'},
        'Tickets are always OPEN or CLOSED; no other ticket changes.', 'No other ticket changes. Tickets must always be OPEN or CLOSED.')
    result['S05']['unspecified'] = ['Invalid tickets, persistence, result encoding and external effects.']
    add('S06', 'persist', {'key': 'supplied key', 'value': 'integer', 'read': 'last successful store', 'horizon': 'includes process restart'},
        'Store the supplied integer at the supplied key; later reads, including after restart, return the last successfully stored integer.',
        'Store a supplied integer under a supplied key. A later read of that key, including after process restart, returns the last successfully stored integer.')
    add('S06', 'persist', {'when': 'storage fails', 'result': 'STORAGE_ERROR', 'frame': 'all previously readable values preserved'},
        'Storage failure returns STORAGE_ERROR and preserves all previously readable values.',
        'If storage fails, return STORAGE_ERROR and preserve all previously readable values.')
    result['S06']['unspecified'] = ['Unstored keys, invalid inputs, concurrent writes, non-storage failures and encoding.']
    add('S07', 'optional_dispatch', {'domain': 'abstract objects; mathematical integers distinct from booleans',
        'branches': {'omitted': 'ABSENT', 'null': 'NULL', 'integer': 'same integer', 'other_present': 'INVALID'}},
        'Distinguish omitted, explicit null, mathematical integer and other present value; return ABSENT, NULL, the integer and INVALID respectively.',
        'Given an object with an optional nullable integer value, return ABSENT when value is omitted, NULL when it is explicitly null, and that integer otherwise. Return INVALID for any other present value.')
    add('S07', 'effects', {'state_changes': 0, 'external_effects': 0},
        'Every specified object-input branch, including INVALID, changes no state and has no external effects.',
        'Produce no state changes or external effects.')
    result['S07']['context']['domains'] = {'integer': 'mathematical integers; abstract type, not a host-language encoding'}
    result['S07']['unspecified'] = ['Non-object outer input; concrete encoding of integer and symbolic outcomes. Interface qualification needed before executable deployment.']
    add('S08', 'filter_order', {'predicate': {'unresolved': 'best'}},
        'Return tasks satisfying the unresolved best predicate; no ranking is chosen.', sources['S08'])
    issue('S08', 'AMBIGUITY', 'Best has no selection criterion, population or cardinality.',
          ['Highest priority', 'Most recent', 'Requester-defined score'])
    result['S08']['unspecified'] = ['Task schema, inputs, ties, effects and errors.']
    add('S09', 'filter_order', {'membership': 'all input occurrences', 'order': 'input insertion order'},
        'For every name sequence return all names preserving their input insertion order.',
        'For every input sequence of names, return all names in insertion order')
    add('S09', 'filter_order', {'membership': 'all input occurrences', 'order': 'alphabetical ascending'},
        'The same output must always be alphabetically ascending.', 'always sorted alphabetically ascending.')
    issue('S09', 'CONFLICT', 'The universal insertion and ascending-order obligations conflict for input [z,a] under ordinary a<z.',
          ['Requester revises insertion-order clause', 'Requester revises alphabetical-order clause'],
          {'input': ['z', 'a'], 'insertion': ['z', 'a'], 'ascending': ['a', 'z']})
    result['S09']['unspecified'] = ['Alphabetical collation for other names, input mutation, encoding and errors.']
    add('S10', 'increment', {'input': 'mathematical integer n>0', 'output': 'n+1'},
        'For every positive mathematical integer n return n+1 exactly.', sources['S10'])
    result['S10']['unspecified'] = ['Zero, negative, noninteger, missing and malformed inputs: no rejection policy.', 'State changes, external effects, interface and encoding.']
    add('S11', 'selection_prefix', {'input': 'integer sequence', 'limit': 'nonnegative integer',
        'predicate': 'value>0', 'membership': 'earliest qualifying occurrences up to limit', 'order': 'input order', 'frame': 'input unchanged'},
        'Return the earliest positive occurrences, preserving input order, with length min(limit, number of positives); zero limit returns empty; do not mutate input.', sources['S11'])
    result['S11']['unspecified'] = ['Invalid sequences/limits, unrelated effects and encoding.']
    add('S12', 'transition', {'when': 'accepted; positive count c', 'precondition': 'c<=available',
        'post': 'available_before-c', 'result': 'available_after'},
        'Accepted positive-count requests require c<=available, subtract exactly c and return the remaining count.',
        'On an accepted reservation, reduce available seats by the requested positive count and return the remaining count. Accept only when the requested count does not exceed available seats.')
    add('S12', 'transition', {'when': 'positive count exceeds available', 'result': 'INSUFFICIENT', 'frame': 'all state unchanged'},
        'Insufficient-seat requests return INSUFFICIENT and change nothing.', 'Otherwise return INSUFFICIENT and change nothing.')
    add('S12', 'invariant', {'condition': 'available seats>=0', 'scope': 'always'},
        'Available seats are always nonnegative.', 'Available seats must never be negative.')
    add('S12', 'effects', {'success_confirmations': 1, 'rejection_confirmations': 0, 'recipient': 'caller'},
        'Emit exactly one caller confirmation on success and none on rejection; other effects are not constrained.',
        'Emit exactly one confirmation to the caller on success and none on rejection.')
    issue('S12', 'AMBIGUITY', 'Accept only when may not require acceptance of all sufficient-seat requests; otherwise scope is unresolved.',
          ['Capacity is sole acceptance criterion', 'Other acceptance criteria allowed, needing definition'])
    result['S12']['unspecified'] = ['Invalid counts, concurrency, persistence, confirmation content/timing/failure and unrelated successful state effects.']
    text = sources['B01']
    add('B01', 'priority_extension', {'added': 'CRITICAL', 'retained': ['LOW', 'NORMAL', 'HIGH']},
        'Add accepted priority CRITICAL without removing existing LOW, NORMAL or HIGH.', 'Add `CRITICAL` above `HIGH` to accepted task priorities.')
    add('B01', 'priority_rank', {'higher': 'CRITICAL', 'lower': 'HIGH'},
        'CRITICAL ranks above HIGH; no list-output sorting follows from rank alone.', 'Add `CRITICAL` above `HIGH` to accepted task priorities.')
    add('B01', 'priority_create', {'argument': 'CRITICAL', 'persisted': 'CRITICAL', 'returned': 'CRITICAL', 'when': 'other creation requirements satisfied'},
        'create --priority CRITICAL accepts, persists and returns CRITICAL when unrelated creation preconditions hold.',
        '`create --priority\nCRITICAL` persists and returns that value')
    add('B01', 'priority_list', {'included_priority': 'CRITICAL'},
        'list includes existing CRITICAL tasks with their priority.', '`list` includes it.')
    filter_id = add('B01', 'priority_filter', {'command': 'list-high', 'criterion': 'priority equals HIGH'},
        'list-high has exactly the HIGH equality priority criterion, not HIGH-or-above.', '`list-high`\ncontinues to mean exactly `HIGH`.')
    add('B01', 'priority_filter', {'command': 'list-high', 'excluded_priorities': ['CRITICAL', 'LOW', 'NORMAL']},
        'CRITICAL, LOW and NORMAL do not satisfy the list-high priority criterion.', '`list-high`\ncontinues to mean exactly `HIGH`.', [filter_id])
    add('B01', 'migration_preserve', {'priorities': ['LOW', 'NORMAL', 'HIGH'], 'post': 'same value per existing task'},
        'Migration preserves each existing LOW, NORMAL and HIGH task priority.',
        'Existing LOW, NORMAL and HIGH tasks retain\ntheir values through migration.')
    add('B01', 'default', {'field': 'priority', 'when': 'missing; context unresolved', 'value': 'NORMAL'},
        'Missing priority defaults to NORMAL; omission context must be clarified for executable use.',
        'A missing priority still defaults to NORMAL.')
    issue('B01', 'AMBIGUITY', 'Missing priority can denote omitted create argument or missing historical stored field; requirement-local source does not define the entire baseline.',
          ['Omitted creation argument only', 'Omitted creation argument and legacy stored field'])
    result['B01']['unspecified'] = ['Complete task schema, other creation preconditions, response formats, storage format, migration protocol, invalid/null priority and output order.']
    # Additional public calibration: explicit behavioral component context is
    # selected by this source, not invented by a prose-to-V1 projector.
    from benchmark.harness.test_optional_support_r5_41 import setup
    app, transport, state, launch = setup(domain=[None, 17])
    context = {'application': app, 'configuration': {'transport': transport, 'state': state, 'launch': launch}}
    source = ('Use the complete public optional-measurement application and configuration supplied in component context '
              + frc.digest(context) + '. Require public state alternatives for route store. '
              'Require exactly the supplied durable content constraints for V1, including value domain null or 17 when present. '
              'No additional supplemental obligations are required.')
    result['P01'] = copy.deepcopy(result['S01'])
    c = result['P01']
    c.update(contract_id='R5.80.P01', obligations=[], unspecified=[], issues=[])
    c['source'] = {'id': 'P01', 'text': source, 'sha256': hashlib.sha256(source.encode()).hexdigest(), 'classification': 'SYNTHETIC'}
    c['context'] = {'scope': 'Complete explicitly source-selected public component calibration; not arbitrary prose.',
        'domains': {}, 'assumptions': ['The supplied complete application/configuration is normative context selected by this source.'],
        'component_authority': context}
    add('P01', 'public_state_alternatives', {'public': ['store']},
        'All declared public state alternatives cover store.', 'Require public state alternatives for route store.')
    add('P01', 'durable_content_constraints', {'requirements': {'V1': copy.deepcopy(state['alternatives']['V1']['constraints'])}},
        'The supplied V1 durable content constraints apply exactly, including optional value domain null or 17.',
        'Require exactly the supplied durable content constraints for V1, including value domain null or 17 when present.')
    for c in result.values():
        frc.validate(c)
    return result


def adversarial(base):
    leak = copy.deepcopy(base['S10'])
    leak['contract_id'] += '.leak'
    leak['obligations'].append({'id': 'S10.LEAK', 'basis': 'STATED',
        'source_quote': 'return n plus one', 'derived_from': [],
        'relation': {'kind': 'increment', 'parameters': {'algorithm': 'specific loop', 'storage_engine': 'SQLite'}},
        'statement': 'Implement the increment using a specific loop and SQLite storage.'})
    missing = copy.deepcopy(base['S10'])
    missing['contract_id'] += '.missing'
    missing['obligations'] = []
    invented = copy.deepcopy(base['S10'])
    invented['contract_id'] += '.invented'
    invented['obligations'].append({'id': 'S10.INVALID', 'basis': 'STATED', 'source_quote': 'For a positive integer n',
        'derived_from': [], 'relation': {'kind': 'transition', 'parameters': {'when': 'invalid input', 'result': 'INVALID'}},
        'statement': 'Reject all nonpositive inputs with INVALID.'})
    return {'LEAK': leak, 'MISSING': missing, 'INVENTED': invented}


if __name__ == '__main__':
    values = candidates()
    values.update(adversarial(values))
    (HERE / 'candidates.json').write_text(json.dumps(values, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({'candidate_count': len(values), 'identities': {k: frc.validate(v) for k, v in values.items()}}, indent=2))
