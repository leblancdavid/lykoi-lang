# Three objectives and learning difficulty

## Objective comparison

| Dimension | A complete symbolic package | B bounded structured update | C typed semantic call |
| --- | --- | --- | --- |
| Input/target | Requirement + explicit vocabulary → full package | Requirement + full current state → one append/update | Requirement + state + available tools → one tool with arguments |
| Structure | Envelope, foundation, identities, definitions, order, typed nodes, result | One declared atomic node/definition/result edit with exact base-state identity | Tool discriminator, variant argument schema, aliases, type, deps, expression and state preconditions |
| Dependencies | Whole graph plus ordered effects/checks must cohere | Earlier typed bindings and definitions exposed; future obligations retained explicitly | Dispatcher checks current refs; schema-valid call can still fail state/dependency validation |
| Validation | Native endpoint validation after generation; optional repair full artifact | Transactional validation after each step, final endpoint validation still required | Strict arguments then native transactional semantic validation; feedback per call |
| Recovery | One malformed token may invalidate full package; repair regenerates substantial text | Roll back rejected update, retain state; wrong accepted semantic choice still poisons later steps | Roll back failed call; model may loop on legal but useless tools (R6.25) |
| Context | Compact requirement/vocabulary plus any pinned reusable library | Requirement/state/order, typed scope, unresolved obligations; state grows during rollout | B context plus registry schemas, matching responses and bounded history |
| Assembly | Mostly already represented, though target identity computation is nontrivial | Deterministic mechanical assembly proposed; profile-specific partial-state validator must be qualified | Existing narrow experimental dispatcher can seal; production stateful semantic MCP unavailable |
| Data | Eight package endpoints; two intent endpoints distinct | No qualified step records; endpoints allow prospective expert derivation | No qualified positive decisions; scripted traces do not establish AI choice |
| Overhead | One model call plus endpoint validation/expansion | Several calls + growing input + per-step validation and assembly | Several calls + schema rendering/transport + validation and tool responses |

B granularity v1: one typed ordered step, one definition declaration or one result
binding, each at an explicit state revision. No arbitrary JSON Patch. First skill
uses exactly one typed value step; broad curriculum may need other profile-specific
variants. A partial state's expected incompleteness must be distinguished from
typing failure. Topological dependency validity never determines error precedence:
the explicit operation order is separately supervised. Mechanical assembly cannot
silently select order from acceptance results. B is a proposed supervision surface,
not an implemented universal builder.

C can use R6.25's four tools (`declare_input`, `apply_operation`, `define_result`,
`validate_candidate`) for its bounded Int64/Bool/Unit expression/composition scope.
`apply_operation` uses oneOf branches, exact deps and earlier aliases. The local
Ollama and synthetic OpenAI envelope qualification is function-call compatibility,
not a deployed/full MCP semantic server or proof that this1.5B model sees all schema
branches. No Lykoi semantic MCP is exposed in the present harness. R6.49 stateful
construction used actual file edits plus scripted production lowering; these are
not semantic MCP calls. A future C adapter must freeze the actual model-visible
tool rendering and envelope. Providers cannot silently simplify typed schemas.

**Conditional recommendation: B**, starting with typed single-step selection.
It separates local semantic selection from complete-package bookkeeping without
requiring a new provider transport. This is a testable engineering choice, not a
measured learning advantage. C is worthwhile only if a selected existing interface
can express the same skill and the captured supervision is qualified. Keep A as
the endpoint comparator. The smallest current executable training-data path remains
A's existing exposed endpoints; that fact does not make another A run scientifically
sufficient or establish that B is easier to learn.

## Measured lengths and structure

[Read-only inventory](DATA-AVAILABILITY.json) remeasures the pinned tokenizer on
the exact ten DIRECT targets and native prompt prefixes. Counts match R6.52:

| Episode | Prompt tokens | Target content | Supervised incl.EOS (historical) | Existing ordered nodes across definitions/program | Local dep depth (nodes) |
| --- | ---: | ---: | ---: | ---: | ---: |
| E01 | 372 | 328 | 329 | 5 | 3 |
| E02 | 381 | 369 | 370 | 6 | 4 |
| E03 | 401 | 424 | 425 | 7 | 3 |
| E04 | 393 | 460 | 461 | 8 | 4 |
| E05 | 384 | 330 | 331 | 5 | 2 |
| E06 | 380 | 409 | 410 | 7 | 2 |
| E07 | 396 | 1018 | 1019 | 9 | 3 |
| E08 | 398 | 1058 | 1059 | 10 | 4 |
| S01 intent | 587 | 470 | 471 | Different production-intent structure | Not comparable |
| S02 intent | 604 | 662 | 663 | Different production-intent structure | Not comparable |

Parameters count as depth0; each local step adds1 over its declared deps. This
metric does not include implicit sequential order or expand composition bodies.
E07/E08 have nested definition-call depth2. Total57 existing step objects across
eight packages are potential decomposition material, not57 admitted demonstrations.
Production IR target lengths are not measured here;470/662 are intent lengths.

Tokenized original step fragments span18–111 content tokens (sorted-key compact
original step objects). This is a measured fragment range, **not** B record target
length: state-revision/update envelopes, signatures/results and EOS add tokens.
No C positive record exists, so no measured C supervised target length is claimed.
Model vocabulary is151,936 tokens; this is not the semantic vocabulary. The eight
packages use five node selectors atom/value/check/end/compose, uint8 codec, scalar
ref/const/add/le/eq and three types. More production capabilities do not fit this
same narrow tool vocabulary. Variable aliases/identities are open bounded strings.

## Estimates (not empirical training results)

| Quantity | A | B | C |
| --- | --- | --- | --- |
| Target length for present scale | Measured328–1058 package tokens | Estimate40–160 for one step with update envelope; definition/result units differ | Estimate40–180 for one typed call; signature/compose variants may exceed this |
| Decisions per program | At least5–10 node choices in these packages, plus signatures/order/result/types/refs/IDs | Similar semantic choices over multiple outputs, plus finish/update choice; roughly7–16 construction units | Similar choices plus tool/state selection; roughly7–20 calls including validation |
| Required context | Measured372–401 for packages; reusable vocab may enlarge it | Estimate400–1600 tokens as current state grows in this cohort | Estimate700–2048+ including schemas/state/feedback; must measure before freezing |
| Dependency depth | Local2–4 measured, nested calls2; ordered spans can cross entire package | Same program depth, not reduced by segmentation | Same program depth; aliases must resolve at call time |
| Feedback complexity | One multi-layer serialization/type/identity/behavior diagnostic | Many localized type/dep/order diagnostics + global unfinished obligations | Schema branch/transport/state/type/ref feedback and repair policy |
| Propagation risk | Early own-prefix error affects entire output | Lower local syntax blast radius, but accepted wrong choice and growing wrong state propagate | Same B risk plus ineffective/legal tool loops, ambiguous schema rendering |
| Data-generation cost | Existing endpoint reuse cheap; new diverse source/FRC/acceptance dominates | Per-unit states, transaction replay, endpoint acceptance and provenance qualification | B cost plus real tool capture, schema/model context, responses/transport replay |

Shorter outputs do not reduce total construction entropy, dependency depth or the
need to infer requirements. Repeated state/schema inputs can make B/C total training
and inference tokens larger than A. Unit accuracy p repeated n times gives p^n only
under an unrealistic independent-error model; do not use it as a performance estimate.
Actual all-step success, endpoint behavior and fully costed rollout are required.
Exact tokenizer measurements for proposed B/C messages and optimizer-work estimates
are future preflight gates; no unseen hypothetical record is assigned a measured count.
