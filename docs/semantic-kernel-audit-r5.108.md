# Lykoi semantic kernel audit — R5.108

**Classification: `R5_108_SEMANTIC_KERNEL_CONVERGING`.**

This is an analytical architectural proposal, not a language revision, proof of
minimality, production refactor or extension of supported behavior. The bounded
normal path is converging toward composition. The repository does **not** contain
one fully integrated, general-purpose 30-primitive implementation.

## 1. Findings and counting boundary

* The exact R5.40/R5.41 inherited candidate count is **30**: 29 from R5.5,
  plus cardinality from R5.10. The raw categorized ledger has **46** entries.
* **18 original candidates remain proposed core** (7 active, 11 refined).
  Two are absorbed, four reclassified as compositions, six unresolved; none
  is declared deprecated. Some retained concepts have only historical executable
  support, notably general cardinality. Core classification does not grant normal
  compiler support.
* Four behavioral concepts were missing from that candidate accounting:
  input presence, resource/capability authority, durable state, atomic commit.
  All have pre-R5.41 antecedents. They are **new to this accounting**, not four
  discoveries first made in R5.104–R5.107.
* The **proposed current architectural kernel is 22 concepts**: 18 retained + 4
  previously uncounted. No additional irreducible category first appearing after
  R5.41 is established by this audit. New executable operators, type domains and
  supported interactions are real progress even when their conceptual foundations
  are older.
* CollectionQuery, pipelines, predicate trees, guards, migration and lifecycle
  are compositions. Their order, authority and rejection behavior remain material.
  Calling something a composition does not make those obligations optional.
* Significant conceptual duplication and partial backend dependence remain.
  No consolidation or leak repair is performed here.

The count measures independently specified semantic concepts at the granularity
in section 4. It does not count JSON keys, operator aliases, FRC labels, every
primitive type, backend functions or supported profiles. It is not a measured
minimum. A more expressive future fold/quantifier algebra could change the
decomposition; it is not silently assumed to exist today.

## 2. Authoritative original recovery

The R5.40 report, section “Candidate core”, states **30**, no #31; the R5.41
report states **30** at its introduction and conclusion. Neither publishes a
replacement list. Their inherited definition is recoverable exactly from:

| Evidence ID | Repository evidence | What it establishes |
| --- | --- | --- |
| H1 | `benchmark/results/phase5c/R5_4-SELECTION-VOCABULARY-LEDGER.md`, rows #1–45 and checkpoint counts | Exact names/signatures; 42 → 44 → 45 raw entries; mixes semantics with observation machinery. |
| H2 | `benchmark/results/phase5c/R5_5-SEMANTIC-ARCHITECTURE-SEPARATION.md`, “Responsibility inventory” | Core membership is #1–23, #25–27, #43–45: **29**; excludes clock observation #24 and #28–42. |
| H3 | `benchmark/results/phase5c/R5_10-MIGRATION-COUNT-EXPRESSIVENESS.md`, sections 2–5, and `benchmark/semantic/README.md:3–14` | Adds cardinality as **candidate core #30**, making 30 core / 46 raw. Count is by occurrence, not changed fields. |
| H4 | `benchmark/results/phase5c/R5_40-BOUNDARY-PROFILE-ADMISSION-B02-CONFIGURATION.md`, final accounting | Inherits the 30; boundary/configuration work is not new core. |
| H5 | `benchmark/results/phase5c/R5_41-INDEPENDENT-OPTIONAL-BOUNDARY-SUPPORT-COHERENCE.md` | Inherits 30; nullable support is profile composition, not #31. |

**Identity collision:** raw historical **#30 is `invoke`**, excluded by H2.
H3's **core #30 is `cardinality`**, an appended concept, not a renaming of
`invoke`. Below `Lxx` denotes the raw H1 ledger ID; `C30` denotes H3 cardinality.
There is no invented consecutive renumbering of the original 29.

The original set is exactly:

`record schema, field, finite sequence, var, literal, equals, and, not,
contains, selection, exactness, source_relative, trim, nonblank, map(trim),
stable_unique, for_each, directed graph, add_edge, acyclic, transition,
precondition, finite domain scope, instant, offset, before,
lexicographic_order, default_missing, operation contract, cardinality`.

The historical “30 substantive” in the final H1 checkpoint includes #24 clock;
H2 subsequently removes the observation mechanism, producing 29. H3 then adds
cardinality. Thus equal numeric counts at different checkpoints do **not** imply
identical membership. The historical definition is provisional and unfrozen.

## 3. Exact original-to-current lineage / kernel table

Paths `bs/` and `ac/` below abbreviate `benchmark/semantic/` and
`src/air_compiler/`. Original purpose/name comes from H1 except C30 from H3.
Reuse is demonstrated normal behavior unless explicitly marked prototype. B-case
references are selected local examples, not an exhaustive clause count. Evidence
does not support a uniform per-primitive B01–B20 denominator.

