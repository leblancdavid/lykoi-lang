# T1 base — current production capability assessment

Terminal: `PRODUCTION_REQUEST_RECORD_UNION_PROFILE_GAP` (static assessment).
No semantic candidate, compilation or acceptance execution; zero repairs.

## Obligations and available compositions

- Contract 2–3: strict exact-key request, stock record list and discriminated
  reserve/release/ship record list, validate **all** shapes before duplicate SKU
  or operation errors. `predicates.scalar_type` admits scalar values and collections
  of nonnullable scalar elements (`src/air_compiler/predicates.py:19–34`);
  `mutable_values.compose:114–124` has the narrower primary collection element
  profile. No parameter record/union schema or request-level record-list validation
  interface is admitted. `references.py:192–200` validates parameters with that
  same type vocabulary. These are current interface/profile limits.
- Decoded state is genuinely useful: `reference_runtime.py:28–44` checks exact
  stored entity fields, types and unique keys. It cannot validate this heterogeneous
  operation-input sequence before dispatch. Treating request records as valid
  stored rows would require prior host shape normalization/validation or would
  substitute stored-state error precedence for clause 3. JSON decoding and exact
  projection alone do not supply those semantic decisions.
- Clauses 4–5 have expressible subsets: ordinary stock/hold/used-ID entity schemas,
  exact identity lookup, existence/extent and numeric comparison guards, ordered
  guard errors, integer counters, explicit listing keys, and hold active/inactive
  state. See `references.py:62–115,186–247` and
  `reference_runtime.py:261–301`. These subsets were assessed, not executed.
- Checked addition accepts signed operands and cardinality (`computation.py:14–58`;
  `docs/typed-computation-v1.md:63–99`). Runtime subtraction is not a named
  operator, but this **finite** domain could admit a declared finite table and
  selection/cardinality composition; arithmetic absence alone is not the gap.
- One existing record write plus 1–8 dependent ordinary creations is supported
  (`atomic_state.py:29–106`; `docs/atomic-durable-history-v1.md:17–38`). Stock
  counter updates plus a new hold/used marker are plausible partial compositions.
  Coupled arbitrary existing-record updates/deletes and arbitrary request folds
  are not supplied by that creation interface. Alternative hold-state/counted
  views merit consideration; no irreducibility claim is made for the state logic.
- Clause 6 requires a pure deterministic request result. Existing writes use the
  declared one-store persistence interface (`reference_runtime.py:130–150`), not
  a normal in-memory request-state fold entrypoint. This is an additional profile
  mismatch, not the primary terminal evidence.

## Why no transport substitute

The permitted transport can decode JSON, pass typed values to compiled APIs and
project exact observations. A Python validator for object keys, discriminated
record shapes and whole-request validation precedence would implement clause 3.
A Python inventory processor would implement clause 4. Neither was authored.
The terminal classification is a current production interface gap, not an author
failure, executed acceptance failure, or proof about kernel 26 expressiveness.

Read inputs: own `tasks/T1/contract.md` and `acceptance.json` (15 cases), current
production files/documents itemized in `../../AUTHORING.md`. Recorder start preceded
task-specific reads; GAP.json holds the actual elapsed interval.
