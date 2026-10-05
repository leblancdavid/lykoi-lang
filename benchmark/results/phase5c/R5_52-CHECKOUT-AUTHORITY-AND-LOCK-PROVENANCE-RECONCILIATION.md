# R5.52 — Checkout, frozen authority and lock-provenance reconciliation

## Outcome

**Production succession stops at eight unrecovered historical physical hashes.**
The checkout conversion, four frozen pins and all 55 inherited harness errors
are explained. Nine of R5.51's 18 residual mismatches are proven line-ending-only;
one is an explicitly authorized R5.50 documentation addition. The remaining
eight cannot honestly be classified as either representation-only or actual
content mutation from the available authority. They remain `UNCLASSIFIED` /
`UNKNOWN`, rather than being accepted from plausible current source or green tests.

R5.52 therefore does not satisfy the successful-reconciliation criteria. No
successor lock, production baseline, production certificate or B02 gate is issued.
The content-provenance stop applies before any reconciliation or succession.
It does **not** establish that an unauthorized semantic or frozen-authority
mutation occurred. Historical byte checks still fail on the active checkout.

## Inherited state and preserved evidence

Initial `git status --short` was empty, HEAD
`e13e881d43b8b5516f2e7114f27b37459bef5035` (`r5.51`). R5.51 remains
`R5_51_TIER2_CERTIFICATE_GAP`: 81 stages, **59 PASS / 22 FAIL / 0 INCOMPLETE**;
43 synthetic Tier-2 tests and exactly one authorized completed synthetic
observation followed by verification and stop. Its 59 PASS stages are not
production qualification. Its failed receipts, diagnostics, materialization and
final-integrity record were not edited, repaired, overwritten or reinterpreted.

The final R5.52 integrity check compares **1,469 historical result files** with
the initial physical snapshot, all **1,065** initial successor-member checkout
hashes, three R5.51 mechanism hashes with its recorded capsule, and all **81**
sealed receipt identities with its summary. This verifies preservation on this
checkout, not retroactive equality with an earlier host's physical publication.

## Evidence and reproducibility

- `R5_52-inventory-v3.json`: final independent member inventory, full expected and
  current SHA-256 identities, repository SHA-256 / Git blob / index identities,
  exact-pin recovery references, authority/current newline counts, per-path
  attributes, normalized equality, original lock identity and ancestry checks.
- `R5_52-inventory.json` and `R5_52-inventory-v2.json`: retained preliminary
  inventories. Additional mixed-ending reconstruction attempts in v2/v3 did not
  resolve the eight unknowns or change any counts.
- `R5_52-evidence/provenance.json`: all 18 dispositions, complete file histories,
  repeated historical pin occurrences, available materialization checks and
  inherited/fresh failure IDs and trace tails.
- `R5_52-evidence/failure-causes.json`: seven error groups, equality of all 55
  fresh/inherited error IDs (including repeated subtests), and raw-pin witnesses.
- `R5_52-evidence/materialization.json`: independent LF checkout, raw lock
  comparison, four raw frozen pins, complete Git EOL inventory and selected
  configuration origins.
- `R5_52-evidence/active-test*.json` / `clean-test*.json`: separately persisted,
  restriction-aware per-module results, with complete failure traces.
- `R5_52-evidence/noninterference.json`: 77 current-source AST comparisons and
  security/methodology content comparisons.
- Generic verification worker records and `final-integrity.json`: validation,
  safety, core count, schema, traceability, contamination and preservation.

The read-only inventory driver is `r5_52_reconcile.py`; bounded diagnostics and
integrity checks are in `r5_52_verify.py`. New diagnostic logic and 22 synthetic
tests are in `benchmark/evaluation/checkout_r5_52.py` and
`test_checkout_r5_52.py`. Diagnostics have no production gate or subject dispatcher.
The supported interpreter is the existing CPython **3.12.10** at
`C:\Users\lblan\AppData\Local\Temp\opencode\python-r531\python.exe`.
The ambient launcher still selects unsupported Python 3.9; it was not used for
qualification or harness execution. Git is **2.25.0.windows.1**.

## A–C. Fresh inventory and line-ending provenance

