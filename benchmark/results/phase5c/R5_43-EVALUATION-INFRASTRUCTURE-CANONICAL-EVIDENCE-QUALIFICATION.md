# R5.43 — Evaluation Infrastructure Canonical-Evidence Qualification

Primary classification: **`R5_43_EVALUATION_INFRASTRUCTURE_QUALIFIED`**.

The prospective canonical comparator and locked recorder are independently
qualified within the documented local, controlled-recorder trust boundary.
**No B02 exposure occurred.** This is infrastructure qualification, not a B02
static support, readiness, audit, admission or acceptance result.

## Inherited state and exact failure

R5.42 permanently remains **`R5_42_PROTOCOL_HALT`**. Its pre-pass stopped before
any B02 observation. At `r5_42_review.py:99`, a fresh independent matrix was
compared to JSON-loaded evidence with native Python `!=`. Analyzer tuple-origin
arrays reload as lists; this caused a false mismatch despite identical canonical
JSON. Its post-pass verification code has the same representation dependency.
Neither historical entry was edited, invoked again, or retroactively repaired.
Its halt report, diagnostic artifacts and attempted recorder remain byte-identical.

Inherited state: 678 historical / 695 prospective lock members; 14 R5.41 focused
tests; 16 coherent profiles / 84 value-state rows; 364 harness passes and 36
prohibited-B02 skips; 31 application/compiler passes; core semantics 30. R5.42
provided no B02 support finding and no semantic/profile gap finding.
Initial `git status --short` was empty.

## Evidence model and serialization boundary

The prospective [versioned protocol](../../../docs/canonical-evidence-r5.43.md)
was written before qualification. Protocol identity means the same finite JSON
data tree, not matching concrete Python object graphs. Its rules are:

| Distinction | Rule |
| --- | --- |
| Object insertion order | Non-semantic; sort string keys |
| Native tuple versus list | Both represent the same ordered protocol array |
| Array order and membership | Preserve; no unordered-array normalization |
| Missing, extra or explicitly null fields | Preserve each distinction |
| Boolean, integer, finite float, string | Distinct scalar types; no coercion |
| Float signed zero | Preserve its canonical spelling |
| Strings | Preserve code points; no Unicode normalization |
| Versions, identities, provenance, classifications | Compare exactly; no migrations |
| Invalid JSON, duplicate keys, non-finite numbers | Reject |
| Sets, custom runtime objects, non-string keys, cycles | Reject rather than serialize lossily |

Canonical authority is immutable UTF-8 JSON bytes: sorted keys, ASCII escapes,
compact separators and finite numbers only. Persistence appends one LF; identity
and equality use the canonical bytes without that LF. SHA-256 covers these bytes,
never `repr`, object addresses or native hashes. Integers retain integer spelling
and floats retain float spelling, preventing both `True == 1` and `1 == 1.0`
Python equality collisions from weakening evidence comparison. This is a local
versioned canonical protocol, not a claim of cross-language RFC 8785 conformance.

Lifecycle: evidence → validated detached tree → canonical bytes → exclusive
persist → strict reload → canonical bytes → compare. Successful serialization
alone is not a passing evidence comparison. The round-trip property is explicitly
tested, including deep mappings/sequences, tuple/list mixtures, strings, integers,
booleans, null, empty collections, optional fields, profile IDs and nested records.

## Implementation correction and authority compatibility

- `benchmark/evaluation/recorder_r5_43.py`: production canonicalization, strict
  loading, persistence, immutable baseline, protected-file lock, verification,
  exclusive pass reservation, observation receipts, halt and final-stop records.
- `benchmark/harness/test_canonical_evidence_r5_43.py`: **29** independent tests.
- `r5_43_qualification.py`: restriction-aware regression and independent matrix
  compatibility checks, production-path simulations and final integrity capture.

The correction is separately versioned because the failed R5.42 apparatus is
historical evidence. It is generic JSON-model canonicalization, not a special
tuple-to-list equality exception. No compiler, semantic runtime, application,
profile, schema vocabulary or historical verifier was modified. Core remains 30.

Read-only R5.41 matrix compatibility was checked twice. Fresh native equality
remains **false**, while the new canonical comparator, canonical round-trip and
deterministic recomputation all pass. New and historical canonical SHA-256 agree:

`02e3c3723a74d16458114760c0c917afbc7597e3ad76c62553014a475471513c`

No evidence migration is required. Historical locks retain their original
canonical hash algorithms, identities and pre-commit HEADs. Verification checks
recorded-HEAD ancestry plus exact pinned bytes rather than rewriting authority.

## Independent regression, adversarial and immutability results

The exact R5.42 failure class is reproduced on synthetic mineral-profile evidence:
freeze through production persistence, reload list-origin data, establish raw
Python inequality, establish canonical equivalence and successfully record
production verification. No B02 data is used in this regression.

All **29/29** qualification tests pass on the initial focused execution, two
recorded focused executions and full restricted discovery. Coverage includes:

1. Tuple-origin/list-loaded and recursively nested equivalence.
2. Round-trip stability and mapping-order independence.
3. Meaningful sequence order and member mutation rejection.
4. Supported→unsupported, missing-field and extra-field rejection.
5. Deep nested mutation, null/absence and version mismatch rejection.
6. String/integer, integer/float, signed-zero and Unicode distinctions.
7. Boolean/numeric collision protection, including nested records.
8. Truncation, duplicate keys, trailing garbage, malformed arrays, invalid UTF-8,
   non-finite constants and numeric overflow rejection.
