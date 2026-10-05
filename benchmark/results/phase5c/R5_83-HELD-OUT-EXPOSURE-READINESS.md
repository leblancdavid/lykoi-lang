# R5.83 — Held-out exposure readiness decision

## Decision and central answer

**`R5_83_B03_EXPOSURE_NOT_READY`**.

The current pipeline is not yet sufficiently qualified to promise that a material
unsupported decision will become a visible halt instead of a silently incomplete
inventory. Its structural rules fail closed **after** unsupported scope is declared.
Source-to-interface annotation, observation exclusions and coverage are still
unqualified reviewer trust boundaries; an erroneous completeness attestation can
pass the mechanical adequacy/authorization helpers. R5.80 also explicitly leaves
production independent input-generation/containment authority unqualified. R5.82
does not supersede that finding.

**Minimal methodological blocker:** no qualified independent source-to-contract/
interface coverage authority has been established that reliably identifies material
unsupported scope (or refuses coverage approval). This is a qualification/enforcement
boundary, not a demand to implement deadline, identity or event semantics, or to
make Lykoi complete. Writing a rule requiring complete review does not establish
that this boundary works. No large successor phase is prescribed by this decision.

The [frozen precommitment](r5_83/PRECOMMITMENT.md) specifies the candidate pipeline,
taxonomy, precedence and change policy. It freezes **current components and known
absences** as `R5.83-CANDIDATE-1`, not a production-ready deployment. The full
authoring/external-verification chain is specified architecturally, not qualified
end-to-end. These operational absences also prevent activation. No mechanical
pre-exposure check currently turns source-completeness judgment into qualified
authority; therefore **CONDITIONALLY_READY is not warranted**.

B03 remains **B03_PRISTINE / B03_NOT_EVALUATED /
B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT**. All access/activity counters are zero.
This report contains no inference about its contents or probability of success.

## Scope, provenance and artifacts

R5.83 is an audit/decision round only. Upstream results remain:

* R5.79 `R5_79_REQUIREMENT_FORMALIZATION_BOUNDARY_QUALIFIED` (architecture only).
* R5.80 `R5_80_REQUIREMENT_FORMALIZATION_PARTIAL`.
* R5.81 `R5_81_IMPLEMENTATION_ADEQUACY_PARTIAL`.
* R5.82 `R5_82_BEHAVIORAL_DECISION_DISCOVERY_PARTIAL`.

Sources are their exact public reports, FRC/BDI/adequacy/V1 specifications,
mechanical helper implementations, and already-public B01 candidate/receipt.
The pre-existing R5.82 files and three locally modified project records were
present at session start and are preserved. New evidence is coordinating audit
evidence, not an independent/isolated qualification. No subagent review occurred.

| Deliverable | Artifact |
| --- | --- |
| Readiness, stage inventory, limitations, criteria, B01 and walkthroughs | This report |
| Frozen candidate pipeline/version selections, taxonomy, precedence, precommitment, post-exposure policy | [PRECOMMITMENT.md](r5_83/PRECOMMITMENT.md) |
| Read-only synthetic negative controls, exact ordinary-component pinning and B01 reproduction | [audit.py](r5_83/audit.py) |
| Frozen observed outputs, component hashes, protected accounting | [audit.json](r5_83/audit.json) |
| Commands and interpretation limits | [README.md](r5_83/README.md) |

## Candidate pipeline: audit of what exists

Each row has an explicit downstream halt. A stage's stated review policy is
distinguished from qualified mechanical enforcement. The exact candidate versions
are in precommitment §1, with physical-byte pins in audit.json. No new formalizer,
discovery rule, authoring controller, mapper or oracle is developed here.

