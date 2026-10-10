# Training-data inventory and unique-example accounting

## Audited positive source cohort

**17 unique contract episodes** are usable as provenance-limited, finite-qualified
positive source candidates for the narrow experimental typed profile. They contain
**49 exact definition IDs**: 40 across eight lifecycles, three discovered definitions
and six primitive-only evaluation roots. Neither number is a semantic-family count.
No independently sourced/reviewed, leakage-qualified generalization dataset is ready:
**0 examples satisfy that stronger admission standard today**.

The unit is a whole requirement episode. Eight lifecycle successors are included
inside their original episode, not added as eight independent training examples.
All comparator implementations are grouped with their shared requirement. Any future
stage-wise SFT extraction must preserve those groups and cannot advertise more diversity.

Paths below are relative to `benchmark/results/phase6/`. Each row is one selected
episode. Original report qualifications accompany the row; no acceptance was rerun.

| ID | Requirement source | Selected symbolic source | Acceptance / replay source | Behavior, not symbol-name novelty |
|---|---|---|---|---|
| L36 | `r6_33/` frozen requirements, R6.36 report §Lifecycle | `r6_36/{old,new,a,b,a_new}.json` | `r6_36/FUNCTIONAL.json`, `REPLAY.json` | BoundedScore, ordered input/sum limits, surcharge successor, selective migration |
| L37 | `r6_37/REQUIREMENT.txt`, `MODIFICATION.txt` | `r6_37/{old,new,a,b,a_new}.json` | `FUNCTIONAL.json`, `REPLAY.json` in that directory | WindowCharge nonnegative/cap/doubled-start checks; changed result, retained caller |
| L38-1 | `r6_38/T1-TASK.json` | `r6_38/T1-A/registry/000005.json` | `modification0-ACCEPTANCE.json`, `REPLAY-1.json` under T1-A | x<=y then sum<=cap; +5 successor |
| L38-2 | `r6_38/T2-TASK.json` | `r6_38/T2-A/registry/000005.json` | same filenames under T2-A | Separate x/y caps; change multiplicity of y |
| L38-3 | `r6_38/T3-TASK.json` | `r6_38/T3-A/registry/000005.json` | same filenames under T3-A | Floor then relative bound; change multiplicity of x |
| L39-1 | `r6_39/T1-TASK.json` | `r6_39/T1-A/registry/000005.json` | `ACCEPTANCE-0.json`, `REPLAY-1.json` under T1-A | Swap check precedence and formula |
| L39-2 | `r6_39/T2-TASK.json` | `r6_39/T2-A/registry/000005.json` | same filenames under T2-A | x cap then sum cap; fee successor |
| L39-3 | `r6_39/T3-TASK.json` | `r6_39/T3-A/registry/000005.json` | same filenames under T3-A | Two floor checks; changed weighted sum and bias |
| D40-1 | `r6_40/DEVELOPMENT-TASKS.json`, D1 | `r6_40/D1/registry/000001.json` | `D1/PROPOSAL-CHECK-1.json` and reload checks | Parameterized interval_fee |
| D40-2 | same, D2 | `r6_40/D2/registry/000002.json` | `D2/PROPOSAL-CHECK-1.json` and reload checks | Parameterized pair_envelope |
| D40-3 | same, D3 | `r6_40/D3/registry/000002.json` | `D3/PROPOSAL-CHECK-1.json` and reload checks | Equality-before-load, echo_charge |
| E40-1 | `r6_40/EVALUATION-TASKS.json`, E1 | `r6_40/E1-A/registry/000001.json` | `ACCEPTANCE-1.json`, `REPLAY-SECOND.json` under E1-A | Interval check of derived sum |
| E40-2 | same, E2 | `r6_40/E2-A/registry/000001.json` | same filenames under E2-A | Pair floor/cap with caller charge |
| E40-3 | same, E3 | `r6_40/E3-A/registry/000001.json` | same filenames under E3-A | Two transforms followed by pair check |
| E40-4 | same, E4 | `r6_40/E4-A/registry/000001.json` | same filenames under E4-A | Echo transform followed by interval checks |
| E40-5 | same, E5 | `r6_40/E5-A/registry/000001.json` | same filenames under E5-A | Strict interval, reverse error order, doubled output |
| E40-6 | same, E6 | `r6_40/E6-A/registry/000001.json` | same filenames under E6-A | Load-first, range rather than equality, no doubled y |

R6.36 uses JSON broker actions, **not actual participant semantic MCP calls**.
R6.37–R6.40 have callable MCP request/response logs. Selecting A in R6.40 avoids
using failed compact-combination targets as positive labels; compact B/C alternatives
and their failures stay associated with the same six contracts. This outcome-aware
selection is disclosed and is suitable only for training-source curation, not evaluation.

## Wider pools: actual artifacts, not extra certified positives

