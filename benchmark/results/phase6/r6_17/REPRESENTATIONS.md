# R6.17 — Symbolic representation alternatives

Qualitative engineering predictions to test, not measured rankings. All forms
require explicit types, closed operation contracts, exact dependencies and effects.
Serialization size and token efficiency must be measured with the pinned tokenizer.

| Alternative | AI generation difficulty | Composition / deterministic meaning | Validation complexity | Token efficiency | Modification locality / reuse | Compiler feasibility |
| --- | --- | --- | --- | --- | --- | --- |
| Typed expression trees | Locally simple grammar; nested binding/duplication can be hard. | Explicit operand structure; sequencing/effects require additional regions. | Local recursive typing straightforward; repeated trees increase visits. | Often verbose for repeated subexpressions; not known for a local model yet. | Local subtree edits easy; reuse needs named functions/definitions. | Simple recursive lowering; preserving repeated evaluations matters. |
| Directed semantic graphs | More IDs/edges and scope management for AI. | Explicit shared values/dependencies; topology alone does not define error/effect order. | DAG, dominance, typing and schedule checks; sharing can reduce storage but not all checking. | References can avoid repeated bodies; IDs/index documentation cost tokens. | Stable node edits and dependency slicing; broad fan-out can enlarge impact. | Feasible topological lowering with explicit schedule and source map. |
| Canonical operation sequences | Linear authoring familiar; long-lived bindings harder. | Explicit order/errors; dataflow sharing through prior bindings. | Dominance/typing/closed scope checks; easier schedule validation. | Predictable overhead; repeated patterns verbose without composition. | Insertions affect downstream scope; parameterized sequence reuse feasible. | Direct lowering; avoid order-sensitive implicit stack conventions. |
| Compact symbolic references | Short calls but discovery/retrieval/signature knowledge difficult. | Meaning only through pinned verified definitions; names alone insufficient. | Resolve transitive closure, substitution and expanded bounds. | Call-site savings may be outweighed by documentation, retrieval and expansion. | Reuse strong if interfaces transfer; registry revisions affect many callers. | Macro expansion feasible; opaque execution meaning forbidden. |
| Hybrid typed DAG + ordered regions | More schema concepts, but splits pure dependencies from execution order. | Typed value sharing plus explicit node/region order; pinned references optional. | Requires both DAG/type and region/scope/schedule validation. | May reduce repeated authoring; initial schema cost larger. | Stable node identity with scoped region edits; reusable closed regions. | Deterministic expansion into foundation sequences; qualification required. |

## Recommended initial candidate

Use a **hybrid DAG/sequence**: pure typed expressions have explicit operands and
bindings; cursor/effect/error-observable nodes live in ordered regions. A node may
refer only to dominating values or declared parameters. Shared definitions are
not runtime memoization: a call executes its expanded body in the declared order.
Never silently common-subexpression-eliminate operations, reorder checks or reduce
work because a value looks pure; error sites, provenance and cutoffs are observations.

For the first experiment, graph serialization is a closed JSON document with
stable node keys, type/signature declarations and ordered region member lists.
Structural arrays retain semantic order; object key order does not. Compact
references point to immutable definition hashes; display names are only metadata.
No model-only latent code, natural-language execution instruction or arbitrary host
expression is executable source. Human review prose may accompany the artifacts.

## Decision challenge before a scored run

On neutral qualification fixtures, serialize the same typed computation as a tree,
bound sequence and hybrid graph. Compare authored tokens, expanded nodes/expressions,
validation/lowering time, diagnostic locations and a localized edit's dependency
footprint. Equivalence is exact ordered execution under the same foundation.
Select the hybrid only if deterministic lowering and diagnostics qualify within
the fixed bounds. If they do not, stop and amend prospectively before task curation;
do not switch representations after hidden-task failures. This challenge is future
qualification, not an extra model search budget during scored evaluation.

Keep B and C's grammar, checker, lowerer and reference facility identical. Their
difference is library origin/adaptation during development, not a superior graph
compiler, shorter unmetered prompt or additional runtime semantics for C.
