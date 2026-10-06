# R5.102 — executable existing-semantic inventory and orphan analysis

Baseline: immutable R5.101 capability report/matrices/evidence, hashes in
`R5_102-PRE-TRANSFER.json` and `R5_102-VERIFICATION.json`. R5.101 remains the
pre-development **1 success / 16 structural / 1 BDI / 2 clarification** snapshot.

## Reading the inventory

**Legacy model support is not normal-path support.** Before R5.102, scalar WHAT
often occupied opaque/prose-shaped FRC parameters; the closed ordinary structural
mapper did not carry generic fields/migrations/lifecycle. The historical V1
mapper required complete explicit component authority, or the separate public
profile supported only narrow title/default cases. Legacy author fixtures could
compile supplied models; that was not deterministic normal scalar authoring.

The normal profile now uses six closed facets (S storage, F fields, C creation,
L listing, T lifecycle, E evolution). All its supported facets have native
structural rows/coverage, existing BDI/adequacy, whole-FRC V1 recovery, normal
restricted authoring and deterministic v0.3 lowering. The shared layer support
described here applies only to the bounded mappings in the versioned profile,
not every program accepted by the legacy compiler.

| Capability / semantic definition | Existing structural representation | Pre-round FRC / V1 / author seam | R5.102 typed FRC and V1/lowering | Compiler/backend and persistence | Executable verification / remaining edge |
| --- | --- | --- | --- | --- | --- |
| String scalar: exact string input/record value | v0.3 `prim:string`, record field, `input` assignment | Generic field prose not projected; no normal complete scalar V1/author | F + C; faithful whole contract, `input` lowering | Existing `valid_state`, assignments, JSON write/read | New multi-domain external create/reload, whole-record transition preservation; Unicode stdout diagnostic fails in current isolated environment. |
| Identifier: UUID creation, unique stable string identity, existing lookup | String key field, `unique_field`, UUID capability, `lookup` | Backend identity existed but scalar formalizer/structure/profile routing absent | F(identifier) + C(resource), T(lookup); no new relationship semantics | Existing collision check, key uniqueness on load/write, key update refusal | Resource-properties subprocess test, lifecycle missing-ID error, migration identity preservation; external/deterministic supplied ID creation absent in backend. |
| Enum: declared exact finite string domain and membership | `kind:enum`, field/input type references, argparse choices, `IN` invariants | Public default profile narrow; no generic domain/field path | F(domain) + C(default), typed finite expansion against approved base model | Existing finite-domain validation, exact serialized strings; finite expansion updates existing `IN` authority | Library/lab/gallery distinct domains; out-of-domain CLI/store/migration rejection; normal CALIBRATION expansion test. Rank policy is a separate seam. |
| UTC timestamp: valid UTC string, exact supplied representation | `prim:timestamp`; `timestamp_input`, stored timestamp validation | No generic typed field/resource projection | F(timestamp), C(timestamp guard/resource) | Existing UTC validation, raw string assignment, reload | Explicit `.000Z` spelling retained, invalid timestamp rejection; date-only type absent. Clock-relative query mapping remains incomplete. |
| Boolean value: exact JSON bool in query view | CollectionQuery `source.fields:boolean`, typed inclusion/order | R5.99 typed query FRC/V1 already exists | No new writable type claimed; scalar profile refuses boolean | Query runtime validates reads; legacy record validator/CLI has no writable bool | Existing CollectionQuery composition/behavior tests plus new negative writable-type test. Query→write backend edge remains an orphan/integration boundary requiring a type extension. |
| Integer value: exact JSON int (not bool) in query view | CollectionQuery `integer`, unique integer keys/order | R5.99 typed read-only FRC/V1 exists | Writable scalar profile refuses integer | Existing query record validation/order only; no v0.3 integer input/field | Query tests and negative writable-type test. No inference of range/arithmetic support from storage/view type. |
| Creation default: omitted input gets exact authorized value | `input_default` assignment, optional CLI argument | Narrow priority defaults existed; generic field/trigger/boundary path orphaned | C `{field,source,value,default:{value,trigger,boundary}}`; omitted/creation only | Existing `inputs.get` default; supplied empty string is not omitted | Source reference/class defaults, explicit empty reference, enum supplied/default contrast; arbitrary optional-guard composition still incomplete. |
| Verbatim versus comparison normalization | Raw input assignment; query independent `none`/`strip`, case policies | Generic verbatim field addition absent; query comparison path already integrated | F(preservation:verbatim); transformations refuse; normal query contract retains comparison | Existing assignments do not trim; validation inspection does not rewrite | Whitespace preserved through create/reload/migration/transition/delete; gallery equality query distinguishes spaces/case. No trim/write transformation added. |
| Optional presence and timestamp-only null | Optional argument + input-default; `nullable:true` only timestamps | No generic scalar default/presence projection | C distinguishes none-default from null-valued omission default; F existing timestamp nullability | Omitted versus supplied at assignment boundary; no stored presence bit; timestamp API null exists, CLI text null is invalid | Null omitted review, supplied timestamp, optional string supplied empty; no general string/enum null or arbitrary presence predicates. |
| Simple validation/rejection | `nonblank_input`, `timestamp_input`, enums; required CLI flags; `record_exists` | Prose generic validation not mapped | C explicit guard/error; T missing/source-state guards | Existing conditions before mutation; invalid stored records fail; argparse required/enum refusal preserved | New blank/time/enum and migration-invalid cases preserve bytes; existing compiler/reference tests; additional guards on base-model amendments remain unsupported. |
| Lifecycle source→target, repeat rejection | State-machine/transition, `performs`, source equality guard and assignments | Compiler/runtime existed, no generic normal FRC/V1/lowering | T maps bounded declared transition to existing machine/guard | Existing runtime checks source, changes only lifecycle field, writes whole record | Three domains advance/reload/repeat/missing; existing model retains transition; no arbitrary composition or terminal guards across arbitrary commands yet. |
| Declared clock/ID resources and least authority | `utc_clock`, `uuid_v4`, `requires`, explicit dependencies/effects | Compiler had grants; formalizer/structure/profile route absent | C explicitly names resource kind; lower derives exact grants/effects | Existing providers execute at creation; least-authority validator unchanged | UUID-v4 uniqueness and UTC timestamp property checks; compiler authority/effect tests; fixed clock exists for legacy list API only, not deterministic create/ID normal execution. |
| Additive field migration / enum-domain evolution | Adjacent versioned migrations `add_fields`, literal values; model enum edits | Historical plans/models executable, but no ordinary field/migration author bridge | E explicit historical default/boundary; base-model domain for normal evolution; faithful V1 | Existing explicit migrate, chain checks, current-schema idempotence, atomic replace | New v1→v2, v2→v3 normal base extension and B04 v3→v4; invalid old domain leaves bytes; creation default never grants historical repair. General migration programming absent. |
| Existing persistence: whole-record JSON, explicit reload/restart, no write on read | `json_file`, read/write authorities, schema envelope, existing state invariants | Legacy backend path worked; generic requirement/store dispatch absent | S path/version/atomic/rejection; normal plan resource allowlist derived from declared store | Existing template `read_state`/`write_state`/`os.replace`; no runtime edits | 51 published primary external invocations, process-separated reloads, missing-file preservation, migration/rejected-operation bytes, controller reopen audit identical. No new concurrency/durability or injected OS-crash proof. |
| Existing guards/list filters/deletion outside bounded scalar profile | v0.3 `record_field_equals`, delete, `field_equals`, `field_before_clock`, bounded `all` | Generic normal guard/filter projection missing | Preserved unchanged in base-model extension, but arbitrary new amendments/clock-relative filtering not emitted by scalar facets | Existing legacy behavior and validation executable | Baseline/compiler/application regressions pass; B04 retains list-high/list-overdue/delete. This preservation is not normal-path closure for new guard/filter requirements. |

