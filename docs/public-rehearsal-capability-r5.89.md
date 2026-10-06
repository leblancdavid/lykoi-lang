# Public rehearsal capability closure — R5.89

**Status: `R5_89_PUBLIC_REHEARSAL_BLOCKED_REAL_AI_QUALIFICATION`.**
The production-facing adapters and bounded calibration path are implemented. No
live model is configured or exercised. The public freeze is an inactive candidate,
and public-mode admission fails closed. This is not a completed public rehearsal.

## Capability profile established before adapter development

[PublicRehearsalCapabilityProfile-1](../rehearsal/public-capability-profile-1.json)
declares a deliberately small **task-creation observation slice**, derived from the
existing public model, compiler and R5.87/R5.88 title/default evidence. It is not
general entity management. The future rehearsal requirement has not been selected.

Supported contracts contain exactly:

1. One STATED `crud` relation with parameters
   `{"domain":"task creation","result":"supplied title"}`; or
2. That relation and exactly one STATED `priority_create` relation with parameters
   `{"condition":"priority omitted","result":"LOW"|"NORMAL"|"HIGH"}`.

IDs, exact statements, quotes and source/approval identities remain bound. No
material issues, domain annotations, context assumptions, implications or component
authority are admitted by these mappings. Qualification requires the human and
blind reviewer to judge that these structured clauses faithfully express the source;
the machine cannot prove an arbitrary statement equivalent to its relation.

The actual existing interface is `create --title TEXT --description TEXT`, with
optional `--priority`. Calibration uses valid nonblank titles and a supplied
description. Description, IDs, timestamps, lifecycle, additional commands and local
JSON persistence exist in the public compiler seed, but this profile makes **no
contractual guarantee** about them. It does not claim title-only CLI syntax, read,
update, deletion, ordering, filtering, cardinality, explicit-priority validation,
blank-input behavior, migrations, persistence, events, arbitrary fields or entities.
Any such additional normative requirement must halt, even if the compiler itself
has some of that capability. A narrow rehearsal envelope is not the whole language.

## Qualified complete mappings

[`mappings.REGISTRY`](../src/lykoi_rehearsal/mappings.py) contains two explicit whole-
contract mappings. Matching is exact, including parameter key sets, obligation
count, default condition and value. There is no partial-success or generic fallback.
Unknown/extra obligations return `UNREPRESENTABLE_SOURCE /
NO_QUALIFIED_COMPLETE_MAPPING`. In particular, the exact R5.87 wizard includes
filtering and ordering and retains its original halt before plan/grant/authoring.

Both mappings use the **unchanged** V1 envelope/normalizer and its existing generic
identified requirement dictionaries. The exact ID, structured relation and statement
are retained; recovery checks compare every atom and statement. The application
operations describe this observation slice. Required configuration/state containers
are declarative scope carriers; their empty shape is not a promise about physical
`tasks.json`, a source-selected complete component, or an independently discovered
baseline. No old supplemental-context recovery rule is broadened. This is a new
bounded adapter consuming existing V1, not qualification of every historical static
V1 consumer or a new V1/language semantic primitive.

Tests qualify both mappings locally: all three enum boundaries, title-only, exact
obligation/statement preservation, extra persistence/filter/order obligations,
cardinality/order/state/validation parameter mutations, changed default trigger,
unknown default, duplicate semantic clauses, context/domain changes and wrong
default implementation. Passing finite tests is not a universal equivalence proof.

## Real AI interfaces and source-only review

[`AIAdapter`](../src/lykoi_rehearsal/adapters.py) performs standard-library HTTPS
Chat Completions requests using a JSON-schema output envelope. Local recursive
schema checks precede native FRC/SOI/compiler validation. Model schema support is
requested with `strict: false` because normative relation parameter objects are
open structured JSON; malformed outputs still fail locally. Provider compatibility
has not been live-tested here.

