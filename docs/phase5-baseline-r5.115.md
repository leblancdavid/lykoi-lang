# Phase 5 preservation baseline — R5.115

Recorded 2026-10-08. This is the implementation baseline for the planning transition,
not a snapshot authorizing a future requirement attempt. Refresh immediately before
each future first access using the [Phase 6 protocol](phase6-generalization-protocol-r5.115.md).

## Exact identity and provenance

- Git commit: `694c4e02f13111e65781e48e69da97c1ea6f4502` (`r5.114`).
- Git root tree: `82152054ba76f049dd85f3e7d389f2bd64aedee6`.
- Before edits and after fresh checks: `git status --porcelain=v1 --untracked-files=all`
  empty; `git diff --stat` empty. No initial local changes or untracked work.
- R5.115 adds planning/status documentation only. The completion worktree contains
  those uncommitted changes; this record does not claim a new R5.115 commit.
- Environment observation UTC: `2026-10-08T13:10:03.201870+00:00`.
- CPython `3.14.3 (tags/v3.14.3:323c59a, Feb 3 2026, 16:04:56)`;
  MSC v.1944, 64-bit AMD64; `Windows-11-10.0.26300-SP0`.
- Executable: `C:\Users\lblan\AppData\Local\Python\pythoncore-3.14-64\python.exe`.
- Workspace: `D:\Dev\axiom`; PowerShell 7+ through OpenCode.
- Session-reported model/provider: `openai/gpt-6.1-sol` / OpenAI. No live
  formalization/provider run was performed. Exact OpenCode build/settings unavailable.
  These facts are provenance, not qualification requirements.
- A first unquoted PowerShell `HEAD^{tree}` command was misparsed; the quoted
  `git rev-parse 'HEAD^{tree}'` returned the root tree above. No repository mutation.

Preserved Git subtree identities (Git object IDs, not physical-file SHA-256):

| Path | Tree object |
| --- | --- |
| `src` | `d1dc40879ec31fc7b522ae8accd9e91ee7105233` |
| `schema` | `8c04839087c76ab111e1eabb05b3e14e6b36ca1c` |
| `air` | `c7abd1483a14cf0c1ca21dd8d2edd3ee3db7ca39` |
| `generated` | `d666daef4f362b2d4423e0be1942954ad4846bed` |
| `tests` | `6563e2c951d61f201d5abddc4f89aeeee5ad6148` |
| `benchmark/harness` | `7ddd8f7d201343816571a10646fed98dab3d8daa` |
| `benchmark/evaluation` | `68c94828b6b16ad5000d80cb999ff4ecc4233df1` |

## Versions and supported boundary

The compiler/backend is the exact committed `src/air_compiler/` Python implementation;
legacy generator/manifest compiler version **0.3.0**, canonical serialized model **0.3**
(`air/task_manager.json`), normal dispatcher **LykoiProgram-1**. Version labels alone
are insufficient identity; the commit/subtrees identify their actual implementation.
The generated task artifact manifest retains SHA-256
`41dee0658ad3b83d8d4cc53fb10a0dc44da8bf894d3fcdf8227c4f08605242cb`.

| Layer | Selected version/profile |
| --- | --- |
| Query semantic / normal profile | `CollectionQuery-0.1` / `collection-query-1` |
| Normal scalar / model amendment / composition | `existing-scalar-1`, `existing-model-1`, `existing-composed-1` |
| Mutable / input / predicate | `typed-mutable-values-1`, `typed-input-values-1`, `typed-predicates-1` |
| Relationships / coupled durable state | `persistent-references-1`, `atomic-durable-state-1` |
| Primary values / authorization | `primary-value-interfaces-1`, `prewrite-authorization-1` |
| Computation / duration conversion / conditional images | `typed-computation-1`, `elapsed-day-conversion-1`, `conditional-created-effects-1` |
| Historical related state | `historical-related-state-1` |
| Representation / sealed pipeline / external plan | `LykoiContractV1`, `sealed-pipeline-1`, `external-cli-plan-1` |

Input/predicate/query interfaces, bounded computation and conditional-effect rules
are pinned by the commit and versioned R5.105–R5.114 specifications, not new R5.115
versions. Historical compatibility schemas and prior representations remain intact.
The normal FRC → source inventory/reconciliation → structural coverage → BDI →
adequacy → faithful V1 → compiler → external verification path functions within
these selected supported profiles; arbitrary profile unions are not implied.

