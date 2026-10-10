# Provenance terminology and coordinate systems

## Four different questions

| Concept | Meaning | Existing evidence |
| --- | --- | --- |
| Semantic origin |Executable operation producing a value/error |VM error.node, plan node.id/op, bind-to-producer relation; no general runtime value-producer pointer |
| Authoring origin |Symbolic definition, expression or caller that supplied that operation |Expansion map definition/local; original package steps/expressions and caller pins |
| Expansion path |Ordered symbolic call-site/target chain leading to the operation |Generated node path `program/<root pin>/<call local>/<target pin>/.../<primitive local>` |
| Input provenance |Input-byte span or character origins transported with a Cell |Cell.start/end/origins; check offset selects site's start, independent of operation's authored coordinate |

Semantic origin must include both the primitive operation and, for implicit
transport, the seq-return wrapper that replaced a span. A check is the error
producer; its site's prior value producer can be a different operation/path.
For E3, check origin is sum/pair while v's returned-span producer is v/interval.
For E4, check origin is total/interval while t's returned-span producer is t/echo.

## Coordinate domains

1. **Input byte coordinates:** zero-based half-open spans [start,end), with valid
   zero-width spans at EOF. Offset2 after two bytes is a valid cursor/region start,
   not necessarily an offending byte. `error.offset` is scalar input-site start
   for these validation checks; encode-stage offset is null under existing VM rules.
2. **Executable node coordinates:** unique plan node IDs. An error node identifies
   the active operation, not the input lexeme or an expression's AST location.
3. **Symbolic coordinates:** immutable definition hash plus local step ID and its
   occurrence/caller path. Definition alone cannot distinguish repeated calls.
4. **Serialized document coordinates:** JSON lines/columns/byte ranges are not
   preserved by canonical hashes or the node map. Object-key layout/formatting
   cannot be recovered from a canonical definition identity.
5. **Expression coordinates:** there are no independent stable IDs for each
   expression occurrence. The original definition can be inspected structurally,
   but the published node map does not map individual substituted expression leaves.

No conversion between these domains is implied by the word “source”. In particular,
caller-relative step IDs and definition-local step IDs are not input offsets.
R6.40's “at v”/“at t” leaves the input-span propagation rule implicit.

## Existing deterministic transport

[R6.10 contract](../../../../experiments/semantic_interpreter/CONTRACT-1.md)
lines25–30,47,52–53 and85–122 specifies Cell provenance, checks and logical work.
Interpreter266–316: refs return existing Cells; constants get the current cursor;
add/le/eq return the left operand's start/end. They do not union both operands'
input ancestry. Integer `origins` is generally empty. Hence flat t reports x's
start0 even though y contributes twice; this is left-operand transport, not a
complete causal-input explanation.

[R6.18 semantics](../../../../experiments/typed_composition_r6_18/SEMANTICS-1.md)
lines25–36 explicitly makes template-expanded provenance/work normative. Composition
returns a seq-wrapped Cell; the returned start is region entry. Internal failures
do not first return that Cell. Literals substituted into argument uses acquire
provenance at actual use and repeated parameter expressions incur repeated work.
Regions cannot be flattened on the assumption that grouping is observationally inert.

VM `span_end` and `rebase_errors` exist outside this wrapper's emitted subset.
They are not a transparent-return mechanism: `span_end` only changes end;
`rebase_errors` changes listed failures to sequence entry. Neither recovers original
arithmetic input ancestry or supplies authored line coordinates. They cannot be
silently enabled in this investigation or the R6.18 wrapper.

## Represented versus inferred

Map entries literally contain `{definition,local}`; caller chain is encoded in
the path key, rather than a separate ordered-array field. With the exact package,
that chain can be decoded deterministically and linked to caller compose steps.
Hygienic bindings are hashes of region path/local, not human source locations.
Definition/result expression attribution can be reconstructed from the package;
runtime values do not themselves carry full semantic/authoring/expansion metadata.

R6.32 reuses R6.18's content identity unchanged. Pins anchor exact versioned
content and closure, not equivalence of two definitions. Any body/dependency
change changes identity and caller paths. Stable across reloading identical content
does not mean stable across edits, alternate inlining or parameter renaming.

Not all concepts must be externally observable runtime fields. Existing runtime
node/offset/work can stay raw while maps and packages provide separate debugging
metadata. Requiring additional expression-level or causal-input lineage would
need a distinct specified interface and qualification.
