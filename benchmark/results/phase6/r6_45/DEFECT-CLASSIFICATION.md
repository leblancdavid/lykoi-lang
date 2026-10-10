# Defect classification

**Final: `R6_45_INTEGRATION_DEFECT` — category E.**

The requirement is determined. The generated application violates its public
persistence error contract through a generic backend decoder integrated without
the nonmigrating application's storage/error policy. The originating implementation
branch is in production runtime_template, not participant-authored kiln guards.
“Integration defect” here includes decoder-to-application error-contract integration;
it does not imply the JSON transport changes an otherwise correct code.

| Candidate | Finding |
|---|---|
| A — application implementation defect | The deployed application's observable behavior is defective. Localization is shared loader/integration rather than the authored field/guard/invariant intent; E is the more precise primary category. |
| B — requirement formalization | Intent's fields/invariants do not restate the complete raw-store/error policy, and the generator leaves that policy implicit. This is a contributing interface/formalization omission, not missing source authority. |
| C — acceptance expectation | invalid_state follows explicit list/invalid-state/no-migration clauses. No evidence supports replacing it with migration_required. Missing shape coverage is a qualification limitation, not an incorrect expected code. |
| D — semantic capability gap | Not established. Existing list/record validation, errors, rejection preservation and explicit migration semantics express the relevant meanings. The chosen intent interface lacks a decoder override, but an unavailable override does not prove irreducible missing meaning. No alternate declarative implementation was executed or qualified. |
| E — integration/error translation | Supported: schema_version=1/no migration intent; shared decoder raises raw migration_required before validity checks; wrapper forwards it; preserved diagnostics show the same code in both versions. |
| F — ambiguity | No material ambiguity for `{}` in kiln. Generic versioned-loader precedence and any proposed new legacy schema remain separately unresolved. |

R6.44 SEMANTIC-AUDIT's field named `capability_gap` is preserved verbatim. Its narrow
observation—no exposed declarative decoder-error override—is valid, but does not
establish category D. This prospective interpretation does not edit its label,
R6.44 scores, evidence or `R6_44_COMPARISON_INCONCLUSIVE` classification.

Evidence scope: one exposed synthetic application; six observations per track
from R6.44 plus static path analysis. No new independent replication, universal
compiler soundness verdict, verified repair or architectural-superiority claim.