The model receives a fixed role instruction and exactly one allowlisted input
request, with no tools or conversation history. Receipts bind adapter version,
configured provider/model, returned model/response ID when supplied, fresh session,
instruction/schema/configuration identities, exact input/source/policy-evidence
identities and output identity. Evidence remains `UNTRUSTED_CANDIDATE`. The designated
credential is read from `LYKOI_REHEARSAL_API_KEY` in the trusted service only and is
never persisted. Provider error bodies are not recorded. No secret is in the repo.

Formalizer and reviewer implement the existing R5.87 Producer interface:

```python
formalizer = AIAdapter("formalizer", configurations()["roles"]["formalizer"])
reviewer = AIAdapter("reviewer", configurations()["roles"]["reviewer"])
candidate = workspace.formalize(formalizer)
inventory = workspace.commit_inventory(reviewer)
coverage = workspace.reconcile(inventory)
# The human reviews approval_summary(candidate), then explicitly approves it.
workspace.approve(owner_credential, candidate)
what_seal = workspace.seal(candidate)
```

The reviewer receives source, authorized clarification and policies, never candidate
clauses. Its source commitment is calculated solely from the supplied source record.
R5.87 validates exact spans, source commitment, evidence references and accounting;
the controller commits SOI before REVIEW_STARTED/reconciliation candidate exposure.
Formalizer and reviewer have different session IDs and independent stateless remote
request contexts. There is **no demonstrated distinct-model/provider independence**.
No model vote confers authority. Ambiguity, omissions, inventions and disagreement
remain human clarification/approval boundaries, with the existing finite review limit.

## Author and verifier

[`RehearsalController` / `RehearsalPipeline`](../src/lykoi_rehearsal/service.py)
prospectively extend the R5.88 classes without editing them. Native V1 validation
recomputes the new closed mappings. Existing structural/coverage, BDI, adequacy,
grant, reservation, deterministic target binding and verification authority remain.
Public admission additionally requires eligible infrastructure and live attributed
formalizer/reviewer evidence for the exact WHAT source. Calibration mode is explicit
and labeled; it can exercise mock transports but cannot claim frozen public admission.

The AI author receives exactly the R5.88 bundle keys: `version`, `run`, normalized
`v1`, minimal `toolchain`, and frozen public seed in `fixture`. `public_author_seed()`
derives that seed from the existing model with scenario expected results removed.
It is toolchain context, not a precomputed response to the future requirement.
Hidden plan cases/results, private verifier material, rejected interpretations and
future answers are absent. Input, output, configuration and instruction identities
are checked when native model evidence is registered. Unsupported/malformed language
halts `AUTHOR_CAPABILITY_FAILURE`; the unchanged compiler is not repaired.

Verification's default production path is a **WHAT-side deterministic rule producer**,
not an exact-FRC fixture registry. It derives executable title/default observations
from the two supported patterns for arbitrary IDs and statements. Candidate AI plan
production is also separately invocable; coverage is reviewed before controller plan
sealing. An optional preapproved AI-plan registry is calibration-only for this freeze;
public eligibility selects the fixed deterministic producer, with no plan lookup
registry. Authors cannot produce/review/seal acceptance authority. Seal precedes the
author bundle and single-use reservation.

### Observation envelope

Actual pass/fail uses fresh external command processes, exit status, supplied-title
stdout substring, and omitted-priority stdout enum. Stderr is captured for diagnosis
and containment attribution. File observations are refused by this profile, despite
the broader R5.88 harness's optional file support. No exact formatting, internal
state, exhaustive domain proof or arbitrary side-effect absence is verified.
Executable claim observations, case identity and obligation/case traceability are
required; a mere `EXERCISED` label is insufficient. Unobservable obligations halt
before implementation grant. Finite observation adequacy still needs independent
review; no claim is made that substring matching proves full output semantics.

## Enforced containment and investigation

- Isolated CPython `-I -S`, fixed worker, source on stdin; separate process per command.
- Fresh temporary case working directory, empty child environment, no service keys.
- Python audit guard restricts file APIs to case read/write and interpreter-runtime
  read-only scope; it denies socket, subprocess and ctypes APIs and out-of-scope
  filesystem mutation. Out-of-scope file, socket and process probes actually reject.
