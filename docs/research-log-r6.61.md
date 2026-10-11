# R6.61 — Additive observation, decision and current boundary

[Diagnostic report](../benchmark/results/phase6/R6_61-REPORT.md):
`R6_61_BROADER_GENERATION_GAP`. Unchanged pinned checkpoint/R6.59 step20 adapter;
one bounded inference-only first-token/minimal-prefix diagnostic, no training.

## Observation

Fence73594 ranks first on6/6 prompts for each model at both penalties. Raw opening4913
is prompt-present; penalty1.1 suppresses it and widens the fence margin, but1.0 still
selects the fence. Adapter improves opening probability without changing the top token.
Exact supplied `{"` prefix yields ordinary JSON objects on6/6 at both penalties.
Native bounded output acceptance is6/6 at1.1 versus1/6 at1.0 for each model;
five1.0 prompt echoes fail native string bounds. All24 lack a complete package;
schema0/24, type/semantic/functional stages NOT_REACHED. Eleven of12 paired outputs
are exact. Original R6.59/R6.60 outcomes and identities preserved.

## Decision and limitations

Initial fence preference is real but cannot explain away continuing package-structure
failure. Penalty interference is measurable, not a sufficient or necessary cause of
initial fence selection. No accepted-generation adapter advantage or independent
authoring/generalization claim. Supplied opening is a valid partial JSON prefix,
not a complete document or a task solution. Frozen scorer/semantics unchanged.
External watchdog sees launcher PID; own-PID in-process RSS bound is enforced, but
numeric model-worker peak is unretained. No inference rerun to repair instrumentation.
An offline draft conflated native bounded output validity with ordinary parsing;
the preserved correction/audit distinguishes them. Both E05/1.0 outputs contain
version7 but lack the other three envelope keys; all other outputs lack all four.

## Current boundary and recommendation

Production kernel26/compiler/lowerer/runtime and experimental semantics unchanged;
no gradients/optimizer/scheduler updates, fine-tuning, expansion, comparison adapter,
historical rescoring, P6-A04 acceptance or P6-A05 access. Offline publication verifies
baseline identities, raw logits/processor ranks/probabilities, outputs and new scores.

Smallest proposed next step: separately authorized read-only next-key competitor
ranking after the same minimal opening; no additional key/graph prefill or training.
Stopped after publication. Further work requires explicit authorization.

This additive supplement supplies the research observation, tradeoff and current
boundary while leaving inherited hash-pinned shared research/decision/overview
documents unchanged, following R6.60's preservation pattern.