| Stage | Input → output | Authority and existing mechanical component | Reviewer dependence / unsupported scope | Failure and downstream halt |
| --- | --- | --- | --- | --- |
| 0. Sealed requirement admission | Authorized exact source + permitted context → immutable admitted source inventory/provenance | Independent benchmark owner; R5.79/V1 prescribe external independent preparation; existing static runner has one-time opening, not prose formalization | Trusted production source/review deployment and protected FRC admission not qualified; FRC-0.1 provenance currently only SYNTHETIC/PUBLIC. No B03 inventory is inspected | Missing authority/isolation/compatible admission: FORMALIZATION_UNQUALIFIED; broken integrity/controller: EVALUATION_INFRASTRUCTURE_FAILURE; **halt before source access** |
| 1. Requirement formalization | Admitted source/context → FRC-0.1 draft, IDs, issues, clauses/coverage/derivations | Independent formalizer; R5.80 structural schema/`validate`, quote/source commitments and relation checks | No automatic prose formalizer; clause meaning/parameters and implications require reviewers; unrepresentable FRC concepts cannot be squeezed into another kind | Ambiguity/conflict retained for review; unknown vocabulary/incomplete/unqualified candidate blocks review approval and all downstream implementation |
| 2. FRC review/freeze | Draft + source/context + evidence → separate exact-content fidelity receipt or refusal | Independent source-WHAT reviewer/owner; `review_gate` checks binding, distinct identity, eight boolean dimensions, active issues | Identity inequality/booleans do not prove isolation, coverage or semantic truth; richer evidence inventory/resolution authority not fully implemented; no trusted production approval qualified | NEEDS_CLARIFICATION / CONFLICTING_REQUIREMENT / REJECTED / INCOMPLETE_FORMALIZATION or binding error; **halt before discovery as an authorized stage** |
| 3. Behavioral discovery/coverage | Approved FRC + reviewed interface/facts/channels → BDI decisions, exclusions, UNKNOWN, coverage evidence | Independent annotation/coverage role; `discover`, 15 existing rule keys, two finite implication mechanisms | Annotation, channel completeness/exclusion authority, general reachability and inventory completeness remain reviewer-dependent; timing/identity/events and general traces/concurrency unsupported | Material UNKNOWN or unqualified annotation/coverage: DECISION_DISCOVERY_UNSUPPORTED, native OUTSIDE_ANALYSIS_SCOPE; **halt before adequate approval** |
| 4. Implementation adequacy | Same FRC + scoped complete BDI/finite authority analysis → adequate/underspecified/clarification/conflict/outside-scope | Separate adequacy authority; `analyze` finite option intersections, authority quote presence, scope/commitment/coverage checks; `authorization` conjuncts fidelity and adequate status | Completeness flag is attested; generic probes not exhaustive options; necessary implications, consumer contract and coupled choices not generally qualified; no production authoring enforcement | Native conflict → ambiguity → outside → underspecified; anything except adequate + full valid fidelity approval **halts before V1 projection/authoring** |
| 5. V1 faithful projection | Approved adequate FRC → full application/configuration/obligations + all-ID map + separate projection receipt → normalized V1 | Independent projection reviewer; R5.80 bounded projector and R5.77 deterministic adapter; whole-document identity/structure checks | Only source-selected complete public components plus existing supplemental kinds have demonstrated mapping; fidelity not equivalent to syntax; no general prose/FRC mapper | UNREPRESENTABLE_SOURCE / NO_QUALIFIED_COMPLETE_MAPPING → V1_REPRESENTATION_GAP; malformed packager/integrity → infrastructure failure; **halt without partial package or consumer dispatch** |
| 6. Lykoi capability/authoring | Exact faithful approved contract + frozen vocabulary/permitted model context → canonical Lykoi model or evidenced gap | Implementation role; normal Lykoi tools, no generated-file edits; existing gap classification | No new full authoring execution protocol/deployment qualified through R5.82; expressibility adjudication needs evidence independent of failing tests | Genuine unsupported semantics → LYKOI_CAPABILITY_GAP; available capability with failed composition → IMPLEMENTATION_FAILURE; uncertainty remains unresolved evidence; **halt without requirement change** |
| 7. Deterministic validation/lowering | Canonical model → validated program/generated executable + manifest or diagnostics | Frozen v0.3 compiler/backend (`src/air_compiler/`); validator/CLI/generator | Validation does not prove source coverage, contract satisfaction or semantic completeness; generic core 30 inherited, not newly recounted here | Implementation error, evidenced semantic gap or tooling failure distinguished; **halt before software execution on nonpass** |
| 8. External behavioral verification | Generated executable + independently prefrozen obligation-linked behavioral cases/context → external observations/result | Independent verifier; benchmark README external-subprocess principle; existing static runner is **not** a full acceptance controller | Full new-pipeline oracle derivation/execution linkage not qualified in R5.79–82; no actual B03 oracle selected/read; tests cannot choose intent or demand excluded freedoms | Required mismatch → IMPLEMENTATION_FAILURE; invalid/incomplete verifier → VERIFICATION_FAILURE; control failure → infrastructure; SUCCESS only on all required checks; **record first terminal result and stop** |

