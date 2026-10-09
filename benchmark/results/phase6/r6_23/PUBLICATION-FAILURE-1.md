# First posthoc accounting failure

`python benchmark/results/phase6/r6_23/publish.py analyze` applied the recorded
privacy filtering, then stopped before writing measurements. The warmup has an
explicit null preflight; the accounting generator used `.get()` on that null.

```text
AttributeError: 'NoneType' object has no attribute 'get'
```

Publisher correction treats absent/null preflight as an empty accounting record
and avoids repeating already recorded privacy substitutions. No frozen runner,
schema, task, adapter, model output, halt or endpoint evidence was modified.
No inference/tokenizer/network request was issued by this publisher.
