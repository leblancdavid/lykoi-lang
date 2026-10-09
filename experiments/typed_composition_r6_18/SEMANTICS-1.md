# Typed composition 1 — bounded semantics and validation rules

This experimental profile lowers only to the unchanged R6.10 VM. Its schema is
`typed-composition-1.schema.json`; executable validation adds graph/type/identity
rules. No third-party schema validator is needed at runtime. `load` is the strict
serialization boundary; `validate`, `expand`, `diagnose` are the in-memory API.
All executable inputs are plain JSON data; no host-language callback is admitted.

## Declarations, immutable values and dependencies

Exactly one revision per case-sensitive ASCII family name is present in a package.
The program is a closed Int64 region; reusable definitions have at most eight typed
parameters. A region declares immutable typed step results, an exact permutation
of steps defining execution order, and one result expression. Each step explicitly
enumerates every referenced parameter/local in `deps`. Its inferred type must equal
its declaration. No mutation, rebinding, shadowing, dotted projection, globals or
free references. Duplicate parameters/locals/families are capture errors.

Types: Int64 (exact signed64 integer; Boolean distinct), Bool, Unit (null).
UInt8 atom returns Int64; value returns expression type; check/end return Unit.
Constants preserve exact type. Add and le require Int64 operands, eq requires
identical types. Addition overflow remains an existing VM runtime rejection.
No integer refinement is inferred: an Int64 result can still fail UInt16BE encoding.

Expressions evaluate recursively left to right using existing ref/const/add/le/eq.
Call arguments are only immutable refs or scalar literals, exactly matching the
monomorphic parameter signature. They are substituted into the template, not
eagerly computed or materialized at call entry. This is template composition,
not call-by-value function evaluation: repeated parameter uses repeat VM expression
charges and literals acquire provenance at their actual use. Arbitrary argument
expressions are refused to prevent accidental duplicated computation. The expanded
form is normative, including these observable provenance/work effects.
In particular, the VM wraps a seq result Cell with the region's start/end span;
it does not preserve the inner expression's start as the returned Cell start.
The nested increment's returned span starts at cursor3, so a subsequent outer
bound failure reports offset3; failure inside increment still reports offset1.

## Scope, order and expansion

Local dependencies form a DAG; all inputs to a step must precede it in the declared
order. Validation never topologically sorts or optimizes execution. Every step,
including an otherwise unused result, executes exactly once in that order until
absorbing failure. Local result expressions execute after all steps. Registry
dependencies are exactly the called families and pin their content IDs. Self and
indirect cycles reject; unused definitions are validated too. No program may be
called as a definition. Nesting is bounded; it adds ordinary seq nodes, not a new
VM operation. Inline expansion preserves those nodes and their charges.

Each region lowers to seq. Its steps lower one for one, except compose lowers to a
nested seq for the target definition. Parameter substitution uses the caller's
explicit immutable expressions; callee locals use fresh deterministic bindings
`b_` + SHA256(region path + '/' + local ID). Root path is `program/<content ID>`;
primitive sites append local ID; call region paths append call local ID and target
content ID. No user identifier can name a generated binding. Caller names have no
visibility in callee scope. Explicit argument passing is the only cross-scope link.

Fixed encode is emit UInt16BE of root. No encode template, host computation, record,
loop, choice, effect, optimizer, code generator or general graph compiler exists.
Original VM `validate` runs after expansion; public `execute` validates again.
Diagnostic mapping preserves raw VM IDs; it never rebases or hides runtime errors.

## Stable identities and tampering

Content ID hashes canonical JSON of `{version, foundation, definition}` excluding
the definition's identity field. Canonical JSON sorts object keys, preserves array
order, ASCII-escapes text, disallows floats, and has no whitespace. Foundation is
raw SHA256 of the frozen interpreter. Name/revision/signature/order/body/dependency
pins all participate. Compact structural identity is not semantic equivalence.
Definition, dependency and call hashes must agree; altered content fails. A revised
definition needs a new ID and callers must be explicitly resealed. There is no
latest-version lookup or mutable persistent registry. The package is copied during
lowering; concurrency/hostile concurrent mutation is not qualified.

## Structured diagnostic precedence

One diagnostic `{code,path,detail}` is returned by `diagnose`; no LLM judgment.
Strict JSON errors (duplicates/noninteger numbers/decode) and representation bounds
precede package/header checks. Headers/signatures and missing dependency targets
precede registry cycle checks. For each definition in supplied order: declaration
uniqueness, order permutation, step expression typing/shapes/reference closure and
exact deps, local cycles, dominance/order, exact symbolic dependency set, result
typing, then content identity. Expansion bounds precede original VM validation.
Mixed-invalid inputs receive this first deterministic diagnostic, not all errors.
Diagnostic order inside an object follows the representation's supplied order;
execution order is exclusively the region order array. JSON key permutation is
not a promise of identical diagnostics on malformed representations.

After validation, the frozen VM alone defines runtime precedence: input preflight,
ordered reads/checks, result and encoding; tightened limits retain existing sites,
depth and logical work. The witness compares exact entire success/failure envelopes
and per-entry ordered traces, including every work cutoff. No static typing claim
eliminates runtime overflow, bounds, truncation, trailing input or budget errors.

## Resource bounds

Serialized/canonical input and expanded plan at most 64KiB; representation traversal
8192 values/depth24, strings256, signed64 integers; at most eight definitions plus
program, eight parameters/dependencies per definition, 32 steps per region and128
stored steps total; expression depth8; dependency traversal depth16; expansion
nesting4 and configurable1..64 emitted nodes. Original VM64-node/depth16/2048
expression-visit limits still apply and win if stricter. Expansion checks node
budget before emitting each node. Program encode consumes one node. Wrapper work
is not charged as VM logical work: timings/allocation and VM work are separate.

These bounds qualify small deterministic composition only. No semantic equivalence
solver, requirements fidelity, AI discovery, universal equivalence, formal proof,
production completeness, local inference or cost superiority is established.