| Manifest | Members | BYTE_IDENTICAL | LINE_ENDING_ONLY | CONTENT_DIFFERENT | UNCLASSIFIED | MISSING |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Historical R5.40 | 678 | 145 | 524 | 1 | 8 | 0 |
| Prospective R5.41 | 695 | 145 | 541 | 1 | 8 | 0 |
| R5.47 infrastructure v2 | 1,065 | 145 | 911 | 1 | 8 | 0 |

There are no unexpected *members*. These protocols protect enumerated paths,
not an exclusive closed-world repository. The inventory separately enumerates
later tracked paths outside each manifest's membership. An extra file in a
future explicitly closed input scope must be `UNEXPECTED`; the synthetic witness
checks that distinction. Later additions are not silently inserted into old locks.

Each proven representation-only row satisfies both:

1. recovered authority SHA-256 equals the original **raw** manifest pin;
2. authority bytes differ from checkout bytes, but normalized text is equal.

Recovery searches all **66** reachable commits (HEAD, all refs and first-parent
counts are identical). It accepts a repository blob or reconstructed LF/CRLF
representation only when its raw digest is exactly the original expected digest.
Mixed-ending hypotheses also require an exact digest and cannot invent content.
Normalization is an in-memory diagnostic: CRLF and standalone CR become LF, with
UTF-8/NUL-free text screening. It is not a production text/binary policy.
Per-path ending forms and counts are retained, including mixed forms. Binary
changes are not accepted by the text comparison in the binary fixtures.

R5.51's diagnostic tested only
`sha256(checkout.replace(CRLF, LF)) == historical_pin`. It correctly found
902 successor mismatches in that direction, but cannot detect the inverse:
a historical CRLF pin and a present LF file. Nine exact reconstructed CRLF pins
account for **902 + 9 = 911** proven representation-only successor mismatches.
The historical/prospective counterparts add eight inverse cases: **516 + 8 =
524**, **533 + 8 = 541**. Thus “18 additional content differences” was a
residual inventory, not proof of 18 non-newline mutations. R5.51's failed results
remain unchanged; this is a new diagnosis.

### Effective Git behavior

There is no tracked `.gitattributes`, no historical `.gitattributes` commit, no
`.git/info/attributes`, and no selected `core.attributesfile` setting. For all
protected paths, `text`, `eol`, `filter` and `working-tree-encoding` are
`unspecified`. System configuration
`C:/Program Files/Git/etc/gitconfig` sets **`core.autocrlf=true`**. No effective
`core.eol` or `core.safecrlf` setting was returned. System/global LFS filter
definitions exist, but no inspected path has a filter attribute selecting them.

Git's clean conversion allows a CRLF working file to compare clean against an LF
index blob. A newly materialized text checkout under `autocrlf=true` normally
expands LF to CRLF; files authored or preserved as LF need not be rewritten merely
because the configuration is enabled. Configuration alone cannot date a specific
file's materialization. The recorded EOL inventory confirms both LF and CRLF
working files, plus the README's mixed representation. Index and HEAD blob
identities agree for every inspected member. A clean status is therefore not
an exact physical-byte attestation.

The exact relationship is **versioned LF content → Git materialized CRLF text**
for the ordinary converted files; unchanged LF working files remain another
valid clean representation. All 1,065 active members match the independent HEAD
materialization either exactly (**47**) or after newline comparison (**1,018**).
No active-versus-current-HEAD logical source mutation is observed. This finding
does not recover the eight unknown historical physical preimages.

## D–E. Historical lock meaning

These are **working-tree-byte locks**, not normalized-text locks:

- `r5_40_review.py:lock/verify_lock` hashes `Path.read_bytes()` and compares raw
  bytes before/after its static pass.
- `r5_41_review.py:historical/lock/lock_check` preserves the R5.40 raw member pins
  and creates/checks another physical snapshot.
- `infrastructure_lock_r5_47.py:manifest/verify` deterministically rehashes physical
  files, including `.gitignore`; the R5.47 report explicitly rejects unknown
  inherited changes and requires explicit future succession.

