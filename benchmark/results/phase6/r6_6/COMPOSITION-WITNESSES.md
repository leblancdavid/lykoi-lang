# R6.6 cross-domain composition witnesses

These are independently designed synthetic format specifications, unrelated to
package fixtures, with the same [candidate interpreter](CANDIDATE-SEMANTICS.md).
They are not Lykoi programs, benchmark solutions or executed tests. Each format
chooses narrow policies deliberately; coverage means specified derivation, not
current implemented support. All offsets are zero-based byte offsets.

## A. Configuration assignments: CFG66

Input is ASCII, <=4096 bytes. Space means byte 0x20 only; line terminator is LF
0x0A only. TAB/CR/comments are invalid. Grammar notation is descriptive, not a new
source syntax; every repetition is bounded by the candidate limits.

```
document := (assignment LF)* EOF             # 0..8 assignments
assignment := name SP* '=' SP* value SP*
name := [a-z][a-z0-9_]*                      # 1..32 bytes
value := string | decimal | 'true' | 'false' | 'none'
string := '"' (plain | escape)* '"'           # <=256 decoded characters
plain := ASCII 0x20..0x7E except '"' and '\'
escape := '\"' | '\\' | '\n'
decimal := [0-9]+                            # Decimal15
```

Every assignment requires its final LF. Value is not syntactically omittable:
`none` means **absent**, `""` means present empty string. Names cannot be keywords
in value position; keyword terminators are space or LF only. Digit continuation
is digits, stop space or LF; other bytes reject at the offending byte. Config
empty input is valid and produces zero rows. Field names need not match an ambient
schema; a subsequent explicitly supplied schema can reject unknown names.

Output row: `(name, present, kind, text?, integer?, boolean?, source_span)`.
Absent has `present=false, kind=absent`; otherwise exactly one typed value is present.
Syntax spans include the name through the last non-space value byte, excluding LF.
Final validation rejects duplicate names exactly/case-sensitively at the second
name's start, in occurrence order. No overwrite or implicit deduplication.

Derivation:

1. C-ATOM ASCII checks input; I-BOUND class recognition/repetition extracts name.
2. Seq interprets separator and spaces; Choice dispatches on quote/digit/t/f/n,
   using factored disjoint prefixes. Finite escape tables build string contributions;
   Decimal15 supplies numeric meaning. Record construction binds the tagged row.
3. RepeatUntil(...,EOF,8) collects rows; End guarantees full consumption.
4. K12 projects row names; K13 and K18 with K06 detect duplicates, preserving the
   original rows. An occurrence scan in I-BOUND attaches the second-name error site.
5. Existing presence K19, equality/membership/conjunction/complement K06–K09 and
   typed bindings K04 apply source-authorized configuration constraints. Selected
   known-field values can feed ordinary typed writes with K17/K20/K21/K22.
   This is a future binding interface; no arbitrary eight-row upsert is asserted.
6. Canonical layout emits original name/order, `=`, canonical tagged value and LF;
   string quote/backslash/LF use the declared escapes, decimal drops leading zeros.

Hand-derived witness (display `\n` within a quoted value means two input bytes):

```
title="a\n\"b"
count=007
enabled=true
note=none
```

Result: title contains `a`, LF, quote, `b`; count integer 7; enabled boolean true;
note absent. Canonical count is `count=7` plus LF. `x=\n` (actual LF after `=`)
rejects `VALUE` at 2; `x="\q"` rejects `ESCAPE` at 3; `x=1` without LF rejects
`TRUNCATED` at EOF 3. For `x=1\nx=2\n` with actual LFs, duplicate rejection is
at offset 4. No backend result is claimed.

## B. Structured import: DSV66

Input ASCII <=4096 bytes. No header. Zero to eight records, each exactly three
fields: key string, label string, quantity Decimal15. Every record ends in LF.
All three fields follow the same quoting rules before their typed conversion.

```
document := (field ',' field ',' field LF)* EOF
field := quoted | unquoted
quoted := '"' (qplain | '""')* '"'
qplain := ASCII 0x20..0x7E except '"'
unquoted := (ASCII 0x20..0x7E except ',' and '"')*
```

Comma is allowed inside quotes. Backslash is literal, not an escape. No embedded
LF/CR/TAB. A quote in unquoted input is invalid. A closing quote must be followed
by comma or LF; Choice after a quote selects another quote as escaped quote, or
a delimiter as end. EOF inside a record is truncation, including after its third
field. Spaces are data. Empty string fields are permitted lexically; quantity
must be one or more digits after unquoting. Quoted `"007"` decodes to integer 7.

Typed output `(key:ASCII(32), label:ASCII(256), quantity:integer, span)` in input
occurrence order. Final validation: key nonempty, unique exact key, quantity <=1000,
in that explicit rule order per record, processing records left-to-right. Quantity
Decimal15 overflow is conversion rejection before final rules. Structural parsing
of the whole document precedes all conversions; conversions run row/field order,
then final rules. A malformed later record therefore precedes an early semantic
key error. This order is a declared policy, not a claim of chronological first error.

Each field retains raw span and a map from decoded character index to originating
byte (both bytes of a doubled quote map to its first byte). Conversion errors map
back through this table; empty quantity points at the field start. This provenance
construction is part of prospective I-BOUND support, not supplied by K12 today.