Absence of a full integrated evaluator is not evidence of a Lykoi language gap.
Freezing a protocol candidate does not fill that absence. Architecture can separate
diagnoses even while current mechanisms cannot warrant every transition.

## R5.80 limitation audit

“Blocker” means missing qualification of the evaluation process itself. A declared
limitation can reduce evidential strength without invalidating a correctly scoped
halt. No item is repaired in this round.

| Limitation | Disposition | Reason and frozen response |
| --- | --- | --- |
| Production input-generation authority not qualified | **Evaluation blocker, active** | No qualified independent source/context/coverage/containment deployment; structural approval cannot prevent hidden invention or omitted scope. FORMALIZATION_UNQUALIFIED before protected admission; preserve the missing authority, not just rename an experimental reviewer |
| Relation parameters partly textual | **Recorded methodological limitation; conditional blocker on undecidable material meaning** | Human review can in principle approve precise textual clauses without an executable calculus. Ambiguous or unsupported material entailment cannot be guessed: NEEDS_CLARIFICATION or FORMALIZATION_UNQUALIFIED. Text itself is not a mandate for a new DSL |
| AI-authored human-style synthetic corpus | **Recorded methodological limitation** | Does not qualify real-user generality. It does not make a faithfully independently reviewed future contract invalid; cannot substitute for missing production authority |
| Strict-isolation-qualified agreement 0/7 | **Recorded limitation of agreement evidence; active deployment blocker remains** | No inference of independent/cross-provider reliability. Zero is not a readiness score threshold; the disclosed containment failure prevents using this evidence to qualify the source authority |
| B01 formalizers diverged on defaulting scope | **Detected ambiguity, conditional source blocker** | Preserved alternatives visibly halt B01. This is evidence the gate can refuse a known ambiguous source, not proof it finds every ambiguity, nor a reason to guess future intent |

Limited V1 coverage (1/9 complete calibrated mapping) is not itself a readiness
score or requirement to expand V1. Missing faithful mapping can be a scientifically
interpretable V1_REPRESENTATION_GAP. Claims of fundamental impossibility require
stronger evidence than this prototype's missing mapper.

## R5.81 limitations after R5.82

| Earlier limitation | What R5.82 actually changes | Remaining active boundary |
| --- | --- | --- |
| Reviewer-dependent decision elicitation | Supported structural rule conjunctions now generate entries; downstream implementer need not invent each supported choice | Upstream fact extraction/review and unsupported family recognition remain; do not count supported rule firing as wholly manual or claim arbitrary-prose discovery |
| Reviewer-dependent inventory completeness | UNKNOWN propagates to unsupported sidecar; coverage defaults unreviewed | No independently approved whole-source coverage receipt/mechanical completeness proof. TRUE can still be incorrectly attested; production trust unqualified |
| Reviewer-dependent necessary implications | Two exhaustive finite-domain mechanisms derive/exclude score ties and lowercase collisions/identity | Exhaustiveness/source domain admission is asserted; arbitrary implications, temporal/coupled constraints and general reachability remain reviewer-dependent |
| Reviewer-dependent consumer observation scope | Explicit MEANINGFUL/DELEGATED/EXCLUDED channels structure the analysis; visible delegated ordering remains discovered | Source justification, missing channels and truthful exclusions not established mechanically or by qualified independent deployment |

