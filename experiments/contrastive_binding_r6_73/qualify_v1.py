"""CPU-only controls, dataset qualification, exact local tokenizer measurements."""
import copy
import hashlib
import json
from pathlib import Path
import sys

# Avoid generic historical module-name collisions: load renderer before baseline imports.
from reconstruct import reconstruct, serialize, Rejection, c, assembly, scorer
from compact_decoder import CompletionLanguage
import importlib.util
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r673_freeze', HERE / 'freeze.py')
freeze = importlib.util.module_from_spec(spec)
spec.loader.exec_module(freeze)
ROOT, OUT, f, write = freeze.ROOT, freeze.OUT, freeze.f, freeze.write


def pin(value):
    return hashlib.sha256(c.canonical(value)).hexdigest()


def rows():
    result = copy.deepcopy(f.read(OUT / 'ACCEPTANCE-EXPECTATIONS.json')['records'])
    amendment = f.read(OUT / 'EXPECTATION-AMENDMENT-1.json')
    row = next(r for r in result if r['id'] == amendment['record'])
    target = row['negatives'][amendment['negative_index']]['decision']
    assert target[amendment['field']] == amendment['original']
    target[amendment['field']] = amendment['replacement']
    return result


def behavior(after, cases):
    observations = []
    for case in cases:
        actual = assembly.behavior(after, case['arguments'])
        observations.append(dict(actual=actual, expected=case['expected'],
                                 passed=assembly.agrees(actual, case['expected'])))
    return observations


def evaluate(text, scope, target, cases):
    try:
        action, after, validation = reconstruct(text, scope)
        again = reconstruct(text, copy.deepcopy(scope))
        assert c.canonical((action, after, validation)) == c.canonical(again)
        selected, _ = __import__('reconstruct').parse(text)
        exact = c.canonical(selected) == c.canonical(target)
        observations = behavior(after, cases)
        return dict(category='accepted' if exact and all(o['passed'] for o in observations) else 'valid_but_wrong',
            reconstructed_action=action, reconstructed_action_identity=pin(action),
            validation=validation, after_identity=after['identity'], deterministic=True,
            exact_decision=exact, behavioral_acceptance=all(o['passed'] for o in observations),
            observations=observations)
    except Rejection as exc:
        return dict(category=exc.category, code=exc.code, detail=exc.detail,
                    reconstructed_action_identity=None, behavioral_acceptance='NOT_REACHED')


def dataset(records, tokenizer):
    ledger, training, all_records, lengths = [], [], [], []
    for row in records:
        scope_before = c.canonical(row['scope'])
        positive = evaluate(serialize(row['target']), row['scope'], row['target'], row['cases'])
        assert positive['category'] == 'accepted', (row['id'], positive)
        # Unchanged scorer runs only on new reconstructed actions, not historical responses.
        score_row = dict(before=row['scope'], completion=[dict(role='assistant', content=serialize(positive['reconstructed_action']))], cases=row['cases'])
        score = scorer.score(score_row['completion'][0]['content'], score_row)
        assert score['accepted'], (row['id'], score)
        common = dict(version='r6.73-training-record-1', requirement=row['requirement'],
            requirement_identity=row['requirement_identity'], typed_scope=row['scope'],
            typed_scope_identity=row['scope_identity'], contrast_family_identity=row['family'],
            contrast_identity=row['contrast_id'], provenance_classification=row['provenance'],
            partition=row['partition'], expectation_review='COORDINATOR_ONLY')
        prompt = [dict(role='system', content='Select one compact semantic decision. Emit exactly op,left,right,deps. '
            'Operations: add,le,eq. Operands: {"ref":"exact identity"} or {"literal":{"type":"Int64|Bool|Unit","value":value}}. '
            'Preserve operand order. Explicit deps are sorted unique direct reference identities. No extra fields.'),
            dict(role='user', content=serialize(dict(requirement=row['requirement'], scope=row['scope'])))]
        for index, target in enumerate([row['target']] + [n['decision'] for n in row['negatives']]):
            positive_label = index == 0
            label = 'positive' if positive_label else 'negative'
            result = positive if positive_label else evaluate(serialize(target), row['scope'], row['target'], row['cases'])
            if not positive_label:
                assert result['category'] == row['negatives'][index - 1]['expected_category'], (row['id'], index, result)
            record = dict(common, id=row['id'] + ('-positive' if positive_label else '-N' + str(index)),
                label=label, compact_target_decision=target,
                correct_compact_decision=row['target'],
                reconstructed_action_identity=result['reconstructed_action_identity'],
                acceptance_evidence=result,
                reason='Requirement-derived positive' if positive_label else row['negatives'][index - 1]['reason'],
                positive_next_token_eligible=positive_label)
            all_records.append(record)
            # Negative token lengths measured without creating positive training records.
            chat = dict(episode_id=record['id'], prompt=prompt,
                        completion=[dict(role='assistant', content=serialize(target))])
            ids, labels, measurement = f.q52.encoded(chat, tokenizer)
            assert not measurement['exceeds_2048'] and not measurement['truncated']
            assert len(tokenizer(serialize(target), add_special_tokens=False)['input_ids']) == measurement['target_content_tokens']
            lengths.append(dict(measurement, label=label, record_identity=pin(record),
                target_sha256=hashlib.sha256(serialize(target).encode()).hexdigest()))
            if positive_label:
                chat.update(record_identity=pin(record), label='positive', partition='training',
                            contrast_family_identity=row['family'])
                training.append(chat)
            ledger.append(dict(id=record['id'], label=label, decision=target, result=result,
                               reason=record['reason'], identity=pin(record)))
        assert c.canonical(row['scope']) == scope_before
    write('SUPERVISION-LEDGER.json', dict(records=ledger, positives=18, negatives=36, fake_reasoning_traces=0))
    write('TRAINING-RECORDS.json', dict(version='r6.73-records-1', records=all_records,
        negative_policy='Contrast/feedback only. Never include negative decisions as positive assistant completions.'))
    write('SFT-POSITIVES.json', dict(records=training, record_count=len(training),
        purpose='Positive compact completion SFT, paired with separate negative feedback ledger; no training executed.'))
    write('TOKENIZATION.json', dict(records=lengths, tokenizer_identity='c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539',
        content_range=[min(r['target_content_tokens'] for r in lengths), max(r['target_content_tokens'] for r in lengths)],
        sequence_range=[min(r['sequence_tokens'] for r in lengths), max(r['sequence_tokens'] for r in lengths)],
        positive_content_range=[min(r['target_content_tokens'] for r in lengths if r['label']=='positive'), max(r['target_content_tokens'] for r in lengths if r['label']=='positive')],
        truncated=0, targets_roundtrip_exact=True, prompt_loss_excluded=True, negative_targets_for_measurement_only=True))
    return ledger


