# P6-A03 exact preserved source verification

Verified UTC `2026-10-08T15:45:35.193051+00:00`, after the persisted fresh snapshot.
Source: R5.116A `captures/redis__redis/candidate-06-source.json`, repository
`redis/redis` (numeric ID 156018), issue 13736 (numeric ID 2779820455,
node `I_kwDOAAJhcs6lsLGn`), https://github.com/redis/redis/issues/13736.
Reporter: `mgravell`, numeric ID 17328, association CONTRIBUTOR.
Title: **[BUG] ACL @read and @write - should they include "select" ?**

Created `2025-01-10T10:22:51Z`; updated `2025-01-10T10:43:25Z`; retrieved
`2026-10-08T13:55:07.762848+00:00`. Revision is the exact retrieved title/body,
not a reconstructed creation-time revision or newer issue. Default-branch revision
metadata `940a4d72fc7caaed6f853b65b39920ff3fb9ac1f` identifies the saved metadata,
not a behavioral baseline or inspected implementation.

| Artifact/encoding | Verified SHA-256 |
| --- | --- |
| provenance physical bytes | 6e80510ddc07ea3acfa8819d470e6eafc761d8e676215d8849677e81c3ff6fc4 |
| source physical bytes | 90132320ad5aa7e7c3996ed97096a798a9ecceea76927a9f9c1948bda58d9970 |
| title UTF-8 | f1b15dd7c777881979721a84aeb0beff4dcfded5686a5fd07fb0b7fbce911089 |
| body UTF-8 | 568764f7390f21f06b50682fc385168116f572b764615dada8b0893963ef3952 |
| saved issue API | a475af91352cef86a3789ff60341fe0c2b33203b54c4f29452bf6864d4c7d843 |
| saved search | 1bca158867971beac0e0d1cfb2c39554d168020615ff2826fdaae8c18f626f40 |
| saved repository metadata | 5e5dfbd19d70b61085bee474b0e139200621da01662479ae74e09bb8b047f0c9 |
| saved default-ref metadata | 5fbe86b66c4b34171a92f4934b9c6e44726d8200252a56b033e6639027085521 |
| preserved curation acceptance | 1b891b5cc09d11849e6dbafbec59f1c25840e68769d7c1e8268798a7071b6c09 |

Six provenance-named artifact hashes, title/body hashes and equality with saved
issue API, issue number/ID/node/URL, and reporter login/ID all passed (11 checks).
Publication verifier additionally checks repository identity and issue timestamps.
Only P6-A03 provenance-named captures are read by that verifier. No batch-wide
source/acceptance verification or later-source content access.

No source refetch, comments, linked StackExchange ticket, fixing PR, commit or
implementation access. The `+select` snippet is the reporter's user-configuration
workaround, not a server fix. Current API labels/state are not behavioral authority.
The source is an attributable reporter proposal; neither Redis maintainer approval
nor product authority is established. Selection order 3 and policy commit
`c840083469efc9f94920ebce41103a51092ac915` are preserved.

R5.116A acceptance is historical same-agent candidate evidence. The new plan is
reconciled directly to preserved source, without generated implementation or oracle
execution. Previous curation exposure and SAME_AGENT/SAME_MODEL review are disclosed;
no blinded, held-out or cognitive-independence claim.
