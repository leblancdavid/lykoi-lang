# R6.66 — Final incremental training preflight

**Final classification: `R6_66_INCREMENTAL_TRAINING_READY`.** All13 mandatory
CPU-preflight components are **QUALIFIED** in the exact pinned training interpreter.
The R6.65 successor scorer is integrated. A fresh bounded20-step experiment is
justified subject to separate owner authorization. Model loads, inference,
backward calls, optimizer updates, scheduler updates and fine-tuning are all0.
Readiness establishes a frozen executable specification and CPU checks, not GPU
training success, resource feasibility on these longer records or model learning.

## Baseline verification and preservation

Initial `git status --short` was clean. Before edits, R6.65's publication checker
and the inherited R6.63 baseline checker both passed under pinned Python3.12.11.
[Baseline](r6_66/BASELINE.json) repeats the full inherited history/environment/
checkpoint/adapter audit in a fresh process and binds R6.59/R6.63/R6.64/R6.65
publications, their payloads and receipts. It rehashes Python executable/DLL,
venv launcher, uv and requirements lock against R6.59's executable supplement.
The same full audit passed again at publication.

R6.63's ten immutable demonstrations and R6.59's qualified infrastructure remain
unchanged. R6.52 checkpoint/tokenizer, R6.54 scheduler, R6.55 AdamW, R6.56 loss
normalization and R6.58 controlled release remain bound by inherited identities.
R6.64's original scorer, halt, failed publication attempt and all historical bytes
are preserved; its missing PREFLIGHT.json and absent model-output directory remain
absent. Kernel26 follows preserved accounting/implementation, not a fresh recount.

- Base weights: `c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`.
- Tokenizer: `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`.
- Preserved R6.59 adapter, never used as initialization:
  `79843df8ce1f3e9bf87c81e0e23073c37a702695df6e52ac384b0a33f77fb7d1`.

## Integrated scorer and executable worker

[Runner](../../../experiments/incremental_training_r6_66/run.py) binds `score`
directly to the unchanged R6.65 successor. Historical R6.64 helpers supply record
conversion and asset access; its dormant scorer is never invoked. `jsonschema`
remains unavailable in the pinned environment and is never imported. No dependency
installation or permissive fallback occurs.

[Scorer integration](r6_66/SCORER-INTEGRATION.json) and
[gold evidence](r6_66/SCORER-GOLD.json) retain exact per-dimension outcomes:

| Check | First qualification and fresh-process replay, each |
| --- | ---: |
| Strict serialization/schema |13/13|
| Exact operation/ordered operands/dependencies/result type |13/13|
| Deterministic assembly |13/13|
| Frozen behavior |13/13 cases;54/54 fixtures|
| Frozen R6.65 negative controls rejected |50/50|
| Direct checker host-domain rejection controls |6/6|

The ten training gold actions additionally match frozen R6.63 AFTER and native
VALIDATION artifacts. The50 negatives reproduce R6.65's exact scores, including
valid-but-wrong semantic choices and commutative swaps. The fresh process repeats
these50 scores; direct-checker6 rejection details are qualified in the first pass.
Repeated fixtures are not independent cases.

[Worker builder](../../../experiments/incremental_training_r6_66/worker.py) retains
R6.59 training/reload mechanics and R6.64's13-case diagnostic loop. Prospective
changes are explicit: R6.66 paths/round, manifest-driven fresh LoRA configuration,
and application of the already frozen precision flags. The actual
[effective worker](r6_66/EFFECTIVE-WORKER.py.txt) is compiled, source-bound and frozen;
dispatch executes these frozen bytes. There is no model execution during preflight.

## Frozen training specification

[Canonical configuration](r6_66/TRAINING-CONFIGURATION.json) contains all inherited
settings, pinned checkpoint files and binaries, dataset/scorer/worker identities,
sampling, normalization, decoding, resource/timeout limits, checkpoint paths,
logging/recovery and explicit resolved choices. No training-critical setting remains
unresolved. The CPU replay constructs LoRA and quantization configuration objects
without creating a model or adapter tensors; both accept the frozen settings.

