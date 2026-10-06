# AI Worker Transport Contract v1

**Normative identity: `AI_WORKER_TRANSPORT_CONTRACT_V1`.** Prospective R5.94C,
bounded to the current four-role experiment. Lykoi depends on AI-worker transport
behavior, not the development tool used to provide that behavior.

## Audit and authority

R5.89 `AIAdapter._request` owns the formalizer/source-only-reviewer, restricted
author and WHAT-only verification-plan input allowlists. R5.91 adds the exact
role protocol and envelope instructions and reviewer whole-source span. R5.94
`SourceProvenance` binds reviewer commitment to source classification. These are
retained, including their exact prompt bytes. Workspace/controller ordering prevents
candidate delivery before source-only commitment; pipeline/controller authority seals
verification before authoring. Transport grants no authority and repairs no output.

`verifier` is the existing internal role identity for verification-plan producer,
not an implementation-aware verifier. Model outputs are untrusted candidates.

## Inputs and minimal interface

`transport.identity() -> implementation identity/interface version`

`transport.provenance() -> actual installation/version information`

`transport.invoke(Invocation) -> Result`

Invocation contains role identity, independently frozen model configuration
(provider, model, temperature, timeout), pinned complete role instructions,
allowlisted input artifacts with their content binding, output envelope schema,
and a new local request identity. `WorkerAdapter.produce(request)` remains the
workspace/pipeline interface; it validates inputs before dispatch, creates the
envelope and structurally validates results. `ProtectedWorkerAdapter` retains
the existing source classification commitment. Transport cannot alter model,
prompts, input/output schema, inference settings or authority rules.

Result contains either a parsed structured envelope or an explicit failure,
plus provenance. A failure must have no candidate envelope. Provenance records
transport identity/version, configured model, actual route if exposed (otherwise
explicitly unavailable), role, instruction/schema/configuration identities,
each input artifact identity, local request identity, session/provider request
identity where available, success/failure and output identity on success.
Every attempt, including local boundary rejection, has a receipt. Raw secrets,
provider error bodies and unrelated sessions are excluded.

## Required behavior

- New isolated invocation context, without implicit repository/global context.
- Exact role instructions and only allowlisted artifacts delivered; no inherited
  conversation or prohibited cross-role state through the normal interface.
- Route to the frozen model with frozen settings; reject detectable substitution.
- Tools and external context disabled/restricted to the existing no-tools policy.
- Retrieve parseable bound structured output; validate binding and schema before
  any candidate is returned. Model output remains untrusted.
- Explicit failures for unavailable configuration/authentication/provider,
  timeout, execution errors, forbidden tool events, malformed/missing result,
  invalid binding/schema, route mismatch or implementation drift.
- Bounded execution: frozen invocation timeout 180 seconds; implementation
  metadata/configuration/session observations have bounded 20/30-second calls.
- Record actual implementation provenance. Implementation change before execution
  requires independent requalification; fresh processes cannot inherit eligibility.

## Forbidden behavior

No implicit repository context, hidden cross-role history, unauthorized tools,
detectable silent model substitution, output fabrication after execution failure,
semantic approval by a worker, prompt tuning or acceptance-criterion repair.
Input boundaries are mechanically enforced, not established by model assurances.
Trusted-local mediated isolation is the boundary; this is not a hostile-code OS
sandbox, model/provider independence or proof of immutable provider weights.

## Qualification and optional implementations

`python -X utf8 -m lykoi_transport.verify verify --implementation opencode
--executable <selected executable>` is the current command equivalent to
`lykoi transport verify`. It makes exactly one public/synthetic call per role,
retains every failure and reports `TRANSPORT_COMPATIBLE` only for four successes
in distinct contexts. No retries, future requirements or protected inputs.
Deterministic adapter, boundary, failure and provenance tests are separately
required by machine preflight. Smoke schemas test transport participation,
not native FRC/model/plan quality or broad model qualification.

OpenCode is one optional implementation. Its implementation-specific evidence
uses an empty cwd, isolated effective config, denied tools, no extra instructions,
fresh CLI invocation and export of only the session just created. Session metadata
must confirm actual model/input and no tool execution. These mechanisms are not
requirements on another implementation: it must supply equivalent observable
boundary evidence via its own mechanism. Historical OpenCode contracts/results
are preserved unchanged. No additional live adapter is claimed without legitimate
existing access to the independently frozen `github-copilot/claude-sonnet-4.6`.
