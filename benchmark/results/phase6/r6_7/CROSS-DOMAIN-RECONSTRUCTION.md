# R6.7 cross-domain reconstruction and removal challenges

All reconstructions are specification sketches, **NOT_RUN**. “Smallest supported”
below means a small retained subset supported by the available witnesses, not a
proved minimum. Node-complete typed plans, all errors and ≤64-node feasibility are
not established; the retained subsets are conditional architectural reconstructions.
Where a constructor can plausibly be factored, list the substitute and its gap.

## Shared meanings

Read observes the same bounded raw Bytes in every format; Seq threads the same
cursor; Choice uses byte-prefix disjointness; repetitions return source occurrence
order; Record binds supplied values; End checks the same whole-input property.
Joining always preserves contribution order, Decimal15 never changes mathematical
meaning by domain, and byte encoding always fixes unsigned big-endian. Formatting
policies, escape tables and validation stages are explicit format data. DSV's second
pass needs a new documented invocation *interface*, not a different Decimal15 meaning.
No domain-specific interpretation of map/contract/authority is permitted.

## CFG66 reconstruction

Retained decode subset: Literal, Seq, Choice, RepeatUntil, ScanClass (or explicit
one-byte class reads+repetition), Record/bindings, End; ASCII preflight, finite escape
projection+character join, Decimal15; ordered validation with spans/prefix context.
No dynamic Take, RepeatCount, UInt8 or UInt16BE is needed. End's predicate and Record
construction reduce to existing meanings once cursor/bindings exist; finite escapes
reduce at scalar level. Encode retains literals, tag/presence dispatch, character/row
iteration, canonical escape/decimal encoding and join, aggregate bounds/output spans.

Plan sketch: EOF-stopped ≤8 assignments; name first/continuation class scan ≤32;
SP* then '=' then SP*; predictive quote/digit/t/f/n branch; quoted contributions
until closing quote, or Decimal15/keyword; SP*; mandatory LF; tagged row, final End;
ordered exact duplicate checks. Canonical layout preserves names/order, emits '=',
selected canonical value and LF. Source_authorized predicates remain existing K06–K19.

Symbolic example: title with backslash-n/backslash-quote decodes LF/quote, `count=007`
decodes 7, enabled true, note none is absent rather than empty. Re-encoding changes
count spelling to 7; source span changes. Remove escape projection: LF/quote value
law fails. Remove Decimal15: typed 7 missing. Remove join: pieces instead of text.
Remove prefix/site support: duplicate truth remains, second-name location missing.
Remove End/final LF checks: `x=1` may wrongly succeed. Remove RepeatUntil: raw
number/boundaries of assignments are not provided to K12.

## DSV66 reconstruction

Retained structural subset: Literal, Seq, factored Choice, class reads/repetition,
Record, RepeatUntil, End, ASCII and doubled-quote projection/join. RepeatCount/Take
and binary atoms are unnecessary. Additional required interface: after complete
structural parsing, bind each decoded field as a buffer with source map, invoke
Decimal15 at local start with EOF completion, rebase errors, then ordered final
checks (nonempty key, uniqueness, quantity≤1000 per row). This interface is claimed
in prose but not operationally specified. Encode uses row/character iteration,
all-string quoting/doubling, decimal E, delimiter literals and joining.

Plan sketch: quote-opening versus unquoted branch; doubled quote versus closing
quote+delimiter factored; exactly three field positions separated by commas and LF;
whole document before row/field conversions; whole conversions before final rules.
K10/K16 select quantity>0; K24 increment only under ≤999; revalidate then encode.
Symbolic rows k1 label a,b quantity 007 and k2 label say "hi" quantity 0 produce
only k1 quantity 8, canonical `"k1","a,b",8` plus LF.

Remove quote-sensitive dispatch: comma in quoted data loses boundary meaning.
Remove character join: doubled quotes stay two bytes. Merge conversion into field
recognition: CE04 changes error precedence. Remove source map: CE11 mislocates
quantity overflow. Remove revalidation: transforms can violate ≤1000. Calling a
host CSV reader or int() would conceal these obligations. The full exact candidate
is not reconstructed until second-pass binding/map/trace rules exist.

## BXC66 reconstruction

Retained decode subset: Literal(header), Seq, UInt8, UInt16BE, dynamic Take,
RepeatCount, Record, End, name-byte validation/ASCII view, immediate bounds/echo,
total length then duplicate checks with prefix/sites. No Decimal15/escape table/
RepeatUntil is necessary. UInt16BE arithmetic can use W05, but not its entire
byte acquisition/inverse/error trace. Encode uses ordered entry iteration, literals,
BytesCopy/join, cardinality, UInt E and prefix binding+K24(+2) trailer construction.

Plan sketch: header/version/count checks; exactly count entries; validate name length
before Take, name bytes as identifiers; content length≤1024 before Take; echo equality;
trailer; End; total cardinality equality; duplicate names in source order. Select
permitted names using K10, preserve arbitrary content, recompute all lengths/count.
Symbolic 16-byte sample from R6.6 yields name a/content [255,0], trailer 0010.
No entries yields 8-byte `52 36 36 43 01 00 00 08`. Echo 0003 instead of 0002
rejects at 12; trailer 0011 rejects at 14; deleting final byte truncates at EOF 15.
These are inherited symbolic expectations, not rerun results.

Remove Take: dependent payload boundaries missing. Remove counted traversal:
count zero versus one cannot determine structural entry repetitions. Remove byte E:
numeric cardinality has no byte representation. Remove byte copy: content FF/00
can be lost/text-normalized. Remove End: trailing data may survive. Remove length
checks: trailer/echo consistency lost. Merge ASCII preflight with textual formats:
arbitrary high-byte payload wrongly rejects. NAME/ENCODING precedence must be made
explicit; the current names-only adapter is insufficiently ordered.

## Shared removal/merge results

| Proposal | Retained result | First unmet obligation |
| --- | --- | --- |
| Eliminate separate tokenizer | lexical spans built inside structural plan | no new tokenizer needed for these formats; costs/node plans still open |
| Eliminate finite escape codec primitive | literal recognition+typed projection | joining/provenance and exact trace remain |
| Replace UInt16BE D by addition | same numeric value on supplied bytes | raw operands/inverse/error/work, CE02 |
| Replace ScanClass by repeated class read | plausible same lexeme | class read/empty/max/EOF trace unspecified, CE14 |
| Replace both repetitions by K12 | only works over supplied occurrences | occurrence segmentation/cursor/count supply is circular |
| Merge D/E by grammar inversion | no automatic canonical choice | CFG normalization and DSV forced quoting require explicit layout |
| Merge spans into record metadata | pairs can be constructed | source/emission cursors/maps not already supplied |
| Remove C-ATOM family name | can inline relations visibly | Decimal15 recurrence/inverse and binary E still need accounted meaning |

No node-count proof is possible from prose plans. Selector/table data are finite
but not necessarily charged/count-limited like structural nodes; moving operations
into descriptor tables can hide size without reducing semantics. Independently fixed
complete plans and a size convention are needed for a bounded sufficiency verdict.
