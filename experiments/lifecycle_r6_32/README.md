# R6.32 — AI-free lifecycle and modification qualification

Final classification: **`R6_32_LIFECYCLE_PARTIAL`**.

- [Qualification report](../../benchmark/results/phase6/R6_32-REPORT.md)
- [Frozen bounded protocol](../../benchmark/results/phase6/r6_32/PROTOCOL.md)
- [Admission/retrieval/successor/edit specification](SPEC-1.md)
- `lifecycle.py`: immutable registry, deterministic admission/retrieval, caller updates,
  hash-linked durable telemetry and reconstruction.
- `edit.py`, `fixture.py`: copied exposed production-backed fixture and pinned edit.
- `qualify.py`: registry/stateful/recovery witnesses, no model calls.
- `test_lifecycle.py`: fourteen focused durability/type/dependency regression methods.

Primary completed evidence: `benchmark/results/phase6/r6_32/attempt-5/` and
`supplement-2/`. Earlier attempts are retained with exact diagnostics; their counts
are not pooled into final capability denominators. No production code was edited.

Focused tests:

```powershell
python -B -m unittest discover -s experiments/lifecycle_r6_32 -p test_lifecycle.py -v
```

Read-only publication integrity check:

```powershell
python -B experiments/lifecycle_r6_32/publication.py verify
git diff --check
```

The runner requires a fresh attempt name and cannot overwrite prior evidence.
Any further functional qualification or pilot remains subject to explicit owner
authorization; these recipes do not authorize H1/H2 or AI authoring.
