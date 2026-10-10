# R6.39 — Symbolic state vs. ordinary summary

**Final classification: `R6_39_COMPARISON_INCONCLUSIVE`.**

All three context policies supported correct genuine modifications in all three
scenarios, with no scored acceptance repairs or regressions. Ordinary-summary-led
continuation with equivalent retrieval was functionally sufficient in this sample.
C used fewer aggregate reported processed input tokens and less measured participant
wall time than B, but it required more completions and had more self-corrected
migration errors. B retrieved full history on T1 and a symbolic snapshot on T2.
Complete development-effort accounting and representation-specific causal attribution
are unavailable. **An advantage uniquely attributable to Lykoi symbolic state over
ordinary summaries is not established.**

## Preservation and qualified route

The initial worktree was clean. [Baseline](r6_39/BASELINE.json) verifies the R6.38
publication manifest/receipt and all inherited identities, then protects **3,786
SHA256 identities**, including production, R6.10 VM, R6.18 wrapper, R6.23 adapter,
R6.25 contracts, R6.32 registry/telemetry and R6.36–R6.38 historical evidence.
Kernel **26** is inherited exact accounting backed by unchanged pinned files, not
a new independent construct recount. All additions are round-local evidence,
nonproduction orchestration and versioned documentation.

[Neutral preflight](r6_39/PREFLIGHT.json) passed on OpenCode **1.18.32**, using
**openai/gpt-6.1-sol**, requested **high** variant, one completion, no tools,
564 input/8 output tokens. The R6.36 qualified child environment is reused:
`OPENCODE_PURE=1`, default built-in plugins eligible, project configuration and
external skills disabled. Effective authentication/reasoning are not attested.
No credential stores/private headers/endpoints were read or published.

## Prospective design and frozen scenarios

[Protocol](../../../experiments/context_comparison_r6_39/PROTOCOL.md) and
[task/source/oracle freeze](r6_39/TASK-FREEZE.json) preceded all construction calls.
The coordinator selected three new, capability-tailored synthetic requirements using
only unchanged Int64 checked add/le, ordered checks, UInt8 input/end and UInt16BE
output. Requirements and expected observations were generated before artifacts.

| Scenario | Original shared behavior | Required successor behavior |
| --- | --- | --- |
| [T1](r6_39/T1-TASK.json) WindowCharge | x<=y, then y<=190; x+y+y | y<=190 **before** x<=y; x+x+y |
| [T2](r6_39/T2-TASK.json) BatchFee | x<=180, then x+y<=180; x+y | Same checks; x+y+9 after checks |
| [T3](r6_39/T3-TASK.json) MinimumLoad | 21<=x, then 21<=y; x+x+y | Same checks; x+y+y+3 |

Every application has two dependent callers sharing the definition. CallerA reads
two bytes and adds a fixed bias; CallerB reads one byte and derives y with a fixed
offset. Both check input end before computation. CallerA must migrate to the shared
successor; CallerB must retain its exact predecessor pin and behavior. Original
definitions remain executable. The selected active CallerA replaces existing
behavior; simply adding an unused definition cannot pass migration acceptance.

No R6.36–R6.38 scored task is reused. These tasks retain the same narrow byte-caller
architecture; they are not a new external-domain generalization sample. T1 happens
to reuse R6.37's symbol name WindowCharge, but has different parameters, checks,
labels, formulas, constants, input bindings and modification requirements. Name
reuse is not claimed as novelty or independent sourcing.

Expectations: [T1](r6_39/T1-EXPECTATIONS.json), [T2](r6_39/T2-EXPECTATIONS.json),
[T3](r6_39/T3-EXPECTATIONS.json). Same-coordinator frozen oracles are independent
of participant artifacts, **not** independently human-reviewed or independently
cognitively authored expectations.

## Identical baselines and context conditions

Each original application was actually AI-authored once, accepted, and cloned
byte-for-byte into all three conditions. Base construction received no modification
objective. All nine modification stages began in distinct fresh sessions; no
candidate tools address another condition's registry. Condition order was
**T1 A/B/C, T2 B/C/A, T3 C/A/B**.

