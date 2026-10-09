# R6.18 minimal typed symbolic composition prototype

**`R6_18_TYPED_COMPOSITION_SUPPORTED`** — bounded deterministic mechanics only.
This standard-library experiment does not modify production Lykoi or the R6.10 VM.

## Deliverables

- [Bounded protocol](PROTOCOL.md), [semantics/validation rules](SEMANTICS-1.md),
  [versioned schema](typed-composition-1.schema.json).
- `composition.py`: strict loading, typing, closed references/dependencies,
  cycle/order/capture checks, content identity and bounded hygienic expansion.
- `examples.py`: reusable bounded addition, nested increment and independently
  authored expanded VM twins. Both contexts pin identical bounded-addition meaning.
- `pair.symbolic.json` / `header_increment.symbolic.json`: complete serialized uses.
  Corresponding `.expanded.json`, `.explicit.json`, `.expansion-map.json` artifacts
  publish deterministic plans and definition/local-site mappings.
- [Raw results](RESULTS.json): all25 rejected representation attempts and six rejected
  serialized inputs,511 runtime/control entry traces, three exhaustive full-result
  digests per context, structural/time/allocation measurements and scalar failures.
- [First test failure](FAILED-ATTEMPT-1.md) and [interrupted evidence attempt](FAILED-ATTEMPT-2.json)
  retain failures and corrections; the second retains the full original runner.
- [Baseline](BASELINE.json), [publication hashes](PUBLICATION-IDENTITIES.json),
  [verification receipt](VERIFICATION.json).
- [Prototype report](../../benchmark/results/phase6/R6_18-REPORT.md).

## Checking the published experiment

From repository root:

```powershell
python -m unittest discover -s experiments/typed_composition_r6_18 -p test_composition.py -v
python experiments/typed_composition_r6_18/preservation.py
python experiments/typed_composition_r6_18/verify_publication.py --replay
```

The verifier replays the complete bounded domain in a fresh process and checks
saved controls, expansion maps and publication bytes without overwriting results.
The generation runner refuses to overwrite `RESULTS.json`. Timings are observations
from the published run, not timing determinism claims. No inference or provider
dependency is present; all task computation is the original VM.

Stop after publication. Smallest recommended future experiment: qualify two ordered
failing checks and their dependent result across nested reuse, explicitly contrasting
reference/literal substitution with materialized bindings and VM span/work behavior.
That experiment requires new owner authorization; the full R6.17 study remains future.
