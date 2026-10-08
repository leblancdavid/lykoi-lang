# R6.6 candidate semantic definitions — interpretation composition 0.1

**Prospective research specification only; not an admitted language profile.**
Names below are not kernel IDs. Implemented accounting remains 26. This document
defines a sufficient bounded candidate vocabulary, not a minimum or universal model.

## 1. Derivation boundary and honest accounting

Start from R6.5 matrix A1/A2/A4/A5, B2/B3 and C2. K01–K10/K18/K19
already describe decoded records, finite sequences, bindings, literals, comparisons,
predicates, selection, cardinality and presence. K12 applies an admitted body; it
cannot invent scanning, dynamic slicing, cursor iteration or a decoder. K24 adds
integers, but its 16-node graph is not a decimal scanner. K23 searches supplied
edges; it does not construct a parse tree from bytes.

Attempted reductions and their boundaries:

| Capability | Composition attempted | Finding |
| --- | --- | --- |
| Tokenization | Selection/map over supplied tokens | Requires tokens first; raw sequence access and cursor recognition missing. |
| Lexical meaning | Equality/finite literal table | Works for a finite escape/ASCII table, once a lexeme is recognized. Variable-length decimal meaning still missing. |
| Parsing | Records/references/reachability | Can represent bounded flat results; constructing grammar-directed results is missing. |
| Encoding | Map over typed rows | Pointwise values do not define concatenation or byte layout. |
| Artifact transformation | Selection, typed replacement, map, cardinality | Sufficient for the witnesses after decoding, with new result/byte binding interfaces; not arbitrary byte computation. |
| Failure/validation | Existing ordered stages/predicates/contracts | Reusable after decoding; cursor failure and deterministic limit accounting belong to interpretation. |

Two **candidate semantic families** are proposed:

1. **I-BOUND**: bounded deterministic sequence interpretation and assembly under
   an explicit typed structural plan.
2. **C-ATOM**: explicitly specified finite lexical/atomic codec relations.

These family names are not a claim of two irreducible constructs. I-BOUND contains
independently observable sequence access, dynamic bounded traversal, construction,
concatenation and failure meanings; C-ATOM contains several scalar relations.
Prospective construct accounting must audit those meanings individually. Putting
them under one name cannot absorb them into K17 or prove a small kernel minimum.

S-PARSE and text/archive S-CODEC from R6.5 overlap structurally in I-BOUND.
S-DIGEST is unnecessary for the chosen integrity contract. Byte values refine K03
representation; producing/accessing them is new meaning. Live T-HANDLE, T-PUBLISH
and resource/process adapters are not needed for pure immutable-value witnesses.

## 2. Value and plan domains

`Bytes(N)` is an immutable ordered sequence of integers 0..255, length <= N.
`ASCII(N)` is a string with characters U+0000..U+007F, length <= N; its serialization
is one byte per character, with no locale, normalization or implicit newline change.
Records have declared named fields; optionals carry explicit absent/present facts,
including present empty string. Finite homogeneous result sequences preserve
occurrence order. Heterogeneous choices must project into one declared record schema
with explicit tag and optional fields. No recursive value type is assumed.

Inputs: versioned plan P, immutable input x (bytes for decode, typed value for encode),
explicit limit vector L, and finite codec descriptors C. Output is exactly
`Success(value, spans, consumed)` or `Reject(stage, code, offset, node, expected)`.
This result envelope and byte/span bindings are prospective profile interfaces;
they are not already accepted v0.3 forms. Offset is a zero-based byte boundary,
including EOF at length(x); spans are half-open [start,end). Encode failures use
typed field paths instead of fabricated source offsets. Nothing is externally
published on rejection. Missing runtime support is `Unavailable`, outside this
pure relation, never a fabricated syntax rejection.

P is a finite acyclic graph, at most 64 structural nodes, with uniquely named
bindings and explicit types. Invocation arguments/bodies cannot contain scripts,
callbacks, dynamic code, user-defined recursion, IO or AI calls. A fixed-depth
nested plan is permitted; recursive grammar references and left recursion are not.
Witness budgets: input/output <=4096 bytes, <=8 top-level records/entries,
<=32-byte names, <=1024-byte content, <=256 decoded string characters, active
structural depth <=16, primitive work <=100000. Limits are part of the relation,
not implicit host memory/time settings.

## 3. I-BOUND decode meaning

