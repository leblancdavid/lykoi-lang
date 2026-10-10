# R6.41 — Symbolic provenance semantics clarification

**Final classification: `R6_41_REQUIREMENT_CLARIFICATION_NEEDED`.**

The two combination failures have an established mechanical cause: a composed
region returns a Cell whose span starts at the region-entry cursor, not at the
input that contributed to its arithmetic value. Both inputs have already been
read, so that cursor is **2**. Later checks report that Cell's start. The frozen
oracle instead expects input-origin offsets **1** (E3) and **0** (E4).

R6.18 explicitly specifies this expanded-sequence behavior. R6.40 freezes exact
oracle offsets, but its task prose does not explicitly define how derived sites
cross composition boundaries. Thus the recorded oracle failures remain failures;
neither a runtime defect nor the correctness of the compact task implementations
against intended requirements is established by equal values. Human clarification
is required before a prospective comparison can choose between these meanings.

## Scope, preservation and evidence strength

The owner authorized a documentation-only investigation. Initial Git status was
clean. [Protocol](r6_41/PROTOCOL.md) and [baseline](r6_41/BASELINE.json) document
read-only inspection. R6.40's **701 publication identities**, receipt/manifest
binding, **4,268 inherited protected identities**, and development/task/vocabulary
freezes (9/24/49 entries) were verified. The R6.32 publication is also checked;
immutable registry pins and submitted dependency closures are retained verbatim.

No VM, wrapper, adapter, registry, scorer or historical acceptance was executed.
Machine-readable records are extracted from existing JSON and compared without
recomputing acceptance. All R6.3–R6.40 historical results and implementations remain
unchanged; kernel26 is inherited accounting backed by preserved hashes, not a new
construct recount. No AI authoring/training, new execution meanings, P6-A04
acceptance checks or P6-A05 access occurred. This is outcome-informed diagnosis,
not independent replication or a new benchmark result.

## Exact failure inventory

[Failure analysis](r6_41/FAILURE-INVENTORY.md) explains the boundaries;
[exact inventory](r6_41/FAILURE-INVENTORY.json) retains every failed recorded row,
its 1-based acceptance-row index, input, expected/actual envelope, node/map entry,
caller chain and corresponding recorded A/X row.

| Task / condition | Final failed observations | Expected → actual offset | Error operation | Recorded failure work |
| --- | ---: | --- | --- | ---: |
| E3 B |46 |1 → 2 |ProxyPair/total check at parameter y = caller v |48 |
| E3 C |46 |1 → 2 |pair_envelope/total_high check at parameter y = caller v |54 |
| E4 B |59 low +29 high |0 → 2 |ProxyInterval/lo or hi check at x = caller t |30 /34 |
| E4 C |59 low +29 high |0 → 2 |interval_fee/low or high check at x = caller t |32 /36 |

Final B/C artifacts have **268 failed observations** across the two tasks. E3-C
also seals the same root twice: its two preserved acceptance files each contain
46 failures. The inventory therefore contains **314 failed submission-row
occurrences**, explicitly distinguishing the repeated E3-C submission from new
cases. A/X recorded final artifacts pass all1,194 observations/task. These are
the historical outcomes; no corrected score is published.

### E3: transformed input values cross two sibling regions

Entry reads x at [0,1), y at [1,2), then checks end. It invokes interval composition
for u=x+4 and v=y+4 at cursor2. Internal interval checks still use the original
argument Cells; those checks' failures retain offsets0/1. Successful region returns
replace u/v spans with [2,2). Entry then invokes pair composition using those Cells.
Its TOTAL_HIGH check explicitly sites parameter y, substituted with caller v.
The reported node is in **sum → pair**, while the changed Cell span originated in
**v → interval**. These are different producer and consumer expansion paths.

Example input `4ca3` (x76,y163): u80,v167, total247 rejects TOTAL_HIGH. B/C offset2;
A/X offset1. C's exact failing operation ends `/sum/<pair pin>/total_high`.
The precise B/C roots, pins, full nodes and substituted check sites are in the
inventory. No FIRST_LOW/SECOND_LOW failure is observed: with the preceding
interval checks successful, u/v>=13. This does not qualify those unexercised
error sites.

### E4: a producer region returns t to a later check region

Entry reads x/y and checks end. Echo composition checks x==77 then y<=189 and
computes t=((x+y)+y)+6. The expression's left operand traces to x at offset0;
the echo region's returned Cell instead has [2,2). Entry passes t to interval
composition. Its low/high checks site x, substituted with that t Cell, so offset2
is deterministic. The failure operation is in **total/out → interval**, not in
the earlier **t → echo** producer region.

For `4d00`, t83: RANGE_LOW at2 instead of0. For `4da1`, t405: RANGE_HIGH at2
instead of0. Within x77,y<=189, low failures are y0..58 (59 selected cases),
high failures are y161..189 (29); all are retained. Earlier echo checks preserve
their input sites. A/X inline the arithmetic without the intermediate seq-return
boundary and report0.

## What differs, and what has not been proved

The existing failed observations agree in status, error code, stage and observed
check precedence, and have no published partial values or output. Successful
observations agree on values, output bytes, consumed input and root provenance.
The failed acceptance predicate differs only in offset; raw node identities also
differ across authored representations. Equal values alone are insufficient.

