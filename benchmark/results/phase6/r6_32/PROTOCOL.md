# R6.32 bounded qualification protocol

Authorization is the owner's R6.32 request. Coordinator-written scripted witnesses;
no AI participant, inference, discovery or comparative H1/H2 trial. Capture the
protected baseline before implementation. Frozen production/R6.10/R6.18/R6.23/
R6.25 meanings remain unchanged. All new machinery is experiment-local.

## Preimplementation expectations

Registry: exact SHA256 retrieval, deterministic sorted name/signature search,
immutable definitions and generations, explicit successor edges and caller decisions.
Use R6.18's validator/expander for admission; admission probes are static, never
functional proof. Keep the frozen definition revision=1; lifecycle generations and
supersession are external metadata. Multiple versions may coexist on disk, but a
closure must have one version per family. No implicit latest-version resolution.

Modification: copy the exposed C/kiln/base intent from R6.16. Change the existing
ignite and set_gate rule to permit a closed vent while firing **only for emergency
loads**. Preserve ordinary-load constraints, cold-state gate writes, phase transition
precedence, nonblank labels, record domains, identifiers/time and listing. Update
both guards and the shared invariant. No added operation. Compare restarted subprocess
execution against requirement-derived expectations on both original/modified copies.
Exhaust all eight phase/vent/load tuples for invariant and transition controls;
include create/list sequences, rejection-byte preservation, corruption, and replay.

Expected semantic change footprint (specified independently of tool output):
`predicate:ignite_gate`, `predicate:set_gate_lock`, `invariant:firing_vent`,
`transition:ignite`, `transition:set_gate`, `definition:vent_policy`.
Expected unaffected: `behavior:create`, `behavior:list`, `field:id`,
`field:created_at`, `field:label`, `field:load`, `field:phase`, `field:vent`.
These field declarations remain identical; their *values* are consumed by the rule.
The legacy impact API is evaluated as supplied, on its supported scalar base with
field:vent as seed and separately on extension-only identifiers. No production repair.
Report native results plus explicitly labeled semantic-set mapping and FP/FN.

Telemetry: immutable fsynced event records, linked sequence, stage start/end,
input/output pins, tool intervals measured with perf_counter, UTC timestamps.
Recovery returns completed and incomplete stages without pretending missing timings
or usage are zero. Crash tests retain unfinished writes and incomplete start events.
Qualification is process-interruption safety on this filesystem, not a power-loss,
hostile filesystem or distributed-transaction guarantee.

Adversarial controls cover the owner's twelve categories plus schema/ambiguity
and mixed-version closure checks. Preserve exact proposals, diagnostics, failed
attempts and unfinished bytes. Freeze source/expectations before execution. Do not
repair behavioral candidates from scored outcomes. Implementation/test defects may
be corrected only with distinct failed-attempt and successor evidence.

Qualified means bounded registry, explicit selected caller migrations, genuine
stateful change and durable recovery demonstrated. Legacy impact incompleteness can
be a published gap but prevents claiming automatic dependency-complete H2 readiness;
use `R6_32_LIFECYCLE_PARTIAL` if that essential capability remains unqualified.
Stop after publication; any AI-authored pilot requires separate authorization.
