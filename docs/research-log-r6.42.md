# R6.42 research observations

[Report and evidence](../benchmark/results/phase6/R6_42-REPORT.md): one prospective,
model-free, unscored experiment, **`R6_42_PROVENANCE_PARTIAL`**.

- Exact expansion preserves16 nodes and all nested seq boundaries. Compact/exact
  agree on78 default and1,169 cutoff comparisons; repeated calls preserve shared
  definition pins and distinct call paths. A new experiment-local registry reloads
  the exact dependency closure.
- Flat retains12 nodes and functional behavior on39 inputs/two passes. Eleven
  inputs per pass expose post-return offsets2 versus0/1. Work differences0/2/6/8
  reflect real entered/completed sequence boundaries; equal budgets can diverge.
- The frozen oracle's numeric UInt8 origin tuples are wrong. Public envelope/work/
  order expectations pass234/234 defaults and3,307/3,307 cutoffs;228 default and
  2,839 cutoff trace expectations fail. Actual numeric origins are empty. Retain
  all failures; no outcome-informed oracle repair or rerun.
- Ten unsupported-provenance/identity controls reject and28 positive node-pair/
  origin claims pass. Existing mappings support node/definition/local/call paths;
  they do not supply authored-text coordinates or integer operand ancestry.
- Eight unchanged R6.18 and14 unchanged R6.32 regression methods pass. Preserve
  4,987 identities, production kernel26, historical publications and scores.

Same-coordinator semantics-derived expectations are prospectively frozen but not
independently human-reviewed. This finite synthetic witness demonstrates no AI
authoring/generalization benefit or universal equivalence. Stop after publication.
