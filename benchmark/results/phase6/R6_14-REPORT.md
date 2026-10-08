# R6.14 — Generic finite-relation construction challenge

**Final classification: `R6_14_FINITE_RELATIONS_SUPPORTED`.**

The unchanged R6.10 VM expresses **full-byte XOR, modulo-256 addition and byte
parity** using existing operations. XOR8 and ADDMOD8 each pass **65,536/65,536
valid pairs**, PARITY8 **256/256 inputs**, on **three complete runs** with identical
full-result/work digests and no observed functional failures. The first XOR8 plan
was rejected; one separately frozen follow-up repairs its consuming-progress witness.
This is finite experimental support, not universal expressiveness, optimality,
independent qualification or a production-language extension.

## 1. Baseline, authorization and freeze

Owner's R6.14 request authorizes bounded construction on unchanged VM, with no new
operations. [Baseline](r6_14/BASELINE.json) verifies **642 protected/history identities**,
production kernel **26**, R6.10 published interpreter identity
`bf5dbfb96d6d50124d109c35804c81e5a27bf4038b7f65b1a909ad4f0cc13fa3`,
R6.13 probe freeze/results identity, and reproduces the exact **21-node nibble XOR
witness, 256/256 pairs**. [Copied witness](r6_14/NIBBLE-WITNESS.plan.json) preserves
the historical plan; [historical evidence](r6_14/HISTORICAL-XOR-EVIDENCE.json) retains
the original nibble result and naive full-byte timeout records. The initial working
tree contained R6.12/R6.13 publication work, recorded before edits and preserved.

[Protocol/specifications](r6_14/PROTOCOL.md) and [spec freeze](r6_14/SPEC-FREEZE.json)
precede new construction. Definitions: XOR8(a,b)=a XOR b; ADDMOD8(a,b)=(a+b) modulo
256; PARITY8(a)=population count modulo 2. Exact integer input domain [0,255]; exact
integer results and one-byte output. Acceptance expectations never changed.

Verified VM limits: 64 structural nodes, depth16, 2048 validation expression visits;
default runtime work100000, input/output4096 and occurrences8, only tighten-able.
Expressions, selectors and their serialized bytes are distinct from structural nodes.
Validation is outside charged runtime work. Static Take progress is conservatively
zero even with a constant length; UInt8 Atom establishes one-byte progress.

## 2. Construction and input boundary

[Builder](r6_14/build.py), [transparent adapter](r6_14/boundary.py),
[original runner](r6_14/run.py), [run freeze](r6_14/RUN-FREEZE.json).
The VM consumes bytes. The adapter only checks argument count, exact integer type
(including Boolean exclusion), range, then serializes bytes. Missing/extra arguments
produce MISSING/ARITY, wrong type TYPE, wrong range RANGE, with deterministic first
argument index. These are **boundary checks**, not integer-valued VM input semantics.
Raw byte shortage/trailing and non-bytes are tested separately. No adapter computes
XOR, addition, parity or decomposition; no host callback or dedicated opcode exists.

### XOR8: reusable projections, cardinality and checked addition

[Successful plan](r6_14/xor8-consuming.plan.json),
[first rejected plan](r6_14/xor8.plan.json).

1. Shared `bits` rule observes the same unconsumed byte through two unary choices:
   high-nibble and low-nibble projections. Each has 16 value-record branches and
   256 one-byte selectors grouped by nibble. Together they expose eight Booleans.
2. UInt8 Atom consumes the byte; the rule returns its explicitly constructed bit
   record. One call reads a; a singleton counted repeat/call reads b as a one-item list.
3. Eight selections retain b's item exactly when its named bit differs from a's.
   `length` of each result converts that Boolean relation into an integer 0/1.
4. Seven bound Horner stages double the earlier result with `add(ref,ref)` and
   add the next bit; UInt8 emission produces the result byte.

The builder enumerates finite unary table data; it is never imported by the VM.
The central binary XOR relation is composed in the plan, not a 65,536-pair table.
Rule sharing is real structural reuse. Bound Horner values avoid exponentially
duplicated expression trees; duplicated ref expressions are still evaluated/charged,
not implicitly memoized. No arbitrary indexing, multiplication, shift or XOR is added.

