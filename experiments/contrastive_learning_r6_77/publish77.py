"""Publish halted linked evidence; no model load, inference or training."""
import ast
import json
import os
from pathlib import Path
import re
import subprocess
from audit77 import ROOT, OUT, old
from durable77 import atomic, digest, load


def main():
    assert old.verify() == load(OUT/'IDENTITY-PREFLIGHT.json')['receipt']
    historical = load(old.OUT/'PUBLICATION-IDENTITIES.json')
    for name, entry in historical['files'].items():
        assert digest(ROOT/name) == entry['sha256'], name
    assert load(old.OUT/'TERMINAL-RESULT.json')['classification'] == 'R6_76_PROTOCOL_HALT'
    assert digest(old.OUT/'PUBLICATION-IDENTITIES.json') == load(OUT/'IDENTITY-PREFLIGHT.json')['r6_76_publication_sha256']
    recovery = load(OUT/'RECOVERY-AUDIT.json')
    qualification = load(OUT/'LAUNCHER-QUALIFICATION.json')
    assert recovery['committed_reuse_qualified'] and not recovery['safe_continuation']
    assert qualification['passed'] and all(qualification['checks'].values())
    assert len(qualification['checks']) == 14
    assert not list(old.x.ARTIFACTS.iterdir())
    assert not subprocess.check_output(['git','diff','--name-only','HEAD'], cwd=ROOT, text=True).strip()
    records = load(old.OUT/'BASE-DIAGNOSTIC-PARTIAL.json')['records']
    fixtures = old.x.read(old.x.OUT/'EVALUATION.json')['records']
    dimensions = ('strict_decision_validity', 'correct_operation', 'correct_operand_identities',
                  'correct_operand_order', 'correct_dependencies', 'reconstruction_success',
                  'functional_acceptance', 'accepted')
    groups = {}
    for label, partition in [('diagnostic','reserved_diagnostic'), ('calibration','training_calibration')]:
        ids = {row['id'] for row in fixtures if row['partition'] == partition}
        selected = [record for record in records if record['id'] in ids]
        groups[label] = dict(planned=len(ids), completed=len(selected),
            dimensions={key:dict(correct=sum(r['scores'].get(key) is True for r in selected),
                                  incorrect=sum(r['scores'].get(key) is False for r in selected),
                                  not_reached=sum(r['scores'].get(key) not in (True,False) for r in selected))
                        for key in dimensions})
    baseline = dict(complete=False, completed=4, reused_committed_observations=4,
                    newly_generated_observations=0, groups=groups,
                    source='benchmark/results/phase6/r6_76/BASE-DIAGNOSTIC-PARTIAL.json',
                    source_sha256=digest(old.OUT/'BASE-DIAGNOSTIC-PARTIAL.json'),
                    evaluation_sha256=digest(old.x.OUT/'EVALUATION.json'),
                    configuration_identity=old.CONFIG_ID,
                    record_identities=[old.x.identity(record) for record in records],
                    next_case_state='AMBIGUOUS_INFLIGHT',
                    next_case=recovery['next_case'], post_training_comparison='NOT_REACHED')
    atomic(OUT/'BASE-EVALUATION.json', baseline)
    stages = dict(identity='PASS', historical_committed_reuse='PASS',
                  synthetic_durable_launcher='PASS', live_model_launcher='NOT_QUALIFIED',
                  historical_inflight_recovery='HALT', baseline='PARTIAL_4_OF_30',
                  gpu_training_preflight='NOT_REACHED', training='NOT_REACHED',
                  adapter_save_verification='NOT_REACHED', fresh_adapter_reload='NOT_REACHED',
                  post_training_evaluation='NOT_REACHED', semantic_comparison='NOT_ESTABLISHED')
    atomic(OUT/'STAGE-STATUS.json', stages)
    phase_memory = []
    for label in ('complete','interruption'):
        path = OUT/'controls_2'/label/'resources.jsonl'
        samples = [json.loads(line) for line in path.read_text().splitlines()]
        worker_samples = [r for r in samples if r['attribution'] == 'worker']
        assert worker_samples
        phase_memory.append(dict(mode=label, samples=len(samples),
                                 worker_samples=len(worker_samples),
                                 max_sampled_worker_rss_bytes=max(r['resident_bytes'] for r in worker_samples),
                                 guaranteed_peak=False))
    terminal = dict(classification='R6_77_PROTOCOL_HALT', configuration_identity=old.CONFIG_ID,
                    halt='Historical fifth generation is ambiguous; no complete raw/token/commit/exit evidence; duplicate generation exclusion unavailable.',
                    completed_base_diagnostics=4, planned_base_diagnostics=30,
                    reused_committed_observations=4, new_completed_generations=0,
                    new_model_calls=0, historical_completed_model_generations=4,
                    historical_total_model_calls=None, historical_generation_warning_lines=5,
                    historical_generated_tokens=sum(len(r['generated_ids']) for r in records),
                    historical_inference_decoder_seconds=sum(r['seconds'] for r in records),
                    historical_decoder_overhead_seconds=None, new_decoder_overhead_seconds=None,
                    new_inference_wall_seconds=None, optimizer_updates=0, scheduler_updates=0,
                    presentations=0, training_attempts_dispatched=0, training_loss=None,
                    training_wall_seconds=None, gpu_memory=None, adapter_verification='NOT_REACHED',
                    reference_inference_initialization='NOT_REACHED',
                    semantic_comparison='NOT_ESTABLISHED', groups=groups,
                    synthetic_worker_exits=qualification['phases'], synthetic_resources=phase_memory,
                    synthetic_qualification_wall_seconds=qualification['seconds'],
                    synthetic_control_failure_preserved=True, audit_process_pid=None,
                    audit_tool_exit_code=0, qualification_first_tool_exit_code=1,
                    qualification_second_tool_exit_code=0, publication_process_pid=os.getpid(),
                    interruption_controls=1, participant_interruptions_this_round=0,
                    long_duration_tool_survival_qualified=False, automatic_retry=False,
                    kernel_constructs=26, p6_a04_acceptance=0, p6_a05_access=False,
                    stopped=True)
    atomic(OUT/'TERMINAL-RESULT.json', terminal)
    subprocess.run(['git','diff','--check'], cwd=ROOT, check=True)
    files = sorted([p for p in OUT.rglob('*') if p.is_file() and p.name not in
                    ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')] +
                   list((ROOT/'experiments/contrastive_learning_r6_77').glob('*.py')) +
                   [ROOT/'benchmark/results/phase6/R6_77-REPORT.md'] +
                   list((ROOT/'docs').glob('*-r6.77.md')))
    for path in files:
        text = path.read_text(encoding='utf-8')
        assert all(line == line.rstrip() for line in text.splitlines()), path
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----', text), path
        if path.suffix == '.json':
            json.loads(text)  # Duplicate-key/corruption specimens are intentionally preserved.
        if path.suffix == '.jsonl':
            for line in text.splitlines():
                json.loads(line)
        if path.suffix == '.py':
            ast.parse(text)
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                target = (path.parent/link).resolve()
                assert target.exists() or (target.parent == OUT.resolve() and
                       target.name in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')), (path,link)
    manifest = dict(version='r6.77-publication-1', files={p.relative_to(ROOT).as_posix():
                    dict(sha256=digest(p), bytes=p.stat().st_size) for p in files})
    atomic(OUT/'PUBLICATION-IDENTITIES.json', manifest)
    for name, entry in load(OUT/'PUBLICATION-IDENTITIES.json')['files'].items():
        assert digest(ROOT/name) == entry['sha256']
    atomic(OUT/'VERIFICATION.json', dict(passed=True, manifest_sha256=digest(OUT/'PUBLICATION-IDENTITIES.json'),
           publication_files=len(files), historical_publication_reverified=True,
           historical_r6_76_verification_sha256=digest(old.OUT/'VERIFICATION.json'),
           tracked_diff_empty=True, git_diff_check=True,
           syntax_links_whitespace_credential_patterns=True, configuration_identity=old.CONFIG_ID,
           kernel_constructs=26, p6_a04_acceptance=0, p6_a05_access=False, stopped=True))
    print(json.dumps(dict(classification=terminal['classification'], base_completed=4,
                         training_updates=0, publication_files=len(files), integrity_passed=True)))


if __name__ == '__main__':
    main()
