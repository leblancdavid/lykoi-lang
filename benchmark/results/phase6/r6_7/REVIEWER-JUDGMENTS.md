# R6.7 independent specification reduction review — precomparison judgments

## 1. Verdict and independence disclosure

**The candidate supports a plausible shared, bounded interpretation-and-assembly architecture and useful value-level reconstructions of CFG66, DSV66 and BXC66. It does not yet specify enough to establish exact observable reductions, complete cost-sensitive outcomes, or a minimum construct set. Specification repair takes priority over minimality claims.**

My strongest findings are:

1. **Raw sequence observation, cursor-dependent traversal, joining, provenance construction and assembly are substantive meanings.** Existing map, record, contract and cardinality operations do not supply them merely by being named.
2. **Some scalar relations admit narrower reduction attempts than the candidate discussion suggests.** In particular, UInt16BE’s arithmetic is derivable from checked addition once its two numeric byte operands exist. Acquiring those operands and preserving codec failures and costs are separate obligations.
3. **Cost is insufficiently operationalized for exact equivalence.** Node entries are observable through work limits, so ordinary inlining, factoring and constructor elimination can change outcomes.
4. **DSV66 needs an explicit decoded-buffer invocation and provenance-composition rule.** Its delayed Decimal15 conversion cannot simply reuse a source-cursor atom without that interface.
5. **Assembly is described less precisely than decoding.** Constructor typing, iteration, rejection paths, intermediate buffers, output provenance and charged actions need operational rules.
6. **Round-trip laws require a semantic-value projection.** Full decoded results contain source spans and other representation-dependent facts that canonical encoding does not preserve.
7. **Several adversarial cells have a clear intended policy but an unresolved exact result.** I therefore do not endorse the blanket assertion that all 27 cells are fully determinate under the protocol’s complete observable-equivalence criterion.

### Independence

This is an owner-requested, separated reasoning pass. It is **nonblind, same-platform procedural separation**, not tool-enforced isolation, organizational independence, independent human authorship, or statistical independence.

I inherited `AGENTS.md`, including its prior R6.6 classification and recommendation. The required repository orientation documents also repeat that classification. I have not treated those statements as evidence for my conclusions.

Before returning these judgments, I did **not** read:

- `benchmark/results/phase6/R6_6-REPORT.md`
- `benchmark/results/phase6/r6_6/ARCHITECTURAL-ALTERNATIVES.md`
- `benchmark/results/phase6/r6_6/OPEN-OBLIGATIONS.md`
- Any substantive R6.7 artifact other than the review protocol.

No publisher conclusion was supplied. No further subagent was used.

All language executions, tests, compiler checks and acceptance runs are **NOT_RUN**. I made no file edits and accessed no P6-A05 content. Initial and final `git status --short` both reported only:

```text
?? benchmark/results/phase6/r6_7/
```

That pre-existing untracked directory was not inspected beyond the expressly requested protocol.

---

## 2. Review criterion and classification vocabulary

An exact reduction must preserve, for the same admissible inputs and limits:

- Semantic value and occurrence order.
- Consumed extent.
- Relevant spans and provenance.
- Rejection stage, code, site, node and expected set.
- Encoded output bytes and output provenance.
- Logical budget outcomes.
- The pure failure frame: no successful prefix or physical effects.

Equality of successful values alone is a **weaker reduction**.

I use these classifications:

| Label | Meaning |
|---|---|
| **Existing** | Meaning is already supplied by the reviewed kernel definitions; prospective type/profile integration may still be necessary. |
| **Candidate composition** | A reconstruction using other candidate meanings is identifiable, but exact equivalence may remain unproved. |
| **New meaning** | The attempted reconstruction imports an observation, computation or construction absent from the reviewed existing algebra. This is not an absolute impossibility theorem. |
| **Unresolved** | Missing rules prevent an exact reduction or a complete specified outcome. |
| **C** | The bounded semantic decision and stated local policy are sufficiently determined, subject to the global precision qualifications below. |
| **I** | A broader capability is deliberately unsupported. |
| **U** | A material obligation within the claimed bounded capability remains unresolved. |

A **C** judgment is neither an execution result nor a formal proof. In particular, none establishes budget-sensitive backend equivalence.

### Universal precision qualification

The candidate gives a useful work-accounting outline, but not a complete charged-action semantics. Consequently, **all exact, all-limit equivalence claims retain a global U obligation**, including cells whose ordinary acceptance/rejection policy I mark C.

I distinguish that common obligation from additional cell-specific gaps rather than relabel every ordinary policy judgment U.

---

## 3. Existing-kernel reduction boundary

The reviewed existing meanings support:

- Typed records, fields, bindings, literals and ordered finite sequences.
- Equality, conjunction, complement, membership and selection.
- Trim, finite pointwise map and stable-first uniqueness.
- Cardinality and explicit presence.
- Typed integer ordering and checked integer addition under the later computation profile.
- Existing operation contracts, authority, durability and bounded atomic commit.

They do **not** automatically provide:

- An indexable raw-byte stream.
- Cursor-relative lookahead or slicing.
- Grammar-directed cursor advancement.
- Accumulating traversal over a variable-length lexeme.
- Joining nested output contributions into a string or byte buffer.
- Character-to-source-byte maps.
- A decoder invocation on a newly constructed intermediate buffer.
- Serialization layouts.
- A new mathematical codec because a descriptor names a library.

K17 can state an operation’s required relation; it does not implement every relation that can be written in a contract. K12 applies a defined body; it cannot supply the body’s missing meaning.

### Finite-table qualification

All witness domains are bounded. A sufficiently large table can therefore describe many relations extensionally. This matters to minimality:

- Equality, selection and projection over **supplied typed table entries** can express a lookup relation.
- This does not by itself recognize a variable-length lexeme, find its boundary, select and expose a scalar result, preserve exact failure sites, or match the proposed logical cost.
- The admitted size and construction authority of such tables would need specification.
- A mathematical finite-table argument is not evidence that a ≤64-node plan or the existing normal profile admits that implementation.

