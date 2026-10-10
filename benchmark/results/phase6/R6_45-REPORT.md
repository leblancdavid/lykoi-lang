# R6.45 — Malformed-state contract reconciliation

**Final classification: `R6_45_INTEGRATION_DEFECT`.**

The kiln contract determines the result: an existing store containing `{}` must
return **invalid_state**. Its source declares JSON-list storage, invalid persisted
state → invalid_state, and no migrations. A shared production decoder instead
raises **migration_required** for a missing/mismatched version tag before checking
shape or record validity. The application integration forwards that generic code.
No migration is selected or executed. This is an inherited persistence/error-
contract integration defect, not a demonstrated semantic capability gap.

## 1. Authorization and preserved baseline

This bounded [protocol](r6_45/PROTOCOL.md) permits documentation-only investigation.
Initial git status showed the R6.44 report/evidence/experiment and three guidance
files as untracked published work. All are preserved.

[Baseline](r6_45/BASELINE.json) verifies 5,059 inherited protected SHA256 identities,
116 R6.44 publication identities, the R6.44 manifest/receipt binding, 20 R6.44 frozen
input identities and nine R6.16 task-freeze identities with no mismatch. This covers
original requirements, historical starting sources and copied/generated submissions,
frozen acceptance files, production and protected research components. The original
R6.44 blank-label baseline adjustment, failed checks, scoring-summary correction,
raw diagnostics and `R6_44_COMPARISON_INCONCLUSIVE` classification remain intact.

Kernel remains **26**, on unchanged R5.114 accounting/protected implementation
identities; no independent recount. Production compiler/lowerer/runtime, R6.10 VM,
R6.18 wrapper, R6.23 adapter, R6.25 contracts and R6.32 registry semantics unchanged.
No repairs, generation, application runs, AI authoring, acceptance execution,
P6-A04 checks, P6-A05 access or historical rescoring occur in R6.45.

## 2. Authoritative requirement

[Inventory](r6_45/REQUIREMENT-AUTHORITY.md) separates source requirements, language
semantics, frozen expectations and observed behavior. Exact original clauses:

* `r6_16/tasks/COMMON.md`:3–5 — persistent JSON **list**, missing file empty,
  every operation reloads/validates the whole store.
* :5–12 — exact required fields/types/domains/invariant; “Invalid persisted state
  fails invalid_state, even for list; no repair is authorized.”
* :13 — “No migrations, concurrency or distributed IO.”
* R6.44 CONTRACT:23 and :44–49 — invalid entire store → invalid_state before
  lookup, guards and mutation input validation.

The literal `{}` is not individually enumerated in the original text. Its wrong
shape follows directly from “JSON list”; the expected code is explicit. Python's
output and a post-author diagnostic label are corroboration, not requirement authority.
There is **no material clarification needed for this input**.

## 3. Exact discrepancy cause and inheritance

[Trace](r6_45/DISCREPANCY-TRACE.md) reconstructs JSON parse → decode_state → Failure
→ wrapper output, with exact function sites and AST fingerprints.

Production `runtime_template.py`:96–97 compares `payload.get('schema_version')`
to current version 1. For `{}`, None differs from 1, so it raises migration_required.
The later envelope-key check and valid_state never run. This is decoder/version
discrimination, not parsing failure, migration selection, record validation or
transport reclassification. The wrapper at R6.16 generate.py:70–71 forwards e.code.

The template, accepted B baseline and B final have identical decode_state/read_state
AST fingerprints. Existing R6.44 diagnostics retain three operations per version:
Python invalid_state **6/6**, production-backed Lykoi migration_required **6/6**,
all preserving exact `{}` bytes. These counts describe existing unscored evidence;
no rerun, new denominator or rescore is performed.

## 4. Defect classification

[Classification](r6_45/DEFECT-CLASSIFICATION.md) assesses A–F. Category E is most
precise: a shared backend decoder's error classification is integrated into a
nonmigrating application without its required error boundary. The application is
observably defective, but its two authored policy guards did not cause the error.
Incomplete raw-store policy formalization and coverage contribute. The acceptance
expectation is supported. No new meaning or kernel construct is shown necessary.
The old SEMANTIC-AUDIT `capability_gap` field is retained without adopting its label
as proof of a language gap.

## 5. Correction options and regression risks

[Options](r6_45/CORRECTION-OPTIONS.md) and [risk assessment](r6_45/REGRESSION-RISKS.md)
evaluate application integration, shared backend changes and unjustified alternatives.

**Smallest recommended repair for the observed discrepancy:** a prospective,
application-scoped mapping of decoder-origin migration_required to the declared
invalid_state for explicitly nonmigrating version-1 list stores. It must preserve
all other errors, validation order and bytes. No production semantic change is
required by that narrow repair; no intent-only repair is demonstrated.

For complete list-format closure, additionally enforce the existing list-only
policy at the same-read application persistence boundary. Static inspection predicts
a matching version-1 envelope can currently be accepted; a code remap alone does
not fix that separate format seam. Neither prediction nor proposed correction is
behaviorally verified. Global remapping risks breaking genuine migration-enabled
applications. Shared production correction has greater scope and first requires
generic recognition/error-precedence clarification.

Do not special-case `{}`, invent legacy defaults, add migrations/primitives, alter
historical expectations or hand-edit generated behavior.

## 6. Prospective acceptance and remaining ambiguities

[Matrix](r6_45/PROSPECTIVE-ACCEPTANCE.md) freezes supported semantic expectations
for 18 small kiln rows: empty objects/lists, missing fields, valid current/old
same-schema data, malformed old records, unsupported-version objects, invalid types,
absence and competing store/lookup/guard/input defects. All are **NOT_RUN**.
Concrete execution fixture serialization/hashes must be bound before any future run.

Kiln has no distinct legacy schema. Its old valid lists are current-valid without
migration. Four separate scope/clarification rows distinguish genuine versioned
legacy compatibility, malformed old-version normal-read precedence and unsupported
versions in migration-enabled applications. Unresolved expectations are not frozen.
No uncertainty there overrides the determined kiln `{}` expectation.

## 7. Architectural implications

[Assessment](r6_45/ARCHITECTURAL-IMPLICATIONS.md): the application obligation is
specific, the originating decoder is shared. Typed invariants and structural
validation do not ensure requirement fidelity for errors raised earlier in decoding.
This exposes a persistence/error-contract integration and review-coverage seam.
Explicit shape/recognition/error-precedence facts carried through lowering are a
design recommendation, not an implemented or demonstrated necessary architecture.
No universal soundness failure, kernel gap or comparative advantage is established.
The analysis is same-agent, exposed review; requirement-derived matrix independence
does not mean independent human authorship or experimental replication.

## 8. Publication and stop

[Publication identities](r6_45/PUBLICATION-IDENTITIES.json) and
[verification receipt](r6_45/VERIFICATION.json) bind these new documents and report
preservation, static/documentation integrity and `git diff --check`. No behavioral
tests or matrix executions are claimed. Versioned
[boundary](../../../docs/project-overview-r6.45.md),
[observations](../../../docs/research-log-r6.45.md) and
[decision](../../../docs/decisions-r6.45.md) preserve shared historical guidance.

**Stopped after documentation-only publication.** Smallest next step is explicit
authorization for a versioned application-integration successor correction and
focused requirement-supported verification, distinguishing code-only repair from
full list-shape closure. No further implementation, experiment or run is authorized.
