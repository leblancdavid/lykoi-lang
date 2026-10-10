# R6.43 — Provenance sidecar qualification and benchmark readiness

**Final classification: `R6_43_PROVENANCE_QUALIFIED_BENCHMARK_PARTIAL`.**

The bounded successor coordinate expectations pass on unchanged saved representations.
The metadata-only sidecar preserves raw executable observations, including
representation-dependent offsets and logical work. A bounded production-backed
stateful modification comparison is feasible in principle. The adaptive symbolic
wrapper does not support stateful application behavior, and independently reviewed
realistic acceptance plus complete workflow-cost measurement remain outstanding.
This establishes no Lykoi superiority.

## 1. Authorization and preservation

Owner authorized one nonproduction, AI-free provenance qualification and a static
practical benchmark-readiness assessment, with no AI authoring comparison. Initial
Git status was clean. [Baseline](r6_43/BASELINE.json) verifies **5,031 protected
SHA256 identities**, inherited R6.3–R6.42 evidence, R6.32/R6.40–R6.42 publication
manifests and receipt bindings, and R6.42 raw originals/archive identities.
[Preservation details](r6_43/PRESERVATION.md) identify protected implementations.

Production kernel remains **26**, by unchanged accounting and implementation hashes,
not a new independent construct recount. Production compiler/lowerer/runtime,
R6.10 VM, R6.18 wrapper, R6.23 adapter, R6.25 contracts, R6.32 registry semantics
and existing provenance maps are unchanged. No registry is written. Saved compact,
exact and flat forms are read directly from R6.42 and hash-bound in the new freeze.

R6.40/R6.41 historical verdicts and **R6.42's original frozen expectations and
failures remain intact**. R6.42 is not rescored. No P6-A04 acceptance or P6-A05
content access occurred. No model authoring, inference/preflight or training was
performed by this experiment; the coordinating coding agent authored the experiment
and documentation, whose session usage is not metered as a comparison.

## 2. Observation contract and prospective review

[OBSERVATION-1](../../../experiments/provenance_r6_43/OBSERVATION-1.md) distinguishes:

| Category | Qualified witness meaning |
| --- | --- |
| Raw-byte origin | Before numeric decode, original byte Cell span[0,1)/[1,2) and origins[0]/[1]. |
| Decoded-numeric origin | Same span, empty origins tuple, labeled AVAILABLE_EMPTY. Empty does not mean input-independent. |
| Sequence-return span | Region entry/end, four nested returns[2,2), root[0,2); not operand ancestry. |
| Symbolic origin | Existing definition/local identity and ordered call path, separate from raw VM coordinates. |

Integer add results retain the existing left-operand span and empty origins. Flat
left/right values retain[0,1)/[1,2). Output spans remain output-buffer coordinates.
Authored text coordinates, independent expression-occurrence identity, dynamic
integer operand lineage and runtime producer chains are explicitly UNAVAILABLE.
Static caller-site annotations do not supply general dynamic ancestry.

[Preparation](../../../experiments/provenance_r6_43/prepare.py) creates new expectations
from specified behavior and unchanged semantic authority without importing the VM,
expander or old oracle, or reading historical actual-output data. It does not take
the R6.42 candidate's observed tuple as its expectation authority. The documentation
and frozen implementation independently specify the omitted numeric origin argument.

[Separate static review](../../../experiments/provenance_r6_43/review.py) checks
Cell's default tuple and UInt decode constructor by AST, raw-atom and seq constructor
rules, declared definition/local paths,16 map entries,16/12 exact/flat node counts,
and six manually derived outcome/work anchors. All39 expectation rows are reviewed
for coordinate consistency. [Review receipt](r6_43/PREEXECUTION-REVIEW.json) precedes
[FREEZE](r6_43/FREEZE.json), which records zero candidate executions before freeze
and binds sources, contract, expectations, review, baseline and saved forms/maps.

**Independence limit:** this is candidate-output-independent specification derivation
and a separately implemented mechanical review, not independent human/cognitive
review, blind qualification or independent replication. The same coordinator knew
R6.40–R6.42 findings. No external reviewer attestation is supplied. The provenance
qualification claim is bounded technical qualification under that disclosed review
standard; an independently human-reviewed expectation claim remains unavailable.

## 3. Minimal sidecar and executable transparency

[sidecar.py](../../../experiments/provenance_r6_43/sidecar.py) imports no execution
machinery. Given an existing raw observation and mappings, it copies coordinate
fields, labels availability, records raw event indices and a complete raw-record
SHA256 commitment. It neither predicts results nor decides acceptance. Charge
records stay in raw evidence; labels do not replace them. Missing map entries remain
unavailable. Flat pairing is explicitly a comparison annotation, not authorship.

[run.py](../../../experiments/provenance_r6_43/run.py) separately instruments existing
Machine methods, forwarding every call to the unchanged superclass. Hooks observe
numeric decode input/output, node entry/return and attempted charges. Every
instrumented envelope is compared with ordinary public execute. Each sidecar call
is checked against a pre-label deep copy and raw digest. Raw errors are retained,
and consumer path remains distinct from the producer region.

The sidecar has no path into VM execution or acceptance. Experiment expectations
are a separate observer qualification checker; they are not an alternative VM or
an application execution oracle.

## 4. Bounded successor results

Domain:36 pairs x/y in0..5, plus empty, one-byte02 and trailing020100: **39 unique
inputs**. Two default passes cover234 form observations. Four selected work budgets
0/13/43/51 cover468 additional form observations. Cutoffs repeat these inputs;
they are not468 new cases. Two further adversarial budget-witness observations are
recorded separately. All execution uses unchanged saved representations.

