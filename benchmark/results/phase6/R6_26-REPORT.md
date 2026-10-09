# R6.26 — Model capability comparison

**Final classification: `R6_26_PROVIDER_COMPATIBILITY_GAP`.**

The prospectively selected capable model, **OpenAI GPT-6.1 Sol through OpenCode
1.18.32**, completed one neutral text response. The unchanged construction tools
were unavailable in that session: OpenCode's MCP status reports **`lykoi failed`
/ `Failed to get tools`**. No construction tool invocation occurred. Calibration,
four fresh tasks, symbolic validation, expansion and functional execution are
**NOT_REACHED**. Whether stronger model capability improves construction is
**undetermined**; this is a compatibility observation about the tested route,
not a model reasoning failure or demonstrated limitation of Lykoi semantics.

## Authorization and baseline

The owner authorized a bounded comparison using existing semantics and allowed
only prospective minimal transport-envelope normalization. Initial Git status was
clean. [Baseline](r6_26/BASELINE.json) verifies **1,318 protected identities**, the
complete R6.25 publication manifest/receipt and the production ledger's
**26 constructs**. All inherited implementation, schema and historical identities
remain exact. The R6.25 Qwen artifacts retain their original classification.

| Frozen implementation/schema | SHA256 |
| --- | --- |
| R6.10 VM | `bf5dbfb96d6d50124d109c35804c81e5a27bf4038b7f65b1a909ad4f0cc13fa3` |
| R6.10 semantic-plan schema | `fdbafa29de67eb89118c7101ab51bd8f58d0aa2dbaa2edf362650ed5b7f50982` |
| R6.18 wrapper | `e5e57901d4df32bcb2eed3b5bbd7ce6f19ee3145bbf71303d96e15b4e3d67fab` |
| R6.18 composition schema | `269dbd2e0c2c758afb8a1288a8e8ed6626001973e1ed69121904c3217638536b` |
| R6.23 deterministic adapter | `1cc2efe486298a94d7119eed6c4a4d3a7eba7ddd99fd4f32b33892c07d963cc2` |
| R6.23 compact schema | `1bd3fb4be3b2affabbd3e6869368b79e876c04c0a782ff8c5798d843bc9118eb` |
| R6.23 complete schema | `86c6a78430af9f7d686a080f99f46ca51081ba6056a8624043a827b927b02398` |
| Production v0.3 schema | `2a2115bd74afe90f4f6fdb4548b6247348bfd07978843f5bdb8676dae5ae596e` |

R6.24's transactional dispatcher and semantic tool definitions, and R6.25's
provider-neutral normalization, are imported read-only. Their exact source
identities and all production compiler/lowerer/runtime identities are in the
baseline. [Regression](r6_26/REGRESSION.json) requalifies R6.25 transport **17/17
methods** without inference. Its synthetic OpenAI-compatible JSON-string envelope
qualification remains valid, but does not certify this new SDK/MCP exposure path.

No production, VM, wrapper, adapter or semantic schema change occurred. No P6-A04
acceptance ran and P6-A05 was not accessed. No new dependencies, model downloads,
training or paid-service configuration were introduced. Existing credentials
are used only by OpenCode and are not collected or published.

## Models and provider inventory

[Inventory](r6_26/INVENTORY.json) contains the live catalog and selected model's
advertised metadata; [configuration](r6_26/MODEL-CONFIG.json) records the prospective
choice. Catalog presence alone was not treated as authenticated availability.

| Track | Identity and role | Outcome |
| --- | --- | --- |
| A | Historical R6.25 local Ollama0.35.0 / Qwen3 8B Q4_K_M | Preserved calibration evidence only |
| B | Requested `openai/gpt-6.1-sol`, high reasoning, OpenCode1.18.32 | Neutral text response reached; construction unavailable through tested SDK/MCP route |
| C | Not selected | No second authenticated provider established; no model switching |

B was selected before any participant exposure for advertised programming,
reasoning and tool-call capabilities. It is the same explicit model identity as
the coordinator, disclosed rather than called an independent replication.
Catalog limits: context**1,050,000**, input**922,000**, output**128,000**. Requested
response output cap**4,096**, high reasoning and native MCP tools are recorded;
effective delivery/configuration and upstream canonical model identity are not
independently attested. No outcome-informed model replacement occurred.

