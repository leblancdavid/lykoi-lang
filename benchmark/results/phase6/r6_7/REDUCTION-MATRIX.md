# R6.7 operation-level reduction matrix

This is the publisher's post-review classification using the owner's labels.
The fuller independent type/failure/attempt inventory is retained in
[reviewer sections 4–7](REVIEWER-JUDGMENTS.md). Witness IDs below refer to
[REDUCTION-WITNESSES.md](REDUCTION-WITNESSES.md); counterexamples there invalidate
stronger claims. Every row concerns specification, execution **NOT_RUN**.

## Meaning of classification

- `EXISTING_KERNEL_DERIVABLE`: the named subrelation has an explicit kernel
  composition witness, conditional on supplied typed operands. This never claims
  that new bytes/result bindings are already accepted in the compiler.
- `CANDIDATE_DERIVABLE`: a stated subrelation composes other candidate operations
  and existing meanings. Unless expressly stated otherwise, equivalence is at
  value/extent level, not budget/error/node/provenance equivalence.
- `INDEPENDENT_MEANING_REQUIRED`: attempts import meaning absent from the reviewed
  admitted algebra; retain it as a semantic obligation. Not a proof against every
  finite-table encoding, alternate algebra or future smaller foundation.
- `REDUNDANT`: an extra primitive adds no required value meaning in these witnesses.
- `UNDETERMINED`: entire operation or exact reduction cannot be decided from 0.1.

Whole-operation precision overrides a successful subrelation reduction. Split
rows prevent a numeric reduction from being mistaken for a full bidirectional codec
reduction. No new construct count is assigned.

Let B be bounded immutable Bytes, A bounded ASCII, i a checked source cursor,
k a bounded integer, V a declared typed value, S an ordered result sequence, and
R the success/rejection envelope. Env binds earlier values only. All node operations
also have the shared work/depth/growth failures whose detailed trace is unresolved.