9. Lossy runtime inputs and cycles rejected before persistence.
10. Ten identical canonical serializations/digests of equivalent evidence.
11. Working-object and reloaded-object mutations leave baseline bytes/digest intact.
12. Successful lifecycle and pre-pass/post-observation mismatch halts.
13. Second dispatch rejection, multiple receipt detection, incomplete callback halt.
14. Protected-byte mutation, observation receipt corruption and pre-pass receipt
    corruption detected; baseline/final replacement rejected.

These negative cases show that the false-negative repair does not make genuinely
different evidence compare equal. No field-dropping or scalar-stringification
shortcut is used. Immutable byte authority and independent reload detach the
baseline from mutable working objects and observation return values.

## Production recorder lifecycle and locked simulations

Persisted simulations are under `R5_43-simulations/`; `R5_43-qualification.json`
also captures their complete baseline, lock, verification, reservation,
observation, halt and final records. Each uses the production recorder with its
implementation and protocol files protected. No simplified testing comparator
or prospective benchmark evaluator is substituted.

| Simulation | Callback count | Final status | Completed observation evidence |
| --- | ---: | --- | --- |
| Equivalent evidence: freeze→verify→observe→record→check→stop | 1 | STOP | one, occurred=true |
| Intentional pre-pass mismatch | 0 | HALT | zero, occurred=false |
| Intentional post-observation nested mismatch | 1 | HALT | one, occurred=true |
| Second unauthorized observation attempt | 1 | HALT | one; second callback prevented |

Mismatch records stage and reason, preserves the baseline and forbids repair or
retry. Tests additionally create two independent linked receipts and require
`multiple` with count 2 and HALT. Observation evidence corruption is classified
as corrupt rather than silently normalized. All successful simulation lock
checks pass; expected mutation failures occur only in disposable adversarial tests.

## Observation-count enforcement and explicit limitations

An exclusive durable reservation precedes callback dispatch. A completed receipt
has a protocol version, integer pass number, reservation digest, evidence and
canonical receipt identity. A second reservation/dispatch is refused. Zero and
one completed observations are independently demonstrated; multiple receipts are
detectable and prohibit successful finalization. A final artifact distinguishes
pre-pass failure from failure after a completed observation and records whether
that observation occurred.

A callback exception or interruption after reservation can leave actual exposure
uncertain. The recorder reports **indeterminate**, `observation_occurred=null`,
HALT and no retry; it does not mislabel this as zero exposures. This is tested.
Completed local controlled runs supply the required zero/one/multiple discipline.
They do not establish exactly-once completion across power/process failure,
hostile filesystem rewrites or evaluator calls outside the authorized recorder.
These explicit local trust boundaries do not authorize ignoring an incomplete
receipt: such a future run must halt and be independently investigated.

## Regression, integrity and contamination verification

Executed:

```powershell
python -m unittest discover -s benchmark/harness -p test_canonical_evidence_r5_43.py -v
python benchmark/results/phase5c/r5_43_qualification.py qualify
python benchmark/results/phase5c/r5_43_qualification.py final-integrity
```

The qualification driver records exact child suite/command output and explicit
skip identities. Plain unrestricted harness discovery was not used.

| Check | Result |
| --- | --- |
| New focused qualification | 29/29, repeated twice in recorded qualification |
| Restricted harness | **429 discovered / 393 passed / 36 prohibited-B02 skips** |
| Application/compiler | **31/31** |
| R5.41 focused tests | **14/14** |
| Independent value-state matrix | **16 coherent profiles / 84 rows**, twice |
| Independent readiness/audit/admission coherence | All 16 profiles agree |
| Canonical matrix stability/round trip | Pass; historical canonical hash retained |
| Model validation / safety | Exit 0 / exit 0 |
| Independent profile structural schema | Valid |
| Independent source traceability | Valid, current independent profile |
| Profile and implementation contamination | Clean |
| Historical lock | **678/678**, identity and ancestry valid |
| R5.41 prospective baseline | **695/695**, identity and ancestry valid |
| New infrastructure lock | **731/731**, no mismatches |
| R5.42 halted artifacts and recorder | Preserved within new 731-member byte lock |
| `git diff --check` | Pass; final results in `R5_43-final-integrity.json` |

New infrastructure lock identity:
`5ded5ebc2a9412883a9796026fec8cd7d9477fa163e05012ac6a3a10a2254242`.
It pins existing authority plus the new infrastructure, tests, protocol and driver
before qualification. Only R5.43 output artifacts and the three requested project
documents are excluded from that lock. Final integrity separately inventories
the report, qualification and simulation artifact hashes.

Structural/source checks use the independent non-B02 profile. Historical sealed
B02 configuration remains protected by hashes; it is not fed to the evaluator,
readiness, audit or admission machinery. The inherited 821-leaf traceability
observation is historical, not a newly evaluated B02 support claim.
LF→CRLF advisory warnings, if emitted by the final diff check for updated project
documents, are captured separately in command stderr; they are not test failures.

## End state and next gate

- **Zero B02 static passes, generation, execution and frozen acceptance.**
- No B02 readiness/audit/admission results produced or used.
- No B02 test of the repaired recorder; no B02 feedback loop.
- R5.42 remains permanently `R5_42_PROTOCOL_HALT`.
- No post-observation semantic/profile/application repair; core semantics **30**.
- B03 prospectively untouched; B17 unexposed/unclassified; Phase 5C paused.

The sole primary classification is
**`R5_43_EVALUATION_INFRASTRUCTURE_QUALIFIED`**.
Recommend a **newly authorized locked whole-contract static support-transfer
evaluation** using this qualified infrastructure. That would be a new experiment,
not continuation/retry of R5.42. It was not started in R5.43. Qualification of the
apparatus does not establish B02 support or semantic generality.
