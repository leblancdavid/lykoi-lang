# R6.44 bounded practical modification evidence

[Report](../../benchmark/results/phase6/R6_44-REPORT.md),
[protocol](PROTOCOL.md), [contract](CONTRACT.md),
[independent expected-impact map](EXPECTED-IMPACT.json).

Completed one bounded exposed-application comparison; stopped pending authorization.
All evidence is additive under benchmark/results/phase6/r6_44. Scripts use exclusive
creation for records so prior results cannot be silently overwritten.

Executed stages: run.py prepare; run.py revise_expectations; separate pre-author
review; run.py freeze; author.py A; author.py B; evaluate.py; summarize.py;
publication.py. These are a record of performed commands, not permission to rerun
authoring or comparison. Publication-only verification: `python -B
experiments/stateful_modification_r6_44/publication.py verify`.

run.py independently constructs requirement truth tables and records original/
accepted baseline behavior. author.py dispatches fresh same-model CLI sessions and
exports actual usage. evaluate.py performs external scoring, AI-free replay and
unscored inherited-error diagnostics. summarize.py preserves and corrects the old
sequence's false regression attribution using the frozen retained-step map.
Publication verifies protected, frozen and published identities without inference.
