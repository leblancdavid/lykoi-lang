# R5.94B — Cross-machine freeze portability

**Final classification:
`R5_94B_CURRENT_MACHINE_ELIGIBILITY_BLOCKED_LIVE_OPENCODE_ADAPTER_CONTRACT`.**

The prospective **R5.94B-GENERIC-PROTECTED-CANDIDATE-2** initially passed its full
first/restart preflights and remains **inactive**, with exact canonical content intact.
After publication, two unchanged-contract preflights failed live OpenCode invocation:
reviewer `AI_EXECUTION_FAILURE / CLI_FAILURE`, then author with the same failure.
The latest machine eligibility is **false**. Python **3.14.3 AMD64**, all **137** content
pins and the published evidence hashes still pass. Neither the underlying CLI/provider
failure cause nor a need to restore historical installations is established.
No B03 activation, authorization or access follows.

## Final identity and evidence

* Format: `protected-portable-freeze-r5.94b-1`.
* Semantic candidate identity:
  `060adb4e30505f3488e36502626f20c4e58a8aa2742b635ddbaca4ce2b943915`.
* Physical candidate file SHA-256:
  `e46c086d294e9ffa58a028cacaa8a27d938027177dfcd250206c81547ee593cf`.
* [Candidate](r5_94b/final/protected-freeze-candidate.json),
  [full manifest](r5_94b/final/dependency-manifest.json),
  [initial machine preflight](r5_94b/final/verification.json),
  [fresh-process preflight](r5_94b/final/restart-verification.json),
  [tests](r5_94b/final/tests.json),
  [cross-machine comparison](r5_94b/final/cross-machine-comparison.json),
  [final accounting and physical evidence hashes](r5_94b/final/final-checks.json).
* Authoritative latest [machine status](r5_94b/final/current-machine-status.json),
  [first post-publication failure](r5_94b/final/publication-check-attempt-1.json),
  [unchanged-contract retry with full structured output](r5_94b/final/publication-check-attempt-2.json).
  The first failure preserves the terminal's structured summary; its complete child
  stdout was not retained. `rehearsal/reverify_r5_94b_publication.py` captures the
  subsequent result and pins its own reporter bytes without modifying frozen procedures.

The earlier engineering candidate 1 and its 25-test/preflight/restart evidence
remain at `r5_94b/` under their distinct identity. Final review added an explicit
check that the controller's working candidate copy matches the externally approved
identity, alongside the separately retained execution guard copy. Candidate 2 adds
the corresponding negative control and precise failure classifications. The earlier
snapshot is preserved; candidate 2 is the current engineering boundary.

## Dependency classification

The manifest has **141 explicit declarations**:

| Class | Count | Eligibility rule |
| --- | ---: | --- |
| `CANONICAL_CONTENT_PIN` | 137 | 135 text-file entries plus two embedded CJ-1 values must match exact canonical identities. |
| `EXACT_BINARY_PIN` | 0 | No binary in this bounded audited set requires experimental byte identity; the verifier implements and adversarially tests exact binary pins. |
| `COMPATIBILITY_CONTRACT` | 3 | Python runtime, OpenCode transport, platform/containment must satisfy their declared contracts. |
| `PROVENANCE_ONLY` | 1 | Aggregate actual installation/platform/representation record; no eligibility comparison to the original machine. |

Every item has dependency, declared type, class, procedure/contract where applicable,
provenance and rationale. Ambiguities reject construction rather than receiving a
lenient class; the final manifest's ambiguity list is empty. The historical case-only
`Controller.py` entry has an explicit tracked `controller.py` locator and the same
inherited hash. There are 135 file-pin entries, including this one alias, rather than
a claim of 135 distinct physical files.

The [class specification](../../../docs/freeze-dependency-classes-v1.md) and
`src/lykoi_freeze/content.py` define **`UTF8_CRLF_TO_LF_V1`**: strict UTF-8 decode,
NUL rejection, CRLF → LF only. Preserve final newlines, lone CR, BOM, Unicode code
points/normalization, whitespace, indentation, comments, prompt wording, formatting
and JSON ordering. Physical JSON files are not reserialized. Only existing CJ-1
semantics apply to the embedded semantic envelope and model configuration.

All inherited file pins are checked against their historical physical representation
before the new canonical identity is created. Physical/LF/uniform-CRLF reconstruction
must explain the historical hash; other differences halt. This is not re-pinning a
different semantic implementation. Every original compiler/controller/workspace/
pipeline/schema/mapping/BDI/adequacy/profile/prompt/verification/access-policy/taxonomy
content remains exact. The executing source-package closure is additionally pinned.

