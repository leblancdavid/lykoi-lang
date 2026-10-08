# R6.16 baseline inventory (before application authoring)

Kernel accounting `R5_114-KERNEL-ACCOUNTING.json`: final_count 26. Canonical
production model validate passes; safety reports zero capability violations and
invalid transitions, six invariants (five runtime-enforced, one structurally
guaranteed). This verifies the published accounting and accepted model, not a
minimality theorem. BASELINE.json preserves 775 source/history identities, including
R6.15 transitive R6.3–R6.14 preservation, R6.15 original publication and supplement.
Initial dirty guidance/R6.15 publication is owner work, retained exactly at baseline.

## Existing production

* `air_compiler.validator`: closed entities, references, assignment/type rules,
  effects/read/write/capability authority and declared lifecycle agreement.
* `lykoi_pipeline.scalar_profile.lower`: existing declarative local storage,
  typed fields, creation providers, listing, explicit scalar guards and lifecycle.
* `air_compiler.mutable_values.compose`: record-local typed writes, exact literal
  types, declared input presence, pure typed predicate guards, atomic single-record
  effects and unchanged rejection. Lifecycle fields cannot be arbitrary mutations.
* `predicate_integration` / `predicates`: field/parameter binding, exact operand
  types, pure Boolean trees and record-local invariants. Runtime enforces declared
  invariants on load and commit; validators do not prove guards preserve invariants.
* `profiles.generate_mutable`: validated deterministic production Python backend;
  emits scalar, predicate and mutation runtime. No experimental VM involved.
* `semantics.impact`: structural reverse dependencies over existing model IDs.
  Extension predicate/mutation facts are not fully indexed by legacy traversal;
  do not infer complete impact coverage from returned paths.
* Other existing profiles cover references, bounded arithmetic, conditional atomic
  creation and explicit historical migration. They are not needed for this prototype.

Existing English/FRC/owner approval workflow exists, but is not automatically
appropriate to compare an owner-independent intent interface. The research adapter
will invoke low-level production semantic APIs and report that narrower scope.

## New experimental infrastructure required

No Track B standalone, Lykoi-independent common-intent generator is established.
Build a bounded schema, ordinary Python generator/runtime, C translation to existing
IR, transport and independent acceptance scenarios. Keep these under
`experiments/value_added_r6_16/`. Application intent and submissions are new records.
C shares syntax validation with B, then runs genuine existing Lykoi validation and
executes its backend. Its full FRC provenance and approval layer is not measured.

Unsupported semantics include unrestricted parsing/arithmetic, distributed
transactions, proof of requirements correspondence and general cross-store safety.
This experiment deliberately selects local enum-state/guard/invariant interactions.
Selection therefore favors the existing semantic layer and does not establish
general-purpose expressiveness. Two domains may share structure; report the bias.

## Environment and effort

Windows/PowerShell, Python standard library, current Git/head/platform captured in
BASELINE.json. Available model is openai/gpt-6.1-sol; default reasoning is not
attested. Fresh task contexts can be requested, with shared filesystem/inherited
guidance. Staged withholding cannot be enforced. Sanitized author metadata export
will be attempted; no billing evidence. Unavailable fields remain null. All new
infrastructure/setup is reported as common overhead, not free per-track effort.