Accordingly, I reject both “a finite table proves an exact existing-kernel reduction” and “bounded codecs are absolutely irreducible.”

---

## 4. Decode-node inventory and reduction attempts

Every row below includes a kernel-only attempt and a candidate-only attempt. None of the candidate reductions is established as cost-exact.

| Named operation | Type and success/failure | Kernel-only witness attempt | Candidate-only witness attempt and judgment |
|---|---|---|---|
| **Literal(b)** | Bytes at cursor → matched constant/raw span and advanced cursor. First mismatch rejects there; shortage rejects at EOF. Empty literal succeeds without consumption outside repetition. | Bind a supplied slice and compare it with K05/K06. This loses cursor acquisition and, with whole-slice equality, first-mismatch localization. **New recognition meaning.** | `Take(length(b))` then equality gives only weaker success equivalence: shortage may precede an earlier mismatch. Bytewise recognition can recover mismatch order if byte access, sequential checks and sites are explicit. **Candidate composition attempt; exact reduction unresolved.** |
| **Atom(c)** | Source bytes/cursor → codec-specific typed value, raw span and new cursor; codec-defined failures. | Existing map/contract cannot invent recognition or decoding. A supplied decoded value avoids the task. **New invocation/binding meaning plus the codec’s own relation.** | Inline the codec’s recognizer and transduction where expressible. This removes a wrapper, not the relation; node/work attribution changes. **Wrapper may be compositional; exact cost/location preservation unresolved.** |
| **ScanClass(first, continue, stop, min, max)** | Byte-class lexeme → raw bytes/span. Positional classes, disjoint continuation/stop; invalid byte, EOF policy and bounds can reject. | Select matching bytes from the whole input. Selection loses contiguous prefix extent, first/continuation distinction, stopping behavior and cursor-relative errors. **New meaning.** | First-position dispatch, then bounded repetition of single-byte recognition, with stopping and K18 checks. Needs explicit handling of empty lexemes, EOF and max-plus-next-byte behavior. **Plausible candidate composition; not an exact reduction.** |
| **Take(k)** | Earlier bounded integer/literal and cursor → exactly k raw bytes; invalid bound rejects before reading, shortage at EOF. | K18 observes extent; K10 filters occurrences. Neither constructs the dynamic contiguous interval from a cursor. **New sequence-access meaning.** | `RepeatCount(single-byte read, k)` then ordered byte construction. Requires numeric byte observation and byte joining; per-byte node costs differ. **Candidate composition at value/extent level; exact failure and cost unresolved.** |
| **Seq(p₁…pₘ)** | Typed dependent node composition, left-to-right; later bindings may use earlier results; failure absorbing. | Existing staged pipelines and graph bindings establish ordered composition, but not cursor/result propagation for these new nodes. **Existing composition principle plus new interface.** | Nested binary Seq or flattening into one sequence preserves ordinary values and order. Depth/node-entry charges and node IDs can differ. **Candidate composition; exact reduction needs a trace law.** |
| **Choice(selector, branches)** | Finite disjoint byte-prefix dispatch → one branch’s common typed result; no match rejects at original cursor; overlap is plan refusal. | Predicates can distinguish supplied values, but cannot obtain lookahead bytes. **New lookahead/control interface.** | Enumerated lookahead followed by explicit branch dispatch. ScanClass is insufficient by itself for arbitrary multi-byte tries. Integer/tag-directed dispatch is also not identical to byte-prefix dispatch. **New observation remains; possible internal factoring, exact costs unresolved.** |
| **RepeatUntil(p, stop, max)** | Cursor-dependent bounded traversal → ordered occurrence sequence, leaving stop unconsumed; max rejection before another body; body must progress. | K12 maps a supplied sequence, not an unknown number of source occurrences whose boundaries depend on parsing. **New dynamic traversal.** | Reconstruct with RepeatCount only if the count is already known. Finding that count first repeats the missing interpretation and changes failure/work order. **No noncircular general reduction established.** |
| **RepeatCount(p, k, max)** | Earlier nonnegative bounded count → exactly k ordered body results, including zero; consuming-body requirement and bounds. | K12 over a supplied k-element iteration sequence is an attempt, but constructing that sequence and threading the cursor are missing. **New cursor-threaded repetition interface.** | RepeatUntil cannot directly stop on an accumulated ordinal because its declared stop selector is byte-prefix/EOF based. Adding environment predicates to stop would extend its meaning. Static unrolling can cover tiny fixed counts with extra dispatch. **General exact reduction unresolved.** |
| **Record(fields)** | Earlier bindings/literals → declared flat typed record with explicit tags/optionals; unused syntax facts may be discarded. | K01/K02/K04/K05 and existing explicit record creation support the value construction principle. **Existing meaning/profile integration**, provided no hidden field computation occurs. | Assembly of a record from bindings is compositional. Attaching source spans, ordinal/prefix inputs and computed metadata requires separately specified bindings. **No justification for counting all record construction as new, but provenance is not free.** |
| **End** | Cursor → success iff cursor equals input extent; otherwise trailing-input rejection at cursor. | If cursor exists as an integer, K18/K06 can compare it with input length and K17 can bind rejection. Cursor acquisition is the prerequisite. **Existing check plus candidate interface.** | EOF selector with an empty successful branch and an explicit rejecting alternative/check is a plausible reconstruction. Branch rejection, expected set and extra lookahead/node charges must agree. **Value/extent reduction plausible; exact reduction unresolved.** |

### Decode details requiring repair

