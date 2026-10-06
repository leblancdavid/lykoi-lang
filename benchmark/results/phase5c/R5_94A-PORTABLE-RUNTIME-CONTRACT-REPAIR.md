# R5.94A — Portable runtime contract repair

## Outcome

**`R5_94A_GENERIC_FREEZE_BLOCKED_EXACT_NON_PYTHON_DEPENDENCY_DRIFT`**.

Python compatibility/provenance separation is implemented and CPython **3.14.3
AMD64 qualifies mechanically**. However, the requested eligible generic freeze
cannot be established while retaining the inherited exact dependencies on this
computer. Do not treat this round as authorization-ready or as a successfully
verified successor to R5.94. The blocker is **not Python incompatibility** and
does not require recovering CPython 3.12.10.

The explicit integrity audit found **101 inherited file-byte mismatches**, all
explained by LF/CRLF representations in either direction. This diagnostic does
not satisfy or weaken their physical-byte pins. The model-configured OpenCode
path contains **1.18.32**, while the inherited freeze binds **1.1.25**:

| Artifact | SHA-256 |
| --- | --- |
| Expected OpenCode | `0a30852198eb8114ad3a9e9c6d04fdbfe263af8c154b9efb48d0480af0b6bf63` |
| Actual OpenCode | `cf664aa1da32b788f9b2699b84a9bb9be30b7e025693b90f9b85829d5fe4e252` |

OpenCode executes the frozen role/configuration interface; no behavioral
replacement contract for it has been established. Accepting that replacement,
revising model configuration, or relaxing the inherited byte pins would exceed
this Python-contract repair. None occurred. No installation or executable
replacement was attempted.

## Implemented deliverables

1. [Dependency classification](r5_94a/candidate-2/dependency-classification.json)
   enumerates every exact file pin and distinguishes Python compatibility and
   provenance. [Contract documentation](../../../docs/python-runtime-contract-v1.md)
   explains the architecture-specific classification, including OpenCode.
2. [`PYTHON_RUNTIME_CONTRACT_V1`](../../../rehearsal/python-runtime-contract-v1.json)
   requires CPython 3.10+, 64-bit Windows/Linux/macOS as prerequisites, no assumed
   upper version bound, and the bounded behaviors listed below. Platforms other
   than this Windows AMD64 machine are not demonstrated by this round.
3. `src/lykoi_runtime/verify.py` implements deterministic structured qualification.
   It explicitly selects ordinary synthetic tests, never discovers benchmark
   requirements or invokes an AI/provider. Qualification takes seconds, not the
   entire historical suite. Unavailable interpreters return structured failure.
4. Qualification receipts retain exact implementation/version/architecture,
   executable path/SHA-256, available Python DLL/ZIP hashes and SQLite version.
5. Selection precedence is explicit `--interpreter`, `LYKOI_PYTHON`, then the
   interpreter executing the command. `--current` qualifies that executing
   process's runtime. No globally configured `python` command is needed.
6. [Final CPython 3.14.3 result](r5_94a/candidate-2/qualification.json):
   **`RUNTIME_COMPATIBLE`**, all checks pass, **41 existing tests** pass.
7. [Historical comparison](r5_94a/comparison-final/historical-comparison.json)
   records bounded synthetic invariance against preserved 3.12.10 evidence.
8. `portable_freeze.py` binds the exact contract/procedure/test identities instead
   of Python version/executable/library hashes. All inherited semantic pins,
   model configurations, prompts, mappings, BDI, adequacy and verification remain.
9. `PortableProtectedController` replaces only the private protected integrity
   dependency and per-run `tools` runtime identity. New controller processes
   qualify their actual `sys.executable` before use; artifact drift within a
   process forces independent requalification before dispatch. Existing child
   compiler/application/containment workers use the same `sys.executable`.
10. Each operation gets a separate adjacent append-only runtime provenance receipt
    in the same journal transaction. Original event evidence (including authority
    artifact-ID strings), artifact payloads and semantic identities are unchanged.

These establish the runtime-contract implementation component. The full requested
success classification is withheld because the production generic freeze did not
verify, and therefore cannot supersede R5.94 for eligible protected evaluation yet.

## Required bounded behavior

The contract checks implementation/version/platform/word size and required stdlib
availability; SHA-256 standard vectors; exact CJ-1 UTF-8 serialization, canonical
artifact identity and malformed/duplicate/nonfinite/float rejection; SQLite
`BEGIN IMMEDIATE`, rollback, committed Unicode data and separate-process restart;
Unicode/space filenames, exclusive creation, atomic replacement, `resolve` and
`is_relative_to`; subprocess argument boundaries, UTF-8 pipes, nonzero status and
timeout; deterministic controller identities/transitions, persistence and corrupt
journal/artifact detection; workspace serialization/restart; existing audit-hook
file/network containment; additional process/native/system audit denial; and all
current compiler/application tests. POSIX additionally requires `resource`.

