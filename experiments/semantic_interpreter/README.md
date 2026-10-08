# R6.10 executable semantic interpreter experiment

One pure operation VM processes CFG66, DSV66 and BXC66 through explicit versioned
JSON plans. See [semantic contracts and assumptions](CONTRACT-1.md),
[reuse/gap accounting](OPERATION-MATRIX.md), and
[adversarial coverage](ADVERSARIAL-RESULTS.md).

Run from the repository root in PowerShell:

```powershell
python -m unittest discover -s experiments/semantic_interpreter -p test_interpreter.py -v
python experiments/semantic_interpreter/baseline.py verify
```

To reproduce the authored plans/schema, run:

```powershell
python experiments/semantic_interpreter/build_plans.py
```

This deterministic authoring tool writes only the experiment's JSON files. The
VM executes their operations directly. It contains no CFG/DSV/BXC dispatch or
opaque parsing library. `execute(plan, input_bytes, limits=None, assemble=True)`
is the in-memory API. Input acquisition and evidence publication are separate
host tools; plans cannot invoke them. Tests use synthetic inputs only.

`BASELINE.json` captures HEAD, frozen publication identities and hashes of 219
protected files before interpreter implementation. `publish_evidence.py` executes
the suite, records ten identical executions per witness, and writes a fresh
`evidence/` directory; it refuses to overwrite an existing publication. Timing
in the test transcript is host elapsed time, not semantic logical work.

This remains experimental and partially typed, outside the 26-construct production
kernel. No production compiler/runtime/verifier integration is provided. Stop after
R6.10 publication; any next experiment requires owner authorization.