| Original identity / semantic concept and purpose | Original evidence | Current level | Current status / explanation | Current implementation location | Demonstrated reuse / leverage |
| --- | --- | --- | --- | --- | --- |
| L1 record schema: typed entity shape | H1/H2 | CORE K01 | CORE_REFINED: closed typed records now compose scalar/collection/boolean domains | `bs/selection.py`, `ac/validator.py`, `mutable_values.py`, `predicates.py` | All B01–B13 local realizations and all normal synthetic record domains; very high |
| L2 field: typed projection | H1/H2 | CORE K02 | CORE_ACTIVE: reading a record member remains independent of binding a parameter | `bs/selection.py`, `ac/predicate_runtime.py:predicate_value`, `runtime_template.py:field_name` | Queries, writes, guards, migrations across normal domains; very high |
| L3 finite sequence: ordered finite values | H1/H2 | CORE K03 | CORE_REFINED: element typing, occurrences, independent order/duplicate/equality policies | `bs/selection.py`, `ac/mutable_values.py`, `mutable_runtime.py` | Record stores plus B02/B03/B07/B10 collections; article/contact/product/profile; very high |
| L4 var: typed bound value | H1/H2 | CORE K04 | CORE_REFINED: field/parameter/resource/staged operand scopes are explicit; not arbitrary code | `bs/selection.py`, `ac/predicates.py`, `predicate_runtime.py` | Every query/operation input; four R5.106 and four R5.107 domains; very high |
| L5 literal: typed constant | H1/H2 | CORE K05 | CORE_ACTIVE: types expanded, constant meaning unchanged; no omission trigger | `bs/selection.py`, `ac/input_values.py`, `mutable_values.py`, `runtime_template.py:value_of` | Defaults, creation and B08 literal archive writes; four R5.105 and four R5.107 domains; high |
| L6 equals: same-type equality | H1/H2 | CORE K06 | CORE_REFINED: operand types, comparison policy and atomic null-false explicit; storage equality distinct from instant equality | `bs/selection.py`, `ac/predicates.py`, `predicate_runtime.py` | B01/B03/B04/B05/B08/B11/B12/B13 plus every condition corpus; very high |
| L7 and: conjunction | H1/H2 | CORE K07 | CORE_ACTIVE: pure truth operation; evaluation is now explicitly all-children in normal predicates | `bs/selection.py`, `ac/predicate_runtime.py` | Owner/exclusion/range/guard compositions B09/B11/B12/B13; four predicate domains; high |
| L8 not: complement | H1/H2 | CORE K08 | CORE_ACTIVE: two-valued complement, including complemented null-false atoms | `bs/selection.py`, `ac/predicate_runtime.py` | Negation/grouping/null tests, B11 guard and B13 archive conditions; four predicate domains; high |
| L9 contains: sequence membership | H1/H2 | CORE K09 | CORE_REFINED: scalar IN collection canonical direction, typed operands and policies | `bs/selection.py`, `ac/collection_query_runtime.py:legacy_predicate`, `predicate_runtime.py` | B03/B12, labels/users/sessions/products/documents synthetic selection; high |
| L10 selection: relate source, predicate and result | H1/H2 | CORE K10 | CORE_ACTIVE: finite occurrence selection remains a fundamental collection relation | `bs/selection.py:evaluate`, `ac/collection_query_runtime.py` | Query family B01/B03/B04/B05/B08/B09/B12/B13; six R5.98 compositions, fourteen successful R5.99 captures; very high |
| L11 exactness: exact vs sound-only selection | H1/H2 | CORE policy | ABSORBED into K10 result relation; coverage of qualifying occurrences is a parameter, not another operation | `bs/selection.py:evaluate`; current queries exact by contract | Exact normal queries broadly reused; sound-only remains prototype; high for exactness, insufficient normal evidence for sound-only |
| L12 source_relative: retain selected occurrence order | H1/H2 | CORE policy | ABSORBED into K03/K10 occurrence semantics; not an additional selection primitive | `bs/selection.py:evaluate`; query ordering subsequently composes explicit keys | Prototype B01/B03 witnesses, current collection preservation; medium |
| L13 trim: remove outer whitespace | H1/H2 | CORE K11 | CORE_REFINED: explicitly typed pure text transformation with stage placement; Unicode boundary partial | `bs/invariants.py`, `ac/mutable_runtime.py:mutable_pipeline` | B02/B06; article/contact/product/profile pipelines; high |
| L14 nonblank: non-whitespace predicate | H1/H2 | COMPOSITION | COMPOSITION: trim + inequality with empty; validation adds outcome/error context | `bs/invariants.py`, `ac/runtime_template.py`, `mutable_runtime.py`, `collection_query_runtime.py` | B06/B07 and creation/query synthetic errors; high |
| L15 map(trim): pointwise transform | H1/H2 | CORE K12 | CORE_REFINED: bounded `map_elements` retains one finite pointwise traversal concept; trim is its argument, not another map primitive | `bs/invariants.py`, `ac/mutable_runtime.py:mutable_pipeline` | B02 and four mutable/input domains; medium |
| L16 stable_unique: retain first equal occurrence | H1/H2 | CORE K13 | CORE_ACTIVE: order/representative choice is irreducible in current bounded traversal vocabulary; no generic fold is assumed | `bs/invariants.py`, `ac/mutable_runtime.py:mutable_unique` | B02; four R5.104 domains with independent duplicate policies; medium |
| L17 for_each: universal element property | H1/H2 | COMPOSITION candidate | EXPERIMENTAL/UNRESOLVED: fixture quantifier and built-in all-record validation exist; arbitrary related-state quantification does not | `bs/invariants.py:evaluate`; `ac/mutable_runtime.py:valid_state` only bounded checks | Historical B02 witnesses; no B15 normal behavior; insufficient evidence |
| L18 directed graph: nodes and edge set | H1/H2 | COMPOSITION candidate | EXPERIMENTAL/UNRESOLVED: typed prototype graph, not persistent normal relationships | `bs/invariants.py`, not `bs/relationships.py` (that is requirement lineage) | B14 finite witnesses only; low |
| L19 add_edge: graph set insertion | H1/H2 | COMPOSITION candidate | EXPERIMENTAL/UNRESOLVED: abstract insertion exists; persistent integrity/effect binding absent | `bs/invariants.py:evaluate` | B14 finite witnesses only; low |
| L20 acyclic: no self reachability | H1/H2 | CORE candidate, excluded from count | EXPERIMENTAL/UNRESOLVED: requires transitive reachability authority beyond current local predicates | `bs/invariants.py:evaluate` graph search | B14 finite witnesses only; insufficient normal evidence |
| L21 transition: typed before/after relation | H1/H2 | CORE K14 | CORE_REFINED: explicit staged candidates and effects; lifecycle is a restricted application of state change | `bs/invariants.py`, `bs/state_relations.py`, `ac/runtime_template.py:execute`, `mutable_runtime.py:execute_mutation` | B02/B07/B08/B10/B11/B13 writes and lifecycle; four mutable domains; very high |
| L22 precondition: applicability predicate | H1/H2 | COMPOSITION | COMPOSITION: predicate + operation outcome + rejection frame; stage and precedence remain obligatory | `bs/invariants.py`, `ac/predicate_integration.py`, `collection_query_runtime.py:prepare_query` | B09/B11/B13 and four interface domains; high |
| L23 finite domain scope: universal scoped rule | H1/H2 | PROFILE / INTERFACE | EXPERIMENTAL/UNRESOLVED: finite semantic quantification is not the finite witness runner; current profiles constrain evaluation scope, not a general quantifier | `bs/invariants.py:validate`; bounded normal invariant validators | Historical sequence/graph witnesses; no general quantified normal rule; insufficient evidence |
| L25 instant: typed UTC time, separate from clock | H1/H2 | CORE K15 | CORE_REFINED: value interpretation is parsed instant, preserving separate wire/storage spelling | `bs/format.py`, `bs/capability_boundary_r5_22.py`, `ac/predicates.py`, `predicate_runtime.py` | B09/B12, sessions/documents clock/range examples; high |
| L26 offset: integral seconds added to instant | H1/H2 | CORE candidate, excluded from count | EXPERIMENTAL/UNRESOLVED: scenario arithmetic is not authorized normal program arithmetic or calendar-day semantics | `bs/format.py` / `probe.py` | Controlled time witnesses, no B19 normal execution; insufficient evidence |
| L27 before: strict instant ordering | H1/H2 | CORE K16 | CORE_REFINED: typed strict-order comparison; le/ge/ranges derive from order/equality/logic, not fresh range cores | `bs/format.py`, `ac/runtime_template.py:select_records`, `predicate_runtime.py` | B09/B12 plus four predicate/interface domains; high |
| L43 lexicographic_order: exact permutation + key precedence | H1/H2 | COMPOSITION | COMPOSITION: typed ordered comparison + key projection + collection/result constraints; preserve direction/tie policy | `bs/state_relations.py`, `bs/generative_r5_13.py`, `ac/collection_query_runtime.py` | B01 and all normal listings; synthetic gallery/query domains; high |
| L44 default_missing: preserve present fields and identity set, fill absent field | H1/H2 | COMPOSITION | COMPOSITION: presence + literal/binding + frame-preserving transition; creation default is a different boundary | `bs/state_relations.py`, `ac/runtime_template.py:migrate`, `profiles.py` | B01/B02/B07/B08/B10 schema introduction; scalar/mutable synthetic migration; high |
| L45 operation contract: typed (input, pre, outcome, post) relation | H1/H2 | CORE K17 | CORE_REFINED: operation identity binds outcomes/state and effect authority for one invocation; no branch-specific core | `bs/contracts.py`, `ac/validator.py`, `semantics.py`, `runtime_template.py` | Original synthetic tuples and current CRUD/query failure/effect contracts; very high, general tuple checker remains bounded |
| C30 cardinality: occurrence count related to integer | H3 | CORE K18 | CORE_ACTIVE: finite extent cannot be derived from equality/selection without another count/index axiom | `bs/cardinality.py`, `bs/generative_r5_13.py`, `ac/runtime_template.py:migrate` (specialized count) | Historical migration and independent generative domains; low normal leverage, no public aggregate query |

