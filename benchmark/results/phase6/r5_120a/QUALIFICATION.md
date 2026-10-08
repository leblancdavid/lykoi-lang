# R5.120A synthetic qualification and preservation

Public known-answer, same-agent/same-model interface evidence. Actual coding model:
`openai/gpt-6.1-sol`, OpenAI. External processes own behavioral observation and
classification; cognitive independence and held-out generalization are not claimed.
The user authorized this synthetic methodology round; test human statements are
explicit synthetic role simulation, not real approval of an external candidate.

## Reproduction

From the repository root:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests -p test_local_research.py -v
```

For individual extracted native records, set `PYTHONPATH=src;tests`, then in Python:

```python
import test_local_research as fixtures
args = fixtures.inputs()  # public synthetic contract and source-side plan
positive = fixtures.run(args)
contract = fixtures.calibration()  # explicitly public R5.80 P01 only
negative_args = fixtures.inputs(contract, fixtures.verification_fixture(contract))
negative = fixtures.run(negative_args, author_fixture=fixtures.author_fixture())
```

`positive` contains all native evidence/observations; the retained JSON is an extracted
receipt/stage/count/negative-observation witness, not a complete production journal.
UTC times vary on reproduction. Bindings and target hashes remain exact for these
inputs and implementation; source snapshot manifest is available from
`lykoi_research.local.implementation_snapshot()`.

## Observed controls

- Public library capture from R5.102: exact synthetic FRC constructed without any
  controller; unchanged source-side literal plan fixed before authorship. Existing
  scalar native profile, faithful authoring, compiler and verifier: **5 cases / 17
  external process steps pass**. Includes persistence/restart, rejection-byte
  preservation and explicit historical migration, not only a compilation check.
- Public P01 store contract: existing canonical task-model author fixture deliberately
  wrong. Compilation passes; `store --code public --value 17` exits **2**, stdout is
  empty and `measurements.json` unobservable. External classification is
  **BEHAVIORAL_VERIFICATION_FAILURE**, never author self-certification.
- Unsupported public `sum` relation halts structural coverage; `effects` halts BDI;
  undetermined priority default halts adequacy; determined priority in P01 without a
  qualified complete mapping halts V1. No downstream author dispatch after any halt.
- Unresolved FRC questions, malformed FRC, inadequate plan coverage and missing native
  plan payload halt. Malformed author fixture fails compilation, verification unreached.
- Source/FRC/plan substitutions, changed expected return code, statement/provenance
  substitution, wrong purpose/evaluator/snapshot and malformed/non-UTC timestamps
  are refused. Receipt identity is not allowed to authenticate a role.
- Production `UNAUTHENTICATED` for receipt-as-credential; direct grant/seal subject
  imitations refused; all local/reserved artifact registration attempts refused
  `RESERVED_OR_UNKNOWN_TYPE`; a registered ordinary context containing the receipt
  is refused `TYPE_MISMATCH` as a grant. Production applicability is false.
- The test production database bytes, revision and event list are **identical before
  and after local positive execution**. Production's own intentional denial calls
  are journaled before that comparison; no audit behavior is disabled.
- AST/API checks exclude Controller/Pipeline construction and grant/registry methods
  from the new runner. There is no production connection/credential argument.

## Checks actually run

All selected commands passed; **146 distinct tests**, not a cumulative round total.
Focused tests were repeated only after interface changes; duplicates are not counted.

| Command (prefix `python -m`) | Passing tests |
| --- | ---: |
| `unittest discover -s tests -p test_local_research.py -v` | 13 |
| `unittest discover -s tests -p test_research_authority.py -v` | 22 |
| `unittest discover -s tests -p test_sealed_pipeline.py -v` | 30 |
| `unittest discover -s tests -p test_authority_controller.py -v` | 34 |
| `unittest discover -s tests -p test_compiler.py -v` | 22 |
| `unittest discover -s tests -p test_application.py -v` | 9 |
| `unittest discover -s tests -p test_scalar_normal_path.py -v` | 13 |
| `unittest discover -s benchmark/harness -p test_baseline.py -v` | 3 |

`air_compiler.cli validate air/task_manager.json`: PASS.
`air_compiler.cli safety air/task_manager.json`: PASS, 0 capability violations,
0 invalid transitions. Whitespace and final change-scope checks recorded with the
round publication. No broad Phase 6 evaluation/source discovery was run.

An initial isolation-test assertion included intentionally attempted production
denials in its baseline and failed because the existing controller correctly journals
denials. Corrected the **new test's measurement boundary**, then passed; production
behavior was never changed. This is synthetic qualification development, not repair
of any historical external result.

## Historical and semantic preservation

Starting `git status --short`: clean. Starting HEAD:
`f94634f375c91b022ad67f35cb060ace1a7af3e2`. Original Git objects:

| Preserved component at starting HEAD | Git object |
| --- | --- |
| `benchmark/results/phase6/` | `3d13969da46f3365954c257bce1d93513295b969` |
| `src/air_compiler/` | `87f3c8c1c8b1af394235aa835d39342b770b6c49` |
| `src/lykoi_pipeline/` | `3c6d011384280460c0b4594197643f286e18fa6c` |
| `src/lykoi_controller/` | `db421a7815728283dd38df9ce6bbe021ef0a3725` |
| `benchmark/evaluation/` | `68c94828b6b16ad5000d80cb999ff4ecc4233df1` |
| `air/task_manager.json` | `2c9a51cc2993462bfcadb34d09b469d081135d75` |
| `r5_120/P6_A03_FIRST_RESULT.json` | `ccf8cbeb3f4c9dae72a6d602d00324e3725d6831` |

No modification to those existing files/trees, schema, generated output, backend,
semantic mappings, or existing test expectations. The new R5.120A evidence is additive
under `phase6/`; all earlier records remain unchanged. Kernel **26**, with unchanged
R5.114 accounting. Existing tests/fixtures are imported, not rewritten.

Only new `src/lykoi_research/local.py`, `tests/test_local_research.py`, new local spec/
prospective protocol/report/evidence and minimal current-boundary guidance additions.
No P6-A03 evaluation, authoring, compilation, Redis probes or ACL simulation; no
P6-A04/P6-A05 inspection. Later external attempts need separate authorization/linkage.

## Final publication audit

- `git diff --check`: no whitespace errors. New files additionally checked with
  `git diff --no-index --check -- NUL <path>`; no whitespace diagnostics (exit 1
  denotes different/new content). Git's normal LF/CRLF conversion notices are not
  whitespace defects.
- `git diff --exit-code --` over existing compiler/pipeline/controller/evaluation,
  schema/model/generated/requirements/Phase 5 evidence and the six preserved Phase 6
  round directories/reports: exit 0, empty diff.
- `git status --short --untracked-files=all`: exactly the seven additive guidance
  edits and seven new runner/test/spec/protocol/report/evidence files described above.
  No historical source, first-result, acceptance or production-state file changed.
- Final focused suite after the last runner snapshot change: 13/13 pass.
- No commit, activation, external evaluation or next-round execution performed.
