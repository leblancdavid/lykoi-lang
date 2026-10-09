# R6.36 — OAuth configuration repair and symbolic lifecycle retry

**Final classification: `R6_36_AI_LIFECYCLE_SUPPORTED`.**

The corrected child-process plugin configuration supported successful access.
The neutral request completed, all four construction tools were discovered, and
GPT-6.1 Sol completed the five frozen symbolic lifecycle stages on first proposals.
Original acceptance passed **338/338** observations; final acceptance passed
**594/594**. Three fresh AI-free replay passes each reproduced **594/594** with
identical full observation digests. No model-authored semantic decision was repaired.

This is a bounded, exposed synthetic feasibility result. It does not establish
independent discovery, generalization, H1/H2 support or a development-efficiency
advantage. The successful configuration is observed; the effective OAuth branch
and endpoint were not exposed by safe runtime diagnostics and remain unattested.

## Authorization, correction and preserved history

One separately authorized successor to R6.33–R6.35 was attempted. Existing
OpenCode **1.18.32** was used without modification. The exact child-only correction
in [environment evidence](r6_36/ENVIRONMENT-CHANGE.json) is:

```python
env = os.environ.copy()
env.pop('OPENCODE_DISABLE_DEFAULT_PLUGINS', None)
env.update(OPENCODE_PURE='1', ...)
assert 'OPENCODE_DISABLE_DEFAULT_PLUGINS' not in env
```

The flag was absent, not assigned another string. External-plugin isolation
remained enabled. `OPENAI_API_KEY` was inherited unchanged, with no global
environment change or value inspection. Stored OpenAI OAuth was confirmed using
supported `auth list`. No private credential store, token copy, authentication
header injection, manual endpoint redirect, provider switch or purchase occurred.

The initial worktree contained untracked R6.35 publication files. Those files
were verified and preserved, not replaced. R6.35's existing verifier passed
**3,103 protected identities and10 published files**. The successor
[baseline](r6_36/BASELINE.json) verifies **3,115 protected SHA256 identities**, all
three historical publication manifests/receipts and the exact R6.33 input freeze.
Historical classifications remain:

- R6.33: `R6_33_PROTOCOL_HALT`, with its original HTTP429 preserved.
- R6.34: `R6_34_PROVIDER_ACCESS_BLOCKED`, with its neutral HTTP429 preserved.
- R6.35: `R6_35_PROTOCOL_HALT`, with zero dispatched inference calls preserved.

Their failures have not been reinterpreted as successful OAuth attempts.

## Neutral preflight and configuration freeze

One fresh OpenCode child received only this [neutral request](r6_36/NEUTRAL-PROMPT.txt):

> Reply NEUTRAL_OK followed by the names of all four available Lykoi construction tools. Do not invoke tools.

It returned:

> NEUTRAL_OK r636_lykoi_admit r636_lykoi_execute r636_lykoi_retrieve r636_lykoi_validate

[Preflight result](r6_36/PREFLIGHT-RESULT.json): exit0, one completed model step,
zero tool invocations, zero errors, **12.516273 seconds**, **302 input /34 output
tokens**. The MCP server also recorded `tools/list`, independently confirming
schema discovery. No lifecycle requirement was sent to that preflight session.

R6.33 used a host JSON-action broker with no callable author tools. The additive
[four MCP adapters](../../../experiments/ai_lifecycle_r6_36/tools.py) expose
unchanged R6.32/R6.18 validation, admission/explicit migration, exact retrieval and
execution. They add no semantic operations. Their descriptions contain no task
examples or expected outputs. Discovery succeeded; semantic MCP invocation was
not exercised because the preserved R6.33 syntax requests JSON broker actions.
The actual lifecycle below exercised the existing host broker and registry.

[Route evidence](r6_36/ROUTE-EVIDENCE.json) contains no safe observed endpoint or
loaded-plugin name. Raw stderr and credential-bearing headers were not published.
Stored OAuth, built-in-plugin eligibility and successful access do not uniquely
attest the selected authentication branch. The configuration repair worked for
access in this attempt; it does not causally prove which credential was used.
No coordinator retry occurred; CLI-internal HTTP attempts are unavailable.

After preflight, [lifecycle freeze](r6_36/LIFECYCLE-FREEZE.json) bound OpenAI /
`gpt-6.1-sol`, requested **high** reasoning, child plugin/environment settings,
four schemas, broker/scorer source, authoring budgets, and every R6.33 frozen
requirement/acceptance identity before lifecycle exposure. A separate authoring
session was launched. Configuration remained unchanged after participant results.

Budgets:15 model CLI invocations maximum,3 proposals per stage, at most2 native
diagnostic corrections per stage,24 participant tool calls,600s per invocation
and1200s total authoring. Five invocations were used; no corrections were needed.
Effective provider reasoning remains unattested; requested variant and reported
reasoning-token usage are recorded separately.

## Lifecycle and functional acceptance

The exact [R6.33 protocol](../../../experiments/ai_lifecycle_r6_33/PROTOCOL.md)
and scorer were reused. Only transport/orchestration was adapted for this round.
All proposal bodies, retrievals, admissions, migration, expansion/provenance maps,
raw sanitized events and session export are saved in `r6_36/`.

| Stage | Observed result |
| --- | --- |
| Reusable typed BoundedScore proposal | Accepted first proposal; ordered x/y checks, bounded checked sum and bias |
| Immutable admission and retrieval | Exact SHA256 predecessor admitted and retrieved |
| Two callers | CallerA and CallerB separately authored; both compose the same predecessor pin |
| Original validation/execution | **338/338** observations; both ordering checks pass |
| Staged modification | Released only after original acceptance; signature-preserving surcharge2 successor accepted |
| CallerA update | Explicit immutable CallerA successor changes only dependency/call pins |
| Total migration | Explicitly selects new CallerA and retains old CallerB |
| Final verification | **594/594** observations; all three ordering checks pass |
| AI-independent replay | **594/594** on each of three runs; identities/dependencies/telemetry verified |

