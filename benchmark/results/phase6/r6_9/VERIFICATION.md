# R6.9 verification record

Executed infrastructure evidence is retained in `evidence-final/qualification.json`,
`evidence-final/test-output.txt` and the sealed `evidence-final/host-attempt/` refusal. The
external host-attempt seal anchor is retained in the qualification record; an owner
must separately retain that anchor before treating it as tamper evidence.

Final collection: **28/28 pass, no skips**. The initial orchestration halt and its
test transcript remain in `evidence/`; see `evidence/ATTEMPT-HALT.md`. Windows
negative controls explicitly allow `SystemRoot` to initialize Winsock. This is
not an exception to the runner's empty environment or successful isolation evidence.

Package identity:
`b2f178d0db9951e3f2ef781403e1d678921a1f7cd76b7328daf7553dec13e440`.
Actual host refusal seal:
`c77bd4567e059006da7e429e82bd6a7315553301f428d3bbeaf2e514527b6038`.
`PUBLICATION.json` pins all delivered file bytes (self excluded), records the scope
check and checks whitespace in untracked publication files as well as `git diff --check`.

`tools/reviewer_isolation/qualify.py` runs synthetic tests and fresh-process negative
controls. It never passes candidate definitions to an adapter/model. Test names
ending in `mock_transport_only` explicitly replace subprocess transport: they test
failure/capture/provenance and command construction, not Linux isolation.

| Evidence category | What it establishes |
| --- | --- |
| Actual package verification | Deterministic export; pinned source bytes; payload identities; byte exclusion checks; filesystem resource rejection |
| Actual broker operations | Forbidden-file/search calls refused by the data API |
| Actual fresh subprocess | Explicit cwd, no synthetic secret variable or parent Python global/history, isolated Python startup, exact stdin |
| Actual negative controls | Unconfined subprocess can read forbidden/guidance files and connect over loopback despite cwd/env/startup controls |
| Configuration/request tests | Session/guidance/retrieval/tool/env constraints and provider-label invariance; no provider-side attestation |
| Mocked adapter transport | Success remains unqualified; failed/timeout output retained; no actual adapter/model invoked |
| Actual seal verification | Altered output/resealed output rejected against retained anchor; incomplete provenance refused |
| Actual host attempt | Unavailable sandbox fails before dispatch and preserves sealed refusal |

Reproduce to a new directory:

```powershell
python -m tools.reviewer_isolation.qualify NEW_EVIDENCE_DIRECTORY
python -m unittest discover -s tools/reviewer_isolation/tests -v
git diff --check
```

The candidate export is preparation work, not a semantic test. No compiler/model/
runtime checks or acceptance checks were needed for infrastructure-only edits.
Frozen language and historical research files are preserved. Substantive reviews,
provider model invocations, format implementations and P6-A04 acceptance executions
are zero. P6-A05 was not accessed.