R6.25's Qwen task had10/10 accepted transport envelopes,9/10 schema-valid argument
objects,1/10 successful construction calls, three correction turns and no completed
program. Its4,955 input/313 output tokens and5.142441s task inference remain historical
measurements, **not paired scored observations against the four fresh tasks**.

## Exact observed compatibility failure

The experiment-owned [stdio bridge](r6_26/bridge.py) mechanically exposes the exact
existing function descriptions and semantic argument schemas as MCP inputSchema.
Its planned tool-call boundary maps MCP name/arguments/request identity into the
existing R6.25 OpenAI-compatible envelope. It neither fills nor repairs arguments.
No tool-call normalization was actually exercised in a live participant call.

The [neutral request/config](r6_26/NEUTRAL/REQUEST.json) asked for one inert declaration
and one inert value-operation request, with exact arguments and ordered feedback.
It contained no calibration or scored requirement. [MCP transcript](r6_26/NEUTRAL/MCP.jsonl)
records initialization at protocol2025-11-25 and a complete tools/list response
whose four descriptions and inputSchema objects match the frozen definitions.

[Raw OpenCode events](r6_26/NEUTRAL/EVENTS.jsonl) record one completed response:

> I can’t perform the calls because `lykoi_declare_input` and
> `lykoi_apply_operation` aren’t available in this session. Neither call was executed.

The subsequent **model-free** [MCP status](r6_26/DIAGNOSTIC/MCP-STATUS.txt) reports
`lykoi failed` / `Failed to get tools`. [Resolved safe configuration](r6_26/DIAGNOSTIC/RESOLVED-SAFE.json)
confirms the intended tool/permission rules. The bridge's initialize/list exchanges
completed, but tool discovery in the OpenCode client failed before construction.
There are **zero tools/call requests**, zero semantic decisions and zero correction
turns. A successful CLI exit0 did not establish tool availability.

`apply_operation` has root oneOf and no root type, unlike the other three schemas.
This is a concrete candidate schema-shape incompatibility. The client did not
expose its precise validation exception, so this report **does not identify that
key as the proven sole cause**. A second model-free probe disabled inherited MCP
connections and retained initialize/tools/list evidence; requested filtered SDK
debug lines were empty. [Qualification](r6_26/PROVIDER-QUALIFICATION.json) distinguishes
observed discovery failure from unverified root-cause attribution.

No envelope-only repair was identified for this pre-invocation discovery failure.
Adding a root type or flattening the semantic argument schemas was not attempted
under the unchanged-schema boundary. B is therefore **unavailable through the tested
route**, not declared unavailable through every possible OpenCode integration.
Calibration and scoring stopped at their prerequisite, without further inference.

## Frozen calibration and fresh evaluation

[Protocol](r6_26/PROTOCOL.md), [pre-exposure freeze](r6_26/PREPARATION-FREEZE.json),
[prompts](r6_26/PROMPTS.json), [tools](r6_26/TOOLS.json) and
[requirements/acceptance manifest](r6_26/TASKS.json) precede neutral model exposure.
Tasks are coordinator-authored, capability-tailored synthetic requirements; freshness
is a new requirement instance, not evidence of independent sourcing or new semantics.
No historical R6.19–R6.25 task instance is rescored. No acceptance oracle or solution
was sent to B. No scored prompt tuning occurred.

| Task | Required construction | Frozen observations | Outcome |
| --- | --- | ---: | --- |
| CAL | Previously exposed R6.25 OffsetTotal; typed inputs, stored subtotal then +3 |7 | NOT_REACHED; unscored |
| N1 Reserve | Typed subtotal then -7, explicit prior-value dependency |7 | NOT_REACHED |
| N2 Threshold | Typed addition, stored Bool upper-bound condition, ordered check |6 | NOT_REACHED |
| N3 Gate | Permission check before stored comparison/check and arithmetic |6 | NOT_REACHED |
| N4 Bundle | Two calls to the same reusable Lift, sum their results, bound check |6 | NOT_REACHED |

