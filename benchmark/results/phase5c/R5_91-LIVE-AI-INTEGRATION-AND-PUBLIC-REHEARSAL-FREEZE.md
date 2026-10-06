# R5.91 — Live AI Integration and Public Rehearsal Freeze

## Classification

**`R5_91_PUBLIC_REHEARSAL_FROZEN`**.

One actual OAuth-authenticated model path now executes all four role adapters.
The final public freeze is active. **No future rehearsal requirement was selected,
generated, inspected, prepared or admitted; no rehearsal was run.**

R5.90 remains **`R5_90_LIVE_AI_WORKERS_BLOCKED_CREDENTIAL_UNAVAILABLE`**, with provider
requests/live runs **0/0**, qualified roles **0/4**. Its report and evidence are
byte-preserved. R5.91 deliberately changes strategy: the project determined that
full role-by-role AI-model qualification is unnecessary before evaluating the current
Lykoi research question. **Evaluate Lykoi, not build general model governance.**

## Actual invocation and provenance

OpenCode **1.1.25**, installed outside PATH, has existing OpenAI and GitHub Copilot
OAuth entries. Environment API credentials remain absent. The OpenAI/account path
and two Copilot GPT connection probes returned HTTP 400. A small non-scored connection
probe succeeded with **`github-copilot/claude-sonnet-4.6`**, selected for all four roles.
These were access diagnostics, not tournaments or semantic comparisons.

The new `public-opencode-adapter-r5.91-1` reuses R5.89's role/input/schema checks and
uses the installed CLI's legitimate OAuth handling. It never extracts or exports
credentials. Each invocation has a fresh temporary working/configuration directory,
role-specific primary agent, tools disabled, deny permissions, no attach/continue/
session reuse, no repository context and no prior conversation. The inherited local
server settings caused two pre-inference CLI failures; new in-process CLI invocations
exclude those settings, without changing or accessing any existing authenticated server.
The user's global OpenCode configuration and the original HTTPS adapter are unchanged.

The wrapper requests temperature **0**, no compaction, sharing disabled and no CLI
autoupdate. The freeze binds the executable's physical digest and declared version,
exact role/model configuration, role prompts (including native protocol guidance),
schemas and wrapper protocol. Receipts bind input/output/configuration/instruction/
schema identities, fresh adapter and CLI sessions and `UNTRUSTED_CANDIDATE` authority.
The requested model alias is exposed; a returned provider build/version, provider
response ID, model weights, authoritative cost/latency/token accounting are not exposed
by these events and are not invented. Provider error headers/bodies and credentials
are not persisted in evidence.

See [access discovery](r5_91/access-discovery.json),
[`model-configurations-r5.91.json`](../../../rehearsal/model-configurations-r5.91.json)
and [smoke integration](r5_91/smoke-integration.json). There were **11 explicit live
role invocations/responses** and four inference connection probes, one successful.
The CLI's total internal provider-request count is unavailable; explicit invocations
are not asserted as exact HTTP accounting.

## Public, non-scored adapter smoke evidence

Only the already-used public source **“Create tasks with titles.”**, the existing
authorized R5.89 title-only calibration bundle, and its sealed WHAT were used.
There was no new benchmark corpus, threshold, future-task tuning or universal
semantic certification.

| Role | Final smoke observation |
| --- | --- |
| Formalizer | Bound structured analysis parsed; native candidate FRC registered. No model-granted authority. |
| Source-only reviewer | Bound structured inventory parsed; exact spans/accounting and source commitment passed; native SOI committed before review/reconciliation. Candidate absent from its request. |
| Author | Restricted controller-authorized public bundle received; candidate Lykoi compiled and passed existing external title calibration. Hidden plan expectations absent from author input. |
| Verification-plan producer | Sealed WHAT/profile information only; candidate plan parsed, deterministic case identities/references assigned, native review/coverage passed. Candidate is not acceptance authority. |

The author/plan smoke uses the existing **synthetic fixture-approved calibration WHAT**,
explicitly distinguished from the real formalizer/reviewer candidates. This is four-role
adapter integration, **not a fully human-approved live semantic end-to-end rehearsal**.
The live source candidates may disagree or request clarification; reconciliation and
explicit human approval remain authoritative. The deterministic WHAT-side production
verifier and its sealing rules remain unchanged.

All development results are retained:

- [Attempt 1](r5_91/attempt-1/results.json): formalizer schema parsing succeeded but
  native FRC validation refused malformed obligations/issues; reviewer did not dispatch
  because no candidate existed. Author invented root `v1`, rejected by compiler.
  Plan used a non-native case shape, refused. **Three live role invocations.**
- [Attempt 2](r5_91/attempt-2/results.json): native formalizer, compiled/verified author
  and reviewed plan succeeded. Reviewer returned inventory items with empty spans,
  refused by native SOI validation. **Four live role invocations.**
- [Attempt 3](r5_91/attempt-3/results.json): all four roles entered their native
  integration boundaries successfully. **Four live role invocations.**

Repairs were role protocol instructions for existing native fields, source-only exact
whole-source span metadata, and deterministic plan case-ID/reference assignment.
No output obligations/expectations were rewritten to obtain a pass. Original invalid
author/model/plan outputs remain visible. **No Lykoi semantics, schemas of the language,
V1 mappings, R5.89 capability profile, BDI/adequacy rules or compiler were changed.**
The exact R5.87 wizard retains **`UNREPRESENTABLE_SOURCE /
NO_QUALIFIED_COMPLETE_MAPPING`**, independently retested.

