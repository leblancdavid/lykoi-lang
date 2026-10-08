# R6.17 — Three-track discovery and generalization experiment, design 1

Prospective protocol. No tasks selected/generated, model selected, registry built,
author sessions dispatched or acceptance executed in R6.17. Separate implementation
authorization is required. Before execution, lock resource settings and exact task/
oracle packages under the rules below; these are procedural gates, not unspecified
discretion to change scoring after observing outcomes.

## 1. Question, foundation and tracks

Does AI-discovered reusable composition improve unseen-task software construction
over fixed symbols, after equivalent opportunity and full vocabulary costs?

Candidate foundation: **an unchanged R6.10 semantic-plan-1 subset**, not production
Lykoi and not a new VM. Initially qualify `atom` (UInt8/UInt16BE), `literal`, `seq`,
`value`, `check`, `choice`, `end`, `emit`, `dispatch`, and expressions `ref`, `const`,
`record`, `eq`, `le`, `add`. Fixed existing codecs: bytes, UInt8, UInt16BE. Exact
contracts/errors/limits come from [contract 1](../../../../experiments/semantic_interpreter/CONTRACT-1.md).
Restrict to monomorphic integer/Boolean/bytes/closed record values and acyclic
ordered byte computations, with no arbitrary dotted projections outside declared
records. No raw text parsing, recursion, physical effects or dynamic native lists.
This narrow initial experiment studies compositional transfer, not general software.

Build a separate experimental checker/expander, without modifying the foundation.
Its type rules and literal/prefix constraints must be fully specified and qualified
before task curation. Any unsupported opcode, codec or behavior is refused, not
implemented by the wrapper. Expanded call execution must use original public
validation/execute. Separate validate-once measurements may be reported but cannot
replace public-path scoring. The exact qualified subset/adapter pins are frozen
before development; expanding this list requires a prospective protocol amendment.

Common public input/output: one JSON request containing hex bytes, response with
exact typed value, output hex or deterministic error code/offset. The boundary only
decodes/encodes transport and projects the frozen VM envelope; it performs no task
relation. A implements the same observations in standard-library Python. Do not
grade incidental internal VM work as a Python functional requirement; foundation
work/cutoffs are separate symbolic conformance observations.

| Track / control | Author's canonical artifact and permitted library |
| --- | --- |
| A — direct conventional | Python, standard library, ordinary reusable Python helpers constructed during development and frozen for evaluation. No access to B/C solutions. |
| B — fixed structured | Same hybrid grammar/checker/lowerer as C; frozen human-designed foundation vocabulary and documentation. No new reusable registry entries. Inline composition is allowed. |
| C — adaptive structured | Identical foundation/tools; may propose and admit compositions only in development under the lifecycle. Frozen learned registry available at evaluation. No new execution meaning. |
| B-cap — fixed capacity control, nested within B | Same grammar/reference/retrieval facility; human-designed parameterized composition library from the same development requirements, frozen before evaluation, with the same 12-definition/256-node/depth4 caps as C. Construction/rejection/retrieval costs recorded. |
| C-expand — attribution ablation | Same frozen C definitions are supplied as expanded typed body templates instead of compact calls, with the same applicability documentation. Independently authored task sessions; no copied C solution. Distinguishes compact names from selected reusable compositions. |

B-cap is required for any AI-discovery attribution; B alone has less library capacity.
A gets equivalent development opportunity to create frozen helpers and documentation,
with 12-helper/256-AST-node/depth4 capacity caps for that reusable library (not a
limit on each Python application). Cross-language node units are not equivalent
semantics; disclose this and use common byte/token exposure caps as well. All frozen
library/index/documentation packages are capped at 64KiB each. Report actual sizes
and sensitivity rather than claiming matching caps guarantees equal useful capacity.
C-expand counts expanded bytes toward the same package limit; inability to fit is
an ablation limitation, not evidence of discovery advantage.

## 2. Development, freeze and evaluation

### Task commissioning (future; before development)