“COMPOSITION candidate” is the level proposed for a concept if its missing
authorities can be supplied; it is not an assertion of executable reduction.
Unresolved graph reachability and offset are explicitly outside the 22 count.
Deprecated is zero because an unsupported prototype is not evidence that its
meaning is unnecessary. Historical files retain their original identity/status.

## 4. Proposed kernel: explicit accounting unit

K01–K18 are the concepts named in section 3. K19–K22 complete the accounting:

| Semantic concept | Original status | Current level | Current status | Demonstrated reuse | Notes / implementation |
| --- | --- | --- | --- | --- | --- |
| K19 input presence / absence observation | Uncounted; pre-R5.41 `fallback`, optional inputs and missing-field defaults | CORE | CORE_REFINED relative to earlier behavior | B01/B06/B07/B10, four input domains; high | Mapping membership, not truthiness, null or default; `input_values.py`, `mutable_runtime.py`, `predicate_runtime.py` |
| K20 typed resource/capability authority | Uncounted; v0.3 `requires`/capabilities and R5.22 external binding | CORE | CORE_REFINED | Clock/ID/storage reads/writes, B09/B12; controlled providers across normal domains; high | Independent of K17 effect declaration; `validator.py`, `creation_provider_runtime.py`, query resource validators |
| K21 durable state / persistence boundary | Uncounted; v0.2/v0.3 state storage and pre-R5.41 state adapters | CORE | CORE_ACTIVE | All persisted B01–B13 local programs and normal mutable/scalar domains; very high | Survives process exit/reload; cannot be reduced to in-memory transition; `runtime_template.py:read_state/write_state`, `profile_runtime.py` |
| K22 atomic commit / all-or-unchanged effect | Uncounted; existing atomic file writes/failure model, made explicit for staged record writes R5.104 | CORE | CORE_REFINED | Multi-field synthetic failures, B06/B08/B10/B13 rejection/reload; high | State transition alone does not imply durable atomicity; `mutable_runtime.py:execute_mutation`, `runtime_template.py:write_state` |

K01 includes scalar domains, finite enums and bounded nullable/type constructors;
K03 includes ordered collection types. This is not a claim that strings, booleans,
time and integers are interchangeable: K15 supplies time interpretation, K06/K16
specify relations, K11 supplies text computation, K18 supplies extent. K05 literal
and K04 binding are retained separately because exact declared values and supplied
environment values have different authority/provenance and default applicability.
K02 projection is distinct from environment resolution. K14 specifies state change;
K17 binds it to an invocation/outcome/effect frame; K20 authorizes resource access;
K21/K22 add durability and commit boundaries. Merging these would hide observable
or authorization obligations.

Predicate is a **semantic family**, not one opaque unit used to conceal its
operators. K06 equality, K16 strict ordering, K09 membership, K07 AND and K08 NOT
are separately counted irreducible relations at the supported algebra's current
granularity. OR derives by De Morgan under the explicitly pure two-valued model.
K19 presence is an independent observation. Null tests are optional-domain tag
inspection under K01/K02, not a second absence primitive. Conversely trim and
stable-first dedup are retained core operations: naming a generic “Transform”
without defining these operations would merely push meaning into Python.

### Exact growth equation

| Original candidate disposition | Count | Identities |
| --- | ---: | --- |
| Still core unchanged (CORE_ACTIVE) | 7 | L2,L5,L7,L8,L10,L16,C30 |
| Refined core (CORE_REFINED) | 11 | L1,L3,L4,L6,L9,L13,L15,L21,L25,L27,L45 |
| Absorbed | 2 | L11,L12 |
| Reclassified composition | 4 | L14,L22,L43,L44 |
| Deprecated | 0 | None established |
| Experimental/unresolved | 6 | L17,L18,L19,L20,L23,L26 |
| **Original total** | **30** | Every original candidate exactly once |

**Original retained core = 7 + 11 = 18.** New-to-ledger core concepts = **4**.
Genuinely new core categories first introduced after R5.41 = **0 established**.
**Proposed current kernel = 30 − 2 − 4 − 6 + 4 = 22.**

This is consolidation analysis, not a historical claim that earlier implementations
already supported all these compositions, nor a claim that all 22 have one shared
executable IR. The old general cardinality experiments remain part of the retained
conceptual kernel, while the normal dispatcher exposes only specialized migration
counting. The six unresolved concepts cannot be counted as integrated capability.

## 5. Post-R5.41 inventory and first-introduction discipline

“First” distinguishes first conceptual evidence from first **normal-path** support.
Rows cover behavioral additions/refinements and every selected envelope, not each
fixture or compiler helper. Semantic levels use the same decomposition as above.
Synthetic domains demonstrate bounded reuse, not independent held-out generality.

