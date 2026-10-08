# R6.12 post-result publication verification review

Status: MANUAL_PUBLICATION_REVIEW_COMPLETE_WITH_QUALIFICATIONS.

## Authority, access and method

This fresh review was requested by the round coordinator after recorded results,
within the research user's initial R6.12 comparison/publication authorization.
Reviewer: inherited OpenAI `openai/gpt-6.1-sol` session. This is a fresh,
correlated same-model review with inherited repository guidance, not independent
task sourcing, independent model evidence, certified blindness or OS isolation.
Freshness does not eliminate shared-model errors in synthetic contracts,
expectations, authoring or review.

Read scope: current R6.12 base and assigned modification contracts/acceptance;
all eight A candidates and their RESULT-1 summary/recorded stdout/return-code
fields; all sixteen B/C CAPABILITY.md assessments; record.py and PROTOCOL.md.
For static gap assessment only, read frozen current production predicates.py,
profiles.py, computation.py, references.py (1–260), mutable_values.py (1–240),
atomic_state.py (1–120), collection_query_runtime.py (140–174), and experimental
VM CONTRACT-1.md/interpreter.py. No historical task solutions, historical plans,
curated sources or P6-A05 were read. Repository path discovery and git status
were also used. No delegation, candidate execution, new trial, repair, language
work or telemetry probe occurred. The only authored artifact is this review.

Method: manually derive each of the 80 base and 24 new explicit observations
from the contracts, then inspect candidate algorithms and recorded outputs.
Do not use candidate agreement as the derivation of an expected value. The
existing result records contain 152 passing observations: 80 base, then 48
original observations repeated with modifications plus 24 new observations.
The owner's reported exact replay of 152 observations is existing corroboration;
this session did not run or independently audit the replay infrastructure.
Repeated observations are not 152 distinct inputs or independent trials.

## Principal findings

1. **Incorrect expected values found: none.** All 104 explicit expectations agree
   with their contracts, including full T5 round observations and T3 checksums.
2. **Concrete A candidate contract violations found: none by this inspection.**
   All eight candidates implement central task behavior rather than published
   input/output tables. This is source-review support, not exhaustive verification
   of all legal inputs or malformed shapes.
3. **B gaps are qualified current-profile/interface assessments.** The inspected
   closed production interfaces support the identified missing bindings; the
   records appropriately acknowledge useful relational/arithmetic subsets. These
   are not kernel-26 impossibility proofs or executed failures.
4. **C gaps are plausible frozen-API composition assessments with an important
   uncertainty.** Missing direct operations are demonstrable. Assertions that all
   suitable finite compositions exceed plan bounds are not proved by the records.
   Preserve the weaker finding: no complete within-bound plan was identified.
5. **Finite-suite and recorder limitations remain.** Missing coverage and incomplete
   enforcement cannot be converted into universal correctness, isolation, or an
   effort advantage. No observed expectation or scoring error requires changing
   the existing finite outcomes.

## Manual expectation ledger

Case numbers below are zero-based JSON array indices. Every row was checked;
short descriptions refer to the full exact observations in acceptance.json.

### T1 base — 15/15 expected observations consistent

| Case | Contract-derived observation |
| --- | --- |
| 0 | A free/held/shipped = 5/0/0; no holds. |
| 1 | Sorted A = 100/0/0, B = 0/0/0; no holds. |
| 2 | A = 0/5/0; active x holds five A. |
| 3 | Reserve then release restores A = 5/0/0. |
| 4 | Reserve then ship gives A = 2/0/3. |
| 5 | A = 0/5/0; holds ordered a(3), z(2). |
| 6 | insufficient at 1: only two free after the first reserve. |
| 7 | unknown_sku at 0, ahead of availability checking. |
| 8 | duplicate_id at 2 despite released x and absent B. |
| 9 | unknown_hold at 0. |
| 10 | unknown_hold at 2 after x was shipped. |
| 11 | duplicate_sku at -1. |
| 12 | shape at -1: n=0 outranks duplicate stock. |
| 13 | shape at -1: boolean qty is not an integer. |
| 14 | A = 0/0/2, B = 0/4/0; only z holds four B. |

### T2 base — 17/17 expected observations consistent

