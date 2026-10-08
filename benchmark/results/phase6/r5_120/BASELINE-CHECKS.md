# R5.120 fresh baseline checks

Run after first terminal boundary result was persisted; no P6-A03 pipeline retry,
authoring, executable generation, Redis probe or acceptance execution. Existing
synthetic suites exercise their public fixtures, not the approved Redis contract.
Synthetic test credentials confer no authority on the real P6-A03 attempt.

From repository root, `$env:PYTHONPATH='src'`; each command exited **0**:

| Command | Result |
| --- | --- |
| `python -m unittest discover -s tests -p test_research_authority.py -v` | 22 passed |
| `python -m unittest discover -s tests -p test_authority_controller.py -v` | 34 passed |
| `python -m unittest discover -s tests -p test_requirements_workspace.py -v` | 26 passed |
| `python -m unittest discover -s tests -p test_sealed_pipeline.py -v` | 30 passed |
| `python -m unittest discover -s tests -p test_compiler.py -v` | 22 passed |
| `python -m unittest discover -s tests -p test_application.py -v` | 9 passed |
| `python -m unittest discover -s benchmark/harness -p test_baseline.py -v` | 3 passed |
| `python -m air_compiler.cli validate air/task_manager.json` | Lykoi validate: ok |
| `python -m air_compiler.cli safety air/task_manager.json` | 0 capability violations, 0 invalid transitions; 6 invariants |

**146 tests passed.** These are unchanged baseline/synthetic authority checks,
not Redis behavior or real-principal authentication. Full historical 397-test
R5.114 evidence remains historical, not rerun.

Existing read-only integrity command also exited 0:
`python -m benchmark.results.phase6.r5_119a.verify_revision`.
Output: `Publication identities: PASS`,
`PASS_NOT_APPROVAL_OR_BEHAVIORAL_VERIFICATION`. Recomputed identities are recorded
in [ARTIFACT-INTEGRITY.json](ARTIFACT-INTEGRITY.json). No controller approval or
behavioral observation is inferred from these checks.
