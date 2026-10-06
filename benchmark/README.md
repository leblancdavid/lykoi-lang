# Phase 5: comparative maintenance benchmark

## Current fresh typed baseline — R5.103

The [fresh current-system report](results/phase5c/R5_103-REPORT.md),
[matrix](results/phase5c/R5_103-CAPABILITY-MATRIX.md) and
[three-round progression](results/phase5c/R5_103-PROGRESSION.md) evaluate every
B01–B20 case from a fresh typed source interpretation. **B01/B04/B05 local
behavioral success, fourteen structural blockers, B18 BDI and B17/B20 clarification**
form the new development baseline. B01 alone changes first result from fresh
representation reaching existing support; generic existing-semantic closures add
no further corpus first-result changes. Historical R5.101/R5.102 evidence remains
unchanged. No held-out generalization or cumulative achievement claim follows.
Stop after the typed mutable values/transformations recommendation for R5.104.

## Preserved corpus status — R5.101

**B01–B20 are an exposed development, transfer and regression corpus.**
Performance on B01–B20 is now development/regression evidence, not held-out
generalization evidence. Future generalization claims require a new
development-unexposed source; none is created by R5.101.

The [current capability report](results/phase5c/R5_101-B01-B20-CURRENT-CAPABILITY-REPORT.md)
and [matrices](results/phase5c/R5_101-CAPABILITY-MATRICES.md) record twenty local
attempts on unchanged Lykoi: B05 external success, sixteen structural halts,
B18 BDI halt and B17/B20 clarification. Local success is not cumulative Phase 5C
achievement. Historical protocols/results below retain their original scope;
old nonexposure wording is not today's corpus status. R5.101 is diagnostic only.

## R5.102 exposed transfer

The [normal-path report](results/phase5c/R5_102-NORMAL-PATH-REPORT.md) is
`R5_102_EXISTING_SEMANTICS_NORMAL_PATH_PARTIAL`. Its
[fixed twenty-case matrix](results/phase5c/R5_102-CAPABILITY-MATRIX.md) has two local
behavioral successes (B04/B05), fifteen structural first blockers, B18 BDI and
B17/B20 clarification. B04 uses fresh typed formalization; nineteen rows replay
R5.101 captures, so unchanged halts are not exhaustive current typed-formalization
results. R5.101 remains the immutable pre-development snapshot. These are exposed
regression outcomes, not held-out generalization or cumulative achievement.

## Current research path — R5.96

The [simplified benchmark protocol](../docs/research-workflow-r5.96.md) governs
prospective ordinary research and the next held-out evaluation. Use compatible
current Python/tooling and the currently available model. No machine, model,
OpenCode, runtime or transport qualification, infrastructure hash gate, protected
activation or controller authorization merely for benchmark access is required.
The historical comparative protocol and its amendments remain preserved below.

Before B03 access, take a fresh snapshot of commit/tree, tests, core/V1 versions,
model/provider when known, time and the declaration that B03 has never been inspected.
Mark B03 exposed at first access. Process/formalize with existing Lykoi, implement
if representable, independently verify and record the first terminal result before
any B03-informed change to Lykoi. Later attempts are post-exposure diagnostics.
R5.96 performed cleanup without B03 access. **R5.97 exposed B03** after the fresh
snapshot and recorded **`DECISION_DISCOVERY_UNSUPPORTED`**, native
`STRUCTURAL_COVERAGE_FAILURE`, before BDI/adequacy/V1/authoring/compilation or
behavioral verification. [The report and immutable first result](results/phase5c/R5_97-B03-HELD-OUT-EVALUATION.md)
retain the exact source, candidate-review limitations and stage accounting.
B03 is no longer pristine/unread; later B03 runs are post-exposure evidence.

Two task CLIs start from equivalent observable behavior. `conventional/task_manager.py`
is maintained as Python source. Track B's source of truth is the repository's
`air/task_manager.json`; `generated/task_manager.py` is its disposable executable.
Historical `experiments/` files are not benchmark working copies.

From the repository root, use the public external baseline and core checks; broad
historical discovery is optional and subject to held-out boundaries:

```powershell
python -m unittest discover -s benchmark/harness -p test_baseline.py -v
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p test_compiler.py -v
python -m unittest discover -s tests -p test_application.py -v
```

