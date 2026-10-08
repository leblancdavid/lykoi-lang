# R6.12 capability coverage matrix

Full task success denominator is five per track. Acceptance failures and static
capability gaps are different observations. Partial meanings below were assessed,
not executed or credited as complete tasks. Exact obligation/doc/code references
are in `workspaces/B|C/Tn/base/CAPABILITY.md`; stage deltas are beside them.

| Task | Python | Production Lykoi partial meanings | Production missing interface | VM partial meanings | VM missing composition |
| --- | --- | --- | --- | --- | --- |
| T1 | Accepted 15 cases | Typed durable records, identity/existence guards, checked counters, ordering, bounded atomic creations | Heterogeneous request record/union validation and pure ordered request-state fold | Scalar predicates, record construction, original-order map/select | Evolving keyed state and runtime sorting |
| T2 | Accepted 17 cases | Dependency existence/reachability, numeric deadline guards, checked sums, deterministic query order | Runtime schedule-valued generation, prefix completion and optimum result binding | Bounds, comparisons, checked addition, ordered traversal | Runtime permutation enumeration and minimum-cost lexical selection |
| T3 | Accepted 17 cases | Decoded enum/scalar validation, record ordering/cardinality | Raw variable framing, byte/checksum observations, codec output | Atoms/take/repeat/end/check, finite codecs, prune selection | XOR plus reverse/sort and accumulated payload totals within frozen plan API |
| T4 | Accepted 16 cases | Endpoint addition, overlap predicates, decoded row order | Original byte slicing, splice and assembly result binding | Forward byte reading, checks, original-order select/map | Random original slices, applied-pair schedule and position-sorted assembly |
| T5 | Accepted 15 cases | Membership/active guards, cardinality/finite weighted tally alternatives, deterministic ID ordering | First-active correlated assignment and integrated grouped-round output | Scalar/record checks, map/select and finite unrolling subsets | First-active rank, grouped reduction and evolving round-state output |

Modification coverage: A passes all three changes; B/C have no complete base and
retain blockers on all three. T4's added NOT equality itself is supported by both
semantic tracks, illustrating why an inherited whole-stage blocker does not imply
every new predicate is missing. T1 resize adds coupled delta state; T3 coalesce adds
ordered accumulation/concatenation. Original/new cases remain NOT_REACHED for B/C.

## Confidence and interpretation

Production findings concern inspected closed parameter/value/result profiles, not
kernel-26 impossibility. The VM lacks direct listed operations, but finite domains
admit possible unrolling/lookup/network compositions. The author did not identify
a complete plan within 64 structural nodes and validation bounds; no exhaustive
lower-bound proof was supplied. Review supports this qualified assessment and
clarifies that 2048 expression visits is a validation-traversal constraint.

All sixteen B/C records are static assessments, not rejected compiler/interpreter
programs. A gaps=0 observed, task success=5/5; B/C assessed gaps=5/5 and demonstrated
complete task success=0/5. No numerical partial-obligation coverage percentage is
invented from these prose subsets. No matched-success efficiency average exists.