R5.81 native precedence, finite independent-domain limitation, scope binding and
authority checking remain unchanged. R5.82 has **zero** independent/strict-qualified
reviews; it does not settle the earlier semantic mutation disagreements or create
production implementation grants.

## R5.82 limitations and unsupported-scope negative control

Recorded evidence: 26 synthetic cases, 29 expected decisions, **25 TP / 0 FP /
4 FN**, **12/12** irrelevant choices rejected, **6/6** hidden interactions,
**11/11** mutations, **4/4** finite probes. Same-context expectations/plans and one
disclosed post-result correction remain development evidence. None is a readiness
threshold; unsupported warnings are not counted as discoveries.

| Limitation | Disposition |
| --- | --- |
| Deadline boundary | **Conditional blocker if declared/material; unresolved reliable-detection boundary is a global readiness blocker** |
| Identity stability | Same: declared identity UNKNOWN can halt, omitted identity may not |
| Event ordering | Same: declared events UNKNOWN can halt, missing/misexcluded channel is not detected from prose |
| Event multiplicity | Same; return-value/input multiplicity support does not qualify emitted-event multiplicity |
| Structural annotation/observation scope/completeness | **Fatal to present exposure readiness** because independent trustworthy source-to-interface coverage approval is not qualified; erroneous positive attestations can conceal the four gaps |
| General reachability/coupled traces/concurrency | **Conditional blockers** where material; OUTSIDE_ANALYSIS_SCOPE rather than invented invariant or completeness claim. A source exclusion needs authority |
| Limited synthetic/independent evidence | **Acceptable declared evidence limitations**, but cannot serve as qualification for the unresolved global trust boundary |

The new read-only audit uses an invented requirement: store an integer durably and
emit exactly one public event per successful call. Both obligations remain in a
synthetic FRC. Its review receipt is a **negative-control bookkeeping receipt**, not
a truthful independent approval. No implementation, static consumer or grant runs.

| Annotation/attestation variant | Observed native output |
| --- | --- |
| Events MEANINGFUL; reviewed flag TRUE | Unsupported channel UNKNOWN; OUTSIDE_ANALYSIS_SCOPE; authorization helper false |
| Events omitted; default unreviewed coverage | OUTSIDE_ANALYSIS_SCOPE; authorization helper false |
| Events omitted; incorrectly asserted complete coverage TRUE | No UNKNOWN; persistence alone inventoried; IMPLEMENTATION_ADEQUATE; authorization helper **true** |
| Events incorrectly EXCLUDED; incorrectly asserted coverage TRUE | Same positive helper result despite source-required public event count |

This is not a bypass of a **truthful** independent reviewer and not a claim that
an authorized implementation ran. It demonstrates exactly where the mechanical
fail-closed guarantee ends: at reviewer-supplied interface completeness/exclusion
truth. The FRC review helper also accepts the structurally valid boolean receipt;
it does not compare event obligations against the BDI. Unknown channels cannot be
flagged if omitted before discovery. The same conditional trust boundary applies
to timing/identity/events; the audit does not claim measured miss rates for their
natural-language recognition. No new family or coverage mechanism is installed.

## Capability completion proposition

**Valid in principle and for Lykoi's research objective:** a held-out benchmark
does not require semantic completeness; it requires visible, interpretable
incompleteness under a frozen method. An independently justified material timing,
identity or event declaration would yield DECISION_DISCOVERY_UNSUPPORTED, which
is useful evidence without adding those capabilities beforehand.

