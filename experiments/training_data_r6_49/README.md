# R6.49 bounded stateful training-candidate pilot

See [report](../../benchmark/results/phase6/R6_49-REPORT.md),
[protocol](PROTOCOL.md) and [tier policy](../../docs/training-data-admission-r6.49.md).
All scripts use stdlib and existing repository semantics. Outputs are immutable
exclusive-create records. They must not overwrite historical or published evidence.

Completed execution order from repository root:

```powershell
python -B experiments/training_data_r6_49/prepare.py
# Actual OpenCode apply_patch constructs AI-INTENT files after source freeze.
python -B experiments/training_data_r6_49/build.py
# Original validator rejection retained; real AI correction then successful build.
python -B experiments/training_data_r6_49/replay.py --pass-id 1
python -B experiments/training_data_r6_49/review.py
python -B experiments/training_data_r6_49/replay.py --pass-id 2
python -B experiments/training_data_r6_49/transcript.py
python -B experiments/training_data_r6_49/dataset.py
python -B experiments/training_data_r6_49/publication.py --publish
python -B experiments/training_data_r6_49/publication.py --check
git diff --check
```

The transcript records actual construction; rerunning scripts cannot reproduce
AI choices and must not claim to do so. Functional replay reloads the sealed
applications and uses one process per request, independent of AI. Reproduction
in a separately authorized disposable copy may remove only that copy's new
replay outputs, then run both replay commands and compare observation hashes.
In this published tree, use the read-only publication `--check`; generation
commands intentionally refuse to replace their original outputs.

The pilot is stopped. No training command or new semantic primitive exists.
