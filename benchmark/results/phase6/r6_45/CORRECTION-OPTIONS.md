# Correction options and smallest recommendation

All options are proposals. No code, semantic contracts or expectations in history
are changed; no option is behaviorally verified.

| Option | Required scope / production meaning | Compatibility and verification |
|---|---|---|
| 1. Application-scoped decoder-error translation | Successor application integration/generator boundary: for an explicitly nonmigrating version-1 list-store application, translate decoder-origin migration_required to its declared invalid_state. No production change or new primitive. Do not translate migration errors for applications that declare evolution. | Smallest repair of the reported error class, not full format closure. Keep all other errors, byte preservation and operation order. Test all operation entrypoints and wrong top-level shapes; ensure migration-enabled apps retain real migration_required. Version-1 envelope acceptance remains a separate format concern. |
| 2. Application-scoped list-only persistence validation | Successor integration implements the **existing** raw JSON-list storage rule before generic version classification, on the same read/snapshot and before dispatch. No rewrite, normalization or callback to an AI; no production semantic change. Generate it from the application storage policy rather than recognizing `{}` or a benchmark case. | More complete closure: rejects every non-list shape, including a version-1 envelope, while preserving empty/valid lists and old same-schema kiln states. Existing generated entrypoints must share this boundary; avoid a separate preliminary file read/TOCTOU seam. Needs list shape, missing-file, field/domain, byte-preservation and precedence controls. This policy is not currently configurable in the frozen intent interface. |
| 3. Shared production decoder correction | Prospective runtime/backend change to distinguish malformed shape from recognized legacy version before choosing migration_required; align version-1 emitted failures with declared contract. No kernel extension follows. | Larger blast radius across scalar/mutable/versioned applications. Generic normal-read version/malformed precedence and supported envelopes need clarification first. Preserve valid legacy lists requiring explicit migration, current envelopes, chain eligibility, idempotence and rejected bytes. Requires targeted compiler/runtime/migration regression qualification. Not authorized here. |
| 4. Change oracle to migration_required | Would weaken an explicit application error rule and make backend behavior normative. | Unjustified. Do not revise frozen expectations or rescore history. An owner may commission a genuinely new contract but that is not repair of the original requirement. |
| 5. Add migration, fields/defaults or an execution primitive | Unnecessary new application/schema/semantic scope. | Unjustified for an object that is not a kiln record list. Do not fabricate legacy data or migration authority. |

## Recommendation

For the single demonstrated discrepancy, **option 1 is the smallest correction**:
an explicitly scoped application-integration error mapping for nonmigrating list
stores. It applies to a meaningful storage class, not an equality test for `{}`.
It must be tied to decoder provenance/application policy rather than globally
rewriting any error string. Existing invariants cannot repair this by adding a
kiln predicate: they run only after the decoder returns.

If the authorized goal is complete list-only persistence contract closure rather
than correction of the observed code alone, prefer option 2 in the same application
integration scope. A same-read list-shape boundary covers the statically predicted
version-1-envelope permissiveness as well. Its modest extra scope should be explicit
in the next authorization; do not claim option 1 solves it.

No smallest **declarative intent-only** edit is demonstrated. v0.3 requires a
schema_version (validator:199–205); mutable composition also relies on it. Removing
it or setting an invented version is not an admitted repair. Remapping generated
code by hand would break provenance. Any successor must be regenerated from an
authorized, separately versioned integration change, with historical sources intact.

Smallest justified next step: authorize one application-scoped successor error-
contract correction and the supported matrix rows, with explicit scope choice
between error-code repair and full list-shape closure. Generic versioned-loader
clarification can be deferred unless shared production correction is commissioned.
