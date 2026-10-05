# R5.77 — Versioned generic benchmark document contract and adapter qualification

## Result and inherited boundary

**`R5_77_BENCHMARK_DOCUMENT_CONTRACT_V1_QUALIFIED`** within prospective V1
evaluation-infrastructure scope. R5.76's **`R5_76_DOCUMENT_ENVELOPE_GAP`** is
addressed by explicitly specifying a new contract, not by claiming a missing
historical authority existed. One generic adapter and **33/33** qualification
tests pass. Five fresh health-bound lifecycles complete and post-check: supported,
unsupported, malformed, incomplete and a public non-held-out seed-bank example.

B02 remains **`B02_EXPOSED_IN_R5_75` / `B02_STATIC_RESULT_INDETERMINATE`**.
Its historical document layout, incomplete ledger and R5.75 callback are
preserved. B02 protected contents and captured documents are not inspected or
adapted. B03 remains pristine: no content read, layout inspection, conversion,
validation or opening. No actual-benchmark authority is issued. Phase 5C remains
paused. Core semantics remain **30**.

## Prospective design authority

The user-authorized R5.77 establishes
[BenchmarkDocumentContractV1](../../../docs/benchmark-document-contract-v1.md).
The new [machine-readable schema](../../../schema/benchmark-document-contract-v1.schema.json)
governs envelope shape; the versioned prose and adapter additionally govern
component structure, duplicates, ordering, normalization and completeness.
Incompatible revisions require another version, without silent legacy fallback.

Permitted sources independently establish the ingredients:

| Authority | Contribution | Limit |
| --- | --- | --- |
| `benchmark/README.md` and existing oracle protocol | Observable requirements and separate external acceptance | No opened-document role/assembly contract |
| R5.72/R5.74 runner | Exact committed resource set, opening and static-only authority | Does not interpret documents |
| R5.38 readiness and `readiness_r5_41.py` | Explicit boundary obligation list, unknown-kind rejection | No serialized obligation identity policy |
| R5.40 `profile_audit` structure | Closed declarative transport/state/launch configuration | Structural validity is separate from support |
| R5.41 application admission/current pipeline | Application, CheckedPlans, readiness, audit and compatibility arguments | No multi-document envelope normalization |
| Public R5.39 seed-bank study and R5.41 independent measurement study | Non-task applications and grounded configuration examples | Not held-out transfer evidence |

The envelope, two roles, unique obligation IDs, metadata exclusion and singleton
behavioral-owner assembly are **new choices**, selected because existing evidence
does not resolve competing designs. A distributed obligations graph would also
be legitimate, but requires inventories, ownership and merge rules unnecessary
for the existing static consumer interface. V1 chooses the smaller design.

## V1 model, payload and obligation ownership

Four required envelope fields: `schema_version`, `document_id`, `role`, `payload`.
One optional object field: `metadata`. No other fields. JSON duplicate keys,
nonfinite numbers and non-UTF-8 input reject. The two explicit roles are:

1. **`behavioral`** — exactly one document owns the complete contract.
2. **`metadata`** — optional descriptive documents, excluded from behavioral identity
   and all static consumer arguments.

Generation/execution material, private acceptance answers, auxiliary fixtures and
prose requiring interpretation are outside the static package. Independent
packaging authority must enforce that separation; the adapter cannot detect
answers disguised as descriptive metadata. There is no inference or recursive
search of arbitrary dictionaries.

The behavioral payload has exactly `application`, `configuration`, `obligations`.
Application uses existing `id/state/operations`; configuration uses existing
closed `transport/state/launch`. The adapter checks structural profiles without
admitting, supporting or generating the application. Existing consumers retain
semantic validation and support decisions.

An obligation has exactly nonblank `id` and object `requirement`, whose nonblank
`kind` is required. Current known boundary component forms retain their existing
structure (`public_state_alternatives`, `durable_content_constraints`). Unknown
kinds are preserved and reach readiness's fail-closed review requirement, rather
than being discarded or mislabeled malformed solely because they are unsupported.
No new behavioral meaning or B02-specific type is introduced.

