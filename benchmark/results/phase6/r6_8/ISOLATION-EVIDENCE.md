# R6.8 pre-assignment isolation evidence

**Gate result: NOT_ESTABLISHED. Reviewer assignment: NOT_RUN.**

## Evidence actually available

- Initial workspace was clean; HEAD is recorded in the report/input inventory.
- This publisher's developer/harness context already included `AGENTS.md`, whose
  R6.7 entry contains a prior verdict, substantive reduction findings and repair
  recommendations. The publisher cannot serve as an unexposed reviewer.
- Reading required project guidance revealed additional finding-bearing text in
  the workflow, overview and README. Files were preserved, not sanitized in place.
- The available Task schema exposes `description`, `prompt`, `subagent_type`,
  optional `task_id` and `command`. It supplies no reviewer-specific workspace,
  instruction override, tool allowlist, no-memory switch, outbound-request capture,
  retrieval boundary or attestation of effective inherited inputs.
- A distinct task/session is therefore not sufficient evidence of input exclusion.
  No task was launched to see whether it would reproduce contaminated reasoning.

These are interface and publisher-context observations, not observations of a new
reviewer's actual prompt. They establish inability to verify the required boundary
here, not that every hypothetical separate process must be contaminated.

## Required channels

| Channel | Evidence / limitation | Gate disposition |
| --- | --- | --- |
| Task instructions | Neutral text prepared; no task assigned | No leak through dispatch; insufficient by itself |
| Inherited project-controlled system/harness context | Publisher has exposed guidance; Task offers no auditable override/export of effective reviewer instructions | NOT_ESTABLISHED |
| Repository guidance | Finding-bearing AGENTS.md is inherited; no reviewer filesystem deny boundary exposed by Task | NOT_ESTABLISHED |
| Automatically loaded documentation | Workflow/overview/README contain findings; no project discovery disable evidence | NOT_ESTABLISHED |
| Search indexes/retrieval tools | Reviewer access restrictions/index exclusion cannot be attested from the interface | NOT_ESTABLISHED |
| Shared memory/summaries | No inspectable reviewer memory inventory or disable control | NOT_ESTABLISHED |
| Preloaded workspace context | No reviewer-specific empty workspace/context attestation | NOT_ESTABLISHED |

No isolated reviewer process was provisioned, no clean-room export was released,
no access-denial probes were run, and no full reviewer request transcript exists.
Creating a temporary folder or supplying an allowlist would not demonstrate the
missing instruction/memory/retrieval controls. No installation, credential search,
provider API call, agent configuration or new isolation infrastructure was attempted.

## Provider-side limits

Hidden provider-side instructions, training exposure, caches and internal state are
not inspectable through these tools. No control over them is claimed. A future
qualification can attest only to observable project-controlled inputs and access,
with explicit limits; it need not invent statistical independence or absence of
training familiarity. Same/different model or provider is not itself proof of
input-controlled independent judgment. The procedure must remain provider-neutral.

## Stop decision

The owner requires stopping when isolation cannot be established. No instruction
to ignore exposed findings, self-disclosure, fresh session or hash substitutes for
that gate. R6.8 stops before substantive review with
`R6_8_INDEPENDENCE_NOT_ESTABLISHED`.
