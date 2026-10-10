# R6.42 — Prospective provenance contract qualification

**Final classification: `R6_42_PROVENANCE_PARTIAL`.**

The compact composition and independently specified exact expansion agree on all
tested execution observations, including returned Cells, raw errors, order and
logical charges. The flat counterpart has the same required functional behavior
at default budgets, with prospectively expected span, offset, node and work
differences. Existing maps support bounded definition/local/call-path attribution.

**Full qualification fails because the frozen independent oracle incorrectly
expects numeric UInt8 Cells to retain raw-byte origin tuples.** The unchanged VM
returns empty tuples after numeric decoding. All frozen public envelopes and work
expectations pass, but intermediate trace expectations fail. The oracle, first
attempt, discrepancies and classification are retained; no repair or rerun occurred.
This is an expectation defect, not evidence of a new executable semantic gap.

## 1. Authorization, baseline and exact identities

The owner authorized one bounded, model-free, unscored prospective experiment
following R6.41. Initial Git status was clean; baseline HEAD was
`b4d6b4a89a143b2a939bd82f966c67523bfb7f06`.
[Baseline](r6_42/BASELINE.json) verifies **4,987 protected identities**, including
R6.3–R6.41 historical evidence, production, VM, wrapper, adapter, contracts and
registry. R6.40's acceptance artifacts remain byte-identical and are not rescored.

| Publication | Verified files | Manifest SHA256 |
| --- | ---: | --- |
| R6.32 |1,262 | `a0f29c93798157330926dc1d133275f73fefab626b4b8cac7a2fcbe23ed653ee` |
| R6.40 |701 | `8a55ba36776fbefd802e4a00952a58d2f0d73945cc44519317126805038b296e` |
| R6.41 |14 | `a95452414e4a62ae0edf67d3575c529c3916dc4c00fa2d7ff73c37ce166cf89c` |

All three publication receipts bind their manifests and report passing integrity.
Exact implementation identities are in the baseline and the supplemental
[implementation index](r6_42/IMPLEMENTATION-IDENTITIES.json). Key unchanged sources:

| Implementation | Raw SHA256 |
| --- | --- |
| R6.10 `interpreter.py` | `bf5dbfb96d6d50124d109c35804c81e5a27bf4038b7f65b1a909ad4f0cc13fa3` |
| R6.18 `composition.py` | `e5e57901d4df32bcb2eed3b5bbd7ce6f19ee3145bbf71303d96e15b4e3d67fab` |
| R6.18 `SEMANTICS-1.md` | `2165203625c67dc6b5df13eb622e7b5f47e1bafafa53af854021a78d451184b7` |
| R6.32 `lifecycle.py` | `43fa9cf90292180033c815a92e97a4c30591c6f7bd460ff70a7a7ec11f61c9cc` |

Production kernel **26** is preserved accounting, supported by unchanged production
hashes and R5.114 `final_count=26`; this is not a new independent construct recount.
Production/compiler/lowerer/runtime, R6.10, R6.18, R6.23, R6.25 and R6.32 are
unchanged. All experiment writes are additive R6.42 files.

## 2. Prospective contract and pre-execution freeze

[CONTRACT-1](../../../experiments/provenance_r6_42/CONTRACT-1.md) adopts current
executable seq boundaries and returned spans, raw stages/offsets and real logical
work. Symbolic definition pin, local node and ordered expansion path are separate
sidecar coordinates. It explicitly declines to equate flat raw offsets/work or
work-budget outcomes. Functional comparison is a separately declared projection;
the raw envelopes remain available intact.

[FREEZE.json](r6_42/FREEZE.json) binds the contract, preparation/execution/oracle
sources, three forms, independent expectations, map and correspondence, control
payloads, baseline and representation manifest **before candidate execution**.
The exact plan and expected map were hand-constructed from the specified behavior,
using only declared pins for naming; they were not obtained from the expander.
The expected charge schedule never executes candidate plans or inspects their bodies.
Expectation independence is specification-derived and pre-execution, not human
review, cognitive independence or blind design: the same coordinator knew R6.41.

### Behavior

