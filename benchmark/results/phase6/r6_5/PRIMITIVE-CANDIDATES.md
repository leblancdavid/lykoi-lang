# R6.5 general-purpose primitive candidates

**Design proposals only.** No source schema, kernel amendment, runtime adapter,
lowerer or verifier is added. Candidate labels are research names, not accepted
construct IDs. Count 26 remains exact. Multiple candidates may ultimately merge
or be rejected; no proposed final kernel count is asserted.

## Semantic candidates and refinements

| Candidate / layer | Meaning and generality | Safety and failure constraints | Compatibility implications |
| --- | --- | --- | --- |
| S-PARSE — new semantic construct candidate | Deterministically interpret an immutable input sequence under a declared terminating grammar/encoding policy, returning declared typed rows plus consumed-input/source-span facts, or a specified failure. Same relation for configuration and delimited imports; structured archive manifest documents are a third use. Not a domain parser callback. | Start with a bounded nonrecursive subset; explicit input/output/depth/work limits, no actions/scripts/IO, no ambient locale, no implicit recovery/normalization. Specify ambiguity, quoting, trailing input and exact error precedence. Full grammar formalism and representation remain unresolved. | New prospective profile/operator meaning, validated grammar and typed result-binding obligations; retain legacy v0.3 rejection of unknown forms. No change to old parse errors/identities. Standard-library realization would not make this existing semantics. |
| S-CODEC — separately justified semantic candidate | Named lossless byte/text/archive encoding/decoding relation with explicit format/version, ordering and accepted variants. Compression/entry interpretation is not physical IO. Potential uses: document interchange, media/asset archives, data backups. Could overlap S-PARSE for text, but compression is not established as a grammar composition. | Bound expanded bytes/ratio/entry count/depth, reject malformed/duplicate/ambiguous entries per policy; no executable archive hooks. Specify canonical assembly separately from lossless decode; do not invent inverse round-trip for lossy metadata. | Separate format policy/version and failure identities. No wheel-specific codec assumed; ZIP as a reusable format would still need independent contract/justification. |
| S-DIGEST — semantic candidate if subject-authored | Explicit algorithm maps immutable bytes to a domain-tagged digest. Useful integrity/caching/deduplication across documents, archives and imports. Existing equality compares supplied digests; it does not derive them. Prefer verifier-owned hashing when subject computation is unnecessary. | Algorithm/version fixed; length/stream limits; collision resistance assumptions disclosed; hash is not signature, authentication or content validity. Snapshot bound before hashing to avoid substitution. | New observable operation if exposed to authored programs; verifier-only implementation does not amend language semantics. Old nominal IDs keep exact comparison/no normalization. |
| T-BYTES/T-HANDLE — type/profile refinement candidates, accounting unresolved | Byte sequences or opaque nominal resources with explicit immutable snapshot/generation, authority scope and resource kind. Finite sequences/nominal records may suffice for representation; live handle nonforgeability cannot follow from a transport string. Applies to every resource domain. | No implicit casts, path-to-capability conversion or manufactured live authority. Fixed byte domain/size; handle expiry/staleness/ownership must be explicit. Distinguish metadata reference from permission token. | New versioned profile type bindings/transport rules likely needed even if no new core construct. Determine refinement versus new semantic capability before adoption. |
| T-PUBLISH — K22 physical refinement hypothesis, class 4 | Stage a bounded complete tree privately and expose it through one declared publication boundary. Could realize existing atomic commit for a narrow resource domain, but not proven for arbitrary files/processes. Uses generated reports, static assets and export snapshots. | All validation before publication; exact supported filesystem/reader model, stale-source rejection, no multi-root effect, no claim of process rollback. Separate logical all-or-nothing, crash durability and cleanup/recovery. | Cannot change old one-store atomic promises. A new profile must state stronger/different failure assumptions; if independently observable guarantees exceed K22, account them as new semantics rather than an adapter. |

The necessary finding concerns the **new interpretation relation**, not the
necessity of these exact names or one construct per format. S-PARSE does not grant
unrestricted recursion, AST mutation, arithmetic or general byte manipulation.

## General runtime primitives (not new application algorithms)

