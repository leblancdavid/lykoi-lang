# Future matched-adapter protocol v1 — not executed

## Decision gate and smallest comparison

Current data do **not** fairly support A/B/C training. Qualified package endpoints8,
incremental records0, semantic decisions0, independently withheld families0. Do not
train three adapters by pretending scripted endpoint traces are observed AI actions.
First authorize a small expert-demonstration/interface/acceptance audit for the
[typed-step skill](SMALLEST-SKILL.md), plus genuinely withheld requirement families.
If only A/B can be qualified, compare A/B with unchanged-base controls; defer C.
If only A is available, a resubstitution smoke can test fitting but cannot answer
supervision superiority. No automatically recommended further A-only training.

## Cohort proposal and pre-registration

For a small learning study propose12 training requirements in at least3 structurally
different development components,4 development-validation requirements in a separate
component and8 evaluation requirements in2 custodian-withheld components. These are
design counts, not available or commissioned records. Increase no counts automatically.
Use deterministic expert targets for **all** objective views initially, making author
provenance matched; genuine AI trajectory training is a separate later factor.
All views must express the identical requirement and yield the same functional
artifact through the same fixed foundation. If the narrow skill cannot support
these distinct structures, reduce claims to learning/reproduction and stop the
generalization study rather than renaming constants as new families.

Partition connected semantic/scaffold ancestry before view generation. Freeze sources,
FRCs, acceptance, qualified representations, exact messages/tool rendering, tokenizer
counts/masks and an external provenance ledger. Evaluation acceptance/solutions are
scorer/custodian-only; model inputs receive the same legitimate requirement/context
facts for all objectives. R6.48/R6.49 exposure cannot be undone by repartitioning.
Independent commissioner/reviewer/custodian must be actually appointed and exclusion
audited. If those controls are unavailable, declare unqualified transfer and no
generalization; do not borrow protected evaluation material for training.

## Model, initialization and budget matching

- Same historical `Qwen/Qwen2.5-Coder-1.5B-Instruct`, revision
  `2e1fd397ee46e1388853d2af2c993145b0f1098a`, weight SHA256
  `c1b9b30e907950516ba3c646bdf570d8084c25a6410a0cdca80cf04b11bc13a8`,
  tokenizer SHA256 `c0382117ea329cdf097041132f6d735924b697924d6f6fc3945713e96ce87539`.
  Base means no-adapter Instruct checkpoint, not the different Ollama coder base.
- Three **fresh, separate** r8/alpha16/dropout0.05 q_proj/v_proj LoRA adapters,
  identical R6.52 initialization/seed651,112 FP32 tensors/1,089,536 parameters.
  Never resume/merge R6.59 step20 into a comparison arm. Preserve it separately.
- Inherit offline local NF4/double-quantization/BF16, pinned stack, SDPA,
  non-reentrant checkpointing, cache-off, adapter-only AdamW with exact R6.55 options
  and linear20-update R6.54 schedule, clipping norm2/max1 and controlled post-backward
  cleanup/cache release. Parameter, optimizer and scheduler update counts match20
  per arm. Same resource limits8GiB reserved/1.5GiB free/16GiB actual worker RSS,
  process1800s; no silent fallback. Future preparation must qualify actual longer
  sequences/accumulation; R6.59 shorter-record success is not blanket fit evidence.
- **Proposed learning budget:**8,000 supervised content+EOS tokens per adapter,
  tolerance±2%,20 optimizer updates; per-update target-token distribution matched
  within±5%. This is a small-budget design, not a claim of adequate exposure.
  Freeze a deterministic family-balanced schedule after exact tokenization. Equal
  per-program weighting within an update: average a program's supervised-unit losses,
  then average programs. Freeze precise accumulation/masking before dispatch.
- Match total actual processed input/target tokens within±5% and report sequence
  lengths and an attention-length-squared forward/backward work proxy separately.
  Equal optimizer updates/trainable tensors give equal optimizer work; they do not
  imply equal total training compute. Target total forward/backward work within±5%
  using a frozen schedule/batching plan and measured GPU operation timing as a
  secondary noisy measure, with no throughput claims from wall time alone.