| Candidate addition / material generalization | First evidence / current extension | Purpose / current level | Benefiting exposed cases | Demonstrated synthetic reuse |
| --- | --- | --- | --- | --- |
| Requirement WHAT/HOW separation, FRC typed obligation labels | R5.79 boundary; R5.80 FRC | PROFILE / INTERFACE: authority/representation, not new operation semantics | All current attempts; success attribution is not behavioral leverage | Public R5.80 requirement corpus; includes unsupported arithmetic/event requirements |
| BDI rule families, finite implications, adequacy choices | R5.81 adequacy / R5.82 discovery | Analysis machinery over behavior; not kernel, even when a rule describes a semantic distinction | All supported paths; B18 unsupported discovery | R5.82 26-case diagnostic corpus; not application semantics |
| Source inventory/reconciliation, controller/workspace, author/verification seals | R5.84–R5.89; live/freeze variants R5.90–R5.96 | Non-language authority/test machinery; excluded | Pipeline execution, not additional behavior | Synthetic governance challenges; not software domains |
| CollectionQuery source/predicate/comparison/order/validation/inclusion/effect/result | R5.98; selection antecedent L10–12/L43 | COMPOSITION of K01–10/K16/K17/K20/K21 | B03/B04/B05 and later B08/B09/B12/B13 | Products/category, users/department, documents/owner and labels; six compositions |
| Casefold comparison, independent strip policy | Query definition R5.98; trim antecedent L13 | CORE K06/K11 operator/policy refinement; not stored-value transformation | B03 uses exact membership; no claim of benchmark casefold requirement | Explicit casefold and strip neighbor contrasts in R5.98/R5.99 |
| Key directions/precedence and identity tie-break | R5.98 normal query; L43 antecedent | COMPOSITION / ordering policy | All current listings; B09 ranges preserve ordering | All six query compositions; R5.99 captures |
| Whole-record, empty/null/error result policy; detached records, exact selection | R5.98, older selection/outcome relations | COMPOSITION K10/K17 with result policy | Query cases including B09 successful empty result | Six query compositions and no-match contrasts |
| CollectionQueryDocumentV1, normal LykoiContractV1/Program dispatcher | R5.98 standalone; R5.99 normal path | PROFILE / INTERFACE, not extra query behavior | Normal query transfers | R5.99 sixteen captures: fourteen executions, one clarification, one refusal |
| Read-only store adapter / complete-state validation before selection | R5.98 array; R5.99 model state | COMPOSITION K17/K20/K21 plus validity boundary | B03 onward queries | Products/users/documents; corruption and unchanged-byte cases |
| existing-scalar-1: typed fields/defaults/lifecycle/resources/additive migration | R5.102 normal integration; v0.3 antecedents | PROFILE / INTERFACE over existing semantics | B04/B05; later fresh B01 | Three scalar public domains; gallery equality/field evolution/enum expansion |
| Equality guard/model amendments, independent lifecycle fields | R5.103 integration; earlier guards/transitions | COMPOSITION K06/K14/K17, bounded profile | B01/B04/B05; later archive guard composition | Guarded required-field evolution, dual lifecycle and clock cases |
| existing-model-1 / existing-composed-1, scalar-query same-state binding | R5.103 | PROFILE / INTERFACE; interaction validation not arbitrary profile union | Prerequisite for later writable/query cases | Scalar/query composition and conflict challenges |
| Controlled UUID/UTC creation binding | R5.103 normal API; v0.3 and R5.22 antecedents | CORE K20 refinement / adapter | IDs/time in normal creations; no new case first-success in R5.103 | Controlled collision/type/refusal/reset, clock boundaries |
| Ordered typed writable collections, enum elements, equality/duplicate policies | R5.104 normal; L3/L6 antecedents | CORE K01/K03 refinement; uniqueness is a type constraint | B02/B03/B07/B10 | Articles, contacts, products, profiles: four domains |
| Scalar/collection replace, append, add_unique, staged multi-field update | R5.104 normal; old state/effect antecedents | COMPOSITION K03/K06/K14/K17/K22; operations differ materially | B02/B07/B10 and literal archive extensions later | Four mutable domains; rejected second-field/commit failure tests |
| Verbatim/trim/stable_deduplicate/map_elements pipeline | R5.104 normal; L13/L15/L16 antecedents | COMPOSITION of K11/K12/K13; verbatim identity | B02/B06/B10 | Four mutable domains with occurrence/pipeline-order contrasts |
| InputPresence, omitted unchanged/reject; creation-only defaults | R5.104 explicit; pre-R5.41 optional/fallback antecedents | CORE K19 refinement + COMPOSITION outcomes | B06/B07/B10 | Four mutable/input domains |
| Ordered validation stage, nonempty/nonblank/typed checks | R5.104; R5.105 stage closure | COMPOSITION predicate/type checks + staged outcome | B06/B07, preserving previous successes | Four mutable/input domains |
| Collection literals / required input / omission default disjoint sources | R5.105 normal closure; K04/K05/K19 antecedents | COMPOSITION sources with PROFILE shapes | B07 newly succeeds | Articles/contacts/products/profiles; four input domains |
| RAW/TRANSFORMED/PERSISTED and conditional local observations | R5.105 explicit stages; ordered pipeline R5.104 | COMPOSITION binding observation points; no extra persistent-state tag | B06 newly succeeds | Four input domains, raw-empty/whitespace/trim contrasts |
| SemanticParameters vs ExternalBinding, required CLI vs application error | R5.105 normal; R5.32 binding antecedent | PROFILE / INTERFACE transport; outcome/rejection behavior uses K17/K19 | B07 and later query errors | Four input domains, supplied/omitted/renamed-flag cases |
| Typed Predicate trees, AND/OR/NOT/grouping | R5.106 normal; L6–9/L27 antecedents | COMPOSITION of core relations; OR derived, no range primitive | Components B08/B09/B11/B12/B13; no new R5.106 first-success | Products/users/sessions/documents: four predicate domains |
| Null/presence, membership direction, nullable atom false, parsed UTC comparisons | R5.106; timestamp/null antecedents v0.3/R5.38 | CORE relation/type policy refinements; presence K19 | B09/B12 later verified | Four predicate domains, grouping/null/boundary/membership contrasts |
| One predicate interpreter for selection, prewrite guards, local staged validation and record invariants | R5.106 integration | COMPOSITION contexts; context-specific effects and scope remain distinct | B11/B13 later verified; invalid-state checks | Four predicate domains; authority-loss, corruption, stage tests |
| Boolean creation/storage/migration/input replacement | R5.106 writable; R5.98 read-only booleans and original literals | CORE K01 domain integration + existing mutation/migration composition | Prerequisites B08/B11/B12/B13 | Four predicate domains, persist/reload tests |
| Exact typed literal replacement | R5.107 normal; literal/replace already supported separately | COMPOSITION K05/K14/K22 / interface closure | B08, enabling B11/B13 | Accounts/products/documents/sessions: four interface domains |
| Existing listing normalization, exact-base AND/OR/replace selection amendments | R5.107 | COMPOSITION selection + amendment authority; profile interface | B08/B11/B12/B13 | Four interface domains, preserved ordering/inclusion/clock base |
| Query preconditions, parameter errors, before-selection rejection | R5.107 normal closure; L22/K17 antecedents | COMPOSITION typed predicate/outcome/read-only frame | B09; supports B12 | Four interface domains; missing/type/validation/precondition/empty-result contrasts |
| Declared resource operands and once-per-query clock sampling | R5.107 normal closure; K20 antecedents | CORE authority refinement + PROFILE binding/sampling policy | B12 | Four interface domains plus injected-clock subprocess |
| task priority/tags/notes/archive/owner/status | Application baseline and B01–B13 realizations | APPLICATION; field names and enum members are not new kernel | B01–B13 | Analogous product/document/session/account values, not identical application concepts |

R5.42–R5.78 consist of evidence, execution identity, qualification, boundary and
packaging work on the inherited behavioral algebra. They do not establish another
numbered core. Relevant changed boundaries are documented by
`ai-independence-r5.48.md`, `benchmark-document-contract-v1.md` and
`benchmark-source-packaging-r5-78.md`; these are interfaces/provenance, not new
software behavior. R5.97 is first exposure/evaluation, R5.100 exposure accounting,
R5.101 capability diagnosis; none adds language behavior. R5.103 also rebaselines
captures. Serialized FRC relation kinds such as `sum`, `external_effect`, `crud`
and `filter_order` are not proof that the compiler implements those behaviors.

## 6. Predicate audit

The normative normal algebra is `typed-predicates-v1.md` and
`ac/predicates.py` / `predicate_runtime.py`.

| Construct | Decomposition / protected distinction |
| --- | --- |
| Equality | K06 primitive relation, exact typed domains and declared comparison policy. No Python bool/int coercion. |
| Ordering | K16 strict order primitive, currently timestamp-only in normal predicates; generalized representation does not grant integer arithmetic. `le/ge` compose strict order/equality; `gt` reverses operands. |
| Membership | K09 primitive in the current bounded algebra; cannot claim derivation from a general existential quantifier that is absent. CONTAINS and IN are one direction-normalized concept. |
| AND, NOT | K07/K08 truth primitives, pure all-child evaluation; no effect/short-circuit authority. |
| OR | Logical composition `NOT(AND(NOT a, NOT b, ...))`; explicit node is a machine representation of the same truth operation, not a new category. |
| Null test | Nullable-domain tag observation; not equality with omitted input and not general SQL three-valued logic. |
| Presence | K19 mapping observation. Supplied null, empty and whitespace are still present. |
| Range | AND of lower/upper comparisons with independently authorized inclusivity. |
| Predicate tree | COMPOSITION of typed operands, atomic relations and Boolean operators. `Predicate` alone is not a sufficient definition of those atoms. |

