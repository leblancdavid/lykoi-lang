"""Pinned CPU tokenizer and isolated construction/validation overhead, no model load."""
import statistics
import time
from transformers import AutoTokenizer
from freeze import OUT, ROOT, c, read, sha, pin, write
from assembly import apply
from qualify import frozen_check


def tree_count(value):
    if type(value) is dict: return 1+sum(tree_count(v) for v in value.values())
    if type(value) is list: return 1+sum(tree_count(v) for v in value)
    return 1


def timed(function):
    samples=[]
    for _ in range(20):
        start=time.perf_counter_ns()
        function()
        samples.append(time.perf_counter_ns()-start)
    return dict(repetitions=20,median_ns=statistics.median(samples),min_ns=min(samples),max_ns=max(samples))


def measure():
    frozen_check()
    from pathlib import Path
    checkpoint=Path(r'C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52\checkpoint')
    tokenizer=AutoTokenizer.from_pretrained(checkpoint,local_files_only=True,trust_remote_code=False)
    assert sha(checkpoint/'tokenizer.json')=='c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539'
    rows=[]
    for folder in sorted((OUT/'episodes').iterdir()):
        a,b=read(folder/'A-RECORD.json'),read(folder/'B-RECORD-2.json')
        complete=c.load(a['target']['text'])
        action=c.load(b['target']['text'])
        before=read(folder/'BEFORE.json')
        after_package=read(folder/'AFTER.json')['package']
        prompt=tokenizer.apply_chat_template(a['context']['messages'],tokenize=False,add_generation_prompt=True)
        assert a['context']['messages']==b['context']['messages']
        ac=len(tokenizer.encode(a['target']['text'],add_special_tokens=False))
        bc=len(tokenizer.encode(b['target']['text'],add_special_tokens=False))
        expanded=c.expand(complete)
        rows.append(dict(episode=folder.name,A_content_tokens=ac,B_content_tokens=bc,saved_content_tokens=ac-bc,
            B_reduction_percent=100*(ac-bc)/ac,prompt_tokens_each=len(tokenizer.encode(prompt,add_special_tokens=False)),
            A_with_one_EOS=ac+1,B_with_one_EOS=bc+1,A_canonical_bytes=len(a['target']['text']),B_canonical_bytes=len(b['target']['text']),
            A_json_tree_nodes=tree_count(complete),B_json_tree_nodes=tree_count(action),
            A_stored_steps=c.validate(complete)['stored_steps'],B_selected_steps=1,expanded_nodes=expanded['nodes'],
            new_semantic_decisions_each=dict(operation=1,ordered_operand_bindings=2,result_type=1,exact_dependency_set=1),
            required_context_each='same requirement + full before-state/literals + mechanical rules; referenced skill/schema supplied separately',
            timings=dict(A_native_validation=timed(lambda:c.validate(complete)),A_validation_and_expansion=timed(lambda:c.expand(complete)),
                B_apply_including_before_validation_after_validation_hashing_expansion=timed(lambda:apply(before,action)),
                after_canonical_identity_hash=timed(lambda:pin(after_package)))))
    # Contract context is measured explicitly, rather than pretending references are free.
    contracts={p:len(tokenizer.encode((OUT/p).read_text(encoding='utf-8'),add_special_tokens=False)) for p in ('SKILL-1.md','step-1.schema.json')}
    write(OUT/'AB-MEASUREMENTS-2.json',dict(entries=rows,tokenizer_sha256=sha(checkpoint/'tokenizer.json'),
        measured_sources={p:sha(ROOT/p) for p in ('experiments/incremental_data_r6_63/assembly.py','experiments/incremental_data_r6_63/measure.py')},
        prior_measurement='AB-MEASUREMENTS.json retained: before explicit experiment-bound checks; hash timing included disk read. Revision 2 measures final assembler and cached package hashing.',
        tokenization='local CPU pinned Qwen tokenizer; canonical ASCII target JSON; content only plus separately noted EOS',
        contract_context_tokens=contracts,
        full_package_schema_context_tokens=len(tokenizer.encode((ROOT/'experiments/typed_composition_r6_18/typed-composition-1.schema.json').read_text(),add_special_tokens=False)),
        A_total_content_tokens=sum(r['A_content_tokens'] for r in rows),B_total_content_tokens=sum(r['B_content_tokens'] for r in rows),
        measurement_limitations=['One host, sequential microtiming, 20 repetitions; no exclusive isolation or learning/efficiency inference.',
            'B timing includes assembler and extra validation/expansion; A may arrive malformed and still needs validation/expansion.',
            'A is sealed and includes cryptographic/mechanical fields. Token savings depend on this explicit assistance convention.',
            'Both objectives need full state context; B transfers copying/identity/scaffold work to the assembler.',
            'No shorter-target learning advantage claimed; no model weights loaded, no training or inference.']))
    print('PASS pinned tokenizer measurements',sum(r['A_content_tokens'] for r in rows),sum(r['B_content_tokens'] for r in rows))


if __name__=='__main__':
    measure()
