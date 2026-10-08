# R6.5 existing-kernel expressibility matrix

## Classification and evidence key

**1** existing semantics; **2** general physical lowering/runtime realization of
an existing specified meaning (candidate, not implemented support); **3** new
observable semantic capability under the current admitted meanings; **4** undetermined.
Primary classes apply to the stated general scope; qualified reuse is separately
listed. “Supported” refers to today's normal subject path, not host Python tools.

Evidence anchors (paths relative to repository root):

- **E1** `benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json:4–79`:
  exact 26 accounting, no additions or minimality proof.
- **E2** `docs/typed-mutable-values-v1.md:9–56,108–126`:
  bounded value shapes, admitted transforms and single-record JSON persistence.
- **E3** `docs/persistent-references-v1.md:36–89,110–150`:
  nominal references, integrity/extent composition, finite reachability;
  pointwise map has no worklist/fixpoint or newly defined transformation body.
- **E4** `docs/typed-computation-v1.md:13–24,56–84`:
  arithmetic is not hidden in map; at most 16 pure graph nodes, no loops,
  recursion, arbitrary expressions or dispatch.
- **E5** `docs/axiom-v0.3.md:26–54` and
  `src/air_compiler/validator.py:134–156`: scoped JSON-file read/write, clock,
  UUID; authority validation is not OS containment or arbitrary callback support.
- **E6** `docs/prewrite-conditional-composition-v1.md:19–34,45–84,86–135`:
  permission checks, trusted host assertion limits, coherent images and bounded
  dependent creations. No authenticated principal or distributed atomicity inferred.
- **E7** `src/air_compiler/profiles.py:40–96,135–170`:
  closed normal author/generator dispatch and fixed runtime composition.
- **E8** `src/lykoi_pipeline/pipeline.py:20–107`: verifier-owned CLI/host execution,
  exact/JSON observations, byte preservation, fixed host Python/env/timeout;
  explicitly not an OS sandbox.
- **E9** `benchmark/results/phase6/r6_4/CAPABILITY-INVENTORY.md:9–40,62–76`:
  prior static gaps and explicit distinction from abstract-kernel impossibility.

These anchors are preservation-bound in [verification](VERIFICATION.md). Reading
static code is not running it. Existing profile limitations are not assumed to
be global mathematical impossibility results.

## A. Structured parsing

| ID / capability | Class | Existing reuse and specific reasoning | Current lowering support / remaining boundary |
| --- | --- | --- | --- |
| A1 text and binary inputs | 3 | Text retention/presence is 1 via K04/K19 (E2). Arbitrary binary-to-value interpretation needs a byte domain/codec relation not supplied by trim, equals or addition (E1/E4). Physical acquisition alone is 2, see D1. | Text inputs supported in declared forms. No authored general byte/decoder path (E5/E7). Byte-as-integer representation alone does not define decoding. |
| A2 tokenization and decoding | 3 | K12 applies an admitted body; it does not split an unknown string into tokens or assign encoding meaning. No scan/slice/character-class stateful interpretation is admitted (E2/E4). Finite literal lookup covers only its declared catalogue. | No normal tokenizer/codec. New S-PARSE/codec semantics before backend library binding. |
| A3 structured representations | 1 | For already decoded bounded flat records and finite nominal relationships, K01–K10/K18/K23 compose structure (E1/E3). This claim excludes arbitrary recursive trees and dynamically heterogeneous node types. | Flat typed record/reference profiles supported; grammar-output binding and arbitrary recursive AST are not (E7). General AST adequacy is 4. |
| A4 grammar-driven parsing | 3 | A supplied grammar determines a new acceptance/result relation; no existing operation consumes one. K23 searches supplied reference edges, not input-derived parse edges (E3/E4). Constructing those edges externally hides interpretation. | No grammar interpreter/profile/lowering. Terminating grammar subset and result binding proposed, not defined by K17. |
| A5 deterministic parse failures | 3 | Existing declared validation errors/ordered stages are 1 (E2/E6); parse-specific offsets, expected-token relation and ambiguity/trailing-input policy require the interpretation's failure semantics. | Existing value/shape errors supported. No parser error model; runtime failure must not be mislabeled syntax rejection. |

