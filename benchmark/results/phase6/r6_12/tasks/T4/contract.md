# T4 — Conditional original-coordinate byte patches

1. One JSON stdin request→one JSON stdout observation, no other stdout. Request
   is exactly `{hex,patches}`. hex is 0–64 even-length ASCII hex digits (either
   case); patches is a list of 0–16 objects, each exactly `{at,old,new,when}`.
   at is an integer 0–32; old/new are each 0–16 even-length ASCII hex digits;
   when is `always` or `match`. Types are strict; booleans are not integers.
2. Validate all shapes/types/ranges first, returning `{"error":"shape","at":-1}`.
   Decode bytes; all positions refer to the original input, never intermediate
   output. In input index order check every patch's at+len(old)≤len(input), else
   `{"error":"bounds","at":I}`. Even potentially skipped patches need bounds.
3. Compare each old to the original slice at its position. `always` must match;
   the first failing always patch yields `{"error":"mismatch","at":I}`. A
   `match` patch applies only on equality, otherwise is skipped. Empty old always
   matches. Bounds for all patches precede every mismatch check.
4. Applied patches must not conflict. Nonempty old spans conflict if their
   half-open intervals overlap. Two empty-old insertions conflict at equal at.
   An insertion conflicts with a nonempty span exactly if span.start≤at<span.end
   (an insertion at its end is allowed). Check applied pairs in lexicographic
   order of original indices (i,j), i<j; first conflict returns exactly
   `{"error":"conflict","at":i,"other":j}`. Skipped patches cannot conflict.
5. Sort applied patches by at, replace each original old span with new bytes,
   preserving all untouched bytes and permitting length changes. Success is
   exactly `{"hex":H,"applied":[I,...],"skipped":[I,...]}`; H is lowercase,
   both index lists ascend by original index, independent of position ordering.
6. Pure deterministic byte work (including byte sequences representing text);
   no files/network/clock/randomness or character decoding. Valid JSON with
   unique object keys and request≤16 KiB UTF-8 are transport preconditions.
   Original bytes≤32, patches≤16, output bytes≤160. Error output has no state.
