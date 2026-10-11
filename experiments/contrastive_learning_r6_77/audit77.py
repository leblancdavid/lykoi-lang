"""Read-only identity and preserved-observation qualification; never calls a model."""
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'experiments/contrastive_learning_r6_76'))
import run76 as old
from durable77 import atomic, digest

OUT = ROOT/'benchmark/results/phase6/r6_77'


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    began = time.perf_counter()
    receipt = old.verify()
    assert receipt == old.x.read(old.OUT/'IDENTITY-PREFLIGHT.json')
    publication = old.x.read(old.OUT/'PUBLICATION-IDENTITIES.json')
    for name, entry in publication['files'].items():
        assert digest(ROOT/name) == entry['sha256'], name
    assert old.x.read(old.OUT/'TERMINAL-RESULT.json')['classification'] == 'R6_76_PROTOCOL_HALT'
    readiness = old.x.read(old.x.OUT/'TRAINING-READINESS.json')
    assert readiness['ready'] and readiness['configuration_identity'] == old.CONFIG_ID
    assert old.x.ARTIFACTS.is_dir() and not list(old.x.ARTIFACTS.iterdir())
    atomic(OUT/'IDENTITY-PREFLIGHT.json', dict(passed=True, receipt=receipt,
           r6_76_publication_sha256=digest(old.OUT/'PUBLICATION-IDENTITIES.json'),
           readiness_sha256=digest(old.x.OUT/'TRAINING-READINESS.json'), seconds=time.perf_counter()-began))
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(old.x.STORE/'checkpoint', local_files_only=True, trust_remote_code=False)
    fixtures = old.x.read(old.x.OUT/'EVALUATION.json')['records']
    records = old.x.read(old.OUT/'BASE-DIAGNOSTIC-PARTIAL.json')['records']
    assert len(records) == 4 and len({r['id'] for r in records}) == 4
    controls = []
    for row, record in zip(fixtures, records):
        started = time.perf_counter()
        assert record['id'] == row['id'] and record['prompt_identity'] == old.x.identity(row['prompt'])
        ids = record['generated_ids']
        assert record['eos'] and ids[-1] == tokenizer.eos_token_id and len(ids) <= 64
        assert tokenizer.decode(ids[:-1], skip_special_tokens=False) == record['raw']
        assert old.x.score(record['raw'], row) == record['scores']
        assert len(record['transitions']) == len(ids)
        language = old.x.CompletionLanguage(row['scope'])
        for index, transition in enumerate(record['transitions']):
            assert transition['ids'] == ids[:index]
            allowed = language.allowed(tokenizer, ids[:index], range(len(tokenizer)))
            assert len(allowed) == transition['allowed_count']
            assert old.x.identity(allowed) == transition['allowed_identity']
            assert ids[index] in allowed
        assert record['raw'] in language.terminals and 0 < record['seconds'] <= 120
        controls.append(dict(id=row['id'], raw_identity=old.x.identity(record),
                             fixture_identity=old.x.identity(row), passed=True,
                             audit_seconds=time.perf_counter()-started))
        atomic(OUT/f'REUSE-{len(controls):02d}.json', controls[-1])
    # The worker records only AFTER model.generate returns and scoring finishes.
    # No pre-generation claim or token journal exists for the next case.
    stderr = (old.OUT/'base-stderr.txt').read_text(encoding='utf-8')
    assert not (old.OUT/'BASE-DIAGNOSTIC.json').exists()
    assert not (old.OUT/'PHASE-base.json').exists()
    atomic(OUT/'RECOVERY-AUDIT.json', dict(committed_observations=4,
           committed_reuse_qualified=True, records=controls,
           next_case=fixtures[4]['id'], next_case_state='AMBIGUOUS_INFLIGHT',
           warning_lines=len(stderr.splitlines()),
           reason='Five generation-warning lines but only four completed records; no fifth raw output, token journal, start/exit receipt or completion commitment.',
           definitely_not_started_after_next=[r['id'] for r in fixtures[5:]],
           safe_continuation=False, duplicate_generation_exclusion=False,
           remaining_completed_observations_needed=26, completed_generation_count=4,
           actual_total_model_calls=None, historical_decoder_overhead_seconds=None,
           scores_reverified_without_generation=True))
    print(json.dumps(dict(identity_passed=True, reuse_qualified=4, safe_continuation=False)))


if __name__ == '__main__':
    main()
