# R5.94C — Provider-neutral AI worker transport

**Final classification: `R5_94C_BLOCKED_NO_FUNCTIONING_TRANSPORT_FOR_FROZEN_MODEL`.**

The prospective abstraction is implemented. OpenCode is an optional transport
implementation, not the architectural contract. No currently discovered supported
transport successfully invokes the independently frozen
**`github-copilot/claude-sonnet-4.6`** configuration. All eight bounded live attempts
failed explicitly with `AI_EXECUTION_FAILURE / CLI_FAILURE`. No output candidate was
fabricated, model substituted, eligible successor freeze published or B03 authority
issued. The underlying provider/CLI cause is not established and was not debugged.

## Deliverables and actual interface requirements

- [AI_WORKER_TRANSPORT_CONTRACT_V1](../../../docs/ai-worker-transport-contract-v1.md)
  and its [versioned record](../../../rehearsal/ai-worker-transport-contract-v1.json).
- `src/lykoi_transport/adapter.py`: minimal `Transport` protocol,
  `Invocation`/`Result`, `WorkerAdapter` and provenance-aware `ProtectedWorkerAdapter`.
- `src/lykoi_transport/opencode.py`: optional OpenCode implementation wrapping the
  byte-preserved R5.91 invocation; no auth-store or credential extraction.
- `src/lykoi_transport/verify.py`: bounded provider-neutral qualification procedure.
- `src/lykoi_transport/freeze.py` and `execution.py`: prospective neutral freeze,
  process-local implementation qualification and unchanged protected controller wiring.
- [Dependency specification](../../../docs/provider-neutral-freeze-r5.94c.md),
  [current manifest](r5_94c/prospective-dependency-manifest.json),
  [discovery](r5_94c/transport-discovery.json),
  [final status](r5_94c/final-status.json),
  [machine eligibility](r5_94c/final-machine-eligibility.json),
  [fresh-process eligibility](r5_94c/final-fresh-process-eligibility.json).

The audit identifies Lykoi-owned input/schema checks in R5.89, complete role instructions
and reviewer source span in R5.91, and source-classification commitments in R5.94.
Workspace/controller commitment ordering, sealed verification, approvals, implementation
grants and compiler behavior remain outside transport. The exact existing role prompts,
native schemas, model settings and semantic authorities are retained.

The transport receives role, pinned complete instructions, frozen provider/model/settings,
only allowlisted bound inputs, schema and bounded timeout/request configuration. It must
create fresh isolated context, enforce input/context/tool restrictions, route to the
configured model, retrieve structured output or report explicit failure, and supply
implementation/session/model-route provenance. It forbids implicit repository context,
hidden cross-role state through the normal interface, unauthorized tools, detectable
silent model substitution and success fabrication after failure. All output remains
an untrusted candidate; schema/binding validation is not semantic approval.

## Model and transport separation

The frozen configuration still names GitHub Copilot / Claude Sonnet 4.6, temperature
**0**, invocation timeout **180 seconds**, original model policy and independence
statement. Its canonical identity is unchanged:
`34d047c1c0a8fc61d4f876c4b341401d38c5c70fc9f5a79feb9d1857689c54c8`.

Transport selection is a separate object with `identity`, `provenance` and `invoke`.
The workspace/pipeline-facing `produce(request)` signature is retained. Existing
OpenCode-specific instructions are historical pinned prompt content, not a requirement
to execute OpenCode. Another legitimate implementation may deliver those exact
instructions and settings while satisfying the same behavioral interface. No additional
live adapter was used or claimed in this round.

OpenCode 1.18.32 and Codex are installed. No Copilot, GitHub or Claude CLI command was
found by command discovery. The installed OpenCode provider model listing includes the
frozen route. Presence-only checks found an OpenAI credential, but no designated Lykoi
service credential, Anthropic credential or GitHub token. Neither Codex/OpenAI presence
nor a different provider credential establishes an equivalent route to the frozen
Copilot/Sonnet configuration. No credentials/auth files were read or published, no
authentication bypass was attempted and no substitute model was invoked.

