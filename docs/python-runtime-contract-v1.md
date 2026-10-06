# Python Runtime Contract v1 — R5.94A

The normative machine contract is `rehearsal/python-runtime-contract-v1.json`;
the exact qualification procedure is `src/lykoi_runtime/verify.py` and its explicit
existing-test selection. Both are content-pinned by the prospective freeze.

CPython 3.10+, 64-bit Windows/Linux/macOS is eligible to **attempt** qualification.
No upper version limit is justified by current evidence. Architecture/platform
restrictions bound this prospective contract; they do not change ordinary project
Python support. POSIX additionally requires the existing `resource` limits API.
Qualification tests module availability, SHA-256, CJ-1 serialization and rejection,
SQLite transaction/rollback and separate-process persistence, Unicode/space paths,
exclusive creation/atomic replacement, subprocess argv/pipes/status/timeout,
controller deterministic identity/decisions/restart/corruption detection, producer
serialization, actual existing containment-hook file/network denial, and all current
compiler/application tests. It invokes no AI/provider and reads no held-out inputs.
TLS/provider behavior is not qualified here; existing model configuration and
OpenCode identity remain exact dependencies. This is finite trusted-local evidence,
not universal Python-version invariance or hostile-code OS isolation.

With `PYTHONPATH=src`, run the chosen interpreter directly:

```powershell
& "<python executable>" -X utf8 -m lykoi_runtime.verify verify --current
```

Alternatively `verify --interpreter "<path>"` or `LYKOI_PYTHON` selects the
qualification subprocess; absent both, the executing interpreter is selected.
No global `python` command is needed. Protected execution uses
`PortableProtectedController` in the selected process; its existing child workers
inherit `sys.executable`. Qualification of a different interpreter cannot authorize
the current process: every new controller process qualifies itself independently.

`RUNTIME_COMPATIBLE` includes exact implementation/version/architecture/platform,
executable path/hash, available DLL/ZIP identities and SQLite version as provenance.
These fields are excluded from semantic freeze/component identities. Each controller
operation event has a separate adjacent append-only runtime provenance receipt in
the same transaction. Original event evidence and artifact payloads are unchanged.
A restart/new runtime must qualify again before activation, authorization
or evaluation; local runtime artifact drift forces requalification. No cached receipt
from another process is accepted as execution authority.

## Freeze dependency classification

* **EXACT_SEMANTIC_PIN:** every inherited R5.94 `files` entry (compiler/import
  closure, controller/workspace/pipeline/protected access, schemas, mappings, BDI,
  adequacy, V1, specifications, capability profile, prompts/instructions, model
  configuration, verification/containment rules, adapter, historical smoke/calibration
  evidence and qualification tests). All inherited non-Python body fields remain
  unchanged. OpenCode 1.1.25 executable remains exact: its behavior participates in
  role execution and there is no behavioral replacement contract. New portable
  controller/freeze machinery and contract/procedure/test/document files are exact.
* **COMPATIBILITY_CONTRACT:** Python executable and Python standard-library/runtime
  behavior, including bundled SQLite, under `PYTHON_RUNTIME_CONTRACT_V1` only.
* **PROVENANCE_ONLY:** Python implementation's exact version, executable pathname,
  architecture/platform particulars within allowed scope, executable/DLL/ZIP hashes
  and SQLite version. Historical smoke receipts retain their original runtime/path
  facts as immutable evidence, not current Python eligibility predicates.

This repairs Python-installation portability. Frozen model configuration contains
an OpenCode executable pathname; its relocation/configuration remains a separate
exact dependency and is not silently rewritten by this repair.