Each file entry records creation physical SHA-256 as well as canonical identity and
the inherited physical hash where available. The semantic candidate identity excludes
provenance; a separate provenance digest binds creation observations. Published evidence
additionally binds the complete candidate file's physical hash. Eligibility reports
actual physical hashes, but a changed physical text hash alone does not fail a matching
canonical pin. Binary verification never calls text canonicalization.

## OpenCode dependency analysis and qualification

[Adapter analysis and contract](../../../docs/opencode-adapter-contract-v1.md) trace
the actual R5.89/R5.91 integration. OpenCode transports allowlisted role requests to
the configured OAuth model and returns events/bound JSON. It does not own Lykoi's
semantic authority, FRC approval, source-review commitment order, verification sealing,
mapping, compilation or protected access decisions.

The exact R5.91 invocation method, prompts and CLI configuration are used by the
public/synthetic procedure `src/lykoi_freeze/opencode.py`, under the pinned
`rehearsal/opencode-adapter-contract-v1.json`:

* Four roles receive intended allowlisted inputs over stdin, with native reviewer
  source commitment and an existing public author-input fixture.
* Candidate-FRC insertion into reviewer input and hidden-verification insertion into
  author input reject before dispatch. Synthetic controller tests additionally reject
  reviewer candidate delivery before commitment and original-prose delivery to authors.
* A fresh initially empty temporary cwd and isolated config are mechanically observed.
  No attach/continue/session argument is allowed. Installed CLI effective configuration
  confirms exact role prompt, zero temperature, model and small-model route, denied
  tools/permissions, no extra instructions/plugins, disabled title/summary/snapshots/
  automatic compaction/sharing/update.
* A qualification-only public adversarial operator command supplies the actual path
  of a synthetic outside-context canary and requests its retrieval. No canary enters
  responses/session messages and no tool executes. Production invocation is unchanged.
* Bound structured JSON is retrieved for every role. Only the just-created synthetic
  sessions are exported: session input, agent, provider and model route are verified.
  There is exactly one user message per role session; all four sessions are distinct.
* Eight deterministic negative controls expose allowlist violations, nonzero exits,
  timeout, provider error events, attempted tool events, missing session and invalid
  binding. Raw provider error bodies/stderr and credentials are not published.
* Version/path/SHA-256 must remain stable during qualification. Process-local execution
  guards requalify changed Python/OpenCode implementations before dispatch; AI invocation
  also rejects implementation drift across the call.

**OpenCode 1.18.32 passed `OPENCODE_ADAPTER_CONTRACT_V1` in the first/restart runs.** Those
preflights each establish **4/4 live roles and 8/8 negative controls**. Their session
sets are disjoint. Exact installed tool SHA-256 is provenance:
`cf664aa1da32b788f9b2699b84a9bb9be30b7e025693b90f9b85829d5fe4e252`.

Post-publication qualification subsequently failed after two completed roles at the
reviewer, and an unchanged-contract retry failed at its first role, the author.
Both return `OPENCODE_INCOMPATIBLE` and machine eligibility false. The CLI failures
are visible, not skipped or converted into a compatibility PASS. The original
successful records are historical observations within this round, **not current
eligibility authority after these failures**. No model/configuration/contract change
or further qualification retry follows. Provider stderr was deliberately not retained;
network, quota, OAuth or adapter-defect attribution is **not established**.

The independently pinned configuration still names **`github-copilot/claude-sonnet-4.6`**,
temperature **0**, timeout **180 seconds**, original policy and independence statement.
Only transport `executable`/`cli_version` fields are separated from current semantic
configuration. Original configuration files and historical receipts are preserved
as immutable evidence. Requested route and session-reported route agree. Provider
weight identity is not exposed; this was already an architectural limitation.

This qualifies the adapter surface, not AI semantic accuracy on future requirements,
all OpenCode behavior, model/provider independence or hostile-native-code OS isolation.
OpenCode 1.1.25 was not executed under this new contract, so **1.1.25/1.18.32 equivalence
is not claimed**.

## Python, machine eligibility and execution binding

The unchanged **`PYTHON_RUNTIME_CONTRACT_V1`** passes on CPython **3.14.3**, Windows
AMD64, SQLite **3.50.4**. Each final first/restart preflight independently passes
**41 existing tests** plus stdlib/CJ-1/hash/filesystem/argv/timeout/SQLite-restart and
actual file/network/process/native-API denial probes. Initial first/restart eligibility
had no failure reasons; the latest preflight is blocked specifically by live OpenCode
execution/model availability. All preflights verify every canonical dependency;
there are no declared experimental binary pins to verify.