An atomic comparison with null/omitted optional input is false; NOT complements
it, so explicit null exclusion may be required. Grouping is material. Source
reconciliation supports bounded associative/commutative/idempotent AND/OR and
double negation, not arbitrary theorem proving. Exact V1 grouping is preserved.
Reconciliation equivalence and executable operator identity are distinct concerns.

## 7. Value and transformation audit

* **Scalar:** typed domain under K01; domain interpretation is explicit, especially
  time K15. A “scalar” label does not define arithmetic, Unicode or coercion.
* **Literal vs runtime parameter:** K05 exact value vs K04 environment binding;
  representations differ materially in input/default/source authority.
* **Default:** conditional binding chosen on K19 omission at a declared boundary.
  Creation default, update preservation and historical migration default are not
  interchangeable grants.
* **Omission vs null:** omission is environment membership; null is a value in a
  bounded optional timestamp domain. They are not two names for `None`.
* **Ordered collection:** K03 finite occurrence sequence, not set. Uniqueness is
  a type/invariant constraint using K06. Duplicate allow/unique is policy; rejecting
  duplicates differs from explicitly transforming them away.
* **Verbatim:** identity transform (including an empty pipeline); no independent
  primitive, but an explicit preservation obligation.
* **Trim:** retain K11's defined text operation rather than hiding it under generic
  backend code. Exact Unicode repertoire remains partially backend-defined.
* **Stable dedup:** retain K13 first occurrence/equality semantics. A general fold
  could derive it, but adding an unimplemented fold to lower the count is unjustified.
* **Pipeline:** ordered function composition plus validation/outcome barriers;
  `map_elements` is K12 finite pointwise traversal. Operation order is semantic.
* **RAW/TRANSFORMED/PERSISTED:** bound observation points. RAW is decoded supplied
  value before transforms, TRANSFORMED the current pipeline point, PERSISTED the
  final candidate **before** commit. PERSISTED is not after-write rollback.
* **Validation stage:** observation binding + type/predicate + declared failure.
  No transformation may follow a PERSISTED observation. Append pipelines observe
  incoming elements, not a fictitious final collection. Final type validation
  still checks the actual candidate collection.

The model is general transformation/observation composition, with a bounded
catalog of explicitly defined operations. The catalog cannot be replaced by an
opaque “transformation” primitive whose meaning comes from Python method names.

## 8. Mutation, lifecycle and persistence audit

| Construct | Classification / reason |
| --- | --- |
| Scalar and whole-collection replace | One typed replacement relation under K14; target type changes, not effect category. |
| Append | Ordered occurrence insertion composed with typed update/commit; duplicate preservation observable. |
| Add-unique | Membership/equality pretest + append-if-absent; prior occurrences/order preserved, not dedup of old values. |
| Atomic multi-field update | Composition of separately authorized changes under K22; single-record scope is currently bounded. Must preserve all-or-unchanged even if the second change rejects. |
| Lifecycle transition | Predicate(source state) + authorized state-field mutation + invariant + atomic outcome/effect; explicit `performs`/machine/trigger association protects field authority. |
| Persistence | K21 durable state, distinct from pure state relation. JSON/path/envelope/tempfile are backend/interface choices. |
| Atomic commit | K22 observable effect guarantee; temporary file + `os.replace` is its bounded implementation, not a portable durability theorem. |
| Migration / additive field introduction | Typed before/after schema relation + presence/literal/default + frame preservation + explicit version boundary + durable atomic commit. No creation-default authority may invent migration values. |
| Reload | Observation of K21 under record validation; no separate kernel primitive. |
| Unchanged-state rejection | K17 conditional outcome + K14 state equality + K22 failure frame. Semantic equality alone does not prove unchanged bytes/no attempted writes. |

Lifecycle meaning is compositional but its **authorization boundary is not
discardable**. An ordinary mutable write cannot assign lifecycle or identity
fields. Transition source/target/trigger/guard must agree and be checked before
generation. Predicate reuse grants neither transition permission nor write access.
State-machine enumeration is a profile of typed states and permitted effects;
current independent single-transition fields are not arbitrary workflow execution.

Persistence has both semantic obligations and backend guarantees. Durable contents,
explicit migration, failure outcome and observable preservation belong to the
contract. Concurrency isolation, fsync/crash recovery and multi-store transactions
are **not** implied by current single-file atomic replacement. Return-after-commit
does not guarantee output transport succeeds: the documented Windows Unicode
stdout failure can occur after persistence.

## 9. Query and resource audit

**CollectionQuery is COMPOSITION**, not a new irreducible query primitive:

`typed source + bound operands + predicate + exact selection + ordered result
+ input validation/preconditions + result policy + authorized read-only frame`.

K10 selection and K16 ordering remain individually defined. Result multiplicity,
inclusion, key precedence/direction/ties, no-match outcome and full-state validation
before selection are not hidden by this decomposition. Query input preconditions
operate before state read/selection in the normal interface, whereas selection
operates on records; neither is silently substituted for the other.

Tradeoff: one CollectionQuery node is a useful validated composition boundary for
AI manipulation, coverage and lowering. Counting it additionally as core would
double-count its facet behavior. Removing the composition interface merely to
reduce vocabulary would duplicate facet specification at every application site.

**Clock and UUID are typed instances of K20 resource/capability**, not two new
kernel operations. Their output contracts differ: UTC instant versus fresh UUID v4
identity with collision rejection. Resource access, returned value type and sampling
policy are separately authorized. Once-per-query sampling and shared-alias caching
are observable policies. Deterministic providers bind declared capability IDs;
ambient time or arbitrary callables in semantic source are not authorized.
Storage read/write are scoped capabilities too. A future external capability
requires a defined interface/effect contract; a declaration alone cannot supply
event ordering, durable delivery or distributed atomicity.

## 10. Cross-layer map: one meaning, multiple representations

Paths beginning `lp/`, `lw/`, `lq/` mean `src/lykoi_pipeline/`,
`src/lykoi_workspace/`, `src/lykoi_query/`.

