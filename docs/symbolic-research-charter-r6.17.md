# R6.17 — Local AI-native symbolic software construction: charter proposal

Status: **proposal; experiment design ready, implementation not authorized**.
The owner's R6.17 request authorizes documentation and experimental design only.
This charter prospectively revises the research objective; it changes no historical
classification, production semantics or executable capability.

## 1. Proposed definition and research question

**Lykoi is a proposed local, provider-independent, AI-native symbolic software
construction system: AI interprets human requirements and constructs explicit
symbolic software, which deterministic tools validate and lower to executable
software that runs without an LLM.**

Workflow: human requirements → AI requirement interpretation → AI-constructed
symbolic representation → deterministic semantic validation → compilation/lowering
→ executable software → external acceptance observations.

Human-readable source is optional. Typed structures, graphs and compact references
are candidates; compactness is not an objective independent of correctness, reuse
and total development effort. Model-specific tokens or hidden neural states cannot
be required execution identities. The executable meaning must be recoverable from
versioned artifacts without the originating model, provider or inference service.

Primary hypothesis: **AI-selected reusable compositions of an unchanged semantic
foundation transfer to unseen requirements and improve correctness or fully costed
development compared with a capacity-matched fixed structured vocabulary.**
Direct Python is the conventional baseline. No adaptive-symbol advantage is assumed.

| Distinction | Meaning | Initial experiment |
| --- | --- | --- |
| A: fixed vocabulary use | AI selects existing human-designed operations/types. | Required foundation/control. |
| B: compositional discovery | AI proposes parameterized reusable definitions whose entire meaning expands to existing deterministic operations. | Only permitted discovery. |
| C: new semantic primitive | An operation needs a new relation, effect, execution rule or implementation not expressible by expansion. | Excluded; record gap for separate specification/implementation authorization. |

These vocabulary categories are not the experiment's track labels: experiment
Track A is Python, B is fixed symbols, C is adaptive **compositions**. Neither
successful composition nor new names establishes neural reasoning, emergence or
a natural machine language. Model training/fine-tuning is outside scope.

## 2. Reusable evidence and changed defaults

The [evidence inventory](../benchmark/results/phase6/r6_17/EVIDENCE-INVENTORY.md)
preserves demonstrated capabilities, prototype boundaries and negative findings.
The 26-construct production kernel is an existing bounded foundation, not a proven
minimum or a restriction that all future software must use exactly 26 constructs.
R6.10 remains a separate partial VM prototype. Neither is replaced by this charter.

Prospectively, kernel minimization, human readability and mandatory FRC/controller/
production-layer traversal are not default architectural selection criteria.
Source-authorized requirements, explicit ambiguity, type/effect consistency,
stable identities, provenance and deterministic execution remain useful principles.
The initial comparison uses common reviewed behavioral contracts to avoid giving
one track a better interpretation of WHAT. It does not measure live human-to-FRC
accuracy or qualify the whole historical approval workflow.

R6.16's lean-path recommendation is scoped exploratory evidence, not an instruction
to remove semantic validation or preselect a winner. R6.14 finite support does not
prove universal expressiveness. R6.15 failures remain failures. Historical contracts,
classifications, first candidates, repairs, seals and contamination disclosures retain
their original meanings.

## 3. Proposed representation and experiment

Recommend a **typed semantic DAG with explicit ordered sequence regions**, using
typed expression trees inside nodes and pinned symbolic references at call sites.
This separates data dependencies from observable evaluation/error order. It is a
testable design choice, not an adopted production language; see
[alternatives](../benchmark/results/phase6/r6_17/REPRESENTATIONS.md).

The [lifecycle](../benchmark/results/phase6/r6_17/ABSTRACTION-LIFECYCLE.md) specifies
closed typed parameters, exact dependency hashes, acyclic expansion, immutable
versions, admission evidence and deterministic lowering. Discovery never supplies
opaque callbacks or invented runtime meaning.

The [experiment design](../benchmark/results/phase6/r6_17/EXPERIMENT-DESIGN.md)
defines three tracks, development/freeze/unseen evaluation, a hand-designed
capacity-matched library control and expanded-symbol ablation. Only development
permits vocabulary discovery. All scored tasks use immutable machinery/vocabularies.
No tasks, hidden answers, models or executable harness are created in this round.

## 4. Local execution architecture and resource gate

Proposed components, all on the local machine:

1. Input broker supplies approved requirement packages to a fresh task process.
2. Local inference engine loads pinned weights/tokenizer/chat template and emits
   Python or typed symbolic data. A replaceable adapter handles inference only.