IDs are exact, case-sensitive strings. Obligations sort by ID; nested component
arrays keep their order. Duplicate IDs with equal content reject; unequal content
at the same ID is a structured conflict. Logical conflicts across distinct IDs
are not inferred. Explicit `[]` is a declaration of no supplemental boundary
obligations; missing `obligations` is incomplete. Application relations still
exist when the supplemental list is empty. Completeness relative to the original
request requires independent authority review, not merely schema acceptance.

## Multi-document assembly and references

Every opened resource must be a V1 document. Resource names are opaque and do
not select parsing behavior. The runner verifies exact sealed inventory before
dispatch. The adapter validates all documents, sorts by document ID, rejects
duplicate IDs (including identical documents), requires exactly one behavioral
role and permits any number of metadata-role documents. More than one behavioral
document is ambiguous even if both claim equivalent behavior. No supersession or
first/last-wins logic exists. A simple valid package is one behavioral obligations
document; valid multi-document packages add metadata documents.

**References are intentionally omitted** in V1. There are no distributed
fragments, document pointers, target-component addresses, resolver or cycle graph.
Envelope `references` rejects as an undeclared field; a reference-only obligation
is malformed. Therefore reference-resolution, unresolved-reference and cycle
tests are not applicable. Existing component-internal semantic references remain
the consumers' responsibility and are not document links.

## BehavioralContract and generic adapter

The normalized structure is:

```text
BehavioralContractV1 {
  schema_version,
  application,
  configuration: {transport, state, launch},
  obligations: [{id, requirement}, ...] sorted by id,
  identity
}
```

Identity is SHA-256 of canonical UTF-8 JSON of the other four fields: sorted
object keys, compact separators, Unicode unescaped, finite numbers only. V1
uses Python's JSON numeric representation rather than conflating integers and
floats. Document identity includes the complete envelope; behavioral identity
excludes document IDs, envelope metadata and metadata-role payloads. Ordering of
documents and obligations is incidental; ordering inside components is preserved.
No filesystem enumeration, timestamp, host identity or AI interpretation enters
the normalized identity. Canonical round trip and re-enveloping reproduce it.

Exactly one adapter:
`benchmark/evaluation/benchmark_documents_v1.py`.
`from_opened` parses explicit bytes, `assemble` normalizes the whole decoded
set, and `verify_contract` validates the normalized output. These are entry
points to the same generic adapter, not benchmark-specific adapters. It has no
I/O, filename heuristics, support determination, obligation rewriting or AI
dependency. Configuration schema validation delegates to the existing structural
validator, not the support checker.

The qualification callback first obtains a normalized BehavioralContract, then
projects application/configuration and obligation requirements into unchanged
CheckedPlans, readiness, audit, admission and compatibility interfaces. Whole
contract support is the conjunction READY / SUPPORTED / ADMITTED / SUPPORTED.
The callback contains no raw-envelope layout assumptions; its static function
accepts only a verified normalized contract. No static consumer was modified.

## Structured errors

Protocol failure is `DocumentError` with a value-free `{code, path}` record:

| Condition | Code |
| --- | --- |
| Wrong/missing version | `UNSUPPORTED_SCHEMA_VERSION` |
| Unknown role, including acceptance/execution | `UNKNOWN_REQUIRED_ROLE` |
| No behavioral document | `MISSING_REQUIRED_ROLE` |
| Repeated document identity label | `DUPLICATE_DOCUMENT_ID` |
| Invalid JSON/envelope, undeclared reference field | `MALFORMED_DOCUMENT` |
| Wrong set API shape | `MALFORMED_DOCUMENT_SET` |
| Invalid payload/component structure | `MALFORMED_PAYLOAD` |
| Invalid obligation entry/component shape | `MALFORMED_OBLIGATION` |
| Equal repeated obligation ID | `DUPLICATE_OBLIGATION` |
| Unequal content for one obligation ID | `CONFLICTING_OBLIGATIONS` |
| Multiple behavioral owners | `AMBIGUOUS_ASSEMBLY` |
| Missing required payload component | `INCOMPLETE_CONTRACT` |
| Invalid normalized shape or identity | `MALFORMED_CONTRACT` |