1. **ScanClass with `min=0`.** The rule needs to say explicitly whether a stop at the first position succeeds empty, how `first` participates, and whether first-byte rejection occurs before or after a zero-length acceptance opportunity.
2. **Maximum extent.** At exactly max bytes, the next byte must be inspected sufficiently to distinguish stop from another continuation byte. Specify that action, charge and error site.
3. **Count typing and limits.** RepeatCount’s table states an earlier bounded nonnegative count, but its runtime count-limit rejection should be explicit, including count-source site.
4. **Lookahead observation.** “Select once” does not yet fix trie traversal order, bytes examined, repeated inspection, or work attribution.
5. **Explicit rejection.** A general reject constructor is not listed. Some reductions depend on ordered false checks standing in for structural rejection; that substitution needs defined stage/code/expected behavior.

---

## 5. Atomic codec inventory and reduction attempts

### 5.1 ASCII

**Type:** raw byte sequence → ASCII character sequence; inverse ASCII → bytes.

**Success:** each byte ≤127 maps to its corresponding code point, with one-byte serialization and no normalization.

**Failure:** first high byte rejects. For whole textual input, this check precedes syntax.

- **Kernel-only attempt:** a finite 128-entry literal table, equality/selection/projection and K12 can describe pointwise mapping once numeric bytes and iteration are supplied. Missing raw-byte access and string joining remain.
- **Candidate-only attempt:** Take or single-byte recognition plus finite table lookup and joining is a plausible reduction.
- **Classification:** **finite scalar mapping is compositional once its domains are exposed; acquisition, joining and whole-input validation are candidate meanings.**
- **Exact gap:** byte/character representation compatibility, preflight charging, node attribution and output construction are not fully fixed.

For BXC66, ASCII must be applied only to names, not content. Also reconcile ASCII’s `ENCODING` rejection with the format’s promised `NAME` rejection for high-byte names.

### 5.2 Finite escape table

**Type:** declared byte-string spelling → ASCII character; inverse character → canonical declared spelling.

**Success:** CFG66 recognizes quote/backslash/LF escapes; DSV66 recognizes doubled quote. Plain characters require a separate identity/copy path.

**Failure:** undeclared escape rejects at its initiating byte.

- **Kernel-only attempt:** typed literal table + equality + finite selection/projection supports the relation on already recognized atomic spellings.
- **Candidate-only attempt:** Choice of literal spellings, followed by K05 character projection, expresses these small decode tables. Encode can dispatch on a supplied character and emit its canonical literal spelling.
- **Classification:** **candidate composition of recognition and finite literal projection; not an independently demonstrated irreducible codec.**
- **Gaps:** string-character iteration, joining, rejection on unmapped characters, and canonical selection for non-injective tables need exact rules.
- **Cost:** table lookup, Choice and Literal have different charged traces unless a common abstraction is specified.

### 5.3 Decimal15

**Type:** nonempty digit lexeme → integer 0…32767; inverse integer → minimal decimal spelling.

**Decode:** positional decimal value, allowing leading zeroes.

**Failures:** empty/non-digit lexeme according to boundary policy; first prefix exceeding 32767 rejects at that digit.

**Encode:** range/type refusal at a typed field path.

- **Kernel-only attempt A:** finite table of accepted lexemes and values. Bounded input makes this an extensional possibility, but it supplies no compact admitted recognizer, prefix-overflow site, scalar extraction or cost law.
- **Kernel-only attempt B:** given digit values, compute `a′ = 10a + d` using checked additions. Multiplication by ten requires four additions (`2a`, `4a`, `8a`, `8a+2a`), then one addition of d. That arithmetic step is derivable. **Variable-length accumulation is not supplied by K12**, and the existing 16-node graph does not license an arbitrary digit recurrence.
- **Candidate-only attempt:** ScanClass obtains digits, but there is no explicit accumulator/fold among the structural nodes. Repetition yields contributions; concatenation does not evaluate decimal place value.
- **Encode attempt:** integer ordering and subtraction by fixed literals can support bounded decision-table constructions. No compact general quotient/remainder or digit-emission construction is specified.
- **Classification:** **new decimal transduction meaning relative to the admitted compact algebra; absolute irreducibility and minimum status unproved.**
- **Important qualification:** the new part is not necessarily every arithmetic substep. Recognition, recurrent state, canonical emission and prefix failure attribution must be accounted separately.

The descriptor also needs explicit behavior for EOF, non-digit bytes not in the stop set, digit-length bounds, and post-unquoting invocation.

### 5.4 UInt8

**Type:** one raw byte → integer 0…255; inverse integer → one byte.

**Failures:** truncation at EOF; encode type/range failure at field path.

- **Kernel-only attempt:** if Bytes elements already are numeric integers and singleton projection exists, decoding is a representation view. The candidate does not list a general sequence-element projection.
- **Candidate-only attempt:** `Take(1)` provides a one-byte sequence, not explicitly a scalar numeric byte. Finite selectors/literals can express a byte-to-integer table, subject to plan-size constraints.
- **Classification:** **arithmetic identity, but raw singleton observation/construction requires an explicit interface.** Treating it as wholly new arithmetic would overcount; treating it as automatically existing would hide access/construction.
- **Exact gap:** charged atom entry/read, truncation and singleton-to-scalar transport.

### 5.5 UInt16BE

**Type:** two raw bytes → integer 0…65535; inverse integer → exactly two big-endian bytes.

**Decode:** `256b₀ + b₁`.

- **Kernel-only attempt:** once b₀ and b₁ are integers, eight doubling additions produce `256b₀`; a ninth adds b₁. This fits a 16-node graph, and intermediate values remain far inside signed-64 range.
- **Candidate-only attempt:** two UInt8 reads, K24 arithmetic and a binding recover the numerical value.
- **Classification:** **decode arithmetic reduces to existing checked addition; byte acquisition remains candidate-dependent.**
- **Failure discrepancy:** a two-byte atom’s truncation node/site and work trace are not automatically those of two UInt8 atoms plus nine additions.
- **Encode attempt:** a finite mapping over 0…65535 or threshold-based constructions can describe high/low bytes. No compact division/remainder or byte extraction rule is admitted. Adding those as host operations would add meaning.
- **Encode classification:** **unresolved reduction; explicit inverse relation remains necessary unless a complete alternative construction is supplied.**

