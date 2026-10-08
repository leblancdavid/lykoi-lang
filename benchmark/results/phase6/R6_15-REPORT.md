# R6.15 — AI authoring efficiency challenge

**Final classification: `R6_15_EXPLORATORY_COMPARISON_ONLY`.**

Conventional Python passes **4/4 fresh tasks** and **2/2 staged extensions**.
The unchanged R6.10 experimental VM passes **3/4 tasks** and **1/2 extensions**.
Actual exported per-call token metadata is available for all six authoring sessions;
API billing, independently controlled separation and reasoning configuration are not.
The staged comparison is **CONTAMINATED_UNENFORCED**: no premature-access markers
observed, but disclosure restrictions could not be enforced independently. This is
bounded exploratory evidence, not a completed controlled/instrumented comparison.

## 1. Baseline, scope and pre-author freezes

The owner's R6.15 request authorizes A (standard-library Python) and C (explicit
semantic plans), including unsuccessful attempts. Production Lykoi is not scored.
[Baseline](r6_15/BASELINE.json) verifies kernel **26**, **687 protected/history
identities**, frozen R6.10 publication and R6.14 preservation/publication identities.
VM SHA256 remains `bf5dbfb96d6d50124d109c35804c81e5a27bf4038b7f65b1a909ad4f0cc13fa3`.
Initial Git status was clean. A first baseline-helper check encountered old R6.10
guidance hashes superseded by later publications; executable/dedicated experiment
identities were verified separately, and the helper was corrected before baseline
recording/task selection. This was not a scored attempt or historical file repair.

Before selection, [protocol](r6_15/PROTOCOL.md) froze600-second cooperative session
deadlines,20-tool budgets, initial candidate plus one optional self-test repair per
task, at most two development test batches/task capped30s, and scored children30s.
All sessions stayed within budgets. No candidate repairs or post-handoff changes;
one pre-candidate modification-builder syntax correction is separately disclosed.

Identifier-only `opencode models --pure` inventory and targeted historical-own-session
export probe established token metadata availability before selection. Listed models
are not credential/routing qualification. All scored exports subsequently identify
**openai/gpt-6.1-sol**. Harness-default reasoning is shared by instruction but not
independently attested. Scripts are standard-library/provider-neutral; no provider
SDK, credential publication, production/VM changes or new semantic operations.

[Task freeze](r6_15/TASK-FREEZE.json) binds common interface, provenance/contracts,
explicit observations and preparation oracle before author dispatch. [Separate seal](r6_15/MODIFICATION-SEAL.json)
binds two changes before base authoring. [Reveal](r6_15/MODIFICATION-REVEAL.json)
occurs after every original submission is frozen. Reserved mode/version2 has no base
expectation; extension does not supersede any original acceptance observation.

## 2. Selection, sessions and functional results

Four coordinator-authored synthetic contracts: saturation/calibration, ordered run
expansion, ordered disjoint-window validation, bounded delimiter nesting. Prior R6.11/12
contracts were read for duplicate avoidance; no historical scored source was supplied
to authors. No CFG66/DSV66/BXC66/XOR8/addmod8/byte-parity task reuse. These tasks did
not design the VM. Selection is implementation-aware, nonrandom and favors bounded
byte inputs; it is not externally sourced or development-unexposed generalization.

Fresh contexts, counterbalanced waves: A(T1,T3)/C(T2,T4), then C(T1,T3)/A(T2,T4).
Fresh modification contexts receive only their own original source/plans and released
change contracts, C dispatched first. No other-track code or scored feedback supplied.
Filesystem restrictions are cooperative; inherited AGENTS.md includes historical
findings. [Access audit](r6_15/ACCESS-AUDIT.json) and author disclosures find no forbidden
argument markers, but do not attest hidden context or enforced withholding.

| Task | Frozen unique observations | Python A | VM C | First-attempt outcome |
| --- | ---: | --- | --- | --- |
| T1 saturating calibration | 348 | 348/348 | 348/348 | Both accepted |
| T2 ordered run expansion | 59 | 59/59 | **24/59** | A accepted; C incomplete |
| T3 ordered disjoint windows | 139 | 139/139 | 139/139 | Both accepted |
| T4 bounded nesting | 519 | 519/519 | 519/519 | Both accepted |
| **Overall** | **1,065 per track** | **4/4 tasks;1,065/1,065** | **3/4 tasks;1,030/1,065** | Failures retained |

Each observation executes three times; these are deterministic repeats, not extra
coverage. Type-sensitive comparison checks exact fields, integer/Boolean distinction,
ordering, bytes and error offsets. All observations are deterministic, including C's
wrong T2 rejections. T4 covers all511 '(' / ')' strings of length0..8 plus8 directed
adversarial inputs. Other task domains are sampled, not exhaustive. Author-chosen
self-test counts differ and are not added to the common acceptance denominator.