| Case | Contract-derived observation |
| --- | --- |
| 0 | Empty order/completion, cost 0. |
| 1 | BCAD, completions 2,3,5,6, cost 44; global optimum. |
| 2 | ABCD, completions 2,4,5,6, cost 59 with A deadline 4. |
| 3 | A completes 9, cost 81. |
| 4 | infeasible: positive duration cannot meet deadline 0. |
| 5 | BA completes 1,4, cost 8 versus AB cost 19. |
| 6 | AB completes 1,3, cost 7; BA also costs 7, so lexical tie wins. |
| 7 | AB completes 3,4, cost 19; BA misses A deadline 3. |
| 8 | Dependency forces AB, completions 3,4, cost 19. |
| 9 | BAC completes 1,3,4, cost 14 versus ABC cost 19. |
| 10 | All weights zero: lexical ABC, completions 3,5,6, cost 0. |
| 11 | infeasible: AB misses B deadline 3; BA misses A deadline 2. |
| 12 | cycle: self-loop. |
| 13 | unknown_dep Z precedes the A/B cycle. |
| 14 | duplicate_id precedes unknown_dep. |
| 15 | shape for duplicate deps precedes duplicate_id/unknown_dep. |
| 16 | Forced ABCDEFG chain, completions 9,18,27,36,45,54,63, cost 252. |

For cases 1–2 the complete dependency-respecting orders and costs are ABCD=59,
ABDC=66, ADBC=62, BACD=61, BADC=68, BCAD=44. With A deadline 4, BCAD is
excluded (A completes 5); the minimum among the remaining orders is 59.
These checks establish optimality here, not just feasibility of the expected order.

### T3 base — 17/17 expected observations consistent

| Case | Contract-derived observation |
| --- | --- |
| 0 | 0100, records 0, payloadBytes 0. |
| 1 | Tag 1 reverses 03 01 02 to 02 01 03; checksum 02; 1 record/3 bytes. |
| 2 | Tag 2 sorts 03 01 02 to 01 02 03; checksum 01; 1 record/3 bytes. |
| 3 | Tag 0 preserves ff 00; checksum fd; 1 record/2 bytes. |
| 4 | Valid empty tag-1 record pruned: 0100, 0/0. |
| 5 | Empty middle tag-0 pruned; aa and sorted 01 09 retained; checksums aa,08; 2/3. |
| 6 | Same bytes as case 3, rendered lowercase; 1/2. |
| 7 | shape for odd-length hex. |
| 8 | short_header for one byte. |
| 9 | version precedes count (02 09). |
| 10 | count for 09. |
| 11 | tag for 03 precedes length/truncation. |
| 12 | length for 09 precedes missing payload. |
| 13 | truncated: payload/checksum incomplete. |
| 14 | First record checksum is ab, supplied 00: checksum precedes later bad tag. |
| 15 | trailing after zero declared records. |
| 16 | Payload 00..07 XORs to 00; tag 00 XOR length 08 gives checksum 08; 1/8. |

In case 5 the exact normalized message is
`01020101aaaa0202010908`, as frozen. No payload was interpreted as text.

### T4 base — 16/16 expected observations consistent

| Case | Contract-derived observation |
| --- | --- |
| 0 | Empty hex, applied/skipped empty. |
| 1 | 41787943; applied [0], skipped []. |
| 2 | ff42; applied [0,1] despite position order 2,0. |
| 3 | 414243; skipped [0]. |
| 4 | mismatch at 0. |
| 5 | ff41424300; both empty-old insertions apply; applied [0,1]. |
| 6 | conflict pair (0,1) for overlapping nonempty spans. |
| 7 | Adjacent spans allowed: 00ff43; applied [0,1]. |
| 8 | Insertion at deleted span end allowed: ff42; applied [0,1]. |
| 9 | Insertion at span start conflicts: pair (0,1). |
| 10 | Two insertions at position 0 conflict: pair (0,1). |
| 11 | bounds at 1 outranks earlier always mismatch. |
| 12 | shape at -1 outranks bounds: later new hex has odd length. |
| 13 | ff; whole original slice matches case-insensitively decoded bytes; skipped [1]. |
| 14 | 424241; applied [0,2], skipped [1]; comparisons use original bytes. |
| 15 | Original 00..1f followed by ff; applied [0], skipped []. |

### T5 base — 15/15 expected observations consistent

Totals here are in sorted candidate order; E denotes exhausted weight, and the
arrow names the eliminated candidate. Terminal rounds eliminate null.

