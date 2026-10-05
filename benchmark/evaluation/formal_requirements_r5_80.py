"""Experimental FRC bookkeeping and bounded projection; no prose interpretation/I/O.

Review is external evidence, never inferred by these functions. Exact relation
comparison is deliberately not a general semantic-equivalence procedure.
"""
import copy
import hashlib
import json
import math

from benchmark.evaluation import benchmark_documents_v1 as v1

VERSION = 'FormalRequirementContract-0.1'
KINDS = ('sum', 'increment', 'crud', 'filter_order', 'normalize_ascii',
         'transition', 'invariant', 'persist', 'optional_dispatch',
         'selection_prefix', 'effects', 'priority_extension', 'priority_rank',
         'priority_create', 'priority_list', 'priority_filter',
         'migration_preserve', 'default', 'public_state_alternatives',
         'durable_content_constraints')
CHECKS = ('source_coverage', 'no_invention', 'ambiguity', 'conflict',
          'neutrality', 'identity', 'consistency', 'fidelity')
OUTCOMES = ('APPROVED', 'REJECTED', 'NEEDS_CLARIFICATION',
            'CONFLICTING_REQUIREMENT', 'INCOMPLETE_FORMALIZATION')


class ContractError(ValueError):
    def __init__(self, code):
        self.code = code
        super().__init__(code)

    def record(self):
        return {'code': self.code}


def canonical(value):
    def json_value(node):
        if type(node) is dict:
            _require(all(type(key) is str for key in node), 'NON_JSON_VALUE')
            for child in node.values():
                json_value(child)
        elif type(node) is list:
            for child in node:
                json_value(child)
        else:
            _require(type(node) in (str, int, float, bool, type(None)), 'NON_JSON_VALUE')
            _require(type(node) is not float or math.isfinite(node), 'NON_JSON_VALUE')
    json_value(value)
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(',', ':'), allow_nan=False).encode('utf-8')


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def _require(condition, code='MALFORMED_FRC'):
    if not condition:
        raise ContractError(code)


def _text(value):
    return type(value) is str and bool(value.strip())