### Other relations

- [ADDMOD8](r6_14/addmod8.plan.json): two UInt8 atoms; checked addition; `le(sum,255)`
  dispatch chooses sum or checked `add(sum,-256)`; UInt8 emission. This exercises
  arithmetic and conditional normalization with no finite lookup.
- [PARITY8](r6_14/parity8.plan.json): same reusable byte projection; nested exact
  Boolean equality with explicit complement; Boolean dispatch returns integer0/1;
  UInt8 emission. This exercises projection, Boolean composition and typed result selection.

## 3. Budgets and complete attempt chronology

Experiment1 froze six attempts, 600-second builder deadline, 120-second construction
process cap, 900-second measurement dispatch deadline, <=180 seconds per worker;
naive comparison validation <=10 seconds. Builder execution and every child remained
within these limits. Session dispatch measured **50.571 seconds**. Original evidence
is [construction record](r6_14/CONSTRUCTION.json), [start](r6_14/RUN-START.json) and
[raw process results](r6_14/RUN-RESULTS.json).

| Attempt | Outcome and cause |
| --- | --- |
| Historical naive XOR8 table copied as comparison | 261 structural nodes; 65,536 two-byte selectors; canonical618,161 / pretty5,382,961 bytes. Validation worker times out at **10.023 seconds**, before any validator response. No runtime acceptance. Its structure already exceeds64; observed halt is timeout, not a returned size rejection. |
| XOR8 projection/cardinality, Take consumption | **57 nodes**, validation rejects `nonconsuming repeat` in all five observations. Its constant Take cannot prove progress. Acceptance worker independently hits this PlanError before any valid case. |
| ADDMOD8 | 9-node plan validates; complete exhaustive acceptance. |
| PARITY8 | 43-node plan validates; complete exhaustive acceptance. |
| Oversized balanced expression tree | 2 structural nodes but 4,096 serialized expression occurrences including encode; validator rejects `expression bound` on visit **2049**. This is an intentional limit control. |
| Oversized structural sequence | 67 authored nodes, depth2; validator rejects `plan size/depth` at walk65, after63 expression visits. Intentional node-limit control. |

Original attempt budget was exhausted. Before any repair, a **separate experiment2**
and explicit budget change were recorded in [follow-up protocol](r6_14/FOLLOWUP-PROTOCOL.md)
and [follow-up spec freeze](r6_14/FOLLOWUP-SPEC-FREEZE.json), under owner's section8
allowance. One successor only: replace the shared rule's Take with existing UInt8
Atom; no other plan operation/expression or expectation changes. <=120-second builder,
<=180-second acceptance child and <=240-second session; **70.558 seconds** measured.
[Construction](r6_14/FOLLOWUP-CONSTRUCTION.json),
[freeze](r6_14/FOLLOWUP-RUN-FREEZE.json), [raw results](r6_14/FOLLOWUP-RESULTS.json).
Successful XOR8 is a **post-failure repair**, not first-attempt success. No further
attempts/budget increases occurred. All failed plans and original traces remain.

## 4. Structural and validation measurements

Canonical bytes use sorted compact JSON; published bytes include readable indentation.
Tree depth counts structural nodes only. Expanded runtime depth includes call/repeat
frames; expression depth is separate. Traversals are counted on original validator via
profiling/tracing in a separate run; wall times use five uninstrumented observations.

| Relation | Nodes | Canonical / published bytes | Tree / runtime / expression depth | Serialized expressions | Validator walk / expression visits | Prefix-pair comparisons | Median validation |
| --- | ---: | ---: | --- | ---: | --- | ---: | ---: |
| XOR8 consuming successor | 57 | 10,582 / 64,295 | 3 / 6 / 4 | 264 | 129 / 602 | 195,840 | 25.819 ms |
| ADDMOD8 | 9 | 695 / 1,819 | 3 / 3 / 2 | 12 | 9 / 12 | 0 | 0.0227 ms |
| PARITY8 | 43 | 8,813 / 58,470 | 3 / 5 / 9 | 191 | 79 / 361 | 130,560 | 16.705 ms |

