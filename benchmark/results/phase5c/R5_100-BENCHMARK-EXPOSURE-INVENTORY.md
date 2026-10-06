# R5.100 — benchmark exposure inventory

**`R5_100_BENCHMARK_EXPOSURE_INVENTORY_COMPLETE`**

Date: 2026-10-06. Scope: retrospective bookkeeping using development-visible
evidence. No benchmark requirement was opened, searched, parsed or evaluated in
this round. Initial working tree was clean. R5.99 Lykoi implementation is unchanged.

## Interpretation and evidence basis

Exposure is measured across the documented **development history**, not solely
the current session or an isolated benchmark implementation agent. A request
can be unseen in a particular isolated context while already exposed to Lykoi
development. The strongest supported exposure label is used in the table;
`EVALUATED` is an accompanying, separate dimension. Evaluated does not mean
passed, behaviorally verified, or evaluated on the current R5.99 implementation.

The following existing records supply the evidence. References are to their
pre-R5.100 content; historical results and wording are preserved.

- **E1 — [research log](../../../docs/research-log.md), historical “Phase 5C
  invariant vocabulary restart” and “clock binding and format restart”.** These
  development entries explicitly record “Re-screening frozen B01–B16 text” and
  “Screening frozen B01–B16 text” (pre-update lines 3081–3104). This is evidence
  of historical direct requirement consumption in development, not merely case
  identifiers or isolated-track success. It covers every B01–B16 case. Its
  source-read history predates R5.97; R5.97's fresh-context first result remains
  immutable, but earlier blanket development-pristine wording cannot establish
  historical nonexposure under this inventory's definition.
- **E2 — [R2 progress](RESUME-R2-PROGRESS.md), lines 19–32.** Historical B01–B06
  track outcomes, including actual Conventional evaluations and Lykoi gap/block
  classifications. B04 was achieved by both tracks.
- **E3 — R3 [B07](RESUME-R3-B07-PROGRESS.md),
  [B08](RESUME-R3-B08-PROGRESS.md), [B09](RESUME-R3-B09-PROGRESS.md),
  [B10](RESUME-R3-B10-PROGRESS.md) progress reports.** Actual Conventional
  evaluations and Lykoi classifications; meaningful array/append, boolean,
  nonarchived/due-window and owner-input/filter disclosures respectively.
- **E4 — R4 [B11](RESUME-R4-B11-PROGRESS.md),
  [B12](RESUME-R4-B12-PROGRESS.md), [B13](RESUME-R4-B13-PROGRESS.md),
  [B14](RESUME-R4-B14-PROGRESS.md), [B15](RESUME-R4-B15-PROGRESS.md)
  progress reports.** Conventional acceptance executions; Lykoi blocks/gaps
  remain distinct from successful request-level behavioral evaluation.
- **E5 — [B16 result](B16-R5_2-RESULT.md), lines 11–44; and
  [corrected post-B16 boundary](R5_2_2-POST-B16-CORRECTED-CONTINUATION.md).**
  Conventional B01–B16 achieved; Lykoi {B01,B04}. B16's persisted users and
  cross-entity ownership validation are development-visible semantics.
- **E6 — [R5.97 report](R5_97-B03-HELD-OUT-EVALUATION.md), summarized in the
  research log's R5.97 entry (pre-update lines 68–98) and project overview.**
  Direct B03 access and a structural evaluation terminating at
  `DECISION_DISCOVERY_UNSUPPORTED` / native `STRUCTURAL_COVERAGE_FAILURE`.
  No B03 behavioral verification was reached in R5.97.
- **E7 — [R5.99 incident](R5_99-FIREWALL-INCIDENT.md), lines 3–19;
  [round report](R5_99-COLLECTION-QUERY-NORMAL-PATH-INTEGRATION.md), lines
  13–19, 137–147; [audit](R5_99-AUDIT.json), fields
  `b04_requirement_file_opened`, `b04_and_later_indirect_log_disclosure`.**
  Confirms accidental behavioral disclosure from historical logs, with no
  direct B04/later requirement-file opening in that round.
- **E8 — [existing development decision analysis](R5_3-SCOPE-AND-B17-B20-DECISION-ANALYSIS.md),
  lines 3, 39–51, 60.** Material B17–B20 summaries were already present in a
  development-authored historical report. B17 actor/role behavior is also
  recorded in the research log's typed-clock/dependency review (pre-update
  lines 3128–3135) and agent workflow. Line 60 explicitly discloses B18 audit
  history/rejected-no-entry/atomicity, B19 recurrence/completion/successor/audit
  effects, and B20 project/ownership permission interactions. These are
  semantic disclosures, not deductions from numbering. The report records
  B18–B20 not executed and prospective B17 work, not a B17 evaluation.

## Inventory

“Yes” below means an evaluation is documented somewhere in the preserved
history, including the Conventional track. It does not assert that every
Lykoi request received an executable candidate or acceptance run.

