# R6.19 — Local AI symbolic discovery feasibility

**Final classification: `R6_19_PROTOCOL_HALT`.**

A working local GPU inference environment and neutral structured-output/tool
calibration were demonstrated. The pinned participant produced nine rejected
development proposals and no accepted abstraction. During the first fixed-vocabulary
evaluation session, its third call returned HTTP500. The paired evaluation stopped.
Discovery, reuse, generalization and a correctness/efficiency benefit were **not
demonstrated**. The HTTP failure prevents a completed model-capability comparison;
it does not establish a Lykoi semantic gap or failure of every local model.

## Inventory and model choice

Initial Git status was clean at HEAD `39146b019ba3b2e13dd4a9ad833b82258d268e41`.
Inventory observations began 2026-10-09 00:26:53 UTC (2026-10-08 local date).
Exact command outputs, model inventory, template and configuration are in
[INVENTORY.json](r6_19/INVENTORY.json).

| Item | Observed |
| --- | --- |
| CPU | AMD Ryzen 7 7700X; x64 (WMI architecture9);8 cores/16 logical processors; MaxClockSpeed4501 MHz |
| RAM | Two17,179,869,184-byte modules,32 GiB installed;4800 reported/configured speed; OS visible32,625,004 KiB; free memory varies, exact snapshots retained |
| OS | Windows11 Home,64-bit,10.0.26300/build26300 |
| Discrete GPU | NVIDIA GeForce RTX4070;12,282 MiB dedicated VRAM; compute capability8.9; driver617.42/WMI32.0.16.1742 |
| Compute | CUDA toolkit13.1 / nvcc13.1.115; NVIDIA-SMI reports CUDA UMD13.4; actual runtime uses CUDA and offloads37/37 layers |
| Other displays | AMD Radeon integrated graphics; WMI536,870,912 bytes; driver32.0.11024.2; Meta Virtual Monitor5.3.57.114 |
| Storage initial snapshot | C:999,072,722,944 total/58,564,919,296 free bytes; D:4,000,475,770,880 total/1,725,206,425,600 free bytes; later exact snapshot in inventory |
| Runtime | Ollama0.35.0; bundled llama-server build1(`161755f29`),Clang18.1.8 Windows AMD64; Python3.14.3 |
| PATH checks | Standalone llama-cli/llama-server, lms/lmstudio, vllm and docker not found; bundled server is present and executed |
| Local weights |18 Ollama manifests, including embeddings,1.5B coder,8B models,20B GPT-OSS and30B coder variants; full digests/sizes retained |
| Structured output | Ollama schema-constrained format tested in calibration; generic JSON format used for symbolic proposals; tools/thinking advertised |

WMI's RTX AdapterRAM value4,293,918,720 is not used as actual VRAM: NVIDIA's
query reports12,282 MiB. Integrated GPU compute was not qualified; Ollama logged
an old AMD driver and excluded that GPU. Installed Python packages are recorded;
no dependency was installed. Runtime/weight discovery is bounded to command
availability and the existing Ollama store, not an exhaustive all-disk search.

Selected existing `qwen3:8b`,8.19B parameters,Q4_K_M,GGUF V3, based on hardware
fit and advertised chat/tools support before scored exposure. Manifest digest:
`500a1f067a9f782620b40bee6f7b0c89e17ae61f686b92c24933e4ca4b2b8b41`.
Local GGUF content verified against SHA256:
`a3de86cd1c132c822487ededd47a324c50491393e6565cd14bafa40d0b8e686f`.
Local `/api/ps` reported6,295,440,588 bytes loaded entirely in VRAM at context8192.
No model was selected or replaced based on symbolic outcomes.

## Locality, calibration and freeze

[Protocol](r6_19/PROTOCOL.md) fixes temperature0,seed619,context8192,
output limit4096/call,think=false,top_k20,top_p0.95,repeat penalty1. Dedicated
Ollama listens on127.0.0.1:11435 with OLLAMA_NO_CLOUD=true and invalid loopback
remote proxies; bundled llama-server runs `--offline` with the verified local GGUF.
The transport permits only loopback inventory/chat endpoints, no pull or fallback.
[SERVER.log](r6_19/SERVER.log), [locality receipt](r6_19/LOCALITY-prepare.json)
and per-call loaded-model records support local inference. No remote participant
inference, download, training or installation occurred. This is runtime configuration
and local-process evidence, not an OS network-firewall attestation. The coordinator
is the existing OpenCode assistant, not the experimental participant; it designed
the harness but did not repair participant semantic output.

