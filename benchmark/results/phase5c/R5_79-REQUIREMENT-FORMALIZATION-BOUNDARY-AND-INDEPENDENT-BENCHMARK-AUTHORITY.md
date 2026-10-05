# R5.79 — Requirement formalization boundary and independent benchmark authority

## Result and inherited gap

**`R5_79_REQUIREMENT_FORMALIZATION_BOUNDARY_QUALIFIED`**, within architecture and
methodology scope. Adopt the [versioned boundary](../../../docs/requirement-formalization-boundary-v1.md).
This qualifies a separation of responsibilities, not a production formalizer,
general requirements DSL, complete arbitrary-requirement V1 conversion or a new
held-out freeze. R5.79 stops here; Phase 5C remains paused.

R5.78 ended `R5_78_B03_PACKAGING_GAP` before B03 access. The historical frozen
source contains prose and regression fragments but no declared deterministic
complete application/configuration/identified-obligation conversion. Its generic
packager correctly rejected public B01 as `UNREPRESENTABLE_SOURCE`, rather than
inventing semantics. That observed gap remains; this architectural decision
defines who must supply the missing meaning prospectively.

## Architectural decision and terminology

`Human Requirement → Requirement Formalization → Formal Requirement Contract
→ Lykoi authoring → Lykoi Program / Semantic Representation → deterministic
validation and compilation/lowering → software`.

* **Human Requirement:** human-written request and permitted context, preserved
  as provenance. Parsing arbitrary prose is not a core language responsibility.
* **Requirement Formalization:** interpretation into precise behavioral intent,
  with ambiguity/conflict handling and independent approval.
* **Formal Requirement Contract (FRC):** versioned authoritative **WHAT**:
  required inputs/results/state/failures/invariants/observable effects and only
  behavior-material assumptions.
* **Lykoi Program / Semantic Representation:** implementation-side **HOW**,
  composed to satisfy the independent FRC.
* **Compilation/lowering:** deterministic transformation of a validated program,
  not interpretation or approval of intent.

Phase 5 begins from independently formalized behavioral authority. It isolates
semantic capability, composition, lowering/compiler and resulting behavior
(failure classes 3–6 in the request). Misinterpretation and incomplete
formalization remain upstream defects, classified separately when discovered.
Independence reduces confounding; it does not prove upstream perfection.

## Minimum contract, equivalence, ambiguity and provenance

The specification requires contract identity/revision/vocabulary, system and
public-boundary identity, relevant configuration and initial context, stable
obligation IDs, exact behavioral relations, and source/resolution/review lineage.
Inputs, outputs, state effects, failure behavior, invariants, side effects and
ordering are specified wherever material, not as mandatory empty boilerplate.

`REQ-001`-style identities are assigned independently of Lykoi support, preserved
through revisions with explicit lineage and retained by V1 normalization for
supplemental obligations. Every FRC obligation needs a projection coverage map,
including requirements represented in application/configuration rather than
supplemental readiness entries.

Behavioral equivalence concerns externally observable results and effects under
declared assumptions. Classes, internal field names and generated Python layout
are not prescribed unless those details are themselves externally required.
Structural hash equality is not a proof of normalized semantic equivalence.

Draft `AMBIGUOUS_REQUIREMENT` records identify source, question and affected IDs.
Only the original requester/independent owner can resolve material ambiguity;
unresolved issues block freeze. Cross-ID logical conflicts block approval as
`CONFLICTING_REQUIREMENTS`; this is independent review, not a newly implemented
general solver. V1 additionally rejects duplicate/same-ID conflicting entries.

Completeness review covers every material required observable behavior, failure,
invariant and assumption, checks consistency, and resolves evaluation ambiguity.
Keep source commitments and fragment → obligation mappings plus authority
resolutions in a committed provenance record. Metadata is excluded from normalized
behavioral identity, so provenance must remain available as a separate audit
artifact. Neither source hashes nor schema validity prove complete coverage.

Future acceptance chain: `REQ-ID → static support evidence → implementation
mapping → acceptance case(s) → observed behavior`. No full acceptance subsystem
is implemented here, and static support is not acceptance success.

## Independent formalization and human/AI roles

Human formalization is valid when independent of Lykoi development feedback.
An isolated AI formalizer is also architecturally valid if it cannot query support,
inspect development solutions, modify Lykoi or disclose protected content, and
its output is independently validated/approved. Neither may weaken obligations
or choose interpretations to improve support. Structural checks are permitted;
support inspection is prohibited during formalization.

Real-world workflow may use `human request → AI formalization → human review
and approval → frozen FRC → Lykoi`. For automated research an independent trusted
benchmark authority can approve instead. Approval evaluates intended behavior,
completeness and consistency, not merely whether another model agrees.

Lykoi remains **AI-native, not AI-dependent**. OpenAI, Anthropic, Gemini,
local/future models and humans can supply formalization/authorship. Provider/model
identity and credentials do not define contract meaning or core execution identity.
Authorship/fairness provenance may be recorded separately. A fixed approved
contract has the same meaning regardless of who produced it.