Their `head` and ancestry fields provide provenance alongside physical files;
they do not make the files map an index/object manifest. Reports of successful
physical qualification in earlier rounds retain their original meaning. There
is no basis for retroactively declaring these exact-byte protocols semantic-text
locks. Normalized comparison here is explanatory evidence, **not a lock PASS**.

R5.31 sections 382–417 and R5.32 sections 344–373 already distinguished the
CRLF authoring workspace from isolated `autocrlf=false` LF test mirrors. They
explicitly preserved physical pins. This history supports investigating checkout
representation, but does not authorize changing old lock semantics or guarantee
that later snapshot hashes are recoverable from canonical repository bytes.

## F–G. Individual dispositions of the 18 residual paths

Full authority/current SHA-256 identities are in the corresponding
`provenance.json.dispositions` row; repository, index and historical recovery
references are retained with them. “Last change” below is the last **versioned
content** change, not an inferred date of newline conversion. All present files
are expected relative to current HEAD. All historical pins remain authoritative
for their own historical locks, including the authorized README successor.

| Path | Role | Last versioned change | Exact mismatch disposition |
| --- | --- | --- | --- |
| `benchmark/README.md` | Benchmark protocol/methodology documentation | R5.50 `cd53c74` | `AUTHORIZED_SUCCESSOR_CHANGE`: eight-line Tier-2 methodology paragraph/link; plus checkout endings. Exact old LF pin recovered. Explicit R5.50 report/decision authorizes methodology documentation, not a frozen behavior rewrite. |
| `benchmark/harness/test_input_binding_r5_32.py` | Evaluator tests | R5.32 `c057438` | `LINE_ENDING_MATERIALIZATION`: pinned CRLF → present LF; no content difference. |
| `benchmark/harness/test_semantic_authority_r5_31.py` | Evaluator tests | R5.31 `ad63d5a` | `LINE_ENDING_MATERIALIZATION`: CRLF → LF. |
| `benchmark/results/phase5c/R5_24-type-matrix.json` | Prospective capability/profile evidence | R5.35 `a27ff03` | `UNKNOWN`: exact physical pin unavailable; same pin already in R5.38. |
| `benchmark/results/phase5c/R5_31-SINGLE-SEMANTIC-AUTHORITY-CONSOLIDATION.md` | Historical research documentation | R5.31 `ad63d5a` | `LINE_ENDING_MATERIALIZATION`: CRLF → LF. |
| `benchmark/results/phase5c/R5_32-INPUT-BINDING-TYPED-FAILURE-BOUNDARY.md` | Historical research documentation | R5.32 `c057438` | `LINE_ENDING_MATERIALIZATION`: CRLF → LF. |
| `benchmark/results/phase5c/R5_32-binding-evidence.json` | Historical synthetic generated evidence | R5.32 `c057438` | `LINE_ENDING_MATERIALIZATION`: CRLF → LF; not a newly expected generated-content change. |
| `benchmark/semantic/binding_study_r5_32.py` | Independent application/research fixture | R5.32 `c057438` | `LINE_ENDING_MATERIALIZATION`: CRLF → LF. |
| `benchmark/semantic/current_pipeline.py` | Current compiler assembly infrastructure | R5.33 `c46a3e3` | `UNKNOWN`: exact pin unavailable; already in R5.37. |
| `benchmark/semantic/input_binding_r5_32.py` | Typed public binding/validation | R5.39 `bdb10e9` | `UNKNOWN`: exact pin unavailable; already in R5.39. |
| `benchmark/semantic/public_adapter_r5_32.py` | Public application adapter | R5.32 `c057438` | `LINE_ENDING_MATERIALIZATION`: CRLF → LF. |
| `benchmark/semantic/public_binding_r5_32.py` | Public profile/binding infrastructure | R5.39 `bdb10e9` | `UNKNOWN`: exact pin unavailable; already in R5.39. |
| `benchmark/semantic/refined_evidence_r5_28.py` | Semantic evidence verifier | R5.33 `c46a3e3` | `UNKNOWN`: exact pin unavailable; already in R5.37. |
| `benchmark/semantic/refined_generator_r5_28.py` | Compiler/lowering infrastructure | R5.38 `4dc980f` | `UNKNOWN`: exact pin unavailable; already in R5.38. |
| `benchmark/semantic/refined_runtime_r5_28.py` | Generated application runtime adapter | R5.33 `c46a3e3` | `UNKNOWN`: exact pin unavailable; already in R5.37. |
| `benchmark/semantic/unified_types_r5_27.py` | Semantic/type validation infrastructure | R5.39 `bdb10e9` | `UNKNOWN`: exact pin unavailable; already in R5.39. |
| `benchmark/semantic/verify_binding_r5_32.py` | Research/evaluator runner | R5.32 `c057438` | `LINE_ENDING_MATERIALIZATION`: CRLF → LF. |
| `docs/input-binding-r5.32.md` | Versioned profile documentation | R5.32 `c057438` | `LINE_ENDING_MATERIALIZATION`: CRLF → LF; successor-only member among these locks. |

