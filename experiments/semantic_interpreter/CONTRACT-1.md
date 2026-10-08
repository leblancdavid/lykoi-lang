# R6.10 experimental semantic-plan-1 contract

This is an executable research refinement of R6.6 0.1, not an admitted Lykoi
profile. Frozen definitions and witnesses remain authoritative for format behavior.
Implementation: `interpreter.py`. Plans: the three `*.plan.json` files. The builder
only authors those files; the interpreter neither imports it nor dispatches on a
format name. Python 3.10+, standard library only, provider-neutral.

## Plan and value domains

The root has exactly `version`, `text`, `rules`, `decode`, `encode`. Rules are
closed acyclic structural definitions, with no arguments or captured environment.
Every structural node has a unique stable `id` and an `op`. Rule references share
definitions; definitions, call sites and unused definitions count toward 64 nodes.
The published plans have **53 / 39 / 31** nodes respectively. Static structural
depth is at most 16; the runtime limit includes rule invocation depth. Repetition
requires a conservatively consuming body. Dynamic Take is conservatively zero
progress; a surrounding positive literal/atom can establish progress.

`semantic-plan-1.schema.json` closes shapes recursively. `validate()` is the
authoritative executable validator for shape, byte classes, dependencies, progress,
selector disjointness, graph size and DAG checks. JSON Schema alone cannot express
these graph properties. No dependency resolution uses files or installed codecs.

Values are exact Python integers (booleans distinct), booleans, ASCII strings,
bytes, records with explicit fields and ordered finite lists. `Cell` transports
each value with half-open source span and character-origin tuple. A CFG row uses
`{name,value:{kind,present,...}}`; this is a tagged representation of the frozen
row, with spans in the separate provenance envelope. Missing tagged fields are
absent, never fabricated nulls. Semantic round-trip projection removes provenance.
There is no coercion of strings/floats/bools to integers.

**Typing limit:** construction expressions determine value types but do not carry
a complete statically checked record/union type declaration. Earlier base bindings
are checked statically; every dotted field projection is not proven statically.
Bad field/type combinations fail with TYPE and publish no partial result. Thus
this is a partial prototype of the fully typed R6.6 plan judgment.

## Structural operations (explicit contracts)

| Operation | Inputs, result and failure |
| --- | --- |
| literal | Exact declared bytes at cursor; first mismatch uses declared code (default SYNTAX), shortage TRUNCATED at EOF. Optional literal projection has the consumed span. |
| scan | Positional first/rest byte classes and disjoint stop; maximal consuming scan, min/max checked before growth. Stop is not consumed; EOF stops only when declared. Returns raw bytes/origins. Optional decimal15 codec interprets each digit immediately, including first-prefix overflow. |
| take | Literal/earlier integer length, bounded before read; exact contiguous bytes. Optional declared membership class checks each byte immediately. BOUND uses length source start; bad membership uses offending byte; truncation uses EOF. |
| atom | Only fixed UInt8/UInt16BE; raw reading followed by explicit numeric decode. |
| seq | Ordered steps, local fresh bindings, absorbing failure; result expression. Optional span_end uses an already-bound value's end (CFG excludes trailing spaces/LF). Optional explicit rebase_errors moves listed errors to sequence start (escape initiator). |
| choice | Ordered finite prefix comparisons, disjoint/prefix-free selectors; one branch, no backtracking. Prefixes <=8 bytes. Unmatched input uses declared code, unmatched EOF TRUNCATED; expected spellings sorted in result. |
| repeat | Stop-prefix/EOF or prior-count controlled repetition. Stop is unconsumed. Explicit max and occurrence_limit flag; top-level records use occurrence budget, lexical contribution lists use their declared bound. Count bound checked before body; body must consume. |
| call | Evaluate one declared rule in an empty environment, sharing the cursor. Cycles and unknown rules refused. |
| end | Cursor must equal supplied input length; otherwise TRAILING. |
| value | Evaluate one closed expression and transport its value/provenance. |
| check | Ordered Boolean predicate; true succeeds, otherwise declared error at declared source Cell start. No implicit reorder or repair. |
| map | Ordered finite pointwise application of an explicit node body. Body sees item and explicit inclusive earlier-occurrence prefix. |
| select | Ordered finite supplied sequence, explicit predicate; retain only true occurrences without reordering. |
| unique | Ordered prefix comparisons of explicitly named field; exact duplicate fails at second field start. Never overwrites or silently deduplicates. |
| bytes_check | Explicit per-byte finite membership validation of supplied bytes; first bad byte rejects. The shipped BXC plan uses checked Take instead. |
| emit | Explicit codec/canonical escape table produces ordered private byte contributions; output bound is checked before each append. |
| each | Ordered supplied finite sequence -> explicit layout body; no arbitrary function. |
| dispatch | Explicit value/tag selection among declared layouts; unknown tag TAG. Boolean discriminants select canonical keys True/False. |

## Closed expression contracts

