# R6.5 — General parsing and typed resource effects decomposition

**Final classification: `R6_5_SEMANTIC_EXTENSION_REQUIRED`.**

This is a **bounded architectural finding**, relative to the meanings admitted by
the existing 26-construct accounting and versioned normal profiles. General
grammar-driven interpretation of previously uninterpreted text/bytes needs a
meaning not supplied by those operations. A backend parser cannot be called an
existing-kernel composition merely by wrapping it in an operation contract or map.
Physical resource access, independent observation and isolation also need work,
but do not all require new core constructs. No extension is admitted or implemented.
This is not a minimality theorem, arbitrary-program impossibility result, native
blocker measurement, or P6-A04 capability/acceptance result.

## Authorization, scope and evidence

The owner's conversation request, “R6.5 — General Parsing and Typed Resource
Effects Decomposition”, explicitly authorizes documentation-only architectural
investigation of families A–E, existing-kernel classification, at least three
non-package examples, candidates, alternatives and a next bounded experiment.
It forbids implementation, benchmark solutions/compilation, P6-A04 acceptance,
P6-A05 access, historical identity changes and provider dependence. That request
is the authority for this round; no execution receipt or evaluator is appointed.

Initial Git status contained the R6.4 publication changes. Before this round's
first edit, they had become the clean existing commit `402963b` (`r6.4`), as shown
by status and recent log. No commit was made by this round. Baseline preservation
digests were captured against that clean state. Existing records are not amended.

Evidence is source/specification inspection, not newly executed behavior:

- [Expressibility matrix and exact evidence anchors](r6_5/EXPRESSIBILITY-MATRIX.md).
- [Primitive candidates and layer obligations](r6_5/PRIMITIVE-CANDIDATES.md).
- [Three conceptual cross-domain decompositions](r6_5/CROSS-DOMAIN-REUSE.md).
- [Publication and preservation verification](r6_5/VERIFICATION.md).
- Prior [R6.4 inventory](r6_4/CAPABILITY-INVENTORY.md) supplies the motivating
  gaps; no package source, fixture, oracle or implementation is revisited here.

All examples and proposed interfaces below are architectural prose, not
Lykoi programs, solutions, executable plans or behavioral test results.

## What the kernel can already do

K01–K10/K18/K19 represent supplied typed records, finite sequences, exact
bindings, predicates, selection, cardinality and presence. K11–K13 provide trim,
finite pointwise application of an already defined transformation and stable
uniqueness. K14/K17/K20 describe lifecycle, operation contracts and scoped typed
authority. K21/K22 support durable state and the qualified local atomic commit.
K23 observes finite nonempty reference paths; K24–K26 add specific checked
integer and elapsed-time meanings. None supplies arbitrary computation.

These compose decoded manifests, nominal dependency references, source-authorized
validation, role/owner checks, explicit state transitions and bounded local
record transformations. They do not turn an opaque input into a token stream,
define an arbitrary grammar's recognizer, decode compressed bytes or extend a
single JSON-store replacement to a multi-root filesystem/process transaction.

The current compiler's own JSON parser and verifier's host-side JSON/hash handling
are implementation/measurement code, not authored subject parsing capabilities.
The existence of such Python code is no native expressibility proof.

## Decision rule: semantics versus implementation

An operation is class 1 when its observable result follows from existing
meanings on admissible inputs. It is class 2 when a physical adapter realizes
an already specified resource/effect contract without adding an application
decision or pure value relation. Class 3 identifies an independent observable
meaning missing under the current vocabulary. Class 4 records insufficient
evidence about a broader composition or contract. The matrix gives every requested
capability a primary class, with narrower class-1 reuse explicitly separated.

Calling a primitive “general-purpose” is not enough for class 2. Token extraction,
decoding and grammar interpretation define new input/output relations even when
implemented by standard libraries. Conversely, reading an authorized immutable
resource's bytes can be a runtime adapter once resource identity, snapshot and
failure semantics are explicitly specified. Its availability in today's normal
profile is a separate question; it is currently absent.

The decisive parsing argument is bounded: existing sequence transforms consume
already supplied values and have fixed admitted bodies. They neither enumerate
character/byte positions nor construct grammar-dependent tokens/trees. Equality,
selection and reachability on supplied records do not construct those missing
representations. Literal enumeration could recognize a fixed finite catalogue,
but does not cover arbitrary input lengths and a supplied grammar. K24's bounded
arithmetic graph cannot silently become a scanning loop. These are the same
accounting principles used when arithmetic and reachability were separately
justified. A new declarative parsing meaning is required **for this general input
interpretation scope**, not proven necessary for every finite special case.

## Minimal architectural alternatives