Decode and encode must therefore be audited separately. A reduction of the numeric decode formula is not a reduction of the bidirectional codec.

### 5.6 Boolean and absent-value projection

`true`/`false` and `none` recognition compose Literal/Choice with K05 typed values and K19-compatible presence distinctions.

No independent Boolean codec is necessary. However:

- Recognizing a keyword boundary is still structural work.
- Absence must not be conflated with empty string or a fabricated null.
- The tagged result schema must enforce exactly the permitted optional-field combinations.

---

## 6. Assembly inventory and reduction attempts

Assembly has no complete node-by-node operational table. The following are identifiable meanings, not fully formalized rules.

| Constructor | Type, success and failure | Reduction attempt and judgment |
|---|---|---|
| **Literal** | Typed constant bytes → output contribution; output/work limits may reject. | K05 supplies the constant; placing it in a bounded output buffer and attributing its range requires assembly. **Existing constant plus new output construction interface.** |
| **AtomEncode** | Typed scalar → canonical encoded contribution; wrong type/range/mapping rejects at field path. | Inline an explicit encoder relation. This moves meaning and changes work/node attribution; it does not make a host encoder admissible. **Codec-dependent candidate composition; exact rules unresolved.** |
| **BytesCopy** | Supplied Bytes → exact output bytes, preserving order; checked growth before copy. | Identity/K04 preserves the supplied value. Copying it into a larger layout requires concatenation. **Value identity is existing; bounded concatenating copy is assembly meaning.** |
| **Seq-concatenate** | Ordered byte/string contributions → one sequence with output ranges. | K12 yields a sequence of contributions, not their flattening. Neither selection nor cardinality joins them. **New joining meaning.** Associative flattening has weaker value equivalence but can alter cost/depth/failure paths. |
| **Finite occurrence iteration** | Ordered typed sequence and layout body → concatenated per-occurrence contributions. | K12 can apply a defined layout body; joining is still required. Nested occurrence/field paths, string-character traversal and occurrence limits need rules. **Map plus assembly joining/profile integration.** |
| **Tag-directed Choice** | Declared tagged value → one layout branch. Invalid tags/field combinations must refuse or reject. | Existing typed tag projection and predicates can distinguish cases. Actual branch/output selection must be specified. **Existing data discrimination plus assembly control interface.** |
| **Presence-directed Choice** | Explicit absence/presence → declared output branch. | K19-compatible presence and conditional construction principle are reusable. Empty is not absent. **Composition**, subject to typed layout and failure-path rules. |
| **Length-prefix construction** | K18 extent → bounded integer → AtomEncode → bytes. | **Composition** of existing extent and explicit encoding. Cardinality must state whether it counts bytes, characters or occurrences. |
| **Trailer construction** | Cardinality of assembled prefix + K24 literal 2 → UInt16BE output. | **Composition**, provided prefix binding exists and counting/copying/reassembly costs are specified. |
| **Output-span attribution** | Layout/field IDs → half-open output ranges. | Existing field IDs do not calculate emitted positions. Requires current-output extent, checked range arithmetic and iteration-qualified identity. **New provenance interface; unresolved formal rules.** |

### Assembly counterexamples

1. **ASCII type alone is too broad for paired layouts.** An `ASCII(256)` string containing TAB, CR or NUL cannot be round-tripped through CFG66’s quoted-string grammar. DSV66 likewise excludes these characters and embedded LF.
2. **Integer type alone is too broad.** DSV66 quantity must satisfy its final ≤1000 rule, not merely Decimal15.
3. **BXC66 local field bounds do not guarantee total output ≤4096.** Eight individually valid 1024-byte contents can exceed the container bound.
4. **A byte-copy instruction is not a concatenation law.** Returning individual copied buffers is observably different from emitting a single framed buffer.
5. **Intermediate buffers matter.** Constructing a BXC prefix, measuring it, appending a trailer and exposing the final buffer could copy the prefix once or twice. The normative trace must decide.
6. **No fabricated source offsets.** Encode errors should use field paths, but work/depth/output-limit rules currently speak largely in cursor/node terms. Their encode equivalents need specification.

---

## 7. Auxiliary boundary and result rules

| Rule | Reduction/classification | Outstanding precision |
|---|---|---|
| **Bytes/ASCII/flat record/optional/tag domains** | Mostly type-domain refinement and prospective profile integration. | No automatic admission into current normal profiles; exact representable encode domain needed. |
| **≤64-node acyclic plan** | Finite graph validation uses existing architectural principles. | Distinguish unique nodes from dynamic entries; shared-node reuse and depth measurement must be fixed. |
| **Binding dominance/no shadowing** | Existing typed binding/dependency principles. | Repeat-local scopes, per-occurrence record construction and span bindings need explicit judgments. |
| **Selector disjointness** | Static finite-prefix analysis. | Formal treatment of EOF, empty prefixes and complements; canonical refusal identity. |
| **Progress check** | New plan-analysis obligation over consuming nodes. | A conservative minimum-consumption analysis is plausible, but not specified as an algorithm/rule set. |
| **Success/Reject envelope** | Existing outcome principle, new typed result transport. | Decode and encode envelopes differ; stage/code/node/expected coverage incomplete. |
| **Unavailable** | External runtime availability boundary. | Must remain distinct from pure rejection, without implying a physical adapter exists. |
| **Whole-input size/ASCII preflight** | Explicit boundary policy. | Parameterized limits versus fixed 4096; work precedence during preflight. |
| **Ordered validation** | Existing predicate and outcome composition. | Ordered row/field execution, resource charging and site transport must be defined. |
| **Duplicate detection** | K12/K13/K18/K06 support the Boolean test. | First-duplicate localization additionally needs earlier-prefix construction and ordered failure. |
| **Occurrence ordinal and earlier prefix** | Not supplied by ordinary map. | Explicitly acknowledged candidate meaning, but no constructor or full judgment is given. |
| **Raw spans** | Candidate cursor/provenance construction. | Which node contributes which span; transformed and discarded syntax treatment. |
| **Decoded-character source map** | New prospective provenance construction. | Composition across unquoting, later decoding and errors is absent from the formal node inventory. |
| **Consumed extent** | Candidate cursor result; End can reuse equality/cardinality. | Not applicable to encoding; envelope needs a distinct form. |
| **Private failure frame** | Pure relation can discard partial internal results. | Logical buffers/limits still need rules; no filesystem atomicity follows. |
| **Canonical expected sets** | Declared deterministic presentation policy. | Byte spelling versus node-ID ordering and stage-specific expected forms require complete definitions. |
| **Physical authority separation** | Reuses K20 boundary; pure bytes confer none. | K21/K22 do not grant filesystem extraction, process execution or atomic publication. |

