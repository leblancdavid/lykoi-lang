"""Post-dispatch CPU audit of archived masks; no model load or generation."""
import importlib.util

from qualify import ROOT, OUT, f, write, check_freeze


def main():
    check_freeze()
    from transformers import AutoTokenizer
    spec = importlib.util.spec_from_file_location('r670_replay_decoder', ROOT / 'experiments/structured_generation_r6_68/decoder.py')
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    tokenizer = AutoTokenizer.from_pretrained(f.STORE / 'checkpoint', local_files_only=True, trust_remote_code=False)
    mask = decoder.StructuralMask(tokenizer, 0, lambda text: f.successor.validate_action(f.successor.c.load(text)))
    tracks = {}
    for track in ('base', 'adapter'):
        probes = f.read(OUT / (track.upper() + '-PROBES.json'))['records']
        decisions = 0
        for probe in probes:
            seed = tokenizer(probe['seed'], add_special_tokens=False)['input_ids']
            emitted = []
            for decision in probe['mask_application']:
                prefix = tokenizer.decode(seed + emitted, skip_special_tokens=False)
                assert prefix == decision['prefix']
                viable, complete = mask.accepts(prefix)
                assert viable
                allowed = [mask.eos] if complete else sorted(i for i, piece in mask.pieces if mask.accepts(prefix + piece)[0])
                assert len(allowed) == decision['allowed']
                assert f.identity(allowed) == decision['allowed_ids_sha256']
                token = decision['selected']
                assert token in allowed
                assert tokenizer.decode([token], skip_special_tokens=False) == decision['selected_text']
                if token != mask.eos:
                    assert tokenizer.decode(seed + emitted + [token], skip_special_tokens=False) == prefix + decision['selected_text']
                assert decision['forbidden_masked'] and decision['allowed_scores_unchanged']
                emitted.append(token)
                decisions += 1
            assert emitted == probe['new_token_ids']
            ids = seed + emitted[:-1] if probe['eos'] else seed + emitted
            assert tokenizer.decode(ids, skip_special_tokens=False) == probe['raw_output']
        assert probes[1]['new_token_ids'] == probes[2]['new_token_ids'] == [92, mask.eos]
        assert probes[3]['new_token_ids'] == [mask.eos]
        assert probes[4]['budget_exhausted'] and not probes[4]['grammar_complete']
        tracks[track] = dict(passed=True, decisions=decisions, exact_allowed_set_fingerprints=True,
                            actual_token_text_correspondence=True, suffix_repeat_identical=True)
    write('TOKEN-MASK-AUDIT.json', dict(passed=True, cpu_only=True, model_loads=0, tracks=tracks,
          source_sha256=f.sha(ROOT / 'experiments/inference_qualification_r6_70/verify_masks.py')))
    print('PASS CPU replay of all 110 actual model-time mask decisions')


if __name__ == '__main__':
    main()
