# Lykoi decision — R6.55

Adopt all exact installed AdamW defaults for previously unspecified fields;
preserve lr1e-4 and weight_decay0 overrides and the R6.54 scheduler. Retain None for
foreach/fused rather than choosing an implementation dispatch mode. Publish canonical
optimizer identity independently of the incomplete full training inventory.

Apply the owner's stop rule to unspecified sampling order and accumulation-loss
weighting. Do not infer these from a seed or a single-record backward probe. Keep
unreached diagnostic, training and trained-adapter results explicit; preserve prior
classifications and measurements. See the [report](../benchmark/results/phase6/R6_55-REPORT.md).
