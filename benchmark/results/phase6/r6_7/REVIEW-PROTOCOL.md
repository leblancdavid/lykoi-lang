# R6.7 independent specification reduction protocol

Prejudgment protocol, fixed before the separated reviewer is invoked. Authority:
owner request “R6.7 — Independent Specification Reduction Audit”, specification
only. Baseline `c1c31072cf38907e81f55a4d9463e03012b872c3`; initial status clean.
The six raw-byte SHA-256 identities in R6.6 PUBLICATION-IDENTITIES.json were
verified before review. The original files remain the frozen evidence.

## Separation and ordering

The primary publisher has read the R6.6 report and repository guidance; it is
not a blind reviewer. A distinct general subagent is explicitly appointed as
the reduction reviewer by this protocol under the owner's reviewer-separation
authorization. It must first read only candidate definitions, witnesses,
adversarial cells and existing versioned kernel meanings, form and return
judgments without reading R6.6's report, alternatives or open obligations.
Its returned judgments are retained verbatim before publisher comparison.
Repository guidance is inherited and discloses the prior classification and
recommendation; this is not concealed. No tool-enforced context isolation,
different provider, different model or independent human authorship is claimed.

Independence here means a separated reasoning pass with no R6.7 substantive
conclusions supplied, explicit non-deference, retained precomparison judgments
and visible disagreements. It is procedural independence, not statistical or
organizational independence. If this procedure fails, use
R6_7_INDEPENDENCE_NOT_ESTABLISHED; lack of blindness alone is disclosed rather
than represented as clean-room evidence. AI-provider independence of semantics
is preserved; no runtime AI service or provider-specific meaning is introduced.

## Decision procedure

1. Inventory every named structural node, assembly constructor, codec and
   auxiliary boundary/result rule; do not count family names as constructs.
2. For each: type, success/failure, kernel-only witness attempt, candidate-only
   witness attempt, circularity, resource/location/order observations lost.
3. Accept reductions only relative to explicit observable equivalence:
   value, consumed extent, error code/site, output order/bytes and logical budgets.
   Value-only equivalence is labelled weaker; missing cost laws block exact claims.
4. Reconstruct CFG66/DSV66/BXC66 from those meanings, with removal counterexamples.
   No host parser/codec or callback may supply missing interpretation.
5. Assess typing/progress/termination/determinism/round trips/source positions/cost.
6. Classify all 27 format cells and 16 attacks as specification judgments.
   Keep every execution NOT_RUN. Informal arguments are not formal proofs.
7. Retain reviewer judgments, then compare R6.6 conclusions and publisher findings.
   Preserve unresolved disputes. Evaluate A/B/C and implementation feasibility
   separately; repair/inconclusive findings take priority over minimality claims.

## Stop and publication

Publish audit, identities, matrix/witnesses, obligations, reconstruction,
adversarial review, disagreement record and bounded next experiment. Update
entry-point prose additively; preserve prior artifacts, kernel 26 and all
implementations. Verify byte identities, links/inventory, unchanged tracked
protected paths and git diff --check. Execute no language or acceptance checks.
Stop after publication; further work requires explicit owner authorization.