For the eight unknowns, all versioned path blobs were tested against their raw
pins, including uniform LF/CRLF forms, prefix/suffix mixed forms, blank-line
forms and bounded incremental-patch reconstructions. Available `r531-lf`,
`r532-lf` and the preserved R5.51 byte-copy were also compared where the paths
exist; their raw/uniform representations do not recover the pins. None is
reported as `UNAUTHORIZED_CHANGE` without evidence of an unauthorized content
mutation. Conversely, documented R5.33/R5.35/R5.38/R5.39 capability work cannot
authorize an unidentified byte difference after those very locks were created.

Possible lost mixed working representation or a snapshot/content discrepancy
remains a hypothesis. A cryptographic digest alone does not disclose its
preimage. No exact old content is available to write an honest content diff for
these eight. They cannot be repaired, restored, normalized or accepted from
current behavior. Obtain the original physical materialization or another
digest-matching authority witness and explicit provenance before succession.

## H. Four frozen physical pins

| Pin | Active diagnosis | Independent LF checkout |
| --- | --- | --- |
| `benchmark/requirements/B01.md` | Exact authoritative LF vs CRLF; normalized equal | Original raw SHA-256 matches |
| `benchmark/requirements/B02.md` | Exact authoritative LF vs CRLF; normalized equal | Original raw SHA-256 matches |
| `benchmark/harness/profiles/B02.json` | Exact authoritative LF vs CRLF; normalized equal | Original raw SHA-256 matches |
| `benchmark/results/phase5c/R5_40-frozen-regression-authority.txt` | Exact authoritative LF vs CRLF; normalized equal | Original raw SHA-256 matches |

These are checkout representation failures, not stale pins, missing paths or
proven frozen-authority content mutations. The saved oracle text's raw LF hash
also identifies the historical Git oracle blob, as already independently
recorded in R5.51. Authority bytes were hashed for integrity; no B02 contract
reconstruction, loader, CheckedPlan, readiness/audit/admission, generation,
execution or frozen acceptance was invoked.

## I. Grouped harness errors

Fresh active run: **429 discovered / 338 pass / 36 preserved skips / 55 errors**.
All error/subtest IDs equal R5.51's inventory. There are **zero assertion failures**.
The 55 errors share checkout materialization as their established cause, with
seven first-reached integrity gates:

| First-reached integrity gate | Error entries | Raw authority witness |
| --- | ---: | --- |
| Archive/requirements manifest mismatch | 25 | All 20 requirement hashes reproduce in LF checkout; active text differs only in endings; binary archive is unchanged. |
| Frozen assertion-preservation transition drift | 16 | R5.2.1 and R5.2.2 carrier source pins reproduce in LF checkout. |
| B15 predecessor hash mismatch | 5 | Both pinned predecessor checkpoint JSON files reproduce. |
| Prospective B16 protocol artifact hash mismatch | 2 | Pinned runner, composer, fragment, requirement and case bytes reproduce. |
| Historical checkpoint hash mismatch | 1 | Historical Phase 5B Lykoi B02 checkpoint bytes reproduce; hash-only checkpoint diagnosis. |
| Pinned Phase 5D continuation mismatch | 3 | Both bridge checkpoint JSON pins reproduce. |
| Replacement audit input drift | 3 | First failing `B04.py` case pin reproduces. |
| **Total** | **55** | |

