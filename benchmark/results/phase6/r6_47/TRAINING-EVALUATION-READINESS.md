# Prospective training/evaluation protocol and readiness gates

## Fair comparison

Pin one open-weight coding checkpoint/tokenizer and common inference precision.
Within each representation/interface condition, evaluate:

| Track | Model | Construction representation |
|---|---|---|
| A |Original checkpoint, no extra training |Python |
| B |Same original checkpoint |Lykoi |
| C |Same checkpoint +Lykoi additional training |Lykoi |
| D |Same checkpoint +comparable Python additional training |Python |
| Optional E |Lykoi-specialized checkpoint |Python, general-coding retention |

Pair training requirement families across C/D, with separately validated Python
and Lykoi targets. Match processed training-token budget, epochs/update-compute,
adapter rank/target modules and hyperparameter-search allowance as closely as
possible. Record inevitable target-length differences and actual work; matching
example count alone is inadequate. Both start from the same checkpoint revision.
Freeze optimization choices using development data only and charge preparation,
rejected data, checkpoints and tuning. This document does not authorize training.

Task expectations are identical across tracks, independently frozen before authoring
and include full specified successes/errors/state effects. Separate requirements
that exceed one profile from within-profile authoring failures; do not fit language
primitives or silently discard unsupported tasks after seeing results.

Cross direct output versus actual callable-tool interfaces on both B/C, and give
Python tracks equivalent validation/execution feedback with the same information
and correction budgets. A tool-using Lykoi fine-tune versus a tool-less Python base
would conflate format/tool/model effects. Use common specification context and a
separate base-model few-shot/documentation familiarization control on development
examples only. Target-model chat/tool serialization is frozen, not assumed from
historical OpenCode transcripts.

Contrasts:

- A versus B: representation/interface under the same base model; familiarity still
  differs and must be measured, not called architecture alone.
- B versus C: specialization effect within Lykoi, including additional training.
- A versus D: matched additional Python training effect.
- (C−B) versus (D−A): incremental representation-specific training benefit; still
  conditional on target data quality, compute and interface matching.
- Direct versus tool-assisted within model/representation: tool-interface effect.
- Optional E versus A: general coding retention; no universal forgetting claim.

Freeze episode-level wall/completion/output/tool/selftest/correction budgets, sampling,
seeds and context caps before trials. Rotate order; use at least three seeds for a
future pilot, report each result and paired uncertainty, not just a best sample.
Small family counts remain exploratory. Match functional requirements, not source
similarity, generated token count or compiler success alone.

Primary outcome: first submission and final within-budget full functional acceptance
per episode, with unchanged-original regressions separated from superseded behavior.
Secondary outcomes: validation errors, correction count, exact replay, invalid-input
fidelity, dependency/authority/persistence obligations, author tokens/time/tool cost.
Record train wall/VRAM/checkpoints, all preparation/retrieval/validation costs,
visible usage and unavailable billing/hidden retries separately. Do not double-count
nested intervals. Score and replay after authoring closure with **zero AI calls**.
No model remains in the execution path.

## Readiness criteria and current verdict

Thresholds are scope-specific process criteria, not a universal minimum sample size.

| Gate | Explicit future criterion | Current status |
|---|---|---|
| Usable diversity | Named target families with nontrivial behaviorally different contracts; whole scaffold/lineage groups; pilot starts with4 development and2 unseen families |FAIL for broad readiness:17 audited episodes in one arithmetic/check domain; no clean unseen evaluation pool |
| Validation quality |100% admitted targets pass frozen deterministic validation and full declared acceptance; invalids/failures excluded from positive labels; exact AI-free replay |PARTIAL: finite accepted positives exist; production kiln defect/ambiguous compact spans preclude broad positive labels |
| Semantic coverage | Every in-scope construct has positive, invalid and interaction evidence; each claimed interaction has a requirement-level example, not just a unit vector; exclusions explicit |FAIL for26-construct objective; PARTIAL for tiny wrapper; equality/corrections/combinations sparse |
| Training/evaluation separation |0 exact/alpha/template/skeleton/successor/abstraction-component overlap; unseen families sealed by separate custodian |NOT_ESTABLISHED; historical tasks are exposed |
| Reproducibility |100% requirement/schema/vocabulary/target/evidence joins, exact identities, tokenizer/chat version, captured actual tool turns, deterministic execution |PARTIAL: historical source identities strong; trainable serialization/extraction not produced |
| Hardware feasibility | Measured chosen checkpoint/sequence/rank fits usable VRAM with1–2GiB headroom; stable small forward/backward and export/reload before any effectiveness claim |PHYSICALLY_PLAUSIBLE for1.5–4B; training stack/checkpoint unavailable in active environment; no execution authorized |
| Contamination | Source/author permissions, review roles, no evaluation solutions in training/retrieval; hidden-context limits disclosed; clean family-unseen tier separate |FAIL for clean generalization: same-coordinator tailoring, shared skeletons, outcome exposure and unattested model/system context |

Additional learning gate after any separately authorized training: improvement over
the base plus matched Python training on reserved families without exceeding budgets,
increased invalid-input failures or retained-behavior regressions. Train-loss reduction
and memorized historical pass rates are not sufficient. Dataset sufficiency is tested
through family-level learning curves and additional held-out families, not by declaring
an arbitrary universal number such as1,000 examples enough.

## Recommended next experiment

Authorize only the **12-episode independent data-generation/extraction pilot** in
[the generation plan](GENERATION-AND-LEAKAGE.md), with paired direct/tool source views,
independent requirement review and sealed family splits. Its purpose is to establish
trustworthy examples, serialization, correction availability and leakage controls.
Do not train during that data pilot. If it passes, separately authorize checkpoint/
training-stack qualification and then a small1.5–4B PEFT familiarity experiment.
Neither this recommendation nor R6.47 publication initiates those steps.