| Single conceptual behavior | FRC representation | Structural projection / V1 | Compiler IR / execution | Semantic level |
| --- | --- | --- | --- | --- |
| Typed collection | `crud` mutable `collections` facet from `lw/mutable_schema.py` | Collection/value type facets, full facts in `LykoiContractV1` | `value_collection`, `mutable_values.py`, list-valued runtime | CORE K01/K03, policies not extra cores |
| Bound/literal/default creation value | `creation` bindings and collection source | CreationValueSource, full `facts` | Assignment input/literal/input_default/resource source; copied values | K04/K05/K19 composition |
| Typed condition | `filter_order` query predicate or `predicate_semantics` tree | Full typed tree and source-origin facts; faithful V1 | `predicates.py` → common `predicate_eval` | COMPOSITION over K06–09/K16/K19 |
| Query selection/order/result/frame | Eight CollectionQuery facet obligations | CollectionQuery facets; standalone `CollectionQueryDocumentV1` or normal V1 | Query document, `collection_query.py`, `collection_query_runtime.py` | One composition, not FRC+facet+V1+runtime four semantics |
| Staged transformation/validation | Mutable pipelines / `input_contracts` conditions | TransformationPipeline, ValidationStage, InputPresence | `mutable_pipeline`, explicit stage environment | COMPOSITION |
| Atomic typed write | `mutations`, changes/guards/effect | ValueMutation, CollectionMutation, AtomicWriteEffect | Private candidate + whole-state validation + single `write_state` | K14/K17/K22 composition |
| Lifecycle | Scalar `lifecycle` facet / legacy machine/transition IDs | Typed lifecycle facts / same V1 envelope | v0.3 `state_machines`, `transitions`, `performs`, source recheck | COMPOSITION with protected write authority |
| Durable additive migration | Scalar `storage` / `evolution`, collection/boolean migration values | Storage/evolution facts retained | Adjacent migration steps / `runtime_template.py:migrate` | COMPOSITION K19/K21/K22 |
| Resource authority/binding | Creation resource bindings, query `resources` | Complete capability IDs/types/sampling facts | `requires`/effects/capabilities; provider adapter/query sample cache | CORE K20 with typed instances |
| Input/error boundary | SemanticParameters, ExternalBinding, MissingInputBehavior | Full input facts / normal V1 | Input/query CLI dispatcher, explicit application vs CLI rejection | PROFILE transport + K17/K19 behavior |

`lp/scalar_profile.py`, `mutable_profile.py`, `query_profile.py` project/recompute
facts and coverage. `lq/contracts.py` recovers faithful normal documents;
`ac/profiles.py` validates/recomposes/dispatches. These mechanisms are not new
application semantics. BDI decision nodes describe material choices; adequacy
checks their authority. Counting each analysis decision as a kernel primitive
would confuse verification vocabulary with software behavior.

## 11. Duplication / conceptual consolidation opportunities

| Duplicate surface | Present evidence | Prospective consolidation / protected difference |
| --- | --- | --- |
| Query predicate vs mutation/lifecycle guard vs local validation `when` | R5.106 already shares `predicate_runtime.py` | Document one typed condition family; keep operand scope, evaluation stage, lookup precedence and effects explicit. |
| Legacy `field_equals`/`filter.kind=all`, query `equals`/`contains`/inclusion vs typed compare/member/AND | `legacy_predicate` normalizes query forms; `runtime_template.py:select_records` remains separate | Conceptual canonical relations; preserve historical interpretation and policy, do not rewrite pins. |
| Legacy `NOT_EMPTY`, `nonblank_input`, mutable/query `nonblank`/`nonempty` | Runtime implementations show `NOT_EMPTY` uses strip/nonblank, whereas mutable nonempty uses length/truthiness | Align definitions before naming consolidation; they are **not all equivalent**, particularly whitespace. |
| Scalar creation input IDs, mutable parameter names, query parameters | `input_values.py`, `profile_runtime.py`, schemas | One semantic parameter identity/binding model; query and legacy adapters have different current envelopes. |
| Query ordering vs legacy `order_by` vs L43 ordering relation | Typed query parses time keys; legacy `sorted_records` compares stored text | Shared conceptual ordered-result policy only after resolving timestamp/tie differences. |
| Validation in query dispatcher, query executor, mutation final type and stored-state validation | `profile_runtime.py:27–33`, `collection_query_runtime.py:prepare_query`, mutable runtime | Shared validation vocabulary; do not collapse precondition, input validation, final-candidate check and complete-store invariant boundaries. |
| Boolean type checks, timestamp parsing, collection uniqueness | Predicate/query/mutable/legacy validators and runtimes | One value-domain specification eventually; exact bool/int exclusion and storage-vs-instant equality must survive. |
| Missing default, creation default, additive migration default | Legacy assignments, input sources, migration relations | Share presence/binding concepts, retain separate triggering boundaries and authority. |
| `ApplicationError`, `Failure`, `MissingExternalInput`, broad ValueError handling | Query/profile/mutable dispatch | Outcome mapping specification; incidental Python exception classes are not independent language primitives. |

Duplication is significant in interfaces and validators; it is less severe in
the new predicate evaluator. Do not assume similar spellings are semantically
identical, and do not merge contexts merely because they call the same interpreter.

## 12. Backend-leak audit

Static source/spec audit; no new runtime probes or portability repairs. Classify
the **specified behavior and its boundary**, not every implementation function.

| Behavior | Classification | Evidence / boundary |
| --- | --- | --- |
| Collection insertion/occurrence ordering, stable-first dedup | LYKOI_DEFINED | Mutable spec explicitly preserves first occurrences/order. `mutable_unique` walks values in order. Python list/dict implementation is not its meaning. Historical `dict.fromkeys` realizes the same explicit rule. |
| AND/OR evaluation and purity | LYKOI_DEFINED | R5.106 all children evaluate, no effects; runtime materializes child values. Legacy fixture short-circuit is not normal effect authority. |
| Mapping presence vs empty/null | LYKOI_DEFINED | Specs define membership; runtime uses `name in inputs`, not truthiness for presence. |
| Duplicate rejection and exact stored collection equality | LYKOI_DEFINED | Allow vs unique, representation-exact timestamp collection equality explicitly defined; no silent dedup or temporal normalization. |
| Dictionary/object member order | PARTIAL | Semantic field sets/IDs do not assign object iteration meaning; legacy persistence sorts JSON keys, query output preserves construction order. If public byte/key order matters, adapters need a declared specification. It is not a general record-order core. |
| Exact string equality | LYKOI_DEFINED | R5.98 sensitive/none is Unicode-codepoint equality, no normalization. Validated types avoid Python bool/int equality leakage. |
| String/identifier ordering | PARTIAL | Key precedence/direction/tie-break explicit; Python scalar `<`/sort supplies detailed string collation. No comprehensive independent collation/domain spec covers all paths. |
| Unicode trim/nonblank/casefold repertoire | PARTIAL | Operation intent/order explicit; mutable spec explicitly uses bounded backend Unicode whitespace. `.strip()`, `.isspace()`, `.casefold()` depend on Python Unicode database/version; normalization version and exceptional codepoints not independently fixed. |
| Null vs missing representation | LYKOI_DEFINED | Bounded nullable timestamp values and mapping absence distinct, null-false atoms specified. `None` is a backend representation, not a leak by itself. General nullability is unsupported. |
| Integer extent / integer type | PARTIAL | Cardinality is mathematical nonnegative size, booleans excluded; read-only query integers exact Python int. Range limits, JSON large-integer interoperability and arithmetic overflow policy are not a general normal-language contract. No normal integer writes/arithmetic. |
| UTC timestamp lexical acceptance | BACKEND_LEAK | `utc_timestamp`, predicate/query validators delegate accepted grammar to `datetime.fromisoformat` after Z replacement. Z/UTC intent is defined, full accepted date/time grammar and precision limits are not independently specified. |
| Parsed instant equality/comparison | PARTIAL | UTC instant interpretation and inclusive/exclusive boundaries explicit. Python datetime resolution/range/parsing determine edge behavior. `fromisoformat` does not define a portable arbitrary-precision instant domain. |
| Legacy timestamp listing order vs typed query timestamp order | PARTIAL | Legacy `sorted_records` uses raw strings, typed query uses parsed datetime. L43 historical generative ordering also evolved separately. Equivalent instants with different spellings can expose different tie/order behavior; do not claim one uniform timestamp ordering. |
| UUID/clock authority and deterministic injection | LYKOI_DEFINED | Typed declared capabilities, v4 validation, collision rejection and once-per-query sample are explicit; randomness/clock source are provider implementations. |
| Unknown/malformed CLI syntax and parser diagnostics | BACKEND_LEAK | General argparse prose/handling remains adapter-dependent. Explicit R5.105 missing-flag rejection has a versioned diagnostic; that specified branch is LYKOI_DEFINED. |
| Declared application errors / precedence | PARTIAL | Error identities, lookup-first mutation guards, query input/precondition order specified. Broad `(OSError, ValueError)` → invalid_state in query/profile dispatch and uncaught exceptional paths depend on backend exception categorization. |
| Atomic write / rejection | PARTIAL | Single-record candidate validation and supported failure preservation explicit. `os.replace`, temporary-file cleanup, OS failure modes, crashes and concurrent lost updates are not general transaction semantics. Cleanup can raise a secondary backend exception. |
| Serialization / duplicate JSON object keys | PARTIAL | Shapes/types/envelope versions explicit, UTF-8 persistence declared. Python `json.load` chooses duplicate-key handling; round-trip numeric/text details and arbitrary decoder extensions are not fully independent language rules. |
| Unicode stdout and post-commit output failure | BACKEND_LEAK | R5.102 recorded Unicode encoding failure after persistence; current emitters use `ensure_ascii=False`/ambient stdout encoding. Successful semantic commit is not atomic with terminal output. |