## Final activated public freeze

**`R5.91-PUBLIC-REHEARSAL-2`**

```text
5ccf1410086f117f9527eefc97d39f519e6e2f7207028175f778460a39f134bb
```

Purpose: **`FUTURE_PUBLIC_REHEARSAL_ONLY`**. Activation: controller revision **2**,
**2026-10-06T03:59:48.308193+00:00** (the actual UTC evidence clock).

Exact [final configuration](r5_91/public-freeze-final.json),
[activation/order proof](r5_91/activation.json), and durable
`r5_91/public-controller-final.sqlite` bind R5.86 controller, R5.87 workspace,
R5.88 pipeline, R5.89 profile/faithful mappings, BDI/adequacy, compiler/semantics,
verification and containment, role configurations/prompts/schemas/protocol,
live smoke evidence, relevant transitive implementations and frozen protocol/failure
taxonomy. Candidate body and activation are separate content-bound records; activation
is owner-authorized through the existing controller journal, not a worker assertion.
The public prototype's existing principals/role credentials retain their trusted-local-
operator boundary; no newly authenticated external human or production security is claimed.

The first configuration **R5.91-PUBLIC-REHEARSAL-1** did activate, but publishing its
receipt failed when decimal verification timings entered the safe-integer canonical
serializer. Its original `public-freeze.json`, `public-controller.sqlite` and
[first-attempt record](r5_91/activation-attempt-1.json) are preserved. The prospective
fix uses a physical verification-file hash and a **different final freeze identity**.
The first configuration is stale/ineligible after the fix and must not be used.
No requirement was admitted under either configuration. This was pre-requirement
freeze preparation, not repair of a rehearsal result.

## Freeze-before-requirement enforcement

`PublicController` refuses requirements message/source registration until the exact
public activation is present and current component/configuration integrity passes.
The gate is at the controller boundary used by the normal workspace, before storage;
an unactivated pipeline cannot consume WHAT. Registration/adoption of activation is
owner-only and content-bound. Changed freeze identity is rejected on controller restart.
Admission and activation revisions share the same append-only journal; timestamps are
supplementary. `prove_admission_order()` mechanically checks activation precedes every
message/source registration. The actual final controller has **zero requirement
admissions**; positive/negative ordering and restart were exercised on old public
synthetic test sources, not the future requirement.

Read-only final integrity/restart/order audit is in [final audit](r5_91/final-audit.json).
Use the final controller/configuration, not an ordinary calibration controller, for
the next public rehearsal. The [frozen protocol](../../../docs/public-rehearsal-protocol-r5.91.md)
requires a genuinely new reasonable human requirement, clarification/human answers,
unchanged pipeline, preserved first terminal result and existing failure taxonomy.
No shopping for a known-fit or intentional-failure requirement. Refusal is a valid result.

## Verification

| Explicit selection | Result |
| --- | --- |
| New R5.91 adapter/provenance/isolation/freeze/admission/restart/public wiring | **14/14 PASS** |
| Existing R5.86 controller | **34/34 PASS** |
| Existing R5.87 workspace | **26/26 PASS** |
| Existing R5.88 sealed pipeline | **30/30 PASS** |
| Existing R5.89 public rehearsal | **33/33 PASS** |
| Compiler/application | **31/31 PASS** |
| Guarded historical R5.80–82/R5.84/V1 | **104 PASS / 2 known CRLF physical-byte pin failures** |
| Model validation / safety | PASS; zero capability violations/invalid transitions |
| Final freeze/restart/order/historical-byte audit | PASS |
| Whitespace/change scope | PASS |

[Summary](r5_91/verification.json) and raw logs remain beside evidence. The first new
test run had one incorrect test-only string-length constant, fixed to the actual
25-character source length; the first log is retained. No historical CRLF files/pins
or evidence were normalized or repaired. Explicit selections avoided protected inputs.
All implementation changes are prospective additions; the existing R5.86–89 code,
compiler, generated files and model were not edited.

## Deliberately minimal policy and stop

AI models remain replaceable, untrusted semantic workers. Model identity is provenance,
not semantic authority. Current policy: **model/provider/configuration identity is run
provenance and frozen experimental configuration; changed configuration defines a
different experiment; artifact meaning and authority do not derive from model identity.**
No general registry, tournament, routing, retirement, broad qualification or compatibility
guarantee was implemented. Same-model correlated errors remain possible. Claimed isolation
is **separate-context/source-blind-to-candidate workflow**, not independent model cognition.

Legacy code/tests/docs/behavior → candidate recovered FRC remains a compatible,
unimplemented future extension. No R5.91 scope was added for it.

**B03_PRISTINE / B03_NOT_EVALUATED / B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT** remain true
by inherited boundary/public-only operations. All inherited and R5.91 B03 access/activity
counters remain **zero**. No B03 access/authorization or readiness classification.
**R5.83-CANDIDATE-1 unactivated.** Phase 5C remains paused. **Stop after R5.91.**

The next separately authorized round can introduce one new public human requirement
and run this frozen pipeline. R5.91 does not choose it or run it.