A judgment `P,n,x,i,env,L => (v,j,spans)` starts at cursor i, uses immutable
already-bound values env and succeeds at j. Nodes mean:

| Node | Formal meaning and typing |
| --- | --- |
| Literal(b) | Consume exactly b. First unequal byte rejects at its position; shortage rejects at EOF. Empty literal allowed outside repetition. |
| Atom(c) | Invoke C-ATOM's declared recognizer and decoder at i; preserve its raw span and typed result. |
| ScanClass(first,continue,stop,min,max) | Consume a byte-class lexeme, with explicitly listed byte sets. First and continuation classes are positional; continuation and stop sets must be disjoint. A byte in neither rejects at that byte; EOF must be declared a stop or rejects as truncation. Return raw bytes and span, enforcing min/max before result construction. |
| Take(k) | Consume exactly k raw bytes; k is a literal or earlier integer binding, 0..declared bound. Check validity before reading; never wrap. |
| Seq(p1,...,pm) | Left-to-right interpretation; later nodes may consume earlier bindings. Failure is absorbing. |
| Choice(selector, branches) | Finite declared byte-prefix selectors, disjoint with explicit EOF selector if used. Select once from lookahead; no trial/backtracking. Otherwise reject at i with canonical expected set. |
| RepeatUntil(p, stop, max) | Before each iteration test explicit stop selector (possibly EOF); if stop, return ordered occurrences without consuming stop. Otherwise reject if count=max, then interpret p. p must consume >=1 byte on every success. |
| RepeatCount(p,k,max) | k is an earlier bounded nonnegative integer; consume exactly k ordered occurrences, including zero. Body must consume >=1 byte. |
| Record(fields) | Build a declared typed record from literals and earlier bindings in a single occurrence. No expression callbacks; unused syntax facts may be discarded explicitly. |
| End | Accept only when cursor=length(x); otherwise reject trailing input at cursor. |

Selectors are finite byte-prefix tries (maximum prefix 8 bytes). Prefix overlap,
including an EOF/empty catchall overlap, is a **plan error**, not grammar ranking.
Prefix factoring permits shared prefixes in Seq; the author must declare branches
after the common prefix. No longest-match ambiguity convention is inferred.
Lexeme recognizers have explicit disjoint continuation and stop classes. This
subset cannot recognize every context-free grammar; ambiguous grammars are refused,
not silently given PEG precedence. Plans are interpreted, not an opaque parser name.

Pure validation stages run between declared structural steps or after decode,
using existing typed equality, membership, cardinality and predicate meanings.
Checks have declared ordered IDs, inputs and error sites; first false check rejects.
A check cannot access a future field or rely on partial failed output. No auto-repair.
Comparing name uniqueness uses cardinality(original) = cardinality(stable_unique)
as a rejection predicate; it does not authorize silently changing duplicate policy.
For error localization an ordered validation pass binds each occurrence, its ordinal,
and the earlier-occurrence prefix as immutable inputs. Compare the current key with
K12-projected prefix keys using K09; first duplicate uses the current span. This
prefix construction is an I-BOUND meaning/interface, not an existing arbitrary fold.

## 4. C-ATOM relation registry 0.1

Each descriptor supplies input domain, lexical boundary, mathematical decode D,
canonical encode E, invalid-input site, bounds and output type. Only the following
relations are proposed here; a new registry entry adds meaning and requires review.

| Relation | D and E | Failure and determinism |
| --- | --- | --- |
| ASCII | D maps byte b<=127 to U+b, pointwise; E is the inverse. | Whole textual input is checked before syntax; first b>127 rejects at that byte. No Unicode replacement. |
| Finite escape table | Map declared byte strings to declared ASCII characters. A: `\\"`->quote, `\\\\`->backslash, `\\n`->LF. B: `""`->quote inside quotes. E uses one declared canonical spelling per character. | Reject undeclared escape at its initiating byte. Non-injective D allowed only with a declared canonical E; no arbitrary table action. |
| Decimal15 | Recognize `[0-9]+` with a declared stop class; D(d0...dm)=sum(dj*10^(m-j)), accepting 0..32767. E is minimal decimal digits (zero=`0`). | First prefix exceeding 32767 rejects at that digit. No signs, whitespace, locale, floats, coercion or wrap. Leading zeros decode but are not retained canonically. |
| UInt8 / UInt16BE | D(b)=b; D(b0,b1)=256*b0+b1. E is unique one-/two-byte representation of integer in 0..255 / 0..65535. | Wrong typed/range input rejects at encode field path; truncated atom at EOF. Endianness fixed. |