These findings warrant future definition work, not broad new infrastructure.
Preserve historical results. Backend differences do not erase the strong defined
semantics for occurrence order, presence, null policy and typed effect boundaries.

## 13. Leverage and stability assessment

Leverage for **every proposed core** is in sections 3–4. The major reusable
compositions have these demonstrated interactions:

| Composition | Qualitative leverage | Demonstrated evidence / limit |
| --- | --- | --- |
| Predicate tree / range / exclusion | Very high | Four predicate domains + four interface domains; query/guard/invariant/staged-validation sharing. B09/B11/B12/B13 depend on complete interfaces, not merely represented trees. |
| CollectionQuery / ordered result | Very high | Six R5.98 compositions; R5.99 fourteen successful normal captures; same-state reads with mutable/scalar writes; selected B03–B13 reads. No joins/aggregates. |
| Mutation pipeline / element map / validation | High | Four mutable domains (96 published invocations), four input domains (132); B02/B06/B07/B10. Counts are round-local, not unique independent domains summed across rounds. |
| Append / add-unique / typed replacement | High | Four mutable domains, then four interface domains; B07/B08/B10. Add-unique standalone exposed-case coverage is thinner than replacement/append. |
| Atomic multi-field update | High | Second-change rejection/type/commit failure and reload tests; four mutable domains. B18/B19 cross-record atomicity is not covered. |
| Lifecycle / guarded operation | High | Canonical transition plus independent fields; mutable field preservation, B11/B13 and four predicate/interface domains. No arbitrary state-machine execution. |
| Migration / additive schema evolution / reload | High | Scalar/collection/boolean defaults, preserved IDs and unrelated fields, B01/B02/B07/B08/B10. No cross-entity migration proof. |
| Defaults / conditional value-source binding | High | Scalar/mutable/input domains, omitted-vs-empty contrasts B01/B06/B07. Different default boundaries deliberately not conflated. |
| Query amendment / literal-write interface | High | Four R5.107 domains (84 published invocations) and five newly successful cases. Exact-base preservation prevents implicit overwrite. |
| Query preconditions / declared error context | High | R5.107 four domains; B09 empty/type/window distinctions, read-only rejection. |
| Controlled resource sampling / binding | High | Creation collision/type/refusal/reset, injected-clock subprocess, B12 boundary tests. Does not prove arbitrary external effects. |
| Universal related-state condition / graph integrity | Insufficient evidence | Prototype witnesses only; not qualified normal compositions. |

**CONVERGING, in the present bounded domains.** Most recent growth closes
representation, binding, authority and interaction seams rather than inventing
task-specific semantic atoms. Primitive catalogs remain bounded; comparison,
presence, collection and state/effect structures recur in several domains.

Counterpressure remains real: several profiles require full facet restatements;
legacy and normal IRs coexist; text/time meaning leaks into Python; explicit
per-operator cases can accrete into a conventional language. Small counted core
alone would be a misleading success metric if opaque profile/backend behavior
carried the missing semantics. The proposed accounting keeps trim, dedup, ordering,
atomicity and resources visible instead of hiding them in generic labels.

### What R5.107's 8 → 13 says

R5.106 supplied represented predicate/boolean components but did not advance a
case's terminal stage. R5.107 closed literal writes/listing precursors (B08),
query error/precondition interfaces (B09), delete/terminal guard interactions
(B11/B13), and clock binding/preserved selection (B12). Five successes arose from
existing families composed through a faithful complete path, with final generic
lock 3 preceding all outcomes. This is strong **bounded compositional leverage**
and evidence that a structural/interface gap can dominate usable expressiveness.
It is not held-out generalization, cumulative B01–B13 achievement, or proof that
the kernel covers other software domains. No token-efficiency experiment ran.

## 14. Remaining exposed demands / hypotheses

Sources are the exact frozen `benchmark/requirements/B14.md` through `B20.md`
and R5.107 terminal records/matrix. Classification concerns proposed kernel
sufficiency, not present compiler support or a detailed implementation design.

| Demand / case | Kernel mapping | Assessment |
| --- | --- | --- |
| Persistent reference existence, duplicate/self rejection, referenced deletion (B14) | Identity under K01/K06, K03, K09 selection, predicates, K14/K17/K20/K21/K22 | **Existing kernel composition appears sufficient** for direct reference/integrity constraints, but current record-local environments cannot bind related records. General finite scope must be qualified. |
| Cycle rejection (B14) | Finite edges/identity plus transitive reachability | **Likely new core primitive required** relative to the 22 proposed current concepts: bounded reachability/closure authority is absent. Historical L20 explored it; not a brand-new idea and not implemented normal support. Do not invent a domain-specific cycle primitive before testing decomposition. |
| Every referenced task complete, with archive distinction (B15) | Related-record binding, predicate and finite universal reduction | **Cannot determine until implementation research.** L17 universal checking is experimental; finite map alone has no general Boolean reduction. May require admitting/refining quantification, not another lifecycle primitive. |
| Users, required owner existence and multi-entity migration (B16) | Typed record collections, selection/existence, defaults, invariant/effect/durability | **Existing kernel composition appears sufficient** at conceptual level for existence/multiple entities. Qualified cross-state binding and commit scope are absent; no arbitrary cross-store atomicity assumed. |
| Old-user migration role (B17) | Enum/default/migration and guard authority | **Cannot determine until requirement clarification**; ambiguity is not a semantic primitive gap. |
| Audit sequence/history and coupled task mutation (B18) | Typed record sequence, ID/time resources, K14/K17/K21/K22, ordered effects | **Cannot determine until implementation research.** Missing normal effect scope/order and monotonic counter computation; new event core is not proved necessary. |
| Atomic completion + exactly one successor (B19) | Authorized lifecycle, typed record construction/copy, ID/time resource, broader K22 scope | **Existing kernel composition appears sufficient** for state-effect shape; current single-record atomic implementation cannot execute it. Commit scope extension needs verification. |
| N UTC calendar days and positive nullable integer recurrence (B19) | Integer domain/validation, typed time and value computation | **Likely new core primitive required** relative to the 22: typed arithmetic/time displacement. L26 seconds offset is experimental, not calendar-day semantics. General arbitrary expression language is not justified. |
| Ordered two audit entries for successor (B19) | B18 ordered-effect demand + successor commit | **Cannot determine until implementation research**, contingent on effect/sequence computation. |
| Unknown-member error (B20) | Lookup failure/outcome/relationship context | **Cannot determine until requirement clarification**; do not select an error to fit support. |

