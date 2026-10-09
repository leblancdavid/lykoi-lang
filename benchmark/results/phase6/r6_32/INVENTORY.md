# R6.32 baseline inventory

[BASELINE.json](BASELINE.json) binds **1,771** unchanged protected raw-file identities
before implementation. R6.31's published checks, manifest hash, all15 listed file
hashes/length-bearing entries and R6.30 preservation/publication union were verified.
The baseline captures HEAD and exact production/experimental implementation pins.
The initial worktree was clean. A baseline-script receipt-field mistake occurred
before baseline capture; [failed attempt 1](FAILED-ATTEMPT-1.json) records it.

| Capability | Existing implementation and scope | Reuse in R6.32 |
| --- | --- | --- |
| Typed composition | `experiments/typed_composition_r6_18/composition.py`, `SEMANTICS-1.md`: content identity, exact Int64/Bool/Unit, dependency/order/type checks, hygienic expansion, fixed VM validation | Direct unchanged API calls for identity/admission/expansion and functional execution |
| Deterministic construction | `benchmark/results/phase6/r6_23/adapter.py`: construct-1 schema/assembly, pins/order and typed wrapper construction | Inventoried and hash-preserved; facade accepts frozen full definitions directly, so compact construction adds no required dependency |
| Production transitions/invariants | `experiments/value_added_r6_16/generate.py`, `src/air_compiler/mutable_values.py`, `profiles.py`, scalar/predicate modules: guarded enum writes, prewrite guards, staged invariants, atomic persistence | Unchanged C generator lowers copied kiln intent and produces both original/modified applications |
| Impact | `src/air_compiler/semantics.py`: reverse dependency BFS and semantic diff over parsed scalar model | Actual unmodified APIs evaluated; extension predicate/mutation omission remains visible |
| Deterministic lowering/generation | R6.18 expand to frozen `experiments/semantic_interpreter/interpreter.py`; R6.16 lower to production scalar/mutable IR and generate_mutable | Exact replay equality and source/IR equality checked |
| R6.30 telemetry | `r6_30/experiment.py`, `evaluate.py`, `evaluate_successor.py`, `recover_and_continue.py`, effort breakdown and native process/session records | Inventory informs null-aware timing/recovery design; no provider/authoring replay |

R6.30's interrupted T2-B had null process wall time, no raw event stream, and native
session export; successor collection preserved missing wall time and token lower
bounds rather than author rerun. R6.32 adds only a local durable journal; it does not
claim to qualify AI-session exports, billing or reasoning attestation.

Kernel accounting remains the exact protected R5.114 ledger: **26 constructs**.
No changes to production compiler/lowerer/runtime/schema/model/generated files,
R6.10 VM, R6.18 wrapper, R6.23 adapter or R6.25 contracts. No P6-A04 acceptance
execution, P6-A05 access, model inference, training or H1/H2 trial.

Baseline pins include existing root guidance/overview/log/decision documents.
New current-round prose is therefore published in separate `docs/*-r6.32.md`
files, following R6.20–R6.31's additive preservation convention.
