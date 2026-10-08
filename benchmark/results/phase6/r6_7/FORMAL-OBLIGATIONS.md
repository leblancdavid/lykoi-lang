# R6.7 formal obligation assessment

These are audit requirements and informal arguments, not a repaired/adopted
specification or proved metatheory. Evidence: frozen candidate sections 2–6,
witnesses A–C and retained independent reviewer sections 7,8,12.

## Typing and preservation

Well-formed source values: immutable Bytes(N) with integer elements 0..255, ASCII(N)
characters 0..127, signed-64 mathematical integers (not Boolean/coerced strings),
finite ordered homogeneous sequences, flat declared records, explicit presence/tags.
Plan inputs include versioned finite descriptors and limit vector; P is a ≤64-node
DAG, unique dominating bindings, disjoint selectors of ≤8 bytes and no effects.
Codec D/E must separately declare source and result bounds. Intermediate values
need explicit types for slices, contributions, raw spans, prefix context, decoded
buffers/maps and output ranges. A sequence of string pieces is not a string.

Required judgments, absent as complete rules in 0.1:

`Γ ⊢ decode-node : (Bytes,cursor,Env,L) → Result(T,cursor,spans)`;
`Γ ⊢ layout : T → EncodeResult(Bytes,output-ranges)`;
`Γ ⊢ conversion : decoded-buffer × source-map → Result(T,source-site)`.

Record tag consistency must rule out both missing selected fields and contradictory
present/kind facts. Repeat-body local bindings cannot leak between occurrences;
prefix contexts must refer to earlier occurrences only. Encode paths need occurrence
indices and stable layout IDs. Preserve types on every success, intermediate growth
bounds, and well-formed failure transport. Current normal-profile admission is a
separate unresolved integration obligation.

**Round-trip domain is narrower than local types:** CFG strings permit printable
characters plus declared escaped LF; DSV excludes LF/TAB/CR and requires nonempty
unique keys and quantity≤1000; BXC requires legal unique names, consistent recomputed
metadata and aggregate size≤4096. The specification must say whether stale decoded
lengths/spans are checked, ignored or reconstructed on encode. CE06–CE08 show why
ASCII/integer/field bounds alone do not define admissibility.

## Progress, termination and possible stuckness

Valid plan+input must return success/rejection, or explicitly separate runtime
Unavailable; malformed plans refuse before input semantics. Malformed source must
return the declared stage/site; exhaustion must return its own logical limit error.
No partial successful result may escape.

Informal termination argument: acyclic calls, finite plan, bounded repeat counts,
and ≥1-byte successful repeat bodies bound cursor traversal. A conservative minimum
consumption analysis could use Literal length, codec minima, Take lower bound,
Seq sum and Choice minimum. Record/End/empty Literal have zero; dynamic Take can
be zero. Empty-success RepeatCount and min=0 ScanClass need explicit treatment when
nested as bodies. A finite work budget does not justify an undefined zero-cost loop.
RepeatUntil count bound additionally limits iterations even on invalid input.

Potential specification stuckness, not observed runtime hangs:

- DSV invokes Decimal15 on a decoded field, but source cursor/env/error rebasing
  are not supplied by Atom's declared raw-input signature.
- Assembly has no complete node judgments or encode-envelope shape: section 2
  says exactly Success(value,spans,consumed), section 5 omits consumed for encode.
- An admissible-looking ASCII value may have no E branch in its paired layout.
- Prefix/ordinal/span dependencies may require unnamed constructors.

Each must become either a well-formedness refusal or a typed deterministic result;
host exceptions/default conventions cannot resolve it.

## Determinism and failure precedence

Declared policies are useful: no backtracking, overlapping selector refusal,
ASCII preflight before syntax, first false ordered validation, BXC bound check
before payload read, DSV whole structure before conversion before final checks.
They are not a complete transition relation. Specify byte order in lookahead,
EOF branches, unknown byte expectations, local-to-source cursor rebasing,
ordered field/row checks, and each limit event. In particular: does work exhaustion
during ASCII preflight preempt ENCODING? What is current cursor during lookahead,
after final decode, during map validation or encode? How do work/depth/occurrence/
output priority rules attach to a single event? These affect observable results.
Name membership versus ASCII in BXC requires an explicit NAME/ENCODING rule.

## Round-trip obligations

Frozen adversarial X06 explicitly limits equality to semantic values, qualifying
the bare D(E(v))=v law. Define projection π removing source representation facts
and reconstructing/checking declared metadata. For paired layout domain V:

```
π(D(E(v))) = π(v)                         v ∈ V
N(x) = E(π(D(x)))                         accepted x, where defined
N(N(x)) = N(x)                           where both passes succeed
```

CFG whitespace/leading zeros and DSV quoting normalize; byte equality is not required.
UInt8/UInt16BE numeric domains admit unique byte encodings. BXC arbitrary content
must copy exactly; length fields are recomputed, not authenticated. Prove source
span/map laws separately from semantic projection. Bounds can prevent re-encoding
an accepted noncanonical DSV input: quoting every key/label can enlarge it beyond
4096 (CE16 gives a concrete 4096→4112 size calculation). Thus unconditional
normalization success needs a domain restriction or explicit
encode OUTPUT_LIMIT, even if D succeeded. Same tight L.work is not a round-trip
success guarantee. None of these laws has a formal proof in this publication.

## Source locations: compositional meaning versus new primitive

With explicit cursor positions, span pairing is ordinary record construction.
With explicit emission lengths and traversal, prefix sums via K18/K24 give output
ranges. With escape contribution provenance, composing local decoded indices with
source maps gives conversion sites. These are W16 compositional sketches.
Neither current K12 nor the listed nodes supplies arbitrary prefix-sum traversal,
decoded-buffer invocation or per-contribution map rebasing. Source tracking needs
explicit observable interfaces, but is not shown to require an independently
irreducible location primitive. Plain byte maps, escape initiating bytes, doubled
quotes, empty fields, EOF and discarded syntax need separate mapping laws. DSV's
“both bytes ... map” wording needs direction clarified for an index→byte function.

## Operation accounting

Atomic semantic step should mean one event in a normative transition/trace, not
one family name, host instruction or elapsed-time interval. 0.1 prescribes charges
for node entry, examined/copied bytes and digit processing. Needed event inventory:

1. plan/preflight checks and ASCII scan;
2. selector trie visits and stop observations;
3. cursor read/advance and bound checks;
4. codec lookup/digit transitions;
5. typed record/result append and growth;
6. validation, prefixes and uniqueness;
7. provenance construction/rebasing;
8. assembly contributions, copying, length observation and range attribution.

Say which are charged, which are zero-cost, their ordering and location/node state.
Specify work is checked before the next event; depth before entry; occurrence/output
before growth, with stated overlap priority. Define metadata/intermediate-buffer
budgets separately from encoded bytes. Reuse of a DAG node versus dynamic entry
must be distinguished. Optimized algorithms must preserve the normative result or
declare a cost translation. Incomplete cost laws block *exact* reductions, not all
value-level algebraic arguments.

## Assessment

Typing/preservation, deterministic small-step completeness, progress rules,
round-trip domain and metadata laws, source-map transport, and normative trace
all require specification repair. Backend feasibility is plausible for finite
immutable values but does not settle any of these obligations or physical effects.