**Not yet established operationally for this candidate:** R5.82 proves declared
unsupported channels stop a bounded adapter, not reliable recognition/refusal of
all materially unsupported source scope. A handwritten checklist or promise in
R5.83 cannot upgrade that observation into qualification. Thus the known misses
alone are not the blocker; their potentially silent omission at an unqualified
coverage authority is. Adding the four families would leave that same methodological
defect and is not justified by this gate.

## B01 protocol sanity check

Use only the exact already-public R5.80 B01 candidate and receipt, not its
implementation, acceptance tests or any held-out request. The read-only audit
reproduces `review_gate → NEEDS_CLARIFICATION`. Conditional discovery finds
`priority-lifecycle:default_trigger_domain` from B01.O07/O08/I1. Creation-only
omission versus creation omission plus absent historical stored priority remains
unresolved; admitted legacy-state reachability is not asserted as fact.

Adequacy diagnostic remains NEEDS_CLARIFICATION, authorization helper **false**,
Lykoi authoring **NOT_RUN**. Under strict stage precedence, the actual chain halts
at fidelity review; the known discovery/adequacy reproductions are public diagnostics,
not permission to run downstream after a source failure. The conceptual path
is: formalization/review → known behavioral decision exposed → unresolved authority
→ NEEDS_CLARIFICATION / implementation unauthorized → no authoring. B01 is not
fixed, not independently rediscovered and not used to alter readiness criteria.
Historical B01 acceptance remains historical evidence in its original scope.

## Counterfactual walkthroughs (synthetic, no B03 inference)

These audit classification paths, not executed complete implementations or new
approved contracts. Current experimental helpers distinguish local gates, while
the full production chain remains unqualified.

| Scenario | Invented situation and expected path | What current evidence supports |
| --- | --- | --- |
| A — fully supported | Exact durable behavior with independently complete authority/coverage, faithful existing V1 mapping and supported semantics → authoring → validation/lowering → independently frozen external checks → SUCCESS only if all pass | Stage distinctions specified; a complete joint source-to-software lifecycle is **not demonstrated**. Missing production prerequisites currently halt admission |
| B — ambiguity | “Return the best record” with no authoritative best criterion → NEEDS_CLARIFICATION / REQUIREMENT_AMBIGUOUS at review → no implementation | R5.80 preserved ambiguity demonstrates this selected pattern; no universal ambiguity-detection claim |
| C — event multiplicity | Exactly one public event per successful store → declared MEANINGFUL events → UNKNOWN → DECISION_DISCOVERY_UNSUPPORTED → no adequate approval/projection/authoring | Declared-channel halt reproduced. Omitted/misexcluded event scope plus false coverage attestation passes helpers: **reliable whole-source distinction is not qualified**, the decisive blocker |
| D — V1 gap | Precise adequate abstract requirement, no qualified complete unchanged V1 map → UNREPRESENTABLE_SOURCE / V1_REPRESENTATION_GAP → no package/authoring | R5.80 mapping failures and R5.81 separate adequacy axis support bounded diagnostic; no fundamental impossibility inferred |
| E — Lykoi gap | Adequate faithful representable contract needs semantics absent in frozen Lykoi → evidenced LYKOI_CAPABILITY_GAP → no weakening/emulation | Existing gap category and frozen-track discipline support distinction; representability alone does not prove semantic capability |
| F — implementation bug | Available capability, authorized author writes wrong selection boundary; validator may pass but external required observations differ → IMPLEMENTATION_FAILURE at behavioral verification | Classification specified; do not relabel as a capability gap after seeing failed tests. External result for this new chain not executed here |

If F's verifier itself crashes or cannot observe a required obligation, the outcome
is VERIFICATION_FAILURE, not an observed implementation bug. If packaging/controller
fails before valid observation, record EVALUATION_INFRASTRUCTURE_FAILURE, not a
semantic gap. All six are distinct in the frozen taxonomy; current protocol is
**not confirmed operationally reliable across them**, principally C and the missing
production transition qualification.