| Alternative | Reuse and added layers | Bounded reach / tradeoff |
| --- | --- | --- |
| M0: decoded-data boundary | Keep current kernel/profiles; external system supplies already typed rows/manifests; use predicates/references/local state writes | Useful configuration validation and import reconciliation after decoding. Cannot claim native raw-input parsing, archive extraction or process effects; changes the system boundary rather than solving the full objective. |
| M1: adapters only | Reuse K20/K21/K22; add general resource access/identity adapters, deterministic binding rules and independent observation | Could extend physical realization of already specified values/effects. Cannot close grammar or compression semantics by hiding parsers. Resource snapshot, nominal type and atomicity refinements need a separate semantic audit. |
| M2: bounded declarative interpretation plus resource adapters | Candidate S-PARSE with explicit byte/text domains and grammar/failure policy; K01–K10/K18–K23 for results/manifests/guards; optional named archive codec; R-ACCESS/R-STAGE adapters, lowering and verifier work | Recommended research direction, not a finalized construct count. Keeps application decisions declarative. A grammar interpreter is new semantics even if lowered to a library. Archive codec and digest meanings require separate justification; no automatic general recursion or conventional callback. |
| M3: unrestricted code/process delegation | An arbitrary script/parser/installer runs behind a command | Rejected as native semantic coverage. It relocates missing behavior into conventional code and gives no kernel sufficiency argument. Process integration may be legitimate external interoperation, with explicit attribution of that boundary. |

M2 is smaller in scope than a general interpreter, unrestricted fold/recursion or
filesystem transaction language. It does not prove a minimum construct set. A
fixed-format codec family might ultimately be preferable to grammar interpretation,
but each codec's accepted input, ordering, ambiguity and failures must have visible
language meaning. A list of adapters with unspecified callbacks is not that design.

## Risks and unresolved questions

1. **Accounting drift:** K17 and K20 could become containers for any algorithm.
   Require a composition derivation or a newly accounted value/effect meaning.
2. **Parsing scope:** choose a terminating grammar subset, ambiguity policy, Unicode
   version/encoding, consumed-input policy, source locations, integer/size limits and
   error precedence. General recursive grammars and error recovery are not justified.
3. **Representation:** the current profiles do not admit a general recursive AST,
   byte collection or tagged parse-result sum. Flat bounded typed rows with nominal
   parent references are a reuse hypothesis; construction/binding support is absent.
4. **Resource identity:** path spellings are not immutable content identity or live
   authority. Symlinks, case rules, stale handles and TOCTOU need a backend-specific
   contract. Digest equality is not authenticity or proof of semantic correctness.
5. **Atomicity:** one-store replace is not multi-file atomicity, crash durability or
   rollback of a process. Whole-tree staging with one publish boundary is narrower;
   readers, concurrent writers, crash points and filesystem support remain unresolved.
6. **External nondeterminism:** pinning an executable/environment constrains inputs,
   not process schedules, clocks, OS failures or exact diagnostics. Stable error
   classification must preserve raw observations and declared limitations.
7. **Verification independence:** producer manifests/statuses cannot establish their
   own correctness. Independent bytes and before/after observations still need an
   explicit oracle and run binding. Same-agent conceptual design is correlated evidence.
8. **Generality:** three designed examples are reuse pressure, not held-out evidence.
   No generic solver, dependency/version resolution, package rules or package-specific
   profile is warranted by this analysis.
9. **Compatibility and provider independence:** candidate types/profiles must be
   prospective and versioned; old v0.3 serialization and frozen histories retain
   their meaning. Grammar execution, lowering and verification must require no LLM
   service or provider credentials. An AI may propose a model but cannot decide
   runtime parse behavior, permission or success.

## Recommended next bounded research experiment

**Seek separate authorization for a specification-only composition challenge** of
a bounded, nonrecursive grammar for configuration assignments and delimited import
rows. Freeze source-authored grammar examples and failure expectations before
design, including non-ASCII decoding errors, delimiters within quoted fields,
duplicate keys, trailing input and size rejection. Ask whether every result can
be derived using existing operations on raw input, without predecoded tokens,
literal enumeration or host callbacks. If not, write the smallest explicit
S-PARSE contract, result representation and prospective accounting argument.

Use two domains with identical interpreter rules, plus a third read-only archive
manifest example to challenge resource identity separation. Specify byte/encoding
and error semantics before discussing physical adapters. Resolve whether fixed
codecs or a grammar operator give the smaller honest boundary. Produce derivations,
counterexamples and an independently reviewable spec; do not implement, compile,
run acceptance or authorize benchmark access. Any later synthetic implementation
and external qualification require their own authorization and precommitted checks.

## Outcome and stop

Existing-kernel reuse is substantial for **already decoded bounded values**.
Adapter and verifier changes alone do not supply general raw-input interpretation.
Thus `R6_5_SEMANTIC_EXTENSION_REQUIRED` is justified within the inspected normative
vocabulary, while final minimal primitive set, arbitrary abstract-kernel expressive
power and resource transaction sufficiency remain unresolved.

Kernel remains **26**; compiler/lowerer/runtime/verifier/model unchanged. Proposed
architecture executions, benchmark authoring/compilation and P6-A04 acceptance
executions: **0**. Publication verification is documentation/preservation checking
only. No P6-A05 access or provider-specific requirement.

**Stop after publication and verification evidence. Await explicit owner authorization.**
