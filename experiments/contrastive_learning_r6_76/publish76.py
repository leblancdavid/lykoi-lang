"""Publish the interrupted first attempt without inference or training replay."""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path
from run76 import ROOT, OUT, CONFIG_ID, verify, write, x


def main():
    receipt = verify()
    assert receipt == x.read(OUT/'IDENTITY-PREFLIGHT.json')
    for path, digest in x.read(OUT/'EXECUTION-FREEZE.json')['files'].items():
        assert x.sha(ROOT/path) == digest
    assert not (OUT/'TRAINING-RUN-CLAIM.json').exists()
    assert not (OUT/'BASE-DIAGNOSTIC.json').exists()
    assert x.ARTIFACTS.is_dir() and not list(x.ARTIFACTS.iterdir())
    assert not subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=ROOT,text=True).strip()
    neutral = x.read(OUT/'NEUTRAL-QUALIFICATION.json')
    records = x.read(OUT/'BASE-DIAGNOSTIC-PARTIAL.json')['records']
    fixtures = x.read(x.OUT/'EVALUATION.json')['records']
    by_id = {r['id']:r for r in fixtures}
    dimensions = ('strict_decision_validity','correct_operation','correct_operand_identities',
                  'correct_operand_order','correct_dependencies','reconstruction_success','functional_acceptance','accepted')
    groups = {}
    for label, partition in [('calibration','training_calibration'),('diagnostic','reserved_diagnostic')]:
        selected = [r for r in records if (by_id[r['id']]['partition']=='training_calibration') == (label=='calibration')]
        planned = sum((r['partition']=='training_calibration') == (label=='calibration') for r in fixtures)
        groups[label] = dict(planned=planned, completed=len(selected),
            dimensions={k:dict(correct=sum(r['scores'].get(k) is True for r in selected),
                               incorrect=sum(r['scores'].get(k) is False for r in selected),
                               not_reached=sum(r['scores'].get(k) not in (True,False) for r in selected)) for k in dimensions},
            generated_tokens=sum(len(r['generated_ids']) for r in selected),
            seconds=sum(r['seconds'] for r in selected))
    summary = dict(classification='R6_76_PROTOCOL_HALT', neutral_passed=neutral['passed'],
        base_complete=False, base_records=len(records), groups=groups,
        optimizer_updates=0, scheduler_updates=0, training_presentations=0,
        training_loss=None, training_gpu_resources=None, trained_adapter='NOT_REACHED',
        fresh_reload='NOT_REACHED', post_training='NOT_REACHED', semantic_comparison='NOT_REACHED',
        teacher_forced_likelihood_comparison='NOT_REACHED',
        halt='Outer command harness terminated the dispatch after 600000 ms during base inference; no Python workers remained.',
        timeout_distinction='Harness timeout, not a measured violation of the frozen 1800-second worker ceiling.',
        neutral_generated_tokens=len(neutral['records'][0]['generated_ids']),
        neutral_seconds=neutral['records'][0]['seconds'],
        neutral_decoder_seconds=neutral['records'][0]['decoder_seconds'],
        base_decoder_seconds=None, base_decoder_timing='Frozen diagnostic logs combined time only; enforcement split unavailable.',
        automatic_retry=False, p6_a04_acceptance=0, p6_a05_access=False, kernel_constructs=26)
    write('TERMINAL-RESULT.json',summary)
    write('HARNESS-INTERRUPTION.json',dict(command='& "C:\\Users\\lblan\\AppData\\Local\\Temp\\opencode\\lykoi-r6-52\\venv\\Scripts\\python.exe" "experiments/contrastive_learning_r6_76/run76.py" dispatch',
        timeout_ms=600000, tool_result='shell tool terminated command after exceeding timeout 600000 ms',
        observed_process_check='Get-Process -Name python -ErrorAction SilentlyContinue: no output',
        raw_inflight_result='Unavailable; only closed atomic partial records are counted',
        restart=False, artifact_root_empty=True))
    write('STAGE-STATUS.json',dict(identity_preflight='PASS',neutral='PASS',base='INTERRUPTED_PARTIAL',
        training='NOT_REACHED',save_reload='NOT_REACHED',post_training='NOT_REACHED',
        learning_assessment={k:'NOT_ESTABLISHED' for k in ['A_mechanics','B_likelihood','C_calibration','D_semantic_binding','E_functional_improvement','F_no_advantage_or_regression']}))
    lines = ['|Dimension|Completed diagnostic correct / completed|Calibration|', '|---|---:|---:|']
    for key in dimensions:
        d = groups['diagnostic']; c = groups['calibration']
        lines.append(f"|{key}|{d['dimensions'][key]['correct']}/{d['completed']}|{c['dimensions'][key]['correct']}/{c['completed']} (unexecuted)|")
    report = f'''# R6.76 — Contrastive semantic learning experiment

**Final classification: `R6_76_PROTOCOL_HALT`.** Neutral live compact-decoder
qualification passed. The unchanged-base diagnostic stage was interrupted by the
outer command harness at600 seconds; training, adapter save/reload and post-training
evaluation were **NOT_REACHED**. No learning or paired advantage is established.

## Identity and preflight

Initial git status was clean. [Identity receipt](r6_76/IDENTITY-PREFLIGHT.json)
reverifies R6.75 publication, all qualified freezes, original R6.74 halts and the
inherited R6.73 supervision, R6.52 checkpoint/tokenizer, R6.59/R6.67 infrastructure,
R6.58 cache-release and R6.65 scorer preservation checks. Local checkpoint/tokenizer
file hashes match. Production kernel remains26. Exact configuration identity:

`{CONFIG_ID}`

[Execution receipt](r6_76/EXECUTION-RECEIPT.json) and
[prospective freeze](r6_76/EXECUTION-FREEZE.json) bind the additive orchestration.
The qualified training and diagnostic source definitions were executed unchanged;
only the runtime evidence destination was rebound to r6_76. The frozen external
r6-75 checkpoint destination was retained, claimed after neutral success, and remains
empty. No historical adapter was loaded. No hyperparameter, dataset, expectation,
decoder, scorer or execution meaning was changed.

## Neutral live decoder qualification

[Qualification](r6_76/NEUTRAL-QUALIFICATION.json): one small neutral scope with two
references and no literals, no expected operation/operand/dependency answer. All three
operations and both reference choices remained grammar-available. Actual pinned NF4
model/tokenizer generated **{summary['neutral_generated_tokens']} tokens including EOS**,
in **{summary['neutral_seconds']:.3f}s**, with **{summary['neutral_decoder_seconds']:.3f}s**
instrumented mask/enforcement overhead (including token-evidence writes).

Every selected token belongs to the recorded allowed set; disallowed logits were
negative infinity. Each prefix stays in the frozen language, terminals allow only
EOS, final EOS is observed and compact parsing passes. No dead end occurred on this
control. The64-token live budget was respected. A one-token prefix of this live
output is nonterminal: this is a truncation consistency check, not a separate
short-budget live generation. [Raw token decisions](r6_76/NEUTRAL-TOKENS.json),
full transitions and stdout/stderr are retained. This is a small neutral control,
not exhaustive live qualification of every diagnostic scope or model behavior.
Decoder validity is structural enforcement, not model learning.

## Frozen base-model evaluation: interrupted

The frozen fixture order starts with24 diagnostics, then6 exposed calibrations.
**{len(records)}/30** completed outputs were atomically preserved; all are diagnostic
renderings. No exposed calibration was reached. Remaining and in-flight cases are
unexecuted/unavailable, not failures or zero-score observations.

{chr(10).join(lines)}

Completed diagnostic outputs total **{groups['diagnostic']['generated_tokens']} tokens**
and **{groups['diagnostic']['seconds']:.3f}s** combined inference/decoder time.
The unchanged qualified diagnostic worker does not separately measure decoder time;
that split is unavailable and must not be inferred from neutral timing. Raw text,
generated IDs, allowed-set identities, exact semantic dimensions and reconstruction
errors are in [partial base results](r6_76/BASE-DIAGNOSTIC-PARTIAL.json).
Outputs were neither repaired nor rescored into successes. Structural JSON validity
did not ensure correct operand binding, exact dependency coherence or reconstruction.
Functional acceptance marked NOT_REACHED remains distinct from false.

## Halt and resource accounting

[Harness interruption](r6_76/HARNESS-INTERRUPTION.json): the tool terminated the
dispatch command after600000ms during base inference. A subsequent process check
found no Python worker. This outer budget was too short for the complete four-phase
orchestration; it is an orchestration failure, not a demonstrated frozen CUDA/RSS or
1800s per-worker violation. No restart or second inference attempt was made.
The interrupted base process has no closed PHASE-base receipt; its external samples
were still in launcher memory and are unavailable. Neutral actual-worker RSS samples
are retained in [neutral phase](r6_76/PHASE-neutral.json). Generation-library ignored
flag warnings remain in stderr. No conclusion about the unobserved in-flight output
or absence of errors during termination is justified.

## Training, adapter and paired assessment

**Optimizer updates0; scheduler updates0; presentations0.** No training initialization,
optimizer construction, loss/backward measurement or trained adapter was reached.
Training loss, allocated/reserved VRAM, minimum device-free memory and wall time are
unavailable, not zero-valued measurements. Adapter tensor changes, frozen-base
tensor verification after training, save/reload reference-logit verification,
post-training30-case scoring and base-versus-adapter comparisons are NOT_REACHED.
The configured54-update ceiling was never exercised. Historical adapters remain separate.

Assessment A–F: mechanics, likelihood, calibration improvement, diagnostic binding
improvement, functional improvement, and no-advantage/regression are all **not
established**. Incomplete base-only results cannot demonstrate advantage, no advantage,
memorization or semantic learning. No broad generalization or Python superiority claim.

## Contamination, limitations and recommendation

The coordinator reviewed fixtures and historical qualification findings. The24
diagnostic renderings cover12 underlying synthetic requirements; repeated renderings
are not independent observations. Six calibrations are exposed. Unit values are null,
so some distinctions are structural rather than behaviorally discriminated. These
remain exploratory, not independently qualified generalization evidence.

Recommended next step: separately authorize a new linked attempt with an outer
execution budget that accommodates all frozen per-process ceilings and durable
launcher resource telemetry. Preserve this interrupted first result; do not resume
or infer authorization from the prior readiness receipt. No new training settings
or outcome-informed diagnostic/decoder changes are recommended from this evidence.

## Publication and stop

[Terminal result](r6_76/TERMINAL-RESULT.json), [stage status](r6_76/STAGE-STATUS.json),
[publication identities](r6_76/PUBLICATION-IDENTITIES.json) and
[verification](r6_76/VERIFICATION.json) bind the evidence and additive supplements.
Production compiler/lowerer/runtime, experimental semantics, kernel26 and R6.3–R6.75
history are unchanged; P6-A04 acceptance0, P6-A05 access false. No credentials,
dataset expansion, comparison adapter, new primitive or model merge. Execution remains
AI-independent. **Stopped after terminal publication. Await explicit authorization.**
'''
    report_path = ROOT/'benchmark/results/phase6/R6_76-REPORT.md'
    report_path.write_text(report,encoding='utf-8',newline='\n')
    supplements = {
        'project-overview': '# R6.76 boundary supplement\n\nR6.76: `R6_76_PROTOCOL_HALT`. Exact R6.75 identity verified; neutral live decoder\npasses. Outer600s harness interrupts base diagnostics before training. No learning\nor comparison established. Kernel26 and historical evidence preserved. Stopped.\n\nSee [report](../benchmark/results/phase6/R6_76-REPORT.md).\n',
        'research-log': '# R6.76 observations\n\nNeutral pinned-model token masking/EOS/compact parsing passes on one neutral scope.\nPartial base outputs show valid JSON can retain wrong operand bindings. The outer\n600s command timeout interrupts evaluation; training and paired assessment are\nNOT_REACHED. No replay or retry. See [report](../benchmark/results/phase6/R6_76-REPORT.md).\n',
        'decisions': '# R6.76 decisions\n\nPreserve the first interruption and raw partial outputs. Do not infer a semantic\nlearning result from syntax enforcement or an incomplete baseline. A linked next\nattempt requires separate authorization and an adequate outer execution budget.\nSee [report](../benchmark/results/phase6/R6_76-REPORT.md).\n'}
    for name,text in supplements.items():
        (ROOT/'docs'/f'{name}-r6.76.md').write_text(text,encoding='utf-8',newline='\n')
    subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
    files = sorted([p for p in OUT.rglob('*') if p.is_file() and p.name not in ('PUBLICATION-IDENTITIES.json','VERIFICATION.json')] +
                   list((ROOT/'experiments/contrastive_learning_r6_76').glob('*.py')) + [report_path] +
                   list((ROOT/'docs').glob('*-r6.76.md')))
    for path in files:
        text = path.read_text(encoding='utf-8')
        assert all(line==line.rstrip() for line in text.splitlines()),path
        assert not re.search(r'sk-[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----',text),path
        if path.suffix=='.json':
            json.loads(text)
        if path.suffix=='.py':
            ast.parse(text)
    manifest = dict(version='r6.76-publication-1',files={p.relative_to(ROOT).as_posix():dict(sha256=x.sha(p),bytes=p.stat().st_size) for p in files})
    write('PUBLICATION-IDENTITIES.json',manifest)
    for path in files:
        if path.suffix=='.md':
            for link in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
                assert (path.parent/link).exists() or link.endswith('VERIFICATION.json'),(path,link)
    for path,entry in x.read(OUT/'PUBLICATION-IDENTITIES.json')['files'].items():
        assert x.sha(ROOT/path)==entry['sha256']
    write('VERIFICATION.json',dict(passed=True,manifest_sha256=x.sha(OUT/'PUBLICATION-IDENTITIES.json'),
        publication_files=len(files),historical_identity_reverification=True,tracked_changes=0,
        git_diff_check=True,syntax_links_whitespace_credential_patterns=True,configuration_identity=CONFIG_ID,
        kernel_constructs=26,p6_a04_acceptance=0,p6_a05_access=False,stopped=True))
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    main()