## Readiness criteria audit

“Specified” below does not mean “qualified”; a governance rule cannot count as
proof of its execution. No readiness criterion is lowered.

| # | Criterion | Finding |
| --- | --- | --- |
| 1 | Pipeline frozen before exposure | **Candidate selection/protocol pinned; executable production freeze incomplete**. Missing deployment, isolation and full authoring/acceptance closure prevents activation |
| 2 | Explicit stage halts | **Specified for every stage**, bounded helpers reject declared issues/unknowns; full production enforcement not qualified |
| 3 | Ambiguity cannot silently become authority | Active represented issues halt, including B01; **whole-source detection/independent authority unqualified**, so the unconditional criterion is not established |
| 4 | Missing behavioral authority cannot become implementation choice | Inventoried finite required choices fail on absent authority; **omitted choices escape** under incorrect completeness attestation |
| 5 | Unsupported discovery scope cannot be treated as complete | **NOT SATISFIED**: negative control distinguishes declared UNKNOWN from silent/misexcluded event scope; source-to-interface coverage trust unqualified |
| 6 | V1 cannot weaken requirements | Complete mapping/fidelity approval specified; missing mapper visibly fails closed. **General production projection review remains unqualified**; no partial projection authorized |
| 7 | Capability versus source/representation failure | **Explicit taxonomy and precedence**; evidenced semantic gap required, earlier source/projection failures not relabeled |
| 8 | Verification versus capability failure | **Explicit taxonomy/evidence rule**, external behavioral mismatch versus invalid verifier distinguished; integrated execution not qualified |
| 9 | Methodology limitations recorded | **Satisfied** by versioned upstream evidence and this audit; no PARTIAL upgrades |
| 10 | First result immutable | **Precommitted**: retain first terminal outcome/evidence; subsequent research separately versioned |
| 11 | Post-exposure development not pristine | **Precommitted**: permanently record exposure/contamination; repairs cannot reset status or first result |
| 12 | B03 untouched throughout R5.83 | **Satisfied by scoped session accounting**, inherited pristine status, exact public allowlist; no protected ledger/content/metadata inspection |

The smallest decisive defect is criterion 5's unqualified source-to-interface
coverage authority, shared with criteria 3–4 and R5.80 input production. Operational
freeze/enforcement/acceptance incompleteness is also recorded, not concealed by
a paper protocol. This is not conditional readiness because no already-qualified
mechanical precondition suffices to establish the missing semantic review boundary.

## Evidence, change policy and protected accounting

The first future frozen-pipeline outcome would be immutable, including an upstream
halt, verifier/infrastructure failure or contamination. Post-result fixes or
clarifications require separate authority and versioned records, explicitly marked
B03-informed; they cannot rewrite the first result or restore pristine status.
See precommitment §§5–6 for evidence, contamination and permissible research actions.
R5.83 itself ends at this decision; no access authority is issued.

The audit source reads only explicitly listed ordinary components plus public B01
candidate/receipt. Every B03 counter remains **zero**: source attempts/reads,
content-revealing metadata, formalization, decision discovery, adequacy, authorization,
reservations, packaging, opening, static/other consumer observation, generation,
execution, acceptance and repair. No B03 FRC/package/content commitment/eligibility
is created. This is session activity accounting with inherited pristine status,
not a claim of independently inspecting a protected ledger. No other held-out
source is read. B02 exposed/indeterminate history remains preserved.

Core **30** inherited; Phase 5C paused. No language/compiler/runtime/schema/V1,
benchmark requirement/oracle or historical evidence is changed. New Python is
read-only audit evidence, not evaluation capability development.

**Final: `R5_83_B03_EXPOSURE_NOT_READY`. Stop after R5.83.**
