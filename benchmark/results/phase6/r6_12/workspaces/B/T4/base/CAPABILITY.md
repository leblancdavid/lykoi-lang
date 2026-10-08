# T4 base — current production capability assessment

Terminal: `PRODUCTION_BYTE_SLICE_SPLICE_PROFILE_GAP` (static assessment).
No semantic candidate, compilation or acceptance execution; zero repairs.

## Obligation mapping and partial compositions

- Clause 1 and shape precedence in 2: scalar enum/integer type checks and numeric
  range predicates are supported. A request-level collection of exact patch
  records and hex length/syntax validation have no admitted typed input or string
  cursor interface (`predicates.py:19–34,43–96`). This assessment includes all
  malformed shapes, not just the 16 published examples.
- Clause 2: if original byte length and old byte length were already supplied as
  trustworthy decoded integers, checked `add` and `le` could express bounds;
  old-span end and original index can be ordinary fields. The missing current
  binding is deriving those lengths from runtime hex strings/byte sequences,
  then evaluating all patch bounds before mismatches. Cardinality counts existing
  finite entity selections, not the length of an arbitrary scalar string
  (`computation.py:29–51`).
- Clause 3: exact equality, enum dispatch conditions, AND/OR/NOT and original
  operation-before observations are supported. But predicate operands retrieve
  whole literal/field/parameter/stage values, not dynamic original byte slices
  (`predicate_runtime.py:5–11`; `predicates.py:49–96`). `old` equality cannot
  compare a span that no production operation binds. Empty-old logic can be
  represented once the typed length is available.
- Clause 4: **interval overlap is not a missing primitive**. Integer comparisons,
  conjunction/disjunction, equality and explicit endpoint values express the
  nonempty-span/insertion conflict rules. Nominal finite selection can inspect
  decoded patches (`references.py:62–115`). Sorting decoded rows by original
  indices/position is available (`collection_query.py:74–85`;
  `predicate_integration.py:55–110`). Constructing applied pairs and selecting
  the first pair needs additional normal bindings; a Python pair scan would
  compute required behavior rather than transport an observation.
- Clause 5: production mutations replace whole typed fields or append/add/remove
  scalar collection elements (`references.py:216–242`; `mutable_values.py:199–230`).
  They do not splice a variable original-coordinate span into a sequence,
  concatenate untouched regions and runtime new payloads, or hex-encode the
  assembled bytes. Pipeline operations are closed to verbatim, trim,
  stable-deduplicate and validation (`mutable_values.py:51–84`).
- Clause 6: pure deterministic JSON observation cannot be supplied by a Python
  patch processor. A JSON serializer for an actual compiled result would be
  permitted; the missing slice/assembly decisions would remain.

## Snapshot composition diligence

The current conditional-effect profile observes committed operation-before
state; unselected assignments preserve fields, and failure discards the private
candidate (`docs/prewrite-conditional-composition-v1.md:69–105,137–140`). That is
useful for original-coordinate semantics and should not be dismissed merely
because there is no named patch primitive. It does not add byte slicing or
length-changing assembly. Finite enumeration might represent some relations;
this is a bounded current operation/interface assessment, not a proof that
kernel 26 cannot express patches under a different profile.

All 16 base acceptance cases remain unexecuted and are not executed failures.
Task-specific reads followed START.json; GAP.json contains actual elapsed time.