The paired clean run, using the **same versioned implementation**, discovers
429 and gives **393 pass / 36 identical skips / zero failures/errors**. Both
use the established restriction-aware R5.38 dispatcher, one bounded module
per child; no nested B02 acceptance or prohibited historical B02 diagnostic
execution is admitted. Constructing historical non-B02 carrier/metadata regression
fixtures does not expose a new B02 subject. These are regression diagnostics,
not production qualification or resumed Phase 5C.

Attribution is overlapping: all 55 are raw-byte integrity/checkout errors;
25 hit the requirement-manifest gate that includes the failed B01/B02 pins;
none is caused by invoking the R5.40/R5.41/R5.47 aggregate lock verifier. Thus
the four-pin and three-lock findings are related physical-state evidence, not
55 independent defects. No error remains in the clean representation to
attribute to behavioral regression, stale checkout content or unrelated
runtime failure. This does not prove arbitrary behavior or the eight lost pins.

## J, P–R. Non-interference, clean materialization and security

The separate diagnostic tree is
`C:\Users\lblan\AppData\Local\Temp\opencode\r552-clean-lf`:
shared-object, no-checkout clone; explicit `core.autocrlf=false`, hooks disabled,
detached checkout of `e13e881`. It remains Git-clean. It executes its own current
HEAD sources, not patched old authority. The active tree and R5.51 dedicated
tree were not rematerialized. This is diagnostic evidence, not a sealed
production workspace.

| Historical raw lock | Exact matches in clean LF materialization | Remaining mismatches |
| --- | ---: | --- |
| R5.40 | 661/678 | Eight inverse CRLF pins, README successor, eight unknowns |
| R5.41 | 678/695 | Same 17 |
| R5.47 v2 | 1,047/1,065 | Nine inverse CRLF pins, README successor, eight unknowns |

An LF clone alone **does not pass these physical locks**. The raw frozen pins
and full restricted regression pass there, but that is insufficient to resolve
lock provenance or qualify production.

No core/model/compiler/profile/application implementation was changed. All
**77** current compiler, semantic-module and generated Python sources have equal
ASTs between current repository bytes and active representation. The generic
application/compiler suite passes **31/31** on the active tree; all current
pipeline/profile behavioral regression methods also pass in the paired harness.
The synthetic LF/CRLF executable witness has identical outputs. No genuine
language or application regression is observed within this tested scope. These
findings concern current content versus current materialization, not behavioral
equivalence to unavailable physical authority.

R5.47 `.gitignore`, publication guard and infrastructure-lock implementation
retain the committed security-correction content. R5.50 methodology fixtures
retain their versioned content. Full R5.47 tests still give **20 pass / 2 fail**:

- `test_historical_lock_unchanged` assumes physical JSON bytes equal Git blob
  bytes; active CRLF vs canonical LF explains its failure.
- `test_ignore_effective_behavior` assumes quiet `check-ignore` returning success
  means ignored. This Git version returns success for matched **negated** rules
  too. Verbose rules identify `!.env.example` / `!.env.sample`; independent
  synthetic `ls-files --others --exclude-standard` checks prove the examples
  are unignored while `.env` remains ignored. The protections are intact.

Those historical tests are not changed or silently excluded. The new synthetic
effective-ignore witness checks observable membership rather than that invalid
exit-code assumption. No credentials, AI/provider configuration or authoring
history are needed, loaded as identity inputs or introduced into reconciliation.
Lykoi remains a language, not an AI runtime.

## Verification and required synthetic coverage

| Fresh check | Result |
| --- | --- |
| Lock raw inventory / original identities / ancestry | Raw counts above; all three identities and ancestry checks valid; historical physical locks FAIL |
| Four frozen pins | Active representation-only; clean **4/4 raw matches** |
| Paired restricted harness | Active 338/36/55; clean 393/36/0, 429 discovered each |
| New reconciliation tests | **22/22 PASS**, including final run after diagnostic changes |
| Application/compiler | **31/31 PASS** |
| Full R5.47 security | **20 PASS / 2 preserved historical FAIL**; both diagnosed |
| R5.50 methodology | **18/18 PASS** |
| R5.51 Tier-2 mechanisms | **43/43 PASS**; synthetic integrity only |
| Generic coherence | **16 profiles / 84 rows**, deterministic/reference equality PASS |
| Structural schema / traceability | PASS / **99 leaves** PASS |
| Configuration / implementation contamination | No findings; implementation scan nine established files |
| Resolved dependencies | PASS, no unknown direct external roots |
| Model validation / safety / semantic count | PASS / PASS / **30** |
| Current-source newline non-interference | **77 equal ASTs**; tested behavior above |
| Historical preservation / R5.51 receipts / diff check | Final integrity PASS; `git diff --check` PASS |

