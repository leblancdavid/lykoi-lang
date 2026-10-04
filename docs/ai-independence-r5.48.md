# R5.48 — AI independence and execution dependency boundary

## Architectural policy

**Lykoi is an AI-native programming language, not an AI runtime.** AI may author,
modify, analyze, navigate, optimize or explain programs, propose transformations
and operate development agents. Core meaning, validation, compilation, lowering
and execution must not depend on an AI provider, model, LLM, OpenCode, ChatGPT,
network inference or AI credentials. An architectural violation fails qualification;
it must not be normalized into the core dependency inventory.

Semantic authority resides in versioned language definitions, declared contracts,
deterministic validator/compiler rules and declared program inputs. A model can
propose a representation; the toolchain independently accepts or rejects it.
For a **fixed valid program**, meaning is independent of its author: GPT, Claude,
Gemini, a local/future model or a human. This does not demand equal author outputs.

Provider unavailability after a program exists must leave validation, compilation,
deterministic lowering and execution viable, subject to ordinary declared program
dependencies. An explicitly chosen future AI library/service could be an optional
application dependency, analogous to a database or web API. It would need a separate
program/tool identity, never become required core semantics. R5.48 implements no
such integration and introduces no semantic construct: core count stays **30**.

## Dependency domains

| Domain | Current interpretation |
| --- | --- |
| `LANGUAGE_CORE` | Lykoi definitions, model parsing, deterministic validator/compiler and semantic runtime rules. |
| `PROGRAM_DECLARED` | Specific program source, inputs, durable store, clock/ID providers and explicit capability dependencies. |
| `BUILD_EXECUTION` | Current Python implementation, resolved stdlib/native implementations, actual interpreter controls, filesystem and invocation context. Git is also an execution dependency of this qualification, not of core compilation. |
| `DEVELOPMENT_AUTHORING` | AI providers/models/credentials, OpenCode, ChatGPT, coding agents, editors/IDEs and hosting used to author code. |
| `OPTIONAL_TOOLING` | Benchmark oracle, recorder, lock/Git inspection and development automation relative to language correctness; their implementations are material to an evaluation that actually uses them. |
| `IRRELEVANT` | Unrelated packages, username, hostname, serial, editor choice and undeclared author metadata relative to the scoped computation. |
| `UNKNOWN` | Material dependencies not safely closed or classified. Qualification cannot succeed with these unresolved. |

Categories are computation-relative: the recorder is optional for compiling a
program, but material for certifying an observation. Installed package lists and
provider accounts are not language dependency closure. Python 3.10+ is a declared
support range; the **actual resolved implementation bytes** matter for reproduction.

`OPENAI_API_KEY` and equivalent author credentials are excluded altogether from
core identity, including presence and keyed fingerprints. A synthetic change in
presence/value, model selection, editor metadata or non-material OpenCode config
must not change identity. This exclusion follows inspected imports and real
core-operation equivalence, rather than merely masking an observed difference.
If a tool starts reading such state on the core correctness path, it violates this
policy. An optional non-core integration must declare its own boundary.

## Current implementation and evidence scope

Fresh modules under `benchmark/evaluation/*r5_48.py` do not import or promote the
quarantined R5.46 identity. They reuse the qualified canonical R5.43 protocol,
R5.45 staged-certificate architecture and R5.47 secret-safe publication guard.
The protocol is **`lykoi-execution-state-identity-v2-r5.48`**.

The v2 envelope binds the R5.47 successor identity, scoped repository physical
bytes and membership, committed/index objects and modes, interpreter descriptor,
observed resolved implementation bytes, qualified effective environment controls,
resolved material tools and scoped context. A material change changes this identity.
Only `PYTHONHASHSEED=0`, `PYTHONUTF8=1` and `PYTHONDONTWRITEBYTECODE=1` are currently
qualified public control values. All considered host variable **names** receive a
domain classification; arbitrary names default to UNKNOWN, not presumed irrelevant.

Children receive a sanitized environment, without modifying the development
session. Search/system/temp context is preserved for ordinary execution but
published categorically, not as raw paths or unkeyed fingerprints. That unresolved
material context is a **qualification gap**, not a claimed identity guarantee.
No material secret is needed by the tested core operations. Future material secret
identity must use R5.47 keyed representation with qualified custody/propagation.

Repository slicing includes `src/`, `air/`, `schema/`, `generated/`, `tests/` and
`benchmark/`, including execution-directory ignored/untracked inputs. It excludes
authoring metadata, output-only R5.48 evidence/report and bytecode caches. Cache
exclusion is valid only for the controlled source-based observations; it is **not**
a proof about unrestricted descendant imports. Symlinks/submodules/unmerged
execution inputs are rejected. Committed content is bound rather than incidental
commit authorship. External Git configuration/helper/attribute closure remains
unresolved. This broad research slice is conservative and is not a proven minimal
per-operation production slice.

Observed-host identities carry explicit material UNKNOWN groups and cannot assemble
a production certificate. Closed-fixture tests bind all fixture components, receipts,
recorder/canonical protocol, authority, semantic count, clean contamination and
required historical/prospective/infrastructure locks through the R5.45 policy seal.
Production-shaped synthetic assembly is not production attestation.

## Stages, TOCTOU and limits

The coordinator captures state before a batch/stage, runs a bounded subprocess,
recaptures, and binds PASS to the same identity and mechanism. A mismatch forbids
reusable PASS and quarantines the run. Evidence publication is exclusive and
secret-checked; arbitrary worker stdout/stderr and tracebacks are withheld.
Restricted harness methods preserve the 36 prohibited/historical skips.

Synthetic final checks recapture identity before recorder reservation, reject stale
or mixed evidence, and permit exactly one **synthetic** observation. Equality checks
do not defeat ABA changes, prove immutable native/OS dependencies or establish an
atomic check-and-execute boundary. Production dispatch remains unavailable.

Offline probes use Python `-B -S`, omit real AI credentials and OpenCode, install an
audit hook denying socket connection/DNS/bind and external process/system calls,
validate valid/invalid representations, generate source and execute a read-only
existing application command in a disposable cwd. Direct source imports supplement
dynamic probes. Audit hooks are not a hostile native-code sandbox; these are bounded
current-core observations, not a proof of every possible program or host.

Benchmark correctness remains **observable behavioral equivalence under the frozen
contract**, independently of AI independence. Identical source, generated code,
functions/classes, control flow, storage or architecture are not required.

## Authorization boundary

No B02 reservation, dispatch, CheckedPlan, readiness, audit, admission, static support,
generation, execution or frozen acceptance is permitted. Accidental exposure or
observed material verification drift requires **`R5_48_PROTOCOL_HALT`**, quarantine
and no restart of the frozen stage. Pre-freeze publication construction failures are
recorded separately and convey no verification evidence. The supplied request ends
before its halt/failure classification list; an execution-identity gap is reported
with a separately documented descriptive label, never as qualification success.

R5.43 history and R5.46 permanent halt/quarantine remain preserved. B03 is
prospectively untouched, B17 unexposed/unclassified, Phase 5C paused.
