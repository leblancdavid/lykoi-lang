# R6.78 — Authorized base-only successor

Owner authorizes preservation/reconciliation of four qualified R6.76 observations
and the unknown fifth generation, one explicitly labeled fifth-case replacement,
bounded live launcher qualification and gated continuation of 30 frozen base cases.
No training, adapters, optimizer/scheduler updates or post-training comparison.

Attempt identity: `R6.78-base-successor-1`; case000 is the fifth-case replacement,
not historical recovery. Historical invocation potentially started; completion,
raw output, usage, wall time and billing unknown. Original counts/halts preserved.

Use R6.77 Journal/launcher and unchanged R6.75 fixture order, model/tokenizer,
NF4 base load, seed651, precision, greedy64-token compact decoder and scorer.
Batch size one;1800s worker,120s generation,16GiB RSS,8GiB CUDA reservation,
1.5GiB minimum device-free memory. Instrument allowed-set computation/progress
persistence without modifying grammar, logits, generated actions or expectations.
Full mask overhead unavailable separately; measured subset explicitly identified.
Input/output token lengths are exact where completed; billing unavailable.

Reverify historical outputs without new inference or historical score changes.
Synthetic real-worker timeout/interruption controls precede live replacement.
The replacement qualifies live identity, commitments, raw output and receipt;
duplicate/corruption controls use its committed evidence, without extra inference.
Only after all gates pass may remaining cases dispatch once, in order.
Semantic incorrectness is recorded by frozen scorer and continues as in frozen
diagnostic loop; runtime/decoder/resource/timeout failures halt without retry.
Partial outputs, starts, token progress, traceback and resource samples survive.

Complete means30 qualified observations, four reused plus26 new including labeled
replacement. Other terminal codes: R6_78_LIVE_ORCHESTRATION_PARTIAL,
R6_78_ACCOUNTING_GAP, R6_78_RESOURCE_OR_STACK_GAP, R6_78_PROTOCOL_HALT.
No claim of training readiness or learning improvement follows completion.
Production26/compiler/lowerer/runtime and experimental meanings unchanged;
R6.3–R6.77 preserved; no P6-A04 acceptance or P6-A05 access. Stop at publication.
