# R6.13 baseline inventory

Verified before scoring/suite changes: R6.12 FREEZE requirements and acceptance
identities, PUBLICATION-IDENTITIES (including all eight A candidates), RESULT-1
artifact hashes, and all protected production/VM/history identities. Machine
evidence: BASELINE.json. All checks matched. VERIFICATION-REVIEW.md read in full.
The initial worktree already contained the uncommitted R6.12 publication; it is
preserved byte-for-byte, along with the other protected historical evidence.

## Denominators and original execution

- Base observations: T1 15, T2 17, T3 17, T4 16, T5 15 = **80**.
- New modification observations: T1/T3/T4 8 each = **24**.
- Modification runs repeat **48 original observations** (15+17+16).
- Historical scoring: **152 observations**, comprising 104 explicit suite entries
  plus 48 repeats. The separate historical replay repeats those same 152
  observations. Neither repetition adds distinct inputs or independent trials.
- Eight Python RESULT-1 records passed, zero repairs, no observed regressions.
  Fresh subprocess per case, CPython standard library, 10-second timeout.
- A: 5/5 base and 3/3 changes executed successfully on the finite original suites.
- B: production, 5 base/3 change static CAPABILITY_GAP assessments; no executable.
- C: frozen VM, 5 base/3 change static CAPABILITY_GAP assessments; no executable.
  B/C acceptance is NOT_REACHED, not 80+72 executed failures per track.

## Known measurement limits

Ordinary json.loads silently collapses duplicate output keys. Canonical JSON
comparison preserves array order and distinguishes integer/float/bool. Development
900-second limit checked only before evaluation (gap recording also checks elapsed);
final duration measured retrospectively. 4500/2700-second session limits not actively
enforced. 10-second subprocess limit enforced by subprocess.run. No observed
historical overrun or affected duplicate-key outcome was found. Expectations and
historical results will not be reclassified under prospective enforcement.

Coverage omissions: malformed nested shapes, maximum-size/interacting inputs,
phase/pair precedence, ordering, T1 interleaving/resize, T2 seven-job optimization,
T3 cap-driven coalescing, T4 maximum assembly, T5 six rounds/max ballots.
Same-model review, synthetic sourcing, known candidate exposure, absent B/C
matched success, late tokens and unavailable billing preclude qualification or
development-efficiency ranking. Static interface gaps are not impossibility proofs.