All first/final candidates are byte-identical, frozen before tests and scored handoff.
Results: [original summary](r6_15/BASE-RESULTS.json), [raw observations](r6_15/results/),
[comparison](r6_15/COMPARISON.json). Python files: `r6_15/A/base/`; explicit VM plans:
`r6_15/C/base/`; immutable first candidates: each track's `first/`. Authoring builders
produce JSON data only and are never imported by VM execution.

### Failure versus capability limitation

C/T2 is a **valid but incomplete semantic plan**, not validator/interpreter failure.
It deliberately rejects counts2..4 with noncontract `AUTHORING_UNSUPPORTED`, failing35
observations. [Capability analysis](r6_15/CAPABILITY-ANALYSIS.md) preserves a qualified
static native-list growth argument: a17-byte input needs list32, while existing list
origins are bounded by consuming repetition or default8-item traversals and have no
flatten/concatenate expression. This is specific, same-agent/unreviewed interface
analysis, not abstract Lykoi impossibility. Scored failure and supported capability
limitation are separately reported. No central computation is delegated to a host
adapter, callback or opaque implementation. No scored PlanError, runtime crash,
infrastructure failure or timeout occurred.

## 3. Actual AI effort

[Base telemetry](r6_15/BASE-TELEMETRY.json) and [modification telemetry](r6_15/MODIFIED-TELEMETRY.json)
retain actual per-call fields, identities/timestamps and tool timing. Input is the
exported input field; cache reads are reported separately. Reasoning/output fields
remain separate, without inferred billing units or source-length token estimates.
Every export reports cost0, but **actual API cost is unavailable**, not established
as free. Cache writes0 throughout. Coordinator preparation/publication usage is
unavailable/unallocated and excluded; author records' local token-null fields are
supplemented by recovered telemetry, not overwritten.

| Session scope | Input | Output | Reasoning | Cache read | Model calls | Development wall s | Tool elapsed sum s |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| A T1+T3, both accepted | 53,693 | 5,497 | 492 | 380,160 | 9 | 132.800 | 2.423 |
| C T1+T3, both accepted | 51,046 | 12,184 | 3,576 | 819,584 | 12 | 410.874 | 15.385 |
| A T2+T4, both accepted | 54,700 | 6,053 | 618 | 380,544 | 9 | 154.230 | 3.926 |
| C T2+T4, one accepted | 78,088 | 7,278 | 4,806 | 654,336 | 11 | 313.598 | 3.411 |
| A modifications T1+T2 | 56,916 | 6,296 | 419 | 806,272 | 18 | 161.041 | 2.500 |
| C modifications T1+T2 | 88,648 | 4,611 | 1,648 | 781,568 | 16 | 193.399 | 2.088 |

Wall durations span first assistant created→final completed, including reads,
development/self-tests, record writing and handoff; they are not provider inference-only
or exact first-tool budgets. Audit separately records first-tool→last-tool durations,
all below600s. Tool elapsed sums can overlap when calls are parallel; they are not
wall-time decomposition. Exported tool parts11/16/17/11/17/19 are within20; authors'
modification self-counts18/20 differ by one under harness representation. Actual
metadata and original self-disclosures are both retained, not silently reconciled.

**Primary matched-success comparison: T1+T3 only.** Python's session wall was about
**3.09x shorter**, with fewer output/reasoning/cache-read tokens and model calls.
Its uncached input field was slightly **higher**, so there is no across-the-board token
reduction. Both tasks are accepted for both tracks. T4 effort cannot be isolated from
the paired failed C/T2 attempt; no source-size allocation of session usage is made.
Failed/mixed sessions are fully reported but excluded from primary accepted-efficiency
ranking. These finite observations favor Python for this accepted pair, not a controlled
causal or general superiority result. No cost-efficiency comparison is justified.

## 4. Staged modification results

M1 adds mode2 superboost; M2 adds version2 delimiters after nonempty expanded runs.
Original artifacts are immutable; revisions and first revision snapshots are separate
under `modified/` and `mod-first/`. [Revision freeze](r6_15/MODIFIED-FREEZE.json),
[results](r6_15/MODIFIED-RESULTS.json) and author `AUTHORING-MOD.json` records retain
all outcomes. First revision equals final revision; no candidate repairs.

| Change | A original / new | C original / new | Accepted modifications | Passing→failing regressions |
| --- | --- | --- | --- | --- |
| M1 calibration | 348/348;53/53 | 348/348;53/53 | Both | 0 each |
| M2 run delimiters | 59/59;22/22 | **24/59;8/22** | A only | 0 each |

No original observable result changed, including C/T2's existing wrong rejections.
Thus zero regressions does not make the incomplete C implementation correct.
Version2 adds14 failing observations for C. Both modification effort sessions include
T2, so no isolated matched-success M1 token/time efficiency claim is available.
**Modification comparison remains contaminated by unenforced staged disclosure**;
chronological sealing/reveal and no observed reads are useful evidence, not containment.

## 5. Representation and execution complexity