**Logical work differs.** On the failed E3 rows, A/X work47/49, B48, C54.
On failed E4 low/high rows, A/X work29/33, B30/34, C32/36. Compact expansion adds
ordinary seq entry/result charges; library bodies also differ in value nodes and
expression reuse. R6.40 scores work-limit controls, not exact cross-condition
work equality. [Recorded comparisons](r6_41/FAILURE-INVENTORY.json) include all
1,194-row work-delta histograms for each task/condition against A. They are
record comparisons, not new execution measurements. X is not C's normative
expanded plan: it supplies flat primitive templates and participants author new
roots. E3 X additionally differs from A in primitive structure; E4 A/X share a
root. Exact IDs/work/envelopes cannot be silently declared equivalent.

No full dynamic trace was collected anew. Statically ordered plans and matching
recorded first-error codes support precedence agreement on recorded inputs, not
all Int64 inputs or every work/depth cutoff. Original R6.40 reload evidence remains
historical evidence of reproducibility, not fresh R6.41 execution.

## Provenance contract and authority

[Terminology](r6_41/PROVENANCE-COORDINATES.md) separates executable semantic
origin, symbolic authoring origin, ordered expansion path and input-byte span.
An input offset is not an authored JSON line/column, expression identity or
definition-local step coordinate. The existing `Cell.origins` tuple is primarily
character provenance; empty integer origins are not a complete operand ancestry.

[Authority audit](r6_41/REQUIREMENT-AUTHORITY.md) distinguishes three sources:

1. **Existing semantic authority:** R6.18 SEMANTICS-1 lines25–36,47–60 and88–92
   make the expanded form normative, preserve seq boundaries/work and raw VM IDs,
   and explicitly demonstrate region-return rather than inner-expression spans.
2. **Frozen scoring authority:** R6.40 protocol lines45–49 requires exact sites;
   frozen expectations and tasks.py pin E3 TOTAL_HIGH=1 and E4 RANGE_LOW/HIGH=0.
   These determine the historical score without revealing an independent human
   adjudication of the cross-representation contract.
3. **Task meaning:** “at v” and “at t” identify derived values but do not specify
   input-origin inheritance versus returned-Cell spans. The scorer's comment
   “requirement-defined input-source offset” is the coordinator's interpretation.
   Participant guidance exposes `site` expressions but omits explicit span rules.

There is therefore a material under-specification between task wording and oracle
interpretation, alongside well-specified existing runtime mechanics. Requirement
clarification is the appropriate terminal classification, rather than an assertion
of a new primitive semantic gap or a preferred contract becoming authoritative.

## Alternatives and recommendation

[Contract alternatives](r6_41/ALTERNATIVE-CONTRACTS.md) evaluate all four requested
choices for determinism, compatibility, debugging, equivalence, complexity and
benchmark fairness.

**Recommended prospective contract: C, implemented at the observation/documentation
level using A's unchanged runtime semantics.** Preserve the raw expanded-operation
node, declared check-site Cell offset/span and work; separately retain symbolic
definition/local identity and expansion path in the existing map/package sidecar.
For comparison use D's explicitly frozen, representation-aware node correspondence.
Do not relabel raw offset2 as input-origin0/1. If originating-byte blame is required,
define and qualify that as a distinct requirement before authoring. This is a
recommendation, not an adopted runtime/schema change or an R6.40 score repair.

[Feasibility](r6_41/EXISTING-MECHANISMS.md): existing artifacts support bounded
node/definition/caller attribution and deterministic current error-site reporting.
They lack authored text coordinates, separately identified expression occurrences,
a runtime value-producer chain, and a specified compact-to-flat correspondence.
Node-level C is feasible as separately preserved analysis metadata without new
execution meanings. Full arithmetic input-origin lineage or replacing returned
spans is not currently supplied by that metadata. Registry hashes anchor exact
versions, not semantic equivalence or identity stability across body edits.

## Human clarification and smallest next experiment

The [audit questions](r6_41/REQUIREMENT-AUTHORITY.md#clarification-questions) ask
which coordinate and blame rule applies to derived values, how region boundaries
are treated, which provenance fields are observable, and what equivalence means
for nodes/work/limits. No maintainer or owner intent is inferred.

[Future qualification criteria](r6_41/FUTURE-COMPARISON.md) require identical
functional behavior, explicit provenance expectations, independently frozen rules,
no post-result changes, separate functional/provenance failures and exact disclosure
of work differences. Representation-aware correspondence cannot waive an actual
input-byte requirement. Fully metered discovery/authoring claims additionally
inherit R6.40's control-capacity and independence limitations.

**Smallest justified next experiment, after human clarification and explicit
authorization:** a model-free, unscored three-representation micro-qualification
using unchanged semantics: one compact nested composition, its exact expansion
with seq boundaries, and a separately authored flat comparison. Cover an internal
check, a caller check on the returned value, sibling repeated calls and one nested
call; include success, each ordered failure, conflicting checks and each work
cutoff through completion plus one. Freeze exact spans, node correspondence,
origin sidecars and work expectations independently before execution. Exact
compact/expansion envelopes must match; flat differences must match the explicitly
chosen contract rather than be normalized from outcomes. No R6.40 rerun or new
discovery is necessary for that qualification.

## Publication and stop

[Publication verification](r6_41/VERIFICATION.json) and
[identities](r6_41/PUBLICATION-IDENTITIES.json) bind the additive documents and
data, verify preservation, links/JSON/whitespace and `git diff --check`.
Versioned [boundary](../../../docs/project-overview-r6.41.md),
[log](../../../docs/research-log-r6.41.md) and
[decision](../../../docs/decisions-r6.41.md) preserve the earlier shared guidance.

**Stopped after documentation-only publication.** Human clarification remains
required; further experiments, contract adoption and implementation require explicit
owner authorization.
