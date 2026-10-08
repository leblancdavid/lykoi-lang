# R6.13 capability-gap reassessment

Whole-task classifications remain **qualified current-interface assessments** for
B/C, not demonstrated acceptance failures or abstract impossibility. No complete
B/C executable existed in R6.12; none was manufactured as a replacement replay
candidate. New partial constructions below receive no whole-task score.

## Exact interfaces, confidence and uncertainty

| Task/stage | B production gap and useful existing meanings | C frozen VM gap and alternatives | Updated confidence |
| --- | --- | --- | --- |
| T1 / resize | Collection-of-request-records/discriminated operations, whole-request precedence and pure request-state/result binding. Existing durable identities, guards, counters, listings and bounded atomic creations remain useful. Resize is not a separately proved subtraction gap. | No direct evolving keyed state fold or sort; map prefix is original source, not prior computed state. Finite delta tables/unrolling remain possible partial alternatives. | High confidence in inspected B parameter-profile limitation and C prefix behavior. Whole-state alternative encodings not excluded. |
| T2 | Runtime schedule-valued synthesis, derived prefix completion/cost and optimum-result projection not exposed by ordinary query/write interfaces. Dependency reachability, sums, guards, ordering, finite multiplication alternatives are useful. | No direct permutation generator, dynamically indexed list update or argmin. Calls are argument-free/acyclic. Seven jobs fitting occurrence bounds does not supply a search algorithm, but fixed networks/finite strategies are not disproved. | Direct interfaces well-supported statically; full noncomposition confidence remains limited. No necessary plan-size lower bound. |
| T3 / coalesce | Raw hex/variable framing, byte codec/checksum observations and encoded result bindings missing from current pipelines. Decoded row ordering/cardinality could be reused. | No direct XOR/reverse/sort/fold expressions. Finite nibble XOR **works**; full byte normalization/coalescing still requires raw framing, arbitrary payload reordering and typed accumulated output. | Narrowed XOR inference: absence of opcode is not absence of finite XOR composition. Full-task gap remains a static unresolved composition assessment. |
| T4 / absent | Dynamic original-byte slicing and length-changing result assembly unsupported direct bindings. Overlap predicates/order and NOT equality are supported. | Forward cursor/emit can assemble bytes but do not directly offer arbitrary original-coordinate slice/result accumulators; explicit finite slices/layouts remain unexcluded. | NOT equality positively executed for B; direct slice rejection for C. Full slice/splice feasibility remains unresolved. |
| T5 | Correlated first-active assignment, grouped weighted iterative tally/round-result projection missing from inspected interfaces. Threshold cardinalities/addition can tally finite weights; compare doubled totals for majority, not division. | No direct grouped reduction/evolving round-state or dynamic first-active indexing. Finite dispatch/unrolling and already supplied selection remain possible subsets. | Current result-interface finding supported statically, no executed full-round candidate or exhaustive exclusion. |

Source anchors reviewed: `src/air_compiler/predicates.py:19–34,43–97` (closed
scalar/collection/predicate grammar), `references.py:186–247` (parameter and
one-record operation/result bindings), `computation.py:14–58` (six closed operators,
16-node graphs), `mutable_values.py:114–138` (scalar collection/pipeline),
`profiles.py:55–96,107–132` (closed normal dispatch/query composition),
`collection_query_runtime.py:149–168` (filter/order stored rows),
`predicate_runtime.py:14–53` (pure Boolean interpreter). VM:
`CONTRACT-1.md:39–72,117–122`, `interpreter.py:32–59,75–113,126–240`
(closed operations/expressions, selector checks, bounds). R6.12 per-track
CAPABILITY records and its review supply additional retained anchors.

## Executed new bounded constructions (separate evidence)

Frozen inputs: [PROBE-INPUTS.json](PROBE-INPUTS.json), identities in
[PROBE-FREEZE.json](PROBE-FREEZE.json). Method 2 raw results:
[PROBE-RESULTS-2.json](PROBE-RESULTS-2.json), with per-process timestamps,
stdout/stderr, return codes and 10-second deadlines.

1. **B request-record collection:** attempted `{type:collection, element:record}`
   using the production type validator; rejected `INVALID_TYPED_PREDICATE`.
   This demonstrates that specific public type construction is refused, not that
   stored records or all possible encodings are impossible. No normal full-program
   compilation was attempted; host request validation would supply central semantics.
2. **B absent predicate:** validated NOT exact string equality, then executed three
   inputs: unequal -> true, equal -> false, empty/empty -> false (**3/3**).
   Strings are already supplied; no byte slicing is credited. The modification
   predicate is not a missing Boolean semantic construct.
3. **B direct XOR/slice/permutations graphs:** each rejected
   `INVALID_REFERENCE_COMPOSITION` at the closed operator check. The recorded
   skeletons are direct-interface probes, not exhaustive compositions or otherwise
   complete task programs. Rejection precedes operand/arity checks.
4. **C direct XOR/slice expressions:** each rejects `unknown expression` during
   validation. Again this only establishes unsupported direct spelling.
5. **C map prefix:** seven-node plan executes on bytes 1,2,3. Incremented values
   are 2,3,4 but inclusive prefixes remain [1], [1,2], [1,2,3], confirming original
   source prefixes. It does not refute a differently encoded finite-state strategy.
6. **C nibble XOR:** explicit grouped prefix relation for two bytes in 0..15,
   21 structural nodes; all **256/256** pairs produce correct XOR value and UInt8
   output. Out-of-domain 16,0 rejects DOMAIN. Host code authors static plan data,
   never computes runtime VM results. This is a reusable finite-relation witness,
   not T3 acceptance or a full-byte XOR composition. The earlier naive 65,536-pair
   discussion is not a necessary node count or impossibility proof.
7. **C naive full-byte lookup:** 65,536 two-byte selectors grouped into 256 result
   branches, **261 structural nodes by authored structure**, already unsuitable
   for the 64-node domain. Method 2 process times out at 10 seconds before any
   validation response. Pairwise selector validation precedes branch-node counting
   in the inspected validator; this is a plausible source of excessive validation
   time, not an attested timeout stack. No interpreter change or smaller full-byte
   alternative attempted after this preserved negative result.

## Interrupted evidence and bounds

Initial probe method 1 was stopped by the terminal tool at 120 seconds without a
published result. [PROBE-INTERRUPTION.md](PROBE-INTERRUPTION.md) preserves this
unsuccessful attempt; no in-memory observations from it are credited. Method 2
changes execution supervision, not frozen plan/candidate/language bytes. The naive
lookup timeout is a newly observed **probe/validation-path limitation**, not a
functional failure of any A candidate and not an R6.12 full-task VM failure.

Runtime work=100000 and validation-expression-visits=2048 are distinct; validation
itself is outside charged runtime work. Node/depth/occurrence/selector-table growth
are distinct, and eight occurrences alone does not rule out grouped 16 operations
or 12 ballots. No lower bound or abstract nonexpressibility proof is provided.

No complete existing-language construction was identified for any of the five
tasks. B confidence is strongest at closed transport/input/result profiles; C
full-composition confidence is weaker, explicitly reduced by the successful finite
XOR witness. Remaining uncertainty is an experimental target, not permission to
extend the implementations.
