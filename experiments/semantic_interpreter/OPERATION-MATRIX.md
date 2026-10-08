# R6.10 operation reuse and semantic-gap matrix

Every exposed operation and implementation mechanism is classified below. Kernel
IDs follow preserved R5.114 accounting. Reuse here means semantic correspondence
on tested supplied values, not production imports or an accepted byte/result binding.
The VM imports no production module. Tests import the pure predicate evaluator for
the explicitly qualified equality/order comparison; they execute no acceptance path.

| Operation/subrelation | Classification | Evidence and boundary |
| --- | --- | --- |
| record fields, literal, ref, finite supplied map/each | Existing-kernel composition K01–K05/K12 | Tagged CFG row, DSV map and layout, fixed-depth generic plan tests. Cursor/span/binding integration is additional candidate meaning. Full static schema correspondence unresolved. |
| eq/le, integer and ASCII string supplied operands | Existing-kernel reuse K06/K16, qualified value subrelation | test_kernel_predicate_correspondence compares 8 vectors to src/air_compiler/predicate_runtime.py; no null/normalization/cost equivalence claimed. |
| length/nonempty | Existing-kernel composition K18/K16 | Empty key, record/name bounds, dependent BXC prefix and trailer tests. No raw observation reduction. |
| select | Existing-kernel composition K10/K16 | DSV quantity selection and BXC empty-selection witnesses. Ordered transport/join remains new. |
| unique truth, check order | Existing-kernel composition K06/K12/K13/K17/K18 | Duplicate tests in all formats; competing DSV rules; conflicting ordered checks in all formats. Prefix acquisition and error site are new. |
| add | Existing-kernel composition K24 | Signed boundary/overflow vectors and executable DSV +1 and BXC +2 layouts, against documented signed-64 contract. Does not claim runtime-code reuse or budget equivalence. |
| explicit absence/Boolean projection | Existing-kernel composition K05/K19 | none versus empty and true/false tests; no extra Boolean codec. |
| literal raw recognition, scan, take, atom access, choice | New candidate semantic meaning | Exact byte/cursor access, first-error/EOF rules and predictive traversal absent from admitted decoded-value operations. Truncation, prefix refusal, raw name and length tests. |
| seq cursor transport, repeat, call | New candidate semantic meaning | DAG/progress/count/stop-driven consuming evaluation; name/record/string cases and generic fixed nesting. Not arbitrary K12 fold. |
| join, emit, layout concatenation/dispatch | New candidate semantic meaning | Ordered string/byte assembly across all domains; canonical escapes and byte layouts. Choice truth is kernel composition; output branch construction is new. |
| ASCII/finite escape scalar mappings | Existing-kernel composition, scalar subrelation only | Exhaustive ASCII scalar inverse; CFG escape and DSV doubled-quote tests. Finite literal relations compose K05/K06; traversal, preflight, join and E emission retain candidate meanings. |
| Decimal15 bidirectional transduction | New candidate semantic meaning | Prefix overflow, delayed conversion/provenance, leading-zero canonicalization, numeric boundaries; arithmetic step alone does not eliminate recurrent scanning/inverse. |
| UInt8/UInt16BE bidirectional codecs | New candidate semantic meaning, raw/inverse envelope retained | All 65536 UInt16 round trips, wrong type/range, truncated atoms. Nine-add decode reduction is a prospective value-level test, not executed here as a reduced plan. |
| bytes exact identity | Existing-kernel composition K04/K05 | Arbitrary binary content preserved, including high bytes and embedded container. Access/append remain new. |
| bytes_check and Take membership | Existing-kernel composition K09 on supplied scalar; New candidate semantic meaning for raw traversal | Invalid name before truncation and high-byte-name checks. No production membership-code correspondence test claimed. |
| Cell spans/origins, prefix, result envelope | New candidate semantic meaning | CFG spans, doubled-quote map, delayed numeric error sites and private failures. Record representation alone does not supply cursor origins. |
| limits, logical event accounting | New candidate semantic meaning | Every tight-work cutoff on three representatives, work-before-depth, occurrence/input/output tests. R6.10 convention; exact R6.6 optimization correspondence unresolved. |
| Python loops/dicts/lists/bytearray/byte slicing/chr/ord/div/mod/multiply | Host implementation mechanism | Closed operation dispatch realizes above meanings; no parsing library, eval/exec, dynamic import, IO or subprocess reachable from plans. Allocator/time behavior not qualified. |
| full static type preservation; field-path encode sites; exact R6.6 cost equivalence; normal-path bindings/lowering | Unresolved semantic obligation | Runtime guards and tested graphs do not discharge these; no production profile integration. |

K11/K14/K15/K20–K23/K25/K26 are inventoried but not exercised: trim, lifecycle,
time, authority, durable/atomic state, graph reachability and duration meanings do
not supply raw grammar interpretation. No existing physical authority is widened.
This experiment does not assert an irreducible meaning count, minimum or completeness.