## Evidence anchors

All executable suites below ran in `R5_102-VERIFICATION.json` (314 tests total).

- `tests/test_compiler.py`: deterministic model generation; invalid literals,
  optional enums, migration chains, transition references/source guards,
  least-authority and effects. Validator/generated-manifest comparison passes.
- `tests/test_application.py`: lifecycle/persistence, rejected-state preservation,
  invariants, priority defaults, two legacy migrations, optional due timestamps,
  fixed-clock scenario and transition scenario. These establish existing support,
  not merely reachable unused code.
- `tests/test_collection_query.py` / `test_collection_query_behavior.py` /
  `test_query_normal_path.py`: existing typed read-only scalar views, independent
  comparison/inclusion/order policies, normal source-authority path and fail-closed
  unsupported writes/types/operators.
- `tests/test_scalar_normal_path.py` (13 tests): actual Workspace→Pipeline→external
  execution in multiple domains; scalar resources/null/default/verbatim behavior;
  additive existing-model evolution; finite enum expansion; scalar-store query;
  schema, unsupported types/scopes/transforms, stale/partial coverage, V1 tamper,
  unchanged adequacy omission, reconciliation and owner-approval negative controls.
- `R5_102-SYNTHETIC-EVIDENCE.json`: three retained complete audits, source captures,
  preauthor literal plans, 51 external observations, identical reopen audits and
  separately retained failing Unicode diagnostic.
- `R5_102-TRANSFER-EVIDENCE.json`: frozen exposed B04/B05 external outcomes,
  remaining stage halts and source-authority limitations.

## Orphan classes and closure outcome

1. **Backend→formalizer/structure/V1/author orphan:** strings, enums, raw defaults,
   optional timestamps, identity, single guarded lifecycle, declared create
   resources and additive migrations. The bounded scalar profile closes these
   edges on tested compositions.
2. **Read-only type→writable backend orphan:** boolean/integer query-view fields.
   Their executable read support does not establish existing write semantics.
   R5.102 leaves the edge explicit and rejects unsupported writes.
3. **Existing model operation→new normal requirement orphan:** arbitrary guarded
   update/delete amendments and clock-relative list projection. Preservation is
   demonstrated; generic emission/coverage/profile composition remains incomplete.
4. **Existing provider→deterministic normal creation-resource testing:** explicit
   resource authority is integrated, but injectable creation clock/ID providers
   are not an existing normal backend feature. No deterministic-provider claim.
5. **Typed profiles→general composition orphan:** scalar mutation and CollectionQuery
   work as separate normal contracts, including querying a prior normal scalar
   model; one mixed contract does not have a complete faithful composition adapter.

These material seams require the partial classification. No unused symbol, JSON
field name, manual historical artifact or successful validator result alone is
counted as executable support or end-to-end closure.