`ref` projects earlier bindings/fields; `const` supplies a typed literal (bounded
ASCII-producing uses are checked at encoding); `record` constructs explicitly
named fields; `decode` applies a closed codec to a supplied lexeme; `join` joins
ordered raw/decoded character contributions, preserving origins, <=256 characters.
`length` observes cardinality of a supplied value; `nonempty` is length>0;
`eq` uses exact same-type equality; `le` compares same-type integer/string values;
`add` is checked signed-64 addition. `input_length` observes supplied input extent;
`output_length` observes the currently private assembled prefix. There are no
expressions for host calls, modules, file paths, subprocesses or provider services.

## C-ATOM contracts

| Codec | Decode / encode | Malformed/overflow |
| --- | --- | --- |
| ASCII | Byte b<=127 -> U+b; inverse pointwise, no locale/newline normalization | First high byte ENCODING; whole text preflight precedes syntax. Arbitrary BXC content bypasses ASCII. |
| finite escapes | Structural Literal/Choice + literal scalar contributions; joining supplies string. E uses explicit finite char->spelling table, <=8 ASCII bytes per spelling | CFG undeclared escape ESCAPE at initiating backslash. DSV doubled quote maps to first quote's byte. Recognition is visible in plans. |
| Decimal15 | Digit recurrence v=10v+d, 0..32767; inverse repeated div/mod 10, minimal spelling, zero=0 | Empty/non-digit DECIMAL, first excessive digit OVERFLOW. CFG converts while scanning; DSV converts after complete structural parse and rebases each digit through origins. |
| UInt8 | b <-> integer 0..255 | Fixed atom shortage TRUNCATED; wrong encode type/range ENCODE_RANGE. |
| UInt16BE | 256b0+b1 <-> two bytes div/mod 256, 0..65535 | No wrapping/padding; truncation at actual EOF; wrong encode domain ENCODE_RANGE. |
| bytes | Exact identity/copy | Non-bytes TYPE; byte layout/append remains an I-BOUND meaning. |

## Error precedence and bounded execution assumptions

Preflight: invalid plan/limits/input type -> plan_reject; oversized input ->
INPUT_LIMIT at configured first excluded byte; whole textual ASCII check; decode
in plan order; declared final conversions/checks; optional layout. Within execution:
next charge -> depth -> occurrence/growth -> read/check. Rejections expose only
status/error/work; no successful prefix, values or bytes. Decode success includes
consumed; layout has no separate consumed field. Encode error offset is null for
encode stage; its path currently identifies only `value`/`tag`, an unresolved
field-path obligation. Limit errors during assembly still use source cursor/node.

The following are **R6.10 experimental assumptions**, not an assertion of exact
R6.6 cost conformance. R6.7 correctly identified insufficient event precision:

1. Each node entry and expression evaluation costs 1. Text preflight costs 1 per
   byte. Literal/read/scan costs 1 per examined byte, including a scan stop byte.
   Lookahead costs 1 for each actually compared byte; EOF observation costs 0.
   Selectors are checked in declared branch/prefix order, so costs are deterministic.
2. Decimal scanning adds 1 per interpreted digit; delayed Decimal conversion costs
   2 per character (examination and interpretation). Unsigned decode adds 1 per
   supplied byte. ASCII conversion costs 1 per byte; ASCII emission preparation
   costs 1 per character; decimal inverse costs 1 per emitted digit.
3. Successful repeat append costs 1; join costs 1 per contribution plus ASCII
   conversion where required. Unique costs 1 per current occurrence plus 1 per
   earlier comparison. Explicit byte membership validation costs 1 per byte.
   Selection append costs 1. Output append costs 1 per byte, before output bound.
4. Record metadata, map prefix snapshots, integer host arithmetic, pure source-span
   transport and copying bounded private buffers have no *additional* charges.
   Their surrounding nodes/expressions/bytes are charged as above. Their physical
   allocations/time are not this semantic metric. This convention needs a later
   cost-preservation experiment and is not a reduction proof.

Before a charged event exceeding the declared work limit, WORK_LIMIT returns the
already-consumed count and the charged event's site. Node depth is checked after
entry charge. Defaults: input/output 4096, work 100000, depth 16, records 8. User
limits may only tighten defaults. Max expression visits in validation 2048;
literal bytes <=4096, classes <=256, literal strings <=4096, signed-64 literals.
Plans are supplied in memory; loading/validation cost is outside execution work.

DSV checks execute per row: key nonempty, uniqueness, representation bounds,
quantity<=1000. Representation-bound check placement is an explicit assumption
where frozen type-bound failure precedence was incomplete. Quantity conversion
of the entire structurally valid document precedes these checks. Lexical fields
are bounded to 256 characters, with key<=32 checked after conversion.

Determinism is tested for values/errors/sites/work/bytes/provenance. No time, locale,
randomness, OS path semantics, AI, network or process observation is used by the VM.
Python byte/string/int behavior realizes the explicitly stated relations; native
stack/allocator failures and hostile caller mutation/concurrent execution are not
qualified. The interpreter is a pure data API, not an OS sandbox.
