# T3 modification — Bounded greedy coalescing

Terminal: `PRODUCTION_BINARY_CURSOR_CODEC_PROFILE_GAP`, static assessment.

Modification clauses 1 and 3 preserve the complete base validation, normalization,
encoding and original actions. Extending the action enum with coalesce removes
none of the original binary cursor/framing/codec interface blockers. Own base
`../base/CAPABILITY.md` and GAP.json identify the admitted scalar/collection input
types, closed pipelines, decoded-row selection and bounded computations, with
production references. Current `docs/axiom-v0.3.md:3–7,26–35,39–45` describes
closed-world validation and declared resources; arbitrary host Python expressions
or parser callbacks are not canonical language semantics. The typed input/value
documentation read in this session distinguishes external JSON decoding from
semantic transforms and retains bounded typed parameters.

New requirement: normalize original payloads first, retain empty records, then
scan left-to-right using the possibly enlarged last output row. Merge only equal
tags with combined length at most 8, concatenate in order, never renormalize the
combined payload, backtrack or discard empties. Re-encode count/checksums. This
adds an ordered accumulator/last-output binding and variable payload concatenation
obligation beyond the base transforms. Decoded tag equality, length comparison
and checked addition are useful subsets; they do not bind raw byte slices or
assemble output payloads through the assessed production profiles. A finite XOR
relation would not close those interfaces, as the base evidence already notes.
No coalescing-specific primitive or abstract impossibility is asserted. The
inherited binary framing and encoding gaps are independently sufficient to halt.

Read all 8 assigned new frozen cases after start. They specify empty input,
same-tag merges, no renormalization of concatenated sorted payloads, length-cap
splitting, empty-record merging/retention, cumulative enlarged-last decisions,
and original checksum rejection. These are expected observations only. Original
17 and new 8 cases are `NOT_REACHED`; zero candidates, compilations, evaluation
attempts, repairs or tests. There is no base success against which to measure
regressions; regression count/rate is unavailable, not zero. No host binary parser,
checksum processor or coalescing algorithm was authored as transport.

Base records are preserved. Reads: own base CAPABILITY.md/GAP.json, own base
contract, assigned modification contract/acceptance, current v0.3 documentation
and session typed-input documentation. Exact timing is in START.json/GAP.json;
session command/read disclosure is in `../../MODIFICATIONS.md`.
