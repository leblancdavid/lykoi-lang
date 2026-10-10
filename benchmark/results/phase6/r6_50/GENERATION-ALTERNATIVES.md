# Dataset-generation alternatives — R6.50

All ratings are hypotheses for a future measured pilot, not demonstrated rankings.
Costs include commissioning, formalization, review, both targets, failures and replay.

| Strategy | Diversity | Cost/scalability | Correctness risks | Leakage / human review | Kernel coverage |
| --- | --- | --- | --- | --- | --- |
| A. Human requirements and implementations | Potentially rich domains and real ambiguities; still biased by author experience | Highest likely labor; slower growth | Humans can misformalize or implement incorrectly; frozen external observation still required | Prior exposure must be audited; independent reviewer remains necessary | May reveal unsupported obligations; no guaranteed 26-construct coverage |
| B. AI requirements, independent acceptance review | Fast proposals, often repeated scaffolds/capability tailoring | Lower proposal cost, review bottleneck; inference billing must be measured | Correlated source/oracle/target errors; human reviewer must derive outcomes before targets | AI origin never becomes human commissioning; unknown pretraining exposure and prompt contamination remain | Coverage prompts can broaden targeting but do not establish exercised meaning |
| C. Deterministic templates with controlled semantic variation | Auditable finite structural space; parameter-only expansion adds little | Low marginal cost after expensive correct template/oracle design | Shared template bugs propagate; validate templates independently and challenge with mutants | Entire template lineage belongs to one partition/component; review every new structural rule | Exact planned coverage possible, but construct occurrence is not application diversity |
| D. AI proposals plus deterministic qualification | More structural exploration than templates if novel behavior is verified | Promising automation; provenance, ambiguity and independent review remain costly | Validator catches representation errors, not wrong intent; external frozen oracle essential | Proposal/tool traces and shared abstractions can leak; reviewer/custodian still separate | Can target gaps under existing meanings; unsupported proposals quarantine rather than extend semantics |

## Prospective empirical selection

Begin with A for independent evaluation commissioning, because this question
explicitly requires human source authority. Use D as a **candidate** training-production
strategy, C for coverage controls and A/B for comparison samples. This recommendation
is about testable workflow, not proven quality or a selected sufficient strategy.

Before larger generation, separately authorize a tiny matched strategy pilot with
the same review standards and fixed effort caps. Record source origin, unique scaffold
components, behavior-counterexamples, accepted pairs per reviewer-hour, measured token/
compute cost, first-candidate acceptance, contradiction/repair rate, rights gaps and
leakage rejections. Commissioners/reviewers do not see implementations before freeze.
Audit a random preselected subset plus every novel structural template. An automatic
qualification pass never substitutes for an unknown rights or independent-review gate.
No such pilot or strategy sufficiency measurement occurred in this round.
