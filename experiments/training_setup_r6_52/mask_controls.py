"""Independent CPU loss/shift/padding/overflow controls on all ten sealed rows."""
import hashlib
import json
import torch
from transformers import AutoTokenizer
from qualify import encoded, MODEL, SEED
from setup import ROOT, write


def checked_record(record, tokenizer, limit):
    ids, labels, measurement = encoded(record, tokenizer)
    if len(ids) > limit:
        raise ValueError('REQUIRED_OUTPUT_WOULD_BE_TRUNCATED')
    return ids, labels, measurement


def main():
    torch.manual_seed(SEED)
    tokenizer = AutoTokenizer.from_pretrained(MODEL, local_files_only=True)
    records = [json.loads(line) for line in (ROOT / 'benchmark/results/phase6/r6_51/DIRECT.jsonl').read_text().splitlines()]
    evidence = []
    for row in records:
        ids, labels, measurement = checked_record(row, tokenizer, 2048)
        try:
            checked_record(row, tokenizer, len(ids) - 1)
        except ValueError as exc:
            assert str(exc) == 'REQUIRED_OUTPUT_WOULD_BE_TRUNCATED'
        else:
            raise AssertionError('overflow not rejected')
        # Map real token labels to a tiny vocabulary for an independent loss calculus.
        # The positions/masks are exact; these logits are synthetic, not model scores.
        mapped = [v % 4 if v != -100 else -100 for v in labels] + [-100] * 7
        shifted = torch.tensor(mapped[1:])
        logits = torch.randn(len(mapped) - 1, 4, requires_grad=True)
        loss = torch.nn.functional.cross_entropy(logits, shifted, ignore_index=-100)
        selected = shifted != -100
        manual = -torch.log_softmax(logits[selected], dim=-1).gather(1, shifted[selected, None]).mean()
        assert torch.allclose(loss, manual, atol=1e-7, rtol=1e-6)
        loss.backward()
        assert torch.count_nonzero(logits.grad[~selected]).item() == 0
        assert (logits.grad[selected].abs().sum(dim=1) > 0).all().item()
        assert int(selected.sum()) == measurement['supervised_tokens_including_eos']
        evidence.append({'episode_id': row['episode_id'], 'tokens_sha256': hashlib.sha256(json.dumps(ids).encode()).hexdigest(),
                         'labels_sha256': hashlib.sha256(json.dumps(labels).encode()).hexdigest(),
                         'overflow_rejected': True, 'padding_masked': True, 'causal_shift_verified': True,
                         'masked_loss_matches_selected_token_loss': True, 'ignored_logit_gradients_zero': True,
                         'all_supervised_positions_have_logit_gradients': True,
                         'supervised_token_count': int(selected.sum())})
    write('LOSS-MASK.json', {'status': 'PASS', 'seed': SEED, 'record_controls': evidence,
          'scope': 'exact real token positions; independent synthetic four-class logits on CPU',
          'causal_shift_note': 'last prompt logit predicts first target; prompt labels themselves are excluded',
          'optimizer_steps': 0, 'dataset_modified': False})


if __name__ == '__main__':
    main()