No version-number-only acceptance occurs. No universal Python-version invariance,
provider/TLS behavioral equivalence or hostile-code OS isolation is claimed.

## Candidate and restart evidence

**`R5.94A-GENERIC-PROTECTED-CANDIDATE-2`**, inactive:

`7635e16fdf2c2fd61f4878bc8d6924fa9995d24a9c92111c07e3fb404878ea03`

* [Candidate](r5_94a/candidate-2/protected-freeze-candidate.json)
* [Verification](r5_94a/candidate-2/verification.json)
* [Fresh-process reverification](r5_94a/candidate-2/restart-verification.json)
* [Exact-dependency audit](r5_94a/candidate-2/exact-dependency-audit.json)
* [Self-bound final state](r5_94a/candidate-2/final-checks.json)

Both processes independently qualify Python and reject actual freeze integrity.
Candidate record self-binding, runtime-contract binding and retained exact pin
identities are distinct from successful physical dependency verification. The
candidate is created, **not eligible, not active, not a verified superseding freeze**.
Earlier engineering candidate/evidence under `r5_94a/final/` remains preserved.

## Validation and historical comparison

**38/38** prospective synthetic calibration challenges pass, reusing all **32**
R5.94 protected challenges with unchanged test methods except the prospective
integrity test, plus new runtime/contract/provenance controls and interpreter
selection. Two focused selection checks subsequently pass, including structured
unavailable-interpreter failure. The comparison calibration uses explicitly
separate exact **local synthetic pins**, with mock workers and no live OpenCode
execution; it does **not** bypass production integrity or validate the actual
candidate. [Passing log](r5_94a/comparison-final/synthetic-calibration-tests.txt).

Against saved R5.94 **3.12.10** supported/unsupported/invariance records, current
3.14.3 synthetic execution retains:

* `BEHAVIORALLY_VERIFIED` and `UNREPRESENTABLE_SOURCE` decisions;
* identical BDI decisions and `ADEQUATE` outcome;
* model source identity
  `ee9fcaacdf579cb6283d4a4212b346fefb1b275165ae570857cd5b24fa42f9bc`;
* generated target SHA-256
  `41dee0658ad3b83d8d4cc53fb10a0dc44da8bf894d3fcdf8227c4f08605242cb`;
* normalized V1 semantic identity
  `16af143013ae37361d0d89d979f661a866e6810f7ea26fc9f85c1b6141e07ac1`;
* public/protected classification distinction and formal/structural/BDI/adequacy
  meaning within the paired fixture scope.

Exact envelope identities change with prospective freeze dependencies. Runtime
provenance, journal receipt bytes, paths, timestamps and execution timing are
intentionally environment-dependent. Only **one runtime was executed**: 3.12.10
is neither rerun nor retroactively qualified under V1. Preserved historical
evidence is comparison evidence, not a second successful V1 qualification.

Pre-freeze failures and corrections are retained in
[development attempts](r5_94a/development-attempts.json), including a SQLite
resource-cleanup probe bug, a correctly denied ctypes import incorrectly handled
by the initial probe, and a provenance implementation bug corrected by separate
receipts. Failed raw qualification/calibration evidence is preserved.

## Reproduction

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH='src'
& "C:\Users\lblan\AppData\Local\Python\pythoncore-3.14-64\python.exe" -X utf8 -m lykoi_runtime.verify verify --current
& "C:\Users\lblan\AppData\Local\Python\pythoncore-3.14-64\python.exe" -X utf8 -m rehearsal.validate_r5_94a check --destination "benchmark/results/phase5c/r5_94a/candidate-2"
```

The second command returns **exit 1**, with runtime qualification passing and
freeze eligibility false. It is a preserved fail-closed result, not an unexpected
Python failure. The writer's blocked branch publishes a stopped result; its exit
0 indicates publication, not eligibility.

## Preservation and boundary

R5.91/R5.94 freezes, R5.95/R5.95A results, frozen compiler/runtime/schema and
semantic machinery were not edited. Pre-existing local documentation and result
work was preserved. No protected source, target identity, content-revealing metadata
or protected store was inspected. All **16 inherited B03 round counters remain
zero**, by inherited declaration plus this round's exclusively synthetic/public
operations, not a fresh protected-ledger inspection. B03 remains **pristine,
unevaluated and unexposed**. No target activation or authorization occurred.

Python no longer needs identical installation bytes under this prospective
implementation. Another runtime must mechanically qualify independently. However,
R5.95 authorization **cannot now proceed** against an eligible new freeze: the
exact non-Python dependencies above still block it. Stop here; no B03 continuation.