| Setting | Frozen value |
| --- | --- |
| Model/base |Qwen2.5-Coder-1.5B-Instruct; original R6.52 base|
| Revision |`2e1fd397ee46e1388853d2af2c993145b0f1098a`|
| Quantization |NF4, double quantization, BF16 compute, UInt8 quantized storage|
| Adapter |rank8 q_proj/v_proj; alpha16; dropout0.05; bias none; FP32; trainable only|
| Fresh adapter mode |inference_mode=false; seed651; exact R6.52 initial tensor check before first update|
| Sequence/batching |2048; microbatch1; accumulation4; no packing/truncation; workers0|
| Updates/sampling |20 maximum;80 presentations; D01–D10 cyclic eight times; no shuffle|
| Loss |per-record causal masked completion+EOS mean divided by4|
| Optimizer |R6.55 ordinary adapter-only AdamW; LR1e-4; weight_decay0; betas0.9/0.999; eps1e-8; all other kwargs bound|
| Scheduler |R6.54 linear; warmup2; total20; optimizer then scheduler on completed update|
| Gradient safeguards |non-reentrant checkpointing; clip norm1; finite checks; no scaler|
| Precision |BF16 forward, no autocast; TF32 matmul false/cudnn true; highest FP32 precision; deterministic_algorithms false|
| Cache |off; R6.58 backward/delete/synchronize/hash/release/hash-check order|
| Memory |reserved ceiling8GiB; device-free floor1.5GiB; RSS16GiB; poll0.1s|
| Timeouts |training/diagnostic process1800s; generation120s; reload120s|
| Decoding |greedy; one beam;128 tokens; repetition penalty1.1; terminal EOS only; no repair|
| Checkpoints |new external r6-66/step10 and step20; retention2; adapter/tokenizer/state/provenance|
| Recovery |exclusive one-shot claims; raw failure/accounting retained; no automatic resume/retry|

All20 update boundaries (40 used/after LR values and cumulative presentation counts)
are recorded as20 rows in [simulation](r6_66/SCHEDULER-SIMULATION.json); neither
optimizer nor scheduler is instantiated or stepped. First update uses LR0,
update3 uses peak1e-4, and the twentieth post-update LR is0. The frozen worker
retains the historical completed-update accounting and checks.

## Dataset, sampling and exact identities

[Dataset identities](r6_66/DATASET-IDENTITIES.json) bind every episode's immutable
files and converted record identity. Canonical order is ascending immutable
episode ID D01 through D10, established before tokenization and qualification.
The converted records exactly match the ten R6.64 records. No record was generated
or expanded. Operation counts remain add4/le3/eq3.

[Sampling manifest](r6_66/SAMPLING.json) enumerates all80 presentations with episode,
update and microbatch position. Each of20 updates has exactly four presentations;
each record appears eight times. Complete order is D01–D10 repeated eight times.
No six-record R6.56 sequence, reshuffle or data-loader sampling is reused.

| Identity | SHA256 |
| --- | --- |
| Canonical dataset object |`75b78ccf27a6043af05cb197fc4c36d73aebbfd244b6fcbc55087d635746daf9`|
| Dataset file |`3b821da3c59046e814ef6f43439df788dd018843d381584dd453dcfa25f842db`|
| Canonical sampling object |`554dc5e8d15b2371088c10ed0c211fd570a58e1f586c1a58795dfb144015a38f`|
| Sampling file |`88bb950c287972eee5a26f386365aa3be4f860b889e2afc7e829afa7df05f469`|
| Canonical training configuration |`b7f02ba671c78baf243148a4ed49b8e143775538bb5cbd82369ee2294d096ca5`|
| Training configuration file |`fd45a5b4309106ee19290183b45907387d11ad21c41d34ad0c68db6d2e8255a9`|
| Diagnostic manifest file |`69300bc5d11b8972c3fe9c42f0a55f4432d292135a15e1c56403cc355ece018e`|
| Effective worker file |`b648490af821996ddbb80a9362bce1c471ed036fe0cf17e5bf4612c8e3e63a89`|

Canonical identities use the inherited canonical JSON encoding; file identities
hash actual pretty-printed publication bytes. These are deliberately distinguished.

## Tokenization and loss-mask evidence

[Exact tokenization](r6_66/TOKENIZATION.json) retains input IDs, labels, attention
masks, target boundaries, causal-logit positions, prefix hashes and padded control
identities for all13 cases. Pinned tokenizer uses effective prefix
`<|im_start|>assistant\n`. Completion is exact target text plus one im_end EOS;
prompt, post-EOS newline and padding are ignored. No target truncation occurs.

