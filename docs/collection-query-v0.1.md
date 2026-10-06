# Lykoi CollectionQuery-0.1 — prospective R5.98 semantics

This is an implemented **bounded query language/profile**, separately versioned
from the compatibility v0.3 task application. Its semantic source is a typed
`CollectionQuery` JSON document, not generated Python. The normative closed-world
validator is `src/air_compiler/collection_query.py`; deterministic Python lowering
uses its adjacent runtime template. No changes to pinned historical semantics,
compiler/runtime, or canonical task application are implied.

## Compositional structure

A query has `id` and these separately identified facets:

| Facet | Meaning |
| --- | --- |
| `source` | Logical collection, closed record field/type map, scalar unique key. |
| `parameters` | Named runtime strings; lower-case CLI-safe identifiers. |
| `predicate` | Field reference, `equals` on a string or `contains` on a string collection, operand reference `{parameter: name}` or distinguishable `{constant: value}`. |
| `comparison` | Independent `case: sensitive|casefold` and `normalization: none|strip`. |
| `ordering` | Ordered key sequence, each `{field, direction: ASC|DESC}`; first key most significant. Unique identity must occur to resolve ties deterministically. |
| `validation` | Ordered input rules `nonempty` or `nonblank`, each naming a parameter and declared error. Empty rules mean no extra validation, distinct from omission. |
| `inclusion` | Additional record dimensions: `all` explicitly prohibits exclusion on that dimension; `equals` explicitly adds a criterion with a typed value. Empty rules mean selection alone. |
| `effect` | `read_only/unchanged` or distinguishable `mutating/write`. Only the former lowers with this backend. |
| `result` | Whole-record collection, `zero_or_more`; no match is explicitly `empty`, `null`, or `error` with a declared error code. |

Field types are `string`, `integer`, `boolean`, and `strings`. Every stored record
must have exactly those fields and a unique identity. No null, arbitrary expression,
regex, joins, range query, pagination, aggregate, or user code is supported.
Selection preserves records unchanged, once per source record; repeated matching
members do not duplicate a record. All record validation runs before filtering, so
an invalid nonmatching record is not silently ignored.

### Text policies

`sensitive/none` is exact Unicode-codepoint equality, including significant spaces;
it performs no case or Unicode canonical normalization. `casefold` applies Unicode
casefold to **both** operands. `strip` strips leading/trailing Unicode whitespace
from **both** operands before the case policy. Neither implies the other. `nonblank`
inspects whether stripping Unicode whitespace leaves anything, but does not modify
the supplied string. These are declared synthetic-profile choices, not retroactive
interpretations of an exposed benchmark's unspecified Unicode details.

### Effect and state adapter

The standalone generated subprocess takes `--store PATH` and named parameters.
Its storage adapter reads a JSON array; missing storage is an empty collection.
It never creates storage or writes files. Success is one JSON stdout value/exit 0;
declared errors are `{"error":"CODE"}` on stderr/exit 1. Malformed storage is
`invalid_state`. This adapter is separate from the historical versioned task-store
envelope and command dispatcher. CLI parser errors remain argparse errors, outside
the supplied-string application domain.

The read-only contract preserves the caller's input records and returns detached
records. Validation errors, no matches and state errors preserve persisted bytes
and missing-file absence. A mutating frame can be analyzed, but is rejected at
lowering, rather than falsely implemented as read-only.

## FRC projection and coverage

The existing `filter_order` FRC relation has a new **closed prospective semantic
profile**: parameters are exactly `{query, facet, value}`. One obligation supplies
each facet. The operation identity, source vocabulary and benchmark identity have
no applicability role. The legacy free-text relation is not parsed by heuristics.
Formalization into these values remains inspectable human/AI work, not an automatic
prose interpreter or an independently approved source contract.

Every obligation must map. Missing/duplicate facets, extra criteria, unsupported
features, arbitrary prose-only relations, and unsupported component context fail
closed. Coverage reprojects the exact FRC and compares the entire projection;
stale/tampered rows or semantic values cannot establish completeness. No partial
query is reported complete. This is structural fidelity, not proof that a drafted
FRC captured every source obligation.

Each policy facet can be `null` to record **omission**, or `{freedom: [values...]}`
to record explicit finite freedom. Those are representable WHAT structures.
Omission produces missing behavioral authority; freedom supplies unconstrained
authority across the declared finite alternatives. Neither compiles until a
complete implementation policy is supplied; this version does not automatically
choose an implementation from explicit freedom.

## BDI and adequacy

The existing BDI selection family handles matching vs nonmatching. The query
extension adds runtime binding, comparison policy, ordered key sequence,
validation policy, inclusion policy, effect frame and no-match result decisions.
Existing ordering's forward/reverse domain cannot encode key precedence; the
generic normalization rule does not distinguish the independent case/strip axes;
transition/persistence rules do not establish an authoritative read-only frame.
Thus these refinements are justified by the six synthetic compositions and their
near misses, not by any benchmark identifier. Decisions preserve source-obligation
origins and source quotes. Reachability is declared/profile-bounded, not a general
proof that every syntactic policy distinction is observable in every possible state.

The extension uses unchanged BDI sidecar translation and unchanged
`ImplementationAdequacy-0.1.analyze`. Missing material policy authority remains
underspecified; explicit freedom remains adequate; conflicting effect authority
remains conflicting. Adequacy does not imply backend support or production grants.

## V1 analysis and explicit extension

Historical `BenchmarkDocumentContractV1` can store arbitrary opaque operation and
relation dictionaries, but its faithful complete mapper and executable semantic
consumers do not define this query vocabulary. Successful JSON serialization is
not faithful executable support. It is **not sufficient for this path**.

`CollectionQueryDocumentV1` is a separately versioned query-profile extension:
exact FRC, FRC commitment, full typed queries and facet origins. Recovery reprojects
and rejects loss or alteration; compilation recovers the FRC, validates it, reruns
coverage/BDI/adequacy and invokes the closed query backend. It is not claimed to be
a transparently interchangeable historical `BehavioralContractV1` component.

Use `python -m lykoi_query validate CONTRACT.json`, or `compile CONTRACT.json
EXISTING_OUTPUT_DIRECTORY`, with `PYTHONPATH=src`. The public API
`lykoi_query.compiler.compile_document` returns deterministic standalone targets.
Generated code is disposable; no host-language source is accepted in a model.

## Corpus and evidential limits

`src/lykoi_query/corpus.py` declares products/category, users/department,
documents/owner including archives, explicit casefold and strip contrasts, and
documents/labels membership. Compositions combine ordering, errors, result and
read-only/inclusion behavior. Unit tests cover loss, stale projection, unsupported
features, near misses, omission/freedom and effect conflicts. External subprocess
tests use literal expected identities and compare complete records and original
storage bytes/absence. Same-agent requirements/model/oracle authorship is disclosed;
process separation is evidence of execution independence, not cognitive independence.

This bounded implementation does not establish universal natural-language
formalization, universal BDI completeness, integration into the historical task CLI,
or held-out generalization. Later public/exposed transfer records are separate.
