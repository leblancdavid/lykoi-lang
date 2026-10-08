# R6.6 adversarial specification challenge matrix

**All entries are NOT_RUN.** C = complete declared outcome within the bounded
candidate specification; I = incomplete for the broader capability; U = unresolved
semantic/integration obligation. C is neither implementation coverage nor proof.
Inputs refer to [witness formats](COMPOSITION-WITNESSES.md); limits and precedence
refer to [definitions](CANDIDATE-SEMANTICS.md). Text offsets count actual ASCII bytes.

## Cross-domain challenges: 27 cells

| Challenge | A: CFG66 | B: DSV66 | C: BXC66 |
| --- | --- | --- | --- |
| Empty input | C: success, zero assignments. | C: success, zero records. | C: header truncation at EOF 0; explicit zero-entry container succeeds. |
| Malformed encoding | C: first byte >=128 rejects ENCODING before syntax. I: Unicode interpretation absent. | C: same ASCII policy; invalid high byte inside quotes still ENCODING. I: Unicode absent. | C: high-byte content valid; high-byte name rejects NAME at that byte. No text decoding of entire container. |
| Truncated input | C: `x=1` rejects mandatory LF at EOF 3; open string rejects at EOF. | C: `a,b,1` rejects LF at EOF 5; open quotes reject at EOF. | C: exact Take/atoms reject at actual EOF; never zero-pad or recover a partial manifest. |
| Ambiguous alternatives | C: disjoint value selector; duplicate/overlapping selector is plan refusal. I: arbitrary ambiguous grammar not admitted. | C: opening quote vs unquoted is factored; after quote, quote vs delimiter disjoint. I: overlapping alternate escape policies refused. | C: version 1 only; same-prefix version branches require factoring. Unknown version rejects at byte 4. |
| Nested structures | C: brace/bracket syntax rejects in value position at its first byte. I: no recursive CFG66 values. | C: nested-looking characters inside field are literal, not structure. I: no embedded record grammar. | C: content containing a container is opaque bytes. I: recursive archive interpretation not derived. |
| Duplicate fields/keys | C: duplicate name rejects at second-name start, no last-wins. | C: unique key rule rejects second occurrence, order retained. | C: exact duplicate names reject after trailer validation at second-name start, no normalization. |
| Invalid lengths | C: name/string/row limit rejects before growth; decimal overflow at first excessive digit. No declared binary length field. | C: key >32 or label >256 rejects bounds; wrong column count rejects separator/LF at offending byte. | C: name length 0/>32, count >8, content >1024 reject at length atom start before Take; echo/trailer mismatches reject at their atom starts. |
| Resource limits | C: input 4097 rejects INPUT_LIMIT at 4096 before ASCII; ninth assignment rejects occurrence bound at its start. | C: same input/record limits; work/output limits checked before growth; transformed quantity >1000 rejected on final revalidation. | C: input/output <=4096; oversized declared payload rejected before allocation; output selection/reassembly rechecks all limits. |
| Conflicting validation | C: ordered `present` then `absent` rules on same field cannot both succeed; first false wins after syntax. | C: `q<=10` then `q>=20` is never relaxed; q=15 fails first rule. | C: if a supplied policy requires a name both permitted and forbidden, ordered checks reject first false; container integrity does not override policy. |

Scope choices are specified rather than unresolved: ASCII-only text, required LF,
no recovery, structural integrity only, and refusal of ambiguous/recursive grammars.
They are incomplete for broader Unicode/general-grammar/archive goals; a claim
covering those goals would require more semantic evidence.

## Candidate-level attacks

| ID | Attack | Determinate response / remaining obligation | Status |
| --- | --- | --- | --- |
| X01 | Repeat an empty literal indefinitely | Plan refusal: successful repeat body must consume >=1. Conservative structural progress analysis may reject some safe plans; not all termination proofs required. | C |
| X02 | Left recursion or cyclic grammar call | Plan DAG check refuses. Acyclic nesting plus consuming bounded repetition terminates under logical budget. | C |
| X03 | Choice selectors `a` and `ab` | Prefix overlap refuses plan; Seq(common `a`, Choice(`b`,...)) requires an explicit remaining-input policy. No implicit longest match. | C |
| X04 | Negative/dynamic oversized Take length | Reject BOUND at referenced length site before read/allocation. Integer overflow cannot wrap cursor; checked mathematical comparison then advance. | C |
| X05 | Future or shadowed binding used as count | Plan refusal, not runtime name lookup. | C |
| X06 | Decode accepted noncanonical spelling | `007` decodes 7; encode emits `7`. Byte identity is not the promised law. Decode(encode(v)) equality applies to semantic values, not original spans. | C |
| X07 | Two false checks at same location | Declared check order determines error ID; no merging of contradictory rules. | C |
| X08 | Bad ASCII plus earlier syntax error | Whole-input ASCII check wins even if high byte is later. Explicit preflight policy avoids backend-dependent ordering. | C |
| X09 | Truncated BXC payload whose length exceeds bound | BOUND precedes truncation because length check is immediate; never read unbounded content. | C |
| X10 | Change FF to FE without changing lengths | Accepted container under structural-integrity contract. Integrity/authentication of arbitrary content is not supplied. | I |
| X11 | Small fixed-depth nested plan | DAG of records can recognize two nested levels; depth limit rejects before deeper entry. Output must flatten into explicitly typed records/references. General recursive AST binding remains unsupported. | C / I |
| X12 | Exhaust work budget during lookahead | Same logical charged-action prefix must yield same WORK_LIMIT independent of machine speed. Abstract metric fixed; backend optimization equivalence unproved. | C / U |
| X13 | Codec name resolves to installed library | Refuse unknown descriptor. Library identity cannot supply unspecified variants, escaping, errors or authority. | C |
| X14 | Decoder declares file destination/executable hook | Refuse effectful plan/codec. Parsed names never grant K20 authority. Physical materialization separate. | C |
| X15 | Dynamic decoded rows persisted as general nested bytes | Pure typed results specified; current normal profiles do not admit all byte/result shapes or arbitrary profile unions. No automatic persistence coverage. | U |
| X16 | Larger document split into accepted chunks | Each call only promises its own full-input contract; chunking is not equivalent without explicit framing/ordering/duplicate/budget policy. Streaming composition not derived. | I |

## Assessment

All 27 format/challenge cells have determinate bounded outcomes. Several also
disclose wider unsupported scope (Unicode A/B, ambiguity A/B, nesting A/B/C).
X01–X16 expose the precision and remaining
boundaries; mixed C/I/U labels are intentional. No percentage, behavioral score,
minimality theorem or held-out evidence is inferred from designed examples.

The candidate is specification-supported for these finite acyclic grammars and
explicit atomic relations. General deterministic interpretation, recursive grammars,
cryptographic integrity and actual Lykoi result integration remain unestablished.
