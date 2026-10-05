# R5.82 public discovery experiment

Inputs are explicitly `corpus.json`, `expected.json`, and the already-public
`r5_80/candidates.json` (selecting B01). No requirement-directory discovery,
protected source/metadata inspection, runner or static-consumer invocation occurs
in the new experiment. Existing guarded V1 regression tests retain their own
public/synthetic scope. The executable emits complete per-case BDIs and evidence
to stdout; `results.json` records compact measured results, not generated software.

* [BDI specification](../../../../docs/behavioral-decision-inventory-v0.1.md)
* [Report](../R5_82-BEHAVIORAL-DECISION-DISCOVERY.md)
* `corpus.json`: 26 public synthetic cases, including six hidden interactions.
* `expected.json`: separate manually reviewed expectations, 29 decisions,
  12 enumerated irrelevant choices, witnesses and unresolved review questions;
  revision 2 discloses one correction to the original 30-decision expectation.
* `experiment.py`: discovery, 11 mutations, four finite-domain implications,
  six plan pairs, R5.81 local integration and conditional B01 calibration.
* `review.json`: independence accounting and coordinating review limits.

Reproduce at repository root, without writing evidence:

```powershell
python -B -S -m benchmark.results.phase5c.r5_82.experiment
python -B -S -m unittest benchmark.evaluation.test_behavioral_discovery_r5_82 benchmark.evaluation.test_implementation_adequacy_r5_81 -v
python -B -S -m unittest benchmark.evaluation.test_formal_requirements_r5_80 benchmark.evaluation.test_benchmark_documents_v1 -v
$env:PYTHONPATH='src'
python -B -S -m unittest discover -s tests -v
git diff --check
```

Expected records are same-context manual analysis, not independent source-owner
review. A reviewed structural declaration is not an automatic natural-language
extraction. Mutations modify the structural capsule and append an explicit change
annotation; they do not re-formalize prose independently. Plans are declarative
residual strategies and predicted outputs, not independent producers or whole
applications. B01 legacy absence is conditional, not a newly asserted baseline fact.
Stop after R5.82. No grants, held-out opening, V1 expansion or Lykoi changes.
