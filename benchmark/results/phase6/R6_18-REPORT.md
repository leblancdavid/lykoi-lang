# R6.18 — Minimal typed symbolic composition prototype

**Final classification: `R6_18_TYPED_COMPOSITION_SUPPORTED`.**

Deterministic construction, validation, hygienic reuse and expansion succeeded in
the declared tiny subset of unchanged R6.10 semantics. Expanded plans preserve
the full observed VM behavior of their explicit twins over the tested bounded
domains and controls. This establishes bounded composition infrastructure, not
AI discovery, reasoning improvement, universal equivalence or language completeness.

## Scope and implementation

The owner explicitly authorized this isolated nonproduction implementation.
Initial Git status was clean. Before implementation, checks verified14 R6.17
publication identities,795 protected Git blobs,20 dedicated R6.10 publication
identities and the production26-construct ledger. [Baseline](../../../experiments/typed_composition_r6_18/BASELINE.json)
records810 protected raw SHA256 identities, including production sources/schema/
model/generated/tools, the VM, R6.3–R6.17 dedicated history and R6.16 implementation.

Implementation: [experimental directory](../../../experiments/typed_composition_r6_18/README.md).
The [frozen bounded protocol](../../../experiments/typed_composition_r6_18/PROTOCOL.md),
[schema](../../../experiments/typed_composition_r6_18/typed-composition-1.schema.json),
[semantics and validation rules](../../../experiments/typed_composition_r6_18/SEMANTICS-1.md),
`composition.py`, `examples.py` and `controls.py` define the deliverables.
Types are exact Int64/Bool/Unit. Only seq, UInt8 atom, value, check, end, fixed
UInt16BE emit and ref/const/add/le/eq expressions are qualified. No new VM opcode.
Explicit local dependency DAGs and ordered regions coexist; order is never optimized.
Closed parameter signatures, pinned family/content IDs, scope isolation, deterministic
generated IDs, expansion limits and original VM validation are enforced without an LLM.

One reusable composition is `bounded_add(x,delta,limit)`: value/add then check/le,
returning the immutable sum. Pair context adds two bytes with limit255. Header context
first checks header7, then invokes a nested increment composition before adding the
second byte. Bounded addition is used twice in the latter context with distinct
generated scopes and exactly the same definition ID as in the pair context.
All example artifacts, independent explicit twins and expansion maps are published.

## Equivalence and repeated determinism

[Raw results](../../../experiments/typed_composition_r6_18/RESULTS.json) contain:

| Context | Unique byte pairs per pass | Success | BOUND failures | Passes | Work range |
| --- | ---: | ---: | ---: | ---: | ---: |
| Pair | 65,536 | 32,896 | 32,640 | 3 | 17–23 |
| Header + nested increment | 65,536 | 32,640 | 32,896 | 3 | 25–42 |

393,216 differential input observations /786,432 public VM executions, zero
mismatches. Each exhaustive pass also checks the independently stated integer
relation and its permitted output/failure domain. The entire VM envelope is compared:
exact result types/values, provenance, consumed bytes, private output/output spans,
errors/code/offset/node/stage/path/expected and logical work. Each context's full
observation digest is identical across all three passes. Explicit/lowered canonical
plans and identities match exactly. Ten repeated expansions per context reproduce
the plan, expansion map and identities. This is finite evidence, not a theorem.

511 retained control observations compare ordered node-entry traces and entire
public execution envelopes: empty/truncated/trailing inputs, competing bound failures,
all256 header values, every work cutoff through full successful work plus one for
success/bound/trailing inputs, and tightened depth/input/output budgets. A test-only
Machine subclass records entries; its envelope is checked against uninstrumented
public execute. Neither the VM implementation nor normal executor is altered.
Traces cover controls; exhaustive full-domain runs compare envelopes, not entry logs.
Six signed/encode-domain probes and an addition-overflow unit control preserve
existing runtime failures rather than claiming typing makes every program succeed.

## Adversarial controls and failed attempts

All25 named representation rejections and6 strict-serialization rejections passed:
self/indirect symbolic cycles, local data cycles, wrong-type arguments, unknown
symbols/missing or dotted references, parameter/local and caller-capture attempts,
duplicate bindings, unsupported opcodes/codecs/expressions, computed arguments,
missing deps, invalid/duplicate evaluation order, malformed definition/parameter/
node shapes, content/call/foundation identity tampering, tight and default expansion
budget exhaustion, duplicate JSON keys, broken JSON, float/nonfinite values and
oversized/deep representations. Valid nested composition and isolated repeated reuse
are positive controls. A156-case shape mutation sweep also passes (153 changed-invalid
representations reject;3 identical no-op replacements remain valid). Eight wrapper
test methods and82 unchanged VM regression methods pass.

