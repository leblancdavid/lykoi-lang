"""Read-only participant verification and additive terminal publication."""
import ast
import json
import re
import shutil
import subprocess
import time
from run78 import ROOT, OUT, old, x, binding, Journal, atomic, digest, load


def main():
    began = time.perf_counter()
    # Preserve the first publication, whose diagnostic partition selector was wrong.
    # This correction aggregates existing immutable scores only; no rescoring/inference.
    if (OUT/'PUBLICATION-IDENTITIES.json').exists():
        archive = OUT/'publication-attempt-1'
        archive.mkdir(exist_ok=False)
        paths = [OUT/name for name in ('BASE-EVALUATION.json', 'RESOURCE-TOKEN-LEDGER.json',
            'FIFTH-CASE-REPLACEMENT.json', 'STAGE-STATUS.json', 'TERMINAL-RESULT.json',
            'INTEGRITY.json', 'PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')]
        paths += [OUT.parent/'R6_78-REPORT.md'] + list((ROOT/'docs').glob('*-r6.78.md'))
        archived = {}
        for path in paths:
            destination = archive/(path.name+'.txt')
            shutil.copyfile(path, destination)
            archived[path.relative_to(ROOT).as_posix()] = dict(
                archive=destination.relative_to(ROOT).as_posix(), sha256=digest(destination))
        atomic(OUT/'PUBLICATION-CORRECTION.json', dict(
            reason='Initial aggregation selected nonexistent reserved_diagnostic partition; frozen fixtures use evaluation_exploratory. Initial zero-denominator table invalid.',
            original_publication_preserved=archived, participant_evidence_unchanged=True,
            historical_evidence_unchanged=True, inference_calls=0, score_changes=0))
    assert old.verify() == load(OUT/'IDENTITY-PREFLIGHT.json')['receipt']
    preserved = {}
    for name in ('r6_76', 'r6_77'):
        path = OUT.parent/name
        manifest = load(path/'PUBLICATION-IDENTITIES.json')
        for file, entry in manifest['files'].items():
            assert digest(ROOT/file) == entry['sha256'], file
        preserved[name] = dict(manifest_sha256=digest(path/'PUBLICATION-IDENTITIES.json'),
            files=len(manifest['files']), classification=load(path/'TERMINAL-RESULT.json')['classification'])
    assert not subprocess.check_output(['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, text=True).strip()
    assert not list(x.ARTIFACTS.iterdir())
    freeze = load(OUT/'EXECUTION-FREEZE.json')
    assert freeze['binding'] == binding()
    for path, sha in freeze['files'].items():
        assert digest(ROOT/path) == sha
    historical = load(old.OUT/'BASE-DIAGNOSTIC-PARTIAL.json')['records']
    fixtures = x.read(x.OUT/'EVALUATION.json')['records']
    assert len(historical) == 4
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(x.STORE/'checkpoint', local_files_only=True, trust_remote_code=False)
    completed = []
    resources = []
    case_integrity = []
    for index in range(6):
        destination = OUT/f'worker-{index:03d}'
        exit_record = load(destination/'EXIT.json')
        samples = [json.loads(line) for line in (destination/'resources.jsonl').read_text().splitlines()]
        worker_samples = [s for s in samples if s['attribution'] == 'worker']
        assert worker_samples and exit_record['worker_pid'] == load(destination/'HANDSHAKE.json')['worker_pid']
        assert all(s['measured_pid'] == exit_record['worker_pid'] for s in worker_samples)
        resources.append(dict(index=index, case_id=fixtures[index+4]['id'], exit=exit_record,
            samples=len(samples), worker_samples=len(worker_samples),
            max_sampled_worker_rss_bytes=max(s['resident_bytes'] for s in worker_samples),
            guaranteed_peak=False, cuda_reservation_observation=None,
            minimum_device_free_observation=None,
            cuda_limits_checked_by_unchanged_frozen_mask=True))
        start = OUT/'cases'/f'{index:03d}.start.json'
        claim = load(start)
        assert claim['index'] == index and claim['binding'] == binding()
        assert claim['case_id'] == fixtures[index+4]['id']
        pre = load(destination/'PRE-DISPATCH.json')
        assert pre['fixture_identity'] == x.identity(fixtures[index+4])
        assert pre['prompt_identity'] == x.identity(fixtures[index+4]['prompt'])
        if index == 5:
            assert load(destination/'HALT-worker.json')['error'] == 'GENERATION_TIMEOUT'
            assert exit_record['returncode'] == 1 and exit_record['failure'] is None
            assert not (destination/'POST-DISPATCH.json').exists()
            assert not (destination/'COMPLETION.json').exists()
            continue
        raw = OUT/'cases'/f'{index:03d}.raw.json'
        commit = load(OUT/'cases'/f'{index:03d}.commit.json')
        assert commit['start_sha256'] == digest(start) and commit['raw_sha256'] == digest(raw)
        record = load(raw)
        row = fixtures[index+4]
        ids = record['generated_ids']
        assert record['id'] == row['id'] and record['eos'] and ids[-1] == tokenizer.eos_token_id
        assert len(ids) <= 64 and 0 < record['seconds'] <= 120
        assert tokenizer.decode(ids[:-1], skip_special_tokens=False) == record['raw']
        assert record['prompt_tokens'] == len(tokenizer.apply_chat_template(row['prompt'], tokenize=True, add_generation_prompt=True))
        language = x.CompletionLanguage(row['scope'])
        assert record['raw'] in language.terminals
        assert len(record['transitions']) == len(ids)
        for offset, transition in enumerate(record['transitions']):
            assert transition['ids'] == ids[:offset]
            allowed = language.allowed(tokenizer, ids[:offset], range(len(tokenizer)))
            assert transition['allowed_count'] == len(allowed)
            assert transition['allowed_identity'] == x.identity(allowed)
            assert ids[offset] in allowed
        assert load(destination/'COMPLETION.json')['raw_sha256'] == digest(raw)
        post = load(destination/'POST-DISPATCH.json')
        assert post['raw'] == record['raw'] and post['generated_ids'] == ids
        assert exit_record['returncode'] == 0 and exit_record['failure'] is None
        completed.append(record)
        case_integrity.append(dict(index=index, id=record['id'], passed=True,
            raw_sha256=digest(raw), commit_sha256=digest(OUT/'cases'/f'{index:03d}.commit.json')))
    assert len(completed) == 5
    # Preserve the incomplete claim: ordinary recovery refuses it and therefore any retry.
    try:
        Journal(OUT/'cases', binding()).recover()
    except AssertionError as error:
        assert str(error) == 'AMBIGUOUS_INFLIGHT_NO_RETRY'
    else:
        raise AssertionError('INCOMPLETE_CASE_NOT_REFUSED')
    assert len(list((OUT/'cases').glob('*.start.json'))) == 6
    assert len(list((OUT/'cases').glob('*.commit.json'))) == 5
    assert load(OUT/'LIVE-QUALIFICATION.json')['passed']
    all_records = historical+completed
    dimensions = ('strict_decision_validity', 'correct_operation', 'correct_operand_identities',
        'correct_operand_order', 'correct_dependencies', 'reconstruction_success',
        'functional_acceptance', 'accepted')
    groups = {}
    for label, partition in [('diagnostic', 'evaluation_exploratory'), ('calibration', 'training_calibration')]:
        ids = {r['id'] for r in fixtures if r['partition'] == partition}
        selected = [r for r in all_records if r['id'] in ids]
        groups[label] = dict(planned=len(ids), qualified=len(selected), dimensions={key:dict(
            correct=sum(r['scores'].get(key) is True for r in selected),
            incorrect=sum(r['scores'].get(key) is False for r in selected),
            not_reached=sum(r['scores'].get(key) not in (True, False) for r in selected)) for key in dimensions})
    assert groups['diagnostic']['planned'] == 24 and groups['diagnostic']['qualified'] == 9
    assert groups['calibration']['planned'] == 6 and groups['calibration']['qualified'] == 0
    assert sum(g['qualified'] for g in groups.values()) == len(all_records)
    failed_destination = OUT/'worker-005'
    progress = load(failed_destination/'TOKEN-PROGRESS.json')
    failed_prefix = progress['selected_prefix_ids']
    failed_pre = load(failed_destination/'PRE-DISPATCH.json')
    ledger = dict(historical=dict(reused_observations=4,
        generated_tokens_including_eos=sum(len(r['generated_ids']) for r in historical),
        inference_decoder_seconds=sum(r['seconds'] for r in historical),
        prompt_tokens=None, decoder_enforcement_seconds=None, billing=None,
        unknown_fifth=load(OUT/'HISTORICAL-RECONCILIATION.json')['fifth_historical_generation'],
        historical_total_model_calls=None),
        successor=dict(attempt=binding()['attempt'], dispatches=6, completed_generations=5,
            replacement_attempts=1, completed_replacements=1, timed_out_generations=1,
            generated_tokens_including_eos_completed=sum(len(r['generated_ids']) for r in completed),
            prompt_tokens_completed=sum(r['prompt_tokens'] for r in completed),
            prompt_tokens_dispatched=sum(load(OUT/f'worker-{i:03d}'/'PRE-DISPATCH.json')['prompt_tokens'] for i in range(6)),
            inference_decoder_seconds_completed=sum(r['inference_decoder_seconds'] for r in completed),
            allowed_set_and_progress_persistence_seconds_completed=sum(r['allowed_set_and_progress_persistence_seconds'] for r in completed),
            full_mask_enforcement_seconds=None, billing=None, resources=resources,
            timeout=dict(index=5, case_id=fixtures[9]['id'], prompt_tokens=failed_pre['prompt_tokens'],
                generated_tokens_exact=None, observed_prefix_token_count=len(failed_prefix),
                observed_prefix_is_lower_bound=True, terminal_eos=False,
                inference_decoder_seconds=None, decoder_enforcement_seconds=None,
                worker_wall_seconds=resources[-1]['exit']['seconds'],
                raw_complete_output=None, score='NOT_REACHED', completion_receipt=False),
            per_case=[dict(id=r['id'], attempt_identity=r['attempt_identity'],
                replacement=r['replacement_attempt'], prompt_tokens=r['prompt_tokens'],
                generated_tokens_including_eos=len(r['generated_ids']),
                inference_decoder_seconds=r['inference_decoder_seconds'],
                allowed_set_and_progress_persistence_seconds=r['allowed_set_and_progress_persistence_seconds'],
                full_mask_enforcement_seconds=None, billing=None) for r in completed]),
        synthetic_qualification=load(OUT/'LAUNCHER-QUALIFICATION.json'),
        optimizer_updates=0, scheduler_updates=0, training_attempts=0,
        missing_measurements_are_null=True, costs_separated=True)
    atomic(OUT/'RESOURCE-TOKEN-LEDGER.json', ledger)
    atomic(OUT/'BASE-EVALUATION.json', dict(complete=False, qualified=9, planned=30,
        reused=4, new_completed=5, replacement_identity=completed[0]['attempt_identity'],
        records=all_records, groups=groups, unqualified_timeout_case=fixtures[9]['id'],
        later_not_reached=[r['id'] for r in fixtures[10:]],
        unchanged_scorer=True, historical_score_changes=0))
    atomic(OUT/'FIFTH-CASE-REPLACEMENT.json', dict(attempt=completed[0]['attempt_identity'],
        historical_case_id=fixtures[4]['id'], replacement_not_recovery=True,
        qualified=True, historical_record_still_unknown=True, record=completed[0],
        completion_sha256=digest(OUT/'worker-000/COMPLETION.json')))
    atomic(OUT/'STAGE-STATUS.json', dict(identity='PASS', historical_reconciliation='PASS',
        historical_reuse='PASS', synthetic_launcher='PASS', live_launcher='PASS_BOUNDED_SCOPE',
        replacement='QUALIFIED', base_evaluation='PARTIAL_9_OF_30',
        generation='HALT_GENERATION_TIMEOUT', training='NOT_AUTHORIZED_NOT_REACHED',
        post_training='NOT_AUTHORIZED_NOT_REACHED'))
    terminal = dict(classification='R6_78_PROTOCOL_HALT', halt='GENERATION_TIMEOUT',
        halt_case=fixtures[9]['id'], qualified_base_observations=9, planned=30,
        historical_qualified_reused=4, historical_fifth_completion='unknown',
        historical_fifth_invocation='potentially started', new_dispatches=6,
        new_completed_generations=5, replacement_attempts=1, replacement_qualified=True,
        live_qualification_passed=True, groups=groups, optimizer_updates=0,
        scheduler_updates=0, training_attempts=0, training_justified=False,
        automatic_retry=False, kernel_constructs=26, p6_a04_acceptance=0,
        p6_a05_access=False, stopped=True)
    atomic(OUT/'TERMINAL-RESULT.json', terminal)
    integrity = dict(passed=True, publications=preserved, configuration_identity=old.CONFIG_ID,
        case_integrity=case_integrity, original_halts_preserved=True,
        original_unknown_not_overwritten=True, incomplete_claim_blocks_retry=True,
        frozen_model_tokenizer_reverified=True, frozen_fixture_decoder_scorer_reverified=True,
        tracked_changes_empty=True, kernel_constructs=26, adapter_destination_empty=True,
        verification_seconds=time.perf_counter()-began)
    atomic(OUT/'INTEGRITY.json', integrity)
    d = groups['diagnostic']['dimensions']
    table = '\n'.join(f"| {key} | {value['correct']} | {value['incorrect']} | {value['not_reached']} |" for key, value in d.items())
    report = f'''# R6.78 — Generation accounting reconciliation and bounded base evaluation

**Final classification: `R6_78_PROTOCOL_HALT`.** Accounting reconciliation and
bounded live launcher qualification pass. The fifth-case replacement qualifies.
Base evaluation stops at `GENERATION_TIMEOUT` on `{fixtures[9]['id']}`.
**9/30 qualified observations**: four reused historical outputs plus five new
outputs, including the explicitly identified replacement. No retry was made.

## Historical preservation and accounting

[Integrity](r6_78/INTEGRITY.json) verifies R6.76/R6.77 publication identities and
original protocol-halt classifications, R6.75 configuration
`{old.CONFIG_ID}`, frozen diagnostic definitions, decoder/scorer and pinned local
Qwen2.5-Coder-1.5B-Instruct checkpoint/tokenizer. The four historical observations
pass raw-token/EOS/prefix/scoring reverification. Production kernel remains26
through preserved accounting/implementation identities, not a new recount.

[Reconciliation](r6_78/HISTORICAL-RECONCILIATION.json): historical fifth invocation
**potentially started**, completion **unknown**. Raw output, token usage, wall time
and billing are unavailable/null. Five warning lines do not prove five completed
generations. Historical counts, missing evidence and original halts are unchanged.
No historical score repair or new historical generation is claimed.

## Replacement and durable qualification

[Replacement](r6_78/FIFTH-CASE-REPLACEMENT.json):
`{completed[0]['attempt_identity']}`, case `{completed[0]['id']}`.
Same frozen prompt, model, decoder, scorer and limits. Completion qualifies with
{len(completed[0]['generated_ids'])} generated tokens including EOS and
{completed[0]['inference_decoder_seconds']:.3f}s inference/decoder time;
semantic full acceptance is false. It is a new replacement, not recovery.

[Live qualification](r6_78/LIVE-QUALIFICATION.json) verifies actual worker identity,
exclusive pre-dispatch claim, hash-bound raw output and completion receipt, then
duplicate-dispatch refusal and corruption rejection using its committed evidence.
Fourteen [synthetic controls](r6_78/LAUNCHER-QUALIFICATION.json) pass, including real
pinned-worker timeout/termination and durable interruption evidence. Deliberate
interruption/timeout qualification is synthetic; the replacement is the bounded
live completion control. The later live generation timeout is also retained.
No long-duration outer-harness survival or externally forced live-model
interruption is claimed. Workers are foreground tracked via unchanged R6.77 launcher.

## Bounded frozen base results

[Base results](r6_78/BASE-EVALUATION.json): each new worker contains one case, well
within1800s worker ceiling; fixture order and at-most-once dispatch preserved.
There are six new dispatch commitments, five complete generations, one runtime
timeout and20 later cases NOT_REACHED. All nine qualified outputs are diagnostic
renderings;0/6 exposed calibrations reached. Semantic failures are scored without
repair, as the frozen loop specifies; the runtime failure stops continuation.

| Dimension | Correct | Incorrect | NOT_REACHED |
|---|---:|---:|---:|
{table}

Operand-binding accuracy is {d['correct_operand_identities']['correct']}/9;
strict serialization is {d['strict_decision_validity']['correct']}/9. These are
exploratory repeated renderings of synthetic requirements, not independent
generalization evidence. Structural enforcement does not establish semantic learning.

## Timeout and resource ledger

[Resource/token ledger](r6_78/RESOURCE-TOKEN-LEDGER.json) separates history from
successor costs. Historical four:168 output tokens and352.462s combined time;
historical fifth costs remain unknown. Successor five complete outputs:
{ledger['successor']['generated_tokens_including_eos_completed']} output tokens,
{ledger['successor']['prompt_tokens_completed']} input tokens and
{ledger['successor']['inference_decoder_seconds_completed']:.3f}s combined time.
Measured allowed-set computation/hash/progress persistence subset:
{ledger['successor']['allowed_set_and_progress_persistence_seconds_completed']:.3f}s;
full mask enforcement split is unavailable. Instrumentation overhead is included.
Billing is unavailable for every case.

Failed worker wall time is {resources[-1]['exit']['seconds']:.3f}s, including model
load and startup; frozen per-generation120s guard raises `GENERATION_TIMEOUT`.
Its journal start, pre-dispatch record, partial token prefix, stdout/stderr,
traceback and RSS samples persist. Observed prefix length{len(failed_prefix)} is a
lower bound, not an exact final generated-token count. No complete raw output,
EOS, completion receipt or score is inferred. Failed inference/decoder totals
remain unavailable. RSS samples are actual-worker observations, not guaranteed
peaks. CUDA limits are enforced by frozen mask checks; numerical extrema were
not separately measured. The incomplete journal refuses recovery and retry.

## Boundaries, recommendation and stop

Optimizer/scheduler updates0; training attempts0. No training/fine-tuning, adapter
modification, dataset expansion, Python comparison adapter or post-training
comparison. Production/compiler/lowerer/runtime, experimental semantics and
R6.3–R6.77 remain preserved; P6-A04 acceptance0, P6-A05 access false.
AI-independent execution semantics unchanged. No credentials published.

Training is **not justified by this incomplete evaluation**. Recommended next step:
separately authorize neutral diagnosis of compact-decoder enforcement cost and
generation-timeout behavior, preserving this failed attempt. Any successor retry
or changed orchestration/instrumentation requires explicit authorization and fresh
identity; do not extend limits or repair from outcomes in this round.

[Publication manifest](r6_78/PUBLICATION-IDENTITIES.json) and
[verification](r6_78/VERIFICATION.json) bind terminal evidence and additive files.
The initial publication aggregation used a nonexistent partition label and showed
zero diagnostic denominators. Its files are retained under `publication-attempt-1`;
[correction](r6_78/PUBLICATION-CORRECTION.json) binds that first publication.
This corrected table aggregates the original scores without rescoring or inference.
**Stopped after publication. Await explicit authorization.**
'''
    path = OUT.parent/'R6_78-REPORT.md'
    assert (OUT/'PUBLICATION-CORRECTION.json').exists()
    path.write_text(report, encoding='utf-8', newline='\n')
    for kind, title in [('project-overview', 'Current boundary'), ('research-log', 'Observations'), ('decisions', 'Decision')]:
        path = ROOT/'docs'/f'{kind}-r6.78.md'
        assert (OUT/'PUBLICATION-CORRECTION.json').exists()
        path.write_text(f'# Lykoi R6.78 — {title}\n\n'
            '`R6_78_PROTOCOL_HALT`: historical fifth generation remains unknown; labeled\n'
            'replacement qualifies and live single-case orchestration passes bounded gates.\n'
            'Nine of30 base observations qualify; sixth successor dispatch hits frozen120s\n'
            'generation timeout. Failure retained, no retry/training. Kernel26 preserved.\n'
            'Full resource/token accounting and limitations are in the\n'
            '[round report](../benchmark/results/phase6/R6_78-REPORT.md).\n\n'
            'Use additive supplements to preserve hash-pinned historical guidance.\n'
            'Recommend separately authorized neutral decoder-cost/timeout diagnosis;\n'
            'incomplete evaluation does not justify training. Stop pending authorization.\n',
            encoding='utf-8', newline='\n')
    subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
    files = sorted([p for p in OUT.rglob('*') if p.is_file()] +
        list((ROOT/'experiments/base_evaluation_r6_78').glob('*.py')) +
        [OUT.parent/'R6_78-REPORT.md'] + list((ROOT/'docs').glob('*-r6.78.md')))
    for path in files:
        text = path.read_text(encoding='utf-8')
        assert all(line == line.rstrip() for line in text.splitlines()), path
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----', text), path
        if path.suffix == '.py':
            ast.parse(text)
        if path.suffix == '.json':
            json.loads(text)  # Deliberate duplicate-key synthetic specimen preserved.
        if path.suffix == '.jsonl':
            for line in text.splitlines():
                json.loads(line)
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                target = (path.parent/link).resolve()
                assert target.exists() or (target.parent == OUT.resolve() and target.name in
                    ('PUBLICATION-IDENTITIES.json', 'VERIFICATION.json')), (path, link)
    files = [p for p in files if p not in (OUT/'PUBLICATION-IDENTITIES.json', OUT/'VERIFICATION.json')]
    atomic(OUT/'PUBLICATION-IDENTITIES.json', dict(version='r6.78-publication-2', files={
        p.relative_to(ROOT).as_posix():dict(sha256=digest(p), bytes=p.stat().st_size) for p in files}))
    for name, entry in load(OUT/'PUBLICATION-IDENTITIES.json')['files'].items():
        assert digest(ROOT/name) == entry['sha256']
    atomic(OUT/'VERIFICATION.json', dict(passed=True,
        manifest_sha256=digest(OUT/'PUBLICATION-IDENTITIES.json'), publication_files=len(files),
        git_diff_check=True, tracked_diff_empty=True, preserved_publications=preserved,
        syntax_links_whitespace_credential_patterns=True, kernel_constructs=26,
        p6_a04_acceptance=0, p6_a05_access=False, stopped=True))
    print(json.dumps(dict(classification=terminal['classification'], qualified=9,
        groups=groups, ledger=ledger['successor']['per_case'], integrity_passed=True)))


if __name__ == '__main__':
    main()