## Live public/synthetic smoke evidence

| Role | First process | Fresh process |
| --- | --- | --- |
| Formalizer | explicit CLI failure | explicit CLI failure |
| Source-only reviewer | explicit CLI failure | explicit CLI failure |
| Lykoi author | explicit CLI failure | explicit CLI failure |
| Verification-plan producer (`verifier`) | explicit CLI failure | explicit CLI failure |

**0/4 successes in each process; eight attempts total, no retries thereafter.**
All attempts use public/synthetic source or the existing public author fixture.
The smoke envelope requires a role and public marker to prove structured transport
participation, not native-model semantic accuracy. Failures and complete sanitized
receipts are preserved in [first](r5_94c/verification.json) and
[restart](r5_94c/restart-verification.json) evidence. Failure receipts bind actual
transport identity/installation, frozen configured route, role, exact instruction,
schema/configuration/input identities and fresh local request ID. Actual session/model
route is explicitly unavailable where execution failed before it was exposed.

The adapter checks empty fresh working context and effective frozen instructions,
model/settings, no extra plugins/instructions, disabled auxiliary contexts and denied
tools. On successful execution it would export only the newly created session and
verify input, distinct session, actual route and absence of tool execution. This round
does **not** claim that the successful-session branch qualified live: every CLI call
failed before that point. Failure handling itself was observed live.

## Mechanical boundary, failure and provenance evidence

New tests **16/16** pass in the final prospective suites. They challenge:

- Formalizer implicit repository insertion, reviewer candidate-FRC insertion,
  author hidden verification/original prose and verification-plan implementation
  insertion: all reject before transport dispatch.
- Exact intended input and existing complete instruction/settings delivery;
  reviewer source-classification commitment invariance.
- Structured binding/schema corruption, provider failure, unexpected transport
  exceptions/timeouts, detectable model substitution and failure containing a
  fabricated candidate: no candidate is returned.
- Success/failure provenance, independently frozen model changes, bounded four-role
  attempts, alternate synthetic interface implementation and implementation drift
  requiring independent qualification.
- An actual unchanged protected synthetic controller/pipeline chain under the new
  neutral controller, supported success, unchanged unsupported mapping refusal,
  source-only review ordering, original-prose author denial and provenance invariance.

The unchanged OpenCode execution parser's eight deterministic negative controls also
pass, covering forbidden inputs, nonzero exit, timeout, provider/tool events, missing
session and invalid binding. Synthetic fixtures are explicitly **not real AI eligibility
receipts**. Boundaries are measured at the interface/controller, not by AI assurances
of honesty. Trusted-local isolation, provider-weight opacity and possible same-model
correlation remain the existing limitations.

## Freeze dependency classification and current eligibility

Prospective format: `protected-provider-neutral-freeze-r5.94c-1`.
Current **engineering manifest identity**, not a published freeze:
`b2616184c738bd90b684d1bac66059e5ba66e7b0ef328ef70c1e89119e0f99f6`.

All **137** R5.94B canonical entries remain identical; **12** additional exact content
pins cover neutral infrastructure, specification and procedures. Neither LF/CRLF
canonicalization nor Python runtime qualification was changed. The only architectural
contract replacement is `opencode-transport / OPENCODE_ADAPTER_CONTRACT_V1` with
`ai-worker-transport / AI_WORKER_TRANSPORT_CONTRACT_V1`. Actual implementation/version/
bytes/location remain separately qualified runtime provenance. Historical OpenCode
files/evidence stay pinned as historical content; no installed OpenCode artifact is
mandatory for the new interface.

The existing strict content verifier is reused through an in-memory projection of
format header/compatibility locator only; it does not execute OpenCode. Inherited
entry equality, frozen model/semantic envelope, external candidate identity and
current file identities are checked before qualification. Controller working-copy
identity and process-local guard binding are retained. Changing transport before
execution must independently requalify; changing it during invocation fails visibly.

