# R5.95A — Runtime Recovery and B03 Authorization Continuation

## Result

**`R5_95A_FROZEN_RUNTIME_ARTIFACT_UNAVAILABLE`**. A general-project-compatible
CPython runtime exists, but it does not satisfy the exact R5.94 runtime pins.
Stop before activation, opaque target identification and authorization. No B03
access occurred. R5.95's historical result is preserved unchanged.

## Read-only runtime discovery

`py --list-paths` reports one registered runtime:

```text
C:\Users\lblan\AppData\Local\Python\pythoncore-3.14-64\python.exe
CPython 3.14.3 (tags/v3.14.3:323c59a, Feb 3 2026)
MSC v.1944, 64-bit AMD64
```

Direct execution with `-B` confirms the exact version, implementation and 64-bit
architecture. `Test-Path` confirms the historical temporary executable is absent.
Dedicated file discovery searched Local/Python, Local/Programs/Python*, the approved
temporary OpenCode directory, Program Files/Python* and C:/Python*. Only the registered
3.14 executable and Local/Python/bin/python.exe entry matched. No matching frozen
3.12.10 runtime was found. This is likely-location discovery, not an exhaustive
machine-wide search. No software installation or environment modification occurred
in R5.95A.

## Compatibility versus frozen identity

CPython 3.14.3 meets the repository's ordinary Python 3.10+ requirement. The freeze,
however, explicitly selects stronger runtime identity:

- `src/lykoi_rehearsal/freeze.py:28–35` records `sys.version`, the SHA-256 of
  `sys.executable`, and the installed Python DLL/ZIP library hashes.
- `src/lykoi_protected/freeze.py:42–45` requires the entire recorded body to equal
  a fresh snapshot. The public R5.91 layer retains those runtime fields.
- `ProtectedController.require_active()` and protected activation use that same
  integrity predicate. A report-only declaration of compatibility cannot bypass it.

The **historical Python pathname is not authoritative**: it is absent from these
runtime identity fields. The same exact runtime artifacts at a different location
could satisfy them. CPython 3.14.3 cannot: direct read-only comparison shows all
three runtime bindings differ (version string, executable hash, library set/hashes).
Exact expected and observed values are in [runtime-recovery.json](r5_95a/runtime-recovery.json).

The required artifacts are CPython **3.12.10, Windows AMD64**, with executable
`4d6f5f81a4bca11191c4c7c6b43632694d0a4ce74e068619d8fdc161d469859a`,
`python312.dll` and `python312.zip` matching the recorded hashes and exact version
string. Merely installing any Python 3.12.10 distribution is not sufficient proof.
Human recovery of the pinned runtime is required before a separately instructed
verification/authorization continuation. No installation, snapshot substitution,
pin change, monkeypatch or machinery repair was attempted.

## Verification and authorization deliverables

The existing candidate record's canonical self-digest was freshly recomputed with
the available interpreter and matches:

```text
f19c6dab34128813558a636e37d1f8c2ff109c45cd82172ab561712ba192f77e
```

This verifies the record's self-binding only, **not full current snapshot integrity**.
Full R5.94 verification was not executed because the frozen-runtime prerequisite
was demonstrably unmet. No fresh component/evidence/controller verification success
is claimed. Initial Git status contained only the preserved R5.95 documentation and
stopped evidence from this session.

| Deliverable | Status |
| --- | --- |
| Runtime recovery evidence | Existing CPython 3.14.3 identified and executed read-only |
| Runtime compatibility determination | General project compatible; exact freeze incompatible |
| Fresh freeze verification | Record self-digest matches; full verification not executed |
| Protected activation receipt/revision | None created |
| Exact B03 authorization | None created |
| Single-use/non-transferability evidence | No new checks; no authorization exists |
| Pre-run eligibility | Not executed; prerequisites unmet |
| Zero-access evidence | Scoped zero counters in machine evidence plus inherited state |
| Continuation report | This report |

No protected controller database was created. B03's opaque registry identity was
not retrieved; no source, content hash, package or content-revealing metadata was
inspected. Source opens, reads, admissions, formalizer/reviewer/author/verifier
deliveries and development exposures are all zero. Authorizations are also zero.
Inherited pristine/unevaluated/unexposed status remains; this is not an independent
protected-ledger audit. Historical evidence and all frozen semantics, mappings,
BDI, adequacy, prompts, models and verification behavior remain unchanged.

## Completion answers

1. CPython 3.14.3 Windows AMD64 at the path above was used for read-only discovery
   and pin comparison, not for a frozen evaluation.
2. General compatibility was established without machinery changes; exact frozen
   runtime compatibility failed.
3. No full fresh R5.94 verification pass; only candidate-record self-digest matches.
4. No protected activation was created.
5. No B03 authorization was created.
6. No actual authorization exists to certify as single-use/non-transferable.
7. No pre-run eligibility pass; the check was not executed.
8. B03 remains inherited pristine, not evaluated and not development-exposed.
9. Every scoped source/delivery/exposure counter remains zero.
10. R5.96 is not authorized to consume a run. Stop before B03 access.