Derivation: ASCII -> I-BOUND field recognition/escape-table joining -> three-field
Record -> ordered repetition/End -> pointwise Decimal15 conversion with byte
provenance -> existing nonempty/cardinality/equality/uniqueness/range predicates.
Successful typed rows may compose existing finite related creation and a qualified
single-store atomic frame for **at most eight** rows under declared model authority;
dynamic import binding and byte provenance are not implemented. No merging with old
records, generated IDs, historical defaults or access authority is inferred.

Pure transform witness: select quantity >0 by K10/K16; preserve key/label and
replace quantity with K24 `quantity+1` only under an explicit <=999 precondition;
validate the transformed result again. Then assembly quotes **every** string,
doubles internal quotes, emits canonical unquoted decimal quantity, comma and LF.
Retained row order is unchanged. No sorting or input repair.

```
k1,"a,b",007
k2,"say ""hi""",0
```

Decoded rows have quantities 7 and 0. Selection/increment yields only k1 with
quantity 8. Canonical output: `"k1","a,b",8` plus LF. `a,b,1` without LF rejects
at EOF 5; `a,b,\n` with actual LF rejects quantity at 4 after structurally successful
decode; `a,"b"x,1\n` rejects closing-quote delimiter at 5. Empty input produces
zero rows/empty canonical output. These are symbolic calculations.

## C. Read-only artifact interpretation: BXC66

A bounded binary container, **not ZIP/wheel**, with no compression, executable hooks,
directories, timestamps, permission bits, symlinks or filesystem extraction.
Input/output <=4096 bytes; numeric atoms are unsigned big-endian.

```
header       4 bytes literal 52 36 36 43 hexadecimal ("R66C")
version      UInt8, exactly 1
entry_count  UInt8, 0..8
each entry   name_length UInt8, 1..32
             name[name_length], bytes [a-z0-9_] only
             content_length UInt16BE, 0..1024
             content[content_length], arbitrary bytes 0..255
             length_echo UInt16BE, equal to content_length
trailer      total_length UInt16BE, equal to cardinality(entire input)
end          EOF, no trailing bytes
```

Names are nominal identifiers; `/`, `.`, backslash and high bytes reject, without
path normalization. Duplicate names reject at the second name start. Content need
not be text: malformed UTF-8 in content is valid. Header/version/name/count/length
checks occur immediately when their inputs exist; length_echo equality immediately
after its atom. Full consumption precedes total-length and duplicate-name checks,
in that order. Name bytes reject at the first invalid byte. Truncated atoms/payload
reject at actual EOF; no allocation based on an unchecked length.

The integrity contract is **structural consistency**, including repeated length,
exact trailer size, unique names and bounded byte ranges. It does not authenticate
the artifact or detect same-length content corruption; no checksum/digest claim.
If arbitrary tamper detection is required, this candidate witness is incomplete.
Authoring a cryptographic digest would need its own visible relation, not K06.

Derivation:

1. I-BOUND Seq reads header; C-ATOM UInt8 reads version/count; K06/K16/K17 check.
2. RepeatCount entry_count invokes Record, typed length atoms and dynamic Take.
   C-ATOM ASCII plus finite name-byte membership validates names, not contents.
3. K06 checks each echo; End rejects trailing input; K18/K06 check total length;
   K12/K13/K18 reject duplicate projected names. Output is ordered entry records
   `(name, content:Bytes(1024), declared_length, spans)`.
4. Pure artifact transform: K10 selects names from an explicitly supplied permitted
   set; project exact content and name. K18 recomputes count/content/name lengths;
   I-BOUND layout with C-ATOM integer encoding reconstructs entries/echo and header.
   Compute trailer as K18 cardinality of assembled prefix + K24 literal 2; emit it.
   Revalidate <=4096. No dynamic subtraction, multiplication, hash or compressor.
5. Existing finite nominal references can link decoded entries to supplied metadata,
   and K23 can check those supplied reference cycles. K20 authority is still needed
   for any eventual byte acquisition/write; K22 single-store commit is not a claim
   of atomic filesystem publication. This witness ends at an immutable byte value.

Hand-derived valid one-entry container, 16 bytes (hexadecimal):

```
52 36 36 43 01 01 01 61 00 02 FF 00 00 02 00 10
```

Length derivation:
header 4 + version/count 2 + name length/name 2 + content length 2 + content 2
+ echo 2 + trailer 2 =16. It represents name `a`, content `[255,0]`.
Replacing the trailer with `00 11` rejects `TOTAL_LENGTH` at offset 14.
Zero-entry valid container: `52 36 36 43 01 00 00 08` (8 bytes). Empty input rejects
header at EOF 0. Changing the one-entry echo to `00 03` rejects at 12; deleting
the final byte rejects trailer at EOF 15. Retaining no entries encodes the above
zero-entry form. These outcomes are derived, not executed.

## Common composition boundary

All three use the same bounded repetition, sequencing, choice, typed construction,
lexical relations, validation and layout meanings. Configuration-specific fields,
DSV quoting and BXC framing are plan data, not new domain primitives. Existing
kernel operations handle decoded constraints and permitted transformations.
New input/output binding support is required for all three; pure sufficiency does
not establish normal-path integration, physical effects or behavioral correctness.
