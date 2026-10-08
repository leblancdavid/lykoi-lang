# R6.10 — Experimental general-purpose semantic prototype

**Final classification: `R6_10_PROTOTYPE_PARTIAL`.**

A single bounded operation interpreter executes explicit plans for all three frozen
R6.6 formats, including byte assembly, errors, provenance and deterministic work.
**82 tests executed: 82 passed, 0 failures, 0 errors, 0 skips.** Bounded execution
feasibility is demonstrated. Full static typed-plan judgments, field-specific encode
error attribution and exact frozen logical-cost correspondence remain incomplete,
so this is a partial realization of the complete candidate contract. It establishes
neither independent qualification, formal correctness, production readiness nor
general-purpose completeness/minimality. Production kernel remains **26**.

## Authority and baseline

The owner's “R6.10 — Experimental General-Purpose Semantic Prototype” explicitly
authorizes bounded experimental implementation of I-BOUND/C-ATOM and publication.
It supersedes earlier stop boundaries only for this experiment, not for production
integration, external acceptance or independent review. No agent delegation or
provider call was used. The implementer inherited earlier findings; tests and design
are correlated same-agent research evidence.

Initial Git status was clean at `4f138419960652720502d396ee816116447c14ef`.
Before interpreter implementation, the dedicated experiment directory was created
and [BASELINE.json](../../../experiments/semantic_interpreter/BASELINE.json)
recorded the implementation manifest: hashes of **219 tracked protected files**,
HEAD and kernel count. **26 frozen publication hashes** were verified, including
all six R6.6 publication identities. Historical R6.3–R6.9 paths and reports, production
src/schema/model/generated and tools were captured and subsequently checked unchanged.
Later-round guidance hashes are not treated as immutable historical publication hashes;
the initial checker exposed that distinction before recording the baseline.

Read R6.6 definitions/witnesses/adversarial matrix and R6.7–R6.9 reports/boundaries.
R6.7's independence failure and qualified reduction findings remain preserved;
R6.8 did not reach reviewer assignment; R6.9 isolation infrastructure is not review
qualification. These are not gates for this explicitly authorized executable round.
K01–K26 were inventoried using preserved accounting and typed-computation/predicate
interfaces. No external curated requirement, fixture or oracle was opened.

## Deliverables

All links below point to the dedicated experimental tree:

| Deliverable | Location |
| --- | --- |
| Interpreter | [interpreter.py](../../../experiments/semantic_interpreter/interpreter.py) |
| Versioned semantic contract and assumptions | [CONTRACT-1.md](../../../experiments/semantic_interpreter/CONTRACT-1.md) |
| Recursive closed JSON Schema | [semantic-plan-1.schema.json](../../../experiments/semantic_interpreter/semantic-plan-1.schema.json) |
| Explicit plans | [CFG66](../../../experiments/semantic_interpreter/CFG66.plan.json), [DSV66](../../../experiments/semantic_interpreter/DSV66.plan.json), [BXC66](../../../experiments/semantic_interpreter/BXC66.plan.json) |
| Plan authoring utility | [build_plans.py](../../../experiments/semantic_interpreter/build_plans.py) |
| Executable tests | [test_interpreter.py](../../../experiments/semantic_interpreter/test_interpreter.py) |
| Operation reuse/gap matrix | [OPERATION-MATRIX.md](../../../experiments/semantic_interpreter/OPERATION-MATRIX.md) |
| Original adversarial case status | [ADVERSARIAL-RESULTS.md](../../../experiments/semantic_interpreter/ADVERSARIAL-RESULTS.md) |
| Test results/transcript | [TEST-RESULTS.json](../../../experiments/semantic_interpreter/evidence/TEST-RESULTS.json), [tests.txt](../../../experiments/semantic_interpreter/evidence/tests.txt) |
| Exact reproducibility observations | [REPRODUCIBILITY.json](../../../experiments/semantic_interpreter/evidence/REPRODUCIBILITY.json) |
| Implementation identities | [IMPLEMENTATION-IDENTITIES.json](../../../experiments/semantic_interpreter/evidence/IMPLEMENTATION-IDENTITIES.json) |
| Publication/scope verification | [VERIFICATION.md](../../../experiments/semantic_interpreter/VERIFICATION.md) |

## Cross-domain execution

| Domain | Demonstrated behavior |
| --- | --- |
| CFG66, 53 structural nodes | Named fields, none versus present empty, Boolean/numeric/string tags, finite escapes, immediate decimal overflow, optional spaces, required LF, exact duplicate rejection, syntax/encoding precedence, canonical strings/decimal, source spans excluding trailing spaces/LF. |
| DSV66, 39 nodes | Shared quoted/unquoted field rule, commas in quotes, doubled quotes/backslash literal, multiple ordered records, whole-document syntax before conversion, Decimal15 after unquoting with character->source mapping, per-row ordered checks, canonical quoting, selection/+1 witness. |
| BXC66, 31 nodes | Header/version/count, dependent name/content lengths, raw arbitrary content, immediate name membership/length/echo validation, EOF before total/duplicate checks, malformed/truncated rejection, recomputed lengths/count/trailer, empty-selection layout. |