The new suite covers all 18 requested areas: raw equality, both LF/CRLF directions,
real text mutation, binary mutation, missing, unexpected and unavailable authority;
real synthetic Git attributes and checkout conversion; repository/physical
distinction; decision-bound successor provenance and unauthorized rejection;
frozen pin diagnosis; clean comparison; executable non-interference; security
succession; historical physical lock preservation; candidate design determinism.
Extra witnesses reject “CRLF present” as proof, require exact recovery, recover a
synthetic mixed pin and check effective ignore exceptions.

Diagnostic development issues were corrected before the final records: an
existing evidence filename correctly rejected overwrite; a wildcard output
filename was invalid on Windows; a guessed methodology module path did not exist.
Preliminary inventories remain, no published record was overwritten, and final
checks use the corrected explicit application label and actual methodology test
path. These were diagnostic-driver issues, not production qualification attempts
or concealed historical test repairs.

## K–O, S. Future identity recommendation and R5.53 boundary

**Historical interpretation is settled; future identity design is conditional.**
R5.50's behavioral claim does not justify treating ordinary LF/CRLF checkout
policy as a Lykoi semantic difference. It also does not authorize overriding
historical exact physical locks. Distinguish, prospectively:

1. `RepositoryContentIdentity`: selected path/mode/versioned blob content,
   including generated artifacts and explicitly authorized successor decisions.
2. `CheckoutMaterializationIdentity`: actual physical digests/membership, effective
   relevant attributes and conversion policy, with pre/post drift equality.
3. Historical frozen physical authority: preserve the exact identity its own
   protocol requires, with separate verified materialization when necessary.

For a future versioned mechanism, binary or explicitly non-text inputs require
exact bytes. Text requires declared text classification, exact repository content
and a proven allowed materialization relationship; normalization alone must not
accept changes to runtime-relevant text or hash-sensitive consumers. Unknown
filters/encodings, missing/unexpected inputs or unexplained content fail closed.
Freeze the policy and authorized transitions before qualification. Preserve the
strongest historically required frozen-authority identity. The synthetic
candidate-identity helper is a deterministic **design witness**, not an issued
successor manifest, authorization validator or production lock implementation.

No production successor is implemented or qualified here, because provenance is
not complete. Blanket LF/CRLF conversion, current-tree manifest regeneration,
restoring older `.gitignore`, formatting or workspace replacement would obscure
the unresolved evidence. The smallest justified action performed is a separate
LF diagnostic checkout and separately versioned evidence. Active configuration
and protected physical files remain unchanged.

R5.53's prerequisite is to resolve the eight unknowns with exact authority
witnesses and documented provenance, then authorize any individual restoration
or successor transition. If that cannot be done, production qualification remains
blocked. Once resolved, the proposed small boundary is:

> Versioned repository content + explicit authorized successor state + exact
> frozen authority + relevant checkout materialization + Tier-2 capsule.

A new round must version that baseline/policy, independently qualify the identity
mechanism, build a clean dedicated materialization, and run **fresh complete
production Tier-2 gates** with correct raw authority, restricted regression,
security, schema/traceability, contamination, core 30, validation/safety and
same-state capsule/certificate receipts. R5.51 and these diagnostic passes cannot
be reused as production qualification. Preserve cooperative before/after drift
checks, no repair/stop and exactly-one accounting. No recursive OS/CRT/AI-state
hermeticity is introduced. B02 still requires separate explicit authorization
after production qualification; neither R5.52 nor this recommendation provides it.

**B02 exposure: zero. Core semantics: 30. Phase 5C: paused.**

Primary classification:

**`R5_52_CONTENT_PROVENANCE_GAP`**
