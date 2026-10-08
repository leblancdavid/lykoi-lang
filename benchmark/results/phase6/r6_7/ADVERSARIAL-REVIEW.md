# R6.7 adversarial specification review

All 27 original cells and all 16 original attacks retain execution **NOT_RUN**.
The tables classify specification, not behavior. No frozen cell is overwritten.
Classification concerns the stated local policy; global typing/cost/envelope gaps
apply even to locally fully specified policies. Thus “Fully specified” does not
mean complete operational semantics or proof for every possible L. Mixed wider
capabilities are recorded separately instead of erasing their bounded policy.

F = Fully specified (local policy); P = Partially specified; U = Underspecified;
C = Contradictory; O = Outside the bounded scope. These abbreviations expand to
the owner's categories, not R6.6's original C/I/U. A contradictory **interface**
is identified separately below; not every incomplete format outcome is contradictory.

## 27 cells

| Challenge | CFG66 | DSV66 | BXC66 |
| --- | --- | --- | --- |
| Empty input | F: zero rows at EOF | F: zero rows/empty encoding | F: header truncation at EOF 0; explicit zero container valid |
| Malformed encoding | F: first high byte before syntax; Unicode O | F: same even inside quotes; Unicode O | P: arbitrary payload high bytes valid, name invalid; NAME vs ENCODING order missing |
| Truncated input | F: x=1 rejects mandatory LF at EOF 3 | F: a,b,1 rejects LF at EOF 5 | F: actual EOF on atom/Take, no padding |
| Ambiguous alternatives | F: disjoint prefixes/refusal; general ambiguity O | F: quote/delimiter factoring/refusal; alternate ambiguous grammar O | F: version 1 only/unknown version at 4 |
| Nested structures | F: braces/brackets invalid values; recursive values O | F: printable nested-looking data literal; embedded grammar O | F: nested-container payload opaque; recursive archive O |
| Duplicate fields/keys | P: truth/order/site policy given, prefix constructor incomplete | P: row/rule order given, prefix/map transport incomplete | P: trailer precedes duplicate, prefix/site transport incomplete |
| Invalid lengths | P: name/raw versus string/decoded growth actions incomplete; decimal rule clear | P: columns clear, decoded-field/type/conversion growth precision incomplete | F: name/count/content bound before Take, echo/trailer sites stated |
| Resource limits | P: row/input examples clear, general L/work/output trace incomplete | P: same plus conversion/provenance/normalization costs | P: allocation bounds clear, reassembly/copy/output-range trace incomplete |
| Conflicting validation | F: ordered false check, no weakening | F: q=15 fails q≤10 before q≥20 | F: first false policy, integrity confers no authorization |

This rejects R6.6's blanket “all 27 determinate” as a complete observable-precision
claim while retaining its useful local examples. Finite refusal/ASCII/structural
integrity are deliberate scope choices, not failures of broader capabilities.

## 16 attacks

| ID | Classification | Audit reason | Execution |
| --- | --- | --- | --- |
| X01 | P | empty repeat body refusal clear; conservative progress rules absent | NOT_RUN |
| X02 | F | cyclic graph refused; bounded acyclic termination informally supported | NOT_RUN |
| X03 | F | a/ab overlap refused; remaining-input policy must be explicit | NOT_RUN |
| X04 | P | invalid length before read clear; exact budget/action/site transport incomplete | NOT_RUN |
| X05 | F | dominance/shadowing refusal clear; formal scope judgments still global obligation | NOT_RUN |
| X06 | P | 007→7 canonical law clear and semantic-not-span equality explicitly stated; π/domain incomplete | NOT_RUN |
| X07 | F | check-ID order governs first false, conjunction not error policy | NOT_RUN |
| X08 | P | ASCII-before-syntax clear; WORK_LIMIT during preflight precedence undefined | NOT_RUN |
| X09 | F | oversized length check before attempted truncated payload | NOT_RUN |
| X10 | F | FF→FE accepted with same lengths; stronger integrity/authentication O | NOT_RUN |
| X11 | P | fixed-depth acyclic recognition plausible; flattened result typing/depth trace missing; recursion O | NOT_RUN |
| X12 | U | precise charged lookahead events/current cursor not defined, only intended invariant | NOT_RUN |
| X13 | F | unknown descriptors refused; installed library cannot add meaning | NOT_RUN |
| X14 | F | effects/hooks refused; bytes grant no authority | NOT_RUN |
| X15 | O | arbitrary persistence/profile union outside pure bounded relation; integration still unresolved | NOT_RUN |
| X16 | F | chunking not same full-input contract; streaming O; cross-chunk duplicate counterexample | NOT_RUN |

Publisher classifies X15 as Outside the bounded scope rather than the reviewer's
integration U: both preserve absence of persistence coverage. This disagreement is
retained in DISAGREEMENTS.md. X10/X16 have fully specified negative boundary policies,
with broader capability outside scope; this does not turn prior I into success.

## Additional precision findings

- Candidate section 2's exactly three-field success envelope versus section 5's
  absent encode consumed is a **Contradictory** interface shape unless a direction
  indexed union is supplied. Neither format nor execution is called contradictory.
- Parameterized L.input versus fixed INPUT_LIMIT offset 4096 is **Partially specified**:
  a fixed-limit reading can reconcile it, a caller-variable reading cannot.
- High-byte BXC NAME vs ENCODING is **Partially specified**, not inevitable contradiction:
  membership-first checking or explicit translation can resolve it, but is not declared.
- Bare full-result round trip is **Partially specified**, because X06 explicitly
  limits equality to semantic values. It is not honest to ignore that qualification.
- Normalization growth past output bound is **Partially specified**: DSV can require
  more canonical bytes than raw input. E must reject or V must restrict it.

No percentages, behavioral scores, passing tests or irreducibility theorem follow.