| Source | Count/unit verified or retained | Available material | Admission limitation |
|---|---|---|---|
| Canonical `air/task_manager.json` | 1 canonical application | Explicit semantic model; production tests and generated manifest | Task-manager lineage and exposed maintenance skeleton; no joined SFT episode audited here |
| R6.10 | 3 explicit plans: CFG66, DSV66, BXC66 | Format contracts, valid programs, diagnostics, byte/provenance observations | Partial static typing/encode attribution/cost contract; broader VM, incompatible with tiny wrapper |
| R6.11 | 4 base tasks +2 modifications, report denominator | Python/VM construction and acceptance | Same-session, exposed synthetic authoring; not six independent families |
| R6.14 | 8 saved `.plan.json` artifacts | XOR8 initial/repaired, addmod8, parity8, nibble/naive/limit probes | Only 3 full finite relations; repaired XOR replaces a rejected target, repeated sweeps are not examples |
| R6.15 | 12 plan files, 6 task/stage slots | 4 first/base pairs and2 first/modified pairs | Only 3 accepted VM bases +1 accepted change; failed T2 preserved; stage separation limited |
| R6.16 C | 6 intents: kiln/custody ×base/s1/s2 | Human-like synthetic requirements, declared fields/guards/invariants, production lowering, changes, acceptance | Two closely related application skeletons; kiln raw-store defect inherited; no independent source/author attestation |
| R6.16 B | 6 parallel intents | Lean intent track comparison | Same requirements; not6 more diversity units and not genuine production semantics |
| R6.18 | 2 caller contexts, shared bounded-add and nested increment | Typed definitions, explicit twins, maps, 25 representation and6 serialization rejection controls | Exhaustive byte pairs qualify two finite contexts, not393,216 training examples; controls are not requirements episodes |
| R6.19–R6.25 | Failures/transport evidence; R6.23 has7 completed invalid candidates and1 interrupted call; R6.25 one incomplete construction attempt | Actual small-model outputs, native diagnostics, incomplete corrections | No accepted executable from these authoring attempts; do not label final invalid response as a solution |
| R6.32 | 5 scripted admitted definitions; 18 adversarial registry controls | Increment lifecycle, dependency/migration receipts, kiln original/modified intents | Scripted mechanics and reused kiln; registry persistence is not application state |
| R6.37 qualification | 1 observed SHAPE→accepted neutral correction chain | Exact malformed argument, diagnostic, corrected argument and successful11/000b execution | Neutral probe, not an independently generated software requirement; separate correction pool |
| R6.39 | 3 self-corrected migration calls reported across B/C | Typed feedback and subsequent valid requests | Alternative trajectories of existing episodes, not3 new requirements |
| R6.40 | 24 final evaluation condition slots:20 accepted,4 failed | Proposals, final artifacts, selftests, acceptance and replay | Six shared contracts; E3/E4 B/C offset failures and E4-B budget stop retained; additional revision not a new contract |
| R6.43 | 3 saved forms of1 provenance witness;39 input rows | Sidecars,39 expectation rows,14 claim-rejection controls, raw archive | Observation qualification, not3 new software programs or702 new examples |
| R6.44 | 1 new Lykoi intent, first=final | Policy successor, separate-session review, acceptance188/188, AI-free replay | Finite tested policy correct; complete store contract defective; older kiln source reused |
| R6.45 | 0 new executable targets | Source authority, static defect trace,18 proposed rows | Documentation only; proposed acceptance is NOT_RUN in that round |
| R6.46 | 1 integration correction bundle,0 new symbolic intents | Explicit profile/adapter,18 rows/25 observations,188 regression observations, exact replay | Same R6.44 intent; correction is integration code/profile, not a model-authored symbolic or MCP solution |

The R6.14 eight filenames and R6.15 twelve filenames were enumerated, not inferred
from execution totals. Auxiliary rows overlap: R6.32/R6.44/R6.46 reuse the kiln lineage,
and first/final/explicit/expanded forms can duplicate exact or near-identical programs.
**Do not sum this table into a training-example count.** It records additional
extractable evidence requiring a separate requirement/artifact/acceptance join.

Historical formal requirement contracts are present in production research, but an
FRC's valid serialization is not behavioral acceptance. No future benchmark source,
P6-A05 content or acceptance solution was read to augment this inventory. Exposed
B01–B20 are potential regression-only lineage, never a new held-out evaluation pool.

## Observed completeness

The17 source bundles have requirements, symbolic targets, deterministic validation
and bounded functional observations. Lifecycle bundles add pins/dependencies,
successors and replay. Available vocabulary/tool schemas are frozen or source-bound.
MCP records supply actual tool names, arguments and feedback for16 of17 bundles;
L36 supplies broker action bodies instead. Successful scored lifecycle corrections
are absent in L36–L38 (first proposals passed); known correction material comes from
neutral qualification, R6.39 migrations and R6.40 identity/revision failures.

Formal requirements differ in completeness: R6.40 compose byte-origin versus region
span is underexplicit. Its accepted A forms are finite-qualified examples, not a
resolution of compact B/C contract ambiguity. Original qualifications travel with
every target. Hidden reasoning and reconstructed causal explanations are unavailable
as training data. No exported reasoning field is assumed to be an attested trace.
