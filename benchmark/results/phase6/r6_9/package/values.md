## Types and observable value policies

Existing writable string, identifier, enum and timestamp scalars retain their
value semantics; existing nullable timestamps remain the only nullable values.
Identity and lifecycle fields cannot be rewritten by ordinary value mutation.
Collections have nonnullable scalar elements of these four types, an explicit
finite enum domain where applicable, **insertion ordering**, **allow or unique
duplicate policy**, and **exact equality**. These are independent typed facts.
Equality compares exact scalar values: case-sensitive string/identifier/enum
comparison and exact timestamp representations, not temporal equivalence.
Empty collections are valid. JSON arrays preserve all retained occurrences and
relative order; they are not mathematical sets. Nested/mixed collections,
numeric/boolean writes and general nullability are outside this profile.

`append` adds another occurrence and requires duplicates-allow. `add_unique`
appends only when no equal value exists; it preserves the prior occurrences and
order, even on a duplicates-allow field. `replace` replaces a whole scalar or
collection. A unique collection is validated for uniqueness; it is **not silently
deduplicated**. Stable deduplication is separately authorized and retains the first
occurrence of each equal value and its relative order. `['b','a','b','B']` becomes
`['b','a','B']`. No sorting, case folding or implicit trimming occurs.

## Presence and deterministic pipelines

Presence is membership in the supplied-input mapping, not truthiness. Omitted
input follows explicit `unchanged` or `reject` policy; reject has a separate
declared missing-input error. Supplied empty strings/arrays are values. Explicit
null is accepted only by an existing nullable timestamp field through the API;
CLI textual `null` is a string, except JSON collection input where it is rejected.
There is no persistent presence tag or general nullable predicate.

Every change declares an ordered `pipeline`, including `[]` for verbatim
preservation, plus `invalid_error` for invalid shape/final type. Steps are:

- `{kind:'transform',operation:'verbatim'|'trim'|'stable_deduplicate'}`;
- `{kind:'validate',rule:'nonempty'|'nonblank'|'typed',error:ERROR}`;
- `{kind:'map_elements',pipeline:[ELEMENT_STEPS]}` on a collection, composing
  existing scalar transforms/validation in order for each retained occurrence.

Trim removes surrounding whitespace using the bounded backend's Unicode
whitespace interpretation. Nonempty tests length, whereas nonblank tests for
non-whitespace content. Thus `trim → nonempty` rejects raw whitespace;
`nonempty → trim` accepts raw whitespace and may store empty. Validation observes
the current pipeline stage. Raw shape checking prevents applying string/list
operations to wrong shapes; enum/domain/timestamp/uniqueness validation is explicit
at `typed` steps and always required on the final result. An element pipeline runs
before a following dedup step only when that order is declared. The pipeline
sequence itself is semantic IR, not backend ordering convention.

Creation pipelines apply only to supplied inputs before existing creation
preconditions; their position relative to those existing guards is fixed by this
profile. Put stage-sensitive creation validation in the explicit pipeline.
Omitted creation inputs use separately typed creation defaults. Update omission
never invokes a creation default. Source reconciliation must authorize changed
creation validation and transformations; prior model guard authority is preserved
by existing-model composition checks.


Single-record mutation reads/validates the complete store, checks existence and
ordered guards, builds a private candidate, runs presence/pipelines/final-value
validation for every change, validates the whole staged store and writes once
using the existing temporary-file/atomic-replace persistence operation. Results
are returned only after persistence succeeds. Rejection leaves prior bytes and
record values intact. The supported OS write/replace failure model preserves the
original destination; this adds no multi-store/distributed/concurrent transaction.

Collection introduction uses explicit adjacent additive migration steps with
typed historical defaults, separately from creation defaults. Steps merge with
the existing scalar migration chain; the declared storage version must match the
complete composed chain. Existing records/IDs, unrelated fields, prior scalar
migrations and explicit authority are preserved. Missing migration authority,
invalid old state and incomplete chains refuse; a current valid store migrates
idempotently. Collection defaults are copied before exposure so record values do
not share mutable default objects.


## Query and lifecycle boundaries

Optional complete existing CollectionQuery groups bind the same model state with
`collection_store:{kind:'composed_scalar',state:STATE_ID}`. String-like collections
project as the existing query `strings` type for membership; compatible scalars
project as `string` for equality. Full store validation precedes the read-only
view; selected results recover whole original records. Query parameter,
comparison, inclusion, ordering, result and read-only effect policies remain
unchanged. Command/state/type/identity conflicts refuse. Independent lifecycle
commands preserve mutable fields and ordinary mutations preserve lifecycle fields.
No OR/NOT/ranges, relationships, joins, aggregates, pagination, durable events,
successor creation or temporal arithmetic are added.
