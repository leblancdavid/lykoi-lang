# R6.7 — Independent specification reduction audit

**Final classification: `R6_7_INDEPENDENCE_NOT_ESTABLISHED`.**

Qualified separated-context review finds useful **subrelation reductions**, but R6.6
0.1 is insufficiently precise for an exact, budget/location-sensitive reduction
or complete deterministic implementation verdict. The strongest in-scope gaps are
logical event accounting, DSV derived-buffer conversion/provenance, assembly/result
typing, encode admissibility and round-trip domains. No irreducibility/minimum or
new construct count is established. Implemented kernel remains **26**. A terminal
exposure check confirmed that the reviewer inherited substantive R6.7 findings
before forming judgments; the original separation disclosure was incomplete.
Specification repair is a substantive recommendation, not an independent verdict.

## Authority, freeze and independence

The owner's “R6.7 — Independent Specification Reduction Audit” authorizes this
specification-only review and publication, and forbids implementation, compilation,
benchmark/acceptance execution, kernel changes and P6-A05 access. Initial status clean
at `c1c31072cf38907e81f55a4d9463e03012b872c3`. All six published R6.6 input SHA-256
identities verified before reviewer invocation; original bytes remain preserved.

[Protocol](r6_7/REVIEW-PROTOCOL.md) was declared before substantive review.
A distinct reviewer context formed [retained judgments](r6_7/REVIEWER-JUDGMENTS.md)
without reading R6.6 report/alternatives/open obligations or receiving publisher
conclusions through the task message. Its response was preserved verbatim and hashed
before comparison. A later [clarification](r6_7/EXPOSURE-CLARIFICATION.md) confirmed
that inherited harness guidance exposed not only R6.6's classification but an R6.7
verdict and substantive findings. Thus the predeclared independent-judgment condition
is not established. Distinct context, non-deference and withheld on-disk documents
do not cure that exposure. Original judgments/disclosures remain untouched, with the
correction separately preserved. No human/provider/model/tool-enforced independence
or statistical independence is claimed. [Provenance](r6_7/INPUT-PROVENANCE.md) and
[disagreements](r6_7/DISAGREEMENTS.md) retain chronology and unresolved distinctions.

## Deliverables

1. This audit report and final classification.
2. Frozen identities/provenance and predeclared independent review protocol.
3. [Operation-level matrix](r6_7/REDUCTION-MATRIX.md), including structural nodes,
   both codec directions, layout construction and auxiliary provenance/boundary rules.
4. [17 composition/failed-reduction witnesses and 16 counterexamples](r6_7/REDUCTION-WITNESSES.md).
5. [Formal obligation assessment](r6_7/FORMAL-OBLIGATIONS.md).
6. [Cross-domain reconstruction/removal results](r6_7/CROSS-DOMAIN-RECONSTRUCTION.md).
7. [27 cells and 16 attack review](r6_7/ADVERSARIAL-REVIEW.md) plus verbatim reviewer
   judgments, exposure correction and preserved comparison/disagreements.
8. Next bounded experiment below; [verification](r6_7/VERIFICATION.md) and
   [publication identities](r6_7/PUBLICATION-IDENTITIES.json).

## Reduction findings

- Typed record construction, End's truth predicate, duplicate truth and ordered
  decoded validation reuse kernel meanings, conditional on explicit supplied inputs.
- Finite escapes/keywords compose recognition and typed literals; a separate
  Boolean codec is redundant. ASCII's finite scalar relation can be factored,
  but raw observation, traversal, joining and preflight ordering remain accounted.
- UInt16BE's **decode arithmetic** is eight doublings plus one K24 addition on
  supplied bytes, within the 16-node bound. This challenges the frozen arithmetic
  recommendation without deriving byte acquisition, E, failures or cost.
- Decimal's five-add 10a+d step reduces; variable-length recurrent interpretation
  and inverse emission are not obtained from pointwise map. Whole relation needs
  retained meaning within the reviewed algebra; no absolute irreducibility claim.
- Dynamic raw slices, predictive lookahead, cursor-dependent traversal and ordered
  joining remain missing meanings relative to current admitted operations. A name
  for a family, descriptor, contract or map body cannot supply them.
- Span pairing can reuse records; output ranges/source maps have conditional
  prefix-sum/contribution compositions. Traversal/provenance transport is not defined
  completely enough to eliminate a whole source-location operation exactly.

