# R6.73 research observations and decisions

[Report](../benchmark/results/phase6/R6_73-REPORT.md) and
[current-boundary supplement](project-overview-r6.73.md):
`R6_73_CONTRASTIVE_SUPERVISION_QUALIFIED`. Historical root overview/log/decisions
are publication-pinned, so these observations and tradeoffs are additive.

## Observations

The original S11 mask admits a duplicate-dependency prefix with no legal terminal.
Thirty-five saved tokens reproduce;94,366 next ASCII pieces reject despite a closing
brace token. Compact finite-language prefix membership removes that late-only mismatch.
All19,500 unique nonterminal character prefixes have a pinned token-extension witness.
This is CPU qualification, not actual model generation or inference benefit.

Eighteen positive compact decisions reconstruct deterministically;54 fixtures pass
unchanged VM execution. Thirty-six negatives divide4 schema/18 semantic rejection/14
valid wrong decisions; two wrong shared-prefix relations are behaviorally equivalent
and require exact semantic-target scoring. All26 adversarial controls pass. Eligible
SFT rows contain only correct assistant targets; negative choices appear only in user
inputs of corrective rows. No reasoning trace is fabricated. No model is loaded.

## Tradeoffs and limits

Explicit deps are retained rather than silently derived: they remain supervised
choices, checked against mechanically computed direct references. Derived result types
reduce redundant output without changing semantics. Scope-bounded complete syntax
enumeration prevents the observed dead end but is not arbitrary JSON Schema decoding;
it admits semantically wrong decisions and does not choose answers.

Canonical wire order needed one preserved failed CPU qualification and a fresh successor;
content-preserving serialization changes no chosen operation/operand/dependency. Initial
helper-import failures and a pre-execution expectation amendment are retained. No history
is repaired or rescored. Dataset categories overlap; no renaming is a new behavioral
family. Training correction hints and result-type scope obligations can be shortcuts.
Independent reviewer/withholding unavailable; proposed evaluation remains exploratory.

## Decision and stop

Recommend one separately authorized CPU-only integration preflight, then possibly one
fresh-adapter test with a precommitted bounded54-update budget. Four passes of54 eligible
rows motivates this budget, not an optimality assertion. Frozen base diagnostics and
identical final-adapter evaluation must precede any learning claim. Production kernel26,
compiler/lowerer/runtime/VM/history remain preserved. Stop after this publication.