| Case | Contract-derived rounds/outcome |
| --- | --- |
| 0 | A:0, E=0; terminal winner null. |
| 1 | A:2 B:1, E=0; terminal A. |
| 2 | A:1 B:1, E=0 -> B; A:2, E=0; terminal A. |
| 3 | A:1 B:1 C:1, E=0 -> C; A:1 B:1, E=1 -> B; A:1, E=2; terminal A. |
| 4 | A:1 B:1 C:0, E=0 -> C; A:1 B:1, E=0 -> B; A:1, E=1; terminal A. |
| 5 | A:2 B:3 C:2, E=0 -> C; A:4 B:3, E=0; terminal A. |
| 6 | A:0 B:0, E=9; terminal winner null. |
| 7 | A:2 B:1, E=9; terminal A, using only nonexhausted denominator. |
| 8 | A:2 B:2 C:1, E=0 -> C; A:2 B:2, E=1 -> B; A:2, E=3; terminal A. |
| 9 | shape: boolean weight. |
| 10 | duplicate_candidate precedes unknown_candidate. |
| 11 | shape for repeated rank precedes duplicate_candidate. |
| 12 | unknown_candidate. |
| 13 | shape: empty candidate list. |
| 14 | All six totals 1 -> F; A,B,C,D:1 E:2 -> D; A,B,C:1 E:3 -> C; A,B:1 E:4, terminal E. Exhausted remains 0 throughout. |

Case 14's penultimate E total 3 is exactly half of 6 and cannot terminate;
the final E total 4 is a strict majority. Every frozen round and ordering agrees.

### Staged expectations — 24/24 consistent

| Task/case | Contract-derived observation |
| --- | --- |
| T1/0 | Resize 2->5: A=0/5/0; x.n=5. |
| T1/1 | Resize 5->1: A=4/1/0; x.n=1. |
| T1/2 | Resize 2->2: A=0/2/0; x.n=2. |
| T1/3 | insufficient at 1: increase exceeds free=0. |
| T1/4 | unknown_hold at 0. |
| T1/5 | unknown_hold at 2 after shipping. |
| T1/6 | Shrink returns three, y reserves/releases three, x ships two: A=3/0/2, holds []. |
| T1/7 | shape at -1 for later n=0, before earlier unknown_hold. |
| T3/0 | 0100, records 0, payloadBytes 0. |
| T3/1 | Tag-1 payloads 02 and 01 concatenate to 02 01; checksum 00; hex 01010102020100; 1/2. |
| T3/2 | Sorted originals 01 03 and 02 concatenate to 01 03 02 without re-sort; checksum 01; hex 0101020301030201; 1/3. |
| T3/3 | Length 8 plus 1 cannot merge; original message retained, checksums 08,fe; 2/9. |
| T3/4 | Empty tag-1 merges with aa; checksum aa; hex 01010101aaaa; 1/1. |
| T3/5 | Different-tag empty records retained, checksums 00,01; original message retained; 2/0. |
| T3/6 | Cumulative same-tag merge 01+02+04; checksum 04; hex 0101000301020404; 1/3. |
| T3/7 | checksum: empty tag-1 requires 01, supplied 00. |
| T4/0 | absent inequality applies: ff42; applied [0], skipped []. |
| T4/1 | absent equality skips: 4142; applied [], skipped [0]. |
| T4/2 | Empty old equals empty slice, skips: empty hex, skipped [0]. |
| T4/3 | bounds at 0 even for absent. |
| T4/4 | Applied absent span overlaps matching span: conflict (0,1). |
| T4/5 | Equal absent span skipped: 4111; applied [1], skipped [0]. |
| T4/6 | Original-position deletion/replacement yields 427879; applied [0,1]. |
| T4/7 | always mismatch at 1 precedes conflict with applied absent patch. |

## A candidates: central algorithms and limits

- **T1 base/modification:** strict complete validation precedes duplicates and
  operations. State dictionaries track actual free/held/shipped units, active
  holds and ever-used IDs. Sorting is by runtime keys. Resize uses signed delta
  and coordinated updates, including decrease/equality. No constants encode
  fixture outcomes or known SKU/hold identities.
- **T2:** validates phases, removes all dependency-ready jobs to detect cycles,
  then enumerates every permutation of runtime IDs. Each feasible permutation
  computes its actual completion/cost; comparison of `(cost, order)` resolves
  ties. Empty permutations succeed. This is a general bounded optimizer within
  the contract, not a greedy shortcut. Its factorial method is justified only
  by the seven-job bound; it supplies no scalability result beyond that bound.
- **T3 base/modification:** cursor parser checks original header, every record and
  trailing bytes before transforming. It computes XOR over actual bytes, performs
  runtime reversal/sorting/pruning, and re-encodes. Coalescing operates on the
  normalized records with the enlarged last output payload, retains empties and
  does not normalize concatenations again. This last behavior is required even
  though coalesced tag-2 payloads need not be sorted globally.
- **T4 base/modification:** phased shape/bounds/mismatch/conflict handling uses
  original slices throughout. Pair iteration is original-index lexicographic;
  interval tests handle empty-old insertions. Assembly sorts actual positions
  only after rejecting conflicts. The absent branch complements original-slice
  equality and preserves always-mismatch precedence.