The VM has no format-name dispatch, separate parser entry points, library grammar
callbacks, eval/exec, dynamic import, filesystem/process/network or AI operations.
Only plan data differs. Recognition, sequencing, traversal, typed scalar conversion,
record construction, validation, joining and byte emission use shared meanings.
Rules share a bounded DAG rather than hiding parser implementations behind names.
All published plans remain below R6.6's 64-structural-node bound, including layouts
and call sites. A fourth synthetic fixed-depth plan demonstrates nested recognition;
recursive structures are not admitted.

## Executed tests and determinism

Terminal environment: Windows AMD64, Python **3.14.3**; standard library only.
Command:

```powershell
python -m unittest discover -s experiments/semantic_interpreter -p test_interpreter.py -v
```

**82/82 unittest methods passed.** Methods containing loops additionally cover
all **65,536 UInt16BE values**, all **128 ASCII values**, all nonempty truncated
prefixes of three inputs, and every work-limit cutoff below successful execution
for one representative per domain. These vector counts are not added to the
unittest denominator. Ten repeated witness executions per format produce identical
values, source provenance, error behavior, logical work and output bytes; fresh
process replay checks the saved observations. Canonical round trips compare semantic
values without input spans; output bytes stabilize after normalization.

Original R6.6 hand-derived outcomes are exercised. Coverage tables explicitly mark
X15 production persistence blocked, X16 streaming unexecuted, and exact X12 frozen
accounting blocked while experimental cutoff behavior passes. Prior NOT_RUN records
are unchanged. Initial development had one fixture-ID collision failure; that
chronology is retained in the adversarial record. Terminal evidence is the final run.

Work is an explicit logical event count, independent of elapsed test time. Node and
expression entries, examined/copied bytes, codec digits, lookahead and selected
append/comparison events are charged by the versioned contract. Host buffer metadata
costs are explicitly outside that metric. The added event conventions resolve gaps
for this experiment; they are not an exact-cost conformance claim about R6.6 0.1.

## Meaning accounting and architectural feasibility

1. **One interpreter supports all formats:** demonstrated on explicit full plans,
   malformed cases, layouts and original transformation witnesses.
2. **Composition without format reinterpretation:** domains/byte classes/escape
   spellings/validation schedules are data. CFG immediate and DSV delayed conversion
   invoke the same Decimal15 mathematical relation at different declared stages.
3. **Family overlap:** lexical escape recognition is structural choice/literal
   projection; scalar codecs need raw access and assembly. Labels are not disjoint
   irreducible construct units. Inlining changes representation/accounting, not meaning.
4. **Kernel composition:** supplied record/literal/binding/map/selection/cardinality/
   predicates/absence/checked addition compose existing meanings. Qualified equality/
   ordering vectors match the actual pure production predicate evaluator. Boolean
   projection needs no new Boolean codec. No whole-family elimination demonstrated.
5. **Bounded/deterministic:** DAG/progress/selector/dependency validation, bounded
   input/output/depth/occurrences/work and deterministic ordered failures exercised.
6. **Faithful-execution limits:** runtime typed values work for shipped graphs, but
   full static field/union consistency is not established. Encode APIs use decoded
   values rather than qualifying every externally supplied typed value. Error paths
   are generic value/tag rather than complete field paths. Accounting is an explicitly
   prospective experimental refinement. These prevent a full contract verdict.
7. **Later lowering:** explicit cursor, closed nodes, pure values and stable schedules
   appear suitable for a bounded IR/backend experiment. Preservation of cost/depth,
   provenance and encode errors under lowering has not been executed or proved.

New candidate meanings actually implemented: checked raw access/recognition,
predictive cursor traversal and bounded consuming recurrence, ordered joining/byte
assembly, provenance/prefix/result transport, Decimal15 recurrence/inverse and
unsigned binary codecs, deterministic cursor errors and logical limits. Existing
scalar subrelations do not eliminate their envelopes. Host arithmetic, byte operations
and containers are implementation mechanisms documented separately. No new kernel
total, minimum, irreducibility or universal parser/computation claim is made.

## Remaining gaps and next proposed experiment

Priority gaps: complete statically declared typed decode/layout/result schemas;
earlier-field dominance/type inference; standalone encode admissibility and precise
field paths; normative accounting refinements and lowered trace correspondence;
all source-map/optional/tag laws; independent expectation review. Unicode, recursion,
streaming, strong integrity and physical effects are intentionally unsupported.
Same-length binary tampering is accepted under the frozen structural-integrity contract.

Recommend a separately authorized **typed-plan and encode-boundary closure experiment**:
freeze this prototype/evidence; add explicit record/union schemas and reject known
ill-typed projections before execution; qualify independent typed-value encode inputs;
carry complete field paths and declared output attribution; compare interpreter and
a small nonproduction lowered backend under every bounded event cutoff. Fix expected
laws prospectively before authoring. Do not integrate into production or start an
independent-review round on this recommendation alone.

## Preservation and stop

Production kernel **26**, production compiler/lowerer/runtime/verifier/schema/model/
generated/tools and historical R6.3–R6.9 identities unchanged. Benchmark solutions
authored/compiled **0**; P6-A04 acceptance checks **0**; P6-A05 not accessed; provider
calls and independent reviews **0**. Diff scope is the new experiment/report and
additive research/boundary guidance. `git diff --check` and preservation/replay checks
are recorded in VERIFICATION.md.

**Stopped after R6.10 implementation, tests, evidence and publication. Await owner
authorization before any next development, production integration or review.**
