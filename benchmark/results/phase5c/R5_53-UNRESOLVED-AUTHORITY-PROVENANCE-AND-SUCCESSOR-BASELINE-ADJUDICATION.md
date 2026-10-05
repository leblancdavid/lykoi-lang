# R5.53 — Unresolved authority provenance and successor-baseline adjudication

## Outcome

**All eight current versions are independently traceable and explicitly authorized
for prospective succession. None of their historical physical preimages was
recovered.** The missing bytes are acknowledged, not invented or normalized into
historical PASS. None of these eight is frozen behavioral authority. Important
compiler/type/profile/evaluator content receives stronger, content-bound review.

The separately versioned **1,083-member** successor
`R5_53-authority-successor-v1.json` qualifies as an authority starting baseline.
Its trusted canonical identity is:

`5dd2e7e645c1736f23a80bff755d347da5688cc9e8b7f7df515bd7110d1534ea`

R5.54 may perform a fresh production Tier-2 qualification against that starting
baseline after separate authorization. R5.53 performs **no production Tier-2
qualification**, issues no production certificate, and exposes no B02 subject.

## Inherited state and research boundary

Initial Git status was clean; HEAD is
`0c0cd6d1c5c0a71380c9234658f852aa8bf363d5` (`r5.52`). R5.52 remains
`R5_52_CONTENT_PROVENANCE_GAP`; R5.51 remains its original certificate gap.
Its **81 receipts, 59 PASS / 22 FAIL / zero INCOMPLETE**, remain historical.

| Inherited physical lock | Exact raw matches | Proven ending-only | Content-different | Unclassified historically |
| --- | ---: | ---: | ---: | ---: |
| Historical R5.40 | 145/678 | 524 | 1 | 8 |
| Prospective R5.41 | 145/695 | 541 | 1 | 8 |
| R5.47 successor | 145/1,065 | 911 | 1 | 8 |

Of the original 18 residual differences, nine inverse CRLF→LF cases remain
proven representation-only, and the README remains the documented R5.50
methodology addition. The eight physical preimages remain unavailable. R5.53
changes their **prospective provenance disposition**, not their historical
physical comparison classification. No protected source was restored or edited.

## A–D. Actual sources searched; exact recovery

`R5_53-evidence/investigation.json` contains complete per-file history, raw current
and repository SHA-256, Git blob/index identity, historical pins, lock membership,
first lock carrier, report identity, lock-HEAD context and existing copy witnesses.

Fresh legitimate local search:

- **67 reachable commits**, **8 distinct reflog commits**, **67 combined commits**;
  no reflog-only commit absent from reachable history.
- **2,676 local Git objects, 2,166 actual blobs raw-hashed**, using all-object
  enumeration rather than only reachable path history. No exact target digest
  occurs anywhere in those blobs. Git fsck passes, with no unreachable objects.
- Current staging/index entries are recorded; no recoverable staged historical
  preimage exists outside the searched object set. Git has no persistent sequence
  of previous index contents to attest.
- **37 tracked project tar archives**: enumerate member names and hash only
  relevant candidate members. None contains a target path. No unrelated archive
  contents or B02 contract content are displayed or reconstructed.
- Preserved R5.37/R5.38/R5.39/R5.40/R5.41/R5.43/R5.47 lock records and earlier
  result/report artifacts are checked for target pin/path context. A lock's hash
  is an identity reference, not a file preimage.
- Four existing project diagnostic copies: `r531-lf`, `r532-lf`,
  `r551-cooperative-workspace`, `r552-clean-lf`. Their target bytes are hashed
  directly. Their separate Git databases have **zero additional blobs** outside
  the main searched object set (1,091 / 1,110 / 2,676 / 2,676 objects).
- Existing `r532-new.patch` and `r532-tracked.patch` backups are inventoried.
  The former names the input-binding test; the latter contains R5.32 matrix patch
  fragments. Neither is a complete missing preimage. No patch is applied or used
  to synthesize historical bytes.