| Candidate | Specified physical obligation / reuse | Constraints and compatibility |
| --- | --- | --- |
| R-ACCESS | Acquire immutable snapshots, read/copy/write explicitly supplied bytes, enumerate a bounded declared tree, release a temporary resource; K20 scoped authority and K21 durable resource realization | Resolve paths under an authorized root via enforced handle policy; prohibit escape/links unless explicitly supported; pin snapshot observation, maximum sizes, metadata treatment and failure classification. Current JSON capability validator remains unchanged. New adapter version and explicit binding required. |
| R-STAGE | Private staging and one-boundary publish/discard for a declared resource domain; candidate T-PUBLISH realization | No arbitrary multi-file transaction claim. Authorize destination and overwrite separately; bound disk use and cleanup; expose inability to guarantee atomic publish. Do not combine JSON-store commit and tree publication as one implicit transaction. |
| R-PROCESS | Invoke a declared executable identity with exact argument vector, environment allowlist, cwd/resource handles, termination budget and externally bounded effects | Contract semantics still class 4 pending audit. No shell strings, dynamic executable search or parser/installer-as-native loophole. Capture raw stdout/stderr/exit/timeout; block or classify missing containment. Executable business decisions remain attributed to external code. Prospective host adapter only. |
| R-ISOLATE | Enforce a specified filesystem/process/network effect boundary and discard environment afterward | Platform-specific enforcement, not an environment variable. Failure to establish isolation is infrastructure-unavailable before subject effects. No provider service required; backend availability is separately qualified. |

A codec library may implement S-CODEC once its semantic contract is admitted.
R-ACCESS must not silently decode formats or decide application content. These
are different layer responsibilities even if one library offers both operations.

## Deterministic lowering rules

- **L-BIND:** preserve declared grammar/codec identity, types, input snapshot,
  consumed-input policy, error identities and operation ordering into prospective
  IR. No inferred trimming, case folding, delimiter repair or format autodetection.
- **L-COMPOSE:** lower admitted decode → supplied typed facts → existing
  predicates/transforms → staged effects, with explicit dependencies and failures.
  Reuse K04/K17 binding and existing guard concepts; finite reference reachability
  is not a general scheduling algorithm. Dynamic row construction support remains
  an integration question, not an implemented path.
- **L-EFFECT:** bind exact authority, source/destination handles, snapshot and
  supported publish assumptions. Error precedence is explicit; external operations
  cannot be speculated or reordered as if pure computations.

These are new lowering rules only **after** semantics are settled. They may
generate library calls, but must reproduce a separately specified relation.
Deterministic code generation cannot make an external process deterministic.
New versioned dispatch/validation/recovery obligations preserve old profiles and
frozen serialized identities; no compiler work is authorized here.

## New verifier infrastructure

- **V-RESOURCE:** verifier-owned immutable input staging, independently read
  before/after trees, byte/digest observations, absence and unchanged-input controls.
  Bind expected artifact identity/path rules to the run; never use a producer PASS
  flag as evidence. Hashing here is measurement, not native authored S-DIGEST.
- **V-ENV:** record declared executable/backend/environment identities, isolation
  establishment, effect logs, raw errors and replay limits. An observer cannot
  restore or normalize an incorrect subject output before comparison.
- **V-CLASSIFY:** preserve parse rejection, semantic validation rejection,
  authority denial, resource failure, infrastructure unavailable, unobservable
  evidence and behavioral mismatch distinctly. Map only declared policies;
  inaccessible observations are not success or an invented semantic blocker.

All three are prospective verifier infrastructure, provider-independent and
versioned separately from subject semantics. Independent execution ownership
does not by itself establish cognitively independent expectations or formal proof.

## Rejected specialization

Reject `install_wheel`, `parse_pip_requirement`, `repair_space_url`,
`normalize_distribution_name`, `create_dist_info`, and `pip_success` as proposed
architectural primitives for this round: their justification here would solely
serve the triggering package workflow. No such primitive is proposed for adoption.
Dependency records, archives, text grammars, content identities and resource
publication have independent non-package uses, but that does not justify package
name/version/tag rules or package resolution as hidden parameters/callbacks.