- **A — full history:** complete exported relevant base conversation, construction
  actions, responses and feedback, rehydrated as a history document. Available
  exported message parts are retained, not summarized. This is not continuation
  of the original native OpenCode session.
- **B — ordinary deterministic summary:** verbatim frozen behavior and objective,
  component/signature/dependency index, caller pins and constraints. Implementation
  bodies and verbose feedback are omitted initially. No LLM creates the summary.
- **C — symbolic snapshot:** authoritative exact typed definition closure, immutable
  identities, signatures, dependency pins, caller bindings, constraints, lifecycle,
  recomputed validation identities and retrieval references. The unchanged R6.38
  generator/verifier operates over the original registry plus frozen behavioral facts.

The registry alone does not contain the human behavioral requirement; host-supplied
frozen facts remain explicit. Initial predecessor/successor and migration maps are
empty; current records are available after authoring through the same common tools.

| Serialized context bytes, same JSON convention | A | B | C |
| --- | ---: | ---: | ---: |
| T1 |42,304 |2,700 |6,925 |
| T2 |35,816 |2,678 |6,541 |
| T3 |41,388 |2,662 |6,888 |

These are document bytes, not provider tokens. A includes export metadata and
repeated instruction/material text; this can inflate rehydration versus native
history. Its effect is not separately measured.

## Information equivalence and actual retrieval

[Information-equivalence audit](r6_39/INFORMATION-EQUIVALENCE.json) and per-task
`Tn-BASE/CONTEXT-FREEZE.json` were installed before modification calls. Immediate
information differs; **accessible task-relevant information** is equivalent.
All conditions have the same guide, model configuration, tools and bounded exact
registry retrieval, plus read-only access to all three frozen context documents.
No acceptance cases, future objectives in base stages, or other candidates are
available. The [supplemental audit](r6_39/SUPPLEMENTAL-AUDIT.json) recomputes actual
snapshots, checks summary facts and complete histories, and exercises all five
registry detail kinds. It is post-authoring unscored qualification, not an oracle change.

Actual context retrieval matters to attribution:

- T1 A retrieved snapshot; **T1 B retrieved full history**; T1 C retrieved snapshot.
- **T2 B retrieved snapshot**; T2 C retrieved snapshot.
- T3 C retrieved snapshot; T3 B retrieved only registry facts, not a context document.

B therefore tests **summary-first with equivalent retrieval**, not an ordinary
summary-only ablation. A also does not remain history-only. No modification retrieval
reported unavailable information. Two common base-stage requests for continuation
contexts returned NOT_AVAILABLE before such contexts existed; they are preserved
and counted. Accessible-equivalence does not imply identical cognition or immediate
representation, and representation crossover limits causal conclusions.

## Functional modification, preservation and replay

| Measure | A | B | C |
| --- | ---: | ---: | ---: |
| Accepted modification scenarios |3/3 |3/3 |3/3 |
| Final functional observations |2,373/2,373 |2,373/2,373 |2,373/2,373 |
| Original/retained observations preserved |1,581/1,581 |1,581/1,581 |1,581/1,581 |
| Successor caller observations |792/792 |792/792 |792/792 |
| Observations with required different value/error |317/317 |317/317 |317/317 |
| Exact dependency/selective migration checks |3/3 |3/3 |3/3 |
| Passing-to-failing regressions |0 |0 |0 |
| Scored acceptance correction turns |0 |0 |0 |
| Self-corrected rejected migration calls |0 |1 |2 |

Each shared original passes **527** observations. Each final run passes **791**:
the unchanged527 predecessor/retained-caller observations plus264 successor caller
observations. The old-to-new differences are81/67/169 for T1/T2/T3. Coverage includes
256 selected two-byte pairs and all256 one-byte caller inputs, exact successful
values/bytes/spans, semantic rejection codes/order/nodes/offsets, truncated/trailing
precedence, input-type rejection and work-limit controls. Observations are not all
unique inputs; this is not full UInt16 input-space or signed64/overflow coverage.

