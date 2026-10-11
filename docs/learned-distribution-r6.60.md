# R6.60 learned-distribution boundary

[Report](../benchmark/results/phase6/R6_60-REPORT.md):
**`R6_60_TARGET_LIKELIHOOD_IMPROVED`**. Exact R6.59 step20 adapter and pinned
Qwen2.5-Coder1.5B/checkpoint/tokenizer/R6.52 environment pass identity checks.
Dropout-off/no-grad paired E01–E06 completion+EOS evaluation improves all six
record losses: equal-record1.647022→1.504801; pooled2,326-token1.627591→1.487384
nats/token. Symbolic operations/references/output definitions improve along with
formatting. This is exposed target fitting, not generalization or valid generation.

No training/evaluation template or prompt mismatch was found. All12 preserved
responses first diverge at character0/token73594 markdown fence and omit required
package-envelope keys. Original0/6 versus0/6 scores remain unchanged. Low but
increased first raw-package token probabilities and gold-prefix/free-running
conditioning differences plausibly explain coexistence of improved likelihood
and failed generation; fence probability/rank and penalty causality remain open.

Initial mask-hash and offline prompt-hash assertion mistakes are preserved and
disclosed; original serializer conventions were verified, no model/mask/prompt
changes occurred and no outcome-informed evaluation rerun was performed.
No optional generation probes, optimizer updates, training, expansion, semantic
changes, Python comparison adapter, historical rescoring or P6-A04/P6-A05 access.
Kernel26 and AI-independent execution preserved. Stop after publication.

Smallest recommended separately authorized step: frozen first-position competing
token logits/ranks for raw-package4913 versus fence73594, with read-only inspection
of historical repetition penalty1.1 versus identity1.0. No automatic continuation.