Two failed attempts are retained. [Attempt1](../../../experiments/typed_composition_r6_18/FAILED-ATTEMPT-1.md)
incorrectly expected identical-field replacements to reject and miscounted the sweep.
[Attempt2](../../../experiments/typed_composition_r6_18/FAILED-ATTEMPT-2.json) preserves
the interrupted original runner source, completed pair-pass counts and failing raw
observations: the outer nested sum's error offset is3, not1. Existing seq result
wrapping changes the returned Cell span to the region start; inner increment failure
still reports1. Explicit and lowered results already matched. Only test expectations
were corrected; no validator/expander/VM behavioral repair occurred. Completed final
evidence is explicitly subsequent to this interrupted attempt, not a first-attempt claim.

## Structural and execution measurements

Canonical compact JSON bytes include full registry/signatures/pins/foundation:

| Measure | Pair | Header + nested increment |
| --- | ---: | ---: |
| Symbolic package bytes | 1,483 | 2,607 |
| Program-only bytes | 757 | 1,322 |
| Registry bytes | 587 | 1,146 |
| Expanded plan bytes | 2,217 | 4,548 |
| Expanded VM nodes | 8 | 14 |
| Symbolic validation median | 102.10 µs | 169.65 µs |
| Expansion after symbolic validation, including VM validation | 66.50 µs | 128.45 µs |
| Full wrapper validation + expansion | 182.20 µs | 315.30 µs |
| Original VM validation | 16.80 µs | 31.50 µs |
| Lowered public execution | 28.90 µs | 53.20 µs |
| Explicit twin public execution | 29.30 µs | 53.55 µs |
| Expand + public execution per call | 223.85 µs | 392.65 µs |
| Full-wrapper Python allocation peak | 22,734 B | 39,019 B |
| Lowered execution allocation peak | 5,200 B | 6,416 B |
| Logical work difference against explicit twin | 0 | 0 |

Timing medians are200 sequential repetitions per method on Python3.14.3/Windows;
raw environment/min/max and per-method tracemalloc peaks are retained. Tracemalloc
measures one call's traced Python allocations, not process RSS or native memory.
Validation and expansion measurements are separated using a private already-validated
measurement seam; production public-path evidence always uses full expansion/public
VM execute. Cold imports, local inference, model authoring/retrieval/token cost and
total development memory are unmeasured. Timings are not isolated-hardware comparisons
or causal efficiency claims. The independent explicit plan deliberately shares the
deterministic site/binding identity convention; expanded byte size includes long
hash-derived IDs. Compactness does not establish reduced AI authoring cost.

## Limits and smallest recommended next experiment

This same-agent infrastructure qualification has no independent specification review,
task/model separation, adaptive discovery, local model selection or comparative run.
The profile is monomorphic, closed and finite: no records/projections/lists/recursion,
user-defined encode layouts, effects, persistent registry/admission/retrieval lifecycle,
general graph compilation or semantic equivalence solver. Call arguments are literal/
reference templates, not call-by-value computations; seq wrapping, repeated expression
charges, provenance and failure precedence remain visible. Conservative bounds/types
can reject useful constructions. Exhaustive testing covers the two byte-pair domains;
the entire signed64 domain, all malformed representations and arbitrary nesting are
not exhaustively proved. Frozen VM's original typing/cost/encode-path limits remain.

Smallest next experiment, **only with separate authorization**: add one reusable
two-ordered-check composition and two nested callers with conflicting failures;
qualify dominance, literal-versus-materialized parameter provenance, every work cutoff
and sequence-result spans over a small exhaustive domain. Keep the same operation
allowlist and foundation. This targets the concrete span/order seam before any broader
type surface or R6.17 task/model commissioning.

## Publication integrity and stop

[Publication manifest](../../../experiments/typed_composition_r6_18/PUBLICATION-IDENTITIES.json)
and [verification receipt](../../../experiments/typed_composition_r6_18/VERIFICATION.json)
check all810 protected identities, published bytes/JSON/links/new-file whitespace,
additive guidance and `git diff --check`. Fresh-process verification replays131,072
byte pairs, matching all saved digests, plus511 trace controls and25 adversarial
representations. Publication manifests exclude themselves; the separate verification
receipt binds the manifest hash. Historical R6.3–R6.17 records remain byte-identical.
Production/compiler/lowerer/runtime and frozen VM remain unchanged; kernel stays26.
No P6-A04 acceptance, P6-A05 access, new provider dependency, training/fine-tuning,
local model inference or full comparative study.

**Stopped after bounded prototype publication. Await explicit owner authorization.**