3. Local registry exposes a deterministic index and exact definition artifacts.
   Retrieval requires no cloud service or embedding model; lexical/type filtering
   suffices initially. Any optional model retrieval consumes the same author budget.
4. Local shape/type/dependency checker and macro expander emit a fixed foundation
   plan, expansion map and evidence manifest. Original foundation validator runs.
5. Local unchanged foundation interpreter or qualified deterministic backend executes
   the plan. Execution uses no model, inference engine, MCP or provider identity.
6. Separate local oracle processes score immutable submissions with a common wire
   boundary and retain exact outputs/errors. Author processes cannot read the oracle.

The initial foundation candidate is a qualified subset of unchanged R6.10 operations
(details in the design). No production or VM edits are needed for the proposed first
wrapper. Any incompatible mapping halts rather than importing host computation.
Stateful production integration, new effects and VM typing closure are later questions.

Before model selection, inventory OS/process isolation, CPU/core count, system RAM,
GPU/backend compatibility, VRAM, disk for weights/artifacts/logs and cooling/power
limits. Required memory is weights at selected precision + runtime workspace +
KV cache at the fixed context length + OS/harness reserve; verify actual peak fit.
CPU-only inference is permitted if fixed deadlines are feasible. No GPU minimum or
specific model is selected here. Python 3.10+ supports existing standard-library VM
execution; the selected local inference engine may have separately pinned drivers
and native dependencies. Record their licenses and offline installation artifacts.

Select the model only after resources are known, using neutral calibration tasks
outside all development/evaluation sets. Then pin model/weights hash, tokenizer,
quantization, backend/version, prompt template, context length, decoding parameters,
seed schedule, reasoning mode if exposed, threads/GPU offload and cache policy.
No weight updates, online memory or task-dependent inference configuration changes.
Disable network after setup and demonstrate model/tool/application operation offline.
OS denial of network is stronger evidence than an instruction to stay offline.

A local MCP server may expose validation/retrieval/lowering, but a CLI or library
interface is sufficient. The same tool semantics and accounting apply either way.
MCP is transport, not evidence of better reasoning or discovery. Runtime manifests
identify foundation/backend and vocabulary hashes, never a provider login or model.

## 5. Minimal roadmap, each stage separately authorized

1. **Smallest executable next step:** build an isolated, nonproduction typed
   composition wrapper over a tiny unchanged R6.10 subset. Qualify one parameterized
   two-operation composition and its fully expanded twin, plus wrong-type, unknown
   dependency, capture, cycle and expansion-limit rejection fixtures. Compare exact
   value/error/provenance/work observations and expansion maps offline. This is
   mechanics qualification, not AI discovery or scored generalization.
2. Qualify local metering, process/input isolation, offline inference and resource
   settings on neutral fixtures; publish model/resource and budget lock.
3. Commission source-only task curation and independently derived acceptance;
   lock selection, splits and untouched evaluation packages before development.
4. Run equal-budget development for A/B/C and the fixed-library control, record
   every proposal/failure and freeze registry/machinery. No hidden evaluation access.
5. Execute predeclared task-level evaluation and staged changes; publish immutable
   first/final artifacts, complete costs, negative results and attribution controls.

No step is begun here. A failed qualification requires a prospective amendment and
new authorization where scope expands; historical artifacts cannot be repaired in place.

## 6. Open architectural questions and major risks

- Can learned parameter boundaries transfer rather than memorize task skeletons?
- Does discovery outperform an ordinary human macro library of equal capacity?
- Do registry typing, retrieval and rejected proposals cost more than they save?
- Is graph authoring actually easier for the chosen local model than Python/trees?
- How much benefit comes from deterministic tooling rather than adaptive vocabulary?
- Can expanded types, errors, provenance and budget cutoffs remain exact across
  nested reuse? What happens when expansion reaches unchanged VM limits?
- Which future state/effect/resource semantics can be qualified without hiding
  computation in adapters? The initial pure bounded experiment cannot answer this.
- Can extension-aware impact analysis be complete? Legacy impact is not sufficient.
- How sensitive are outcomes to local model size, quantization and context capacity?
- Evaluation can be development-unseen without being absent from model pretraining;
  audit that limit and report it rather than claiming certified novelty.
- A frozen registry tests vocabulary selection/reuse, not continuous online language
  evolution. New primitives remain a separately governed research program.

**Stop after R6.17 publication.** Design readiness means sufficient specification
for separate implementation authorization, not implementation readiness, completed
control qualification, observed adaptive benefit or general-purpose completeness.