| Benchmark | Exposure status | Evaluated? | Evidence/reason |
| --- | --- | ---: | --- |
| B01 | `DIRECTLY_EXPOSED` | Yes | Public calibration and historical frozen-text reading (E1); historical evaluations (E2). |
| B02 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1), explicit R5.75 whole-set opening in research log; historical success/gap evaluations (E2). R5.75 remains indeterminate. |
| B03 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1), direct R5.97 access/structural evaluation (E6); earlier Conventional execution (E2). R5.97 behavioral stages not reached. |
| B04 | `DIRECTLY_EXPOSED` | Yes | Historical B01–B16 frozen-text reading (E1); both tracks achieved B04 (E2). R5.99 separately confirms indirect log disclosure (E7). |
| B05 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); input-dependent list-filter disclosure and Conventional execution (E2). |
| B06 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); input-dependent filter/trim disclosure and Conventional execution (E2). |
| B07 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); ordered array/append disclosure and Conventional execution (E3). |
| B08 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); boolean archival-state disclosure and Conventional execution (E3). |
| B09 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); nonarchived selection/due-window disclosure and Conventional execution (E3). |
| B10 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); owner-input/trim/filter disclosure and Conventional execution (E3). |
| B11 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); Conventional acceptance execution (E4). No unseen behavior inferred from supersession IDs. |
| B12 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); clock-relative deadline described in research log; Conventional acceptance execution (E4). |
| B13 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); Conventional acceptance execution (E4). |
| B14 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); array/append/graph and cycle-rule disclosures (E4, research log); Conventional acceptance execution (E4). |
| B15 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); dependencies/archival disclosed in progress report; Conventional acceptance execution (E4). |
| B16 | `DIRECTLY_EXPOSED` | Yes | Historical frozen-text reading (E1); persistent users/ownership disclosure and Conventional acceptance execution (E5). |
| B17 | `INDIRECTLY_EXPOSED` | No documented evaluation | Actor-required/existence, roles, read exemptions and owner permissions already described in development summaries (E8). Prospective analysis is not evaluation. |
| B18 | `INDIRECTLY_EXPOSED` | No documented evaluation | Audit history, rejected operations producing no entry, and atomicity already described in E8 line 60 (also line 41). |
| B19 | `INDIRECTLY_EXPOSED` | No documented evaluation | Recurrence, completion/successor and audit-entry effects already described in E8 line 60. |
| B20 | `INDIRECTLY_EXPOSED` | No documented evaluation | Project permissions and ownership/project interactions already described in E8 line 60. |

### Limits and historical reconciliation

Direct exposure is positively documented for B01–B16 by E1; it is **not**
attributed to R5.99's accidental search. Those cases also have development-visible
reports, so direct exposure does not imply absence of indirect exposure.
B17–B20 have confirmed material indirect exposure; direct access to their
requirements by the development agent is not established by the inspected
evidence. No complete-content consumption is inferred from a concise summary.

Older “B03 pristine” / “B17 unexposed” declarations are retained as historical
round/context claims. This prospective inventory does not rewrite any frozen
result, first-result record, checkpoint or achieved history. It records the
broader development-history contamination visible in their own documentation.

The original R5.99 grep response is not reproduced in the inspected persisted
R5.99 artifacts. The incident is a contemporaneous account of that response;
the report/audit do not enumerate its individual later-case hits. No search was
replayed, and historical implementation streams were not opened to manufacture
that missing transcript. Therefore **the exact case-by-case R5.99 accidental
disclosure scope remains unknown**. That provenance limitation does not make
any inventory row `UNKNOWN`: independent positive evidence establishes exposure
for all twenty cases. It also does not license claiming R5.99 disclosed B18–B20
specifically; their confirmed indirect exposure basis is E8.

## Exact R5.99 firewall failure

After the first full regression run and before a passing generic freeze,
`functions.grep` was requested with the exact file path
`D:\Dev\axiom\benchmark\results\phase5c\R5_99-VERIFICATION.json` and pattern
`FAIL|ERROR|Traceback|AssertionError|error:|Ran [0-9]+|tests":`.
The tool instead returned matches from the parent results directory, including
historical B03/B04/later implementation, prediction and regression logs carrying
behavioral descriptions. Delivery of those descriptions into development context
violated the no-semantic-exposure boundary. The requirement files themselves
were not directly opened. B03 transfer 2 was cancelled; this was no authorized
benchmark evaluation. The internal tool cause beyond the observed scope mismatch
is not established.

## Completion and selection boundary

- Directly exposed: **B01–B16** (historical development evidence).
- Indirectly exposed as strongest established label: **B17–B20**.
- Evaluated historically: **B01–B16**; R5.97 B03 was structural, not behavioral.
- `PRISTINE_BY_AVAILABLE_EVIDENCE`: **none**.
- `UNKNOWN` inventory rows: **none**; incident-hit attribution remains limited
  as stated above.
- No tests or benchmark runners were invoked. Documentation verification uses
  Git diff/status/whitespace checks only. Changes are this new report and minimal
  project-overview/research-log additions; no historical result file is edited.
- No requirement or candidate metadata was inspected to determine exposure.
- **`NEXT_HELD_OUT_CANDIDATE = NONE`**: no lowest-numbered pristine case after
  B03 exists in this inventory. No candidate was opened or evaluated.

Stop at this selection result. The next step is **not** to snapshot and run an
existing Bxx as genuinely held out. A separately instructed round must first
provide a genuinely new, development-unexposed evaluation source; then R5.96's
fresh snapshot → first access/exposure → unchanged-capability evaluation → first
terminal result discipline can apply. B01–B20 remain usable as exposed diagnostic
or regression cases, with their historical results preserved.
