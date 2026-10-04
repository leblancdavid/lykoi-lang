# R5.36 checked public launch profile

This prospective local Python launch boundary wraps the unchanged R5.35 checked
transport and `benchmark.semantic.current_pipeline`. It is infrastructure, not
application semantics. Core candidate constructs remain 30; no #31.

## Assembly and public entry

At generation/provisioning time, call
`benchmark.semantic.checked_launch_r5_36.generate(application, bundle, transport_spec,
state_declaration, launch_config)`. The bundle directory already exists. Generation
uses the existing compiler, emits checked transport metadata, and copies the same
generic launcher for every supported application. No application Python wrapper.

From any working directory with the configured store parent available:

```text
python -E "<bundle>/launch_runtime_r5_36.py" <public-operation> [<public-flag> <value>]...
```

For the independent acoustic station:

```text
python -E "<bundle>/launch_runtime_r5_36.py" calibrate --channels " left " --channels right --samples 3
python -E "<bundle>/launch_runtime_r5_36.py" calibrate-json --samples "[]"
python -E "<bundle>/launch_runtime_r5_36.py" stamp
```

The interpreter and bundle path identify the executable, not semantic arguments.
Every token after the entry script is forwarded unchanged to the checked transport.
There are no bootstrap flags, positional store/trace/profile/provenance paths, or
required environment variables. `-E` is ordinary Python interpreter isolation;
the launcher also strips `PYTHON*` from its child environment and uses `-E` there.
Repository imports/PYTHONPATH are unnecessary in the copied bundle.

## Deterministic profile

`launch.json` has these exact fields:

| Field | Meaning |
| --- | --- |
| version | `R5.36` |
| id | nonempty infrastructure profile identity |
| application | canonical semantic application SHA-256 |
| generation | existing generated provenance/generation SHA-256 |
| provenance | canonical complete provenance SHA-256, including unit/CheckedPlan identities |
| transport | canonical checked `transport.json` SHA-256 |
| persistence | canonical `{policy,state}` SHA-256 from checked transport/state declaration |
| capabilities | canonical `capabilities.json` SHA-256, assembled from existing plan requirements |
| store | `{base:"cwd",path:RELATIVE,parent:"require_existing"}` |
| trace | `{mode:"local_required",directory:{base:"cwd",path:RELATIVE,parent:POLICY}}` |
| runtime | `current_pipeline.python.local.v1` |
| provider | `{mode:MODE,types:REQUIREMENTS,values:VALUES}` |

Provider MODE is `production` (empty VALUES; existing UUID/UTC providers) or
`controlled_test` (exact required capability names and checked typed values).
Provider types must match plan requirements and the existing runtime registry.
No arbitrary module/plugin or callback selection. Controlled values are visibly
test-only; production returned values are never recorded in launch configuration.

`launch_provenance.json` binds launcher, launch metadata and capability signature
bytes to the existing generation. Existing transport/boundary seals and generated
artifact/runtime/provenance checks remain in effect. Runtime loading rejects all
incompatible references/providers/policies before transport or semantic execution.
These are revision checks, not authentication against a hostile bundle writer.

## Paths and persistence

Paths use nonempty portable slash-separated relative segments. No absolute path,
drive/colon, backslash, empty segment, `.`/`..`, NUL/control character, or segment
ending in a space/dot. Spaces inside ordinary segments are permitted. Resolution
uses the actual process cwd and normal filesystem resolution (including existing
symlinks); it is not a containment sandbox. OS-specific invalid names/permissions
may still cause a checked launch failure. Absolute-path configuration is outside
this prototype, not required for the frozen local-process contract.

Store parent directories must exist; the store itself cannot be a directory.
Launch does not create a store or its parent. The already checked R5.35 policy
alone decides REQUIRE_EXISTING versus INITIALIZE_DECLARED_STATE, file-free missing
reads, and first-write realization. Trace directory policy is `create` (mkdir with
parents) or `require_existing`. State/evidence path overlap rejects. Required
local evidence is the sole supported mode; disabling trace cannot ground this
research prototype. Preflight failure emits stderr JSON `LAUNCH_FAILURE`, exit 4,
with no semantic invocation. No alternate semantic failure is manufactured.

## Evidence and environment

Each process allocates an invocation UUID and emits one exclusively created
`<trace-directory>/<invocation>.json`. Temporary internal semantic/transport paths
are allocated by bootstrap and removed afterward; they are not public parameters.
The bundle embeds the unchanged transport and semantic records together with
application/profile/generation/provenance/transport identities, PID, executable,
entry, exact argv/cwd/resolved paths, public stdout/stderr/exit and state digests.
The semantic record retains operation, input, outcome and actual external values.

No application configuration is read from environment. Ambient `LYKOI_R5_22_CAPS`
is overwritten with the checked provider descriptor before child execution; normal
OS environment remains available for the interpreter and temporary filesystem.
Arbitrary environment variables have no application-semantic configuration role.

The independent observer resolves paths from its expected configuration, captures
the actual Popen PID/command/cwd/public endpoints and durable pre/post bytes, and
locates exactly one newly emitted evidence file. The challenger reconstructs the
expected launch and transport identities from semantic source and CheckedPlans,
checks process/evidence correlation, then delegates to the existing independent
R5.35 and semantic challengers. Internal evidence alone is insufficient.

Separate verdicts: LAUNCH_PROFILE_CONFORMANT, TRANSPORT_CONFORMANT,
INPUT_BINDING_CONFORMANT, PERSISTENCE_BOUNDARY_CONFORMANT,
SEMANTIC_EXECUTION_CONFORMANT, OUTPUT_CONFORMANT; `launch_grounded` is separate.
Unreached layers are null. A checked profile can be structurally conformant while
launch fails a declared directory prerequisite; it has no grounded invocation.

## Scope

Launcher may locate, validate, configure, bootstrap and invoke. It has no semantic
AST interpreter, predicates, domain validation, migration/default/result rules,
collection manipulation or binding conversion. Native packaging, installation,
OS launch scripts, HTTP hosting, containers and production observability are
outside the prototype. Persistence concurrency/crash atomicity and hostile-runtime
attestation are not established by these endpoint observations.

Evidence and readiness decision:
[R5.36 review](../benchmark/results/phase5c/R5_36-CHECKED-PUBLIC-LAUNCH-PROFILE.md).
