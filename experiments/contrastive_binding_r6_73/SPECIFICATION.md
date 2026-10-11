# Compact semantic decision, version r6.73-decision-1

One exact JSON object: `{"op":"le","left":{"ref":"used"},"right":{"literal":{"type":"Int64","value":0}},"deps":["used"]}`.
`op` is add/le/eq; left and right are ordered operands. An operand is exactly
`{"ref":"identity"}` or `{"literal":{"type":"Int64|Bool|Unit","value":...}}`.
Int64 excludes Boolean/float and is signed 64-bit; Bool is a JSON Boolean;
Unit is null. No coercion, aliases, extra keys, repeated JSON keys, NaN or floats.
Dependencies are zero to two distinct strings in canonical sorted order.
Duplicate operand references are legal; duplicate scope identities are ambiguous
and reject. Literal values must exist with exact host type in the immutable scope.

The authoritative R6.18 expression checker derives types and direct reference
sets from the selected operation and operands. Explicit deps must equal that set;
the renderer never substitutes the derived set. No indirect dependencies are added.
The fixed selected/value envelope and result type are mechanically reconstructed.
The unchanged R6.63 assembly checks the output-type obligation and applies unchanged
validation/expansion. add requires Int64; le requires Int64 and returns Bool; eq
requires matching types and returns Bool. These rules are imported, not reimplemented.

Reference resolution is exact against the pinned scope, with params and prior results
sharing one unambiguous namespace. Wrong but well-typed choices remain untouched.
Schema rejection, semantic rejection, and requirement mismatch are separate stages.
Commutative order remains an exact supervision obligation even if behavior cannot
distinguish a swap. Shared-prefix le/eq can likewise agree behaviorally while being
distinct requirement-derived semantic targets; these are not new behavioral families.

A scope-bounded completion language may enumerate all three operations, all ordered
operand choices and all zero/one/two distinct dependency subsets (including incorrect
ones). It receives no requirement, expectations, result-type filter or acceptance cases.
Prefix membership must mean extension to an actually complete serialization, avoiding
late-only uniqueness filtering. CPU tokenizer transitions use full decoded prefixes;
EOS is admitted only at an exact terminal. This qualifies deterministic token paths,
not live model generation. Semantic validation remains separate from grammar.