No partial static evaluation follows document errors. Downstream unexpected
interface exceptions have a separate `STATIC_INTERFACE_FAILURE` infrastructure
classification; none occurred in qualification. A completed document-failure
observation records the failure, not a support PASS. There is no unresolved-link
error because V1 permits no document references. First-error selection for a
multiply invalid set is not a behavioral identity guarantee.

## Synthetic fixtures and independent tests

`benchmark/evaluation/test_benchmark_documents_v1.py` constructs public measurement
fixtures and independently evaluates the JSON Schema keyword subset actually used
by the checked-in schema. Schema-level validation is deliberately distinct from
additional adapter component/assembly validation. Published valid representations
and normalized contracts are retained beside evidence, not inferred from test results.

**33/33 PASS**, covering all applicable required conditions:

* V1 schema validation and independent schema rejection checks;
* document identity, one-document contract, multi-document metadata assembly;
* deterministic ordering and BehavioralContract identity;
* duplicate document ID, missing role, malformed payload/configuration/obligation;
* unsupported version, conflict and identical duplicate obligation rejection;
* metadata stability, empty explicit obligation set and canonical round trip;
* supported and unsupported full static lifecycles;
* malformed and incomplete lifecycle completion without partial static calls;
* public non-held-out seed-bank adaptation and full pipeline;
* arbitrary filename invariance (including synthetic B02/B03 names);
* separate denied-access controls on fake B02 and B03 files;
* deterministic offline extraction with standard-library imports only;
* unknown role, ambiguous assembly, strict JSON and no support calls in adapter;
* unknown obligation retained and rejected by readiness, not dropped.

Reference resolution/unresolved-reference tests are intentionally not applicable;
the unsupported reference-field rejection is tested. All real protected access
attempt counters are zero. Fake denied-read witnesses use temporary synthetic
files, never protected repository contents.

Development runs passed 32 and then 33 tests as independent schema coverage was
added. A UTF-8-only parser check was added before fresh qualification; the final
fresh evidence run passes 33. No development test failure, failed observation,
completed-ledger replay or evidence repair occurred.

## Full pipelines and non-held-out representation

`r5_77_qualification.py` runs fresh generic health, seals exact fake packages,
freezes state/health, opens once and dispatches once per disposable ledger:

`sealed package → opening → V1 validation → generic adapter → BehavioralContract`
`→ CheckedPlans → readiness → audit → admission → compatibility`
`→ whole-contract result → completion → post-check`.

Each lifecycle records:
`AUTHORIZED → OPENING_RESERVED → OPENING_CONSUMED → DISPATCHED → COMPLETED`.

| Evidence | Outcome | Static views | Completion/post-check |
| --- | --- | --- | --- |
| [supported.json](R5_77-evidence/supported.json) | `STATIC_SUPPORTED` | CheckedPlan `store`; READY/SUPPORTED/ADMITTED/SUPPORTED | 1/PASS |
| [unsupported.json](R5_77-evidence/unsupported.json) | `STATIC_UNSUPPORTED` | Known optional nullable Boolean/text boundary gap; NOT_READY/UNSUPPORTED/REJECTED/UNSUPPORTED | 1/PASS |
| [malformed.json](R5_77-evidence/malformed.json) | `DOCUMENT_FAILURE`, malformed JSON | No static evaluation | 1/PASS |
| [incomplete.json](R5_77-evidence/incomplete.json) | `DOCUMENT_FAILURE`, missing obligations | No static evaluation | 1/PASS |
| [public-seed-bank.json](R5_77-evidence/public-seed-bank.json) | `STATIC_SUPPORTED` | Seven CheckedPlans; READY/SUPPORTED/ADMITTED/SUPPORTED | 1/PASS |

The non-held-out real example is the **existing public R5.39 seed-bank boundary
study**, not a newly invented measurement fixture or B02-derived application.
Its application has two durable versions, creation/query/ordered-read operations
and migration. A prospective V1 wrapper uses its existing application and
configuration, with explicit obligations covering its public routes and declared
durable constraints. The public study is a permitted non-held-out evaluation
example; this is not a claim about frozen B01 acceptance or a first-exposure
benchmark. No historical study evidence is rewritten.
The same adapter/static/lifecycle path succeeds; the real-example representation
is [public-seed-bank-representation.json](R5_77-evidence/public-seed-bank-representation.json).
The runner's mode is `SYNTHETIC_TEST` because this is adapter validation using
already-public material, not a new actual held-out observation.

