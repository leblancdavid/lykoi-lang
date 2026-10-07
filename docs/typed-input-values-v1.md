# Lykoi typed input/value closure 1 — R5.105

`typed-input-values-1` is an explicitly selected bounded extension of
`typed-mutable-values-1`, not a new major semantic family or a change to the
historical v0.3 serialization. Set `context.domains.input_value_profile` to
`typed-input-values-1`. Retain every scalar and mutable facet and add the
`input_contracts` facet under the existing typed mutable FRC profile. Prior
R5.104 contracts retain their versioned interpretation.

## Values and provenance

Scalar literals already supported by the scalar profile remain typed string,
enum and supported timestamp constants. No writable boolean/numeric type,
arbitrary expression evaluation, computed lists or general nullability is added.

Collection creation has three disjoint closed representations:

* **Literal:** `{source:'literal',value:[ELEMENTS]}`. Always copy these exact
  authorized typed elements. There is no semantic input, CLI binding, pipeline or
  omission default for this field. `[]` is an explicit literal value.
* **Required supplied input:** `{source:'input',input,encoding,pipeline,error}`.
  Omission is rejected by the declared input contract, never converted to `[]`.
* **Input with omission default:** the preserved R5.104
  `{input,encoding,default,pipeline,error}`. Only omission invokes the declared
  default; supplied `[]` is input, not a default. No creation default applies to
  mutation. Historical migration defaults remain a separate authority.

Collections preserve their declared scalar element type/enum domain, insertion
order, exact equality and allow/unique duplicate policy. Unique literals with
duplicates reject; allow literals preserve every occurrence. No implicit trim,
sort or deduplication. Persisted required record fields cannot themselves be
omitted; absence belongs to the input mapping and declared omission policy.

## Observation stages and conditions

Every closure pipeline validation has exactly
`{kind:'validate',rule,error,stage,when}`. Existing rules are nonempty, nonblank
and typed. `stage` is RAW, TRANSFORMED or PERSISTED:

* **RAW** is a private copy of the adapter-decoded externally supplied typed
  value before any semantic transformation. CLI JSON decoding is an external
  encoding operation; it is not trimming or semantic value computation.
* **TRANSFORMED** is the value at that point in the ordered pipeline, after all
  preceding transformations. A validation may still observe RAW after trim.
* **PERSISTED** is the final proposed value at the persistence boundary, validated
  before commit so rejection remains atomic. No later transform/element map may
  follow this observation. It does not mean an already-written value is rolled
  back after rejection. Reload/store validation observes committed values.

Append/add-unique pipelines operate on incoming elements rather than the whole
persisted collection: explicit PERSISTED element-stage checks are refused. The
complete resulting collection always receives final typed validation before
commit. Replacement and creation pipelines can validate the PERSISTED candidate.

`when` is null (unconditional) or `{stage,predicate}` for one bounded input-state
predicate: present, absent, empty, nonempty or whitespace. Presence is mapping
membership and independent of value/stage. Empty/nonempty compare raw strings
with `''` exactly; whitespace means a nonempty string containing only whitespace.
No trim is inferred: RAW `'   '` is nonempty and whitespace, RAW `''` is empty
and not whitespace. TRANSFORMED string predicates observe the current pipeline
value. No OR/NOT, cross-parameter programming or general boolean expressions.

Omitted input invokes neither transformation nor value validation. Creation uses
its declared omission default or required-input rejection. Optional mutation
omission leaves the field unchanged; when all changes are omitted it also avoids
writing the store. Supplied empty strings/arrays remain supplied values. Explicit
null remains supported only for the existing nullable timestamp API type; CLI
text `null` is not a general null literal. No new null predicate is introduced.

Thus RAW nonempty → trim accepts whitespace and may persist empty; trim →
TRANSFORMED nonempty rejects whitespace; RAW-nonempty conditional TRANSFORMED
nonempty accepts raw empty but rejects raw whitespace. These are distinct facts.

## Semantic parameters and external adapters

`input_contracts` is an array of:

```
{operation, parameter, type, presence:'required'|'optional',
 binding:{source:'cli_flag',flag,encoding:'text'|'json'|'repeated'},
 missing:null|{kind:'application_error',error}|{kind:'cli_rejection'}}
```

