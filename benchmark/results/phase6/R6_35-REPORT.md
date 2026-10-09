# R6.35 — OAuth connection verification and symbolic lifecycle retry

**Final classification: `R6_35_PROTOCOL_HALT`.**

The one authorized bounded successor stopped at working-connection verification,
before a neutral model request. The selected model label matches the working
harness and R6.33/R6.34, but the effective working-session OAuth route and endpoint
could not be established safely. The owner's explicit instruction to stop when
the working route cannot be identified governs this outcome.

## Sanitized connection findings

- Installed OpenCode: **1.18.32**.
- Current harness identifies **openai/gpt-6.1-sol**. Five recent assistant metadata
  records corroborate that label; they do not uniquely bind the active session or
  attest its authentication route. Only provider/model/finish fields were queried.
- Supported `opencode auth list` lists OpenAI credentials as **OAuth** and also
  lists an **OPENAI_API_KEY** environment route. No credential store or credential
  table was read. Environment values were never printed, copied or exported.
- The child CLI's resolved configuration has no configured default model, no
  agent-specific model overrides, zero configured plugins, and only an Ollama
  provider override. No OpenAI baseURL/apiKey/header override appears there.
  This is fresh CLI configuration, not an attestation of an already running
  desktop session's loaded configuration.
- R6.33/R6.34 selected the same OpenAI/model label. Their effective authentication
  and endpoint were unattested. R6.34 also had OPENAI_API_KEY present and its
  child environment set `OPENCODE_PURE=1` and
  `OPENCODE_DISABLE_DEFAULT_PLUGINS=1`. These flags are an integration difference
  worth investigating; they do **not** prove a particular credential was selected
  or establish the cause of either HTTP429.

See [route audit](r6_35/ROUTE-AUDIT.json) and
[session metadata](r6_35/SESSION-METADATA.json). Resolved configuration was filtered
in memory through an allowlist; raw configuration and command stderr were not
published. Stored OAuth plus successful current conversation is insufficient to
prove which endpoint/authentication branch a new experiment subprocess would use.
No assumption was made that `credit_balance_exhausted` was temporary.

## Gate and lifecycle outcomes

| Stage | Result |
| --- | --- |
| Selected provider/model label comparison | MATCH |
| Effective working-session OAuth route/endpoint | UNVERIFIED — terminal gate |
| Tiny neutral request / four-tool neutral discovery | NOT_REACHED |
| Successful-access lifecycle configuration freeze | NOT_REACHED |
| Reusable composition proposal, validation, admission, retrieval | NOT_REACHED |
| Two pinned callers and original execution | NOT_REACHED |
| Staged modification and signature-preserving successor | NOT_REACHED |
| CallerA migration / CallerB predecessor retention | NOT_REACHED |
| Frozen functional observations | NOT_REACHED; no pass denominator |
| AI-independent replay | NOT_REACHED; no authored executable artifacts |

[Terminal result](r6_35/RESULT.json) records zero participant model/tool calls,
semantic broker calls, corrections, registry/retrieval operations and artifacts.
No provider request was dispatched, so no new provider error was observed and
provider access was not tested. This is a protocol halt, not a demonstrated
provider-access block or model-authoring gap. No substitute composition was
manually authored. Frozen acceptance and dependency expectations were preserved.

The coordinator read historical reports containing lifecycle summaries to compare
the routes. No participant received lifecycle requirements; no blind or independent
coordinator claim is made. No new requirement or acceptance expectation was created.

## Measurements and authoring effort

[Measurements](r6_35/MEASUREMENTS.json): **0 participant inference invocations,
0 tool calls, 0 correction attempts, 0 admissions/retrievals/migrations**.
The audit script's protected-hash/configuration interval was **1.2933234 seconds**.
That excludes earlier orientation, other metadata commands and publication, and
is not total effort. Semantic authoring, execution and replay timings are
NOT_REACHED. Participant token measurements are NOT_REACHED. Coordinator input,
output, reasoning, cached tokens and fully costed preparation/publication effort
are **unavailable**, not measured zero. No efficiency claim follows.

## Preservation and publication

The initial worktree was clean. [Baseline](r6_35/BASELINE.json) verifies **3,103
protected SHA256 identities**, extending R6.34's preserved baseline with its
publication and receipt. R6.33's input freeze is checked byte-for-byte. R6.3–R6.34
history, production compiler/lowerer/runtime, R6.10 VM, R6.18 wrapper, R6.23 adapter
and R6.25 contracts remain unchanged. Production remains **26 constructs** on
the inherited verified accounting basis; no new kernel derivation is claimed.

Only additive R6.35 audit/evidence/report/addendum files are published. The
publication manifest and verification receipt in `r6_35/` verify protected hashes,
new publication identities, relative links, additive whitespace, unchanged tracked
files and `git diff --check`. Publication verification executes no model or
acceptance workload. No full H1/H2 trial, P6-A04 acceptance or P6-A05 access occurred.

## Limitation, recommendation and stop

The remaining blocker is **effective-route attestation**, not lack of a stored
OAuth credential. Recommended next separately authorized experiment: expose a
supported, credential-free diagnostic for the active OpenCode session's selected
authentication type and endpoint, including API-key/default-plugin precedence;
then one neutral request with retries disabled and a bounded deadline. A diagnostic
must establish the existing working route without reading/exporting tokens or
switching credentials. Lifecycle requirements should remain gated behind that
access result. No purchase or provider change is recommended here.

**Stopped after this one bounded verification attempt and publication. Further
diagnosis, preflight or lifecycle authoring awaits owner authorization.**