`src/lykoi_freeze/freeze.py` implements structured machine preflight, requiring an
external expected candidate identity. It verifies the manifest before executing
qualification code, then checks runtime/platform/containment and live model adapter
availability. `src/lykoi_freeze/execution.py` supplies process-local `ExecutionGuard`,
`CrossMachineProtectedController` and `QualifiedProtectedOpenCodeAdapter` around the
unchanged protected semantic machinery. Semantic components use canonical identities;
actual implementations, paths, versions, libraries, SQLite and OS/platform are separate
per-operation/worker provenance. Fresh processes cannot reuse an earlier guard receipt.
Transport paths are selected explicitly or through `LYKOI_OPENCODE`, never by rewriting
the frozen model. Paths/usernames/temp locations are not experimental eligibility pins.

Reverification from the repository root, using a selected interpreter directly:

```powershell
$env:PYTHONPATH='src'
& "<qualified Python executable>" -X utf8 -m rehearsal.validate_r5_94b check `
  --opencode "<this machine's OpenCode executable>" `
  --expected-identity 060adb4e30505f3488e36502626f20c4e58a8aa2742b635ddbaca4ce2b943915
```

The command does live public/synthetic transport qualification. No global Python
installation path is required. The supported platform scope remains the existing
CPython 3.10+/64-bit Windows/Linux/macOS contract, with POSIX resource requirements.
Another machine may qualify with different tool bytes/locations and line endings,
but must actually pass every declared contract and retain the frozen semantic content.

## Adversarial and cross-machine evidence

Final new tests: **26/26**, no skips. They include fourteen meaningful text mutation
subcases: prompt word, mapping value, code token, JSON value, BDI rule, verification
expectation, comment, indentation, JSON ordering, missing/additional final newline,
BOM, NFC/NFD and lone CR. Every mutation invalidates its canonical pin. Invalid UTF-8
and binary/NUL input reject as text; exact binary CRLF changes invalidate binary pins.
Unknown/missing classes, undeclared canonicalization, escaping paths, content drift,
model substitution, resealed semantic substitution and stale tool/runtime guards reject.

Actual unchanged synthetic pipeline tests preserve supported success and restart,
unsupported complete-mapping refusal, source-blind reviewer/author boundaries and
public/protected semantic invariance. They compare current normalized V1, BDI,
adequacy, generated model identity and target bytes with preserved R5.94 outcomes.
Mock qualification in those synthetic controller fixtures is explicitly **not** an
eligibility receipt; the separate final live preflights qualify the actual machine.

All **101** inherited physical-byte differences retain canonical content continuity.
Complete ordinary-manifest mirrors at relocated Unicode/space paths verify with
uniform LF and uniform CRLF. Historical R5.94A 3.12.10/3.14.3 comparison evidence is
preserved and bound by its physical hash in the new comparison record. It establishes
agreement on the recorded synthetic semantic outputs, not retroactive qualification
of 3.12.10. Mirrors execute on the current computer: **a second physical computer was
not executed or certified in this round**.

## Preservation, protection and stop

R5.91, R5.94, R5.94A, R5.95, R5.95A, R5.92A and R5.93 historical evidence/machinery
are unchanged. Lykoi semantics and benchmark behavior are unchanged. R5.94B defines
new freeze infrastructure and prospective qualification only.

All **16 scoped B03 counters remain zero**, including source-access attempts/reads,
content-revealing metadata, openings/admissions, role dispatches, authorizations,
FRC/projection/compilation/verification/observation and development exposure.
Pristine/unevaluated/unexposed state is inherited plus this round's exclusively
ordinary/public/synthetic operations, **not a fresh inspection of protected target
files or ledgers**. No B03 content, target metadata or opaque identity was retrieved.

The old exact Python/OpenCode byte/path and line-ending blockers are removed by the
new dependency classification. The latest live adapter qualification nevertheless
fails, so **B03 authorization cannot proceed on this machine on this evidence**.
A future separately instructed continuation must obtain a passing unchanged-contract
machine preflight before considering activation and target-specific owner authority.
Restoring historical tool bytes is not a new eligibility requirement and is not
demonstrated to resolve these CLI failures. **This round authorizes neither activation
nor B03. Stop here.**