`operation` and `parameter` identify semantic inputs, independently of flag
spelling. `type` retains exact scalar domain/nullability or collection
element/order/duplicate/equality policy. The backend binds a declared flag to
that identity using an explicit argparse destination, not flag-derived names.
All creation and mutation inputs, including mutation identity lookup, need
exactly one declaration. Literal/resource assignments are not parameters.
Optional status must agree with creation defaults or mutation unchanged policy;
required status must agree with required input/reject policy. Query/lifecycle
bindings keep their existing profiles; their semantics are not expanded.

Required input needs declared missing behavior. `application_error` emits the
declared JSON error on stderr, no stdout, exit 1. API creation also checks required
presence before executing the scalar backend; required mutation preserves its
existing declared missing error and lookup-first API order. CLI required presence
is checked at the external boundary before operation dispatch.

`cli_rejection` authorizes an external missing-input rejection without inventing
an application error identity: exit 2, no stdout, diagnostic
`missing required input: FLAG\n`. That diagnostic is the versioned adapter
representation of rejection, not a claim that the source authorized argparse's
incidental prose. It is intercepted explicitly; parser `required=True` is not
used for closure inputs. Normal malformed/unknown CLI syntax remains adapter
syntax handling. A CLI-only rejection does not declare an application API error;
the API's existing mutation omission policy remains separate.
For a required mutation parameter with CLI-only rejection, `missing_error` is
explicit null (no application error identity). An omitted direct API value raises
`MissingExternalInput`, not an invented JSON application error. Structural
validation requires the matching declared CLI rejection; bare null missing-error
authority without that binding refuses.

Missing bindings, wrong/nonexistent parameter identities, conflicting duplicate
flags/declarations, wrong type/encoding, changed required status and attempts to
bind constants refuse. Distinct flag spellings are allowed when source-authorized;
reconciliation must reject invented/swapped bindings. Parser choices do not
define semantic enum validity or missing-input behavior.

## Authority, structure, BDI and faithful normal V1

The closed producer schema extends the normal typed FRC vocabulary with literal
creation, explicit stages/conditions and `input_contracts`. All facts retain
source quotes and exact relations. Source-only inventory disagreement on invented
literal initialization, trim, required status, missing error, stage or binding
disputes reconciliation. Structured facts do not grant behavioral authority.

Structural projection preserves CreationValueSource, SemanticParameters,
ExternalBinding, MissingInputBehavior and the existing full ValidationStage,
InputPresence, TransformationPipeline and AtomicWriteEffect facts. Coverage
recomputes the complete IR/projection. Missing selected input facet, stage,
condition, required-input error, or literal/default distinction fails closed.

BDI retains existing pipeline/stage decisions and adds finite value-source,
required-input, missing-input and external-binding decisions. Adequacy uses the
existing source-authority engine; removing determined material authority is
IMPLEMENTATION_UNDERSPECIFIED. No unrelated predicate/decision family is added.

Normal V1 retains full source contract, profile facts and recomputed typed IR.
Recovery compares the entire faithful projection, including literal contents,
source/default distinction, validation stage/condition, required presence,
binding and error. Lowering recomposes/validates the IR and deterministically
generates the self-contained runtime through the normal compiler dispatcher.

## Atomicity, persistence, composition and boundaries

The existing single-store/single-record atomic mutation protocol is reused:
validate/read state, check lookup/guards, prepare all changes privately, validate
the final candidate, atomically persist once, then return. Rejected type/stage
validation and supported write/replace failures preserve prior bytes. This is
not distributed/concurrent transaction semantics. Collection literals are copied,
persisted, reloaded and queried through unchanged CollectionQuery membership.
Literal creation does not invent historical migration authority.

Synthetic article/contact/product/profile source captures and external literal
plans are in `src/lykoi_workspace/input_corpus.py`; tests are in
`tests/test_input_values.py`. Source extraction, inventories and oracles are
same-agent captures with synthetic approval, not live English accuracy or
independent cognition. Exposed corpus transfer is regression evidence only.
No OR/NOT/ranges, relationships, graph/events/successors, temporal arithmetic,
joins, aggregates or pagination is implemented. See the R5.105 report for actual
verification and the pre-transfer content lock.