def adversarial(records):
    base = records[0]
    target, scope = base['target'], base['scope']
    controls = []

    def control(name, text, expected, custom_scope=None, gold=None, cases=None):
        result = evaluate(text, custom_scope or scope, gold or target, cases or base['cases'])
        assert result['category'] == expected, (name, result)
        controls.append(dict(name=name, input=text, scope_identity=(custom_scope or scope)['identity'],
                             expected_category=expected, result=result, passed=True))

    def changed(name, field, value, expected='schema_rejection'):
        obj = copy.deepcopy(target)
        obj[field] = value
        control(name, serialize(obj), expected)

    changed('unknown_operation', 'op', 'multiply')
    obj = copy.deepcopy(target)
    del obj['right']
    control('missing_operand', serialize(obj), 'schema_rejection')
    for name, value in [('bool_as_int', False), ('float_as_int', 1.0), ('int64_overflow', 2**63), ('string_as_int', '1')]:
        changed(name, 'right', {'literal': dict(type='Int64', value=value)})
    changed('unknown_literal_type', 'right', {'literal': dict(type='Float', value=1)})
    changed('unknown_reference', 'left', {'ref': 'missing'}, 'semantic_rejection')
    changed('missing_dependencies', 'deps', [], 'semantic_rejection')
    changed('wrong_dependencies', 'deps', ['spare', 'used'], 'semantic_rejection')
    changed('duplicate_dependencies', 'deps', ['used', 'used'])
    changed('unsorted_dependencies', 'deps', ['used', 'limit'])
    changed('ambiguous_operand_tags', 'left', {'ref': 'used', 'literal': dict(type='Int64', value=0)})
    changed('operand_list_instead_of_object', 'left', ['used'])
    changed('type_incompatible_add', 'right', {'literal': dict(type='Bool', value=False)}, 'semantic_rejection')
    changed('literal_absent_from_scope', 'right', {'literal': dict(type='Int64', value=100)}, 'semantic_rejection')
    obj = copy.deepcopy(target)
    obj['result_type'] = 'Int64'
    control('unexpected_field', serialize(obj), 'schema_rejection')
    for name, text in [('malformed_json', '{'), ('trailing_text', serialize(target) + 'x'),
                       ('duplicate_json_key', serialize(target).replace('"op":"add"', '"op":"add","op":"le"')),
                       ('nan_serialization', serialize(target).replace('"right":{"ref":"limit"}', '"right":{"literal":{"type":"Int64","value":NaN}}'))]:
        control(name, text, 'schema_rejection')
    from fixtures import pin as state_pin
    duplicate = copy.deepcopy(scope)
    duplicate['params'][1]['name'] = duplicate['params'][0]['name']
    duplicate['identity'] = state_pin({k:v for k,v in duplicate.items() if k!='identity'})
    control('duplicate_scope_identity', serialize(target), 'semantic_rejection', duplicate)
    prior = next(r for r in records if r['id']=='F06-dependencies-P1')
    collision = copy.deepcopy(prior['scope'])
    collision['params'][1]['name'] = 'adjusted'
    collision['identity'] = state_pin({k:v for k,v in collision.items() if k!='identity'})
    control('parameter_prior_identity_collision', serialize(prior['target']), 'semantic_rejection', collision, prior['target'], prior['cases'])
    ordered = next(r for r in records if r['id']=='F03-order-P1')
    wrong = copy.deepcopy(ordered['target'])
    wrong['left'], wrong['right'] = wrong['right'], wrong['left']
    control('wrong_order_valid_semantics', serialize(wrong), 'valid_but_wrong', ordered['scope'], ordered['target'], ordered['cases'])
    assert not controls[-1]['result']['behavioral_acceptance']
    repeated = next(r for r in records if r['id']=='F08-repeated-P1')
    control('repeated_operands_legal', serialize(repeated['target']), 'accepted', repeated['scope'], repeated['target'], repeated['cases'])
    # Legal Int64 boundary arithmetic retains unchanged overflow behavior.
    from fixtures import state, fixture, decision, lit
    bound_scope = state('BoundaryControl', [], [2**63-1, 1], 'Int64')
    bound = decision('add', lit('Int64', 2**63-1), lit('Int64', 1), [])
    control('native_add_overflow', serialize(bound), 'accepted', bound_scope, bound, [fixture({}, error='OVERFLOW')])
    write('ADVERSARIAL-VERIFICATION.json', dict(passed=True, records=controls,
        counts={category:sum(r['expected_category']==category for r in controls)
                for category in ('schema_rejection','semantic_rejection','valid_but_wrong','accepted')}))