def validate(contract):
    """Closed envelope/entry validation plus identity/provenance cross checks.

    This validates records, not behavioral fidelity, implication entailment,
    arbitrary consistency, reviewer authority or natural-language completeness.
    """
    try:
        canonical(contract)
    except ContractError:
        raise
    except (TypeError, ValueError, RecursionError):
        raise ContractError('MALFORMED_FRC') from None
    _require(type(contract) is dict and set(contract) == {
        'schema_version', 'contract_id', 'revision', 'source', 'context',
        'obligations', 'issues', 'unspecified', 'implementation_choices',
        'lineage', 'formalizer', 'review'})
    _require(contract['schema_version'] == VERSION, 'UNSUPPORTED_FRC_VERSION')
    _require(_text(contract['contract_id']) and _text(contract['formalizer']))
    _require(type(contract['revision']) is int and contract['revision'] >= 1)
    source = contract['source']
    _require(type(source) is dict and set(source) == {'id', 'text', 'sha256', 'classification'})
    _require(_text(source['id']) and _text(source['text']))
    _require(source['classification'] in ('SYNTHETIC', 'PUBLIC'))
    _require(source['sha256'] == hashlib.sha256(source['text'].encode('utf-8')).hexdigest(),
             'SOURCE_COMMITMENT_MISMATCH')
    context = contract['context']
    _require(type(context) is dict and set(context) == {
        'scope', 'domains', 'assumptions', 'component_authority'})
    _require(_text(context['scope']) and type(context['domains']) is dict
             and type(context['assumptions']) is list)
    _require(all(_text(x) for x in context['assumptions']))
    _require(context['component_authority'] is None or type(context['component_authority']) is dict)
    for name in ('obligations', 'issues', 'unspecified', 'implementation_choices', 'lineage'):
        _require(type(contract[name]) is list)
    _require(all(_text(x) for name in ('unspecified', 'implementation_choices') for x in contract[name]))
    _require(contract['review'] is None, 'REVIEW_MUST_BE_SEPARATE')
    ids = []
    for obligation in contract['obligations']:
        _require(type(obligation) is dict and set(obligation) == {
            'id', 'basis', 'source_quote', 'derived_from', 'relation', 'statement'})
        _require(_text(obligation['id']) and _text(obligation['statement']))
        _require(obligation['basis'] in ('STATED', 'NECESSARY_IMPLICATION'))
        _require(_text(obligation['source_quote']) and obligation['source_quote'] in source['text'],
                 'UNBOUND_SOURCE_QUOTE')
        _require(type(obligation['derived_from']) is list)
        _require(all(_text(x) for x in obligation['derived_from']))
        _require((obligation['basis'] == 'NECESSARY_IMPLICATION') == bool(obligation['derived_from']))
        relation = obligation['relation']
        _require(type(relation) is dict and set(relation) == {'kind', 'parameters'})
        _require(relation['kind'] in KINDS, 'UNKNOWN_RELATION')
        _require(type(relation['parameters']) is dict)
        ids.append(obligation['id'])
    _require(len(ids) == len(set(ids)), 'DUPLICATE_OBLIGATION')
    graph = {o['id']: o['derived_from'] for o in contract['obligations']}
    def visit(node, active):
        _require(node not in active, 'CYCLIC_DERIVATION')
        for parent in graph[node]:
            _require(parent in graph, 'UNBOUND_DERIVATION')
            visit(parent, active | {node})
    for node in graph:
        visit(node, set())
    issue_ids = []
    for issue in contract['issues']:
        _require(type(issue) is dict and set(issue) == {
            'id', 'category', 'description', 'affects', 'alternatives', 'witness', 'resolved'})
        _require(_text(issue['id']) and _text(issue['description']))
        _require(issue['category'] in ('AMBIGUITY', 'CONFLICT', 'QUESTION'))
        _require(type(issue['affects']) is list and all(x in ids for x in issue['affects']))
        _require(type(issue['alternatives']) is list and all(_text(x) for x in issue['alternatives']))
        _require(issue['witness'] is None or type(issue['witness']) is dict)
        # v0.1 does not implement source-owner resolution; new source revision required.
        _require(issue['resolved'] is False, 'UNSUPPORTED_RESOLUTION')
        issue_ids.append(issue['id'])
    _require(len(issue_ids) == len(set(issue_ids)) and not set(issue_ids) & set(ids),
             'DUPLICATE_IDENTITY')
    for row in contract['lineage']:
        _require(type(row) is dict and set(row) == {'change', 'previous', 'current', 'reason'})
        _require(row['change'] in ('retire', 'split', 'merge', 'meaning_change'))
        _require(type(row['previous']) is list and type(row['current']) is list)
        _require(all(_text(x) for x in row['previous']) and all(x in ids for x in row['current']))
        _require(_text(row['reason']))
    return digest(contract)


def review_gate(contract, receipt):
    commitment = validate(contract)
    _require(type(receipt) is dict and set(receipt) == {
        'contract_commitment', 'reviewer', 'outcome', 'checks', 'findings'}, 'MALFORMED_REVIEW')
    _require(receipt['contract_commitment'] == commitment, 'STALE_REVIEW')
    _require(_text(receipt['reviewer']) and receipt['reviewer'] != contract['formalizer'],
             'NONINDEPENDENT_REVIEW')
    _require(receipt['outcome'] in OUTCOMES and type(receipt['findings']) is list, 'MALFORMED_REVIEW')
    _require(type(receipt['checks']) is dict and set(receipt['checks']) == set(CHECKS), 'INCOMPLETE_REVIEW')
    _require(all(type(x) is bool for x in receipt['checks'].values()), 'MALFORMED_REVIEW')
    if any(i['category'] == 'CONFLICT' for i in contract['issues']):
        return 'CONFLICTING_REQUIREMENT'
    if contract['issues']:
        return 'NEEDS_CLARIFICATION'
    if receipt['outcome'] == 'APPROVED':
        _require(all(receipt['checks'].values()), 'FAILED_APPROVAL_CHECK')
        _require(bool(contract['obligations']), 'EMPTY_APPROVAL')
    return receipt['outcome']


