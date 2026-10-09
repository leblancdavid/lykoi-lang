# First publication verification failure

After inference and report drafting, the first `publish.py verify` exited1:

```text
File "publish.py", line168, in verify
  assert (report.parent/link.split('#')[0]).exists(),link
AssertionError: r6_20/VERIFICATION.json
```

The posthoc verifier checked links to its own not-yet-created manifest/receipt
before writing them. This is a publication-ordering defect, not a participant or
frozen diagnostic-runner failure. No model request was retried. Prospective fix:
allow only the two known pending receipt paths in the preliminary check, then
recheck every report link after publication files exist. The frozen runner,
schemas, prompts, controls and results are unchanged.
