# T4 MODIFICATION — static capability assessment

Terminal outcome: CAPABILITY_GAP / ORIGINAL_SLICE_AND_PATCH_ASSEMBLY_UNAVAILABLE.

The preserved base has this same static code, no implementation, and no acceptance
execution. Base clauses 3–5 require arbitrary original-coordinate byte-slice
comparison, first applied-pair conflict in original-index order, and position-sorted
replacement assembly preserving untouched original bytes. The modification
explicitly retains these requirements and bounds-before-match precedence.

The new requirement is when=absent: apply on slice inequality, skip on equality,
remove len(old) original bytes when applied, and do not raise mismatch. Empty old
always skips. This does not itself require a new Boolean primitive: eq(eq(a,b),
false) can express inequality and Boolean dispatch can select applicability once
the compared slice is available. Thus no independent new predicate capability
gap is claimed. The missing original slice and general assembly still block it.

Frozen evidence inspected: CONTRACT-1.md 39–72 and 83; interpreter.py 32–59,
266–316, 344–374, 426–455, 489–541, 551–575. take consumes only at the forward
cursor; ref traverses statically spelled keys. No seek, dynamic slice/index,
sort, splice or state-fold node exists. map/select preserve supplied order;
bytes is identity and join builds ASCII strings. Sequential output emission
cannot itself discover position order and untouched original ranges.

Bounds/length comparisons and the conditional predicate are supported subsets.
Enumerating bounded positions/lengths or multiple VM calls does not identify a
complete within-bound plan: original indexing/assembly still needs explicit
composition within 64 nodes/2048 expression visits, and execute has no external
typed patch environment. Host slicing, sorting, pair checking or replacement
would implement central behavior and is prohibited. Assessment is static API
coverage evidence, not an executed VM failure or general impossibility theorem.

Assigned contracts and both suites were read after START.json. Original cases:
16 NOT_REACHED; new cases: 8 NOT_REACHED. Candidate attempts, repairs, acceptance
subprocess invocations: 0. No fabricated regression observations; regression
rate unavailable because base success was absent. Base records are preserved.
No host task algorithm, VM modification, historical plan or other-track solution
was used.
