# Frozen public rehearsal protocol — R5.91

Purpose: **future public rehearsal only**, separate from B03 and all benchmark freezes.
Configuration: **R5.91-PUBLIC-REHEARSAL-2**; exact identity is in the activation evidence.

1. Verify freeze integrity and the existing controller activation before introducing
   a requirement. Use `PublicController`, `Workspace`, `OpenCodeAdapter` and
   `PublicPipeline`; the controller refuses message/source registration before activation.
2. Introduce one genuinely new, reasonable public human requirement. Do not choose it
   specifically because it is known to fit the capability profile or to fail.
3. Admit it through the normal requirements wizard. Permit clarification questions
   and actual human answers. Model outputs remain untrusted candidates; explicit human
   WHAT approval and existing controller gates remain required.
4. Use fresh role sessions, frozen role instructions and configuration. Reviewer inputs
   contain source/authorized evidence only; commit SOI before reconciliation. Authors
   receive only the restricted bundle after plan sealing and implementation grant.
5. Run the frozen pipeline without changes to semantics, mappings, prompts, schemas,
   adapters, profile, BDI/adequacy, compiler, verifier or containment after seeing the
   requirement. The deterministic WHAT-side verifier remains the acceptance authority;
   an AI plan is only a reviewed candidate, never automatic authority.
6. Preserve the **first terminal result**, its exact artifacts and controller events.
   Use existing failure codes and stage attribution: clarification/disputed coverage,
   unsupported BDI or inadequate implementation, `UNREPRESENTABLE_SOURCE /
   NO_QUALIFIED_COMPLETE_MAPPING`, plan coverage failure, freeze/grant failure,
   `AUTHOR_CAPABILITY_FAILURE`, compile/runtime/containment failure,
   `BEHAVIORAL_VERIFICATION_FAILURE`, or `BEHAVIORALLY_VERIFIED` as applicable.
   Refusal and successful implementation are both valid experimental results.
7. No post-task repair belongs to that original result. Any later diagnostic or changed
   configuration is a separately identified experiment. Stop after the one rehearsal.

Model/provider/configuration identity is retained as run provenance and frozen
experimental configuration. A changed model configuration creates a different
experimental configuration. Lykoi artifact semantics and authority do not derive
from model identity. No general qualification registry or interchangeability guarantee.

All four roles currently use the same `github-copilot/claude-sonnet-4.6` configuration
via OpenCode OAuth. Claim: **separate-context/source-blind-to-candidate workflow**;
not independent model cognition. Correlated errors remain possible. Provider weights
and an unexposed model build/version are not frozen. Model aliases are recorded honestly.

The R5.89 narrow envelope and the exact R5.87 wizard's historical refusal remain.
Local Python containment retains its declared trusted-generated-program scope.
Future legacy code/tests/docs/behavior → candidate recovered FRC remains compatible
as an unimplemented extension, with no new authority path.

R5.91 does **not** select, prepare or run the future requirement. B03 remains pristine,
unevaluated and unexposed, all counters zero; R5.83-CANDIDATE-1 is unactivated.