An independent human curator, without access to candidate libraries or run outcomes,
uses only the locked foundation's public semantic scope to commission **8 development
tasks and 24 evaluation tasks**. Within that necessarily scope-limited domain, select
by precommitted behavior-family coverage, not predicted winners or candidate abstractions.
Use fresh independently specified small byte-processing requirements; no historical
R6 tasks/answers or P6 curated sources. Keep syntactically different isomorphic tasks
in one family; near-duplicates across the split are excluded before lock.

Evaluation strata: 8 novel-domain/parameter variants of encountered relations;
8 unfamiliar combinations of at least two encountered concepts with dependency/order
interactions; 8 stress/negative-transfer cases where candidate reuse might be unsuitable
(boundary/error-order/coupled-output variations). Curator labels strata from behavioral
relations before seeing any discovered library. This is conceptual exposure, not
guaranteed reuse suitability. Do not substitute easier tasks after freeze.

For each task an acceptance author separately derives exact typed observations from
the requirement, including normal, boundary, malformed input and error precedence.
At least 24 unique base observations/task and 12 unique new observations/change;
use exhaustive enumeration when a declared small domain permits it and report exact
coverage otherwise. Exactly one staged modification per evaluation task, introducing
an unfamiliar interaction while retaining original observations unless an explicit
prelocked requirement supersedes them. Record superseded cases separately.
Two source-only reviews resolve ambiguity before lock; no candidate source guides
oracle construction. Pin transport, acceptance code, packages, seeds and selection
log before development. Neutral correct/wrong/malformed fixtures qualify scorer.

### Development

All A/B/C/B-cap developers receive the same eight requirements, permitted examples
and public development observations, in the same order. Separate track workspaces;
no cross-track library/solution sharing. Library discovery may span development
tasks, but application authoring uses fresh task contexts with only the declared
within-track library/history summaries. Record all effort, failed candidates and
proposals, including human library design/review. B-cap designers see no C library.
Track B may improve its application inline but cannot silently become adaptive.
Library acceptance uses only development/neutral fixtures, never evaluation answers.

### Freeze

Pin foundation, all checker/lowerer/transport/oracle/inference configuration, registry
entries/indexes/documentation and A's helpers. Freeze rejected proposal logs and
exact development effort before any evaluation requirement is revealed. Unused
definitions remain visible and charged. Empty learned vocabulary is valid data.
Attest no evaluator requirements/answers entered development; record access logs.

### Evaluation

Run all 24 tasks in each A/B/C/B-cap/C-expand condition with **3 fixed seed
replicates**, 360 base task-condition runs and 360 modification runs. No seed
selection by results. Task/replicate gets a fresh process/context; no persistent
chat, vector store, feedback history or library writes across evaluation tasks.
Base and modification contexts are separate; modification receives only its own
base artifact and released change, not hidden base scores or other solutions.
All base artifacts across conditions are frozen before modification reveal.

Counterbalance five condition orders by cyclic rotation indexed by task ID plus
replicate; alternate base/modification dispatch order. Run model inference serially
on the same host to avoid competition; deterministic tools use the same CPU limits.
Do not warm one condition with another's prompt cache. Keep weights resident, clear
task KV/prompt caches consistently and report cold setup separately.

Scored acceptance gives no feedback until all final submissions are immutable.
All planned tasks/replicates remain in denominators; missing, invalid, timeout and
unsupported applications are unsuccessful, with distinct cause codes. No hand repairs.
If a base fails, still attempt its modification on the frozen available artifact;
missing bases remain explicit and are not silently excluded. Paired-success analysis
is secondary; aggregate failure costs stay reported.

## 3. Equal opportunity and fixed budgets

Before model choice use hardware-neutral limits; neutral calibration may only set
the resource-dependent wall cap, not change token/attempt limits or task design:

- Development per A/B/C: 256,000 input+output tokens, 160 model calls, 2 hours active
  human/tool/model wall effort, at most 24 composition/helper proposals and the
  lifecycle caps. B may spend the same budget on inline design/testing/documentation.
