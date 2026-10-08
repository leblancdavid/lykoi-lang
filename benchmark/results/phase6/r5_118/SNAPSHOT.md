# R5.118 fresh pre-access snapshot — P6-A02 only

Recorded before opening P6-A02 provenance, source or acceptance bodies. Authorization:
user request R5.118 only. Protocol: Phase 6 generalization protocol R5.115 with
R5.116A procedural sourcing amendment. Externally authored, procedurally selected
material; not independently blinded or pristine held-out.

## Git and chronology

- Initial observation UTC: `2026-10-08T14:25:33.8943887Z`.
- Initial HEAD: `6b20be1332b9e81d7bdd7c075fd0bd9fa3a23221`.
- Initial dirty state: modified AGENTS.md, README.md, docs/agent-workflow.md,
  docs/project-overview.md, docs/research-log.md; untracked R5_117-REPORT.md and
  r5_117/. These were pre-existing R5.117 publication work, not R5.118 edits.
  Initial diff stat: five tracked files, 62 insertions, one deletion.
- During collection, that work was committed externally as `0934907` (`r5.117`);
  the evaluation agent issued no commit command. Stable pre-access HEAD:
  `09349071c6c63154bcbe82e02e6f2fd2d002ab3c` at
  `2026-10-08T14:26:26.4390328Z`, clean worktree before this snapshot was added.
  The pre-existing publication is retained in this commit rather than overwritten.
- Stable root tree: `bc1a548c71540164be5dce6b421562e0f1b8e9be`.
- Diff from R5.115 planning commit `185073db0667ab10cdf033c03846548f21b48fac`
  over src/schema/air/generated/tests/benchmark harness/evaluation/conventional: empty.

| Scope | Git tree identity |
| --- | --- |
| src | d1dc40879ec31fc7b522ae8accd9e91ee7105233 |
| schema | 8c04839087c76ab111e1eabb05b3e14e6b36ca1c |
| air | c7abd1483a14cf0c1ca21dd8d2edd3ee3db7ca39 |
| generated | d666daef4f362b2d4423e0be1942954ad4846bed |
| tests | 6563e2c951d61f201d5abddc4f89aeeee5ad6148 |
| benchmark/harness | 7ddd8f7d201343816571a10646fed98dab3d8daa |
| benchmark/evaluation | 68c94828b6b16ad5000d80cb999ff4ecc4233df1 |

## Semantic and runtime identity

Implementation R5.114; proposed kernel **26**, unchanged ledger blob
`cb0f5c566149fae770e270bdbe71d456a03fe8b9`. No additions/removals/reclassifications.
FRC `FormalRequirementContract-0.1`; compiler/Python backend `0.3.0`; canonical
model `0.3`; dispatcher `LykoiProgram-1`; representation `LykoiContractV1`;
pipeline `sealed-pipeline-1`; external plan `external-cli-plan-1`.
Profiles: collection-query-1, existing-scalar-1, existing-model-1,
existing-composed-1, typed-mutable-values-1, typed-input-values-1,
typed-predicates-1, persistent-references-1, atomic-durable-state-1,
primary-value-interfaces-1, prewrite-authorization-1, typed-computation-1,
elapsed-day-conversion-1, conditional-created-effects-1, historical-related-state-1.
Exact versions and bounds remain docs/phase5-baseline-r5.115.md.

CPython 3.14.3; Windows/PowerShell; workspace D:\Dev\axiom.
Model/provider: OpenAI `openai/gpt-6.1-sol` via OpenCode. Harness build/settings
unavailable. No switch authorized.

## Fresh tests before access

PYTHONPATH=src; complete command output retained in session transcript:

| Command | Result |
| --- | --- |
| python -m air_compiler.cli validate air/task_manager.json | ok |
| python -m air_compiler.cli safety air/task_manager.json | zero capability violations/invalid transitions; 5 runtime-enforced, 1 structurally guaranteed invariants |
| python -m unittest discover -s tests -p test_compiler.py -v | 22 pass, 0.054 s |
| python -m unittest discover -s tests -p test_application.py -v | 9 pass, 2.584 s |
| python -m unittest discover -s benchmark/harness -p test_baseline.py -v | 3 pass, 4.322 s |

34 fresh regression passes; not P6-A02 acceptance or a 397-test rerun.
Historical R5.114 verification remains preserved.

## Fixed attempt budget and method

One exact-source review, one WHAT-only candidate and one same-agent source
reconciliation/materiality review using existing policies; no online lookup,
comments, fixing PRs, solutions, curl invocation or next-source access. One
existing FRC envelope validation. No live provider adapter or invented credentials.
No independent reviewer or owner approval is supplied. Missing material decisions
or required approval terminate NEEDS_CLARIFICATION, with those causes separated.
If legitimate authorization exists: one downstream authoring attempt, no repair,
maximum 30 minutes from source access. Stop at first terminal result; no rerun.
Implementation freedom is assessed by material observable consequences, not by
requiring a change request to respecify its entire application. Prior R5.117
result and source are not reopened or reinterpreted.