This exhausts available local project objects, archives and identified preserved
copies. Unavailable external backups, deleted staging states and unfetched remote
objects are not attested. No external unrelated source, credential/configuration,
prompt history, hash guessing, newline reconstruction or content synthesis was
used for these eight. R5.52's already failed reconstruction hypotheses remain
historical diagnostics, not newly accepted authority evidence.

**Exact historical recovery: 0/8.** Each historical status is
`HISTORICAL_PREIMAGE_UNAVAILABLE`. Similarity and normalized equality do not
qualify as `HISTORICAL_PREIMAGE_RECOVERED`.

## E–H. Required per-file adjudication

All eight belong to the historical 678, prospective 695 and R5.47 1,065-member
locks. The additional first known lock carrying each exact pin is identified
below. All seven `.py` files are authored UTF-8 experimental infrastructure;
the JSON matrix is UTF-8 generated capability evidence. Full current raw-byte
identities are in `investigation.json`; exact authorized **repository** identities
are in [the versioned decision](../../../docs/authority-successor-r5.53.md).

| File | Role | Historical SHA-256 | Preimage recovered? | Current provenance | Behavioral criticality | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| `benchmark/results/phase5c/R5_24-type-matrix.json` | Capability/profile matrix | `eb54bbfeb9cf9be77851ac553dcabe54fd5ba446ca1b03f92a90911969e8ca3f` | No; unavailable | Last content R5.35 `a27ff032`; report §28; first pin carrier R5.38 `4dc980f2`; preserved current copies; content-bound decision | `GENERATED_EVIDENCE`; consumed readiness/profile information | `CURRENT_STATE_PROVEN_AUTHORIZED` |
| `benchmark/semantic/current_pipeline.py` | Current checked application assembly | `27a83b7e86c45d787822b5dd28670dd6f46fac2223d1f2ef79d9985169c56350` | No; unavailable | Last content R5.33 `c46a3e38`; report boundary inventory and cross-shape assembly; first pin carrier R5.37 `d77f7ad0`; copies; decision | `COMPILER_RUNTIME` | `CURRENT_STATE_PROVEN_AUTHORIZED` |
| `benchmark/semantic/input_binding_r5_32.py` | Public typed decoder | `d74e5de623112ad41b300adaba016970a3326464d3da0f90c45757e760e33665` | No; unavailable | Last content and first pin carrier R5.39 `bdb10e95`; report §§9–11 nullable decoding; copies; decision | `PROFILE_SUPPORT` | `CURRENT_STATE_PROVEN_AUTHORIZED` |
| `benchmark/semantic/public_binding_r5_32.py` | Checked metadata and independent binding oracle | `5d0816fafd233b88ea52b343752cee93ebd693e15f3fd499dafca79293db4270` | No; unavailable | Last content and first pin carrier R5.39 `bdb10e95`; report §§9–12 descriptor/oracle integration; copies; decision | `PROFILE_SUPPORT` | `CURRENT_STATE_PROVEN_AUTHORIZED` |
| `benchmark/semantic/refined_evidence_r5_28.py` | Semantic conformance verifier | `d77e9231dfd9a25f861bce9ae1cf814660c9a20c19a2d1ce01ec4a12e4b224fd` | No; unavailable | Last content R5.33 `c46a3e38`; report side-qualified state/frame verification; first pin carrier R5.37 `d77f7ad0`; copies; decision | `BENCHMARK_INFRASTRUCTURE` | `CURRENT_STATE_PROVEN_AUTHORIZED` |
| `benchmark/semantic/refined_generator_r5_28.py` | Checked lowering/emission | `f78822bf31b179de67d5c7fb4deca78072d979633fceccbc48355f3606e7f7ec` | No; unavailable | Last content and first pin carrier R5.38 `4dc980f2`; report §§15–16 checked non-null consumer scheduling; copies; decision | `COMPILER_RUNTIME` | `CURRENT_STATE_PROVEN_AUTHORIZED` |
| `benchmark/semantic/refined_runtime_r5_28.py` | Generated application persistence/runtime | `897960b8cfe0e1c045edffda23c108a8c758c41ef74377d6a3e24ca80b816c47` | No; unavailable | Last content R5.33 `c46a3e38`; report per-operation pre/post codecs; first pin carrier R5.37 `d77f7ad0`; copies; decision | `COMPILER_RUNTIME` | `CURRENT_STATE_PROVEN_AUTHORIZED` |
| `benchmark/semantic/unified_types_r5_27.py` | Authoritative current type analyzer/CheckedPlan | `2065a68971236b282fd4d66aefe6501f9204fbe1efc1cc70f8fed2bb49efae38` | No; unavailable | Last content and first pin carrier R5.39 `bdb10e95`; report §§1–8 canonical equivalent-provider correction; copies; decision | `SEMANTIC_CORE` experimental analyzer | `CURRENT_STATE_PROVEN_AUTHORIZED` |

