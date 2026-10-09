# Initial baseline verification observation

Before adapter implementation, the baseline checker required every R6.18
publication entry to equal the current workspace. It stopped on `AGENTS.md`.
R6.19's existing preservation policy deliberately protects the R6.18 experimental
files/report, while successor guidance has later identities. This is a historical
guidance supersession, not a newly modified VM/wrapper or altered old manifest.

The corrected checker records each historical mismatch only when the same path
already has a matching later protected identity and is shared guidance. All
dedicated round artifacts must match; historical manifests are themselves pinned.
No model inference occurred and no historical file was edited.

The second checker invocation stopped because the finite shared-guidance allowlist
omitted root `README.md`. Inspection of the original R6.18 manifest identified
that entry; it was added under the same matching-later-protected-identity rule.
Both preparatory failures precede experiment implementation and inference.

```text
AssertionError: AGENTS.md
```
