# R6.10 publication verification

Initial clean HEAD: `4f138419960652720502d396ee816116447c14ef`.
Baseline recorded before interpreter implementation: 219 protected tracked files,
26 frozen publication hashes (including the complete six-file R6.6 specification
publication inventory), kernel 26. R6.3–R6.9 round paths/reports and production
src/schema/air/generated/tools remain raw-byte identical to the baseline manifest.

Executed final qualification:

```powershell
python experiments/semantic_interpreter/build_plans.py
python experiments/semantic_interpreter/publish_evidence.py
python experiments/semantic_interpreter/baseline.py verify
python experiments/semantic_interpreter/verify_publication.py
git diff --check
git status --short
```

The final suite reports **82 tests, 0 failures, 0 errors, 0 skips** on Windows
AMD64 Python 3.14.3. `evidence/tests.txt` preserves test names and outcome;
`TEST-RESULTS.json` records environment/denominator. Reproducibility records ten
identical runs per format including values, provenance, bytes and logical work.
Publication verification replays those saved observations in a fresh Python process
and checks the captured implementation SHA-256 identities. This is local repeatability,
not independent cognition or formal verification.

Only six current guidance files are modified, insertion-only; new files are the
dedicated experiment and R6.10 report. Historical guidance text remains an exact
line subsequence. `git diff --check` checks tracked edits; the verifier separately
checks new publication files for trailing whitespace. Publication identities cover
source, plans/schema, tests, evidence, report and guidance, excluding the identity
file itself. SHA-256 is byte identity, not authentication or immutable storage.

The interpreter never loads benchmark requests/oracles or invokes production
compilation. The one correspondence test imports the pure predicate evaluator;
all operands are synthetic. No production test/acceptance suite was run. P6-A04
acceptance **0**, P6-A05 access **0**, provider/reviewer calls **0**, kernel **26**.

Preserved limitations: incomplete full static typing, external typed-value encode
qualification and precise encode field paths, exact R6.6 cost equivalence and
lowering proof; Unicode/recursive/streaming/physical operations not implemented.
No independent-review qualification inferred from R6.9. Stop after publication.
