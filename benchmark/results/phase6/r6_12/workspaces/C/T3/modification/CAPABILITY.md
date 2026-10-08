# T3 MODIFICATION — static capability assessment

Terminal outcome: CAPABILITY_GAP / XOR_REORDER_AND_GREEDY_FOLD_UNAVAILABLE.

Preserved base outcome: XOR_AND_PAYLOAD_REORDER_UNAVAILABLE; no implementation
or acceptance execution. Base clauses 2–4 require original-message XOR checks,
tag-directed reversal/sorting, re-emission checksums and payload totals. The new
contract retains validation and normalization, so it does not resolve these
inherited blockers. Hex conversion is permitted transport, not XOR/reordering.

Modification clauses 1–3 add a greedy left-to-right output-state fold: compare
the next tag with the last output tag, test combined length, concatenate payloads
and replace the last record, or append a new record. Subsequent decisions must
observe the enlarged output record. Normalized payloads must not be normalized
again and empty records remain. Pointwise maps over original prefixes cannot
carry that updated last-output record between iterations.

Frozen evidence inspected: CONTRACT-1.md 39–83, 117–122; interpreter.py 32–59,
266–384, 443–455, 489–541. Expressions/codecs have no XOR or byte permutation,
dynamic list indexing, binary concatenation or accumulated state reduction.
join is ASCII string construction, not arbitrary binary concatenation; bytes
copies a supplied byte value. Emitting several buffers can concatenate final
output bytes but does not create an updated record for the next greedy decision
or provide XOR. select retains order; unique rejects rather than merges.

Bounded unrolling was considered against the base assessment: eight records
and eight-byte payloads do not alone cause the gap. Fixed reads/layout and prune
subsets are expressible, but no complete composition of inherited XOR/reorder
plus the new greedy state updates was identified within 64 nodes, 2048 expression
visits and argument-free acyclic rules. This is implemented-API coverage evidence,
not a mathematical impossibility or executed interpreter rejection.

Both assigned contracts/suites were read after the modification recorder start.
Original cases: 17 NOT_REACHED; new cases: 8 NOT_REACHED. Candidate attempts,
repairs and acceptance subprocess invocations: 0. No regression observations;
regression rate unavailable without a successful base. No host central algorithm,
VM changes, historical plans or other-track solutions were used.
