# R6.43 provenance observation contract 1

Research-only labeling of unchanged R6.10/R6.18 observations. No execution meaning
is added. Authority: R6.10 CONTRACT-1 and its frozen implementation (Cell default,
Machine.decode, Machine.run); R6.18 SEMANTICS-1 sections25–36 and49–60. The
implementation refines the character-origin tuple wording: numeric decoding keeps
the lexeme span but uses the empty default origins. The authority is not R6.42's
candidate output or its failed oracle.

## Coordinates and availability

| Category | Existing observation | Meaning / exclusions |
| --- | --- | --- |
| Raw-byte origin | Cell supplied to numeric decode, span and origins | Fixed atom's raw bytes have [start,end) and tuple(range(start,end)). Observe before decode; never assign this tuple to decoded integers. |
| Decoded-numeric origin | Cell returned by UInt8 decode | Same span; origins=(). Empty retained origins are AVAILABLE_EMPTY, not proof of no input dependence. |
| Sequence-return span | Cell returned by seq | Region-entry cursor to current cursor (or declared span_end); not operand ancestry. This saved witness has no span_end/rebase_errors. |
| Symbolic origin | Existing map definition/local and ordered expansion path | Exact content pin and call-local chain. Raw VM node remains intact. Flat correspondence is a comparison annotation, not flat symbolic authorship. |

Arithmetic ref/add values keep the existing left-operand span and empty numeric
origins. That span is labeled VALUE_SPAN, never dynamic operand lineage. At cursor2
the four nested regions return [2,2); root success returns [0,2). Flat left/right
values keep [0,1)/[1,2). Errors preserve node, offset, stage, path and work. A
consumer check's symbolic path must not be replaced by its input producer's path.
Emission output_spans use output-buffer coordinates, not input coordinates.

Authored-text line/column, separate expression-occurrence identity, dynamic integer
operand lineage and runtime value-producer chains are UNAVAILABLE. An absent map
entry is UNAVAILABLE, not inferred from an ID. Static saved caller-site annotations
may identify a producer region; they do not establish a general runtime lineage.

## Sidecar boundary

sidecar.py accepts already-collected observations and metadata. It copies and
labels fields, retaining a commitment to the complete raw record and each event's
index. It imports no VM and cannot execute, predict a value, determine acceptance,
rewrite an offset or change a charge. No metadata feeds the executable plan.
Observation hooks are separate in run.py; each instrumented public envelope is
compared with the unchanged uninstrumented public API. No charge is skipped.

Compact versus its exact expansion requires identical plan, map, full raw trace,
envelope and work at the same budget. Flat equivalence is only the separately
specified functional projection at default budgets. Its IDs, offsets, seq-return
events, work and equal-budget outcomes remain observably different.

## Prospective freeze and scope

prepare.py derives new expectations from the documented saved behavior and fixed
semantic rules, without importing VM/expander/oracle or reading historical results.
review.py separately checks constructor/seq authority via AST and saved structural
forms, coordinate rules, path declarations and six manually specified outcome
anchors before freeze. This is an output-independent mechanical review, not an
independent human, blind review or separate cognitive author. Coordinator exposure
to R6.40–R6.42 is disclosed. No independent-reviewer attestation is available.

Successor checks cover39 saved input cases, two default passes and work budgets
0/13/43/51. Default expectations enumerate every successful node return, numeric
decode input/output, functional outcome, exact work and error offset. Cutoffs
qualify observation preservation and exact-twin correspondence, not a new complete
independent cutoff oracle. All checks remain a bounded nonproduction qualification.
No R6.42 result, artifact or expectation is repaired or rescored. Stop at publication.