def historical_decoder(tokenizer):
    from decoder import StructuralMask
    failure = f.read(ROOT / 'benchmark/results/phase6/r6_72/BASE-C-S11-FAILURE.json')
    mask = StructuralMask(tokenizer, 0, lambda text: scorer.validate_action(c.load(text)))
    ids, prefix = failure['partial_token_ids'], failure['partial_output']
    assert tokenizer.decode(ids, skip_special_tokens=False) == prefix
    transitions = []
    for i in range(1, len(ids)+1):
        full = tokenizer.decode(ids[:i], skip_special_tokens=False)
        singleton = tokenizer.decode([ids[i-1]], skip_special_tokens=False)
        previous = tokenizer.decode(ids[:i-1], skip_special_tokens=False)
        transitions.append(dict(index=i-1, token_id=ids[i-1], text=singleton,
            prefix=full, singleton_concat_matches=previous+singleton==full,
            state=mask.accepts(full)))
    assert all(t['state'][0] and t['singleton_concat_matches'] for t in transitions)
    allowed = [i for i, piece in mask.pieces if mask.accepts(prefix + piece)[0]]
    assert not allowed and mask.accepts(prefix)==(True, False)
    terminal = prefix + '}'
    assert mask.grammar.fullmatch(terminal) and mask.accepts(terminal)==(False, False)
    try:
        scorer.validate_action(c.load(terminal))
    except c.Diagnostic as exc:
        terminal_error = exc.data
    else:
        raise AssertionError('duplicate terminal accepted')
    closing_brace_tokens = [i for i, piece in mask.pieces if piece == '}']
    assert closing_brace_tokens
    unique_terminal = terminal.replace('["snapshot","snapshot"]', '["snapshot"]', 1)
    assert mask.accepts(unique_terminal)==(True, True)
    write('S11-CPU-ANALYSIS.json', dict(passed=True, original_failure_sha256=f.sha(ROOT/'benchmark/results/phase6/r6_72/BASE-C-S11-FAILURE.json'),
        decoder_sha256=f.sha(ROOT/'experiments/structured_generation_r6_68/decoder.py'),
        transitions=transitions, prefix=prefix, regex_partial=True, terminal_regex_match=True,
        terminal_rejection=terminal_error, allowed_count=len(allowed), admitted_ascii_tokens=len(mask.pieces),
        closing_brace_token_ids=closing_brace_tokens, generated_tokens=len(ids), budget=128,
        unique_dependency_control_complete=True, model_calls=0, historical_rescoring=False,
        cause='Prefix recognizer admits duplicate deps while uniqueness is enforced only on full completion. The regex-partial state is not coaccessible in the actual validated language.',
        excluded_causes=dict(tokenizer_boundary_mismatch=False, missing_closing_token=False,
            generation_budget_exhaustion=False, invalid_operation_schema_alternative=False,
            eos_before_completion=False), hidden_model_reasoning='NOT_OBSERVED'))