[Calibration](r6_19/CALIBRATION.json):3/3 exact typed JSON extraction results and
1/1 inert echo-tool selection pass. Tool execution did not expose host code. Four
calls report268 input/29 cached-input/77 output tokens and45.329s call wall time,
including21.928s reported load time. Warm JSON generation is about87.7–87.9
tokens/s; first-call reported2.20 tokens/s is retained without normalization.
Simple structured JSON success did not predict symbolic-schema reliability.

[BASELINE.json](r6_19/BASELINE.json) pins the production26-construct ledger,
R6.10, R6.18 wrapper/schema/semantics and prior protected history. [FREEZE.json](r6_19/FREEZE.json)
pins the protocol, tasks, compact interface and exact runner before participant
symbolic exposure. The operation subset remains seq/UInt8 atom/value/check/end/
UInt16BE emit and ref/const/add/le/eq with exact Int64/Bool/Unit. New harness
mechanically seals identities and AUTO pins only; it never repairs semantic bodies.

A first setup attempt used an empty default model directory and stopped before
inference; [setup failure](r6_19/SETUP-FAILURE-1.md) preserves it. The existing
model store was then explicitly selected. [Pre-exposure review](r6_19/PRE-EXPOSURE-REVIEW.md)
records new-harness API corrections before D1; no outcome-informed retuning occurred.

## Frozen tasks and discovery

[TASKS.json](r6_19/TASKS.json) contains3 development and4 evaluation requirements,
each with365 finite cases:361 byte-pair combinations plus4 truncated/trailing
inputs. Tasks vary biased sums, equality, interval predicates, reversed checks and
single-point acceptance. Types, ordered failure, materialized predicates and
parameterized/nested reuse are requested. Candidate behavior scoring would compare
value, output, consumed bytes and first failure code; full repeated envelopes and
work cutoffs would be saved separately. No candidate reached that scoring stage.
These are synthetic, capability-tailored coordinator tasks; unseen means not yet
shown to this participant, not independently curated or absent from pretraining.

Three discovery sessions exhausted their three-call budgets (six repair calls).
First-attempt valid0/3; accepted development tasks0/3; valid expanded proposals0/9.
Six proposals violated the definition-list/cap requirement; one referenced the
unknown family `symbol`; one response pattern missing `dependencies` occurred
twice. Precisely:6 VOCABULARY,1 UNKNOWN_SYMBOL,2 PROPOSAL_SHAPE rejections.
All raw proposals and feedback remain in [calls](r6_19/calls/D1_1.json),
[D1](r6_19/sessions/D1.json),[D2](r6_19/sessions/D2.json),[D3](r6_19/sessions/D3.json)
and [RESULTS.json](r6_19/RESULTS.json). No manually repaired abstraction exists.

[Frozen vocabulary](r6_19/VOCABULARY.json): zero definitions, canonical `[]`,2 bytes,
SHA256 `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`.
Empty admission is a result, not a hidden selection of successful discoveries.
Discovery interval129.210s; nine calls consume15,563 reported input tokens,
7,641 separately reported cached-input tokens and9,661 output tokens; call wall
129.081s. Cached fields are kept separately rather than assumed additive billing.

## Halted evaluation and comparison

The precommitted counterbalanced schedule started Track B/E1. Two responses reject
the fixed-vocabulary rule before expansion. Third request returns HTTP500 at local
17:37:00 after15.151s server-logged request time. [HALT.json](r6_19/HALT.json) retains
the terminal event; [failed request](r6_19/FAILED-CALL.json) is explicitly a
deterministic reconstruction, not an original transport capture. The exception did
not retain the response body; cause and failed-call token telemetry are unavailable.
No retry or post-outcome model/prompt/budget/harness repair was performed.

