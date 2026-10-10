# Decision supplement — R6.41

## Preserve raw semantics, request provenance authority

[Investigation](../benchmark/results/phase6/R6_41-REPORT.md) explains the failures
without declaring compact artifacts correct from equal values. Preserve R6.40
scores, submitted artifacts and frozen expectations. Retain R6.18's established
expanded seq-span/work behavior; do not silently rebase errors or flatten regions.

Prospective recommendation: preserve raw operation/node/Cell-site/work and keep
symbolic definition/local/caller paths separately using existing artifacts. This
improves attribution without conflating authored coordinates with input-byte blame.
Use independently frozen representation-aware node correspondence only where
requirements justify it. Exact input-byte obligations remain exact.

Tradeoff: region spans are mechanically faithful but often weak causal-byte
explanations; full arithmetic input ancestry needs an explicit additional interface.
Maps support bounded node origins today, not complete expression/text coordinates
or cross-edit semantic identity. Human clarification determines which provenance
is required before future qualification. No implementation or contract adoption
is authorized by this recommendation. Stop after documentation publication.
