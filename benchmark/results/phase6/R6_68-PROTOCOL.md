# R6.68 — Frozen structured generation and semantic action qualification

Owner authorization: one bounded nonproduction inference-only base/adapter
comparison. No training, dataset expansion for training, installation, execution
semantic changes, historical rescoring, P6-A04 acceptance or P6-A05 access.

## Freeze and diagnostics

Verify R6.67/R6.66/R6.65 publication manifests, inherited R6.52 checkpoint and
tokenizer/executable audit, R6.67 final adapter files and preserved kernel26.
Nine coordinator-authored fresh diagnostics are frozen before inference, three
each for add/le/eq. They cover literal-only, mixed literal/reference, distinct
and repeated references, asymmetric le order, Bool versus integer operands,
irrelevant inputs and chain prefixes. No Unit/shared-diamond evaluation family.
Gold actions and behavioral fixtures pass the unchanged R6.65 scorer and R6.63
assembly. These are exploratory non-independent variations: the coordinator has
read prior findings and construction helpers. No exact training records reused.

## Conditions and budgets

- A: unchanged R6.67 prompt-building and generation procedure applied to fresh
  tasks. Its inherited system prompt already asks for unfenced JSON.
- B: A plus an additional emphatic raw-JSON instruction in the user message.
- C: A prompt plus an experiment-local structural LogitsProcessor. It enforces
  compact ASCII JSON in fixed key order; selected/value envelope, Int64/Bool
  result labels, add/le/eq alternatives, exactly two ref/const operands,
  at most two distinct dependency strings and permitted literal types/range.
  Any reference string is allowed; literals need not be in the task scope.
  Result type need not match the operation. Decoder has no scope or gold access.
  Unicode strings may be escaped. This is a structural serialization subset,
  not a general JSON Schema decoder; partial prefixes may dead-end and budgets
  may truncate. Structural validity is never attributed to model learning.

Use installed Transformers and regex only. Same pinned NF4/BF16 base preparation,
precision/seed651, unmerged final adapter and tokenizer. Greedy single-beam128-token
generation, repetition penalty1.1, cache off and terminal-EOS-only stripping
match R6.67. Conditions run A/B/C on base then A/B/C on adapter, N01–N09 each.
Exactly54 calls maximum, one replication, no retry or model-output repair.
120s per generation,3600s per worker, reserved VRAM8GiB maximum and free1.5GiB
minimum. Identity or runtime protocol failure halts; preserve partial outputs.

## Scoring and measurement

The unchanged R6.65 scorer reports strict serialization, schema validity,
correct operation, ordered operands/literals, result type, exact direct
dependencies, deterministic assembly and behavioral acceptance separately.
All dimensions must pass for semantic acceptance. Downstream false flags after
a parse/schema halt indicate NOT_REACHED, not diagnosed semantic failures.
Preserve untouched text/token IDs and first failure. Report Markdown, invalid
JSON, schema, wrong operation/operand/type/dependency, assembly, functional,
termination and inference errors, including downstream diagnostics when reached.

Measure generation wall time, synchronized model-forward time, separately timed
mask enforcement and setup, other generation bookkeeping, output tokens, per-call
peak allocated/reserved VRAM, scoring and available validation/assembly timings.
Forward hooks add synchronization overhead to all conditions: these measurements
are instrumented times, not uninstrumented deployment latency or a causal estimate
of the mask's effect on model-forward cost. No provider calls or API billing.

Classification: matched-condition adapter accepted-count improvement beyond base
implies R6_68_SEMANTIC_ACTION_LEARNING_OBSERVED (bounded diagnostic observation).
Otherwise B/C structural improvement implies R6_68_STRUCTURED_GENERATION_ONLY;
otherwise R6_68_NO_OBSERVED_ADVANTAGE. Unavailable constrained mechanism gives
R6_68_GENERATION_INTERFACE_GAP; integrity/runtime protocol failure gives
R6_68_PROTOCOL_HALT. No broad or independent generalization inference.

Seal publication and verify it in a fresh process; recheck baseline identities,
additive scope and git diff --check. Stop after publication and await authorization.