- Shorter B/C units require more presentations to match supervised tokens. Repeated
  state/tool schemas can exceed A compute. Scheduling may repeat **qualified** rows,
  never invent semantics/traces or mask arbitrary portions of a target. Any masked
  padding to equalize compute must be predeclared and no-update qualified, with
  memory and ignored-label controls; it adds no new supervised information.
  Packing/truncation is not inherited; do not introduce it implicitly.
- The numeric schedule is **not yet executable**: B/C tokenizer lengths and records
  do not exist. If these token and compute tolerances cannot both be met within
  limits, halt three-arm commissioning; choose the smaller supported comparison or
  preregister separate token-matched and compute-matched studies under new authority.
  No outcome-driven budget change or checkpoint selection.

Measure distinct program presentations, unit presentations, repeated family exposure,
content/EOS/prompt/padding tokens, sum and squared lengths, optimizer state steps,
LRs, gradient norms, peaks, training/integrity/save/reload times. Retain failures and
initialization/final adapter/frozen-base hashes. Step20 is the sole comparison
checkpoint; step10 is an artifact, not a selected best-evaluation checkpoint.
One seed/run per arm is an exploratory pilot without variance/robustness claims.

## Inference and equivalent functional evaluation

Base and each adapter use identical objective-specific prompts/interfaces. Score
base-A vs adapter-A, base-B vs adapter-B, base-C vs adapter-C before cross-arm deltas.
Development validation may fix a protocol **before** training; evaluation cannot tune
prompts or select operators. Propose greedy1 beam, repetition_penalty1.0, native EOS,
no gold-prefix prefill, raw strict targets. This is a prospective neutral-decoding
choice, not a change to R6.59 scores. Tool schemas are supplied identically within
C controls, full typed state within B controls. Semantic assembly is identical
mechanical work for base and adapter; no expert-selected missing semantic node.

Freeze common whole-task caps:2,048 generated tokens including repairs,16 model
turns,24 construction/validation actions,3 correction turns,180s generation+tool+
validation wall budget excluding measured load/integrity setup. Each call must fit
context2048; exceeding it halts the task, without discarding required state. Model
calls/tool schemas may impose unequal overhead; report it rather than remove it.
Caps are proposed feasibility limits requiring preflight, not demonstrated fit.
A initial output and B/C final assembled output both face the same frozen acceptance.
For the one-step skill both B/C may finish in one selection; full-program studies
require natural rollout from initial state, never teacher-forced intermediate states.

| Metric | Definition / denominator |
| --- | --- |
| Strict target-format | Exact admitted package/update/call syntax, duplicate-key and extra-field rejection; per first output and per attempt |
| Typed operation selection | Selected operator and result/operand types satisfy the source; all eligible requirements, reached-stage subset separately |
| Dependency correctness | Resolvable prior refs, exact deps, identity/scope/order; required references per output and complete tasks |
| Deterministic assembly | Update/call produces intended validated endpoint without semantic filling; all tasks and reached subset |
| Functional acceptance | All frozen cases pass; per requirement, not mean case pass rate alone |
| Invalid-input handling | Typed-input/resource/lookup/etc failures and unchanged state as applicable; report case counts |
| Error precedence | Simultaneous-failure output/code/site/order against frozen expectations; NOT_APPLICABLE for simple pure step requirements |
| Repair iterations | First candidate, rejected actions, accepted-but-wrong actions, calls until accepted endpoint, exhausted caps |
| Total overhead | Prompt/output tokens, call count, inference, transport, assembly, validation, expansion/execution, wall and load separately |

Report local step/call success separately from complete-program success. Static
schema acceptance is not behavior. Functional stages blocked by syntax/type errors
are NOT_REACHED while whole-task acceptance is failure; preserve both denominators.
Retain raw outputs/feedback, no fence stripping, hash rewriting by model-output scorer
or acceptance-informed repair. Deterministic seal computation is permitted only as
the predeclared mechanical assembler for both controls, explicitly costed.

Primary outcome: first-attempt complete functional acceptance on identical withheld
requirements; secondary bounded-repair endpoint acceptance and all overhead. Report
paired task differences and exact counts, without asserting statistical superiority
from a tiny pilot. Training reproduction and related-development transfer are
separate panels. No Python comparison adapter, universal language advantage or
independent semantic understanding claim is part of this protocol.