Supported families include typed scalar/nullable and ordered collection state;
presence-aware inputs and staged transformations; explicit typed predicate/query
selection and ordering; bounded lifecycle/guarded writes; nominal references,
existence/restriction and finite path reachability; one-store atomic coupled updates,
bounded related creations and durable history; declared clock/ID resources;
signed-64 checked computations and fixed UTC displacement/day conversion;
role/owner/set prewrite authorization and conditional created-image composition;
source-authorized additive primary/related version migrations; and verifier-owned
controlled-host context with externally classified observations.

## Exact proposed kernel: 26

Preserve [R5.114 accounting](../benchmark/results/phase5c/R5_114-KERNEL-ACCOUNTING.json),
Git blob `cb0f5c566149fae770e270bdbe71d456a03fe8b9`:

1. record schema
2. field
3. finite sequence
4. var
5. literal
6. equals
7. and
8. not
9. contains
10. selection
11. trim
12. map(trim)
13. stable_unique
14. transition
15. instant
16. before
17. operation contract
18. cardinality
19. input presence
20. typed resource/capability authority
21. durable state
22. atomic commit
23. finite nonempty-path reachability
24. checked integer addition
25. fixed-duration instant displacement (`offset`, fixed elapsed seconds)
26. checked elapsed-day duration conversion (`seconds = N * 86400`)

This is a proposed architectural count, not a minimality proof or 26 unrestricted
normal-language operations. R5.115 changes neither count nor semantics.

## Verification evidence

The committed [R5.114 verification receipt](../benchmark/results/phase5c/R5_114-GENERIC-VERIFICATION.json)
(Git blob `3e9cb23fe95c4df0114be9c5131e12cfa3138bb7`) records **397 passing tests**,
30 successful commands including validation/safety, UTC
`2026-10-08T08:14:32.922316+00:00`, implementation/test digest
`d8279800ca64751fe8de7e512498a0ea5f2f0df1d8161460ffbb82b02754f32b`.
Its full stdout/stderr and exact argv remain preserved. R5.114 also preserves
**133 synthetic external invocations** before lock and fresh exposed transfer
**16/20 successes B01–B16 / 447 invocations**. These are historical receipts,
not new R5.115 runs or held-out evidence.

Fresh R5.115 recheck, `PYTHONPATH=src`, all exit 0 on the clean baseline:

| Command | Observed result |
| --- | --- |
| `python -m air_compiler.cli validate air/task_manager.json` | `Lykoi validate: ok` |
| `python -m air_compiler.cli safety air/task_manager.json` | 0 capability violations, 0 invalid transitions; 5 runtime-enforced and 1 structurally guaranteed invariant |
| `python -m unittest discover -s tests -p test_compiler.py -v` | 22 pass, 0.082 s |
| `python -m unittest discover -s tests -p test_application.py -v` | 9 pass, 2.753 s |
| `python -m unittest discover -s benchmark/harness -p test_baseline.py -v` | 3 pass, 4.403 s |

**34 fresh tests**, not an additional 397-test rerun. No new failures observed;
broader current regression status is supported by the preserved receipt and unchanged
implementation/test baseline. Historical installation/CRLF-pin failures in older
experiments and the frozen guidance trailing-space defect remain documented there.
They are not erased or relabeled by these checks.

## Limitations retained

B01–B20 are permanently **Exposed development/regression corpus** (also useful for
transfer). B17–B20 currently halt on formalization disputes; B18/B19 downstream
is `NOT_REACHED`. Missing historical-role/error authority is not a semantic gap.
Actual clarified B18/B19 behavior remains unverified. Original first results,
including B03, remain immutable.

Arbitrary field/type/collection evolution, general conditional implication, broader
lifecycle/deletion branching, computed legacy creation, unrestricted expressions,
calendar recurrence and distributed/external effects remain outside the bounded
profile. Graphs are bounded to 16 nodes; coupled creations to 1..8 records in one
cooperating local store. Controlled-host assertion is not authentication; ordinary
CLI actor parameters are selectors. Principal mapping requires real source/provider
authority. No hostile-code isolation or general crash/distributed transaction proof.
Python-dependent Unicode/time/error/adapter behavior and artifact safe-integer transport
limits remain; backend independence is unproven. Synthetic captures, inventories,
approvals and oracles were same-agent evidence with shared scaffolding. Finite tests
do not establish broad formalization accuracy, universal correctness, kernel minimality,
unfamiliar-software generalization or AI efficiency.