Final first/fresh-process offline eligibility audits establish:

| Check | Result |
| --- | --- |
| All 137 inherited canonical pins and 12 new pins | PASS |
| Frozen semantic/model envelope | PASS, unchanged |
| CPython 3.14.3 `PYTHON_RUNTIME_CONTRACT_V1` | PASS, 41 existing tests plus probes per process |
| Platform/process/filesystem/SQLite and existing containment probes | PASS |
| Prospective regression suite | **241/241**, no skips, per process |
| Compiler/application tests within suite | **31/31** |
| Protected/source/authority/workspace/pipeline/verification/freeze regressions | PASS in scoped suite |
| External baseline | **3/3**, per process |
| Model validation/safety | PASS, per process |
| Whitespace/change scope at audit | PASS; final publication rechecked |
| Real worker transport/model availability | FAIL, retained eight live failures |
| Complete current-machine eligibility | **FALSE** |

The final offline audits make **zero new live attempts**, verify original evidence
hashes and unchanged invocation surface, and carry forward failures only. They cannot
upgrade a failing transport into eligibility. Runtime and nontransport checks execute
again in each audit process.

### Preserved initial engineering failure and prospective dependency correction

The initial full unchanged run executed **242** tests: **241 pass / 1 fail**, reproduced
in its fresh process. The sole failure is the last assertion of
`ProtectedTests.test_freeze_integrity_and_historical_identity`, which compares the whole
R5.91 snapshot to the current installation. Diagnostic comparison finds changed
historical `files` and `runtime` fields. Canonical inherited content still passes.
This is a historical exact representation/installation predicate, not a new Python
or semantic incompatibility. Its test and both failing logs are preserved unchanged.

The prospective suite excludes that one historical installation-bound test from new
machine eligibility, recording its disposition and replacing its eligibility purpose
with neutral canonical integrity/mutation tests. It does not change historical
acceptance or pretend the original check passed. The initial manifest and
`R5_94C_BLOCKED_MACHINE_PREFLIGHT_FAILURE` record remain at
[initial final-checks](r5_94c/final-checks.json). New independent final-status evidence
records the corrected prospective classification; no earlier record is overwritten.

## Qualification command and stop

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH='src'
& '<selected Python>' -X utf8 -m lykoi_transport.verify verify `
  --implementation opencode --executable '<selected OpenCode executable>'
```

This evaluates the neutral interface using its current optional adapter and bounded
public inputs. `rehearsal.validate_r5_94c check --expected-identity <external identity>
--executable <implementation>` runs the complete prospective preflight. The recorded
round is stopped; commands are for a separately instructed future qualification,
not permission for indefinite retries or protected access. A prospective freeze can
be created only after complete live and fresh-process eligibility passes.

**No successor generic protected freeze candidate was published.** Previous candidates
are preserved inactive under their own identities. Computer A/B may use different
Python and transport implementations only if each independently passes the same
contracts and exact frozen semantic/model configuration. No second physical-machine
or universal portability qualification is claimed.

All **16 scoped B03 counters remain zero**. B03 remains pristine, unevaluated and
unexposed by inherited declaration plus exclusively ordinary/public/synthetic operations,
not by inspecting target files, metadata or ledgers. Historical R5.94/A/B, R5.95/A,
R5.92A, R5.93 and OpenCode failures are untouched. No semantics, compiler, mappings,
BDI, adequacy, profile, prompts, controller/workspace/pipeline authority, verification
rules or protected access policy changed.

**Next-round B03 activation/authorization is still blocked.** First establish a
functioning transport for the unchanged frozen model and a passing current/fresh-process
generic freeze preflight. Only separately authorized subsequent work may then consider
activation and exactly scoped target authority. R5.94C stops here.