- B-cap: same 2-hour human/tool effort cap and 256,000-token/160-call cap for any
  optional AI assistance; record human minutes independently. Human design is a
  measured comparator, not an uncharged advantage. Pure-human model usage is zero.
- Per evaluation base or modification: 32,000 input+output tokens including system,
  requirements, schema, library/index/retrieval and tool responses; 20 inference
  calls, 30 tool invocations; first complete submitted candidate plus at most two
  self-test repairs; two self-test batches, each CPU30s. No hidden oracle feedback.
- Per task author wall cap is `max(600s, 2*Tneutral)`, where `Tneutral` is the measured
  full 32,000-token neutral session duration on the chosen resource/configuration.
  Lock this single value before task curation/development; if infeasible, halt.
  All conditions use it; no task-specific or Track C extension.
- Tool subprocess cap30s, memory1GiB excluding model process; per-author cumulative
  non-inference tool CPU60s. Scorer cap30s/scenario, memory1GiB, identical transport.
  The supervisor must enforce and meter limits; unavailable enforcement halts primary
  comparison, rather than calling cooperative limits equivalent.

Stop each session on the first exhausted cap and retain partial artifacts. Search,
retrieval, validation, generated test cases, failed proposals and model tool calls
are included; no C-specific unmetered search/helper agent/background compute.
Tools need no LLM internally. Equal maxima are opportunities, not equal actual use.
Show actual testing/search volume and overhead. Pre-existing foundation/compiler
costs are recorded separately as inherited assets; new checker/registry work is
fully recorded and allocated to benefiting symbolic conditions. Common scorer cost
is recorded equally; no unallocated setup hidden from end-to-end comparisons.

The charter author already knows historical outcomes. Future task authors receive
an explicit minimal allowlisted package, not repository AGENTS/history or this
finding-bearing context. No delegation or inference occurs in the current round.

## 4. Generalization and contamination controls

| Threat | Required control / failure consequence |
| --- | --- |
| Unequal requirements | Byte-identical public source contract/examples/clarifications; no suggested abstraction or algorithm for C alone. Record requirement-package hashes. |
| Model/config variation | Same pinned local weights/tokenizer/template/precision/backend/decoding settings; fixed seed schedule and context; no training or adaptive routing. Record actual runtime config. |
| Context/answer leakage | Allowlisted per-task mounted workspace; no repository history, shared chats, hidden test files, coordinator outcomes or cross-track source. OS process/user boundary and denied network; full supplied prompt/tool transcripts. Neutral negative controls attempt forbidden reads/network before scoring. |
| Task contamination | Curator/oracle workspaces outside author mounts; access attestations and reveal logs; modifications withheld physically until base seals. Premature access terminates affected primary comparison. |
| Training memorization | Split by behavioral skeleton, perturb names/constants/data layouts, include unfamiliar interactions and source provenance checks; do not merely rename development tasks. Model pretraining exclusion cannot generally be certified: disclose and bound novelty claim to development-unseen. |
| Ordinary macro reuse | B-cap same reference grammar/retrieval/checker/caps and development set; A can build helpers. Improvement over B alone is not AI-discovery evidence. |
| Compact encoding | C-expand ablation and both compact/expanded sizes; names alone cannot establish meaningful abstraction. |
| Extra computation | Same calls/tokens/wall/tool CPU/test limits; meter internal search/retrieval; forbid hidden tools/providers/agents and unlogged background work. |
| Retrieval advantage/cost | Same deterministic index machinery in B-cap/C; include index/tool/docs tokens and latency. Log unused fetches, misses and full closure costs. |
| Compiler/validator advantage | B/B-cap/C identical frozen checker/lowerer and foundation; record cold/warm and public validation separately. A's syntax/testing costs counted too. |
| Human tailoring | Human B-cap library frozen without evaluation access; curator sees no libraries. No coordinator pruning of failed C proposals without cost/log. Human edits to C semantics are excluded. |
| Scorer/infrastructure defect | Prequalify wrong/malformed/duplicate-key outputs and timeout enforcement; halt affected scores on defect, preserve originals and require prospectively versioned successor experiment. |