- Ten-second execution timeout; file-backed output capture, one-million-byte returned
  output limit. On Windows the capture limit is checked after process completion;
  it is not a disk quota.
- POSIX worker implements CPU 8 s, file 2 MB and address-space 512 MB limits. These
  limits were **not exercised on Windows**. No Windows job object, restricted token,
  OS filesystem ACL sandbox or OS network firewall is implemented.
- Only deterministic registered compiler targets are dispatched by the service.
  Role/bundle interfaces keep author and verifier inputs separate. Administrators,
  controller database and interpreter remain trusted.

This is **trusted generated local program containment**, not hostile-code safety.
Python audit hooks are bypassable by hostile/native code and are not OS enforcement.
The lack of robust OS sandboxing does not independently block this expressly trusted
compiler-generated public profile; hostile-code rehearsal would require a separate
scope and qualification. Remote model HTTPS transport legitimately uses the network;
the generated-target worker has no allowed network behavior.

## Executable freeze, invocation and eligibility

[R5.89-PUBLIC-CANDIDATE-1](../benchmark/results/phase5c/r5_89/public-freeze-candidate.json)
binds physical bytes of ordinary transitive implementation modules, schemas, compiler,
specification, workspace/pipeline/controller, profile, mappings, adapters/worker,
prompts/output schemas, role configurations, qualification record, public model seed,
calibration tests/corpus and reproduction driver. It also binds the interpreter and
available embeddable runtime libraries. The inherited per-run manifest binds exact
WHAT, analyses, plan seal, component freeze and grant after plan preparation.
Content integrity is machine-verifiable; the hash is not self-issued activation
authority. This is not a fully hermetic OS or provider-weights snapshot.

With a normal Python 3.10+ installation and `PYTHONPATH=src`:

```powershell
python rehearsal/qualify.py
python -m lykoi_rehearsal.freeze check
python -m lykoi_rehearsal.invoke formalizer   # allowlisted public request JSON on stdin
python -m lykoi_rehearsal.invoke reviewer     # separate source-only request on stdin
python -m lykoi_rehearsal.invoke author       # controller-released author bundle only
python -m lykoi_rehearsal.invoke verifier     # WHAT/WHAT-seal/profile identity only
```

For this checkout's existing embedded interpreter, prepend repository and `src`
to `sys.path`, then use `runpy` as recorded in the engineering report. Single-role
invocation produces candidates/receipts, never approval or controller grants. For
end-to-end invocation, use the Workspace calls above, a service-owned
`RehearsalController(..., model_configurations=configurations(),
author_seed=public_author_seed())`, and an `AIAdapter("author", ...)` passed to
`RehearsalPipeline`. `mode="CALIBRATION"` is mandatory for development dry runs;
reviews and owner approval remain explicit service/human actions. Then call
`prepare(what_seal, run_id, review_rationale=...)` and `execute(prepared)`.

Eligibility accepts **infrastructure only**, with no future-requirement parameter.
It checks exact freeze drift, public activation identity/purpose, configured roles,
designated credential availability, approved multiple live calibration receipts,
controller components/configuration/role separation, exact public seed, empty public
plan registry and containment profile. Default public service mode rejects before
WHAT consumption when infrastructure is ineligible; author and verification dispatch
recheck it. An activation record alone cannot override missing qualification.

### Remaining activation work

Before a requirement is selected: provision actual role models and the service key;
exercise at least two live public development calibration runs; preserve receipts,
failures, source-only ordering and exact controller/acceptance evidence; independently
review and human-approve their qualification record; bind that configuration/evidence
in a separately authorized new public freeze and healthy controller; activate only
that public candidate. The capability profile must not be changed around the future
requirement. Today's null-model candidate cannot accept a genuinely new requirement
as a frozen rehearsal without this pre-requirement configuration/qualification step.

**Stop after R5.89.** Requirements recovery remains an unimplemented provenance
extension to sealed authority. B03 remains pristine/unread/unevaluated/unexposed,
all counters zero; `R5.83-CANDIDATE-1` remains unactivated.
