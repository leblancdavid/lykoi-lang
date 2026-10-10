# R6.51 — Supervised formats and conversion qualification

## A: direct symbolic generation

[Converter](../../../../experiments/training_infrastructure_r6_51/convert.py) reads
only the sealed ten-entry R6.49 admission index. It verifies R6.49/R6.50 publication
identities, inherited protected bytes, all exact Boolean admission gates, training
partition, source episode/family identity and each referenced source artifact hash.
Global seal failures halt conversion. Per-entry malformed/incomplete records are
excluded with a reason; no repair or alternative source is inferred.

The [v1 record schema](training-record-1.schema.json) stores conversational
`prompt`/`completion` arrays plus explicit source family, broader component and
provenance metadata. Prompt: original requirement, relevant
[compact vocabulary](VOCABULARY.json), required output shape. Completion: exact
canonical JSON serialization of the source symbolic target. No acceptance cases,
oracle output, validation answers or executable Python are placed in the prompt.
Provenance sidecars bind all original direct references, limitations and source;
the training loader must project **only prompt/completion**, never flatten the
metadata/acceptance into text. Semantic authority remains the unchanged underlying
specification/schema; the compact vocabulary is a training prompt summary only.

- E01–E08: complete `typed-composition-1` package, including reusable definitions,
  dependency pins and foundation, from `SYMBOLIC.json`. These are deterministic
  source artifacts, usable as supervised endpoints, **not AI-authored trajectories**.
- S01/S02: final `AI-INTENT.json`, the typed symbolic authoring representation used
  by unchanged R6.16 C lowering into production semantics. This is an authoring-level
  intent target, not the expanded `SYMBOLIC-IR.json`. The latter, application and
  original validation identities remain bound in provenance. Initial failed AI
  edits/repairs remain original evidence; no failure is rewritten as success.

**10 structurally usable preparation records**, five nominal families, only two
connected scaffolds; eight experimental stateless endpoints and two production-backed
stateful endpoints. No general-purpose/kernel-wide curriculum claim. These formats
are profile-conditioned and should be reported separately if used together.
Embedded SHA256 seals are exact training text but not computable by a neural model
in general. The proposed tiny test deliberately measures strict exposed artifact
reproduction; future novel-program construction should use a separately frozen
existing seal-tool workflow and genuine decision captures. Do not silently strip
pins/reseal invalid outputs or credit memorized hashes as semantic generalization.

`DIRECT.jsonl` is canonical, LF, one record per episode, preserves target JSON
semantics and source identity. All ten pass Draft2020-12 outer-record validation;
eight targets pass unchanged wrapper validation; two intent targets pass their
unchanged schema. Existing sealed production semantic validation/replay evidence is
preserved, not rerun or rescored. Tests do not prove universal target correctness.

## B: tool-assisted construction

Proposed input: requirement, actually exposed semantic tools and their pinned typed
argument schemas, and the actual pre-decision construction state (plus any observed
history/feedback available at that turn). Target: one **observed** assistant choice
`{name,arguments}` that schema/type checks and whose actual tool response succeeds.
Role serialization can use the pinned model's tool-call template or a JSON completion;
the chosen mapping must be fixed before future capture/training. Loss applies only
to assistant selection/arguments, not tool response or feedback.

[Tool-decision design schema](tool-decision-1.schema.json) requires captured state,
tool exposure, AI-authorship, capture identity/index and actual response. Its JSON
Schema cannot establish AI-authorship, match the selected name to the exposed list,
validate arguments against a runtime-selected schema, or reconstruct state. Those
are additional identity/replay/capture gates for a future parser. No positive B
instance was fabricated; only design-schema consistency and missing-record rejection
are qualified. The converter fails closed on any unrecognized non-null trajectory
instead of assuming it is trustworthy.

**Usable genuine semantic-tool decision records: 0; `TOOL.jsonl` is empty.**
All ten entries have `actual_semantic_tool_trajectory=null`. E01–E08 scripted API
traces are excluded. S01/S02 have genuine AI file-edit capture via apply_patch/bash,
but no semantic Lykoi tool was exposed/selected, nor the needed semantic construction
state/typed decision capture. These two edit episodes are preserved and explicitly
distinguished from the eight scripted ones in [exclusion ledger](CONVERSION-ASSESSMENT.json).
No deterministic trace is automatically transformed into an AI decision.

## Leakage and qualification scope

All source episodes and derivatives stay `training_development`. No row-level random
train/eval split: family plus connected component are partition keys. The converter
rejects moving an exposed row into evaluation and splitting shared families/scaffolds
across partitions. R6.48 original zero admission remains zero; R6.49 successor ten
admissions remain ten, with zero Tier E. F5/F6 quarantine and external held-out sources
are not read by conversion. Publication integrity hashes preserved artifacts without
opening their task content. No P6-A05 content access occurred.

The guard covers the sealed cohort's known ancestry; it does not prove unseen
equivalence or enforce custodian isolation. R6.50 independent-evaluation/custody gaps
remain. Future independent components must be separately commissioned, frozen and
withheld before training, and prevented from entering exports including derivatives.
Diagnostics reusing trained examples are explicitly non-independent/resubstitution,
not leaked independent evaluation disguised as a new test set.

Controls cover strict JSON duplicates/nonfinite values, all eight admission gates
(False/int/string/null), missing required references, identity tamper/path traversal,
evaluation assignment, family/component split, scripted/edit substitution and unknown
trajectory format. See [test evidence](TESTS.json). Converter uses standard library;
schema tests use already-installed jsonschema4.26.0. No dependency installation.
