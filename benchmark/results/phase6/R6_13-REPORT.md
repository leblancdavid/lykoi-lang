# R6.13 — Benchmark validity and scoring repair

**Final classification: `R6_13_SCORING_AND_REPLAY_QUALIFIED`.**

The successor scorer rejects duplicate output keys explicitly and records enforced
process/cooperative session budgets. Unchanged Python candidates pass **152/152
original-suite replay observations** and **98/98 adversarial observations**.
No candidate functional failure, acceptance timeout or scorer error was discovered.
B/C still have no frozen full-task executable; their acceptance remains NOT_REACHED.
New semantic probes narrow some gap claims and expose a naive VM lookup-validation
timeout. This classification qualifies bounded scoring/replay, not independence or
statistical superiority. Historical R6.12 outcomes remain unchanged.

## 1. Baseline and preservation

[Baseline inventory](r6_13/BASELINE-INVENTORY.md) and
[machine identities](r6_13/BASELINE.json) verify original R6.12 FREEZE requirements/
acceptance, publication identities, all eight implementation snapshots and protected
history before scoring repair. VERIFICATION-REVIEW.md was read in full.
Initial Git status included existing uncommitted R6.12 publication/documentation;
no historical result or candidate byte was overwritten.

Historical evidence: **80 base + 24 new modification suite entries**, plus **48
repeated original observations** on modifications = 152 scored observations.
The historical 152-observation replay is another repetition, not distinct inputs.
A had 5/5 tasks and 3/3 changes accepted, first attempts, zero repairs; B/C each
had five base/three change static assessments and zero scored executables.

All **614 protected/history/R6.12 file hashes** match at verification. Production
kernel remains **26**; compiler/lowerer/runtime and R6.10 interpreter unchanged.
P6-A04 acceptance executions 0; P6-A05 not accessed. No scored implementation
repairs, provider calls/dependencies or new language constructs.

## 2. Successor scorer and budget rules

[Protocol](r6_13/PROTOCOL.md), [scorer](r6_13/scorer.py),
[10 regression tests](r6_13/test_scorer.py), [checks](r6_13/CHECKS.json).
Version `r6.13-scorer-1`:

- Duplicate object keys reject at every depth, including escaped equivalent keys;
  no overwrite. Invalid/nonfinite/trailing output and invalid UTF-8 reject explicitly.
- Exact JSON comparison ignores object-key order, preserves array order and numeric/
  Boolean types, rejects extra fields and nonzero exit. Identical A/B/C rule.
- Candidate mismatch, timeout, launch error and scorer error have separate statuses;
  raw stdout/stderr/return codes and UTC start/completion/monotonic duration retained.
- Replay: **10 seconds/process**, **900 seconds/replay session**. Direct child kill/
  wait through subprocess.run; remaining session time limits each launch, prevents
  further dispatch and rejects beyond-deadline completion. Not descendant/AI-session
  containment; cleanup/detection can overshoot. Actual timeout regression tests pass.
- Per-task development budget **N/A**: no new authoring trials. Historical 900-second
  task and 4500/2700-second session limits retain their original partly observational
  enforcement status. No retroactive budget relabeling or historical scorer edits.

## 3. Adversarial suite freeze and denominators

[Acceptance manifest](r6_13/ADVERSARIAL-1.json),
[freeze identities](r6_13/FREEZE.json), [fixture preparation](r6_13/prepare_suite.py).
Version `r6.13-adversarial-1`, frozen before any candidate run. Each entry has an ID,
explicit expected behavior and contract-based rationale. Original cases unchanged.

| Task | Base entries | Modification entries | Main added challenge |
| --- | ---: | ---: | --- |
| T1 | 10 | 6 | Eight SKUs/16 operations, max units, IDs, interleaving/history, validation precedence, repeated resize |
| T2 | 10 | — | Seven independent jobs/5040 schedules, weighted optimum, lexical ties, deadline63, cycles/phase interactions |
| T3 | 10 | 6 | Eight records/64 payload bytes, repeated-byte sorting, missing fields/error precedence, exact8 merge/split-then-merge |
| T4 | 10 | 6 | Sixteen patches/160-byte assembly, pair (0,2) precedence, skipped overlaps, original-coordinate/absent interactions |
| T5 | 10 | — | Six rounds,12 ballots/max weight9, transfers/exhaustion, strict half, duplicate/malformed phase ordering |
| Total | **50** | **18** | **68 suite entries** |

[Exact input accounting](r6_13/INPUT-ACCOUNTING.json) identifies **three entries
already in the original suite**: T3 tag-with-length, T3 length-before-truncated,
T5 shape-before-duplicate. They remain deliberate repeat evidence; suite is frozen
and was not rewritten after replay. Thus **65 task inputs are additional**, not 68.
Modification snapshots also repeat 30 successor base cases: **98 observations =
50 base + 18 modification + 30 repeats**. Duplicate *domain* IDs are tested;
duplicate input-object keys/transport-invalid JSON remain outside the contract.

## 4. Frozen-candidate results, kept separate

[Replay start](r6_13/REPLAY-START.json) binds the driver/scorer/freeze before execution;
[raw replay](r6_13/REPLAY.json) records each observation and candidate identities
checked immediately before/after its runs. Fresh process per case.