Read two UInt8 values x/y; end-check precedes all computation. Guarded(x) checks
x<=3 at x (`INNER`), computes x+1 and returns it. Nested(x) invokes Guarded(x).
Entry invokes Nested(x) as left, then Nested(y) as right; checks 3<=left at left
(`POST_LOW`), then left+right<=6 at right (`POST_HIGH`), computes/returns their sum
and emits UInt16BE. Conflicting failures remain absorbing in this exact order.

| Form | Frozen canonical identity |
| --- | --- |
| Compact package | `6191aefa032b81032c2efceb3ebbfd3039e75caeecf18752e5e38d5c08b0e661` |
| Independent exact plan | `85ff3750358e93ee99ee9557cb829dda0315e52832b92d44d3c048837e260ba9` |
| Flat plan | `27982121fff4f9293ab61ef93672fe221fc52331537d71656f05dff6f0825f66` |

[Representation manifest](r6_42/REPRESENTATION-MANIFEST.json) additionally records
raw file hashes and the Guarded/Nested/Entry definition pins. Compact lowering is
canonically identical to the independently frozen exact plan: **16 executable
nodes**, including root plus four zero-byte nested seq regions. Flat has **12
nodes**, retaining the root but removing those four intermediate region boundaries
and result-ref charges. These are existing operations, not new execution primitives.

## 3. Frozen acceptance and bounded execution results

[EXPECTATIONS.json](r6_42/EXPECTATIONS.json) specifies exact typed public results,
errors, sites, stages, offsets, returned Cell spans/origins, entry/return order and
charge schedules. [CORRESPONDENCE.json](r6_42/CORRESPONDENCE.json) independently
specifies node pairs, definition/local origins and nested/repeated call paths.

Domain: **36 unique pairs**, x/y in0..5, plus empty input, one-byte `02` and trailing
`020100`: **39 inputs**. Two default-budget passes produce **234 form observations**
and **78 paired comparisons** each for compact/exact and compact/flat. Every form
also runs every numerical work budget0 through its frozen full work+1 for every
input: **3,307 cutoff observations** (compact1,169; exact1,169; flat969).

| Requirement / check | Recorded result |
| --- | --- |
| Compact/exact full default envelope, Cell trace and charge trace |78/78 paired agreements |
| Compact/exact cutoff observations at identical budget |1,169/1,169 agreements |
| Flat externally required default functional behavior |78/78 paired agreements |
| Default observations against frozen public envelope/work/order |234/234 |
| Cutoff observations against frozen public envelope/work/check-entry order |3,307/3,307 |
| Entire default observations against frozen oracle, including intermediate origins |6/234 |
| Cutoff trace digests against frozen oracle |468/3,307 |
| Invalid identity / unsupported provenance controls |10/10 expected rejections |
| Positive definition/path and flat-node comparison claims |28/28 supported |

Instrumentation records raw node entry/return and every attempted charge, then
compares each instrumented envelope with uninstrumented public `execute`; all
agree. Default second-pass data are identical. The cutoff agreement check also
compares full partial traces for compact/exact, not just error code or work.
Checks listed at entry do not assert predicate evaluation completed before a cutoff.

Per form/per default pass: **5 successes**,20 INNER failures (12 first,8 second),
8 POST_LOW,3 POST_HIGH,2 TRUNCATED and1 TRAILING. Successful values are exact Int64
and UInt16BE bytes. The root returns span[0,2) and empty arithmetic origins.
No partial values or bytes are published by rejection envelopes.

## 4. Preserved first-attempt discrepancy

[Discrepancy analysis](r6_42/DISCREPANCY-ANALYSIS.json) records **3,067 failed oracle
comparisons**:228 default and2,839 cutoff comparisons. Default envelopes, work,
spans, node identities, order and charge records agree; the default trace contains
**450 differing numeric-origin list lengths** across the two passes/three forms.
Trace digests also differ because they include those fields.