Negative-control marker scans supplement actual boundary evidence; absence of a
marker is not isolation. If isolation/configuration cannot be verified, retain
exploratory observations only and classify comparative attribution inconclusive.
No inference of learned internal reasoning from the visible abstraction artifacts.

## 5. Metrics and accounting

Retain per task/condition/seed/stage raw transcripts, source, first/final submissions,
expanded plans, exact observations and per-event monotonic timing. Define:

| Metric | Measurement / denominator |
| --- | --- |
| Functional correctness | Full-task acceptance = every frozen applicable observation passes; unique observation pass fraction reported separately. Type-sensitive exact comparison, missing artifacts fail. |
| First-attempt success | First complete artifact sealed before its first selftest; score it post-handoff even if invalid. Final success is separate, as are repairs/pre-candidate revisions. |
| Generalization | Full acceptance by held-out stratum/task/seed; success using an admitted definition versus without it; development/evaluation separation and family IDs visible. |
| Modification regressions | Previously passing applicable observation becomes failing; new-change and retained-suite pass counts, inherited failures and supersession separate. |
| AI tokens | Actual tokenizer counts for every input/output, repeated context/tool/retrieval, generated rationale; cache fields separately if any. Never estimate from source bytes. |
| Inference time | Prefill/generation wall and CPU/GPU timing when available; queue/load/cache time separate. Same-host active effort sum is not experiment elapsed time. |
| Total development time | Discovery/design/review + authoring/repairs + retrieval/testing/validation/lowering; stage wall, human active minutes and machine compute separate, no sum of overlapping intervals masquerading as wall. |
| Discovery cost | All C proposals, rejected drafts/checks, registry/index/docs building; A helper and B-cap design costs likewise. Common/new infrastructure and inherited asset costs explicitly separated. |
| Vocabulary size | Admitted/rejected/deprecated/alias counts; body nodes/expressions, dependency depth, stored/index/docs bytes and tokenizer tokens. Count unused entries. |
| Reuse frequency | Calls and distinct successful development/evaluation tasks per definition; failed calls, inline copies and unused entries separately; repeated seed runs not new concepts. |
| Representation size | Authored bytes/tokens, referenced transitive vocabulary closure, fully expanded nodes/expressions/bytes, generated Python bytes; distinct units. |
| Validation/compilation | Cold/warm median of five uninstrumented repeats on immutable artifacts; traversal profiling separately, expansion and original validation/time/peak memory split; public-path cost retained. |

For condition j, define lifecycle effort through N evaluation tasks:
`E_j(N) = new infrastructure share_j + development/library effort_j + sum(task
authoring + retrieval + testing + validation + lowering effort_j)`.
Compute separate curves in wall effort, human minutes, input/output tokens and
machine seconds; do not add incompatible units. Common setup gets equal allocation,
C-only registry/discovery gets C allocation; report alternative allocations for
shared symbolic tooling. Inherited infrastructure investment is unknown where
historical telemetry is absent: disclose it and give bounded marginal comparisons,
not a fully measured lifetime cost claim.

Report N=1,8,16,24 task curves and observed break-even within this range; no projected
unlimited reuse claim. Three author seed replicates measure variability: charge
discovery once per hypothetical deployment, then report each replicate deployment
and their distribution. Also show actual total experimental expenditure (all replicas
and controls). Failed task costs remain. Cost per accepted task divides complete
condition effort by accepted task count; zero accepted means undefined/infinite, not
zero. Matched-success savings are secondary to coverage/full effort.

## 6. Falsifiable decision rules