[Provenance](r6_39/PROVENANCE.json) verifies all27 admitted definitions: nine common
base definitions and18 participant successors match actual model MCP arguments
after mechanical identity sealing only. No coordinator semantic repair occurred.
Old definitions retain exact bytes, dependencies and behavior. CallerA successor
structure differs only in required dependency/compose pins; total migrations retain
CallerB explicitly. Invariants mean the frozen checks, prescribed order, types,
binding and input-end requirements, not arbitrary untested properties.

T1 C, T2 B and T3 C initially supplied caller names rather than SHA256 keys in
migration decisions. Common immutable-registry validation rejected each with
IDENTITY; all self-corrected within their first dispatch. These are real repair
attempts, although no post-acceptance correction turn was needed. C did not reduce
repair iterations. The same protection is available to A and B.

[AI-independent replay](r6_39/REPLAY.json) runs in a separate Python process with
zero model calls. All nine saved registries pass791/791 on each of three passes:
**21,357 repeated replay observations**, full envelopes, errors, work, identities,
expanded plans and provenance maps match each run exactly. Alternative valid shared
successor representations can differ across conditions; task agreement is not a
proof of universal equivalence or identical runtime work.

## Token, effort, time and cost accounting

[Measurements](r6_39/MEASUREMENTS.json) reconcile exported completion usage with
step-finish events and MCP exchanges. [Chronological ledger](r6_39/REQUEST-LEDGER.json)
preserves every observed completion's model, usage, timestamps and message identity.
All retrieval/tool feedback is included in participant input totals. SDK categories
are provider-reported-through-OpenCode values, not locally estimated tokenizer counts.

| Modification participant totals | A | B | C |
| --- | ---: | ---: | ---: |
| Noncached input |91,670 |73,785 |72,469 |
| Cached input/read |450,432 |199,680 |164,864 |
| Cache write |0 |0 |0 |
| **Processed input: input + cache** |**542,102** |**273,465** |**237,333** |
| Output |8,321 |8,169 |8,545 |
| Reported reasoning |245 |361 |559 |
| Model completions |24 |25 |28 |
| MCP calls |64 |66 |66 |
| Retrieval calls |15 |17 |17 |
| Participant + context-generation seconds |342.759 |289.739 |222.601 |
| Context generation/verification seconds |0.019142 |0.003518 |0.023257 |
| Retrieval dispatch seconds |0.169139 |0.293392 |0.212506 |
| Retrieval response local token estimate |20,088 |43,720 |26,626 |
| Scored validation/lowering seconds |0.003572 |0.003949 |0.003045 |
| Scored execution seconds (main finite case loop) |0.128205 |0.130261 |0.103487 |
| Full acceptance interval seconds |0.157746 |0.164678 |0.128953 |

Execution timing excludes small auxiliary invalid/type/budget control loops; full
acceptance intervals include them. Retrieval estimates are ceil(JSON characters/4),
**not exact provider-token allocations**. Responses include both text and structured
content, so serialized response size is not automatically the provider input size.
SDK reasoning is retained as its own bucket, not silently summed into output.

| Scenario | A processed input / seconds | B processed input / seconds | C processed input / seconds |
| --- | ---: | ---: | ---: |
| T1 |226,879 /71.056 |163,373 /84.326 |81,244 /84.507 |
| T2 |157,879 /206.386 |65,498 /79.293 |69,965 /61.344 |
| T3 |157,344 /65.318 |44,594 /126.119 |86,124 /76.750 |

Common original construction costs **62,013 processed input** (42,685 noncached,
19,328 cached),7,162 output,560 reasoning,17 completions,54 MCP calls and231.843s.
They are actual shared setup, not three independently repeated base runs. The
measurement file also shows transparent one-third allocation: processed totals
562,773/294,136/258,004 and participant/context/shared-base time420.040/367.020/299.882s.
Neutral preflight is common additional setup, separately recorded rather than
arbitrarily assigned to a condition.

Descriptively, B and C reduce modification processed input versus A by49.6% and
56.2%. C versus B is36,132 fewer processed input tokens (**13.2%**),1,316 fewer
noncached input,34,816 fewer cached input,376 more output,198 more reported reasoning,
and three more completions. C's aggregate measured participant/context time is
67.138s lower (**23.2%**), but T1 is essentially tied/slightly favors B; T2/T3 favor
C. T2's long A interval and T3's long B interval are not repaired or excluded as
outliers. Provider latency, caching and unobserved retry effects are not isolated.

