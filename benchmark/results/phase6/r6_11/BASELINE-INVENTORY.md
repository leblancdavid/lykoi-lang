# R6.11 baseline and capability inventory

Initial `git status --short` was empty. HEAD is
`ba2d4244b367f0bf87bb49f9e9c1ed5b81e04ebe`, root tree
`a35963b9c653e99a8d6c564df2c31930363d5921`.
BASELINE.json was recorded after adding pilot preparation files; its status correctly
shows the new untracked pilot directory. No production/history edits preceded it.
The baseline pins 446 tracked files and verifies 47 historical publication hashes.
Scope is explicit: curated source trees are not traversed or content-hashed.

## Production

R5_114-KERNEL-ACCOUNTING.json reports final_count=26, no additions. Verified exact
accounting bytes and production src/schema/air/generated/tools. Compiler compatibility
version 0.3.0, serialized model 0.3, normal dispatcher LykoiProgram-1. The architectural
count is not 26 unrestricted operations or a minimum. K01–K26:

1. record schema
2. field
3. finite sequence
4. var
5. literal
6. equals
7. and
8. not
9. contains
10. selection
11. trim
12. map(trim)
13. stable_unique
14. transition
15. instant
16. before
17. operation contract
18. cardinality
19. input presence
20. typed resource/capability authority
21. durable state
22. atomic commit
23. finite nonempty-path reachability
24. checked integer addition
25. fixed-duration instant displacement
26. checked elapsed-day duration conversion

Normal profiles support bounded decoded state, collections, predicates, queries,
relationships, controlled resources and one-store atomic effects. They lack an
admitted raw-byte recognition/codec profile for these contracts. No production
program was authored or compiled for scoring. Canonical validation/safety and
34 production/Phase 5 baseline test methods were freshly checked separately.

## Experimental

R6.10 semantic-plan-1 is separate from production: bounded cursor nodes, explicit
byte recognition, fixed unsigned codecs, expressions, ordered traversal, checks,
construction and layout. Maximum 64 structural nodes, depth 16, default eight
occurrences; this pilot tightens input to 64 bytes. CONTRACT-1.md and interpreter.py
were read; no historical plan was copied into a scored candidate. The new plans
use 5/8/9/10 nodes; modifications use 10/11. Their unused required encode node is
validated, but assembly is disabled because the contracts return structured values.
Full static field/union typing and exact lowering-cost correspondence remain open.
Fresh original VM regression suite passes 82 methods; that suite is not pilot scoring.

## Existing benchmark and formalization machinery

Phase 5 benchmark/README.md documents conventional Python, external subprocess
oracles, historical cumulative tracks and frozen identities. Existing harness,
evaluation, conventional source and protected history bytes are pinned, not modified.
The new pure-byte pilot has its own external-process acceptance recorder; historical
task-manager oracles are not repurposed into new requirements.

FormalRequirementContract-0.1 in benchmark/evaluation/formal_requirements_r5_80.py
provides closed envelopes, source hash/quote binding, relation records and review
separation. Four synthetic envelopes validate using existing `effects` bookkeeping
relations carrying the full observable specification. That does not establish native
structural coverage, BDI/adequacy/V1 projection or production approval. No pipeline
failure is waived. The prospective directly executed experimental-plan pilot is
explicitly authorized; production-path downstream stages remain NOT_REACHED.

## Conventional tools and model configuration

Observed Windows 11 AMD64 (10.0.26300), CPython 3.14.3, Git 2.52.0.windows.1,
PowerShell 7.6.6, installed OpenCode CLI 1.18.32. CLI version does not attest the
active harness build. Python subprocess/importlib/json, unittest and ordinary
standard-library development are available. No third-party dependency is installed.

Active session reports OpenAI `openai/gpt-6.1-sol`, model `gpt-6.1-sol`. All authoring
uses this same session; no separate provider request or configuration change.
Effective reasoning effort, temperature, sampling seed, context size, input/output/
reasoning tokens, billing and server-side hidden context are not exposed. Other
configured providers/models were not enumerated: no safe targeted configuration
inventory was available without inspecting private settings. No credentials are read
or published. Exact task/protocol hashes are available; full effective prompt identity
is unavailable because inherited system/tool/conversation context is not exportable.
