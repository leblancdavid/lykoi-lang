# T4 BASE — static capability assessment

Outcome: CAPABILITY_GAP / ORIGINAL_SLICE_AND_PATCH_ASSEMBLY_UNAVAILABLE.
No acceptance executed; no runtime failure claimed.

Contract 3 requires comparing each old value to an arbitrary original byte slice
at runtime position; contract 4 checks applied pairs in original-index order;
contract 5 assembles replacements in position order with untouched original bytes.

References: CONTRACT-1.md 45, 47–60, 64–72, 83; interpreter.py 32–59,
ref evaluation 269–274, take/atom 426–442, seq 443–455,
map/select 489–513, emit 524–532, call 540–541.
Take reads exclusively at the current cursor, and no node can seek/reset it.
Ref projects statically spelled record keys, not runtime indices or byte slices.
The bytes codec is identity, join produces strings, map/select preserve sequence
order, and no sort, splice, slice, list concatenation or state fold is exposed.

Considered bounds and subsets: input 32 bytes/output 160 bytes fit VM limits;
add/length/le can express scalar end-bound comparisons after suitable parsing;
finite Boolean dispatch can express applicability conditions if slice equality
were available; eq can compare whole byte values. Sixteen patches can be parsed
in groups/unrolled stages, so the occurrence ceiling alone is not decisive. One
could read the original as individual atoms and dispatch over all 33 positions
and nine lengths, but dynamically indexing those bindings is unavailable and
explicit range/slice cases plus validation/assembly do not fit the frozen 64-node
acyclic argument-free plan. Re-reading original bytes with a fresh execute call
does not supply an external typed patch environment; choosing inputs or collecting
results in host code to implement slicing, pair validation, sorting or patching
would move central behavior into transport. A simple forward one-patch subset does
not satisfy arbitrary original-coordinate out-of-order patches. No fallback or
acceptance-specific implementation is provided. Assessment is confined to the
frozen API, not a general impossibility theorem.