- **T5:** reassigns original weighted ballots against the current active set,
  computes totals/exhaustion, compares strict majority, and eliminates largest ID
  among lowest totals. It constructs every round rather than just a known winner.

Numeric fields use exact int checks excluding bool. Enum membership checks in
T1/T3/T4 also reject nonstring JSON values because none equals an admitted string;
explicit extra type checks are not required to establish a defect here. All
candidates build their observations from request data, have no acceptance-file
reads, and use standard-library algorithms. No concrete implementation shortcoming
within the specified domain was found; finite tests and manual source inspection
still leave room for overlooked edge cases.

## B/C gap validity and overstatement qualifications

### B — production

The inspected `predicates.scalar_type` is closed to scalars and nonnullable
scalar-element collections. `references` parameters use that vocabulary. Stored
row validation and record schemas do not provide a request-level heterogeneous
record-union validator with the required whole-request phase precedence.
The current pipelines expose verbatim/trim/stable-deduplicate, not general hex
parsing or byte slicing. Computation graphs supply checked addition/cardinality
and specific time operations; ordinary queries filter/order existing records
without computed schedule or ballot projections. Atomic composition permits an
existing write and bounded creations, not an arbitrary request-state interpreter.

| Task/stage | Qualified static conclusion |
| --- | --- |
| T1 base/resize | Request-record/union profile gap is supported. Existing identities, guards, counters, ordering and hold-state representations are useful; their absence is not asserted. Resize retains the input-profile gap, not a newly proved subtraction impossibility. |
| T2 base | Runtime schedule synthesis/prefix-cost/optimal derived-result bindings were not found. Finite multiplication, dependency checks and predeclared candidates must not be dismissed just because no permutation opcode exists. |
| T3 base/coalesce | Raw hex/framing/codec and encoded-result bindings are missing in the inspected profile. Finite XOR relations and decoded-row sorting are possible subsets; coalescing adds accumulator bindings but does not prove a new irreducible construct. |
| T4 base/absent | Dynamic original-byte slice and length-changing assembly are unsupported direct interfaces. Interval conflict and Boolean negation already compose; absent is not an independent Boolean semantic gap. |
| T5 base | First-active ranked assignment and grouped iterative round-result bindings were not found. Weighted totals can use threshold counts plus additions; majority needs no division; field ordering can express elimination ties after totals are bound. |

These findings support stopping at an evidenced current profile gap under the
transport rule. They do not prove every legal sequence of ordinary API invocations,
alternative state encodings or finite relational programs impossible. In particular,
the distinction between permitted decoded-data projection and prohibited host shape
validation is a material comparison boundary. Allowing the latter would change
the task allocated to B; it is not a reason to silently relax this frozen protocol.
No static outcome is an observed compile/runtime failure. No B/C regression rate
exists without a successful base and executed modification observations.

### C — experimental VM

Confirmed direct API facts: forward-only cursor operations; static record-key
refs rather than dynamic byte/list indexing; map prefixes contain original items,
not computed prior outputs; select preserves order; no fold, arbitrary binary
value concatenation, sort, XOR or dynamic subtraction opcode; calls are acyclic,
argument-free and evaluate in an empty environment. This supports the identified
T1 state/sort, T2 schedule search, T3 XOR/reorder, T4 slice/assembly, and T5
ranked-round composition concerns, retained by the staged changes.

Important limitations on stronger readings of those assessments:

- C/T2 base lines 26–28 and C/T4 base lines 23–26 assert that explicit branches or
  range/slice cases cannot fit the plan bounds, without a construction-independent
  lower bound. Those are plausible estimates for the discussed approaches, not
  exhaustive non-composition proofs. A smaller finite strategy is not excluded.
- C/T3 base line 26's 65,536 XOR operand pairs describe a naive full two-byte
  lookup relation, not a necessary size for XOR. Bitwise/decomposition or staged
  finite dispatch strategies require their own accounting. The next lines properly
  weaken the conclusion to no complete within-bound composition identified.
- C/T1 modification's missing subtraction/negation is a direct-op fact, not a
  proof that the bounded 1–100 delta relation cannot compose through finite dispatch.
  The inherited state/lookup/output concerns remain the substantive assessment.
- The **2048 expression-visit bound is validation traversal**, not a runtime
  expression-evaluation budget. Runtime charged work defaults to 100000. Structural
  nodes, definition reuse, validation revisits, depth and runtime work are distinct
  constraints; none alone supplies an unpresented lower-bound proof.
