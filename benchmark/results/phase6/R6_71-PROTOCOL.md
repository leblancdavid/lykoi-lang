# R6.71 — Authorized successor execution protocol

Owner authorization: one bounded nonproduction inference-only execution of the
previously frozen R6.68 A/B/C comparison through R6.70-qualified infrastructure.
This document records that authorization and execution boundary; the pre-dispatch
freeze is [SOURCE-FREEZE.json](r6_71/SOURCE-FREEZE.json), which binds the runner,
effective worker, baseline verification, exact copied inputs and execution manifest.
This prose was published after inference, not represented as a pre-dispatch artifact.

## Immutable inputs and dispatch

- Verify R6.70 publication/readiness, R6.69 verifier, R6.67 adapter files/tensors,
  R6.52 checkpoint/tokenizer, R6.65 scorer and inherited protected identities.
- Preserve R6.68 and R6.69 original protocol halts. Stop on identity mismatch.
- Copy the nine R6.68 diagnostics and A/B/C configuration byte-for-byte into a
  new output directory; never regenerate requirements or expected answers.
- Execute base A/B/C, then adapter A/B/C; N01–N09 in each condition, one call
  per cell, 54 total. No retries or outcome-dependent changes.
- A uses original prompts/decoding; B adds the exact frozen raw-JSON instruction;
  C uses A prompts plus the unchanged qualified model-time structural mask.
- Greedy one-beam generation, 128-token maximum, repetition penalty 1.1,
  cache disabled, inherited seed651 and precision/runtime configuration.
- Inherited limits: 120 seconds per generation, 3600 seconds per worker,
  8GiB peak reserved maximum, 1.5GiB device free minimum at stopping-criteria checks.

## Verification and scoring

Use exact namespace-aware R6.69 fingerprints before scored calls, including
unwrapped base and adapter-wrapped base plus trained adapter identity. Freeze all
parameters and use eval/inference mode. Check unchanged manifests after calls.
The preparation helper's historical name includes training, but no optimizer,
scheduler, backward pass or training step is invoked.

Score raw outputs with unchanged R6.65 scorer and frozen expert completions and
fixtures. Decode all IDs and remove terminal EOS only. Do not strip Markdown,
repair JSON, reorder dependencies, or infer expected results from generated actions.
Report all eight scorer dimensions separately. Only all-dimension acceptance is
semantic success; pre-schema false flags do not establish observed semantic choices.
Persist per-call attempt, raw output, first scorer rejection, tokens, wall time,
mask/setup overhead, scoring and assembly diagnostic time, and VRAM peaks.

## Interpretation and publication

Semantic learning requires correct semantic-construction improvement beyond
structural enforcement, with schema-conditional and matched-schema comparisons.
Structural improvement alone receives `R6_71_STRUCTURED_GENERATION_ONLY`.
Do not claim independent generalization or language superiority from nine
coordinator-designed diagnostic variations and one deterministic generation each.

Publish additive evidence, verify publication hashes, inherited identities and
`git diff --check`, then stop. Production kernel26/compiler/lowerer/runtime,
experimental semantics, weights, dataset and all prior evidence remain preserved.
No training, optimizer/scheduler update, Python comparison adapter, historical
rescoring, P6-A04 acceptance or P6-A05 access. Further work requires authorization.