### Current-state provenance versus physical lock context

Full Git histories establish the initial introductions and evolution: current
pipeline R5.29; analyzer R5.27; emitter/verifier/runtime R5.28; public binding
R5.32; matrix first committed R5.25 under its historical R5.24 filename. No later
versioned content change follows each last change listed above. The introducing
reports describe the changes, and the exact current blobs occur in the first
commits carrying the corresponding lock pins. Later result artifacts and the
R5.51 byte-copy/R5.52 LF-copy corroborate preservation of current logical content.
Those copies are not independent authorship or recovered historical authority.

Four first-lock **HEAD** fields name the preceding commit: R5.38's generator and
R5.39's decoder, public binding and analyzer. Those old HEAD blobs differ, as
expected when a physical snapshot includes that round's uncommitted changes.
The independent audit verifies the **carrier commit**, both its exact current
implementation and the lock member pin in the same tree, and records the older
HEAD identities and ancestry separately. It does not substitute HEAD bytes for
the missing physical preimage. This corrects an overly strong preliminary audit
assertion; the failed development observation is preserved. No baseline or
historical record changed to obtain the final independent PASS.

### Semantic and behavioral impact

None of the eight is treated as harmless merely because it was a lock member:

- The analyzer can change typing, checked dependencies and semantic admission.
- Assembly and lowering can change generated behavior and registered state codecs.
- Runtime can change persistence, durable validity and observable application behavior.
- Decoder/metadata can change profile acceptance, suppliedness, nullable conversion
  and independent binding conformance.
- The verifier can change experimental acceptance/conformance judgments.
- The matrix can influence readiness/profile capability metadata. It does not
  redefine frozen requirements or the external oracle.

The historical unknown differences have **indeterminate impact**: their preimages
are unavailable. We do not claim a no-impact old→new comparison. For the current
versions, exact Git evolution plus recorded round purpose and explicit current
authorization supply the stronger evidence required by their criticality.
R5.53 itself changes no model, semantic construct, compiler, runtime, profile,
external oracle or application implementation. Current source versus its working
representation remains covered by R5.52's preserved evidence and fresh integrity.

## G, I–K. Frozen authority, historical failures and harness interpretation

The eight are current experimental infrastructure/evidence, not the frozen
Phase 5 behavioral contract/compiler/runtime/schema. The four inherited frozen
pins are freshly matched against **exact raw Git repository bytes**, without
subject parsing or evaluation. Their original SHA-256 values remain in the
successor. Strong frozen identities are never replaced by a generic change record.
There is no unresolved frozen behavioral authority and no observed unauthorized
versioned semantic/compiler/profile mutation.

Two statements remain separate:

1. **Historical:** old physical locks cannot be reproduced on this checkout;
   unavailable preimages are not recovered. Historical physical FAIL remains FAIL.
2. **Prospective:** independently recorded current repository versions may begin
   a new versioned baseline under the explicit R5.53 decision.

