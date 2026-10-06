# R5.98 — exposed-source obligation sanity review

This is a fresh analytical review by the active research agent, before any
Lykoi implementation change in R5.98. It is **not** a blind separate-context,
separate-model, owner-approved or held-out review. The R5.97 report and candidate
were visible. Independence here means checking the inventory against the original
source and shared contract, rather than assuming the prior inventory is correct.

Authority read: `benchmark/requirements/B03.md`, `benchmark/baseline.md`,
`benchmark/requirements/README.md`; comparison: `R5_97-FRC.json` and the inventory
table in the R5.97 report. No other requirement or hidden acceptance oracle read.

## Findings

| Recorded item | Fresh source check |
| --- | --- |
| 001 interface | Confirmed: explicit command and runtime argument; shared JSON interface applies. |
| 002 selection | Confirmed: collection **membership**, not scalar-field equality; all qualifying records, not one arbitrary match. |
| 003 case | Confirmed: case-sensitive, reinforced by the example. |
| 004 whitespace | Confirmed: matching input is not trimmed. Validation can inspect whitespace without changing the match value. |
| 005 inclusion | Confirmed: completed records remain eligible. |
| 006 ordering | Confirmed with context: shared contract specifies `(created_at, id)` ascending. |
| 007 validation | Confirmed: empty/whitespace-only rejected with declared code; shared stderr/exit-1 interface applies. |
| 008 empty result | Confirmed: no match is `[]`, not null or an error. |
| 009 effect | Confirmed: no storage change, including rejection under the shared error frame. |

**Nine behavioral obligations confirmed. Disputed: 0. Missing local behavioral
obligations: 0. Invented behavioral obligations: 0.** Cumulative compatibility,
stored-state validation and migration behavior are inherited context, not erased
by this local inventory or requalified here.

Interpretation caveats: “never changes storage” reasonably preserves bytes and
file absence, but those words are an operational refinement rather than a literal
source quote. “Whitespace-only” does not declare a Unicode whitespace algorithm;
the candidate leaves that unresolved detail rather than defining one. “Exactly”
does not independently specify Unicode canonical-equivalence processing. No such
extra processing should be inferred. These bounded ambiguities do not invalidate
the nine-item inventory. Synthetic development must declare its own precise text
domain/policies and must not silently claim those choices as B03 source authority.

The source demonstrates a structural bridge failure, not a compiler failure.
`B03_FIRST_RESULT = DECISION_DISCOVERY_UNSUPPORTED` and native
`STRUCTURAL_COVERAGE_FAILURE` remain immutable. B03 is permanently exposed.