Escaped string recognition itself is I-BOUND repetition/choice over raw spans;
unescaping is ordered concatenation of decoded atomic contributions. This joining
meaning belongs to I-BOUND, not an existing map transform. Decimal decoding is
new mathematical meaning here; a host `int()` call would only realize this contract.
Boolean `true`/`false` interpretation is finite literal-to-boolean projection,
derivable from choices and K05; no Boolean codec is needed.

## 5. I-BOUND assembly and transformation

Assembly uses a finite typed **layout**, not automatic inversion of any grammar:
Literal, AtomEncode, BytesCopy, Seq-concatenate, finite occurrence iteration and
tag/presence-directed Choice. Dependencies form a DAG; referenced values are bound
before use. Length prefixes are K18 cardinality followed by C-ATOM encoding.
All outputs remain private until bounds and declared validations pass. Assembly
does not open/write a file. `consumed` for encode is not meaningful and is absent.
The span result maps output ranges to layout/field IDs, not to invented input spans.

Byte copy preserves exact supplied bytes. ASCII text concatenation preserves decoded
characters in order. Record projection/replacement, selection and existing finite
pointwise application of these **now specified** bodies compose K01–K12. Extending
their accepted input/output types is prospective integration, not current lowering
support. Arbitrary fold, string replace, compression, digest, sorting or recursive
tree rewrite is not licensed. C-ATOM can be inlined into an interpreter that has
its arithmetic/transduction meanings; doing that moves the accounting, not removes it.

Required laws (specification goals, not proved backend properties):

- For every admissible typed value v, D(E(v))=v for the explicitly paired layouts.
- For accepted x, E(D(x)) is canonical, and applying this normalization twice is
  idempotent. It need not equal x (leading zeros and whitespace can change).
- Failed decode/validation/encode exposes no successful prefix and has no effects.
- Same P,C,L,x yields the same value or rejection, including order and location.

## 6. Errors, budgets, safety and runtime realization

Preflight precedence: malformed plan/unknown codec/type inconsistency -> refuse plan;
oversized input -> `INPUT_LIMIT` at offset 4096 (first excluded byte); ASCII textual
encoding check -> `ENCODING` at first high byte; then structural evaluation in
declared order; then ordered final semantic validations; then optional assembly.
Conflicting rules are never weakened: both apply in order, and first false wins.
An obviously unsatisfiable contract may receive a static diagnostic, but runtime
precedence is unchanged. Equality/order on predicates retains existing typed rules.

During interpretation each node entry and each examined/copied byte costs one work
unit; scalar codec digit processing costs one additional unit per digit. Stop
lookahead charges each examined byte. Before the next charged action when work
would exceed L.work, reject `WORK_LIMIT` at the current cursor/node. Node entry
checks depth before entry; result append/copy checks output and occurrence limits
before growth. Overlapping limits are checked work, depth, occurrence, output;
then syntax/read/check. Location for invalid bound is the referenced length atom's
start, or the declaring node for a literal; repeat maximum rejection uses cursor.
The logical work metric is normative; optimizations must reproduce its outcome
without host time dependence. Proof of this preservation is outstanding.

Syntax expected sets are sorted lexicographically by byte spelling/node ID; codes
and node IDs are fixed by the plan. No host exception text is semantic output.
UTF-8/UTF-16, normalization, recovery and arbitrary nested recursion remain outside
this registry, not underdetermined interpretations of ASCII input.

Both families are pure: supplied bytes convey **no authority**. K20 remains the
gate for physical acquisition/publication, K17 for contracts, K21/K22 for existing
qualified durable commit; none is widened. Parsed names are data, never paths or
capability tokens. No network/process/environment access, allocator addresses,
clock/ID observation, callbacks or provider services affect this relation.

Runtime support would require checked cursor arithmetic, immutable bounded buffers,
typed record/result bindings, explicit decoder tables, bounded plan evaluation,
deterministic assembly and error/span transport. Generated loops, buffer slicing,
tables, memoization or a library are implementation techniques **only after** they
faithfully realize these definitions. Existing compiler dispatch rejects these new
forms today. Versioned IR/schema/validation/lowering/independent verification and
legacy rejection preservation would be mandatory in a separately authorized round.