Read `baseline.md` for the external behavioral contract, `requirements/README.md`
for the ordered frozen requests, `harness/README.md` for the oracle protocol, and
`results/BASELINE.md` for baseline provenance. For execution progress and the
current acceptance boundary, see the [project overview](../docs/project-overview.md).
The prospective [bounded-bridge decision](results/phase5c/R5_4-BOUNDED-BRIDGE-DECISION.md)
stops exhaustive R5.3 reconstruction as the B17 prerequisite while preserving
its evidence; R5.2.2 remains authoritative and B17 is unexposed.
The [prospective B17 dependency adjudication](results/phase5c/R5_4-B17-PARTIAL-DEPENDENCY-ADJUDICATION.md)
preserves request-level classification through B20 and keeps independent
blocked-request clause observations separate from benchmark outcomes.
The original execution protocol below is retained as historical context;
later protocol amendments and checkpoints are documented under `results/`.

The prospective [R5.50 reproducibility boundary](results/phase5c/R5_50-BENCHMARK-REPRODUCIBILITY-BOUNDARY-REVIEW.md)
requires Tier 2 experimental reproducibility on a declared compatible platform,
with relevant implementation/authority/evaluator/dependency state bound and
immediate pre/post observation drift checks. Behavioral equivalence is the target,
not identical source or a fully hermetic machine. Development AI state belongs
to separate authoring/fairness records, not fixed-source language execution identity.
This methodology qualification does not authorize B02 exposure or resume Phase 5C.

The test harness treats both applications as subprocesses; it never imports
their internal modules or uses their internal test suites as the shared oracle.

## Execution protocol

New runs report `LYKOI_CAPABILITY_GAP` (and refer to Lykoi in the Track B
instruction). Existing benchmark records retain the historical
`AXIOM_CAPABILITY_GAP` outcome, which the harness still accepts when reading
recorded attempts. The original Track B instruction below is preserved for
comparability with those runs.

Use the same AI model/configuration, requirement text, tool limits and time
budget for both tracks. Give Track A only its conventional working tree and
Track B only its model, compiler, generated output, and normal Lykoi tools;
keep each track's experiment branch/working copy isolated. Do not reveal the
other track's solution to an agent. Preserve prompts, model/version, transcripts,
tool calls, elapsed wall time, token usage when available, git diff, test results,
and hashes at each step. Run B01, then B02, ... B20; accepted changes accumulate.

Track A instruction: "Implement the requested requirement in the conventional
Python application. Inspect the repository as needed. Python source is
canonical. Preserve prior accepted behavior and verify with the provided
external acceptance tests and relevant internal tests."

Track B instruction: "Implement the requested requirement in the Axiom task
application. The semantic model is canonical. Do not edit generated Python or
the frozen compiler/runtime/schema. Validate and regenerate normally. If the
frozen Axiom language cannot express the requirement, report
AXIOM_CAPABILITY_GAP with the missing concept and supporting validator or
generation evidence. Preserve prior accepted behavior."

Before each change, construct *backend-neutral* external acceptance cases from
that request and freeze them before either agent starts. Run all accumulated
cases on both tracks in fresh isolated directories and run their applicable
internal tests. Never rewrite an earlier baseline/requirement/oracle to make a
track pass. A compiler change during the primary run invalidates that Track B
step; separately studied extensions must be labeled as a different experiment.

If Track B reports a genuine gap, record it, leave B unchanged, and advance.
Where a later request needs a missing prerequisite, report BLOCKED_BY_GAP with
its ID; do not score that dependent request as a new failure or change the
requirement. Track A continues sequentially. Compare outcomes only on shared
achievable behavior; also report cumulative coverage lost to gaps.

For each step record: correctness against external oracle, old-case regressions,
attempts/rework, gap or blocked status, elapsed time and tokens/tool calls when
measurable, and separately a blinded reviewer judgment of change explanation
and inspectability (1–5 rubric: 1 cannot trace behavior; 3 traceable with
significant inference; 5 behavior, constraints, and impact readily traceable).
Mark missing telemetry N/A. Report raw evidence and denominators, not just an
aggregate score. A green validator or safety report is not a behavioral proof.
