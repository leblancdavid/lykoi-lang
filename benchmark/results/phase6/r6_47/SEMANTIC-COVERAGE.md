# Semantic coverage and diversity

## What was measured

The selected17 episodes contain49 exact immutable definitions and209 step nodes.
Count each selected definition once, even if repeated in registry snapshots:

| Experimental occurrence | Exact count |
|---|---:|
| check |63|
| value |41|
| UInt8 atom |51|
| compose |24|
| end |30|
| ref expression |348|
| const expression |89|
| add expression |83|
| le expression |61|
| eq expression |2|

Expression counts include results, sites and step expressions. These are syntactic
occurrences in49 definitions, **not**83 distinct addition behaviors,63 invariant
families or24 independent reuse tasks. The cohort has eight shared-definition
selective-migration lifecycles and nine single-relation discovery/evaluation episodes.
At the scaffold level there are only **two** patterns: shared checked-arithmetic
byte callers with selective successor migration; and checked-arithmetic relation/
transfer construction. Both are one stateless arithmetic/check domain. The wider
kiln/custody pool adds guarded local durable state, with closely related skeletons.

## Production kernel:26 constructs, separate population

The17 experimental positive bundles contain **0 production-model targets**, so
production occurrence in that cohort is0 for **each of K01–K26**. Matching operator
names across profiles is not evidence that a model was trained on production semantics.
The following matrix maps auxiliary evidence and gaps; it does not add unit-test
vectors to the17-example denominator or infer production completeness from the VM.
IDs follow preserved R5.114 accounting (K01–K23 baseline, K24–K26 additions).

| ID | Production construct | Auxiliary production evidence / training gap |
|---|---|---|
| K01 | record schema | Task manager, kiln/custody fields; only narrow application families |
| K02 | field | Many repeated fields; nominal/nullable/reference combinations need source joins |
| K03 | finite sequence | Mutable-value/collection tests; absent from the arithmetic positive cohort |
| K04 | var | Typed field/parameter bindings in intents; richer binding/effect combinations sparse |
| K05 | literal | Creation/write values in all six C intents; constants are not diversity |
| K06 | equals | Explicit `eq` occurs12 times in kiln s2 and12 in custody s2; repeats of enum policy |
| K07 | and | Each C s2 has3 explicit `and` nodes; conditional state constraints dominate |
| K08 | not | Each C s2 has2; negation/error interactions need different families |
| K09 | contains | Collection/profile tests; no `contains` in six C intents |
| K10 | selection | Production queries/listing; different selection/write interactions not joined |
| K11 | trim | Task-manager/input profile evidence; normalization-versus-raw validation order sparse |
| K12 | map(trim) | Collection tests; no curated requirement episode in selected cohort |
| K13 | stable_unique | Collection tests; distinguish from reject-duplicates and order preservation |
| K14 | transition | Kiln/custody guarded state changes; same two-state scaffold overrepresented |
| K15 | instant | Clock-created timestamps/sorting; recurrence and temporal scope not supplied |
| K16 | before | Production date/predicate tests; missing broad requirement-level examples |
| K17 | operation contract | Typed guards/writes/ordered errors; persistence decoder seam demonstrates incomplete fidelity |
| K18 | cardinality | Historical typed-computation tests; count→ordinal→atomic-history examples require joins |
| K19 | input presence | Required inputs, blank-label and omitted-gate controls; presence×nullable×ordered validation sparse |
| K20 | typed resource/capability authority | Production declarations/controlled host tests; authentication is not established |
| K21 | durable state | Two C domains, restart and exact rejection bytes; kiln list/envelope defect limits positives |
| K22 | atomic commit | Cooperating local write/rollback evidence; no general crash/concurrency coverage |
| K23 | finite nonempty-path reachability | Persistent-reference tests; absent in selected positive cohort and six C intents |
| K24 | checked integer addition | Production typed-computation examples; experimental add83 is a different profile |
| K25 | fixed-duration instant displacement | Historical offset tests; calendar recurrence is outside this meaning |
| K26 | checked elapsed-day duration conversion | Signed64 dimensioned conversion tests; sparse source-authoritative end-to-end examples |

Auxiliary six C intents have explicit operator counts (base/s1/s2): kiln eq6/7/12,
and1/1/3, not2/2/2, or1/1/1; custody eq6/7/12, and1/1/3, not2/2/2, or1/1/2.
All other explicit `op` names occur0 in these six serialized intents. This is an
**intent syntax census**, not a count of compiler-internal K01–K26 executions.
Implicit state/storage/resource lowering must not be guessed from absent `op` keys.

## Requested behavioral dimensions

| Dimension | Selected17 source cohort | Gap / underrepresented combination |
|---|---|---|
| Typed expressions | Int64/Bool/Unit, add/le/eq; Bool mostly check results | Rich records/collections/nullable types; mixed type and boundary-error requirements |
| Conditional behavior | Checks absorb failure; no branching in wrapper | State-conditional effects, multiple branch paths, branch×authority |
| State transitions |0 application-state episodes | Two-state kiln/custody auxiliary pool; multi-step invariants/history/schema evolution |
| Invariants | Explicit ordered numeric checks | Persistent whole-store/reference invariants and invariant×migration |
| Persistence |8 definition-registry lifecycles | Registry history is not mutable state; list/envelope/absence corruption policy |
| Effects/authority |0 production-effect episodes | Host-role/owner/resource scope, atomic rejection; no invented authentication |
| Ordered operations | Explicit order throughout;63 check sites | Multi-error precedence across decode/lookup/guard/input/commit |
| Symbolic dependencies |24 compose occurrences, pinned caller lifecycles | Transitive diamonds, multiple abstractions, differing migration layers |
| Composition/reuse |8 two-caller lifecycles;3 discovered relations | Cross-domain reuse; nested compact combination full acceptance unresolved in R6.40 |
| Successor modifications |8 lifecycle episodes | Mostly formula/pin changes; structural state/schema/authority changes sparse |
| Error precedence | Ordered numeric/input checks and malformed bytes | Production store→lookup→guard→input; migration-enabled ambiguity remains |
| Provenance | Exact pins/maps; replayed spans/work | Raw/decoded/region/symbolic coordinate distinctions; authored text and dynamic lineage unavailable |
| Invalid-input behavior | Truncated/trailing/type/budget and semantic failures | Production raw-state shapes, signed64 boundary combinations, resource and rollback faults |

Broad production readiness fails on coverage. A small experimental-profile study
could target the implemented subset, but must label excluded state/effect semantics
and retain wholly unseen requirement/scaffold families for evaluation.
