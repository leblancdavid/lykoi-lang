# R6.64 — Incremental Lykoi construction training preflight

**Final classification: `R6_64_RESOURCE_OR_STACK_GAP`. Completed optimizer updates:0.**

The single prospective preflight failed before model loading, inference or training.
The new diagnostic scorer imports `jsonschema` in the exact pinned R6.59 training
interpreter, where that module is unavailable. No trained adapter was produced.
This is an R6.64 scorer/stack integration gap introduced by this experiment's code,
not evidence that QLoRA training or the qualified expert actions are unsupported.

## Baseline and preservation

Initial `git status --short` was clean. The existing R6.63 baseline-check command
passed under the pinned private Python before R6.64 files were created.
[Baseline receipt](r6_64/BASELINE.json) repeats the inherited R6.62/R6.61/R6.60/R6.59
audit, protected-history/environment/checkpoint checks, and rehashes every R6.63
publication payload. It also freshly rehashes the Python executable/DLL, venv
launcher, uv executable and requirements lock against the R6.59 supplement.

[Dataset identities](r6_64/DATASET-IDENTITIES.json) bind all ten episode directories,
including qualified B-RECORD-2, source, before/after states, target, typed scope and
behavioral acceptance evidence. Target text and immutable scopes were checked
against those historical records. Operation counts remain add4/le3/eq3. The
records remain deterministic expert demonstrations, not AI-selected trajectories.
Historical acceptance evidence was preserved, not newly behaviorally rescored.

The inherited audit verifies R6.52 checkpoint/tokenizer, R6.54 scheduler, R6.55
AdamW, R6.56 loss/sampling specification and R6.59 cache-release qualification.
The R6.59 trained adapter remains unchanged, with weight SHA256
`79843df8ce1f3e9bf87c81e0e23073c37a702695df6e52ac384b0a33f77fb7d1`.
The base weights remain SHA256
`c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`;
tokenizer SHA256
`c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`.
Kernel26 is established by preserved accounting/implementation, not a new recount.

## Prospective configuration and incomplete freeze

[Protocol](R6_64-PROTOCOL.md) and
[runner source](../../../experiments/incremental_training_r6_64/run.py) specify
fresh original-base initialization, pinned revision, seed651, NF4 QLoRA rank8 q/v,
2048 sequence length, microbatch1/accumulation4, exact R6.55 AdamW with decay0,
R6.54 20-update/2-warmup schedule and R6.59 controlled cache release.

The explicitly proposed sampling sequence is **D01–D10 repeated eight complete
cycles**,80 presentations/eight per record. The six-record R6.56 sequence is not
inherited for dispatch. First update LR0 advances optimizer moments; subsequent
ticks follow the historical schedule. Completion plus one EOS is the proposed
supervision, mean per record divided by4 with prompt/newline/padding ignored.
Proposed decoding is greedy128 tokens, repetition penalty1.1, cache off and EOS
termination. Limits are8GiB reserved/1.5GiB free/16GiB RSS and1800s process timeout.

Ten exact training targets with full skill/schema and requirement/state contexts
were persisted in [DATASET.json](r6_64/DATASET.json). Three diagnostic-only proposals
in source cover literal-only add, repeated-reference le and literal-first eq of a
prior Bool alias. None uses Unit/shared-diamond material or enters training data.
No diagnostic prompt was dispatched. Expected varied outputs were explicit
prospective literals, not derived from model output.

**The executable configuration, sampling, token masks and diagnostic acceptance
freeze did not complete.** Gold diagnostic validation stops on its first record,
before DIAGNOSTICS.json, TOKENIZATION.json, configuration/sequence/scheduler
manifests, effective-worker freeze or PREFLIGHT.json are written. Source/protocol
intent is not an executable freeze receipt. These missing stages are explicitly
listed in [deliverable status](r6_64/DELIVERABLE-STATUS.json).

## Actual failure and stop

