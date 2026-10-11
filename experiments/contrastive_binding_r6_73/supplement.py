"""CPU completion witnesses and safely labeled contrastive SFT record conversion."""
import json
from pathlib import Path
from reconstruct import serialize, c
from compact_decoder import CompletionLanguage
import importlib.util
spec = importlib.util.spec_from_file_location('r673_successor', Path(__file__).resolve().parent/'qualify.py')
qualify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qualify)

OUT, f, write = qualify.OUT, qualify.f, qualify.write


def main():
    source = Path(__file__).resolve()
    write('SUPPLEMENT-SOURCE-FREEZE.json', dict(stage='BEFORE_SUPPLEMENT_CONTROLS', source_sha256=f.sha(source)))
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(f.STORE/'checkpoint', local_files_only=True, trust_remote_code=False)
    positives = f.read(qualify.RESULTS/'SFT-POSITIVES.json')['records']
    records = f.read(qualify.RESULTS/'TRAINING-RECORDS.json')['records']
    by_requirement = {row['record_identity']:row for row in positives}
    direct = {(record['requirement_identity'],record['typed_scope_identity']): by_requirement[qualify.q.pin(record)]
              for record in records if record['label']=='positive'}
    corrective, measurements = [], []
    for negative in (r for r in records if r['label']=='negative'):
        correct = direct[(negative['requirement_identity'],negative['typed_scope_identity'])]
        prompt = list(correct['prompt']) + [dict(role='user', content=serialize(dict(
            candidate_decision=negative['compact_target_decision'],
            instruction='This candidate does not satisfy the requirement. Return the correct compact decision using the same scope.')))]
        target = serialize(negative['correct_compact_decision'])
        record = dict(episode_id=negative['id']+'-corrective', prompt=prompt,
            completion=[dict(role='assistant', content=target)],
            label='positive_corrective_target', input_candidate_label='negative',
            requirement_identity=negative['requirement_identity'], typed_scope_identity=negative['typed_scope_identity'],
            reconstructed_action_identity=correct['record_identity'],
            correct_action_identity=next(r['reconstructed_action_identity'] for r in records
                if r['label']=='positive' and r['requirement_identity']==negative['requirement_identity']
                    and r['typed_scope_identity']==negative['typed_scope_identity']),
            contrast_family_identity=negative['contrast_family_identity'], partition='training',
            provenance_classification=negative['provenance_classification'],
            negative_ledger_identity=qualify.q.pin(negative), acceptance_evidence_reference=correct['record_identity'],
            reason_in_model_prompt=False, fabricated_reasoning_trace=False)
        # Reconstructed action identity is the authoritative action hash, not the parent record hash.
        record['reconstructed_action_identity'] = record.pop('correct_action_identity')
        ids, labels, measurement = f.q52.encoded(record, tokenizer)
        assert not measurement['exceeds_2048'] and not measurement['truncated']
        assert target == correct['completion'][0]['content']
        assert tokenizer.decode(ids[len(tokenizer.apply_chat_template(prompt, tokenize=True, add_generation_prompt=True)):
            len(ids)-2], skip_special_tokens=False)==target
        corrective.append(record)
        measurements.append(measurement)
    write('CONTRASTIVE-SFT-POSITIVES.json', dict(version='r6.73-corrective-sft-1', records=corrective,
        count=len(corrective), input_negatives_only=True, assistant_targets_all_correct=True,
        policy='Use with 18 direct SFT positives. Bad decisions occur only in explicitly labeled user input; reasons remain metadata.'))
    write('CORRECTIVE-TOKENIZATION.json', dict(records=measurements,
        target_range=[min(r['target_content_tokens'] for r in measurements),max(r['target_content_tokens'] for r in measurements)],
        sequence_range=[min(r['sequence_tokens'] for r in measurements),max(r['sequence_tokens'] for r in measurements)],
        truncated=0, assistant_targets_positive_only=True))
    # Every character prefix has a one-token extension witness on the pinned tokenizer.
    char_ids = {}
    for token_id in range(len(tokenizer)):
        if token_id not in tokenizer.all_special_ids:
            text = tokenizer.decode([token_id], skip_special_tokens=False)
            if len(text)==1 and text.isascii():
                char_ids.setdefault(text, token_id)
    controls, seen = [], set()
    for row in qualify.q.rows():
        grammar = CompletionLanguage(row['scope'])
        identity = qualify.q.pin(grammar.texts)
        if identity in seen:
            continue
        seen.add(identity)
        witness = {}
        for text in grammar.texts:
            for i in range(len(text)):
                witness.setdefault(text[:i], text[i])
        assert set(witness)==grammar.prefixes-grammar.terminals
        for prefix, next_char in witness.items():
            ids = tokenizer.encode(prefix, add_special_tokens=False)
            assert tokenizer.decode(ids, skip_special_tokens=False)==prefix
            token_id = char_ids[next_char]
            following = tokenizer.decode(ids+[token_id], skip_special_tokens=False)
            assert following==prefix+next_char and grammar.accepts(following)[0]
        controls.append(dict(language_identity=identity, unique_nonterminal_prefixes=len(witness),
            every_prefix_has_token_extension=True, full_decode_boundary_checks=True))
    write('PREFIX-EXTENSION-CONTROLS.json', dict(passed=True, controls=controls,
        unique_prefix_observations=sum(r['unique_nonterminal_prefixes'] for r in controls),
        inference=0, note='Distinct prefixes of five bounded languages; not independent task examples.'))
    print('PASS 36 corrective SFT records with correct assistant targets and every compact prefix token-extension witness')


if __name__=='__main__':
    main()
