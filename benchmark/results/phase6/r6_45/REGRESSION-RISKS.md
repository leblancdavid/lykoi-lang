# Regression-risk assessment and prospective verification requirements

These are risks and required controls, not tests run or regressions observed in R6.45.

| Risk | Why relevant | Required prospective evidence |
|---|---|---|
| Global migration error masking | A real version-2 application must still reject a valid version-1 list with migration_required until explicit migration. | Keep application policy scope explicit; verify an existing migration-enabled fixture separately before expanding shared scope. |
| Incomplete malformed-shape closure | Code translation cannot reject version-1 envelopes that currently decode successfully. | K10 distinguishes error remapping from list-only decoding; report any remaining format seam separately. |
| Valid predecessor state rejected | Old kiln state is often valid current same-schema data, especially firing/closed/emergency. | K06, valid empty/nonempty lists, cold/closed records; unchanged list bytes and cool success. No data backfill. |
| Wrong precedence / partial validation | Moving validation to one operation or after lookup can miss list/create or unrelated invalid records. | K01 across entrypoints and K14–18; extend the same store-first rule to all six known operations in later qualification, including create/cool/rescue. |
| Double-read or partial-state race | A separate host preflight followed by another read introduces a new incoherent snapshot seam. | Use a single decoded snapshot for validation/dispatch; do not claim concurrency guarantees. Review file-read and error origin paths. |
| Rejection changes bytes or absence | Auto-initializing `{}` to [] would violate no-repair and byte preservation. | Exact bytes before/after every rejection; missing remains missing on list; no migration or write on read. |
| Broad exception reclassification | Converting any Failure/OSError to invalid_state could mask persistence failures or domain errors. | Restrict origin/policy; preserve declared lookup/guard/input and persistence errors. Do not generalize Python's broad catch into language authority. |
| Generated provenance broken | Hand edits bypass the frozen generator and may silently diverge at regeneration. | New versioned generator/integration identity, deterministic regeneration identity and model preservation; historical generated sources stay untouched. |

Minimum verification for an authorized option-1 successor: supported shape/error/
precedence rows, normal successful operations, exact no-write checks and a static
scope audit demonstrating no effect on declared migration-enabled paths. Complete
contract qualification additionally needs K10/list-only shape closure and every
operation entrypoint. Production-wide changes need targeted existing compiler,
mutable/state-validation and explicit migration regression suites, plus clarified
generic precedence. No broad historical benchmark rescore is required or authorized.

Do not count any proposed check as passed. New verification would establish only
the tested successor's behavior and preserve original R6.44 classification/scores.
