# R5.95 — B03 Protected Evaluation Authorization

## Classification

**`R5_95_AUTHORIZATION_BLOCKED_DESIGNATED_RUNTIME_UNAVAILABLE`**.

The mandatory frozen-candidate verification could not start: PowerShell could not
resolve the designated CPython 3.12.10 executable. This is an operational
verification blocker, not evidence that the candidate's contents fail integrity.
R5.95 stops before activation and before target identification/authorization.

## Frozen candidate and verification attempt

Candidate: **`R5.94-GENERIC-PROTECTED-CANDIDATE-1`**.

Recorded exact identity, read from the existing freeze record (not freshly verified):

```text
f19c6dab34128813558a636e37d1f8c2ff109c45cd82172ab561712ba192f77e
```

The R5.94 report designates the following read-only check, attempted from the
repository root on 2026-10-06:

```powershell
& "C:\Users\lblan\AppData\Local\Temp\opencode\python312\python.exe" -B -c "import sys,runpy; sys.path[:0]=['src','.']; sys.argv=['rehearsal/validate_r5_94.py','check']; runpy.run_path('rehearsal/validate_r5_94.py',run_name='__main__')"
```

Observed shell error:

```text
&: The term 'C:\Users\lblan\AppData\Local\Temp\opencode\python312\python.exe' is not recognized as a name of a cmdlet, function, script file, or executable program.
Check the spelling of the name, or if a path was included, verify that the path is correct and try again.
```

Python did not start. Component/evidence bindings, runtime pins, protected provenance,
activation machinery, role visibility, accounting, semantic/model/configuration pins
and verification machinery therefore have **no fresh mechanical verification** in
R5.95. Initial `git status --short` was clean. Existing candidate/interface records
were read for orientation; this does not substitute for the frozen check.

No runtime installation, replacement runtime, repair, retry, semantic change or
pipeline change followed. Historical R5.91, R5.92A, R5.93 and R5.94 evidence is preserved.

## Deliverable status and pre-access evidence

| Requested item | R5.95 result |
| --- | --- |
| Active protected freeze receipt | Not created; candidate remains inactive by inherited R5.94 state and no activation in this round |
| Exact freeze identity | Recorded above; fresh verification blocked |
| B03 single-run authorization identity | Not created |
| Bound role-policy identity | No authorization binding created; existing policy unchanged |
| Pre-access state | Inherited pristine/unevaluated/unexposed; not `AUTHORIZED_NOT_ACCESSED` |
| Single-use/non-transferability evidence | Existing R5.94 synthetic evidence preserved; no new mechanical checks run |
| Pre-run eligibility | Not executed; authorization prerequisite unmet |
| Authorization report | This stopped report and [machine state](r5_95/authorization-blocker.json) |

B03 was not identified from a protected registry, opened, read, hashed, packaged,
admitted or delivered to any role. No content-revealing metadata was inspected and
no AI/provider request was made. All R5.95 actual source/exposure counters are zero;
authorizations are also zero. The counter basis is inherited R5.94 zero/pristine
evidence plus the operations of this session, **not an independent protected-ledger
audit**. No protected controller store was created or consumed.

## Completion answers

1. No R5.94 protected freeze was activated.
2. The inactive candidate's recorded exact identity is the digest above.
3. No B03 single-run authorization identity exists from this round.
4. No authorization journal revision exists; no controller operation ran.
5. No opaque B03 binding was created; B03 was not read.
6. No actual authorization exists to certify as single-use/non-transferable.
7. B03 retains inherited `B03_PRISTINE`, `B03_NOT_EVALUATED` and
   `B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT`; no contamination transition occurred.
8. All scoped source opens/reads/admissions and role/development exposures remain zero.
9. Pre-run eligibility does not pass: it was not executed and no activation or
   authorization exists.
10. Evaluation is not eligible. A separately instructed continuation must address
    the runtime blocker and complete frozen verification/authorization before any
    evaluation can begin. R5.95 ends here without accessing B03.
