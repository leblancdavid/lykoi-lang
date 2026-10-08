# R5.117 fresh evaluation snapshot — P6-A01 only

Recorded before opening the preserved P6-A01 body/acceptance record in this round.
User authorization: R5.117 only; unchanged pipeline, first terminal result, no repair.
Protocol: `docs/phase6-generalization-protocol-r5.115.md`, with R5.116A's disclosed
procedural sourcing amendment. Material is **externally authored, procedurally
selected evaluation material**, not independently blinded or pristine held-out.
Prior curation-session exposure is preserved; a fresh snapshot does not erase it.

## Baseline identity

- Initial UTC: `2026-10-08T14:14:00.2097307Z`.
- Git commit: `6b20be1332b9e81d7bdd7c075fd0bd9fa3a23221`.
- Root tree: `21f620ebb71880d684204c885570674a7157306c`.
- Initial `git status --short`, `git status --porcelain=v1 --untracked-files=all`
  and `git diff --stat`: empty; clean worktree, no local diff to retain.
- `git diff 185073db0667ab10cdf033c03846548f21b48fac -- src schema air generated
  tests benchmark/harness benchmark/evaluation benchmark/conventional`: empty.
  This is the R5.115 planning commit; implementation remains R5.114.
- CPython 3.14.3, Windows/PowerShell, workspace `D:\Dev\axiom`.
- Session model/provider: `openai/gpt-6.1-sol` / OpenAI, via OpenCode.
  Exact harness build/provider settings unavailable; no provider switch authorized.

| Scope | Git object identity |
| --- | --- |
| src | `d1dc40879ec31fc7b522ae8accd9e91ee7105233` |
| schema | `8c04839087c76ab111e1eabb05b3e14e6b36ca1c` |
| air | `c7abd1483a14cf0c1ca21dd8d2edd3ee3db7ca39` |
| generated | `d666daef4f362b2d4423e0be1942954ad4846bed` |
| tests | `6563e2c951d61f201d5abddc4f89aeeee5ad6148` |
| benchmark/harness | `7ddd8f7d201343816571a10646fed98dab3d8daa` |
| benchmark/evaluation | `68c94828b6b16ad5000d80cb999ff4ecc4233df1` |
| R5_114-KERNEL-ACCOUNTING.json blob | `cb0f5c566149fae770e270bdbe71d456a03fe8b9` |

The exact proposed kernel is **26**, identified by the unchanged R5.114 ledger
and the numbered inventory in `docs/phase5-baseline-r5.115.md`. No additions,
removals or reclassifications. This is an architectural hypothesis, not minimality.

## Versions

FRC `FormalRequirementContract-0.1`; legacy compiler/backend `0.3.0`; canonical
model `0.3`; normal dispatcher `LykoiProgram-1`; representation `LykoiContractV1`;
sealed pipeline `sealed-pipeline-1`; external plan `external-cli-plan-1`.
Profile inventory is exactly the R5.115 baseline: `collection-query-1`,
`existing-scalar-1`, `existing-model-1`, `existing-composed-1`,
`typed-mutable-values-1`, `typed-input-values-1`, `typed-predicates-1`,
`persistent-references-1`, `atomic-durable-state-1`, `primary-value-interfaces-1`,
`prewrite-authorization-1`, `typed-computation-1`, `elapsed-day-conversion-1`,
`conditional-created-effects-1`, `historical-related-state-1`.
Version labels are supplemented by the exact unchanged source subtree above.

## Fresh checks before source access

`PYTHONPATH=src`; the tool transcript retains complete output. All five commands
completed successfully, with no observed failure:

| Exact command | Result |
| --- | --- |
| `python -m air_compiler.cli validate air/task_manager.json` | `Lykoi validate: ok` |
| `python -m air_compiler.cli safety air/task_manager.json` | 0 capability violations; 0 invalid transitions; 5 runtime-enforced / 1 structurally guaranteed invariants |
| `python -m unittest discover -s tests -p test_compiler.py -v` | 22 pass, 0.052 s |
| `python -m unittest discover -s tests -p test_application.py -v` | 9 pass, 2.419 s |
| `python -m unittest discover -s benchmark/harness -p test_baseline.py -v` | 3 pass, 3.882 s |

34 fresh regression tests, not P6-A01 acceptance and not a 397-test rerun.
R5.114's 397-test receipt, 133 synthetic invocations and 16/20 exposed corpus
successes remain historical evidence. R5.115's baseline record is preserved.

## Fixed finite attempt budget

One source-bound candidate formalization and one same-agent source reconciliation;
one review of exact preserved source, recorded curation questions and already approved
policies. No online lookup, comments, fixing PRs/commits, project implementation or
conventional jq invocation. No independent reviewer/human answer is supplied with
this authorization; record unavailable authority rather than manufacture it.
If material questions remain after this review, publish `NEEDS_CLARIFICATION`.
No clarification retry, alternative model, or downstream attempt after that halt.
If authorized downstream work is possible: one authoring attempt, no repairs, maximum
30 minutes from source access for the attempt. Provider-call count/token telemetry
unavailable; no new live provider adapter. P6-A02–P6-A05 are outside this round.

Normal formalization discipline: WHAT-only candidate, source traceability, material
uncertainty retained, conventions not authority, no synthetic human approval.
The workspace implementation's `formalize` is a producer interface rather than an
English parser and stamps source `SYNTHETIC`; external evidence will not be mislabeled
or passed through invented human/controller credentials. Manual source-bound FRC
candidate evidence and the existing FRC validator are sufficient for this
clarification-first attempt; no claim of independent reconciliation is permitted.
