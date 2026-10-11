# R6.65 scorer dependency analysis

## Exact dependency and repair boundary

R6.64 `experiments/incremental_training_r6_64/run.py:77-78` imports `jsonschema`
inside `score` solely to validate the action against the frozen R6.63
`step-1.schema.json`. Its unavailable import happens after strict parsing and
before operation, operand, type, dependency, assembly and behavioral scoring.
The false defaults in the preserved first failure are unmeasured downstream
checks. This library is not required by deterministic execution or assembly.

The successor is `experiments/incremental_scorer_r6_65/scorer.py`. It retains the
R6.64 score dimensions and exact canonical selection comparisons, removes the
third-party schema call, and adds explicit stage/error classifications and
conjunctive acceptance. Original R6.64 code, targets, failure and publications
remain byte-identical. There is no training-runner integration in this round.
No dependency is installed; no version requirement for `jsonschema` is needed
for this successor. Historical envelope validators still have their original
dependency; this qualification does not replace them or claim to validate
arbitrary JSON Schema documents.

## Validation requirements and authoritative machinery

| Requirement | Frozen requirement and implementation |
| --- | --- |
| Strict serialization | Unchanged R6.18 `composition.load`: bounded JSON, duplicate-key rejection, no floats/exponents/nonfinite numbers, no markdown or trailing objects; representation depth/string/Int64 limits. |
| Required/forbidden fields | `composition.shape` reused for exactly id/type/deps/node and exactly op/expr; direct operand dictionaries contain exactly ref or const. |
| Selected envelope | id exactly `selected`, node op exactly `value`, type exactly Int64 or Bool. This is the frozen step schema, not the broader production model schema. |
| Operation enumeration | Exactly one expression key, add/le/eq; exactly two ordered direct operands. Recursive expressions and additional operation keys reject. |
| Operand/literal representation | ref is exactly a string; const uses unchanged `composition.expression` and tree bounds: signed64 int, exact bool, or Unit null. bool is never an int; no coercion. |
| Dependency representation | Exactly a list of at most two unique strings. Membership/order/exact direct reference set are separate assembly checks. |
| Scope and references | Unchanged R6.63 `assembly.apply`: immutable before-state identity, validated full prefix, ASCII identifier/existence checks, exact typed available literals and direct reference scope. Self/unknown/malformed references reject. |
| Operand/result types | Existing expression typing: add/le require two Int64 operands; eq requires identical types. Declared type must equal inferred type and before-state result obligation. |
| Dependency meaning | Existing assembler requires exactly sorted distinct direct references. No missing, extra, unsorted, transitive-parent substitution or dangling dependency is admitted. |
| Deterministic assembly | Existing native sealing, package validation and expansion; repeated assembly of strict serialized reload must match after-state and validation. Gold also matches frozen AFTER/native VALIDATION. |
| Invalid task arguments | Existing `assembly.behavior`: exact parameter-key set and exact literal type; ARGUMENT_SHAPE/ARGUMENT_TYPE are fixture outcomes, never coerced values. All four frozen invalid-argument fixtures are exercised. |
| Correct semantic selection | Separate exact operation, ordered operands, type and dependency comparisons against unchanged expert action. Schema/type validity does not imply correct selection. |
| Behavior | Existing AI-independent R6.10 execution through unchanged R6.63 observation path; exact expected status/type/value/error comparisons. No model or new evaluator. |

The finite local shape checker implements all constraints in the pinned step
schema on the domain admitted by the existing strict loader. The schema by
itself admits mathematically integral floating JSON numbers in some validators;
the prior scorer's strict loader already rejects those before schema checking.
Existing representation bounds also remain stricter than the schema alone.
Schema-valid null literals do not imply scope admission or a Bool/Int64 result.
These distinctions are retained, not relaxed.

## Error and acceptance semantics

- `SERIALIZATION_FAILURE`: strict loader failure (including its resource/Int64
  bounds); preserve native code/path/detail separately from scorer stage.
- `SCHEMA_FAILURE`: parsed action violates the closed frozen action shape/domain.
- `ASSEMBLY_FAILURE`: schema-valid action fails existing scope/type/dependency
  or native assembly validation.
- `SEMANTIC_MISMATCH`: assembly succeeds but any exact selection or behavioral
  acceptance dimension is wrong. This is a valid-but-wrong choice.
- `ACCEPTED`: all eight historical acceptance dimensions pass conjunctively.
- Unexpected errors are `INFRASTRUCTURE_FAILURE`, not semantic rejection.

A commutative operand swap can pass all fixtures while failing exact ordered
source selection. This remains rejected by full acceptance. A wrong operation
can retain correct operands, result type and dependencies, yet fail behavior;
the dimensions are independently reported. Exact target reproduction remains
an additional observation rather than a new acceptance obligation.

This is same-coordinator deterministic qualification on exposed expert data,
not independent schema certification, universal equivalence or model learning.