BoundedScore predecessor:
`81a03fd951da7af6a5e25c8f1e922664f36ba69b7bcde53530f10fd00322479c`.

BoundedScore successor:
`354406290a75b7f2ebc5ef144940d946ad7af0bc5e437021213050ad32250f65`.

[Dependency evidence](r6_36/DEPENDENCY-IMPACT.json) contains exact caller identities,
successor edges, total migration decisions and selected roots. Old definitions
remain saved and unchanged. Original A returns x+y+7 within limit300; modified A
returns x+y+9. Retained B returns x+14 for x<=189 and otherwise SUM_LIMIT.

[Original acceptance](r6_36/ORIGINAL-ACCEPTANCE.json) and
[final acceptance](r6_36/FUNCTIONAL.json) cover the frozen64 A byte pairs, all256 B
byte values, truncation/trailing/input-type controls, ordered rejection precedence,
signed negative/overflow/encode-range probes and representative logical-work cutoffs.
Expected semantic rejection is distinct from provider/runtime infrastructure failure.
There were no provider errors or unexpected infrastructure exceptions in this attempt.

## AI-independent replay and provenance

Authoring terminated and [closure](r6_36/AUTHORING-CLOSED.json) was written before
a new Python replay process. Replay contains no model dispatch. All three runs
match full result envelopes, errors, traces, expanded plans and logical work; the
stable row digest is:

`c12cf1c24033f207eab53edfb6261c36776fe74998e3a97c0392c17cb4d6924a`.

[Replay](r6_36/REPLAY.json) records three passes, **1,782 repeated observations**,
not1,782 distinct test inputs. [Replay integrity](r6_36/REPLAY-INTEGRITY.json)
reconstructs registry and journal, verifies all five immutable definition identities,
predecessor/successor edges and selective migration against the independently
specified frozen dependency map. [Provenance](r6_36/PROVENANCE.json) verifies saved
definitions equal the raw model proposals after only mechanical `c.seal`, and
migration equals the exact model request. Original error sites/check order and
signature are preserved in the successor. Expansion maps are retained.

The unchanged R6.33 replay function emits its historical
`R6_33_AI_LIFECYCLE_SUPPORTED` label inside this round's raw `REPLAY.json`.
That inherited scorer label is retained transparently; the authoritative successor
classification is [R6.36 RESULT.json](r6_36/RESULT.json). No historical R6.33 result
was overwritten or reclassified.

## Measurements and effort

[Measurements](r6_36/MEASUREMENTS.json) preserve actual step-finish usage and
separate overlapping timing intervals:

| Measurement | Observed result |
| --- | --- |
| Neutral / lifecycle CLI model invocations | **1 /5** |
| Participant callable tool invocations | **0**; four schemas discovered |
| Host broker registry operations | **4 admissions,38 retrievals,1 migration**; retrievals include evaluation probes |
| Correction turns / coordinator semantic repairs | **0 /0** |
| Authoring input / output / reasoning tokens | **13,921 /2,579 /124** |
| Authoring cache read / write tokens | **5,248 /0** |
| Authoring total reported tokens | **21,872**; preserves OpenCode's separate token buckets |
| Combined preflight + authoring reported tokens | **22,208** |
| Authoring CLI intervals summed | **100.843251 seconds** |
| Lifecycle interval including export | **103.545753 seconds** |
| Registry admission / retrieval time | **0.011352 /0.066913 seconds** |
| Original / final validation-expansion time | **0.000731 /0.001648 seconds** |
| Original / final acceptance interval | **0.130171 /0.356222 seconds** |
| Three replay intervals | **0.098948 /0.104489 /0.099260 seconds** |

Admission includes validation; expansion belongs to acceptance. These intervals
overlap and must not be added as independent effort. Isolated migration timing
is unavailable in the unchanged registry. Provider HTTP count, effective route,
effective reasoning, actual subscription/billing cost, coordinator tokens and fully
costed preparation/publication effort are explicitly unavailable. OpenCode's cost
counter0 is not proof of a USD0 bill. No paid-credit purchase occurred.

## Preservation, limitations, recommendation and stop

Only additive R6.36 files were published. Production remains **26 constructs**
on the preserved historical accounting basis. Compiler/lowerer/runtime,
R6.10 VM, R6.18 wrapper, R6.23 adapter, R6.25 contracts and all protected
R6.3–R6.35 evidence are unchanged. Publication verification checks protected
hashes, both new freezes, publication identities, relative links, credential
redaction, additive whitespace, unchanged tracked files and `git diff --check`.
No full H1/H2 study, P6-A04 acceptance or P6-A05 access occurred.

Remaining limits: capability-tailored exposed requirement, same-platform model,
coordinator-known oracle, no comparative control, no effective-route attestation,
and no exercised semantic MCP tool calls. The frozen scorer asserts functional
values/error codes and selected ordering conditions; complete error/trace/work
envelopes are checked for deterministic replay, not against a separate comprehensive
oracle. This supports this bounded AI-authored lifecycle only.

**Recommended next experiment:** a separately frozen small unseen composition and
selective-migration task using the now-accessible configuration, with actual calls
through the four MCP adapters and a requirement-derived error-site/order oracle.
Freeze budgets and task before authoring; keep H1/H2 comparison separately scoped.

**Stopped after one bounded attempt and publication. Await explicit authorization
before any further experiment or configuration change.**
