"""Successor CPU qualification; retain failed v1 and its evidence unchanged."""
import json
import importlib.util
from pathlib import Path
from reconstruct import c

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('r673_controls_v1', HERE/'qualify_v1.py')
q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(q)
ROOT, OUT, f = q.ROOT, q.OUT, q.f
RESULTS = OUT/'qualification_2'


def write(name, value):
    path = RESULTS/name
    assert not path.exists(), path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n', encoding='utf-8', newline='\n')


def main():
    q.freeze.check_freeze()
    first = f.read(OUT/'IMPLEMENTATION-FREEZE.json')
    for path, digest in first['files'].items():
        original = ROOT/path
        if original.name in ('reconstruct.py', 'qualify.py'):
            original = original.with_name(original.stem+'_v1.py')
        assert f.sha(original)==digest, original
    q.write = write
    paths = list(HERE.glob('*.py'))+[OUT/'EXPECTATION-AMENDMENT-1.json']
    write('IMPLEMENTATION-FREEZE.json', dict(stage='BEFORE_SUCCESSOR_CPU_CANDIDATE_EXECUTION',
        files={p.relative_to(ROOT).as_posix():f.sha(p) for p in paths},
        reason='Canonical compact wire field order; choices and unchanged renderer preserved.',
        predecessor_freeze_sha256=f.sha(OUT/'IMPLEMENTATION-FREEZE.json')))
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(f.STORE/'checkpoint', local_files_only=True, trust_remote_code=False)
    records = q.rows()
    ledger = q.dataset(records, tokenizer)
    q.adversarial(records)
    q.historical_decoder(tokenizer)
    q.compact_controls(records, tokenizer)
    write('QUALIFICATION.json', dict(classification='R6_73_CONTRASTIVE_SUPERVISION_QUALIFIED',
        positives=18, negatives=36, contrast_categories=9, contrast_pairs=9, qualified_examples=54,
        positive_behavioral_observations=54,
        negative_categories={k:sum(r['label']=='negative' and r['result']['category']==k for r in ledger)
            for k in ('schema_rejection','semantic_rejection','valid_but_wrong')},
        same_behavior_wrong_relation_negatives=[r['id'] for r in ledger if r['label']=='negative' and r['result'].get('behavioral_acceptance') is True],
        predecessor_attempt='CPU controls passed through S11 analysis, then compact grammar target-order assertion failed; preserved.',
        model_loads=0, participant_inference=0, training=0, optimizer_updates=0, scheduler_updates=0,
        kernel_constructs=26, experimental_execution_semantics_unchanged=True,
        historical_rescoring=0, p6_a04_acceptance=0, p6_a05_access=False,
        evaluation_classification='EXPLORATORY_COORDINATOR_RESERVED', stopped=True))
    print('PASS R6.73 successor reconstruction, supervision, behavior, adversarial, decoder and tokenizer qualification')


if __name__=='__main__':
    main()
