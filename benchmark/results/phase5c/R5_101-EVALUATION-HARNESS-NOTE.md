# R5.101 evaluation bookkeeping observation

The first execution of `R5_101-evaluate.py` reached B01–B17 and then B18.
B01–B16 printed their current outcomes (B05 verified; the other fifteen
structural), B17 printed formalization clarification. B18 returned the native
`UNSUPPORTED_BDI_SCOPE`: the `effects` relation is accepted by the existing
structural bridge, but discovery reports `unsupported_observation` with
`rule_for:external_effect` missing for each obligation. Adequacy and later stages
were not reached.

The evaluation script's bookkeeping initially recognized only structural failure
or success and raised an assertion for this legitimate third outcome, before
publishing its JSON. This is an **evaluation-harness classification defect**, not
a Lykoi runtime failure. The terminal B18 output was visible in the tool transcript;
its native classification is preserved here. No implementation or interpretation
was repaired. The evidence-only script was extended to record this existing BDI
halt, then the same twenty captures were run to publish complete evidence. This
does not change capability. No product harness, schema, mapping, semantic,
compiler, BDI, adequacy or backend file was changed.
