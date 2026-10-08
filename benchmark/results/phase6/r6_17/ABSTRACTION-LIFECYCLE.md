# R6.17 — Compositional abstraction lifecycle, specification proposal 1

No implementation or registry exists from this specification. Only reusable
composition of fixed deterministic meanings is admissible in the initial design.

## Artifact and judgment

A proposed definition carries: schema/foundation version and hash; logical family
ID; immutable revision; typed ordered parameters/results; closed body with stable
node IDs; exact direct dependency hashes; effect/cursor/error contract; bounds;
source development-task IDs; proposer/model/prompt/session provenance; validation
attempt log; and admission evidence. Human prose describes intended use, but the
body and pinned contracts define execution. No natural-language evaluator.

Initially use monomorphic signatures over the qualified foundation domains; no
ad-hoc inferred polymorphism, variadic arguments, captured globals, recursive calls,
ambient resources or plug-in code. Input parameters and explicit constant literals
are the only free values. Structural template parameters may select only qualified
node fragments of declared signatures; otherwise refuse them in the initial profile.

Type judgment checks exact domains (Boolean is not integer), record fields, ordered
list elements, all branches/results, dominance and region scope. A call may not
weaken a required input domain, introduce a hidden effect, widen a resource bound
or suppress an error. Reject unsupported type judgments before execution, even if
the original VM would defer them to runtime. A conservative rejection is an
authoring/coverage cost; passing is not proof of requirement correspondence.

## Ten lifecycle stages

| Stage | Required behavior and retained evidence |
| --- | --- |
| 1. Proposed | During development only, AI submits signature, body, dependency pins, intended reusable relation and applicability/non-applicability examples. Retain every draft, rationale, prompt, time and failure. |
| 2. Type-checked | Close free variables; exact argument/result typing; scope/dominance, branch and cursor contracts; no coercion or arbitrary host code. Failures leave immutable rejected proposals. |
| 3. Validated | Check dependency DAG, hygienic expansion, foundation allowlist, expanded resource limits, original validator and exact observation controls. Differential checks compare call and expanded body; exhaust finite small domains where feasible, otherwise fixed boundary/adversarial/metamorphic cases. Contract checks/test coverage are labeled, not universal proofs. |
| 4. Stable identity | Allocate stable family ID for lineage and content ID `sha256(canonical semantic payload)`. Payload includes types, ordered body, error/bound contracts, foundation hash and dependency hashes. Provenance has a separately hashed envelope. Same content cannot acquire different meaning through a display name. |
| 5. Versioned storage | Append immutable accepted/rejected records and admission status to registry; freeze an exact manifest of available revisions. Never mutate an accepted definition or use mutable latest-version lookup. |
| 6. Retrieved | Deterministic type/keyword index returns signature, limits, applicability and exact ID; fetching the full body is available. Log query, rank, bytes/tokens, fetches and time. No task answers or hidden evaluation metadata in index. |
| 7. Composed | Call with explicit typed arguments/dependency pins; capture-free substitution, fresh derived node IDs and ordered regions. Calls execute by expansion, not magical function dispatch. Check combined bounds/authority at call and application level. |
| 8. Revised/deprecated | Development revision creates a new content ID and explicit compatibility/migration record. Retain old versions and callers. Deprecation removes from future default indexes without rewriting historical meaning. Evaluation freeze forbids all additions/revisions/deprecations, including apparently harmless fixes. |
| 9. Lowered | Resolve exact transitive closure, topologically expand definitions, alpha-rename local bindings/IDs deterministically from caller ID + definition hash + local path, substitute typed values, emit original foundation plan and expansion map, then run original validator. Missing pins, cycles, overflow or unsupported expansion reject. |
| 10. Audited | Manifest binds input program, registry, foundation, checker/lowerer, expanded plan and executable. Map diagnostics/work sites from expanded IDs to definition/call provenance without changing raw observations. Retain test evidence and scope, dependency diffs and reverse callers. Audit runs offline without the authoring model. |

Canonical payload: UTF-8 compact JSON, sorted object keys, ordered arrays unchanged,
no floats, duplicate keys or Unicode normalization. Symbol/binding identifiers
are case-sensitive ASCII; arbitrary literal text uses the qualified domain.
Content equality is structural equality, not semantic-equivalence certification.
Semantic rewrites require new versions unless an independently qualified
normalization law is already frozen. Hash integrity is not proof of correct meaning.

## Aliases, reusable compositions and memorization

- **Alias:** a new label for one operation or the same body with renamed symbols;
  no new parameterized behavioral structure. Count separately; never credit it as
  a discovered semantic abstraction or omit its storage/retrieval cost.
- **Reusable composition candidate:** binds a multi-operation relation and an
  explicit interface/ordering/error discipline, with at least two independently
  authored development-task uses with different inputs/constants. Admission
  requires those two uses; their success is development reuse, not generalization.
- **Transfer:** an admitted definition is used successfully on an unseen task or
  unfamiliar combination without registry edits. Report per-definition and
  per-task results, including unused definitions, failed reuse and hand-inlining.
- **Task memorization:** full-task bodies, copied example answers or finite tables
  of whole acceptance cases are prohibited. Task-specific constants are visible
  and charged. Legitimate finite tables for a declared general relation remain
  possible but must have an explicit domain and evaluation variants outside the
  development examples; do not relabel table lookup as neural emergence.

Admission does not require unique novelty beyond existing macro techniques. A
successful composition is an ordinary verified macro unless the comparison shows
that AI selection improves transfer over the matched human-designed macro control.

## Growth, dependencies and correctness boundary

Per development run: at most 24 proposals (all attempts, including revisions), 12
admitted composition definitions, dependency depth 4 and 256 stored body nodes
in total. Aliases consume these same storage/proposal caps and are separately counted.
Unused/redundant definitions may be deprecated only before freeze; their construction
cost remains. Index size/full expanded bytes are also reported, not hidden by node caps.
Equivalent capacity caps apply to the hand-designed control. A definition must still
fit unchanged VM bounds after application expansion: 64 structural nodes, depth16,
2048 validator expression visits and the original runtime defaults. Macro references
cannot bypass those bounds. Preflight expansion is capped at 64KiB and 4096 expression
occurrences to avoid unbounded generation before original validation; a stricter
original limit still wins. Caps are prospective, not claims about current tooling.

Dependencies have exactly one pinned revision each. Conflicting pins for the same
logical family in one application are rejected initially; no implicit version merge.
Reject self/indirect cycles and forward dependencies during registry admission.
Expansion has no recursion and must terminate within caps. Reverse dependency
indexes support impact auditing, but their completeness must be tested independently.
Declared effects can only compose already qualified effects; initial subset is pure
apart from cursor consumption/private byte output and deterministic rejection.

Correctness claims are layered: shape/type/DAG checks; expansion-by-definition;
foundation validation; differential observation tests; external task acceptance.
None individually proves human requirement fidelity or a universal abstraction law.
Runtime guard failures, well-typed wrong results and unsupported foundation gaps
remain possible and stay in outcome denominators.
