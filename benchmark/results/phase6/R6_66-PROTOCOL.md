# R6.66 — Final incremental training preflight protocol

Owner authorizes one bounded CPU-only nonproduction preflight. This protocol
freezes a fresh original-base ten-record training specification; it authorizes
no model inference, optimizer/scheduler updates or fine-tuning. GPU execution
requires separate owner authorization after terminal publication.

## Inputs and settings fixed before qualification

- Immutable R6.63 D01–D10 identities in ascending episode order. Exact R6.64
  conversion and the same three prospective structural diagnostics are reused.
  No training-data or diagnostic expansion; no reserved-family solutions.
- R6.65 successor scorer, unchanged, enforcing all eight acceptance dimensions.
  Preserve R6.64 scorer, halt, traceback, publication and historical classifications.
- Exact R6.59 interpreter and inherited infrastructure. R6.52 original checkpoint
  and tokenizer revision `2e1fd397ee46e1388853d2af2c993145b0f1098a`.
- Seed651; NF4 double quantization; BF16 compute; FP32 rank8 q/v adapters,
  alpha16/dropout0.05; fresh trainable adapters with inference_mode=false.
- Sequence2048; microbatch1; accumulation4; no packing/shuffle/truncation.
  Eight D01–D10 cycles,80 presentations, four per update,20 planned updates.
- Completion plus one EOS; prompt, newline after EOS and padding masked.
  Installed causal shifted masked mean per record divided by4, no token pooling.
- R6.55 ordinary adapter-only AdamW, LR1e-4, decay0, betas0.9/0.999, eps1e-8;
  all remaining optimizer kwargs preserved. Clip norm1; nonfinite halts.
- R6.54 linear schedule, warmup2/total20. Update1 uses LR0; one scheduler tick
  after each completed optimizer update. CPU simulation calls the pure factor
  function only; no optimizer or scheduler instance or update.
- R6.58 controlled cache release as preserved in R6.59. Reserved ceiling8GiB,
  device-free floor1.5GiB, RSS16GiB; monitoring0.1s; process1800s, reload120s,
  per-generation120s. Greedy128 tokens, one beam, repetition penalty1.1, cache off,
  terminal EOS stripped only. No repair or expectation inference from outputs.
- Checkpoints step10/20 in new historical external store `r6-66`, retention2.
  Atomic telemetry, exclusive dispatch/run/path claims, no automatic retry/resume.
  Recovery preserves raw failure/accounting and requires new authorization.

## Qualification and freeze

Verify historical publication, executable, distribution, checkpoint, tokenizer,
adapter, production and experimental identities through inherited fresh-process
audits. Freeze source before execution. Convert exact records, freeze complete
sampling, validate gold and replay R6.65 negative controls. Use pinned offline
tokenizer to retain exact IDs, masks, causal target/logit positions, effective
assistant prefix and headroom for all13 cases. Reject malformed records.

Freeze canonical configuration and executable effective worker. Independently
replay all CPU checks in a fresh pinned process, including installed loss helper
on synthetic CPU tensors (no model or backward), exact scheduler factors, source
binding and absent output/dispatch paths. Mandatory components must all be
QUALIFIED. Any failure is retained and halts; readiness cannot follow imports alone.

Publish report, evidence, readiness and identity manifests; perform a fresh-process
publication check and `git diff --check`. Preserve kernel26/semantics/R6.3–R6.65;
P6-A04 acceptance0/P6-A05 access false. Stop after publication. The proposed next
experiment measures exposed fitting/mechanics, never independent generalization.
