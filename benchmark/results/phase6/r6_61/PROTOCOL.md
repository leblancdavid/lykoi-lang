# R6.61 — Frozen inference-only decoding diagnosis

Owner authorization: first-token distributions and one separately labeled
prefix-continuation diagnostic using unchanged Qwen2.5-Coder-1.5B-Instruct and
R6.59 step20 adapter. Exposed E01–E06 only; no training, dataset or semantics change.

## Pre-execution specification

Verify R6.60 publication and its R6.59/R6.52 preservation chain before dispatch.
Use exact R6.56 diagnostic messages/native template/assistant generation prefix,
pinned tokenizer, NF4/double quantization/BF16, inherited k-bit preparation, SDPA
and cache off. Eval mode, all parameters nontrainable, inference_mode, no optimizer
or scheduler construction. Verify base/buffer/quantization and adapter tensor
identities before/after each model's single fresh process.

First-position: one unprefilled forward per prompt/model. Retain complete FP32
raw logits; apply installed Transformers RepetitionPenaltyLogitsProcessor to
the exact full prompt IDs at penalties1.0 and1.1. Greedy, one beam. Probability
is FP32 softmax over the complete vocabulary after each transformation; rank is
1 + count of strictly greater logits (ties reported). Margin sign is raw-opening
minus fence, for both logits and probabilities. Verify IDs4913 and73594 using
the pinned tokenizer; neither is assumed a complete delimiter. No temperature,
top-p or top-k transformation applies under greedy decoding.

Supplied prefix: exactly UTF-8 bytes7b22 (`{"`), no whitespace/newline, one token
4913, appended after the unchanged assistant-generation prefix. This is a valid
*partial JSON lexical prefix* (object and key-string opening), not a complete
JSON document. Verify it can extend syntactically to a JSON object; no key,
value, operation, dependency graph, identity or task-specific solution is supplied.
Tokenize the full rendered prompt plus prefix and require its IDs equal the
original prompt IDs followed by4913. Freeze per-record IDs/text/hashes before
any model load. Prefix is the first two bytes of every frozen target.

One continuation per model/record/penalty,24 total, no retries. Penalties1.0/1.1
are predefined controls within this single diagnostic. Inherited generation
configuration: greedy, max_new_tokens1400, one sequence, EOS151645/151643,
pad151643, use_cache false, context cap2048. Each generation bounded120s;
each model process bounded1800s including baseline checks/load/hash overhead.
Reserved GPU8GiB, device-free1.5GiB, worker RSS16GiB; per-step checks and external
100ms RSS watchdog. Retain timeouts/errors and stop on resource/protocol failures.

## Frozen evaluation expectations

Evaluate exactly prefix + raw continuation with only a final generated EOS
removed for text decoding. Preserve all token IDs, EOS, raw text and binary logits.
No fence stripping, whitespace normalization, identity sealing or repairs.
Use unchanged R6.56 scorer, R6.18 schema/native typed validator/expander/VM and
frozen R6.48 E01–E06 functional fixtures. No historical rescoring and no P6-A04
acceptance/P6-A05 access. Top-level required keys are definitions/foundation/program/
version. Native stage failures govern; later validations are NOT_REACHED when
blocked. Lexical key occurrence is separate from structural presence.

First divergence: strict parser offset for serialization failures, native diagnostic
path/code for schema/type/semantics, and first functional difference if reached.
Report missing top-level keys, visible wrong-type labels, repetition (consecutive
identical8-token blocks), premature EOS with incomplete package and token/time
truncation. Wrong typed arguments/semantic operations are only validated at reached
stages; do not infer their correctness from snippets or target string inequality.

Classification: first-token blocker requires decisive initial-choice evidence AND
full validation/functional acceptance under this minimal prefix. Prefix continuation
supported requires correct independently scored continuation beyond supplied bytes.
Persistent downstream construction failures support broader generation gap; incomplete
measurements are inconclusive or protocol halt. No independent authoring/generalization
claim. Publish failures and stop; smallest next experiment is recommendation only.