| Measure | Development | Track B | Track C |
| --- | --- | --- | --- |
| Completed responses |9 |2(E1 partial) |0 |
| Invalid proposals |9 |2 |NOT_REACHED |
| Accepted tasks |0/3 |E1 incomplete;E2–E4 NOT_REACHED |NOT_REACHED |
| Input/output tokens |15,563/9,661 |2,186/2,148 for completed calls |NOT_REACHED |
| Call wall |129.081s |27.521s completed +15.151s failed request |NOT_REACHED |
| Abstractions/reuse |0/0 |0 |NOT_REACHED |
| Functional/expansion/determinism/work-cutoff scoring |NOT_REACHED |NOT_REACHED |NOT_REACHED |

No B/C correctness or efficiency ranking is available. Charge all discovery cost
to any later claimed C net advantage; this round achieved none. Original proposal
validation timings were not instrumented and are unavailable; posthoc deterministic
rejection replays are separately timed in RESULTS and are not substituted for
authoring measurements. Expansion/execution timings and resource-limit outcomes
are NOT_REACHED. Library serialization overhead is recorded per session, about
3–21 microseconds in discovery for the2-byte empty library. Original request traces
include complete prompts and telemetry. Whole-round elapsed time is the inventory
start through [verification timestamp](r6_19/VERIFICATION.json), including interactive
setup/publication, not an active-labor estimate. No energy/API-billing estimate.

## Limitations and next step

[Inherited context](r6_19/INHERITED-CONTEXT.md) records that harness guidance already
supplied the substantive R6.19 terminal summary before this session's inventory and
model selection. `INHERITED_R6_19_OUTCOME_PRIMING` prevents an independent-replication
or unbiased model/task-selection claim. Actual loopback calls are new recorded
observations, but the coordinator knew same-round findings. Participant request
records contain the compact interface/tasks/feedback, not that inherited summary.

The observed participant/schema mismatch is bounded to this8B model, prompt,
generic JSON output mode and fixed small repair budget; it is not a model-family
or language impossibility claim. Diagnostics combined unrelated vocabulary causes
under one message. Neutral calibration used a stronger schema constraint than
symbolic authoring, and did not qualify complex typed output. HTTP500 is a separate
local runtime failure with undetermined cause. No acceptance program, reuse,
unseen generalization, expansion or execution correctness was established here.

Coordinator prior exposure to R6.18 examples and results, synthetic task tailoring,
unknown model pretraining contamination, one seed, fresh message arrays without
process-per-task isolation, runtime prefix-cache reuse, nonisolated hardware and
no capacity-matched fixed-macro control limit interpretation. B never received a C
vocabulary; since the vocabulary is empty and C never ran, prompt/compute symmetry
is designed but not empirically compared. No inference about internal language of
thought or general reasoning improvement is supported. Requirements appear within
the declared subset by construction; model authoring failures are not unsupported
requirements, and empirical task-coverage qualification remains unexecuted.

Recommended separately authorized next experiment: first diagnose the pinned
Ollama HTTP500 with neutral long structured output and preserve response bodies;
then qualify nested symbolic-schema output on unscored calibration data. Freeze
any prospective prompt/schema/transport changes before a new bounded discovery
attempt with freshly unseen tasks; E1 and D1–D3 are now exposed. Existing hardware
and weights suffice to attempt this; no model download recommendation is needed.

## Publication and stop

[Publication identities](r6_19/PUBLICATION-IDENTITIES.json) and
[verification](r6_19/VERIFICATION.json) check protected bytes, frozen runner/tasks,
empty vocabulary, evidence JSON, new-text whitespace and `git diff --check`.
Verification preserves836 protected identities and checks45 publication identities,
with zero mismatches; the manifest excludes itself and the separately bound receipt.
Production/compiler/lowerer/runtime, kernel26, R6.10 and R6.18 implementations and
R6.3–R6.18 dedicated historical artifacts remain unchanged. Guidance additions are
prospective. No P6-A04 acceptance or P6-A05 access. Experiment-owned parent and
orphaned runner processes were stopped; desktop Ollama remains available.

**Stopped after bounded publication. Await explicit owner authorization.**