Symbolic retrieval did not erase C's aggregate descriptive input reduction, but B
has fewer processed inputs on T2 and T3. B's T1 full-history retrieval dominates
its extra response volume. There is no consistent per-task token winner beyond
history reduction, no completion reduction, and no correctness or repair advantage.

**Actual API billing is unavailable.** Exported SDK cost fields are zero, not proof
of free use or a monetary saving. Exact upstream serialization, model tokenizer,
hidden HTTP attempts, effective reasoning, coordinator preparation/publication usage,
and complete context cloning/audit/freeze wall overhead are unavailable/unmetered.
Measured representation generation and all participant retrieval are included;
full end-to-end development accounting is not claimed. Stage wall includes
CLI/export/evaluation; MCP, validation and execution intervals overlap it and must
not be added again. Fewer processed tokens alone does not establish lower cost.

## Validity and architectural decision

This is **exploratory**: visible stage sessions are distinct and permissions exclude
filesystem/cross-candidate tools, but provider/harness hidden-context separation is
unattested. The coordinator saw historical findings before selecting tasks and
froze the acceptance oracle itself. Tasks are synthetic, narrowly capability-fitted,
short-history and structurally similar; only one run per condition/scenario occurs.
Counterbalancing does not remove all caching/time/model variation. No statistical
significance or population reliability estimate is justified from three scenarios.

All conditions use the same typed immutable registry, validation and lowering.
The ordinary summary includes exact interface/dependency identities and can retrieve
symbolic state. This compares **initial context policies within Lykoi**, not the
presence versus absence of the symbolic-state layer. Common checks cannot be
credited as a unique C-context benefit, nor can B's success justify deleting that
registry layer. Information crossover and missing fully accounted effort prevent
an advantage classification; B's success with retrieved C information also prevents
a strong ordinary-summary-only sufficiency classification.

Recommendation: **retain the existing nonproduction registry/identity machinery;
use ordinary deterministic summaries as a viable summary-first context option with
exact retrieval, and keep symbolic snapshots optional. Do not mandate C or remove
the state layer on this evidence.** A separate controlled ablation with repeated,
varied-history tasks and fully metered setup/billing would be needed to decide
whether snapshot maintenance adds incremental value. That is a recommendation,
not authorization or work started here.

## Deliverables, integrity and stop

- Frozen requirements/expectations and source freeze: `r6_39/Tn-TASK.json`,
  `Tn-EXPECTATIONS.json`, `TASK-FREEZE.json`.
- History manifests: [FULL-HISTORY-MANIFESTS.json](r6_39/FULL-HISTORY-MANIFESTS.json);
  actual `Tn-A/B/C/HISTORY.json`, `SUMMARY.json`, `SNAPSHOT.json`.
- Authoring: all `Tn-BASE/A/B/C/attempt0/` prompts/config/events/exports,
  `MCP.jsonl`, registry and telemetry records; `CLOSED.json` preserves stage budgets.
- Functional results: per-run `ACCEPTANCE-0.json`; replay `REPLAY-1/2/3.json`.
- Accounting, information audit, provenance, supplemental controls and
  [terminal result](r6_39/RESULT.json) are published beside those artifacts.
- Versioned [boundary](../../../docs/project-overview-r6.39.md),
  [observations](../../../docs/research-log-r6.39.md) and
  [decision](../../../docs/decisions-r6.39.md) preserve pinned parent documents.

[Publication verification](r6_39/VERIFICATION.json) checks all protected identities,
prospective and actual-context freezes, additive publication hashes, JSON/whitespace,
relative links, credential-pattern scan, unchanged tracked files and `git diff --check`.
No production/compiler/lowerer/runtime or earlier execution semantics changed.
No training, full R6.31 study, P6-A04 acceptance or P6-A05 access occurred.

**Stopped after bounded comparison, model-free replay, analysis and publication.
Await explicit authorization before further work.**
