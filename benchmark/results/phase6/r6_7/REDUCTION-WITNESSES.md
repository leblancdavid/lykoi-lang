# R6.7 witnesses, failed reductions and counterexamples

All arguments are informal specification reasoning; **NOT_RUN**. Exact equivalence
would preserve value, bytes/order, extent, error stage/code/node/site/expected,
provenance and limits for every admissible P,C,L,x. The witnesses below explicitly
state weaker equivalence. No opaque parser, codec, int(), slice(), join() or callback
is admitted to complete a missing step.

## Positive and conditional witnesses

**W01 — construction/identity.** Given typed earlier bindings a,b, K01/K02 declare
fields, K04 supplies bindings and K05 supplies constants; ordinary record construction
returns `{a:a,b:b}` without computing a slice, ordinal or span. Identity returns
supplied Bytes unchanged once that representation is admitted. Profile extension is
required; this is a value-meaning witness, not a current serialized program.

**W02 — End predicate.** Given integer cursor i and finite B, K18 returns n=|B|,
K06 computes i=n, and ordered K17-bound validation rejects otherwise. This derives
full-consumption truth. It does not derive i, the parser-specific error envelope,
node ID or charging for End. Those cannot be inferred from the predicate.

**W03 — finite literal relations.** For CFG escapes use disjoint spellings
backslash-quote, backslash-backslash, backslash-n: each Literal success projects
the appropriate quote/backslash/LF K05 literal. For DSV an already recognized
double quote maps to one quote. For keywords, Literal(true/false/none) projects
Boolean/explicit absent. E maps the finite escaped characters to their declared
canonical spellings; all permitted plain characters copy through a separate identity
branch. ASCII has 128 entries b→U+b. Finite tables plus equality/selection/projection
can express these scalar relations on supplied atoms; Choice supplies recognition
where admitted. Combining characters requires traversal/join. An exhaustive ASCII
Choice must respect prefix length/node/descriptor accounting; no ≤64-node exact
plan is claimed. These are finite value-relation reductions, not cost equivalence.

**W04 — decimal substep.** Given integer accumulator a and digit d, form
t2=a+a, t4=t2+t2, t8=t4+t4, t10=t8+t2, next=t10+d using five K24 adds.
For a≤32767,d≤9 all intermediates are signed-64 safe; compare next≤32767
with K16 before retaining it. This derives one decimal step. K12 is pointwise,
not an accumulator; RepeatUntil returns occurrences rather than recurrent state.
Without a newly specified recurrence and digit-to-integer view this is not D.
Canonical E requires inverse place-value emission, also not derived. Huge finite
tables are extensionally possible under global bounds; no admissible compact
table, prefix-overflow error witness or cost law is furnished.

**W05 — UInt subrelations.** Bytes is declared an integer sequence, so UInt8's
arithmetic is identity *if* singleton element observation/construction is supplied.
Take(1) only returns a sequence; neither K18 nor map supplies scalar extraction.
Given b0,b1 in 0..255, define a0=b0, a(r+1)=ar+ar for r=0..7, then v=a8+b1.
Eight doubling nodes plus one add yield 256b0+b1; maximum 65535, safely within
signed-64, and nine arithmetic nodes fit a 16-node graph even with explicit source
bindings. Byte-acquisition/normal-path context remains prospective. This reduces
numeric D only. E would need high=floor(v/256), low=v−256high and construction;
division/remainder/dynamic subtraction are not admitted by naming them. Finite
threshold tables remain an uncompleted alternative, not an impossibility result.

**W06 — Literal via Take is not error-equivalent.** Let literal=[61,62], input=[63].
Literal rejects mismatch at 0; Take(2) first rejects truncation at EOF 1. Take then
equality only agrees on accepted bytes. Bytewise recognition could repair it, but
requires observation, ordered site checks and a new trace.

**W07 — flattening/inlining is not full elimination.** Seq(Seq(p,q),r) and
Seq(p,q,r) can return the same values. Removing a Seq node entry changes work and
active depth; inlining Atom can change rejecting node identity. An unchanged L can
distinguish them. Treating the old entries as ghost steps requires a specified trace
translation, not a silent optimization. Existing staged ordering does not itself
thread parser cursors.

**W08 — ScanClass sketch.** Consume first byte from first-class; repeat consuming
one continuation byte until disjoint stop/EOF; K18 verifies min/max; concatenate raw
contributions. For min=0 an initial stop must bypass the first-byte step. At max,
inspect next byte to distinguish stop from excess continuation. The algebra lacks
a general single-byte class projection/negative selector and exact failure/charging
rules for this replacement. Value-level factoring is plausible but incomplete.

**W09 — Take attempt.** RepeatCount(byte-read,k) plus byte joining constructs k
bytes if byte-read exists. It introduces different entries/costs and must preserve
pre-read bound errors and EOF site. Kernel selection over supplied rows can filter
an interval only after indices/cursor-relative interval are supplied; supplying those
is the missing raw access. Counting a sequence cannot slice it.

**W10 — lookahead attempt.** K06/K09 can discriminate a *supplied* prefix.
Choice supplies that prefix without consuming it; existing predicates do not.
Replacing Choice by trial parse changes failure/extent and violates no-backtracking.
Longer finite tries need a normative byte-examination order.