### Relationship hypothesis

Reference values themselves can be IDs. Existence and deletion integrity compose
predicate/selection with state/effect boundaries; persistence does not turn an ID
string into a reference guarantee automatically. A reusable **relationship
composition** must retain target identity/domain, validation boundary and authority.
B14's cycle constraint exposes a distinct reachability issue; B15 exposes quantified
related-state evaluation. These cannot be claimed solved by storage arrays or
record-local predicates. Thus B14–B16 probably need normal-family extensions,
potentially a small reachability/quantification core addition, not necessarily an
irreducible `Relationship` atom.

### Event/effect hypothesis

B18's actual source requires **durable internal audit history**, not network I/O
or subscription to an external event source. Its native halt is
`UNSUPPORTED_BDI_SCOPE / rule_for:external_effect`, an analysis taxonomy label;
that label does not prove an ontological external-event primitive is needed.
Atomic record mutation + audit-record append is plausibly a composed state effect
under a larger commit scope. Monotonic sequence allocation, failure consistency
and effect order are meaningful missing authority. Truly external delivery, retries
and irreversible effects would raise additional resource/effect semantics, but
are not invented as B18 requirements. Research must determine whether the current
effect abstraction can carry them without hiding behavior in adapters.

### Arithmetic hypothesis

B19 needs typed integer validation and calendar-day displacement of a due instant,
not merely another clock sample. Resources provide fresh IDs/time, not the computed
due date. A bounded typed computation algebra could express arithmetic/displacement
and copy/construction under an atomic effect composition. Whether a general
Expression semantic is warranted remains open; naming it without defining its
operators would conceal growth. Arithmetic bounds, nulls, calendar interpretation
and ordered audit sequence must be explicit. No recurrence-specific core or
implementation is proposed here.

## 15. Hierarchical semantic map

```text
CORE (22 proposed concepts; qualified normal coverage remains bounded)
  Value structure: K01 typed record/domain, K02 field projection,
                   K03 occurrence sequence, K04 binding, K05 literal
  Relations:      K06 equality, K07 AND, K08 NOT, K09 membership,
                   K10 selection, K16 strict order, K18 cardinality
  Computation:    K11 trim, K12 finite pointwise map, K13 stable-first dedup,
                   K15 instant interpretation
  State/effects:  K14 before/after state relation, K17 operation/outcome/effect,
                   K19 presence, K20 capability authority,
                   K21 durable state, K22 atomic commit
    -> COMPOSITIONS
       Predicate trees -> OR, ranges, exclusions, nonblank/null checks
       CollectionQuery -> source + condition + ordered result + read-only frame
       ValueMutation -> replace / append / add_unique + guard + atomic commit
       TransformationPipeline -> transformations + map + staged validation
       Lifecycle -> source predicate + authorized transition + invariant
       Migration -> presence/default + schema relation + preservation + commit
       Input contract -> typed binding + presence + declared rejection
       Resources -> typed clock/UUID/storage instances + sampling/binding policy
         -> PROFILES / INTERFACES
            v0.3 compatibility model
            CollectionQuery-0.1 / CollectionQueryDocumentV1
            collection-query-1 normal path / LykoiContractV1 / LykoiProgram-1
            existing-scalar-1 / existing-model-1 / existing-composed-1
            typed-mutable-values-1 / typed-input-values-1
            typed-predicates-1 / R5.107 predicate/value interfaces
              -> APPLICATION
                 Tasks: priority, tags, notes, archived, owner, pending/completed
                 Articles/contacts/products/profiles: typed values/pipelines
                 Accounts/documents/sessions: guards, listings, clocks, errors

UNRESOLVED (not integrated kernel count)
  finite universal scope / related-state quantification
  persistent graph composition / reachability / cycle integrity
  temporal displacement / arithmetic
  broader ordered atomic effects and multi-entity binding qualification

OUTSIDE LANGUAGE SEMANTICS
  approval controller, freeze/provenance, test fixtures, SOI review process,
  BDI/adequacy analysis machinery, runtime/tool/model qualification
```

Profiles intentionally constrain support. They must not be mistaken for semantic
atoms, and combining named profiles is not proof that their interactions are valid.
The actual model and typed facts remain the semantic source of truth; generated
Python is a disposable realization, not a canonical behavioral specification.

## 16. AI-native implications and recommendations

**Observed:** typed trees, exact value sources, stable IDs, explicit facets and
deterministic faithful projection give machines local, checkable edits. One condition
language reduces repeated behavior specification. Effects, resources, stages and
authority remain separable. Application field names do not select compiler behavior.

**Limits:** full facet restatement, embedded prior bases, multiple legacy/normal
representations and several type/validation implementations duplicate information.
Profile names can obscure whether a failure is a semantic gap or unsupported
interaction. Compactness and AI edit reliability have not been measured. Exact
authority/evidence repetition is sometimes necessary; semantic duplication and
provenance duplication are not the same problem.

Recommendations, **not implemented**:

1. Protect K01–K22 as the explicit proposed accounting, including low-leverage
   cardinality and stable dedup until a demonstrated, equally explicit reduction
   exists. Keep unresolved concepts outside supported-capability claims.
2. Explicitly document CollectionQuery, predicate trees, pipelines, lifecycle,
   migration, defaults, mutation operations and ordered result as compositions.
   Preserve stage, occurrence, null, rejection and authority obligations.
3. Consolidate conceptual conditions/operands/types/validation/binding vocabulary
   prospectively; retain different evaluation contexts and historical compatibility.
   Do not add human-friendly aliases or broaden syntax for readability.
4. Formalize Unicode operation repertoire/version, string ordering, timestamp
   grammar/precision/order, integer range/serialization, exceptional outcome mapping
   and supported commit/output boundaries. Preserve historical byte evidence.
5. **Persistent relationships/cross-entity integrity remains the recommended next
   major capability for R5.109**, if separately instructed. Investigate general
   identity/reference binding, finite related-state scope and reachability leverage;
   distinguish relationship composition from any necessary new core relation.
6. Avoid a benchmark-shaped `task_dependency`, `archive`, `audit_task` or
   `recurring_task` primitive. Any new arithmetic/quantifier/effect operator needs
   independent domain pressure and explicit semantics, not a backend escape hatch.
7. Keep the WHAT/HOW/verification split, faithful cross-layer projection, stable
   identities, pure conditions, scoped capabilities and atomic failure frames.
   An AI-friendly composition node should minimize repeated behavioral facts without
   discarding independently authorized constraints. No token experiments yet.

**Answer to the central question:** the recent evidence supports discovery of a
small bounded semantic algebra, rather than one new core per application feature.
It does not establish a complete general software algebra. The next stress point
is relational quantification/reachability and ordered multi-effect computation;
those should test this architecture, not justify silently recreating Python syntax.

**Stop after R5.108.** No relationships, event, arithmetic, production refactor or
infrastructure work is authorized by this document.
