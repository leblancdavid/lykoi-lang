# OpenCode Adapter Contract v1 — dependency analysis and bounded qualification

R5.89 defines allowlisted stateless producer inputs, structural output validation,
binding/schema receipts and independent WHAT-side verification. R5.91 replaces
HTTPS invocation with `opencode run --model github-copilot/claude-sonnet-4.6
--agent lykoi-ROLE --format json`, stdin, fresh temporary cwd and isolated config.
The unchanged `opencode_adapter.py` supplies exact role prompts, denies tools,
disables extra instructions, snapshots, title/summary and compaction, clears
inherited `OPENCODE_*` settings, and never attaches/resumes a session. It parses
JSON events, rejects tools/errors/missing sessions and extracts bound JSON.

OpenCode owns OAuth and transport. Compiler semantics, review/commit ordering,
approval, author bundles and hidden verification authority remain Lykoi's logic.
Neither an exact OpenCode executable nor an arbitrary version is sufficient:
the bounded interface above is what the experiment depends on.

The normative contract is `rehearsal/opencode-adapter-contract-v1.json` and its
procedure `src/lykoi_freeze/opencode.py`. It uses the actual unchanged invocation
method and exact prompts/config, observes argv/environment/stdin/cwd, validates
allowlists (including attempted candidate/hidden-plan insertion), exercises four
live synthetic bound-schema responses, exports only those created sessions to
check actual agent/provider/model/input, and requires distinct sessions. Synthetic
source and a qualification-only adversarial operator command ask for an outside
context canary at its actual synthetic pathname; no canary may be returned or
enter session messages and no tools may execute. Effective `debug config` must
confirm the exact role prompt, model route, empty extra instructions/plugins and
tool/permission restrictions. Production invocation stays unchanged.
Error/parser/binding negative controls are deterministic, not provider
failures induced by changing the frozen model route. Model output quality for a
real requirement is not certified by these interface probes.

Exact tool version/path/hash and session/instruction/input/output/model-route
provenance are retained. Raw provider stderr, credentials, auth stores and unrelated
sessions are never read/published. Export failures or route mismatch fail qualification.
Requested and session-reported model route are verified; immutable provider weights
are not exposed by the architecture. No equivalence claim for historical 1.1.25
is made without running this new contract against that installation.
