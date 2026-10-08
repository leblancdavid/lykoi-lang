# T4 staged change — Absence-conditional replacement

1. Retain every base obligation; add `absent` to when. Shape validation accepts
   it, and bounds are still checked for every patch before any match decision.
2. An absent patch applies exactly when old differs from the original slice;
   equality skips it. If applied, it removes len(old) original bytes and inserts
   new, just like any other applied patch. This does not raise `mismatch`.
   Empty old consequently always skips for absent.
3. Existing mismatch precedence, conflict detection, original-coordinate assembly,
   index ordering, output shape and resource/environment rules all remain intact.
