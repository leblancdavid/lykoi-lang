# R6.5 cross-domain reuse analysis

These are conceptual examples chosen to pressure reuse, not source contracts,
benchmark solutions, executable programs, behavioral results or held-out evidence.
No fixture, program or oracle is authored or executed.

## X1 — Parse and validate a configuration file

Scope: immutable UTF-8 assignments in a declared bounded grammar; preserve exact
values, reject duplicate keys and unknown enum values, publish one validated
configuration snapshot. Quoting, whitespace and errors must be source-authorized.

1. R-ACCESS obtains one authorized immutable file snapshot; T-BYTES/encoding
   policy binds input. Reading alone does not interpret assignment syntax.
2. S-PARSE interprets the declared grammar into finite `(key,value,span)` rows.
   Malformed encoding/syntax/trailing input uses the separately declared failures.
3. K01–K10/K18 represent rows, test key membership and duplicate cardinality,
   validate allowed values and select supported keys. Optional trim is K11 only
   where policy explicitly permits it. Stable deduplication is not duplicate rejection.
4. K17/K20 guards authorize publication. Single JSON-state replacement can reuse
   K21/K22 if the output is that qualified store; a general file output needs
   R-STAGE with a separately justified physical contract.
5. V-RESOURCE independently observes unchanged input, exact accepted output and
   unchanged destination on declared prepublication rejection. Comparing producer
   “valid” metadata alone is insufficient.

The existing kernel covers stages 3–4's bounded data decisions, not stage 2.
Configuration-specific grammar is data for S-PARSE, not a new runtime parser function.

## X2 — Extract and transform an asset archive

Scope: read a bounded archive of text assets, select entries named in an explicit
manifest, trim authorized text content, create a complete export snapshot under
one destination root. No executable content is run. Reject duplicate paths,
escaping paths and declared expansion-limit violations.

1. R-ACCESS snapshots the archive. S-CODEC interprets its container and compressed
   payload relation; decompression is not supplied by finite map or file IO.
2. Finite typed entry/manifest records hold supplied names, sizes and dependency
   edges. K06/K09/K10/K18 enforce explicit equality/membership/duplicate rules;
   K23 can detect declared reference cycles, but does not order extraction work.
3. S-PARSE/S-CODEC decode selected text with the same declared encoding/failure
   model as X1. K12 applies already defined K11 trim to each selected decoded
   value. Arbitrary image conversion or serialization is outside that body.
4. R-ACCESS enforces actual root containment and writes specified bytes into a
   private tree. A string predicate alone cannot prevent symlink escape. Assembly
   into another archive would additionally need S-CODEC encoding semantics.
5. R-STAGE publishes only if the narrow T-PUBLISH contract is independently
   established; otherwise atomic publication is unresolved. Failed validation
   discards private staging; process rollback/multi-root commit is not promised.
6. V-RESOURCE observes destination entries/content and unchanged source. Any
   digest measurement is verifier-owned unless subject-authored S-DIGEST is
   separately necessary and authorized.

This pressures codec, resource containment and transaction boundaries without
package installation. A generic `extract_transform` callback would conceal all
three and is rejected.

## X3 — Process a structured data import

Scope: bounded delimited UTF-8 rows with declared quoting grammar; import contact
records into one existing local durable store, reject missing identities and
invalid references, preserve prior store bytes on validation failure.

1. R-ACCESS snapshots input; S-PARSE with a different declarative grammar produces
   typed row candidates. Duplicate headers, quoted delimiters and empty versus
   absent fields have explicit policies. Encoding/tokenization is the same
   general interpreter responsibility as X1.
2. K19 preserves presence, K06/K10/K18 implement declared identity/duplicate
   decisions, K11–K13 perform only explicitly authorized trim/stable uniqueness.
   Nominal references/existence use K01/K04/K06/K10/K18, as in X2's manifest.
3. K17 guards and K20 authority apply to the committed before-state. Proposed
   rows and errors must bind to a coherent operation frame. Existing bounded
   related creation supports limited compositions; **arbitrary bulk import row
   creation is not currently implemented or proven**. Unbounded batch promises
   need a separate integration/semantic audit, not extrapolation from finite sequences.
4. For an admissible bounded write composition, K21/K22 support one-store
   candidate validation and replacement. Large imports do not inherit this claim
   merely by being finite. A new export tree uses the distinct T-PUBLISH question.
5. V-RESOURCE observes exact committed rows, reference integrity, old byte
   preservation on rejection and unchanged input. Reproducibility is relative to
   pinned grammar/input/store/observation policy, not every OS failure trace.

Import duplicate/merge rules are existing predicates and declared mutations where
supported; they are not embedded in a codec or guessed by a backend.

## Shared capabilities and independent pressure

| Capability | X1 configuration | X2 archive assets | X3 data import |
| --- | --- | --- | --- |
| S-PARSE with explicit encoding/failures | assignment rows | selected text/manifest documents | delimited rows |
| Finite records/predicates/presence | keys/value domains | entries/manifest policy | fields/identity policy |
| Nominal references/reachability | optional section references | asset dependencies | contact/group references |
| R-ACCESS immutable authorized resources | config input | archive input/staging | import input |
| S-CODEC | text encoding if separate | container/compression plus text | text encoding if separate |
| Guard/lifecycle/durable-state composition | approved snapshot | staged/published metadata | bounded store updates |
| Atomicity scope | qualified one-store output | unresolved physical tree publication | qualified bounded one-store write |
| Independent observation | accepted config bytes | exported entry bytes/tree | committed/rejected store bytes |

S-DIGEST is optional for authored programs in all three; independent integrity
measurement does not require an authored digest primitive. R-PROCESS is also
optional in all three and is **not** used to bypass their missing parser/codec.
An external converter could be legitimate interoperation in another system, but
its conversion semantics would remain external and receive no native coverage credit.

All three require an honest raw-input interpretation boundary. They show why
S-PARSE is reusable; they do not demonstrate that one final grammar/AST design,
archive codec or transactional adapter is sufficient. None independently
justifies a package-only primitive, general dependency solver or unrestricted code.