The oracle's atom schedule supplies origins `[0]`/`[1]`. The VM initially creates a
raw byte Cell with byte origins, but `decode` returns `Cell(v,x.start,x.end)` at
interpreter.py lines348–354, so the numeric Cell has its dataclass default `()`.
The origin expectation was a coordinator derivation mistake despite the explicit
semantic authority. This is not repaired in frozen code, expectation files or scores.
All cutoff envelope/order/work expectations pass; differing cutoff trace commitments
are retained as failures rather than retrospectively waived.

Full qualification requires the independently frozen observation expectations to
pass. Exact twins agreeing with one another cannot overcome this failure. The
classification therefore remains **partial**, even though the measured
representation-aware mechanics show the expected correspondence.

## 5. Error sites, sequence spans and provenance correspondence

| Error / location | Compact = exact raw offset | Flat raw offset | Ordered site |
| --- | ---: | ---: | --- |
| First INNER |0 |0 | left → Nested → Guarded / guard |
| Second INNER |1 |1 | right → Nested → Guarded / guard |
| POST_LOW |2 |0 | Entry / post_low, sites returned left |
| POST_HIGH |2 |1 | Entry / post_high, sites returned right |
| TRUNCATED |actual EOF0/1 |same | x/y atom |
| TRAILING |2 |2 | end before compositions |

The nested Guarded and Nested returns have spans[2,2), because the two bytes were
already consumed. Flat add results instead retain their left operand's spans
[0,1) and[1,2). The eight low plus three high cases therefore produce **11 raw
offset differences per pass**,22 across both passes. All declared guard errors
remain stage `validation`; malformed input errors remain `structure`; budget
errors remain `limit`. Full raw node/offset/stage/error records are retained.

[Actual expansion](r6_42/ACTUAL-EXPANSION.json) matches all **16 independently
expected map entries**. Each entry identifies definition content hash and local
node; nested paths append left/right call-local plus Nested pin, then inner plus
Guarded pin. Repeated calls share definition identity but retain distinct caller
paths and generated bindings. A new R6.42-only registry admits the exact closure;
restart retrieval preserves all three definitions and pins
([registry evidence](r6_42/REGISTRY.json)). No historical registry is updated.

[Provenance evidence](r6_42/PROVENANCE.json) keeps raw error consumers distinct from
producer regions. Entry/post_low has an empty consumer expansion chain and sites
the Cell returned by Entry/left/Nested; the producer path does not become the
error's consumer path. Flat-to-exact node pairs are frozen comparison annotations,
not fabricated flat authorship or executable region membership.

Existing mapping thus supports bounded node/definition/local/call-path attribution
and preserves current raw spans/work. It does not supply authored text coordinates,
expression-occurrence identity or dynamic integer operand lineage. The first
attempt's wrong numeric-origin expectation reinforces that these must not be inferred.

## 6. Actual logical work and budget behavior

[WORK.json](r6_42/WORK.json) retains every input's raw work. All values below were
prospectively derived and agree with actual execution.

| Outcome | Inputs | Compact = exact | Flat | Difference |
| --- | ---: | ---: | ---: | ---: |
| Success |5 |51 |43 |8 |
| First internal failure |12 |15 |13 |2 |
| Second internal failure |8 |27 |21 |6 |
| POST_LOW |8 |37 |29 |8 |
| POST_HIGH |3 |43 |35 |8 |
| Malformed input |3 |same |same |0 |

Each removed seq entry/result costs two logical charges if it completes. The first
internal failure has only two additional region entries; the second includes the
completed first sibling and the second sibling's entries. The work-delta histogram
is0:3 inputs,2:12,6:8,8:16. This is logical VM work, not elapsed time, wrapper
validation effort, host allocation or an AI efficiency measurement.

At input `0201`, budget43 allows flat success(value5, bytes`0005`) but compact/exact
reject WORK_LIMIT during total computation; budget51 allows all three to succeed.
Cutoffs retain the actual raw next-charge node/site. Numeric-conversion cutoffs can
site the original byte after the cursor advanced; later expression cutoffs use the
current cursor. Flat equal-budget outcomes are not asserted equivalent.

## 7. Adversarial controls and verification

Nested/repeated successful calls (`0201`), first conflicting internal failures
(`0404`), second internal failure before a caller low failure (`0004`), post-return
low (`0000`) and high (`0302`) are in the finite domain. All cutoffs through
completion+1 are included for every form/input, including malformed cases.

