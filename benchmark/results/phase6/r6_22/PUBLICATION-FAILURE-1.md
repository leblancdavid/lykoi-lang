# First publication verification failure

The first `python benchmark/results/phase6/r6_22/publish.py verify` invocation
failed before writing publication identities or receipt. The link checker demanded
that those two outputs already exist while checking the report's links to them:

```text
AssertionError: (WindowsPath('D:/Dev/axiom/benchmark/results/phase6/R6_22-REPORT.md'), 'r6_22/PUBLICATION-IDENTITIES.json')
```

This is a posthoc publication ordering defect. A correction defers existence checks
only for the exact two outputs being created, then checks both after writing them.
Frozen runner/protocol/manifest, all generation evidence and diagnostic halt are
untouched. No inference or tokenization follows this correction.