Exact observations include errors/sites/node IDs/expected sets, consumed extent,
bytes/order/provenance and limits. Replacing an atom by many adds or flattening Seq
can change WORK_LIMIT/depth behavior. All successful reductions are explicitly
subrelation/value-level where appropriate, with lost information identified.

## Three-format findings and formal repair

CFG66's literal/class/choice/repetition plus escape/decimal relations supports
tagged configuration values; DSV66 shares recognition/joining but requires an
explicit post-unquoting conversion interface; BXC66 shares dependent raw traversal
and typed validation/assembly, without text decoding its arbitrary content.
Small retained subsets are reported, but complete ≤64-node plans and inclusion
minimality are not established. Domain policies are plan data; meaning cannot be
reinterpreted per format or delegated to a host conventional parser/codec.

Repair obligations: typed decode/encode/result judgments; progress analysis;
complete error and lookahead rules; L-dependent limit sites and normative cost
events; source-map and earlier-prefix construction; legal paired-layout value
domains and semantic projection π; conditional canonicalization laws under output
bounds. A bare span-bearing result round trip fails under whitespace/leading-zero
normalization; X06 already distinguishes semantic equality, so define it explicitly.
Assembly omits encode consumed despite a globally mandatory envelope shape.

The audit retains all prior executions **NOT_RUN**. Several local policies are fully
specified, others only partial; lookahead exhaustion is underspecified. The blanket
27-cell determinate claim is not accepted as complete observable precision. Stronger
Unicode/recursion/integrity/streaming/physical effects remain outside bounded witness
coverage rather than behavioral failures. No formal proof is claimed.

## Requested architectural outcomes

| Outcome | Semantic necessity assessment | Implementation feasibility, separately |
| --- | --- | --- |
| A. Both families independently necessary | not established: multiple internal operations reduce; raw interpretation and some transduction obligations remain, but family partition is not irreducibility | bounded hybrid plausible after repair; faithful lowering unverified |
| B. One family reduces to the other plus existing semantics | no complete witness: current I-BOUND lacks decimal recurrence/inverse; current C-ATOM lacks grammar traversal/layout; inlining moves meanings | could be implemented by one engine, which proves no semantic reduction |
| C. Different smaller compositional foundation justified | local factoring supported (finite tables, numeric D, construction/checks); globally smaller sufficient foundation inconclusive, exact cost/domain rules missing | a read/traverse/join/explicit transducer foundation is a proposal, not adopted or proven smaller |

No chosen outcome implies two new constructs. Failure to discover a full reduction
is not evidence of irreducibility. Kernel K01–K26 and normal profiles stay exact.

## Recommended next bounded experiment

Seek separate authorization to **establish independent review context and then
challenge prospective specification repair**, before executable conformance work.
Freeze R6.7 exposed observations; have a demonstrably input-controlled reviewer
form fresh judgments without classification/finding-bearing harness guidance.
Do not call a fresh session alone independence. Independently fix expectations
before authoring prospective 0.2 (leave 0.1 exact).

1. Give decode/encode/conversion typed judgments, progress rules, legal value domains,
   source-map/prefix constructors and a complete normative event trace.
2. Produce complete node-level plans and paired layouts for the same three formats,
   including explicit refusal/error sites and graph/descriptor size accounting.
3. Challenge ScanClass elimination, UInt16BE numeric reduction, source-map composition
   and finite escape factoring against identical errors/locations/limit traces.
4. Include CE04/CE09/CE10/CE11 plus tight-limit Seq/atom contrasts, fixed-depth nesting
   and a non-ASCII demand as refusal/scope checks. Do not enlarge meanings by host code.
5. Have a separated reviewer decide repaired sufficiency/exact reductions and retain
   disagreements. If unresolved, publish repair/inconclusive findings again.

No implementation, schema/compiler/lowerer/runtime/verifier change, benchmark authoring,
P6-A04 acceptance or P6-A05 access is proposed as part of that bounded experiment.
Any later execution needs separate authorization and independently fixed expectations.

## Verification and stop

Publication-only byte/link/inventory checks and `git diff --check` passed as recorded
in VERIFICATION.md; historical tracked artifacts and implementation remain unchanged.
Semantic executions **0**, benchmark solutions authored/compiled **0**, P6-A04
acceptance checks **0**. No P6-A05 access, provider-dependent runtime semantics,
new approval or kernel extension. Publication integrity is not semantic proof.

**Stopped after R6.7 publication. Await explicit owner authorization for further work.**