### Duplicate-localization witness

For rows `r₀…rₙ`, an explicit prefix interface could bind:

```text
current = rᵢ
earlier = [r₀, …, rᵢ₋₁]
duplicate = contains(map(project_name, earlier), current.name)
```

Ordered validation rejects the first current row satisfying duplicate and uses its name span.

This is a sound compositional sketch **after prefix construction is admitted**. Naming that prefix as an immutable input without defining its construction is hidden delegation.

---

## 8. Strongest specification gaps and counterexamples

### 8.1 Cost is not yet a complete relation

The text charges each node entry and each examined/copied byte, plus digit processing. It leaves important questions open:

- Is ASCII preflight charged, and can WORK_LIMIT precede a later ENCODING error?
- Does a byte inspected by selector lookahead and then consumed incur two charges?
- Which trie path defines “examined” bytes?
- Does Decimal15 recognition inspect digits separately from decoding?
- Are table lookup, predicates, stable uniqueness, cardinality and prefix construction charged?
- Does character-map construction count as output growth?
- Does checking a retained immutable buffer inspect its bytes again?
- Are record/tag/span fields counted against an output-byte budget?
- Does shared DAG-node reuse count depth according to call stack or graph structure?
- Which action order applies when work, depth and growth limits simultaneously fail?
- Where is the “current cursor” during nonconsuming lookahead and assembly?

**Counterexample:** Replace one UInt16BE atom with two UInt8 atoms and nine additions. Successful integers can agree, but a small work budget can distinguish the programs through extra entries/actions. Thus numeric equality is not exact observable equivalence.

Likewise, flattening nested Seq nodes can remove entry charges and change depth-limit behavior.

### 8.2 DSV66 delayed conversion is not fully connected to Atom

DSV66 requires:

1. Parse the entire document structurally.
2. Unquote fields with provenance.
3. Convert quantities in row/field order.
4. Run final rules.

Decimal15 is defined as a cursor recognizer/decoder over bytes. To apply it to an unquoted string requires:

- A typed decoded-buffer input.
- A new local cursor.
- Exact full-field consumption.
- An EOF boundary appropriate to conversion.
- Transport of errors through the source map.
- Attribution to the original conversion node and stage.
- Cost rules for the second pass.

These are plausible additions, but are not supplied by “pointwise conversion.”

**Counterexample:** A quoted quantity with an early semantic failure and a later malformed record must report the later structural error first. Inline Decimal15 during field parsing gives the wrong precedence.

### 8.3 Span-sensitive round trips fail without projection

CFG rows contain source spans; BXC rows contain declared lengths and spans; DSV rows contain source spans/maps.

Canonicalization changes representation:

```text
count = 007\n
```

can encode as:

```text
count=7\n
```

Re-decoding changes offsets and spans. Therefore:

```text
D(E(v)) = v
```

cannot generally mean equality of the full span-bearing result.

Required repair:

```text
semantic_projection(D(E(v))) = semantic_projection(v)
```

with separate laws for reconstructed metadata, output ranges and valid representable domains.

### 8.4 Input and output limits are not uniformly parameterized

The relation accepts an explicit limit vector L, but INPUT_LIMIT is described using offset 4096. If `L.input` is smaller, the rejection boundary should follow L or the spec must say those limits are fixed rather than caller-variable.

“Output <=4096 bytes” also needs separate definitions for:

- Encoded bytes.
- Intermediate raw buffers.
- Decoded strings.
- Typed record sequences.
- Provenance metadata.

### 8.5 BXC name error identity conflicts with codec layering

The format promises a high-byte name rejection as NAME. The derivation invokes ASCII plus membership; ASCII’s declared error is ENCODING.

Rejection is certain, but exact error identity depends on:

- Whether byte membership runs first.
- Whether ASCII failure is explicitly translated.
- Whether ASCII is bypassed after direct range recognition.

That order/translation is not specified sufficiently for an exact claim.

### 8.6 Admissible encode values are underdefined

Round-trip laws need more than the declared local record types:

- Legal string repertoire.
- Tag/optional consistency.
- Nonempty/unique keys where required.
- Quantity bounds.
- Valid BXC names.
- Aggregate output bound.
- Treatment of stale declared-length/span fields.

Without these, some well-typed values have no valid canonical representation in the paired grammar.

### 8.7 Hidden delegation risks

The following shortcuts would import unspecified meaning:

- `parse(plan)` delegated to an unspecified host parser.
- `int(field)` supplying lexical, overflow and site policy.
- A library’s CSV quoting rules.
- A binary struct library supplying inverse byte extraction or incidental truncation errors.
- Generic string joining without an assembly rule.
- A host slicing operation supplying cursor bounds and rejection order.
- A host enumeration operation supplying prior prefixes and ordinals.
- A library codec name determining the relation.
- Host iteration over record fields determining byte order.
- Host timing determining WORK_LIMIT.