[Preserved failure](r6_64/PREFLIGHT-FAILURE.json) records the exact terminal traceback
and one subsequent read-only scorer inspection. The freeze command exits1 at the
gold-action acceptance assertion. D01's raw scorer result is structurally parsed
JSON, then `No module named 'jsonschema'`. Its remaining false defaults are
unmeasured checks following an exception; they are **not** model failures or
contradictions of R6.63 expert qualification.

The traceback/scorer output was transcribed from terminal tool output; automated
subprocess wall time for this failure was not retained. The diagnosis invokes no
model and does not retry preflight. No dependency installation, scorer replacement,
configuration modification or training retry follows the failure. R6.63 schema
qualification used a separate interpreter; it did not establish availability of
that library in the qualified training environment.

## Measurements and learning assessment

| Requested observation | Actual status |
| --- | --- |
| Training attempts dispatched / optimizer updates / presentations |0 /0 /0|
| Base and trained diagnostic calls |0 /0; NOT_REACHED|
| Loss progression, LR observations, gradient norms |NOT_REACHED|
| Training time, peak VRAM, minimum device-free memory |NOT_MEASURED|
| Adapter save, identity and fresh-process reload |NOT_REACHED; no adapter|
| Strict/schema validity and operation/operand/type/dependency selection |NOT_MEASURED|
| Deterministic assembly and behavior of generated actions |NOT_REACHED|
| CUDA/numerical training failures |No training executed; not qualified by absence|

[Terminal result](r6_64/RESULT.json) records these denominators. Improved likelihood,
training-record reproduction, valid generation and varied semantic selection are
all unassessed. No-observed-learning is not the appropriate classification because
no model comparison occurred. No training mechanics or learning benefit is claimed.

The intended ten-record resubstitution test would measure exposed fitting. Repeated
presentations and same-coordinator capability-aware data cannot distinguish reusable
semantics from memorization. The three proposed structural tasks share authorship,
foundation and context and are non-independent; they cannot establish generalization.
Operation selection alone would not establish complete-program construction ability.

## Smallest recommended next experiment

Separately authorize **CPU-only diagnostic-scorer qualification in the exact pinned
training environment**. Specify a compatible schema-checking path prospectively,
check gold acceptance plus malformed/duplicate-key/wrong-choice rejection controls,
and freeze its identity before any new model/training dispatch. This is an integration
qualification recommendation, not permission to install dependencies, repair this
attempt or start another run. A later fresh B-only attempt requires explicit approval.

## Publication and terminal boundary

[Publication identities](r6_64/PUBLICATION-IDENTITIES.json) bind the report, source,
prospective protocol, partial data/preflight evidence and additive
[research/decision/boundary supplement](../../../docs/research-log-r6.64.md).
[Verification](r6_64/VERIFICATION.json) repeats baseline/executable/data preservation,
scope, JSON/Python/link/whitespace/credential checks and `git diff --check`.
A separate process rechecks the publication seal. Publication integrity PASS does
not mean training/scorer preflight PASS.

The [first publication invocation](r6_64/PUBLICATION-ATTEMPT-1.json) failed before
sealing because the historical baseline's unqualified `run` import resolved the
already-loaded R6.64 module, causing recursion. The publication-only verifier now
executes the unchanged historical baseline check in a fresh process. Attempted
runner/worker/scorer, protocol and data stay unchanged; no preflight or model retry.
The repeated traceback is summarized with its external harness-output location.

Production compiler/lowerer/runtime and experimental execution semantics remain
unchanged; kernel26; new primitives0; dataset expansion0; Python comparison adapter0;
R6.3–R6.63 preserved; P6-A04 acceptance0; P6-A05 access false. Deterministic execution
remains AI-independent. External assets remain temporary historical storage.

**Stopped after failed preflight and terminal publication. Await explicit authorization
before stack qualification, a new training attempt or further research.**