**W11 — repetition circularity.** RepeatUntil cannot become RepeatCount unless
the occurrence count is known. Computing that count by parsing reinstates RepeatUntil
and changes first-error/work order. RepeatCount cannot become RepeatUntil because
stop is a byte-prefix/EOF selector, not an ordinal/environment predicate. Static
unrolling tiny fixed counts adds dispatch/graph size and does not derive dynamic
counted traversal. K12 over a supplied k-element sequence needs its construction
and cursor threading first. DAG acyclicity is not a substitute for either meaning.

**W12 — assembly factoring.** On supplied S, K12 applies a specified layout body
to each item, returning ordered pieces; Seq-concatenate joins them. Constants and
identity copies then need no separate value-transform meanings, but joining remains.
`[[a],[b]]` is not `[a,b]`. Reassociation can change work/depth/output failure
identity; exact trace laws are open. No automatic inverse of parsing is claimed.

**W13 — length/trailer.** K18(B) → integer count, explicit range validation → E(count)
is a length prefix. For BXC prefix P, K18(P) and K24(count,2) → UInt16BE E form the
trailer. The prefix must be bound once as an immutable value; computing its length
does not license hidden double assembly/copying. Limits/representation units matter.

**W14 — validation/uniqueness.** K12 project keys S, K13 stable_unique(keys),
K18 both, K06 equality derives duplicate-free truth without altering S. Ordered
validation evaluates check IDs in source-declared sequence, first false wins.
Conjunction computes truth but is not an error-order witness by itself.

**W15 — localization condition.** For current r_i and supplied prefix S[0:i],
K12 projects earlier keys, K09 checks current key membership; ordered validation
rejects the first duplicate using current raw name span. The prefix and ordinal
are I-BOUND inputs claimed in 0.1 but lack a node/trace constructor. Deriving them
from parser traversal or an indexed prefix pass needs explicit meaning, not map
callbacks. Duplicate *truth* is kernel-derived; first duplicate *site* is conditional.

**W16 — positions.** Given checked start/end cursors, pair them into [i,j) using
record construction. For emitted contributions c1…cm, hypothetical offsets are
o0=0, o(t+1)=ot+K18(ct) via K24; ranges [ot,o(t+1)) associate layout/field IDs.
This is a compositional recurrence, not an admitted fold. Similarly map each plain
character to its source byte and each escape output to its initiating byte, then
join/rebase contributions. DSV later conversion needs composition of local decoded
indices with this map. New traversal/binding interfaces are necessary; no reason
yet to declare an additional irreducible SourceLocation primitive.

**W17 — work.** 0.1 charges node entry, each examined/copied byte and extra digit
processing. It does not exhaustively identify events for preflight, tables, checks,
prefix building, provenance or assembly. Matching numerical weights cannot prove
same WORK_LIMIT result until an ordered event trace is specified.

## Counterexample inventory

| ID | Input or demand | First failed obligation |
| --- | --- | --- |
| CE01 | Literal=[61,62], input=[63] versus Take+equality | mismatch at 0 versus EOF 1; W06 |
| CE02 | UInt16BE versus two UInt8+nine adds under tight L.work | numeric equality does not preserve trace/rejecting node; W05/W17 |
| CE03 | nested versus flat Seq at tight depth/work | constructor elimination changes resource outcome; W07 |
| CE04 | DSV `a,b,x` LF followed by malformed `c,"d"x,1` LF | whole-document structural rejection must precede early quantity conversion; inline Atom violates policy |
| CE05 | CFG `count = 007` LF → `count=7` LF | semantic integer retained, source spans differ; full result round trip false |
| CE06 | encode CFG ASCII text containing TAB/CR/NUL | declared ASCII type exceeds grammar's representable domain |
| CE07 | encode DSV quantity 1001 or string containing LF | integer/ASCII typing alone exceeds final/lexical domain |
| CE08 | eight BXC entries each with content length 1024 | local field bounds do not establish aggregate 4096 output bound |
| CE09 | BXC high-byte name with ASCII-before-membership | ENCODING from codec versus format NAME; error order/translation absent |
| CE10 | L.input=16, input length 17 | fixed offset 4096 conflicts with a variable limit interpretation |
| CE11 | DSV quoted `"32768"` quantity | overflow site must map local digit index 4 to raw field byte start+1+4; second-pass invocation/map composition missing |
| CE12 | BXC FF→FE with unchanged lengths | accepted by design; arbitrary integrity is outside scope |
| CE13 | two accepted text chunks each containing same key | global duplicate rejection lost; chunking not a reduction |
| CE14 | min=0 ScanClass at initial stop, or exactly max before continuation | optional-empty/max lookahead rules and charged actions need fixing |
| CE15 | fixed-depth nested output or non-ASCII bytes C3 A9 | flattening type/depth trace unresolved; UTF-8 text outside ASCII scope |
| CE16 | eight DSV rows with distinct 32-character unquoted keys, quoted 248-character labels containing 223 quotes, quantity 1000 | each raw row is 32+(248+223+2)+4+3=512 bytes, total 4096; canonical quoting keys adds 16 bytes, violating 4096 output bound |

CE02/CE03 identify distinguishing trace possibilities, not measured budgets. Exact
numerical cutoffs cannot be inferred from an incomplete event model. All are
specification counterexamples/pressure, not behavioral failures.