| Episode | Full sequence tokens | Supervised tokens including EOS |
| --- | ---: | ---: |
| D01 |1264|40|
| D02 |1257|36|
| D03 |1250|36|
| D04 |1333|40|
| D05 |1252|34|
| D06 |1245|34|
| D07 |1257|36|
| D08 |1258|38|
| D09 |1253|36|
| D10 |1245|34|

Microbatch1 is unpadded with all-one attention; independent right-padding controls
to2048 use zero padding attention and -100 labels. All13 round trips, boundaries,
causal positions and masks pass and reproduce exactly in a fresh process. Minimum
diagnostic prompt headroom is756 tokens; every gold target+EOS fits within128 tokens.
Five empty/missing/wrong-role/chat-boundary/malformed-target controls reject.

[Mask qualification](r6_66/LOSS-MASK-QUALIFICATION.json) and
[CPU replay](r6_66/CPU-REPLAY.json) test the installed ForCausalLMLoss helper on
synthetic CPU logits, without model inference or backward. All13 masks match manual
causal-shifted cross entropy and seven-token padding invariance. Loss helper file
hash remains `32aed0a8faf1b1b618300a51d1e4fc3564a06a9f4f4ec1130b27f1fa0e4f565b`.
Equal four-record mean0.8274764567613602 differs from pooled-token negative control
0.8275411662302519; the executable worker uses each record's loss/4.

## Frozen diagnostics and readiness gate

[Diagnostic manifest](r6_66/DIAGNOSTICS.json) binds all13 prompts, expected operation,
ordered operands, direct dependencies, result type, exact assembly/native-validation
identities, functional fixtures, decoding protocol and128-token limits. Gold10
are exposed training diagnostics; V01 literal-only add, V02 repeated-reference le
and V03 literal-first eq of an existing Bool alias are unchanged R6.64 prospective
diagnostics. They are structurally varied, coordinator-authored and non-independent.
No expectations come from model output or reserved evaluation-family solutions.

All mandatory components are **QUALIFIED**: baseline, dataset conversion, sampling,
tokenization, loss masks, scheduler simulation, scorer integration, scorer gold,
scorer negatives, diagnostics, complete configuration, output paths and effective
worker. [CPU results](r6_66/CPU-QUALIFICATION.json),
[fresh-process capture](r6_66/CPU-REPLAY-PROCESS.json),
[freeze receipt](r6_66/PREFLIGHT.json) and
[readiness receipt](r6_66/TRAINING-READINESS.json) preserve evidence. No mandatory
component is PARTIAL or BLOCKED; remaining blockers are empty.

Both qualification passes run under
`C:\Users\lblan\AppData\Local\Temp\opencode\lykoi-r6-52\venv\Scripts\python.exe`.
CUDA visibility is disabled; replay confirms CUDA is uninitialized. The intended
output parent passes an exclusive create/read/delete probe; no checkpoint/output
root or dispatch claim is created. Publication-only capture code was added after
the training source freeze; it is independently hash-bound in raw process evidence
and publication and does not change any frozen training payload.

## Publication, recommendation and stop

Publication identities and verification receipts bind report/protocol, integrated
source, frozen configuration/effective worker and all evidence. Fresh-process
publication verification and `git diff --check` pass; JSON/Python/links/whitespace/
credential scans and additive scope checks pass. An additive
[boundary/research/decision supplement](../../../docs/research-log-r6.66.md) records
the current boundary without rewriting pinned history.

Recommend a separately authorized fresh original-base B-only20-update experiment:
base13-case diagnostics, one training attempt, fresh-process adapter reload, then
the paired13-case diagnostics using this exact freeze. Retain failures and actual
LR/loss/gradient/resource/accounting and output measurements. Success would measure
exposed fitting and mechanics; it cannot establish independent generalization,
full-program construction ability or superiority over Python.

Production compiler/lowerer/runtime and experimental semantics unchanged; kernel26;
new primitives0; inference0; optimizer/scheduler updates0; fine-tuning0; dataset
expansion0; Python comparison adapter0; installations0; P6-A04 acceptance0;
P6-A05 access false. AI-independent execution remains preserved. External assets
remain in temporary historical storage; identity checks are not durable archiving.

**Stopped after CPU-only qualification and publication. Await explicit authorization
before model dispatch, the fresh20-step attempt or any further work.**