## B. Typed artifacts

| ID / capability | Class | Existing reuse and specific reasoning | Current lowering support / remaining boundary |
| --- | --- | --- | --- |
| B1 files and directories | 2 | K20/K21 permit declared physical resource authority/durable realization (E5). A bounded immutable file/tree snapshot adapter is plausible without a new application algorithm; names, authority root and observable contract must be explicit. | Only JSON-store access accepted. General file/tree binding absent. This class does not license arbitrary path dereference or assumed atomic tree writes. |
| B2 archives and structured documents | 3 | Typed supplied manifests are 1; interpreting serialized documents or compressed archive entries adds codec/format relations (A2/A4). A file extension or record named Archive defines no decoding behavior (E2/E9). | Neither subject format codecs nor archive extraction/assembly. Physical copying separated in C2/D1. |
| B3 metadata and content identities | 3 | Supplied nominal metadata/exact identity comparison is 1 (E3). Deriving digest/size/format metadata from raw content is an independent relation; K06 compares values, not hashes bytes (E1/E4). Host verifier hashing is infrastructure (E8). | Nominal record identity supported; subject digest/inspection absent. Physical stable-resource identity adapter may be 2, but does not automatically justify authored hashing. |
| B4 typed resource references | 4 | Nominal references to metadata records are 1 (E3). Whether live opaque handles with scope, generation and nonforgeability are only K20 refinements needs an explicit contract; records cannot manufacture enforceable authority. | No general live handle profile; JSON resource names supported (E5). Candidate R-ACCESS must resolve stale/scope behavior first. |
| B5 resource lifecycle | 1 | Declared states/transitions, guards and durable metadata use K14/K17/K21 (E1/E6). Model created/staged/published/released states as existing enum meanings. | State lifecycle supported within profiles. Physical creation/release and crash cleanup need adapters; metadata transition is not evidence of actual deletion. |

## C. Resource transformations

| ID / capability | Class | Existing reuse and specific reasoning | Current lowering support / remaining boundary |
| --- | --- | --- | --- |
| C1 read and write | 2 | Realize explicit K20 read/write and K21 persistence using a bounded general physical adapter (E5). Contract must bind snapshot, content and failures. No silent content interpretation. | JSON record storage supported; byte file IO absent from accepted normal capabilities. |
| C2 extract and assemble | 3 | Projection of supplied finite entries is 1 (K10/K12). Archive decomposition/compression/serialization relations are new meanings, even if a library realizes them; writing specified entry bytes is separately 2. | No archive codec or authorized materialization path (E7/E9). Generic “extract” callback would hide both layers. |
| C3 validate and transform | 1 | On admitted decoded values: exact comparisons, predicates, selection, trim, stable uniqueness, bounded checked arithmetic and declared staged failures compose (E1–E4). | Qualified transformations supported. Arbitrary format conversion, compression or byte transduction is 3, not licensed by K12. Cross-profile arbitrary union not established. |
| C4 dependency relationships | 1 | Finite nominal edges, existence, cardinality and nonempty reachability express supplied dependencies/cycle checks (E3). | Reference profile supported. General topological scheduling, graph-derived output, constraint solving/version selection are not supplied by boolean reachability; those broader scopes are 4. |
| C5 transactional behavior | 4 | Qualified one-store candidate validation/replacement is 1 (K22, E2/E6). Arbitrary multi-file/process atomicity does not follow. Whole-tree staged one-root publication is a possible physical realization, pending failure/reader/crash contract. | Single-store frame supported. Multi-root commit, crash recovery, concurrent publication and process rollback absent; no proven class-2 lift. |

## D. External effects

