# R6.6 architectural alternatives and redundancy challenge

All alternatives are prospective. Human readability of source/generated code is
not a criterion. Deterministic runtime behavior must not require an AI service or
provider credentials; authoring assistance may come from any provider.

| Criterion | A: dedicated parsing/codec constructs | B: general deterministic interpretation/composition | C: bounded vocabulary + explicit typed codecs |
| --- | --- | --- | --- |
| Generality | Grammar parser plus lexer, encoder, binary reader can serve many formats, but risk per-format proliferation. | Largest potential reach if sequence access/iteration/reduction/arithmetic are defined; deterministic alone says little about expressive scope. | Same bounded structural interpreter for three domains; scalar registry is extensible only with explicit semantic review. |
| Compositionality | Typed interfaces connect lexer/parser/codec; overlapping escaping/span/error responsibilities can duplicate meaning. | One typed evaluation model can derive parsers/codecs, but needs a substantial operation algebra and termination/effect discipline. | Shared Seq/Choice/repetition/layout; codec leaves are explicit and pure; existing decoded predicates/writes remain distinct. |
| Formal precision | High with complete grammar/codec contracts; an opaque `parse(format)` registry is inadequate. | Possible small-step semantics, but all scalar/sequence operations, work accounting and errors must be stated. | Candidate 0.1 defines exact bounded byte/ASCII relations, structural nodes, staging and refusal rules; no general recursion claim. |
| Implementation complexity | Separate engines and cross-engine error/provenance reconciliation; library wrappers insufficient. | Highest initial scope: general evaluator, typing, termination/budgets, possibly checked folds/recursion and optimizer. | Moderate relative scope: bounded evaluator, codec leaves, layout/provenance support; still substantial new compiler/runtime work. |
| Deterministic lowering | Feasible for a fixed grammar subset; normalize engine behavior to semantic contract. | Feasible in principle, not established; general determinism/termination harder with broad evaluation. | Plausible finite DAG/consuming bounded repeats with specified codecs; logical cost and exact errors constrain optimization. |
| Verification | Independent recognizers per construct, round-trip and malformed-input checks. | Broad interpreter refinement/termination proofs and independent witnesses required; self-interpreter agreement insufficient. | Independent small relations plus paired layouts and cross-domain challenge sets; codec registry growth expands obligations. |
| Security/authority | Dedicated APIs can restrict effects, but conventional codecs may accept external references/hooks. | Explicit effect system needed; unrestricted callbacks/processes defeat native coverage and containment. | Pure supplied bytes only; no authority from names; physical K20 enforcement separately verified. |
| Existing-kernel compatibility | New versioned profiles; declared records/predicates/K22 reused after decode. Existing unknown forms stay rejected. | Risk of replacing rather than extending kernel meanings, especially K12/K17/K24; reject implicit reinterpretation. | Retains 26 unchanged; new result/byte/IR bindings prospective; old errors/IDs/storage and approval boundaries preserved. |
| AI-native authoring | Many coordinated policies; typed schemas can make omissions visible. | Uniform authoring vocabulary, but greater room for accidental algorithms, termination omissions and unsound generated claims. | Explicit schemas/dependencies/bounds/codec laws support machine checking; AI must supply selectors/layouts/policies without runtime inference. |

## Reduction attempts and candidate redundancy

1. **Separate tokenizer:** not needed by CFG66/DSV66. ScanClass, choices and spans
   give lexemes inside I-BOUND; a materialized token stream is optional typed output.
   This does not prove that all contextual/Unicode lexing fits the subset.
2. **Separate parser per domain:** no new config/DSV/archive primitive justified.
   Their framing, escape tables and output schemas are plan data in the same algebra.
3. **Standalone general serializer:** assembly is another direction of structural
   composition. Grammar inversion cannot derive a canonical layout automatically;
   layout must be supplied and paired laws checked. Parsing and assembly might still
   be separately counted core meanings after an accounting audit.
4. **Boolean conversion:** finite literal projection derives it; no new scalar codec.
5. **Length/ordinal generators:** K18 and K24 suffice for these layouts. UInt16BE
   interpretation/encoding is new, not supplied by integer addition itself.
6. **Subject digest/checksum:** structural integrity is enough for the declared BXC66
   contract; stronger integrity is an open extension question, not hidden evidence.
7. **C-ATOM versus I-BOUND:** finite tables can be inlined as choices; UInt8 can use
   byte value projection. Decimal15/UInt16BE can be derived only if additional fold,
   multiplication/division or equivalent finite transduction meanings are provided.
   A 32768-value lookup table is finite but not evidence of useful general minimality.
   Replacing C-ATOM with B transfers semantic burden; no strict minimum established.
8. **Bytes/results/spans:** representation refinements reuse sequence/record concepts;
   generating slices, tags, prefixes and provenance introduces observable operations.
   Do not count every field as a construct, or erase operations as “just types”.
9. **Deterministic failure:** existing ordered validation handles decoded conditions;
   syntax position, resource rejection and full consumption are inseparable policies
   of interpretation. A separate error primitive is not justified by the witnesses.

## Recommendation and evidence strength

Prefer **C as a bounded investigation candidate**, not an adopted design. It makes
the missing meanings visible while avoiding an unrestricted computation engine.
A with factored internals may be semantically identical to C. B may ultimately be
smaller in irreducible meanings, but has no specification-level reduction here that
derives the witnesses using fewer *honestly accounted* operations.

Sufficiency is conditional on the proposed typed interpreter/codec definitions and
limits. Independent reductions, lower bounds and authoring/verification measurements
are absent. Three synthetic specification witnesses cannot establish universal
expressiveness, correctness, AI reliability, performance or a proven minimum.