def check_revision(previous, current):
    """One-edge stable identity/lineage check; historical ID reuse needs a ledger.

    This does not decide semantic change: conservative clause-byte changes must
    be declared even when a reviewer might prove a paraphrase meaning-preserving.
    """
    validate(previous)
    validate(current)
    _require(previous['contract_id'] == current['contract_id'], 'REVISION_ID_MISMATCH')
    _require(current['revision'] == previous['revision'] + 1, 'REVISION_SEQUENCE_MISMATCH')
    before = {o['id']: o for o in previous['obligations']}
    after = {o['id']: o for o in current['obligations']}
    events = current['lineage']
    for event in events:
        _require(all(x in before for x in event['previous']), 'UNBOUND_PRIOR_ID')
        old, new = event['previous'], event['current']
        if event['change'] == 'retire':
            _require(bool(old) and not new and not set(old) & set(after), 'INVALID_LINEAGE')
        elif event['change'] in ('split', 'merge'):
            _require(bool(old) and bool(new) and not set(old) & set(after)
                     and not set(new) & set(before), 'INVALID_LINEAGE')
            _require((len(old) == 1 and len(new) >= 2) if event['change'] == 'split'
                     else (len(old) >= 2 and len(new) == 1), 'INVALID_LINEAGE')
        else:
            _require(old == new and bool(old), 'INVALID_LINEAGE')
    retired = {x for e in events if e['change'] in ('retire', 'split', 'merge') for x in e['previous']}
    declared = {x for e in events if e['change'] == 'meaning_change' for x in e['current']}
    _require(set(before) - set(after) <= retired, 'UNDECLARED_RETIREMENT')
    for oid in set(before) & set(after):
        fields = ('relation', 'statement', 'source_quote', 'basis', 'derived_from')
        if any(before[oid][field] != after[oid][field] for field in fields):
            _require(oid in declared, 'UNDECLARED_MEANING_CHANGE')
    return {'status': 'REVISION_EDGE_VALID', 'new_ids': sorted(set(after) - set(before)),
            'retired_ids': sorted(set(before) - set(after))}


def compare_relations(left, right):
    """Only exact recognized clause equality/subset, never provider-based meaning.

    Statements/context/issues are retained in scope identity; different natural
    language is REFER_TO_REVIEW rather than guessed equivalent. IDs, provenance
    of authorship and array order do not enter the clause set.
    """
    validate(left)
    validate(right)
    if canonical(left) == canonical(right):
        return {'classification': 'STRUCTURALLY_IDENTICAL', 'scope': 'complete-record'}
    scope = lambda c: [c['source']['id'], c['context'], c['unspecified'],
                       [[i['category'], i['description'], i['alternatives'], i['witness']] for i in c['issues']]]
    if canonical(scope(left)) != canonical(scope(right)):
        return {'classification': 'REFER_TO_REVIEW', 'scope': 'different-domain-or-issues'}
    atoms = lambda c: {canonical({'relation': o['relation'], 'statement': o['statement']})
                       for o in c['obligations']}
    a, b = atoms(left), atoms(right)
    if a == b:
        result = 'EXACT_CLAUSE_EQUIVALENT'
    elif a < b or b < a:
        result = 'CLAUSE_SUBSET_REQUIRES_REVIEW'
    else:
        result = 'REFER_TO_REVIEW'
    return {'classification': result, 'scope': 'bounded-exact-declarative-clauses',
            'left_only': len(a - b), 'right_only': len(b - a)}


def project(contract, receipt):
    """Complete calibrated-context projection or explicit failure; no partial bytes.

    The only positive rule is an explicitly source-authorized complete public
    component context plus the two already-defined V1 supplemental kinds.
    Generic behavioral relations have no faithful full mapping in this prototype.
    This conservatively reports an adapter gap, not a proof of V1 impossibility.
    """
    outcome = review_gate(contract, receipt)
    if outcome != 'APPROVED':
        return {'status': 'NOT_APPROVED', 'review_outcome': outcome}
    context = contract['context']['component_authority']
    unsupported = [o['id'] for o in contract['obligations'] if o['relation']['kind'] not in
                   ('public_state_alternatives', 'durable_content_constraints')]
    if context is None or unsupported:
        return {'status': 'UNREPRESENTABLE_SOURCE', 'gap': 'NO_QUALIFIED_COMPLETE_MAPPING',
                'obligations_without_mapping': unsupported,
                'missing_component_authority': context is None}
    try:
        _require(set(context) == {'application', 'configuration'}, 'INVALID_COMPONENT_AUTHORITY')
        obligations = []
        coverage = []
        for o in contract['obligations']:
            relation = o['relation']
            requirement = {'kind': relation['kind'], **copy.deepcopy(relation['parameters'])}
            # Prevent parameters from overriding the normative kind.
            _require('kind' not in relation['parameters'], 'INVALID_COMPONENT_AUTHORITY')
            obligations.append({'id': o['id'], 'requirement': requirement})
            coverage.append({'frc_id': o['id'], 'v1_id': o['id']})
        document = {'schema_version': v1.VERSION, 'document_id': 'r5-80-' + validate(contract),
                    'role': 'behavioral', 'payload': {**copy.deepcopy(context), 'obligations': obligations}}
        normalized = v1.assemble([document])
    except (v1.DocumentError, ContractError):
        return {'status': 'UNREPRESENTABLE_SOURCE', 'gap': 'INVALID_V1_COMPONENTS'}
    recovered = recover(normalized, contract)
    _require(compare_relations(contract, recovered)['classification'] in
             ('STRUCTURALLY_IDENTICAL', 'EXACT_CLAUSE_EQUIVALENT'), 'PRESERVATION_FAILURE')
    return {'status': 'PROJECTED', 'document': document, 'normalized': normalized,
            'coverage': coverage, 'context_commitment': digest(context),
            'recovered_relation_commitment': digest([o['relation'] for o in recovered['obligations']])}