Libraries may realize an already specified relation. They cannot complete its missing definition by convention.

---

## 9. Reconstruction and small sufficient subsets

These are **small sufficient architectural subsets**, not proven inclusion-minimal sets. Removal examples identify lost distinctions; they do not establish that a removed constructor has no alternate reduction.

### 9.1 CFG66

**Decode subset**

- Literal recognition.
- Seq.
- Disjoint byte-prefix Choice.
- RepeatUntil with EOF/quote/class stopping.
- Byte-class/raw-byte recognition.
- Record/binding construction.
- ASCII validation.
- Finite escape projection and ordered character joining.
- Decimal15.
- Ordered validation with raw spans and earlier prefixes.
- Full-consumption check.

ScanClass can plausibly replace some single-byte repetition. Conversely, repetition and byte dispatch can plausibly replace ScanClass at weaker equivalence. RepeatCount, dynamic Take and UInt16BE are unnecessary for this witness.

**Encode subset**

- Constant contributions.
- Tag/presence dispatch.
- Character occurrence traversal.
- Finite canonical escape encoding.
- Decimal encoding.
- Ordered concatenation and row iteration.
- Output bounds and output-range attribution.

**Existing kernel reuse**

Presence, schema checks, duplicate Boolean checks and permitted postdecode predicates; no authority is derived from a name.

**Removal counterexamples**

- Without escape transduction/joining, the raw spelling `\n` is not a decoded LF.
- Without decimal meaning, `007` is only a lexeme, not integer 7.
- Without occurrence order, canonical rows may be reordered.
- Without prefix/provenance support, duplicate truth can be detected but the second-name site is not reconstructed.
- Without full consumption/final LF policy, `x=1` can be wrongly accepted.

**Judgment:** successful semantic-value composition is supported; exact plan, cost, provenance and encode-domain completeness remain unresolved.

### 9.2 DSV66

**Decode subset**

- Literal delimiters.
- Seq.
- Factored Choice around quoting.
- Bounded field/row repetition and byte-class recognition.
- ASCII validation.
- Doubled-quote projection and string joining.
- Record construction.
- Whole-document full-consumption check.
- Explicit second-pass decoded-buffer conversion.
- Decimal15.
- Decoded-index/source-byte maps.
- Ordered final validation and earlier-prefix support.

RepeatCount and binary UInt codecs are unnecessary.

**Encode subset**

- Ordered row traversal.
- Character traversal with quote doubling.
- String quoting literals.
- Decimal encoding.
- Concatenation and output bounds.

**Existing transform subset**

Selection by quantity, checked addition of one under ≤999, record projection/replacement and result revalidation.

**Removal counterexamples**

- Without quote-aware dispatch, a comma inside `"a,b"` is confused with a field separator.
- Without joining, doubled quotes remain two quote bytes instead of one character.
- Without delayed conversion, a malformed later record can lose precedence over an earlier bad quantity.
- Without provenance composition, quantity failures in quoted fields acquire incorrect original-byte sites.
- Without final revalidation, incrementing 1000 can escape the admitted transformed domain.

**Judgment:** structural and transformation sketches are credible, but the conversion/provenance interface is a genuine missing part of the formal reconstruction.

### 9.3 BXC66

**Decode subset**

- Header Literal and Seq.
- UInt8.
- UInt16BE, or two numeric-byte reads plus existing arithmetic with explicit failure preservation.
- Dynamic Take.
- RepeatCount.
- Record construction.
- Name byte membership and explicit ASCII mapping/error policy.
- Immediate ordered bound/equality checks.
- Full-consumption check.
- Cardinality/total-length check.
- Duplicate Boolean check plus ordered prefix/span localization.

Decimal15 and escape tables are unnecessary. RepeatUntil is unnecessary if counted repetition remains primitive.

**Encode subset**

- Literals and BytesCopy.
- Ordered entry traversal and concatenation.
- K18 lengths/count.
- UInt8/UInt16BE encoding.
- Prefix binding, K18 prefix extent and K24 `+2`.
- Final bounds and output provenance.

**Removal counterexamples**

- Without dynamic Take, an entry’s payload cannot be consumed according to its previously decoded length.
- Without unsigned big-endian meaning, `[0,2]` does not specify length 2.
- Without count-dependent traversal, count zero and count one are not distinguished structurally.
- Without End, trailing bytes may be accepted despite an otherwise plausible trailer.
- Without byte copy, arbitrary content such as `[255,0]` may be text-normalized or corrupted.
- Without trailer checking, `00 11` can be accepted in the supplied 16-byte example.

**Judgment:** a pure immutable container transformation is supported at architectural/value level. Error layering, assembly and logical costs remain incomplete. No authentication or physical publication is derived.

---

## 10. All 27 format/challenge cells

The following are independent specification judgments. **Every cell’s execution status is NOT_RUN.**