| Operation / semantic purpose | Inputs → outputs | Local failure conditions | Classification; witness/failed attempt |
| --- | --- | --- | --- |
| Literal: recognize exact spelling | B,i,constant → constant/span,j | first mismatch; EOF shortage | UNDETERMINED; W06 Take+equality loses first-mismatch order |
| Atom: recognizer/codec invocation and binding | B,i,descriptor → V/span,j | descriptor refusal; codec errors | UNDETERMINED; inline relation moves meaning and cost, W07 |
| ScanClass: maximal positional class lexeme | B,i,sets/min/max → B/span,j | neither class nor stop; min/max; undeclared EOF | UNDETERMINED; W08 repetition sketch needs byte/EOF/min/max rules |
| Take: dependent contiguous slice | B,i,k → B(k),j | invalid k before read; EOF | INDEPENDENT_MEANING_REQUIRED; W09 cannot get dynamic slice from selection/cardinality |
| Seq: cursor-threaded dependent order | plans,Env,i → bound V,j | first failure | UNDETERMINED; existing staged composition principle, cursor transport new; W07 flattening alters trace |
| Choice: predictive byte-prefix dispatch | B,i,disjoint trie → branch V,j | plan overlap; unmatched prefix | INDEPENDENT_MEANING_REQUIRED; W10 predicates need prior lookahead |
| RepeatUntil: consuming stop-directed traversal | B,i,body,stop,max → S,j | max before next body; body reject/nonprogress refusal | INDEPENDENT_MEANING_REQUIRED; W11 count acquisition is circular |
| RepeatCount: count-directed traversal | B,i,k,body,max → S,j | invalid count; nonprogress refusal; body rejection | INDEPENDENT_MEANING_REQUIRED; W11 byte stop cannot observe iteration count |
| Record: typed field construction only | literals/earlier bindings → declared record | type/tag/optional mismatch | EXISTING_KERNEL_DERIVABLE; W01, source/ordinal computation excluded |
| End: full consumption predicate only | supplied i,B → Boolean/check | trailing input | EXISTING_KERNEL_DERIVABLE; W02; error attribution/work remains undetermined |
| ASCII scalar map | supplied b≤127 → U+b; inverse | high byte/type/range | CANDIDATE_DERIVABLE; W03 finite recognition/projection; raw access/join separate |
| Whole-text ASCII preflight | B → validated B | first high byte before syntax | UNDETERMINED; ordering declared, examination and WORK_LIMIT scope absent |
| Finite escape scalar table D/E | recognized spelling or character → character/spelling | unknown escape; unmapped encode char | CANDIDATE_DERIVABLE; W03; traversal/join/canonical E required |
| Decimal15 decode/encode | digit lexeme ↔ integer 0..32767 | empty/invalid digit; first prefix overflow; encode range | INDEPENDENT_MEANING_REQUIRED; W04 fixed arithmetic step reduces, recurrent transduction/inverse not derived |
| UInt8 bidirectional byte view | B(1) ↔ integer 0..255 | EOF; encode type/range | UNDETERMINED; W05 identity needs singleton observation/construction interface |
| UInt16BE decode numeric formula | supplied b0,b1 → integer | typed/range precondition | EXISTING_KERNEL_DERIVABLE; W05 nine K24 additions |
| UInt16BE whole decode/encode | B(2) ↔ integer 0..65535 | EOF; encode type/range | UNDETERMINED; W05 raw binding/inverse/cost not supplied |
| Proposed extra Boolean/none codec | recognized keyword → Boolean/absence | boundary/type errors structural | REDUNDANT; W03 literal projection; explicit absent not empty |
| Assembly Literal | declared byte literal → contribution | output/work bound | CANDIDATE_DERIVABLE; W12 constant plus emission/join interface |
| AtomEncode | V,descriptor → canonical B/A | type/range/mapping; output bound | UNDETERMINED; codec relation required, field path rules incomplete |
| BytesCopy exact value | supplied B → same B | wrong type | EXISTING_KERNEL_DERIVABLE; W01 identity; appending not included |
| Seq-concatenate / string join | ordered B/A contributions → B/A | growth/output/work | INDEPENDENT_MEANING_REQUIRED; W12 map returns pieces, not flattening |
| Finite layout occurrence iteration | S,layout → concatenated B | body/aggregate bounds | CANDIDATE_DERIVABLE; W12 K12+join with prospective binding; exact trace unresolved |
| Tag-directed layout Choice | tagged V,branches → B | invalid tag/optional schema | UNDETERMINED; discriminant predicates existing, output branch interface unspecified |
| Presence-directed layout Choice | explicit presence,branches → B | invalid value/schema | UNDETERMINED; K19 observation alone does not emit branch bytes |
| Length-prefix construction | supplied sequence → integer → B | cardinality/range/output | CANDIDATE_DERIVABLE; W13 K18+encoder |
| BXC trailer construction | assembled prefix B → UInt16BE length | aggregate/range/output | CANDIDATE_DERIVABLE; W13 K18+K24(+2)+encoder |
| Ordered decoded validation | typed operands/predicates/check order → R | first false declared check | EXISTING_KERNEL_DERIVABLE; W14 stages, not merging into conjunction |
| Duplicate truth predicate | S keys → Boolean | typed input | EXISTING_KERNEL_DERIVABLE; W14 K12/K13/K18/K06 |
| Occurrence ordinal/earlier prefix | S,current occurrence → ordinal,prefix | bounds/site definition unresolved | UNDETERMINED; W15 missing traversal/projection interface |
| First duplicate location | S,prefixes,name spans → Reject | first repeated exact key | CANDIDATE_DERIVABLE; W15, conditional on explicit prefix supply |
| Raw spans/consumed extent | node start/end cursor → span,j | checked cursor bounds | CANDIDATE_DERIVABLE; W16 cursor pair construction; cursor access is prerequisite |
| Decoded-character provenance and rebasing | atomic contributions/raw spans → index map | invalid composition/site | UNDETERMINED; W16 escape and intermediate-buffer rules needed |
| Output span attribution | layout emission positions/IDs → ranges | path/index/growth | UNDETERMINED; W16 no operational emission trace |
| Success/Reject transport/private failure | typed outcome → observable R | malformed envelope; no partial publication | UNDETERMINED; existing result principles, decode/encode shape inconsistent |
| Limits and atomic work steps | evaluation state,L → next step or Reject | work/depth/occurrence/output | UNDETERMINED; W17 prescribed weights lack complete event trace |

Static DAG validation, dominance, closed descriptors and selector disjointness
are plan well-formedness obligations, not new format operations. Type refinements
are not automatically new constructs. `Unavailable` is a runtime-support boundary,
not a parser rejection. Physical authority/durable commit retain K20–K22; no
reduction here changes them. Kernel K14–K16/K23/K25/K26 supply lifecycle/time/order/
reachability/duration meanings, not missing raw interpretation or unrestricted fold.
