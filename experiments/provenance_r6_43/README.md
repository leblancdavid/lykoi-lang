# R6.43 observation-only successor qualification

[Report](../../benchmark/results/phase6/R6_43-REPORT.md) and
[contract](OBSERVATION-1.md). The small sidecar labels existing raw observations;
run.py's transparent hooks separately collect raw decode/return/charge events.
No production, VM, wrapper, registry or saved representation is edited.

One preparation and one execution were run:

```powershell
python -B experiments/provenance_r6_43/prepare.py
python -B experiments/provenance_r6_43/run.py
```

These commands refuse to replace published freezes/results. Do not rerun the
qualification into this round. Review is pre-execution and independent of candidate
outputs, but has no independent human/cognitive attestation. See PREEXECUTION-REVIEW.

Read-only publication integrity check after publication:

```powershell
python -B experiments/provenance_r6_43/publication.py --verify
```

This verifies files and archived evidence and runs no plan or model. Benchmark
readiness documents are proposals/assessments, not an initiated comparison. Stop
after publication; further execution requires explicit authorization.