| A snapshot | Original base replay | Original new replay | Adversarial base | Adversarial modification |
| --- | ---: | ---: | ---: | ---: |
| T1 base | 15/15 | — | 10/10 | — |
| T1 modified | 15/15 repeated | 8/8 | 10/10 repeated | 6/6 |
| T2 base | 17/17 | — | 10/10 | — |
| T3 base | 17/17 | — | 10/10 | — |
| T3 modified | 17/17 repeated | 8/8 | 10/10 repeated | 6/6 |
| T4 base | 16/16 | — | 10/10 | — |
| T4 modified | 16/16 repeated | 8/8 | 10/10 repeated | 6/6 |
| T5 base | 15/15 | — | 10/10 | — |

- Original replay: **80 base, 24 new, 48 repeated** all pass. Zero observed original
  regressions on modified snapshots; these are replay observations, not new authoring.
- Adversarial: **68 entries and 30 repeats** all pass; zero observed base-suite
  differences on modified snapshots. Three entry overlaps disclosed above.
- Scorer errors **0**, candidate failures **0**, acceptance timeouts **0**.
- B/C each: original **152 NOT_REACHED** and adversarial **98 NOT_REACHED** positions,
  with per-stage GAP/CAPABILITY identity records. No observed acceptance failures or
  regression rate inferred from missing executables. No undifferentiated A/B/C score.

## 5. Capability reassessment and negative evidence

[Reassessment](r6_13/CAPABILITY-REASSESSMENT.md) distinguishes precise missing input,
state, search, raw-byte/assembly and grouped-result bindings from useful compositions.
Confidence is high for inspected closed direct interfaces, lower for any exhaustive
noncomposition claim. No abstract impossibility or minimum-construct proof.

Separate frozen partial probes on unchanged implementations:

- B request-record collection and direct XOR/slice/permutations constructions reject.
  NOT equality validates and runs **3/3** predicate observations; absent is not a
  missing Boolean meaning. No complete production compilation attempted.
- C direct XOR/slice expressions reject; seven-node map probe confirms original,
  inclusive prefixes rather than prior computed results.
- C **21-node nibble XOR passes all 256 pairs**, rejecting out-of-domain input. A
  finite relation can compose without a dedicated XOR opcode. This narrows the
  earlier naive lookup reasoning; full byte normalization still unconstructed.
- Naive full-byte lookup has 261 authored structural nodes (over64); individually
  supervised execution **times out at 10 seconds before a validator response**.
  The initial combined probe invocation had already been interrupted by the terminal
  tool after 120 seconds without published observations; preserved separately in
  [interruption evidence](r6_13/PROBE-INTERRUPTION.md). Later method2 changes execution
  supervision only and is not described as first-attempt success.

Newly discovered limitation: excessive validation-path time for that large lookup
construction; no scored A functional defect. VM validation lies outside charged
runtime work. Timeout does not establish all full-byte XOR strategies impossible.
No full-task B/C success or failed full-task executable is demonstrated by these probes.

## 6. Comparative conclusion and validity

**The practical Python coverage conclusion on this batch does not change.** It now
has stronger finite boundary/adversarial evidence under repaired scoring. B/C remain
current-interface/static composition gaps, with affirmative partial capabilities
and narrowed confidence about finite XOR. No matched-success set exists, so the
development-efficiency question remains unanswered. Replay seconds are not authoring
effort. **Token usage, authoring time and repair efficiency have not been remeasured**;
historical exported tokens/billing limitations remain as recorded.

Here and in the frozen protocol, "no new authoring trials" means no new scored
full-task AI development assignment. The exploratory partial probe plans were newly
authored in this session; their preparation effort was not isolated or metered as
an efficiency trial. Their later execution supervision is explicitly versioned.

[Threats to validity](r6_13/THREATS-TO-VALIDITY.md) documents same-model correlation,
synthetic nonindependent sourcing, known implementation exposure, finite suite/input
repeats, scorer changes, hard-enforcement gaps, missing initial probe completion data
and capability uncertainty. No independent qualification, general language superiority
or statistical significance is claimed.

Verification: **10 scorer + 116 baseline methods pass**, production validation/safety
pass, protected identities match, `git diff --check` passes. Baseline methods comprise
22 compiler, 9 application, 3 historical baseline and 82 VM tests, not task acceptance.
Final publication checks and file identities are in
[PUBLICATION-CHECKS.json](r6_13/PUBLICATION-CHECKS.json) and
[PUBLICATION-IDENTITIES.json](r6_13/PUBLICATION-IDENTITIES.json).

## 7. Recommended next development experiment and stop

Separately authorize a **generic finite-relation/typed result-binding construction
challenge** on the unchanged VM first: prefreeze small relations beyond XOR and a
candidate bit/nibble decomposition for full UInt8 XOR, record structural nodes,
selector growth, validation wall time, runtime work and negative attempts under
process/session limits. Establish which parts compose before proposing a general
typed accumulator/index/slice/result interface. Independently review contracts and
expected outputs; no benchmark-specific opcode or automatic interpreter repair.

A later comparative authoring experiment should use independently supplied tasks
including whole tasks supported by all tracks, prospectively instrumented repeated
authoring trials and real budget supervision. That would measure matched successful
effort; this replay cannot. Neither experiment is authorized by this publication.

**Stopped after scorer, acceptance replay and capability reassessment publication.
Await explicit owner authorization before further benchmark or language work.**