| Challenge | CFG66 | DSV66 | BXC66 |
|---|---|---|---|
| **1. Empty input** | **C:** zero rows. Requires EOF stopping without invoking a consuming body. | **C:** zero rows and empty canonical output. | **C:** empty input truncates header at EOF 0; explicit zero-entry container succeeds. |
| **2. Malformed encoding** | **C/I:** whole-input first-high-byte rejection is declared; Unicode interpretation unsupported. | **C/I:** same whole-input ASCII policy, including quoted fields; Unicode unsupported. | **U:** arbitrary high-byte content is valid and invalid name bytes reject, but NAME versus ASCII ENCODING layering is unresolved. |
| **3. Truncated input** | **C:** `x=1` requires LF and rejects at EOF 3; unfinished quoted string rejects. Full stage/node/expected catalog still needs completion. | **C:** `a,b,1` rejects at EOF 5; unfinished quotes reject. | **C:** checked exact reads reject at actual EOF; no padding or successful partial manifest. |
| **4. Ambiguous alternatives** | **C/I:** disjoint tagged-value prefixes work; overlapping prefixes refuse plans. General ambiguous grammar unsupported. | **C/I:** factoring quote handling yields disjoint decisions; arbitrary overlapping policies unsupported. | **C:** version 1 policy and explicit factoring are adequate at decision level; unknown version rejects at byte 4. |
| **5. Nested structures** | **C/I:** brace/bracket values reject; recursive CFG values unsupported. | **C/I:** permitted nested-looking printable characters are data; embedded record interpretation unsupported. | **C/I:** nested-container content is opaque bytes; recursive archive interpretation unsupported. |
| **6. Duplicate fields/keys** | **U:** duplicate truth and intended second-name site are clear, but the prefix/provenance traversal is not operationally defined. | **U:** uniqueness and row order are clear; ordered per-row final rules and prefix/site transport need explicit reconstruction. | **U:** total-length-before-duplicate policy is clear; first-duplicate localization has the same missing prefix interface. |
| **7. Invalid lengths** | **U:** decimal overflow policy is clear; name/string limits need raw-versus-decoded extent, growth and exact rejection rules. | **U:** column-count rejection is clear; decoded key/label bounds and second-pass quantity sites are insufficiently formalized. | **C:** length/count checks before Take and echo/trailer sites are declared. Exact limit-charging implementation remains globally U. |
| **8. Resource limits** | **U:** input/row policies are stated, but parameterized input bounds, work trace and decoded-output accounting are incomplete. | **U:** same gaps, plus conversion/provenance costs and transformed-result validation charges. | **U:** preallocation bounds are clear; assembly intermediates, copy/count costs and output-limit paths are incomplete. |
| **9. Conflicting validation** | **C:** ordered present/absent requirements cannot both pass; first false check wins after the declared structural stages. | **C:** q=15 fails the first of `q<=10`, `q>=20`; no rule weakening. | **C:** ordered permitted/forbidden policy rejects first false; structural integrity does not override policy. |

This table differs from the frozen matrix’s blanket completeness statement. The differences concern **claimed bounded precision**, not unsupported broader ambitions.

---

## 11. All 16 candidate-level attacks

**Every attack’s execution status is NOT_RUN.**

| ID | Independent judgment | Reason |
|---|---|---|
| **X01 — repeat empty literal** | **C; progress-analysis U** | The consuming-body rule forbids it. A conservative validation analysis is plausible but needs explicit inference rules, including choices and counted zero iterations. |
| **X02 — left recursion/cyclic calls** | **C** | Cyclic plan references are refused. A finite DAG, finite repetition bounds and bounded input support termination informally. No general recursive grammar is admitted. |
| **X03 — selectors `a`, `ab`** | **C** | Prefix overlap is a plan error. Factoring requires an explicit post-`a` policy, including EOF/other-byte behavior. |
| **X04 — invalid Take length** | **C; exact-budget U** | Negative/oversized lengths reject before reading; checked cursor arithmetic prevents wrapping. Runtime length-source site is declared. Literal-bound rejection uses node identity rather than a fabricated byte site. |
| **X05 — future/shadowed count binding** | **C** | Binding dominance and uniqueness refuse the plan. Repeat-local scope rules still need general formalization. |
| **X06 — noncanonical accepted spelling** | **C/U** | `007 → 7 → "7"` is clear. Full round-trip equality is unresolved until semantic projection excludes/reconstructs spans and representation metadata. |
| **X07 — two false checks** | **C** | Declared order chooses the error. Conjunction’s all-child truth semantics must not replace ordered rejecting validation. |
| **X08 — later high byte, earlier syntax error** | **C/U** | ENCODING-before-syntax policy is clear. Its precedence relative to WORK_LIMIT during preflight is not complete. |
| **X09 — oversized declared payload and truncation** | **C** | Immediate bound validation wins over attempting the truncated payload. This is an explicit declared order, not host allocation behavior. |
| **X10 — FF changed to FE** | **C/I** | Accepted under structural consistency; arbitrary corruption detection/authentication unsupported. The bounded result is determinate, even though the broader integrity capability is incomplete. |
| **X11 — small fixed-depth nesting** | **C/I/U** | Acyclic fixed-depth recognition is plausible; general recursive ASTs unsupported. The record/flattening/provenance typing and exact depth measure are unresolved. |
| **X12 — work exhaustion in lookahead** | **U** | The intended machine-independent policy is sound, but the exact examined-byte/action trace and cursor/node attribution are not fully fixed. |
| **X13 — installed library codec name** | **C** | Unknown descriptors refuse. A known descriptor must denote its reviewed mathematical relation, not a library’s undocumented variants. |
| **X14 — file destination/executable hook** | **C** | Effectful plans/codecs are outside the closed pure domain. Parsed names carry no authority. This does not establish an OS containment mechanism. |
| **X15 — arbitrary dynamic persistence** | **U** | Current profiles do not admit arbitrary byte/result shapes or profile unions. Pure results do not imply persistence/lowering coverage. |
| **X16 — split larger input into chunks** | **C/I** | Chunked calls are not equivalent to one full-input call. Streaming/global duplicate, order and budget composition are unsupported. A concrete difference is a duplicate key appearing in two separately accepted chunks. |

---

## 12. Formal obligations

The following are requirements for a later specification revision, not proofs supplied by this review.

### 12.1 Typing

Define separate judgments for:

- Decode nodes.
- Layout nodes.
- Codec domains/codomains.
- Intermediate decoded-buffer invocation.
- Binding dominance and occurrence-local scope.
- Tag/optional consistency.
- Provenance maps and encode field paths.
- Representable paired-layout values.

Prove preservation: successful execution produces a value inhabiting the declared type, including cross-field and aggregate bounds.

### 12.2 Progress and termination

Provide a conservative minimum-consumption analysis:

- Literal length.
- Atom-specific minimum extent.
- Take’s dynamic zero possibility.
- Seq sum.
- Choice minimum across branches.
- RepeatUntil/RepeatCount behavior.
- Empty Record/End behavior.