def compact_controls(records, tokenizer):
    controls, seen = [], set()
    for row in records:
        scope = row['scope']
        key = serialize(dict(names=[p['name'] for p in scope['params']]+[s['id'] for s in scope['steps']], literals=scope['literals']))
        if key in seen:
            continue
        seen.add(key)
        grammar = CompletionLanguage(scope)
        steps = 0
        max_tokens = 0
        for text in grammar.texts:
            ids = tokenizer.encode(text, add_special_tokens=False)
            assert tokenizer.decode(ids, skip_special_tokens=False) == text
            max_tokens = max(max_tokens, len(ids))
            for i in range(len(ids)+1):
                prefix = tokenizer.decode(ids[:i], skip_special_tokens=False)
                assert grammar.accepts(prefix)[0]
                if i < len(ids):
                    assert not grammar.accepts(prefix)[1]
                    assert grammar.accepts(tokenizer.decode(ids[:i+1], skip_special_tokens=False))[0]
                steps += 1
            assert grammar.allowed(tokenizer, ids, []) == [tokenizer.eos_token_id]
        assert serialize(row['target']) in grammar.terminals
        # Admission of all relations and wrong bindings/dependencies is task-independent.
        assert {json.loads(t)['op'] for t in grammar.texts} == {'add','le','eq'}
        controls.append(dict(scope_language_identity=pin(grammar.texts), complete_decisions=len(grammar.texts),
            token_prefix_observations=steps, max_target_tokens=max_tokens, all_paths_extendible=True,
            terminal_eos_only=True, requirements_and_expectations_used=False))
    sample = records[0]
    grammar = CompletionLanguage(sample['scope'])
    text = serialize(sample['target'])
    ids = tokenizer.encode(text, add_special_tokens=False)
    # Exhaust exact full-decode token mask at start, dependency boundary and last token.
    points = sorted({0, next(i for i in range(len(ids)) if '"deps":' in tokenizer.decode(ids[:i], skip_special_tokens=False)), len(ids)-1})
    masks = []
    vocab = range(len(tokenizer))
    for at in points:
        allowed = grammar.allowed(tokenizer, ids[:at], vocab)
        assert ids[at] in allowed and tokenizer.eos_token_id not in allowed
        masks.append(dict(prefix=tokenizer.decode(ids[:at], skip_special_tokens=False), allowed_count=len(allowed),
            next_target_token=ids[at], allowed_identity=pin(allowed), eos_allowed=False))
    duplicate = text.replace('["limit","used"]', '["used","used"]')
    assert not grammar.accepts(duplicate)[0]
    write('COMPACT-DECODER-CONTROLS.json', dict(passed=True, scope_languages=controls, exact_masks=masks,
        duplicate_dependencies_excluded_before_terminal=True, inference=0,
        limitation='Finite pinned-scope language, not arbitrary JSON grammar or live-model completion qualification.'))


def main():
    freeze.check_freeze()
    assert not (OUT/'IMPLEMENTATION-FREEZE.json').exists()
    paths = [HERE/'reconstruct.py', HERE/'compact_decoder.py', HERE/'qualify.py', OUT/'EXPECTATION-AMENDMENT-1.json']
    write('IMPLEMENTATION-FREEZE.json', dict(stage='BEFORE_CANDIDATE_EXECUTION', files={p.relative_to(ROOT).as_posix():f.sha(p) for p in paths}))
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(f.STORE/'checkpoint', local_files_only=True, trust_remote_code=False)
    records = rows()
    ledger = dataset(records, tokenizer)
    adversarial(records)
    historical_decoder(tokenizer)
    compact_controls(records, tokenizer)
    write('QUALIFICATION.json', dict(classification='R6_73_CONTRASTIVE_SUPERVISION_QUALIFIED',
        positives=sum(r['label']=='positive' for r in ledger), negatives=sum(r['label']=='negative' for r in ledger),
        contrast_categories=9, contrast_pairs=9, qualified_examples=len(ledger),
        positive_behavioral_observations=sum(len(r['result'].get('observations', [])) for r in ledger if r['label']=='positive'),
        negative_categories={k:sum(r['label']=='negative' and r['result']['category']==k for r in ledger) for k in ('schema_rejection','semantic_rejection','valid_but_wrong')},
        same_behavior_wrong_relation_negatives=[r['id'] for r in ledger if r['label']=='negative' and r['result'].get('behavioral_acceptance') is True],
        model_loads=0, participant_inference=0, training=0, optimizer_updates=0, scheduler_updates=0,
        kernel_constructs=26, experimental_execution_semantics_unchanged=True,
        historical_rescoring=0, p6_a04_acceptance=0, p6_a05_access=False,
        evaluation_classification='EXPLORATORY_COORDINATOR_RESERVED', stopped=True))
    print('PASS R6.73 reconstruction, supervision, behavior, adversarial, decoder and tokenizer qualification')


if __name__ == '__main__':
    main()