- Eight occurrences do not by themselves rule out 16 operations/patches or 12
  ballots: grouping/unrolling can avoid a single oversized traversal. C records
  acknowledge this. Final emitted buffers can concatenate output bytes, although
  they do not by themselves supply an updated typed accumulator for later use.

Accordingly, retain C outcomes as **static frozen-API capability assessments with
unresolved exhaustive-composition uncertainty**. No concrete successful alternative
plan was established in this review, and no new plan/trial was authorized or run.

## Scoring, contract and finite-evidence limitations

### Observed outcomes and denominators

A result summaries report first-attempt base counts 15+17+17+16+15=80, zero
repairs; modification counts 23+25+24=72 (48 original + 24 new), zero repairs.
Recorded stdout and return codes agree with the manually checked observations.
The original 48 repeated cases all agree with their base outcomes, supporting
zero observed regressions for A on those cases. Eight successful task/stage
records do not constitute eight independent task sources.

B/C static gaps belong in task coverage/overall success denominators as the
protocol requires, but must not be recast as 80 executed failing observations
per track. Modification gaps do not yield measured regression observations.
There is no A/B/C matched-success set on which to estimate relative successful
development effort. Shorter time to a static halt is not a faster successful
implementation. Later token/cost exports cannot repair this missing match or
establish sourcing/OS independence; this review did not inspect that metadata.

### Recorder blind spots (prospective; no observed score change)

- `record.py:139–143` parses stdout with ordinary `json.loads` and compares sorted
  JSON serializations. It correctly preserves list order, distinguishes bool/int
  and int/float for these fixtures, rejects extra parsed fields and rejects trailing
  non-whitespace output. However, duplicate output object keys collapse silently.
  The contracts explicitly require unique *input* keys; whether repeated output
  keys must be rejected deserves prospective clarification. Current candidates
  emit ordinary unique-key dictionaries, so this did not affect their outcomes.
- `record.py:125` checks the 900-second elapsed budget before the case loop, not
  at completion or before each case. The recorder itself could accept a result
  completed beyond that budget. It does not enforce whole-track session caps.
  All eight inspected A result elapsed values are under 69 seconds; no A overrun
  was observed. This is a protocol-enforcement limitation, not a reason to relabel
  these results. Session caps/other-track timing were not independently audited.
- The recorder checks a prior failed result before a repair but does not itself
  prohibit every alternative path to a later trial after success/gap. Its process
  controls depend partly on author/session discipline. Reviewed A records are all
  attempt 1, zero repairs; no prohibited extra trial was demonstrated.

No material ambiguity or contradictory expected value was found in the central
task contracts. The bounds are deliberately finite. No input-validity promise
should be inferred for malformed transport JSON, duplicate input keys or oversized
requests, which the contracts exclude from the domain.

### Specific coverage omissions

- **Shared shapes:** the explicit suites sample very few malformed key sets,
  nested nonobjects, wrong list types, floats, booleans and range violations.
  They do not exhaust the request/record/union shape space. Strict-looking source
  validation is useful evidence, not universal shape coverage.
- **T1:** no eight-SKU/16-operation boundary sequence, broad multi-SKU interleaving,
  all identifier-length boundaries, or complete error-precedence cross product.
  Resize fixtures do not exercise all repeated-resize interactions and quantities.
- **T2:** the seven-job fixture is a forced chain with one legal order, not a
  seven-job optimization stress case. Pure multi-job cycles, every numeric/type
  boundary and broadly interacting deadlines/dependencies/ties are not covered.
- **T3:** no eight-record/64-payload-byte valid boundary message, broad duplicated
  byte sorting, or every missing-tag/missing-length/checksum/trailing combination.
  Coalescing lacks an exact-length-8 merged fixture and a cap-triggered split
  followed by later merging into the newly created last output record.
- **T4:** no 16-patch boundary, maximum-length assembly, or multi-conflict case
  choosing among several candidate pairs. The latter means the suite does not
  establish first-pair lexicographic precedence merely by testing pairs (0,1).
  All insertion/span/skip configurations are not exhausted.
- **T5:** six candidates are tested, but the longest fixture has four rounds.
  There is no six-round or twelve-ballot/max-weight boundary case, nor broad
  rank/transfer/tie permutations. Full frozen round observations are checked,
  but all round shapes and all valid ballot populations are not universally covered.

These are prospective limitations only. Frozen contracts, suites, candidates and
results remain authoritative and unmodified. The defensible publication claim is
finite A success with general central algorithms, B/C qualified static coverage
gaps, and an exploratory correlated comparison—not universal correctness,
independently sourced generalization, kernel minimality or proven effort advantage.