Establish finite evaluation from DAG structure, bounded repetition and finite charged actions. Do not rely on WORK_LIMIT to repair an ill-defined zero-cost infinite loop.

### 12.3 Determinism

Define:

- Prefix-selector traversal.
- Validation-stage order.
- Conversion order.
- Limit precedence.
- Code/node/expected attribution.
- Provenance composition.
- Assembly traversal and emission order.

Then establish uniqueness of success or rejection for fixed P, C, L and input.

### 12.4 Cursor and source-position safety

Establish:

```text
0 <= start <= cursor <= input_length
```

and checked advances without wrap.

Specify maps for:

- Escaped characters.
- Doubled quotes.
- Quoted empty fields.
- Derived buffers.
- EOF errors.
- Duplicate-name sites.
- Multi-stage conversions.

No fabricated input offsets should appear in encoding failures.

### 12.5 Cost

Define a small-step or equivalent normative event trace covering every charged action, including preflight, validation, provenance and assembly.

For reductions, require either:

1. Equality of normative charged traces; or
2. A stated cost translation with explicitly weaker equivalence.

A reduction that preserves values but changes WORK_LIMIT behavior must not be called exact.

### 12.6 Round trips and normalization

For each paired layout, define the semantic projection π and admissible value domain V:

```text
π(D(E(v))) = π(v), for v in V
N(x) = E(π(D(x)))
N(N(x)) = N(x), where defined
```

Also specify metadata reconstruction and whether the same budget vector permits both passes. A structural round-trip law should not imply that every tight-budget invocation succeeds.

### 12.7 Failure frame and integration

Prove that rejection exposes no successful prefix, without assuming filesystem effects.

Separately specify any later normal-profile binding, schema/IR transport, lowering, authority, persistence or physical publication. These are not consequences of pure interpretation.

---

## 13. A/B/C architectural alternatives

The permitted sources do not define a labelled A/B/C alternative table, and I have deliberately not opened the prohibited alternatives document. I therefore use the following **explicit local labels**, without asserting that they match the publisher’s labels.

| Local alternative | Assessment |
|---|---|
| **A — structural interpreter with atomic meanings expanded into its algebra** | Viable only if it visibly adds byte observation, joining, recurrent decimal interpretation, inverse encoding and provenance. Inlining scalar behavior can simplify interfaces but does not erase its semantic accounting. The existing structural node list alone does not derive all codecs. |
| **B — explicit codec relations plus existing decoded-data operations, with no general structural interpreter** | Adequate for already delimited atoms and decoded values. Insufficient for the witnesses’ sequencing, dynamic lengths, quote-sensitive boundaries, counted entries and exact source sites unless descriptors become format parsers. That enlargement would hide structural delegation. |
| **C — bounded structural interpretation/assembly plus explicit atomic relation registry** | The clearest candidate for the three witnesses. It separates grammar/layout structure from scalar interpretation and makes library conformance review possible. Its current specification still needs cost, provenance, assembly and encode-domain repair. It is a candidate architecture, not an adopted minimum. |

### Independent preference

**C is the most auditable starting point for specification repair.** A may later support useful internal reductions. B is insufficient if “codec” means only the declared scalar relations.

This preference is based on the reviewed meanings and reconstruction gaps, not the inherited recommendation.

### Implementation feasibility, separately

A checked bounded interpreter and assembler appear technically feasible with immutable buffers, explicit tables and cursor arithmetic. That observation does not establish:

- Faithful normal-path lowering.
- Exact logical-budget preservation.
- Correct source-map transport.
- Compatibility with current profiles.
- A verified independent implementation.
- Physical acquisition/publication behavior.

There is no implementation impossibility finding here.

---

## 14. Recommended bounded next specification experiment

Subject to separate authorization, the highest-value next step is a **specification trace challenge**, not further construct-count compression.

Produce explicit typed plans and normative traces for:

1. **DSV66 delayed conversion:** an early empty/overflowing quantity combined with a later syntax failure; a quoted quantity whose original-byte error site differs from its decoded index.
2. **UInt16BE expansion:** direct atom versus two UInt8 reads plus nine additions, identifying precisely which equivalence is preserved and which work/error observations differ.
3. **BXC66 assembly:** zero entries and one retained entry, including prefix binding, trailer calculation, copy events and output provenance.
4. **CFG66 canonicalization:** whitespace/leading-zero changes with a declared semantic projection and reconstructed spans.
5. **Competing limits:** preflight high byte versus tight work budget; lookahead at its last allowed charge; output growth coinciding with occurrence/depth limits.

No minimum claim should precede that repair. Any disagreements should remain visible rather than being resolved by changing the equivalence criterion after comparison.

---

## 15. Paths read and action record

### Directly read

1. `benchmark/results/phase6/r6_7/REVIEW-PROTOCOL.md`
2. `benchmark/results/phase6/r6_6/CANDIDATE-SEMANTICS.md`
3. `benchmark/results/phase6/r6_6/COMPOSITION-WITNESSES.md`
4. `benchmark/results/phase6/r6_6/ADVERSARIAL-MATRIX.md`
5. `benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json`
6. `docs/project-overview.md` — tool-delivered portion, lines 1–710.
7. `docs/agent-workflow.md`
8. `docs/semantic-kernel-audit-r5.108.md` — tool-delivered portion, lines 1–430.
9. `docs/typed-computation-v1.md`
10. `docs/typed-mutable-values-v1.md`
11. `docs/typed-predicates-v1.md`

### Inherited guidance

- `AGENTS.md`, supplied by the harness.

### Commands

- `git status --short`, before substantive review and at completion.

### Final boundary

**Precomparison review complete.** These are independent analytical judgments with explicit nonblind separation and unresolved precision findings. Kernel accounting remains 26. No files were edited; no semantic, test, compiler or acceptance execution occurred; P6-A05 was not accessed.
