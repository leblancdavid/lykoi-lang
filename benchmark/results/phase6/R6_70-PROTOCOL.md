# R6.70 — Final constrained-decoder integration qualification

Owner-authorized bounded nonproduction correction of neutral serialization only.
Preserve all R6.3–R6.69 history, including untracked R6.69 publication. Verify
R6.68/R6.69 manifests and inherited checkpoint/tokenizer/adapter/scorer identities
before dispatch. No scored inference, rescoring, training or semantic changes.

Reconstruct the neutral dictionary in declared grammar order `id,type,deps,node`
and nested `op,expr` after the sorted configuration round trip. Preserve values,
operation and operands exactly. The R6.68 grammar and R6.69 namespace verifier
remain byte-identical. CPU controls must pass before model loading: correct
order, incorrect outer/nested order, missing/extra fields, types, operations,
all six operation/result alternatives and 100 identical serialization repeats.

Reuse the R6.69 live qualification worker through a frozen, inspectable derived
source: the serialization correction, an additional repeated suffix probe,
per-token prefix/allowed-set fingerprint and selected-token evidence, early raw
probe persistence, and inference initialization/preservation receipts. No
changes to model load, tensor verification, grammar or generation settings.
Use inference mode, frozen parameters and local offline artifacts only.

Two workers, base then adapter, at most five neutral generations each: unseeded
128-token probe, suffix continuation twice (4 tokens each), complete-action EOS
(1 token), one-token budget exhaustion (1 token). Greedy frozen R6.68 settings,
seed651 and precision remain fixed. Limits: 120s/generation, 1800s/worker,
8GiB peak reserved VRAM, 1.5GiB minimum device free. Preserve failures and stop
on unexpected runtime/integrity failures; no model retry. Expected unseeded
budget exhaustion is not a structural failure. Repeated suffix token sequences
must match. Synthetic CUDA controls require exact allowed-token sets, unchanged
allowed logits, forbidden negative infinity, completion-only EOS and invalid
prefix rejection. Actual generation records must match every mask selection.

Ready requires both live 535-entry base comparisons, adapter exact tensor/file
identity, before/after preservation, model-time mask/continuation/EOS/budget and
repeatability controls, frozen nine-case/A/B/C/scorer identity and resource/path
qualification. Readiness permits proposing a fresh successor comparison runner;
it does not authorize dispatch or reactivate the historical R6.68 runner.
Publish one terminal readiness receipt, report, raw controls/resources, source
and publication manifests. Fresh-process integrity and git diff --check required.
Kernel26, compiler/lowerer/runtime and experimental semantics stay unchanged.
No installations, dataset expansion, Python comparison adapter, P6-A04 acceptance
or P6-A05 access. Stop after publication and await explicit authorization.
