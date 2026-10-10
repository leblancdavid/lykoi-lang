# Architectural implications

## Demonstrated or directly localized

* **Requirement-to-program integration:** an explicit list-only/no-migration/error
  contract was lowered through a generic versioned persistence loader. The intent
  schema carries record facts and policy guards, but no independent decoder-error
  policy. The generated application leaks a code outside its declared version-1
  behavior failures. Static type/binding/effect validation did not prevent this.
* **Persistence validation ordering:** for `{}`, shared decode_state fails before
  whole-store record validity and predicates. Typed invariants cannot classify an
  input they never receive. Strengthening the kiln invariant alone is ineffective.
* **Migration classification:** the executed branch checks mismatch, not whether
  the payload is recognized, valid legacy data or eligible for an explicit chain.
  The observed migration_required does not prove migration is possible or required.
* **Error reporting:** wrapper forwarding is faithful to the backend code but not
  the application's public error contract. Error identity declarations are not a
  complete executable guarantee over decoder exceptions.
* **AI-assisted review:** the existing separate-session pre-author review and frozen
  baseline cases did not qualify this wrong-shaped input. Participant self-testing
  exposed it later; preserved unscored diagnostics corroborated it. That shows a
  coverage/review seam in this trial, not a comparative defect-prevention advantage.

## Bounded deductions and unverified hypotheses

The shared function predicts the same branch for other non-list/wrong-version
payloads, and predicts version-1-envelope permissiveness. These are static controls
to investigate prospectively, not newly measured cross-application failures.

A broader design may benefit from explicit persistence-format, recognition,
version-selection and error-precedence contracts carried through lowering and checked
against emitted runtime behavior. That is a prospective architecture recommendation;
this round neither implements such a contract nor proves a general formalization
failure. A whole-program error-effect guarantee or migration recognizer is not shown
necessary as a new primitive. Existing list/value/error/validation meanings suffice
for the identified requirement, while the current selected integration does not
faithfully expose them for malformed raw stores.

**Scope conclusion:** the obligation is application-specific; the originating loader
and integration mechanism are shared. Therefore the issue has an architectural
interface implication, but it is not evidence of kernel insufficiency, universal
unsoundness, general AI review unreliability or Lykoi-versus-Python superiority.
Deterministic application execution remains AI-independent.
