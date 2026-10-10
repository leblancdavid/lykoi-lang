# Lykoi decision — R6.54

Close only the explicitly authorized scheduler gap using the exact installed
Transformers linear-warmup/linear-decay semantics, including its zero initial LR and
optimizer-before-scheduler order. Freeze used-update and post-update rates separately
to avoid an off-by-one description. Microsteps and skipped updates do not tick.

Halt on the remaining required AdamW beta/epsilon gap. Library defaults are inspectable
but were not adopted as experiment settings; the owner forbids inventing additional
values. Recommend one complete prospective optimizer decision, then one bounded smoke.
See the [amendment](../benchmark/results/phase6/r6_54/SCHEDULER-AMENDMENT.md).