Fresh checks prove all 1,065 R5.47 physical members remain identical to R5.52's
recorded active state; corresponding older members are unchanged. The **911**
proven ending-only findings are retained, not reopened. Original raw match counts
remain **145/678**, **145/695**, **145/1,065**. The diagnostic LF checkout's old
lock counts remain historically **661/678**, **678/695**, **1,047/1,065**.

Preserved R5.52 paired harness observations, same implementation HEAD:

- Active checkout: **338 pass / 36 skip / 55 error**, 429 discovered.
- LF diagnostic checkout: **393 pass / 36 skip / zero error**, 429 discovered.
- All 55 errors correspond to seven raw-byte integrity gates. Changing checkout
  materialization removed them; the active result is not relabeled passing, and
  raw-byte failure alone is not evidence of a semantic regression.

These harness results are **inherited observations**, not freshly rerun R5.53
production gates. Current protected source/physical state preservation is freshly
verified. Full production regression remains R5.54 work.

## L–P. Successor eligibility, construction and qualification

All seven eligibility requirements pass: no unresolved frozen authority, no
observed unauthorized semantic/compiler/profile mutation, exact traceable current
authority, preserved security, retained historical failures, explicit successor
semantics, zero B02 exposure.

The predecessor manifests are retained byte-for-byte and explicitly identified by
path/raw digest in the successor. The new scope has **1,083 members**: all 1,065
predecessor members plus **18 enumerated additions**, including applicable newer
infrastructure/policies and four R5.53 additions. New uncommitted additions have
`blob: null`; they are content-bound published additions, not fabricated Git
history. The later independent auditor and R5.53 reports/results are evidence
outside this baseline, to be bound as appropriate by a future capsule.

`authorized-transitions.json` records **every identity transition**: eight current
authority authorizations, one R5.50 README change, 116 old physical→repository
identity changes, and 18 scope additions. Only 116 require different historical
pin versus repository digest; many of the 911 active ending-only cases already
had LF repository-compatible historical pins. Thus these denominators measure
different relationships and do not contradict R5.52.

Identity semantics, implemented in `benchmark/evaluation/authority_r5_53.py`:

- Exact repository-content SHA-256, path, Git blob and mode determine members.
- Binary/material content and repository text containing CR retain exact bytes.
- Declared UTF-8 LF text permits only exact equality or exact CRLF-pair expansion
  relationship. Bare CR, arbitrary normalization/content mutation and unsupported
  filters/encodings reject. Effective attributes and EOL settings are recorded.
- Checkout representation is a separate receipt, not baseline identity. Active
  receipt: **56 exact / 1,027 permitted LF/CRLF representations**.
- Four frozen original authority identities remain explicit and exact. Historical
  hash-sensitive consumers still require their physical authority representation
  in a future production workspace; this baseline does not bypass their gates.
- Trusted baseline identity is externally pinned; mutated/resealed successors
  reject. Local cooperative provenance is not adversarial signature attestation.

Qualification verifies deterministic reproduction, canonical reload, all member
identities/relationships, exact frozen pins, preserved R5.47 security state,
synthetic mutation rejection, checkout receipt, predecessor preservation and Git
ancestry. A separate auditor independently reads Git blobs/modes and current
bytes, verifies the trusted ID and decision/adjudication links, and checks every
first lock carrier without using the successor build/verify functions.

The baseline is qualified as a **clean authority starting point** for a fresh
R5.54 production experiment. It is not a complete execution capsule, sealed
production workspace, Tier-2 certificate, static observation or B02 authorization.

## Fresh verification and preserved security

Supported interpreter: existing CPython **3.12.10**, with bytecode writes disabled.
Bounded workers use the established restriction-aware dispatcher. Evidence is
published through the R5.47 secret-safe immutable publication boundary.