## Future held-out packaging

The V1 specification requires independent trusted pre-exposure packaging:

1. An authority outside Lykoi development prepares/validates the V1 package and
   independently reviews full obligation coverage and static-role separation.
2. Commit/seal immutable V1 bytes and exact static resource inventory before
   exposure. Commit generation/execution/acceptance material separately.
3. Publish only version, inventory/roles, commitments, provenance and packaging
   attestation to development. No contents or content-derived hints are supplied.
4. Freeze adapter/consumers/health/state against commitments; separately authorize
   opening only after prospective prerequisites qualify.
5. Open once, deterministically assemble, observe once, complete/post-check, stop.
   Errors cannot justify silent reinterpretation or post-opening first-exposure retry.

If B03 needs historical-to-V1 conversion, that independent authority performs it
without feeding contents to development and records conversion provenance before
sealing. **This process is defined, not performed or attested for B03.** No B03
contents or layout are used to design V1, and R5.77 grants no B03 exposure.
Future B02 conversion can only be separately authorized post-exposure diagnostics;
it cannot retroactively make R5.75 a V1 experiment.

## Simplicity and health verification

| Metric | V1 |
| --- | --- |
| Document roles | **2** |
| Required envelope fields | **4** |
| Optional envelope fields | **1** |
| Document references | **None** |
| Adapter modules | **1** |
| Normalized structure | Version + application + configuration + obligations + identity |
| Semantic count | **30**, unchanged |

No document language, graph resolver or runner authority stack is added.
Health workers retain their original CurrentState binding; an enclosing state
additionally pins the V1 specification/schema/adapter/tests/driver. Immediate
checks enforce both scopes rather than falsely claiming workers hash the new
adapter. Canonical evidence publication and a read-only audit link the results.

| Required check | Result |
| --- | --- |
| Runner | **74/74 PASS** |
| Document contract | **33/33 PASS** |
| Compiler/application | **31/31 PASS** |
| Generic semantic/support | **157/157 PASS**, 36 metadata-only prohibited skips |
| Coherence | **16 profiles / 84 rows PASS** |
| Schema/traceability | PASS; **99/99 profile leaves**, independent V1 schema checks |
| Contamination | Clean generic support; adapter has no benchmark filename behavior |
| Validation/safety | PASS |
| AI independence | Offline/site-disabled core probe PASS; deterministic adapter extraction PASS |
| Safe exclusion | **14 PASS / 36 pre-import prohibited skips** |
| Publication | Canonical sealed evidence PASS; deliberate marked-value rejection PASS |
| State/ledger integrity | Immediate checks PASS; read-only audit verifies **45 evidence files / 122 state members**, zero replay |
| Whitespace | `git diff --check` and new-file whitespace audit **PASS** |

Commands, from repository root with `PYTHONPATH=src`:

```powershell
python -B -S -m benchmark.evaluation.test_benchmark_documents_v1
python -B -S benchmark/results/phase5c/r5_77_qualification.py
python -B -S benchmark/results/phase5c/r5_77_audit.py
git diff --check
```

Evidence: [summary](R5_77-evidence/summary.json), [state](R5_77-evidence/state.json),
[health](R5_77-evidence/health.json), [tests](R5_77-evidence/document-tests.json),
and [read-only audit](R5_77-evidence/audit.json). Audit revalidates document
commitments, normalized identities, state members, completion/result linkage
and publication without static-consumer or observation replay.

## Recommendation and stop

Use V1 only for independently reviewed prospective static packages. This qualifies
the bounded V1 adapter contract, not arbitrary historical layouts, generality,
complete prose interpretation or acceptance behavior. Future incompatible document
needs require an explicitly versioned extension and independent qualification.

The next prerequisite for a pristine benchmark is trusted independent V1 packaging
and a separate owner-authorized exposure protocol. Do not immediately open B03
or reuse B02 as held-out evidence. **R5.77 stops here**, with core **30**, AI
independence intact and Phase 5C paused.
