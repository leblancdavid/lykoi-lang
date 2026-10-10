# R6.48 training-data process pilot

Separate stdlib-only nonproduction experiment. See the
[report](../../benchmark/results/phase6/R6_48-REPORT.md) and
[protocol](PROTOCOL.md). Baseline implementations are imported unchanged.

Stages actually executed:

```powershell
python -B experiments/training_data_r6_48/prepare.py
python -B experiments/training_data_r6_48/construct.py
python -B experiments/training_data_r6_48/replay.py --pass-id 1
python -B experiments/training_data_r6_48/replay.py --pass-id 2
python -B experiments/training_data_r6_48/replay.py --pass-id 3
python -B experiments/training_data_r6_48/dataset.py
python -B experiments/training_data_r6_48/publication.py --publish
python -B experiments/training_data_r6_48/publication.py --check
```

Generation commands refuse preexisting output files. Published records are
immutable; these commands are not permission to replace or rerun this round.
`publication.py --check` is read-only integrity verification. To reproduce the
generation process after separate authorization, use a disposable repository
copy with the R6.48 generated output directory absent, preserve the source-side
scripts and compare candidate and observation hashes; timestamps are run-local.
The first publication invocation failed on a schema/reference checker bug; its
manifest is retained, and the corrected invocation issued manifest v2. Publication
history records this actual session. Fresh source/artifact/replay reproduction
does not recreate that historical failure; use `--check` on the published bundle
for publication reproduction rather than attempting to overwrite its receipts.

Eight finite-accepted experimental episodes have scripted construction traces,
not AI semantic tool trajectories. Two sources need clarification and two whole
contracts have capability gaps. All twelve lack independently qualified
provenance. Zero training export entries; no training, downloads or dependencies.