| Check | Result |
| --- | --- |
| Exact available historical preimages | **0/8**; unavailable explicitly recorded |
| Current adjudication / carrier / criticality | **8/8 authorized**, independent audit PASS |
| R5.53 synthetic tests | Final **18/18 PASS**; preliminary 16/16 retained |
| R5.52 synthetic mechanisms | **22/22 PASS** |
| Compiler/application | **31/31 PASS** |
| R5.50 methodology | **18/18 PASS** |
| R5.51 Tier-2 mechanisms | **43/43 PASS**, synthetic only |
| Full R5.47 security | **20 PASS / 2 preserved historical FAIL** |
| Security correction content | `.gitignore`, publication guard, infrastructure lock match R5.47 repository content |
| Generic coherence / schema / traceability | **16 profiles / 84 rows**, PASS / PASS / **99 leaves** PASS |
| Contamination / dependencies | PASS / PASS |
| Validation / safety / core count | PASS / PASS / **30** |
| Successor independent integrity | **1,083/1,083 PASS**, exact frozen authority **4/4** |
| Historical/prospective/R5.47 physical locks | **FAIL / FAIL / FAIL**, unchanged original counts |
| Historical result integrity | **1,675 files unchanged**; **81 R5.51 receipts** preserved |
| `git diff --check` | PASS |

The two security assertions retain their documented causes: raw working-tree JSON
versus Git blob equality, and this Git version's quiet negated-ignore matching.
They are not repaired or silently counted as passing. Fresh R5.52 effective-ignore
and publication witnesses pass. No security rollback or secret publication occurs.

Synthetic coverage includes all twelve requested areas: actual exact match,
wrong match, normalized-only rejection, authorized successor, unauthorized
mutation, stronger frozen rule, documentation/infrastructure distinction,
deterministic identity, LF/CRLF representation independence, binary exactness,
successor mutation rejection and historical-lock preservation. Additional tests
cover canonical encoding, mode mutation, bare CR, frozen-pin mismatch and unbound
frozen evidence. Real historical bytes are never synthesized for tests.

## Evidence, reproduction and R5.54 recommendation

Drivers: `r5_53_adjudicate.py` (inventory/adjudication/baseline/verification) and
`r5_53_independent_audit.py` (separate read-only verifier). Key artifacts:
`investigation.json`, `supplemental-source-search.json`, `adjudication.json`,
`authorized-transitions.json`, `checkout-controls.json`, `checkout.json`,
`qualification.json`, `independent-audit.json`, focused/static worker records,
`historical-lock-status.json`, `security-preservation.json`, `final-integrity.json`.
The final integrity record binds this report and updated project documentation.
Immutable publication refuses overwrite; replay qualification in an independent
evidence destination. Tests can be rerun without publishing duplicate receipts:

```powershell
$env:PYTHONPATH='src'
& 'C:/Users/lblan/AppData/Local/Temp/opencode/python-r531/python.exe' -B -m unittest discover -s benchmark/evaluation -p test_authority_r5_53.py -v
```

Recommend separately authorized R5.54: bind the successor's trusted identity and
explicit policy, build a dedicated compatible materialization, independently
verify all hash-sensitive frozen inputs, and run fresh complete restricted Tier-2
production gates/capsule checks/security/schema/traceability/contamination with
immediate same-state checks and no historical receipt reuse. Version the future
gate policy to consume the new successor while recording old physical FAILs;
do not modify old verifiers, excuse new unexplained drift or reuse diagnostic
passes as production receipts. R5.54 qualification is not performed here.

**Lykoi is a language, not an AI runtime.** AI credentials/providers/models,
OpenCode configuration and prompt history remain outside language authority.
**The benchmark evaluates required behavior, not generated-code similarity.**
No conventional implementation structure becomes authority through reconciliation.

**B02 exposure: zero. Core semantics: 30. Phase 5C: paused.** No reservation,
dispatch, CheckedPlan, readiness, audit, admission, static support, generation,
execution or frozen acceptance is invoked on B02. Any exposure would require
protocol halt and quarantine. No production certificate is issued.

Primary classification:

**`R5_53_SUCCESSOR_PROVENANCE_QUALIFIED`**
