# R6.64 — Prospective B-only incremental construction smoke

Owner authorization: one bounded nonproduction QLoRA experiment on the ten R6.63
expert demonstrations. Exact qualified ACTION targets and B-RECORD-2 provenance;
no A or C training. All history and execution semantics remain immutable.

## Freeze before calls

Use original pinned R6.52 Qwen2.5-Coder-1.5B-Instruct checkpoint/tokenizer with
R6.59 environment and cache-release mechanics. Fresh seed651 adapter must match
the R6.52 initial112 tensors. Never initialize from R6.59 trained weights.
NF4/double-quant BF16, SDPA, FP32 rank8 q/v adapters, alpha16/dropout0.05,
nonreentrant checkpointing, sequence2048, microbatch1, accumulation4.
AdamW exact R6.55 settings including weight_decay0 and lr1e-4; norm2/max1 clip.

Exactly80 presentations: D01 through D10 in order, repeated eight complete cycles.
Each record appears eight times; four consecutive presentations per update.
No shuffle, packing, truncation, dataset variants, held-out sources or reserved
Unit/shared-diamond material. Full skill and schema system context plus human
requirement and complete immutable state are frozen identically for training and
diagnostics. Gold targets and fixtures are never in inference prompts.

R6.54 scheduler:20 total updates,2 warmup, constructor LR0; optimizer then one
scheduler tick per successful update. First LR0 update advances moments only;
no change to historical schedule or total-step semantics. Completion JSON plus
one turn EOS supervised, prompt/newline/padding ignored; causal mean per record
divided by4, four backward calls per update. Delete graph references after
backward and hash accumulated gradients across every controlled cache release.

## Diagnostics and acceptance

Before training freeze ten exposed records and three coordinator-authored
structurally varied diagnostics: literal-only addition, repeated-reference le,
and literal-first equality against one prior Bool alias. These three are only
diagnostics, never training records or independent evaluation material.
Gold actions must pass strict serialization, step schema, exact operation,
ordered operands, result type, dependencies, repeatable deterministic assembly
and all literal behavioral expectations before model dispatch.

Greedy decoding, one beam, max128 new tokens, repetition_penalty1.1, cache off,
EOS-only termination, exact pinned tokenizer/chat template. Preserve raw text
and token IDs; no fences stripping, JSON repair, decision correction or alternate
decoding. Score dimensions separately. Invalid model output is a diagnostic
observation, not an infrastructure halt. Repeat identical prompts/configuration
after fresh-process reload. Also measure paired eval-mode completion-only loss.

Reserved VRAM ceiling8GiB, device-free floor1.5GiB, worker RSS16GiB,100ms checks,
training/diagnostic process1800s, each generation120s, reload120s. Stop on any
observed resource violation, nonfinite loss/gradient, base update or unrecoverable
error. One exclusive training claim; no retry or modified settings. Save10/20
adapter-only checkpoints with two-checkpoint retention; no merge or search.

## Learning assessment and publication

Report likelihood fitting, exposed reproduction, valid generation and varied
semantic selection separately. Incremental learning supported requires verified
changed adapter and improved valid generation, not merely updates or lower loss.
No generalization or complete-program claim. Publish exact dataset/configuration,
sequence/schedule, diagnostics, raw calls, losses/resources, adapter identities,
reload, comparison and preservation verification. If preflight is incomplete,
publish protocol halt before updates. Resource/stack failures retain first evidence.
Production kernel26 and all historical production/experimental semantics remain
unchanged; no P6-A04 acceptance or P6-A05 access. Stop after publication and await
explicit authorization.