| ID / capability | Class | Existing reuse and specific reasoning | Current lowering support / remaining boundary |
| --- | --- | --- | --- |
| D1 filesystem operations | 2 | Bounded read/write/create/remove with explicit K20 authority and K17 failure contracts can have general physical adapters. Restrict scope to declared resources; pathname equality is not containment (E5). | Only scoped JSON read/write subject capability. General filesystem/handle binding absent. Recursive operations and link policies require explicit limits. |
| D2 process execution | 4 | K20 can describe external authority, but does not specify a process contract: executable identity, argv bytes, env, cwd, termination and possible effects need meaning (E5/E8). An adapter-only design is plausible, not established. | Verifier runs processes; authored general process execution absent. Calling a parser executable is external delegation, not native A4 coverage. |
| D3 environment isolation | 2 | Enforcement of a declared effect boundary belongs to runtime/host infrastructure; no new pure value operation needed. It requires an externally defined isolation policy and failure-to-establish handling (E5/E8). | No OS/filesystem/network sandbox. `env={}`/`-I -S` and timeout are bounded invocation controls, not containment. |
| D4 effect authorization | 1 | Typed resource grants and source-authorized role/owner predicates compose K20/K06–K10/K17/K18 (E5/E6). Authorization decision and external authentication remain distinct. | Existing scoped JSON and trusted controlled-host interfaces supported. Physical byte-resource enforcement/authenticator is absent and must not be inferred. |
| D5 deterministic observation and error reporting | 4 | Declared error precedence and exact comparison are 1 (E2/E8); stable projection of OS/process observations needs a policy and independent measurement. External outcomes are not deterministic merely because reporting is. | Existing JSON/CLI observations supported. General file/process observation and error taxonomy adapters absent. Exact cross-platform failure behavior unproven. |

## E. Verification

| ID / capability | Class | Existing reuse and specific reasoning | Current lowering support / remaining boundary |
| --- | --- | --- | --- |
| E1 preconditions and postconditions | 1 | Predicates and K17 express supported-value conditions (E1/E6); postconditions apply to explicitly bound post-state values. Contract declaration alone does not enforce arbitrary external predicates. | Prewrite/value checks supported. General artifact post-state binding/measurement absent; requires verifier work. |
| E2 observable effects | 2 | Independent before/after acquisition and run binding realize measurement of declared effects; comparison uses existing equality/predicates (E8). Observer never supplies subject behavior. | Existing CLI/JSON/byte-preservation observations; general tree/process adapters absent. |
| E3 artifact integrity | 2 | For externally supplied expected bytes/identities, independent byte acquisition, digest measurement and comparison are verifier infrastructure (E8). Authored digest construction is B3 class 3. | Some verifier-owned hashes/byte checks exist. General artifact coverage, algorithm/path manifest binding and independent trusted expectations not implemented. |
| E4 failure classification | 1 | Declared finite enum outcomes, exact observation predicates and K17 compose classification when inputs/policy are supplied (E8). Infrastructure-unavailable, subject rejection and mismatch remain distinct. | Current runtime/behavioral/binding outcomes exist. General parse/effect error policies and observations absent; new error labels alone do not add a classifier. |
| E5 reproducibility boundaries | 4 | Contracts can state pinned inputs, expected equality and limitations (1), but cannot prove equivalence of OS/platform/time/concurrency observations (E8/E9). Need explicit measurement and replay policy. | Current verifier constrains invocation, not general bitwise/environment reproducibility. No architectural replay results obtained. |

## Aggregate conclusion

There are **25 primary rows: 7 class 1, 6 class 2, 7 class 3, 5 class 4**.
Counts are not a coverage score; publication checks mechanically verify the row
inventory. Every row's scope and mixed narrower
case matters more than a percentage. The general parser relation is the decisive
class-3 finding. Physical adapters, lowering rules and verifier infrastructure
do not erase it. No arbitrary-code delegation or package-specific operation is
credited in this matrix.