Canonical bytes use sorted compact JSON; published bytes preserve authors' formatting.
Standalone validation: five timings, traversal profiling in a separate untimed run.
Public `execute` validates on every call. Runtime sums below include three repeats
of the entire acceptance mix, including rejections; common>64 boundary bypasses VM
and has no VM work. These are not validate-once throughput benchmarks.

| Base task | Python bytes / function-if-loop counts | VM nodes | VM canonical / published bytes | Validation walks / expr visits / selector comparisons | Median validation ms | VM work range, successful or rejected |
| --- | --- | ---: | --- | --- | ---: | --- |
| T1 | 826 / 1-5-0 | 16 | 1,343 / 1,344 | 16 /22 /1 | 0.0442 | 2–39 |
| T2, C incomplete | 978 /1-6-1 | 14 | 1,236 /3,543 | 14 /21 /0 | 0.0587 | 2–131 |
| T3 | 1,239 /1-7-1 plus1 comprehension | 59 | 6,319 /6,320 | 59 /95 /32,640 | 4.1315 | 12–432 |
| T4 | 964 /1-7-1 | 20 | 2,214 /7,764 | 20 /60 /0 | 0.0614 | 19–595 |

Python branch/loop/function counts are AST observations, not cyclomatic-complexity
proofs or equivalents of semantic nodes. Python runtimes include `solve` envelope/hex
construction; C includes public validation/execute plus common projection. All-case
runtime sums A/C respectively: T1 **0.000748/0.065884s**, T2 **0.000163/0.010335s**,
T3 **0.000366/1.832023s**, T4 **0.000946/0.228830s**. Different outcome mixes and
tiny Python times/host noise prevent treating these as stable speedup estimates.
Scored child wall times additionally include startup, JSON/result recording and
separate validation profiling; see raw records. Full per-observation work/time and
modified structural metrics are retained in COMPARISON.json/raw results.

T1 extension adds1 VM node (16→17) and canonical97 bytes, versus Python6 bytes.
T3's59/64-node explicit lookahead is close to the bound and selector-heavy. T4's
prefix-cardinality state representation is indirect but accepted. T2 highlights
native flat-list representation friction. Maintainability has only two bounded change
observations, not independent readability, general repair or long-term maintenance
measurement. Structural metrics are not interchangeable authoring-effort units.

## 6. Threats to validity, preservation and next step

- Four synthetic, implementation-aware tasks; no randomized/independent sourcing.
- Coordinator-authored contracts/oracle, correlated interpretations; sampled domains
  except finite T4 delimiter strings. Scorer-integrity tests challenge selected cases.
- Fresh contexts share filesystem, inherited research guidance, tools and provider.
  No OS/provider isolation or equivalent reasoning/routing attestation. Task pairing
  permits within-track learning; counterbalancing only partially controls order.
- Budgets equal, but development test volume varies. Cooperative model deadlines;
  no hard whole-session interruption. Six actual sessions, no replicated authors.
- Token metadata includes inherited guidance, documentation, tooling and logging;
  task-group attribution only. API billing and coordinator usage unavailable.
- Staged modifications are intentionally classified contaminated. Two small changes
  do not establish broader maintainability; failed attempts remain reported.
- Single Windows/CPython host, no affinity/idle-host guarantee; profiling separate,
  very short call timings and different wrappers limit runtime comparison.

[Verification](r6_15/PUBLICATION-CHECKS.json) records relevant regressions, scoring
checks, production model validate/safety, preserved687 identities and git diff --check
plus untracked-file whitespace checks. [Publication identities](r6_15/PUBLICATION-IDENTITIES.json)
bind all new artifacts/report and additive current guidance. Historical R6.3–R6.14,
the original XOR8 Take rejection/repair/naive timeout, production compiler/lowerer/runtime
and VM bytes remain preserved. Historical publication manifests are unchanged; their
entry-point guidance hashes describe their original publication, not newly updated
R6.15 guidance. P6-A04 acceptance executions0; P6-A05 not accessed. Incidental Python
bytecode caching in one author session is disclosed; protected source hashes match.

**Evidence supports a local exploratory Python advantage** in base success rate and
effort on the fully accepted T1/T3 pair. It does not establish universal superiority,
controlled matched-task cost efficiency, independent qualification or an advantage
for Lykoi. The VM does demonstrate successful explicit composition on three fresh
contracts without language changes, while its unsuccessful list-valued task remains
visible. No Lykoi implementation changes follow these outcomes.

**Recommended next experiment:** separately authorize independently selected source
contracts, task-level isolated sessions with pinned reasoning/routing, auditable
restricted input packages and enforced modification withholding, complete usage/billing,
replicated authors and identical testing opportunities. Use the same frozen VM; include
failed/capability-limited tasks and a byte-output versus native-list interface distinction
as a predeclared variable, not an after-failure repair or hidden task-computing adapter.

**Stopped after bounded comparison and publication. Await explicit owner authorization
before further experiments, replay or Lykoi changes.**