def recover(normalized, original):
    """Recover recognized V1 clauses; retain original provenance for comparison.

    Not a prose reconstruction. Compare exact complete component context as well
    as every supplemental ID, including detection of added/dropped clauses.
    """
    v1.verify_contract(normalized)
    _require({'application': normalized['application'], 'configuration': normalized['configuration']}
             == original['context']['component_authority'], 'CONTEXT_PRESERVATION_FAILURE')
    entries = {entry['id']: entry['requirement'] for entry in normalized['obligations']}
    _require(set(entries) == {o['id'] for o in original['obligations']}, 'OBLIGATION_PRESERVATION_FAILURE')
    result = copy.deepcopy(original)
    for o in result['obligations']:
        requirement = entries[o['id']]
        _require(requirement['kind'] in ('public_state_alternatives', 'durable_content_constraints'),
                 'UNSUPPORTED_RECOVERY')
        o['relation'] = {'kind': requirement['kind'],
                         'parameters': {k: copy.deepcopy(v) for k, v in requirement.items() if k != 'kind'}}
    return result


def projection_gate(contract, review, projected, receipt):
    """Separate content-bound projection review; no production authority issued."""
    _require(review_gate(contract, review) == 'APPROVED', 'UNAPPROVED_FRC')
    _require(type(projected) is dict and projected.get('status') == 'PROJECTED', 'NO_COMPLETE_PROJECTION')
    _require(v1.assemble([projected['document']]) == projected['normalized'], 'PROJECTION_DOCUMENT_MISMATCH')
    expected = [{'frc_id': o['id'], 'v1_id': o['id']} for o in contract['obligations']]
    _require(projected['coverage'] == expected, 'PROJECTION_COVERAGE_MISMATCH')
    _require(compare_relations(contract, recover(projected['normalized'], contract))['classification']
             in ('STRUCTURALLY_IDENTICAL', 'EXACT_CLAUSE_EQUIVALENT'), 'PRESERVATION_FAILURE')
    _require(type(receipt) is dict and set(receipt) == {
        'contract_commitment', 'document_commitment', 'coverage_commitment', 'behavioral_identity',
        'reviewer', 'outcome', 'checks', 'findings'}, 'MALFORMED_PROJECTION_REVIEW')
    _require(receipt['contract_commitment'] == validate(contract)
             and receipt['document_commitment'] == digest(projected['document'])
             and receipt['coverage_commitment'] == digest(projected['coverage'])
             and receipt['behavioral_identity'] == projected['normalized']['identity'], 'STALE_PROJECTION_REVIEW')
    _require(_text(receipt['reviewer']) and receipt['reviewer'] != contract['formalizer'], 'NONINDEPENDENT_REVIEW')
    checks = ('coverage', 'no_weakening', 'no_invention', 'context_identity', 'supplemental_identity')
    _require(type(receipt['checks']) is dict and set(receipt['checks']) == set(checks)
             and all(type(v) is bool for v in receipt['checks'].values()), 'INCOMPLETE_PROJECTION_REVIEW')
    _require(receipt['outcome'] == 'APPROVED_PROJECTION' and all(receipt['checks'].values()), 'UNAPPROVED_PROJECTION')
    _require(type(receipt['findings']) is list, 'MALFORMED_PROJECTION_REVIEW')
    return {'status': 'APPROVED_PROJECTION', 'scope': 'public-explicit-component-calibration',
            'behavioral_identity': projected['normalized']['identity'], 'production_authority': False}
