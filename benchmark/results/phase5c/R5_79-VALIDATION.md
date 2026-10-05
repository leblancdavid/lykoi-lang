# R5.79 — Public/synthetic boundary validation

This record separates conceptual architecture checks from executable V1 checks.
No protected requirement, regression fragment or captured B02 document is used.
It does not attest a production formalizer or automatic consistency solver.

## Synthetic conceptual examples

### A — Exact calculation, no implementation prescription

Human fragments, invented for this round:

* `S-A#1`: “Accept two signed integers and return their sum.”
* `S-A#2`: “Reject non-integer inputs without changing stored data.”

Independent authority resolves integer domain as mathematical signed integers,
inputs as a pair, and the failure category as `INVALID_INPUT`. Approved assumptions:
one request at a time, no externally observable side effect on success either.
These are explicit authority decisions, not defaults inferred from Lykoi support.

Formal obligations (conceptual machine-readable relations):

```json
[
  {"id":"REQ-001","requirement":{"kind":"behavior_relation_v1","when":"both_inputs_integer","output_relation":"result = left + right","effects":"none"}},
  {"id":"REQ-002","requirement":{"kind":"behavior_relation_v1","when":"either_input_not_integer","failure":"INVALID_INPUT","state_relation":"unchanged","effects":"none"}}
]
```

The tokens above have their meaning stipulated by this synthetic example; they
are **not an installed general requirements DSL or readiness-supported kind**.
Provenance maps `S-A#1 → REQ-001`, `S-A#2 → REQ-002`, with source commitment and
the authority's domain/failure decisions retained. No class, function, internal
storage field or Python source is required. A table-driven and an arithmetic
implementation would be judged by the same quantified behavior, not layout.

V1 may carry these requirement objects unchanged as opaque kinds, but that alone
does not specify a complete valid application/configuration or qualify support.
A full approved projection is required. If the application component cannot
represent unbounded arithmetic faithfully, package qualification halts with an
evaluation representation gap; do not bound the integers to make it pass.
This negative case prevents envelope validity from becoming a completeness claim.

### B — Bounded existing V1 projection

Use only the existing synthetic optional-measurement fixture and public R5.39
seed-bank constructor from `test_benchmark_documents_v1.py`. No new interpretation
of historical requirements is asserted. Human-style supplemental requests invented
for this review, with the explicit public component context supplied:

* `S-B#1`: “Cover the declared public routes in this supplied system.”
* `S-B#2`: “Retain the declared durable content constraints for each state version.”

The authority's formalization is exactly:

* `REQ-001`: `public_state_alternatives`, `public` = the supplied transport's
  declared public route list.
* `REQ-002`: `durable_content_constraints`, `requirements` = the supplied state
  alternative names and their declared constraint arrays.

System ID, input/output/state relations and configuration are the **already
explicit public component context**, not invented from those two sentences.
This is a scoped supplementary-obligation example, not proof of whole-request
formalization completeness. Project the approved components verbatim into one
behavioral envelope. Set its obligations to those two `{id, requirement}` entries.
Keep `S-B#1 → REQ-001`, `S-B#2 → REQ-002` in protected provenance or descriptive
metadata; both requirements themselves remain in the behavioral payload.

The adapter's ID rule is independent of spelling: `REQ-001` and `REQ-002` survive
just as the existing fixture's `public-coverage` and `durable-coverage` do. It sorts
by exact ID and copies requirements unchanged. No implementation source is part
of the envelope. Existing tests corroborate assembly, order, round-trip, metadata
exclusion, schema checks and public/synthetic static paths. They do not qualify
the independence of a fixture constructor (which uses existing checked plans),
or a future formalizer. No such constructor is approved for protected formalization.

### C — Ambiguity before freeze

Invented fragment `S-C#1`: “Reject invalid dates.” Draft issue:

```json
{"id":"AMB-001","status":"AMBIGUOUS_REQUIREMENT","source":"S-C#1","question":"Which format, timezone and calendar validity rules define a valid date?","affected_obligations":["REQ-001"]}
```

The draft cannot be frozen until the independent owner supplies those rules.
Do not choose a format by querying Lykoi or copy a task-manager due-date design.
Retain the resolution as provenance and only then produce precise obligations.

### D — Conflicting requirements

Invented source requires, for the **same** inputs/state, both `result = 0`
(`REQ-010`) and `result = 1` (`REQ-011`), with a single integer output.
The independent reviewer rejects freeze as `CONFLICTING_REQUIREMENTS` because
one observation cannot satisfy both equalities. Different IDs do not hide the
contradiction. This is a conceptual consistency rejection, not an adapter feature.
Separately, executable V1 tests reject differing requirements sharing one ID as
`CONFLICTING_OBLIGATIONS`; identical repeated IDs also reject.

## Required-condition accounting

| # | Condition | Evidence and scope |
| --- | --- | --- |
| 1 | Human requirement → formal obligations | A and scoped B; conceptual independent authority decisions |
| 2 | Formal obligations → V1 | B's explicit payload mapping; A's missing application cannot be silently filled |
| 3 | Deterministic adapter → BehavioralContractV1 | Existing executable assembly/round-trip/order tests |
| 4 | IDs survive normalization | V1 `normalize_payload` retains exact IDs; executable ordering tests corroborate |
| 5 | No implementation details required | A has only behavioral relations; B supplies declared components, no generated source |
| 6 | Ambiguity representable before freeze | C issue record and mandatory authority resolution |
| 7 | Conflicts rejected | D conceptual cross-ID rejection; executable same-ID V1 rejection |
| 8 | Provenance retained | A/B fragment maps; committed authority record survives separately from normalized contract |
| 9 | No provider/model in meaning | A/B contain none; metadata changes do not change V1 behavioral identity |
| 10 | B03 untouched | Scoped public reads and guarded existing suite; no actual issuer/opener/evaluator invoked for B03 |

Provenance is intentionally **not** claimed to survive inside BehavioralContractV1:
the adapter excludes metadata. Retain a separately committed mapping so audit
and acceptance can follow obligation identity after normalization.

## Executable corroboration

Command from repository root:

```powershell
python -B -S -m benchmark.evaluation.test_benchmark_documents_v1
git diff --check
```

The existing module's entry point activates protected exclusions before its suite.
Its fake protected-file tests use temporary synthetic content; they do not open
real B02/B03 resources. Synthetic static consumers/ledgers are bounded V1 interface
checks, not actual observations. No general harness discovery is needed.

Executed result: **33/33 PASS**, zero failures/errors and **zero protected read
attempts**. Whitespace verification passes. The ten rows above are conceptual/
interface coverage, not “10 passing formalizer tests.”
