# Direct generation versus tool-assisted construction

Both are plausible supervised objectives. Existing evidence does not select a winner.
The R6.23/R6.25 small-model failures motivate familiarity training, not proof that
tool calls or fine-tuning will solve authoring. GPT success is not small-model evidence.

| Property | A: direct symbolic output | B: actual typed tool trajectory |
|---|---|---|
| Input | Requirement, profile/schema/foundation version, permitted vocabulary/closure | Same plus exact tools, arguments schema, current state and previous feedback |
| Target | Authored symbolic package or intent, not generated Python | Actual assistant function name/typed arguments in chronological order |
| Evidence sidecar | Validation, domain-specific observations, acceptance/replay identities | Same plus tool result/error, correction edges and final artifact |
| Available positive source bundles |17 for narrow experimental profile |16 with actual callable MCP logs; L36 broker can train a separately labeled action format |
| Completeness | Requirement/target joins simpler; production and VM formats must remain separate | Visible tool exchange complete locally; provider request serialization/hidden context unavailable |
| Serialization | Strict JSON, array order significant, content pins bind names/revision/closure | Several distinct historical interfaces and round prefixes; do not silently unify their semantics |
| Length | Smaller target; long dependency closures may exceed context | Tool feedback/history can dominate tokens and exceed 1–2K windows |
| Corrections | Separate bad-program+diagnostic→repaired-program objective | Native feedback supports real corrections; few diverse successful correction chains |
| Risks | Memorizing opaque identities/constant templates; valid syntax but wrong requirement | Memorizing tool names/pins, redundant retrieval, long feedback; whole-definition admission is not node-wise construction |

R6.37–R6.40 admission frequently sends an entire definition/batch in one call. This
is tool-assisted **lifecycle construction**, not evidence of an extensive dataset
for incremental per-expression R6.25 declaration/operation/result construction.
R6.25's attempt remains incomplete. True node-wise incremental training needs new
observed trajectories; a final AST may not be reverse-engineered into an alleged
model tool transcript.

## Prospective record contract (design only)

Common metadata: `example_id`, `family_id`, `lineage_id`, `profile`, `foundation_sha256`,
`requirement_sha256`, `vocabulary_sha256`, `schema_sha256`, `artifact_sha256`,
`validation_ref`, `functional_ref`, `replay_ref`, `quality`, `provenance_limits`,
`split`, `license_or_permission`, and source-byte identities. Null means unavailable.

A stores exact requirement text and allowed vocabulary as input, symbolic authored
form as output; evidence stays outside the prompt if unavailable to a future author.
The deterministic adapter may seal new definitions **after** model authorship.
Dependency pins remain exact when retrieved/supplied. Do not train a model to guess
its own SHA256 or replace runtime pins with prose. Generated code, expansion maps
and acceptance outputs are evidence, not extra independent solution examples.

B stores visible `messages` and `tools`: assistant `tool_calls`, parsed typed
arguments, call ID, tool feedback and final artifact. Preserve causal sequence,
multiple calls, tool-result association, rejection and rollback. Mask system/user/tool
text from loss; train accepted assistant actions and actual successful corrections.
Failed assistant actions remain context or an explicitly separate diagnostic objective,
not positive answers. Do not include oracle feedback unavailable during authoring.

Use source canonicalization only for metadata/hashing, not to reorder executable
arrays or malformed-input diagnostic order. Verify strict duplicate-key/integer
serialization and versioned schemas. The provider chat template/tokenizer will need
separate future qualification; current raw exports are not that serialization.
Crop neither requirements nor closures to fit: split only at genuine action/state
boundaries with sufficient preceding context, or reject overlength records.

**Recommendation:** retain paired A and B views of each admitted episode. Start
data preparation with A as the compact audit anchor and B as a faithfully observed
trajectory. A/B records count as one diversity unit and stay in the same split.
For an eventual format experiment use equal target-token/training-compute budgets,
same family groups, and direct versus callable-tool evaluation crossed separately.
No hidden model reasoning, unobserved rationale, or reasoning-token count becomes
supervised reasoning text.