| Check | Result |
| --- | ---: |
| Default observations against new frozen results/work/errors/all returned Cells/raw and decoded origins |234/234 |
| Compact/exact identical raw default traces and envelopes |78/78 pairs |
| Compact/exact identical raw selected-cutoff traces and envelopes |156/156 pairs |
| Flat default functional projection |78/78 pairs |
| Qualification instrumented versus ordinary public execution |702/702 |
| Sidecar pre/post raw-record identity and commitments |702/702 |
| Raw decode inputs / numeric decode returns, default passes |450 /450 |
| Observed seq returns, default passes |350 |
| Declared expansion map entries |16/16 |
| Adversarial coordinate/availability controls |14/14 expected rejections |
| Qualification failures |0 |

Default second-pass evidence digests match. Each form/default pass has5 successes,
20 INNER failures,8 POST_LOW,3 POST_HIGH,2 TRUNCATED and1 TRAILING. These outcome
categories derive from the frozen contract; no new historical scoring follows.

Compact/exact POST_LOW/POST_HIGH offset2 differs from flat0/1 in11 cases/pass:
**22 preserved raw offset differences**. Default work for success is51 versus43;
first INNER15 versus13; second INNER27 versus21; POST_LOW37 versus29; POST_HIGH43
versus35. Errors/stages/raw nodes remain intact. At0201/budget43, flat succeeds
while compact rejects WORK_LIMIT. Neither equal-budget flat equivalence nor
representation-normalized offsets are asserted.

**Cutoff ceiling:** selected-budget checks qualify transparency and exact-twin
correspondence. They do not use an independently derived complete cutoff trace
oracle or repeat R6.42's exhaustive numerical cutoff sweep. The full default
Cell expectations are independently frozen from semantic authority. Qualification
is not a proof over all bytes, signed64 values, depths, codecs or compositions.

## 5. Adversarial evidence

[ADVERSARIAL](r6_43/ADVERSARIAL.json) preserves coordinate claims and actual verdicts:
numeric origins incorrectly set to[0]; raw-byte origins incorrectly emptied;
nested returned span replaced by operand span; compact low/high offsets normalized
to0/1; flat offset normalized to2; wrong repeated-sibling expansion path; producer
path used as consumer path; four invented unavailable coordinates/lineages; missing
map guessed from node ID; and full flat-envelope equivalence.

These are observation-claim controls, not new execution validation rules. Candidate
plans are not changed to obtain passing results. The two budget-witness calls also
match their ordinary public envelopes; they are outside the702 qualification count.

Complete raw observations and labels are published losslessly as
[QUALIFICATION.json.gz](r6_43/QUALIFICATION.json.gz); [archive identity](r6_43/RAW-ARCHIVE.json)
binds exact compressed/original bytes and sizes. Local raw JSON remains unchanged
and ignored to avoid duplicate publication. [RESULT](r6_43/RESULT.json) records
denominators, review limits and zero qualification failures.

## 6. Realistic benchmark and measurement readiness

[Capability inventory](r6_43/BENCHMARK-CAPABILITIES.md) finds production support for
persistent state, interdependent record-local operations, shared typed invariants,
multiple operation callers, same-store installs, external subprocess acceptance,
regression retention and AI-independent execution. R6.16/R6.32 supply bounded
mechanics; no fresh realistic application acceptance is run here.

The R6.18/R6.32 symbolic path is stateless arithmetic/check composition. Immutable
definition-registry persistence does not implement mutable application state. A
stateful adaptive-symbolic study therefore exceeds its current envelope. Production
has broader bounded reference/atomic/migration profiles, but the simple R6.16
adapter does not expose every such profile. General callbacks, arbitrary external
effects, distributed transactions, authentication and arbitrary schema migration
remain outside these established capabilities.

[Measurement assessment](r6_43/MEASUREMENT-READINESS.md): external correctness and
modification-regression observation are supported. Visible completions, exported
input/output/cache fields, participant wall and tool intervals are partially
measurable using existing records. Hidden retries, effective provider settings,
exact retrieval-token attribution, actual billing and complete coordinator/setup/
review/export/publication effort are unavailable or incomplete. Missing values must
remain null, and nested intervals must not be double counted. No telemetry platform
was implemented or model route invoked in this round.

**Smallest next proposal:** [one existing production-backed kiln-style application,
two tracks, one in-place shared-policy change](r6_43/NEXT-EXPERIMENT.md). Compare
direct Python with declarative production-backed Lykoi. Independently freeze the
policy/error/invariant and old-store treatment, baseline acceptance, two dependent
operation changes, retained callers/regressions, restart and rejection-byte cases.
This is technically feasible bounded exposed-development research, pending actual
independent acceptance review and separate authorization. It is not an initiated
comparison or an adaptive-symbol advantage test.

## 7. Publication integrity and stop

[Publication manifest](r6_43/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_43/VERIFICATION.json) verify protected/frozen/publication
hashes, exact archive recovery, JSON, relative links, new-file whitespace, credential
patterns, additive-only scope and git diff --check. No executable source or tracked
historical file changes. Versioned [boundary](../../../docs/project-overview-r6.43.md),
[observations](../../../docs/research-log-r6.43.md) and
[decision](../../../docs/decisions-r6.43.md) retain prior shared guidance.

**Stopped after bounded qualification and publication.** Remaining provenance limits
are explicitly unavailable authored-text/dynamic lineage and unattested independent
cognitive review. Practical benchmark readiness and complete economic measurement
remain partial. Await explicit authorization before any new review, authoring,
application modification, replay or experiment.