The four fresh tasks cover arithmetic, Boolean conditions, dependencies, failure
ordering and reuse within the unchanged bounded subset. **25** fresh acceptance
observations and7 calibration observations are frozen; **zero** are executed.
Structural signatures/operation order/call edges and expected output/error cases
are explicit. Completed-program validation and functional behavior are unmeasured.

Prospective construction budget:16 model steps,24 semantic calls, three correction
turns,180s wall,60,000 cumulative input and16,384 cumulative output tokens at visible
step boundaries. Since compatibility failed, no scored runner was activated or
subsequently implemented; correction/token-boundary enforcement remains unqualified.
[Preparation notes](r6_26/PREPARATION-NOTES.md) preserve this limitation and the
model-free diagnostic's cp1252 console-print failure after its evidence was saved.

## Measurements and failure classifications

[Measurements](r6_26/MEASUREMENTS.json), [functional status](r6_26/FUNCTIONAL-RESULTS.json),
[artifact inventory](r6_26/MODEL-REPRESENTATIONS.json) and [failure classifications](r6_26/FAILURES.json):

| Measurement | Actual observation |
| --- | ---: |
| Neutral OpenCode sessions/completed model steps |1 /1 |
| Upstream HTTP model requests including hidden retries |Unavailable |
| Neutral input/output/reasoning tokens |178 /39 /62 |
| Neutral total tokens /cached read /cached write |279 /0 /0 |
| Neutral client wall, including initialization |19.163931s |
| Isolated inference/construction/validation/expansion/execution time |Unavailable / NOT_REACHED |
| SDK-reported cost |0; retained as returned |
| Actual API billing |Unavailable, not inferred zero |
| Authorized selection/schema-validity denominators |0/0; unmeasured |
| Semantic construction operations /completed programs |0 /0 |
| Calibration /fresh tasks attempted |0 /0 |
| Fresh acceptance observations executed |0/25; NOT_REACHED |
| Correction turns /manual repairs |0 /0 |
| Tool-discovery failures /text-inference failure events |1 /0 |

The measured wall time is not an inference-speed comparison. SDK token fields are
reported independently; output and reasoning fields are not silently conflated.
SDK/catalog zero pricing is not a billing receipt. No tool-selection accuracy,
semantic reasoning quality or functional-correctness rate can be inferred from
absent tool exposure. No invalid semantic arguments/dependencies/compositions or
incorrect behaviors were observed because those stages were never entered.

## Interpretation, integrity and stop

This run establishes a **tested OpenCode SDK/MCP discovery compatibility gap**.
It provides no evidence for or against a model-capability effect on symbolic
construction. It neither establishes model incapability nor an architectural
advantage over conventional programming. Fresh-session hidden-context exclusion,
independent replication and causal model selection are not attested.

Remaining limits include native schema visibility, exact provider-envelope capture,
unqualified scored budget enforcement and the bounded existing expression/registry
interface. Typed validation would still not prove requirements satisfaction; overflow,
encoding range and ordered runtime failure remain observable semantics. No production
extension is justified by this discovery failure.

**Recommended next experiment, requiring separate authorization:** qualify a native
tool exposure route with the exact frozen schemas and inert synthetic calls. If a
schema-envelope representation change is needed, explicitly authorize and prove
preservation of the accepted semantic argument set, then freeze it before another
comparison. Do not resume this halted attempt or change its model from its outcome.

[Publication identities](r6_26/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_26/VERIFICATION.json) verify protected bytes, kernel26,
pre-exposure freeze, exact tool-schema identity, JSON/links/whitespace,17 transport
regressions, absence of construction/scored exposure and `git diff --check`.
Verification issues no inference. Additive [overview](../../../docs/project-overview-r6.26.md),
[research log](../../../docs/research-log-r6.26.md) and
[decision](../../../docs/decisions-r6.26.md) retain the current boundary.

**Stopped after the bounded neutral compatibility attempt and publication.
Await explicit owner authorization before further work.**