All successful plans meet limits. XOR8/PARITY8 each author512 unary selectors but
reuse rule definitions; validation rewalks a rule both as a definition and per call.
Thus shared representation does not imply shared validation work. The original rejected
XOR8 has265 expressions, 112 walks/510 expression visits before rejection and median
25.238 ms. Exact repeated-expression shapes, rule calls, five timings and failures:
`r6_14/*-structure.json`. [Summary](r6_14/SUMMARY.json) indexes successful measurements.

**2048 is a validation expression-visit limit, not a runtime evaluation limit.**
602 visits coexist with up to1196 charged XOR8 runtime events; comparisons of those
numbers are not comparisons of identical units. Selector disjointness does pairwise
work separately from expression traversal and runtime selector matching.

## 5. Exhaustive acceptance, timing, work and determinism

Exhaustive runs validate once, then use **unchanged Machine/run/plain/provenance**,
including encode, on valid bytes/default limits. The runner spells out the public
execute's nontext validated-byte path without changing any VM method or suppressing
charged events. This separates execution from repeated validation. Oracle operations
are external expected-value calculations; they never enter the plan's execution.

| Relation | Unique valid domain covered | Repeated full passes | Wall seconds per pass | Work min–max | Work sum per pass |
| --- | ---: | ---: | --- | --- | ---: |
| XOR8 | **65,536/65,536** | 3 | 14.904, 14.896, 15.291 | 176–1196 | 45,219,840 |
| ADDMOD8 | **65,536/65,536** | 3 | 1.302, 1.289, 1.298 | 22–24 | 1,507,072 |
| PARITY8 | **256/256** | 3 | 0.02559, 0.02486, 0.02535 | 56–566 | 79,616 |

The three per-relation SHA256 digests match over input, **entire success envelope**
(value/provenance/consumed/output/spans) and work. All expected values and emitted
bytes are exact; zero observed functional failures. Repeated passes are repeats,
not extra distinct-domain coverage. Checkpoints every4096 pairs retain progress.

Public `execute` equals the validate-once path at a fixed8x8 boundary grid for both
binary relations and all256 parity values. Public cross-check wall times: XOR8
**1.735 s /64**, ADDMOD8 **0.00362 s /64**, parity **4.417 s /256**. These are batch
cross-check timings including both paths, not a pure public-API benchmark. Validation
dominates the selector-heavy public API; validate-once timings should not be advertised
as public execute throughput or production performance.

Acceptance records: [XOR8](r6_14/xor8-consuming-acceptance.json),
[ADDMOD8](r6_14/addmod8-acceptance.json), [PARITY8](r6_14/parity8-acceptance.json).
They retain work histograms, pass digests/times and explicit negative observations.
There are57/57/42 negative summary entries respectively; work-cutoff entries aggregate
**2066/68/848 distinct cutoffs**, each tested three times. Every cutoff below successful
work for frozen representatives returns WORK_LIMIT at exactly that charged count.
Input/output/depth exhaustion and invalid limit vectors pass; no construction hits
default runtime limits. Negative values, above255, floats/strings/bools/null/containers,
missing/extra arguments, invalid-order precedence, native non-bytes, truncated/trailing
bytes and malformed shapes/IDs/refs/cycles/overlap/depth reject deterministically.
Malformed over64/over2048 plans are the separate controls above.

## 6. Memory and reproducibility

[Machine record](r6_14/RUN-START.json): Windows11 build26300, AMD64 Family25 Model97
Stepping2, AuthenticAMD,16 logical CPUs; CPython **3.14.3**, MSC1944 64bit;
QueryPerformanceCounter monotonic clock,1e-7-second resolution. GC enabled, thresholds
(2000,10,0). Serial fresh workers, same interpreter; no CPU affinity/idle-host guarantee.
All code is Python standard library, AI-provider independent, with no provider calls.

Separate 256-case public-execute tracemalloc samples report peak traced allocations:
XOR8 **2,067,507 bytes**, ADDMOD8 **906,363**, parity **1,937,746**. These are peaks
across the sample with default GC, including validation allocations retained until
collection. They are not per-call allocation, exhaustive-domain peak memory, RSS or
native allocator measurements. Memory sampling is separate from exhaustive timing.