Separate future **Requirement Formalization Research** includes interpretation
reliability, review burden, cross-model behavioral agreement, ambiguity discovery,
completeness verification, interactive contracts and minimal change diffs. Exact
JSON identity between formalizers need not be required for equivalent behavior.

## Phase 5 authority and mapping to V1

The FRC is prospective authoritative behavior; original prose is provenance/context.
Its independently approved evaluation projection must faithfully supply existing
`application`, `configuration` and identified `obligations`. Package those explicit
components as exactly one behavioral `BenchmarkDocumentContractV1` document,
optionally with descriptive metadata. The existing deterministic adapter produces
`BehavioralContractV1` without prose interpretation or support-based choices.

The existing application format is semantic-facing and bounded. It may express
declarative required relations, but must not prescribe development implementation.
Projection review is therefore material. Unknown supplemental kinds are retained,
not dropped; unsupported static results remain possible. If a full required
relation cannot be expressed faithfully in this evaluation format, retain it in
the FRC and halt qualification with an evaluation representation gap. Do not
invent a complete conversion or infer a Lykoi capability defect from that alone.
This residual production qualification work does not prevent defining the
architecture, but prevents claiming packaging readiness.

Prospective trusted B03–B20 process: qualify on safe examples first; separately
authorize independent source access; formalize and resolve issues; review
completeness/consistency/projection; structurally map to V1; commit source/FRC/
provenance/map/review/package/inventory; seal protected contents; publish only
safe metadata/commitments. Separately committed acceptance material has separate
authority. Only a later one-time runner authorization can open a sealed static
package and observe it. Use existing `phase5_runner_v2`, `ACTUAL_HELD_OUT`,
one-time ledger and safe exclusion; no new authority stack is installed.

This process is **specified, not executed**. No blanket access to B03–B20 is
authorized; exposure history remains per-request. Formalization cannot restore
pristine status to an exposed request or amend historical frozen authority.

## Validation and evidence limits

[R5.79 validation](R5_79-VALIDATION.md) records all ten requested conditions with
invented calculation/ambiguity/conflict examples and scoped public component
mapping. It explicitly distinguishes conceptual formalization review from
executable interface behavior and identifies a negative unrepresentable case.

Executed from the repository root:

```powershell
python -B -S -m benchmark.evaluation.test_benchmark_documents_v1
git diff --check
```

V1 corroboration: **33/33 PASS, zero failures/errors, protected read attempts 0**.
The unchanged suite covers normalization, identity, round-trip, same-ID conflict,
metadata exclusion and synthetic/public static lifecycles. Fake protected resources
are temporary synthetic files. These results are not “33 formalizer tests,” nor a
new generality, completeness or production containment claim. No broad harness
discovery, actual held-out observation, compiler change or model change occurs.
Whitespace verification passes after the documentation changes.

## B02, B03 and semantic accounting

B02 remains **`B02_EXPOSED_IN_R5_75` / `B02_STATIC_RESULT_INDETERMINATE`**.
Its public historical callback failure illustrates why implicit document
interpretation inside observation is undesirable. No B02 prose, regression
fragments, captured documents or support outcome is used as design feedback.

B03 remains **`B03_PRISTINE` / `B03_NOT_EVALUATED` /
`B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT`**.

| Actual B03 activity in R5.79 | Count/status |
| --- | --- |
| Source reads / protected development read attempts | **0 / 0** |
| Formalization / packaging attempts | **0 / 0** |
| Authorizations / reservations / openings | **0 / 0 / 0** |
| Observations / static-consumer calls | **0 / 0** |
| Generation / execution / acceptance / repair | **0 / 0 / 0 / 0** |
| FRC / V1 package / package commitment | **Not created** |
| Runner eligibility | **Not claimed** |

These are scoped activity statements and inherited pristine status, not a
content/hash inspection of B03. No protected source is read to establish them.
Core semantics remain **30**; formalization is upstream, not semantic #31.

## Success criteria and next gate

All sixteen requested architecture criteria are covered by the versioned
specification: distinct human/formal requirements and transformations; Phase 5
formal authority; minimal behavior content; stable IDs; explicit ambiguity;
source provenance; implementation neutrality; independent human/AI formalization;
provider-independent meaning; deterministic explicit V1 projection; prospective
sealed process; pristine B03; no B02 design feedback; core 30.

Recommend the next **separately authorized formalizer/process qualification gate**
using synthetic human requirements, public B01 and additional non-held-out examples.
It must select/version the machine-readable behavioral vocabulary, independently
review coverage/consistency, reject unresolved ambiguities/conflicts, demonstrate
faithful full V1 projection without support-driven feedback, and qualify trusted
containment/review/commitments. No B03 formalization begins in that qualification.
Only after it passes should independent protected formalization/packaging be
considered; actual one-shot observation needs subsequent separate authorization.

Final classification: **`R5_79_REQUIREMENT_FORMALIZATION_BOUNDARY_QUALIFIED`**.
R5.79 stops. No next gate executes here.
