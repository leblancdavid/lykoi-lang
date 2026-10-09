# R6.34 linked successor — access-first protocol

Owner authorization: one bounded successor to R6.33, conditional on neutral
access and inert tool qualification. Historical R6.33 is immutable.

Before participant exposure, verify R6.33/R6.32 publication manifests and the
R6.33 protected baseline. Inventory existing configured credentials by provider
name and type only; never publish credential values. Select the already configured
OpenAI GPT-6.1 Sol/high route used in R6.33, advertised as tool-capable. Catalog
entries are not access evidence. No provider fallback, purchase or account setup.

Preflight budget: at most two OpenCode run invocations, 90 seconds each,
240 seconds total including inventory/export. First request is exactly a tiny
neutral acknowledgement. Only if it succeeds, request discovery/invocation of
`inert_echo` with the literal `neutral`. The tool has no semantic or file effects.
Any failed access or unqualified tool gate stops before lifecycle exposure.
CLI internal HTTP retries are not individually bounded or metered by this runner;
the process deadline is enforced. Newly purchased spending allowance is USD 0;
existing-route consumption ceiling is USD 1 where metered. If spending cannot
be metered, do not proceed to lifecycle authoring. Failed-call usage is missing,
not zero. No credits are purchased automatically.

On qualified access, freeze the selected route, reasoning request, tools,
instructions, original R6.33 syntax/requirements/modification/scorer/dependency
expectations and all source identities before participant task exposure.
Lifecycle budget: at most 12 model invocations, 24 tool invocations, 20 minutes,
USD 5 metered consumption, at most two correction turns per stage. No change of
model after exposure, no semantic repairs by the coordinator, no new operations.
Use unchanged R6.32 registry and unchanged R6.33 requirement-derived evaluator.
Stage the modification only after predecessor/two-caller acceptance.

After authoring closes, replay saved executable packages in a separate process
with no model route. Compare envelopes, errors, traces, provenance, order, logical
work, dependency pins and raw identities under unchanged expectations.

If access fails, classify `R6_34_PROVIDER_ACCESS_BLOCKED`; downstream stages and
their timings are NOT_REACHED, with no constructed substitutes. Publish explicit
artifact/registry/replay absence records. Otherwise use the owner's lifecycle,
partial, authoring-gap or protocol-halt classification as supported by evidence.

Preserve production kernel26, all protected semantics and R6.3–R6.33 evidence.
No H1/H2 study, P6-A04 acceptance or P6-A05 access. Verify publication hashes,
preservation, links and `git diff --check`; stop after publication.

Coordinator disclosure: inspecting the historical R6.33 orchestration source
revealed its task text to the coordinator before preflight. It is never included
in preflight participant prompts, configuration or inert tool definitions.
No independent/blinded coordinator claim is made.