Original commands, executed from repository root:

```powershell
python -B benchmark/results/phase6/r6_14/audit.py baseline
python -B benchmark/results/phase6/r6_14/build.py
python -B benchmark/results/phase6/r6_14/run.py supervise
python -B benchmark/results/phase6/r6_14/followup.py
python -B benchmark/results/phase6/r6_14/publish.py
```

Evidence writers intentionally refuse overwriting existing files; those commands are
the run provenance, not instructions to overwrite this publication. Read-only identity
check: `python -B benchmark/results/phase6/r6_14/audit.py verify`. For reproducing a
single case, load the published JSON plan, import original interpreter and call
`execute(plan, bytes([a,b]))` (parity one byte). Source describes exact exhaustive input
order, external oracle, digest serialization, measurements and supervised deadlines;
any later full replay must retain its own separately authorized evidence location.

## 7. Interpretation and practical limits

1. **Existing operations suffice for these tested relations.** No dedicated bitwise
   primitive is necessary for these finite UInt8 examples; a missing direct opcode
   did not imply semantic impossibility.
2. **Compositional reuse fits current limits.** XOR8 fits57/64 nodes, using unary
   projections, explicit typed records, equality, selection/cardinality and addition.
   The same projection supports parity, while addition normalization is compact.
3. **Representation and validation matter.** Ten KiB compact XOR8 still uses512
   selectors and195,840 validation comparisons. Sharing reduces plan duplication but
   the validator revisits definitions. Five-million-byte naive formatting and unbounded
   pairwise validation before a size response are implementation/representation limits.
4. **Authoring is nontrivial.** Boolean-to-integer conversion through singleton selection,
   explicit bit-field bindings and staged doubling are indirect. The Take-progress
   failure demonstrates authoring friction despite correct intended consumption.
   Builders reduce manual repetition, but authoring tokens/time/repair cost were not
   instrumented; builder execution seconds do not measure AI effort.
5. **Runtime overhead is substantial relative to compact addition.** XOR8's average
   work690 versus addition23, and approximately15s versus1.3s exhaustive passes under
   this harness. Bitwise projection/parity share ordered linear selector scans; cost
   changes with byte/branch order. This is finite overhead evidence, not an asymptotic
   result, optimality comparison or host-language benchmark.
6. **No semantic impossibility demonstrated.** Failures concern static progress proof,
   representation bounds and validation time. Formal completeness, minimality, arbitrary
   input domains, larger widths, whole benchmark-task composition and production
   expressibility remain unestablished. The native integer-input interface is absent;
   the transparent validated byte boundary is explicitly part of this experiment.

Same-agent contract/oracle/construction exposure, correlated tests, platform-specific
timings, partial public-API crosschecking for binary relations and limited memory
sampling constrain interpretation. Exhaustive finite execution is empirical coverage,
not a formal proof or independent review.

## 8. Preservation, verification and stop

[Regression transcripts](r6_14/CHECKS.json): **126 unittest methods pass** (82 VM,
22 compiler,9 application,3 baseline,10 R6.13 scorer); production model validation
and safety pass. [Publication checks](r6_14/PUBLICATION-CHECKS.json) record
`git diff --check`, new-file whitespace checks and final642 preserved identities.
[Publication identities](r6_14/PUBLICATION-IDENTITIES.json) bind new artifacts/guidance.
Production kernel26, compiler/lowerer/runtime and R6.10 VM unchanged; historical
R6.3–R6.13 artifacts preserved. P6-A04 acceptance executions0, P6-A05 not accessed;
no independent reviewer, subagent, provider or new semantic operation.

**Recommended next experiment:** separately authorize a fixed-budget unchanged-VM
representation comparison: prefreeze a threshold-based byte projection versus these
unary selectors, with identical UInt8 domains, explicit shared-expression/binding
accounting, standalone/public-validation and validate-once timing, and independently
reviewed expectations. Test whether selector-free decomposition lowers validation
cost within64 nodes before proposing any general VM validation/interface change.
Do not infer a need for a XOR opcode or integrate these plans into production.

**Stopped after bounded construction and publication. Await explicit owner authorization
before further experiments, language work or replay.**