Ten independently frozen negative payloads reject: returned-span-as-input-origin,
authored-text coordinates, invented integer lineage, wrong sibling nested path,
wrong local origin, missing region origin, incorrect flat node pair, body identity
tampering, call-pin tampering and asserted full flat-envelope equivalence. Positive
controls cover all16 actual map entries and all12 frozen flat node pairs. These
are deterministic R6.42 observation-claim checks; they are not new VM validation
rules or a cryptographic human-authorship attestation.

[Regression records](r6_42/REGRESSIONS.json) retain actual commands/stdout/stderr:
**8 R6.18 methods and14 R6.32 lifecycle/registry methods pass**. Preservation checks
run before/after execution and again at publication. No historical acceptance,
AI authoring, inference or training was run; the experiment's execution is
AI-independent. No P6-A04 acceptance execution or P6-A05 access occurred.

Raw first-result evidence is published losslessly as
[DIFFERENTIAL.json.gz](r6_42/DIFFERENTIAL.json.gz) and
[ADVERSARIAL.json.gz](r6_42/ADVERSARIAL.json.gz). Each decompresses to the exact
original JSON bytes; [archive identities](r6_42/RAW-ARCHIVES.json) bind both raw and
compressed identities/sizes. Local originals are unchanged and Git-ignored to
avoid duplicating94.8MB of repetitive text. Default traces are complete; cutoff
envelopes/order/trace commitments cover all inputs, with complete cutoff traces
retained for eight representative inputs. Every failed oracle comparison also
retains its full actual trace and frozen expectation. This packaging does not
remove, rebase or normalize any execution difference.

[Publication identities](r6_42/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_42/VERIFICATION.json) check manifest hashes, frozen and
protected identities, archive recovery, JSON, whitespace, relative links,
credential-pattern absence, unchanged tracked files and `git diff --check`.
The [first publication-check attempt](r6_42/PUBLICATION-ATTEMPT-1.md) failed because
its implementation index searched the wrong directories for R6.23/R6.25. Only
the unfrozen integrity checker's path selection was corrected; no execution or
acceptance rerun occurred. The failed diagnostic is retained.
The [second check](r6_42/PUBLICATION-ATTEMPT-2.md) incorrectly required a newline on
the canonical JSON registry generation. The checker now validates its exact
canonical bytes; the generation itself remains unchanged.
The [third check](r6_42/PUBLICATION-ATTEMPT-3.md) checked links to its own manifest/
receipt before generating them. Initial publication now defers only those exact
destinations; subsequent read-only verification checks all links after creation.
Versioned [boundary](../../../docs/project-overview-r6.42.md),
[observations](../../../docs/research-log-r6.42.md) and
[decision](../../../docs/decisions-r6.42.md) preserve historical shared guidance.

## 8. Limits, next architectural experiment and stop

This is one small branch-free behavior and39 inputs, not a proof over all UInt8
pairs, all Int64 values, overflow/encode domains, depth/output limits, arbitrary
compositions or universal equivalence. Cutoff observations are repeated inputs
under changed budgets. Registry hashes prove exact content/pins, not behavioral
equivalence across revisions. The sidecar does not reconstruct authored text,
integer input ancestry or independent expression occurrences. The frozen
numeric-origin oracle defect prevents full observation acceptance.

**Recommended separately authorized next experiment:** an observation-only
diagnostic-sidecar qualification that first specifies and checks raw-byte versus
decoded-numeric versus seq-return coordinates directly against unchanged semantic
authority, then freezes new expectations for consumer/producer-region attribution
and explicit unavailable-lineage flags. Retain this failed freeze; use a new round
and independent pre-execution review of the coordinate table. Do not add byte-origin
blame semantics or modify R6.18 returned spans to satisfy it. Rich dynamic arithmetic
lineage would require a separate requirements decision and qualification.

**Stopped after this bounded unscored qualification and publication.** Existing
maps support the tested node-level contract mechanically; complete provenance
qualification remains partial because the frozen origin expectation failed.
Further work requires explicit owner authorization.