Task is the independent analysis unit; three seeds are repeated authorings, not
72 independent tasks. Average full-acceptance indicators within each task, compare
paired task means. Report paired differences and task-cluster bootstrap95% intervals
with10,000 resamples and fixed analysis seed1729. The two primary adaptive comparisons
are C–B and C–B-cap; use97.5% intervals for those two simultaneous decisions.
Secondary A/ablation/stratum observations use95% intervals and are exploratory.
Predeclared meaningful margin: 5 percentage points correctness; 15% lifecycle-effort
reduction at N=24. Intervals wide enough to cross these margins mean inconclusive,
not equality. Effort uncertainty uses the same clustered task resampling with fixed
recorded setup costs and separately disclosed allocation sensitivity.

- **Adaptive symbols outperform fixed:** C beats both B and B-cap with lower
  interval bound above +5pp full acceptance and no >5pp modification disadvantage;
  or correctness difference entirely within ±5pp and a ≥15% lifecycle-effort
  reduction whose interval upper bound for effort ratio is <0.85. Require successful
  transfer in unfamiliar-combination stratum and full cost records. Distinguish
  correctness benefit from efficiency benefit. If setup/human cost allocation
  reverses the result, efficiency finding is inconclusive.
- **Fixed symbols equally effective:** C/B-cap base and modification differences
  have intervals entirely within ±5pp and lifecycle effort ratio entirely in
  [0.85,1.15]. Similar point estimates alone are insufficient; B-only agreement
  cannot rule out ordinary library capacity as explanation.
- **Direct Python better:** A exceeds symbolic conditions by >5pp accepted-task
  interval or meets ±5pp correctness equivalence with effort ratio <0.85 including
  helper/setup costs; disclose if supported against only some symbolic conditions.
  One unsuccessful symbolic attempt does not prove universal Python superiority.
- **Discovered definitions fail transfer:** fewer than two distinct evaluation tasks
  successfully reuse admitted definitions, or zero unfamiliar-combination successes
  despite development reuse. Report empty/unused libraries separately; no evidence
  of discovery is not evidence of new primitives being necessary.
- **Vocabulary overhead outweighs benefit:** correctness equivalent/inferior and
  C lifecycle-effort ratio to B-cap has lower bound >1.15 at N=24, or no observed
  break-even and positive total excess cost. The latter is a bounded overhead finding
  even when intervals prevent a superiority decision.
- **Inconclusive:** insufficient precision, mixed correctness/cost tradeoff, contamination,
  missing telemetry, failed B-cap capacity matching/ablation, machinery defect or
  unqualified local controls. Preserve observations; no forced winner.

These outcomes concern the locked local model, narrow foundation and task distribution.
They do not establish general intelligence, internal neural abstraction, natural
machine language or architecture suitability for arbitrary software.

## 7. Stopping and publication

Pre-run halt: unresolved requirement ambiguity, no resource/model lock, unqualified
typing/expansion/transport, failed offline/containment/metering controls or missing
sealed independent evaluation packages. Development stops at first exhausted cap;
freeze records available library, even empty. Evaluation stops each author/scorer
at caps, retains failures, and stops the affected comparison on leakage, config
drift, registry/machinery mutation or oracle defect. No budget expansion, task
replacement, library repair or adaptive stopping based on favorable scores.
Finish the predeclared batch when controls hold; publish failures and precision
limitations without automatically enlarging it. Further rounds need authorization.

R6.17 publication classification is **R6_17_SYMBOLIC_RESEARCH_DESIGN_READY** if the
design covers these gates, controls, metrics and next-step boundaries; **DESIGN_PARTIAL**
if a required design decision is absent; **ARCHITECTURAL_CONFLICT** if the proposal
requires forbidden execution meaning/provider dependence; **PROTOCOL_HALT** if this
documentation round cannot preserve its authorized boundary. Use full R6_17 prefixes
for all four labels. Ready is a design judgment, not successful qualification/run.

Stop after publishing the charter/design. No implementation, inference, training,
P6-A04 acceptance or P6-A05 access in this round. The smallest next executable step
is the isolated composition-wrapper qualification in the charter, separately authorized.
