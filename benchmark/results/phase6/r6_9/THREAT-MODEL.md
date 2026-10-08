# R6.9 isolation threat model

Trust boundary: an exposed publisher prepares bytes; a trusted local supervisor
validates them and controls transport; an independently approved adapter/model
receives only the authorized request. The supervisor and host administrator are
trusted, not adversarially contained by their own process. A seal anchor belongs
with the owner or independent evidence custodian, outside the writable evidence.

| Contamination channel | Implemented control | Executed evidence / remaining limit |
| --- | --- | --- |
| Inherited system/developer instructions | Build a new fixed system message and package-only user payload; no agent API | Injection/configuration rejection tested; actual provider hidden messages unverified |
| OpenCode guidance/configuration | No OpenCode import or agent launch; reject guidance markers; sandbox has no config mounts | Fresh Python process tested; unconfined guidance-file access negative control succeeds; real sandbox unavailable |
| Nonallowlisted repository files | Validate exact package; broker exposes only listed bytes; planned sandbox mounts only staged input and adapter | Broker denial, unexpected-file, symlink and hardlink rejection executed; cwd-only OS access negative control succeeds |
| Session/history/shared memory | New UUID request; reuse configurations refused; no conversation input or memory tool | Fresh subprocess has no parent Python globals; provider sessions/caches/preloaded context not independently inspected |
| Retrieval/indexes/search | Tool-free invocation; explicit retrieval-disabled contract; broker denies search | Broker enforcement and configuration checks executed; a provider's internal retrieval remains unverified |
| Environment/provider config | Empty explicit environment; provider/model and adapter hash mandatory; no ambient SDK | Synthetic environment sentinel absent in actual fresh child; no credentials accessed or stored |
| Network/external tools | Offline static adapter profile; Linux unshared network/filesystem namespaces and no tool permissions | Command construction tested with mocked transport only; actual unconfined loopback access succeeds; sandbox path NOT_RUN |
| Shared writable state | Private staging and sandbox `/work` tmpfs; input/adapter read-only mounts | Plan/configuration checks only for sandbox; no real hostile-adapter containment on this host |
| Model preloaded context | Explicit model ID/adapter pin and captured outbound contract | Provider-side weights, training exposure, hidden prompts, safety policy, caching and state are unverified |
| Publisher leakage | Neutral questions; frozen passage maps; local package filenames; no comparison material before sealing | Byte exclusions/reproduction tested; covert semantic bias/paraphrase cannot be excluded mechanically |
| Adapter substitution/failure | Exact adapter hash; no runtime imports/mounts; failure/timeout preserves partial output | Identity failure exercised; transport failure/timeout mocked, not live provider failures |
| Output/provenance alteration | Seal all record/output/stderr bytes; verify against separate expected anchor | Modification and resealing attacks rejected; hash does not authenticate author or defeat rewriting anchor and evidence together |

## Scope of enforceability

The file broker enforces its own data API, not arbitrary code execution. A fresh
process, `-I`, empty environment and explicit cwd enforce limited local input
properties; they do not isolate the filesystem/network. Three executed negative
controls deliberately demonstrate that distinction using synthetic files only.

Bubblewrap must be present on Linux, namespaces must actually be usable, and the
adapter must be a separately audited standalone executable needing no host library
mounts. Discovery of its executable is not qualification. This Windows host lacks
that backend. WSL reports no installed distribution; no environment was installed.
The runner fails closed before starting any reviewer/adapter process.

## Unverified assumptions and limitations

- No absolute isolation, statistical independence, absence of training familiarity,
  or provider-internal input exclusion is claimed.
- No online/provider-specific transport is implemented. A future remote provider
  needs a separately tested destination-restricted supervisor transport, no arbitrary
  redirects or tool calls, explicit account/session/data-retention configuration and
  captured effective API requests. Credentials must remain outside evidence and
  reviewer filesystem/environment.
- Standalone adapters may contain embedded context. Their exact bytes must be audited
  and approved; hashing alone is insufficient. Provider/model labels are declarations,
  not authenticated provider identities.
- Host administrator/publisher tampering and filesystem races in publisher-controlled
  source/evidence directories are outside the current trusted-host guarantee. Staged
  payload bytes avoid later source-mount mutation; they do not solve hostile-host races.
- Capture uses a 30-second timeout but has no independent memory/output-volume cap.
  Bubblewrap is not a complete hostile-code resource or side-channel boundary.
- The marker filter is defense in depth, not a classifier for paraphrased findings.
  Input dependency completeness and unbiased passage selection still need independent
  approval. No reviewer is eligible based only on a synthetic correct answer.
