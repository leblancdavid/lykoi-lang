# R5.81 public adequacy experiment

Only `corpus.json` and the exact already-public R5.80 `candidates.json` and
`reviews.json` are loaded by the experiment. No requirement-directory discovery,
protected ledger, static consumer, program generation or benchmark observation.

- `corpus.json`: 16 bounded synthetic cases and paired variants.
- `coverage.json`: coordinating relevance inventory, witnesses and semantic limits.
- `experiment.py`: deterministic sidecars, seven clause removals, internal removal,
  executable residual plans, five public-contract results; full JSON to stdout.
- `results.json`: recorded compact outcomes and command observations.
- `review.json`: independent attempt, two review passes, corrections/disagreements.
- [Specification](../../../../docs/implementation-adequacy-v0.1.md).
- [Report](../R5_81-IMPLEMENTATION-ADEQUACY-QUALIFICATION.md).

Reproduce from repository root without writing artifacts:

```powershell
python -B -S -m benchmark.results.phase5c.r5_81.experiment
python -B -S -m benchmark.evaluation.test_implementation_adequacy_r5_81
python -B -S -m benchmark.evaluation.test_formal_requirements_r5_80
python -B -S -m benchmark.evaluation.test_benchmark_documents_v1
git diff --check
```

The corpus is hand-authored experimental source, not automatically extracted
human intent. Positive classifications are profile-local and coverage-review
dependent. Synthetic fidelity assertions in authorization tests are fixtures,
not real source-owner approvals. Results grant no actual implementation authority.
