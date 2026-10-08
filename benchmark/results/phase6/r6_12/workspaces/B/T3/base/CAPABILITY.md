# T3 base — current production capability assessment

Terminal: `PRODUCTION_BINARY_CURSOR_CODEC_PROFILE_GAP` (static assessment).
No semantic candidate, compilation or acceptance execution; zero repairs.

## Obligation mapping

- Clause 1: action is expressible as an enum; hex is a string. Exact hexadecimal
  syntax, even-length and length bounds have no string-length/character/cursor
  predicate in the closed trees (`src/air_compiler/predicates.py:43–96`).
  Types and exact enum equality alone do not validate this string language.
- Clause 2: decode the hex representation, consume a header and a runtime number
  of length-delimited records, distinguishing ordered truncation/tag/length/checksum
  errors and trailing bytes. No production binary cursor, byte-index/slice,
  counted framing, or hex codec input operation is admitted by the inspected
  normal compiler dispatcher (`profiles.py:55–96,135–170`), typed input vocabulary
  (`predicates.py:19–34`) or transformation pipeline (`mutable_values.py:51–84`).
  Legacy declared capability adapters are JSON file, clock, UUID and file-access
  authority (`validator.py:134–150`), not an extensible arbitrary parser callback.
- Clauses 2–3: original validation must complete before normalize/prune. Existing
  RAW/TRANSFORMED/PERSISTED staging and unchanged-on-failure effects are useful
  **after** values have been typed/decoded; they do not supply this binary grammar.
  See `docs/typed-input-values-v1.md:34–68,145–153`.
- Clause 3: tag-0 verbatim payload is a partial expressible subset. Existing query
  ordering can sort decoded byte-valued rows with explicit identity/tie keys;
  scalar predicates can select nonempty decoded records if length is explicitly
  available. Existing finite entity cardinality can count retained records.
  Those observations require a decoder and permitted typed representation first.
  The closed pipeline map only applies verbatim/trim/stable-deduplicate and
  validation, not payload reverse or numeric byte-sequence sorting
  (`mutable_values.py:51–84,114–124`).
- Clause 4: exact lowercase hex re-encoding and recomputed XOR checksums have no
  current production encoder/result-construction interface. A sequence of runtime
  payload lengths is not a cardinality field-sum (`computation.py:29–58`).
  A Python serializer may serialize an exact observation to JSON, but computing
  this binary observation in that serializer would implement the contract.

## Composition limits, not a kernel theorem

Byte values and XOR are finite. A declared lookup relation over byte pairs could
in principle encode XOR; literal finite relations, predicates, selection and
cardinality are real available meanings (`references.py:62–115`). Missing a named
XOR primitive alone does not justify the terminal classification. The current
production profile does not bind raw byte positions/runtime slices to those
relations, traverse the variable framing, and construct the normalized encoded
message. Feeding already parsed record/checksum observations from Python would
move clauses 2–4 into prohibited host central behavior.

This is a current semantic/profile interface gap, not an executed compiler/runtime
or acceptance failure and not an impossibility/minimum claim. All 17 base cases
remain unexecuted. Task-specific reads followed START.json; GAP.json records time.
