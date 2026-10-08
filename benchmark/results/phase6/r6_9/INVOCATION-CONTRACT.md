# R6.9 provider-neutral invocation contract 1

`review-boundary-1` separates responsibilities and never imports the language
implementation or an AI-provider SDK.

| Layer | Contract |
| --- | --- |
| Input | External expected package SHA-256, exact manifest/file set, purpose and approved obligations |
| Adapter | Separately approved standalone executable, exact SHA-256, explicit provider and model labels |
| Model invocation | One canonical JSON stdin request; new UUID; fixed system message; package-only user content; no previous messages, agent session or implicit configuration |
| Tool permissions | Explicit array; implemented offline execution accepts only `[]`; retrieval disabled |
| Environment/network | Explicit empty environment and `network:none` for the implemented offline profile |
| Capture | Raw stdout and stderr plus return code; empty output, nonzero exit and timeout halt; partial output retained |
| Provenance | Version, package/config/runner identities, exact request, execution backend/cwd/file/runtime/environment/tool/network declarations, outcome and limitations |
| Sealing | Raw output, stderr and canonical provenance hashes in canonical seal; separately retained seal SHA-256 required for verification |

Changing provider/model labels does not change questions, allowed context, effects,
tool policy, sealing or the meaning of the contract. No OpenAI identity, credentials,
account format or execution ID is required. UUIDs are local invocation correlation
IDs, not provider attestation. No credentials have been requested or discovered.

## Implemented runner

```powershell
python -m tools.reviewer_isolation.boundary run-synthetic PACKAGE PACKAGE_SHA256 CONFIG.json ADAPTER NEW_EVIDENCE
python -m tools.reviewer_isolation.boundary verify-seal NEW_EVIDENCE EXTERNAL_SEAL_SHA256
```

Configuration has exactly these keys:

```json
{"provider":"synthetic-local","model":"literal-fixture-1",
 "adapter_sha256":"<64 lowercase hexadecimal characters>",
 "environment":{},"tools":[],"network":"none","session":"new",
 "retrieval":"disabled","system_message":"Use only the supplied synthetic input."}
```

No environment/configuration credential channel is supported. An independently
audited adapter could embed a local model or talk to a dedicated model service only
in a later separately implemented transport profile. Do not embed credentials in
adapters, model labels or output. Current profile is offline and exposes no sockets,
host runtime libraries, repository, home directory or tool executables by design.

Linux command construction uses bubblewrap `--unshare-all`, `--new-session`,
`--die-with-parent`, `--clearenv`, `--cap-drop ALL`, read-only staged `/input` and
`/adapter` mounts, a private `/work` tmpfs, and explicit `--chdir /work`. No host
runtime tree is mounted. That branch was **not executed or qualified here**.
The candidate package remains undispatched regardless of backend availability.

## Status and refusal semantics

`SEALED_SYNTHETIC_UNQUALIFIED` means captured synthetic bytes only. It is never
independence, infrastructure qualification or a semantic verdict. There is no
code path that produces a qualified-review status in R6.9.

Package mismatch/unexpected resources, contamination markers, undeclared operational
dependencies, excess tools/environment, reused sessions, retrieval/network expansion,
adapter substitution, unavailable controls, failed adapter or missing provenance
halt. Refusals are sealed when storage is available. If sealing/verification itself
fails, the utility raises/fails and cannot report qualification. Output evidence
directories must be new; existing failures cannot be overwritten by retrying.

Hash seals detect modification relative to a trusted external anchor. They are not
signatures, immutable storage or authentication. The verifier never treats printed
success text as authority. Later qualification must check actual access denial and
effective provider requests, not accept configuration claims or this report alone.
