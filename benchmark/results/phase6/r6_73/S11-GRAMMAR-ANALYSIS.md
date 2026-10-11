# S11 grammar-dead-end diagnosis

The cause is established for the saved S11 token path by a CPU-only replay using
the original R6.68 decoder and pinned R6.52 tokenizer. See
[exact transitions and token enumeration](qualification_2/S11-CPU-ANALYSIS.json).
R6.72's first failure remains unchanged and unscored.

The historical prefix after 35 tokens is:

```json
{"id":"selected","type":"Bool","deps":["snapshot","snapshot"],"node":{"op":"value","expr":{"add":[{"ref":"snapshot"},{"ref":"snapshot"}]}}
```

The regex at decoder.py lines 10–12 accepts zero, one or two dependency strings,
without uniqueness constraints. `accepts` returns `(True, False)` immediately for
partial regex matches at lines 37–38, bypassing terminal validation. The duplicate
array is therefore admitted, along with every later incomplete prefix.

At the saved prefix the regex has consumed both operands, the expression close
and node close; only the outer `}` remains. That token **exists** in the pinned
tokenizer (ID92). Adding it yields a complete regex match but the unchanged R6.65
structural checker rejects with `SHAPE` at `$/action/deps`: at most two distinct
strings required. Every one of the 94,366 admitted ASCII token pieces fails to
produce an accepted next state. EOS is not offered because the prefix is incomplete.
The original mask's `assert allowed` raises `GRAMMAR_DEAD_END`.

This is a **prefix/completion consistency defect**: regex-partial viability is
weaker than coaccessibility in the actual terminal-validated language. The state
is reachable under the prefix recognizer but has no valid completion. Token-mask
construction faithfully reflects that inconsistent recognizer; it is not a missing
closing-token or logits error. Decoded-prefix and concatenated singleton-token text
agree at all 35 saved transitions. The 128-token budget is not exhausted. add/Bool
is structurally admitted by design; no operation/type semantic check caused this
halt. No hidden model reasoning is observed or causally attributed.

A local unique-dependency serialization completes under the unchanged checker.
This is an **unscored CPU control**, not a repaired R6.72 response or successful
semantic action: its original add/Bool binding remains semantically inconsistent.
The full prefix recognizer would also be susceptible to other late-only terminal
restrictions; this analysis establishes this failure's duplicate-dependency cause,
not a global completeness theorem about the historical decoder.

The new compact completion language enumerates complete **syntax-only** decisions
from the input scope: all operations, ordered references/literals and zero/one/two
distinct dependency choices. Prefix acceptance means being a prefix of one such
complete serialization. No requirement, expected decision or acceptance fixture
enters the grammar. Incorrect operations, distractors, reversed operands and wrong
dependency sets remain selectable. Duplicates are excluded before entering a dead
state, and full decoded token sequences are used for mask membership.

CPU qualification covers 1,734 complete decisions in five languages, 47,517
token-prefix observations, three exhaustive full-vocabulary mask states and
[19,500 distinct nonterminal prefix extension witnesses](qualification_2/PREFIX-EXTENSION-CONTROLS.json).
Each witness has a pinned single-character token whose full appended decode advances
to another valid prefix. Complete states offer EOS only. This qualifies this finite
scope-bounded mechanism; there was no generation, participant inference or model load.
