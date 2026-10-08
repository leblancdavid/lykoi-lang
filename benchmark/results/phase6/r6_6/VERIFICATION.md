# R6.6 publication integrity and preservation verification

## Scope

Checks cover publication bytes, inventory, relative-link existence, whitespace and
Git preservation only. They do not execute candidate interpretation/codec relations,
import Lykoi modules, run acceptance or inspect P6-A05 content. No verifier/compiler/
runtime implementation is changed. Read-only standard-library publication assertions
are run from the pre-approved temporary directory, not added to Lykoi source.

Initial status was clean at `17b09e30c5450920710761321d676cbab92ecd5e`.
Baseline Git object IDs (metadata, not curated content inspection):

| Scope | Baseline object ID |
| --- | --- |
| src | 0be82961e9b0f7748defcca7add66bb17c007eba |
| schema | 8c04839087c76ab111e1eabb05b3e14e6b36ca1c |
| air | c7abd1483a14cf0c1ca21dd8d2edd3ee3db7ca39 |
| generated | d666daef4f362b2d4423e0be1942954ad4846bed |
| Historical Phase 6 tree | bc9b249ebf83fe76b99a9096d9d57c27e09fe59f |
| R5.114 kernel accounting blob | cb0f5c566149fae770e270bdbe71d456a03fe8b9 |

The Phase 6 tree is a baseline identity; new untracked R6.6 publications do not
rewrite that tree or any historical file. Object IDs are Git SHA-1 identities;
primary publication identities use SHA-256 over exact raw working-tree bytes in
[PUBLICATION-IDENTITIES.json](PUBLICATION-IDENTITIES.json). This note and manifest
are not self-hashed, avoiding recursive identities. Hashes are not signatures,
independent review or behavioral evidence.

## Checks and results

| Check | Result / bounded claim |
| --- | --- |
| Git scope | Exactly seven tracked navigation/log files changed: AGENTS.md, README.md, benchmark/README.md, docs/agent-workflow.md, docs/decisions.md, docs/project-overview.md, docs/research-log.md. |
| Insertion preservation | Every original line remains in order in each of the seven files; no historical section replaced. |
| Protected implementation/history | No tracked changes outside those seven files; no staged changes. src/schema/air/generated and all historical research, sources, approvals and identities remain unchanged. |
| New file inventory | Exactly R6_6-REPORT.md plus seven files under r6_6/: five content documents, this verification note and the identity manifest. No model, plan, program, test or runtime file added to the workspace. |
| Kernel accounting | Preserved JSON has final_count=26 and additions=[]; no accounting amendment. |
| Publication identities | Six primary SHA-256 entries recompute exactly (report, definitions, witnesses, adversarial matrix, alternatives, obligations). |
| Document inventory | Matrix has nine format/challenge rows and X01–X16; obligations O01–O10; alternatives include A/B/C and all nine requested criteria. Counts describe specification inventory only. |
| Links | Relative links in the eight new publications resolve; targets checked for existence without opening them. New tracked links likewise resolve. |
| Whitespace | git diff --check passes. All eight new files checked for trailing whitespace and conflict markers. |

Read-only Git checks: `git status --short`, `git diff --name-only`,
`git diff --cached --name-only`, `git diff --check`; HEAD/object metadata captured
with `git rev-parse`. Publication assertions use explicit UTF-8 decoding for Git
prose and raw bytes for SHA-256, avoiding platform-default text decoding.

The first publication check stopped on the manifest link before the manifest had
been created. The preliminary check was adjusted to defer only that missing target;
after manifest publication the full link/identity assertions were rerun without
deferral. Git also reports the configured future LF-to-CRLF conversion for navigation
files; whitespace checks pass and no Git configuration or historical bytes changed.

## Evidence limitations and stop

No implemented behavior or semantic proof is established by these checks. Designed
witnesses and adversarial outcomes **NOT_RUN**; proposed semantic, benchmark authoring,
compilation and P6-A04 acceptance executions **0**. No P6-A05 access, independent
cognitive review, provider requirement, permission change or commit made by this round.

`R6_6_COMPOSITION_CANDIDATE_SUPPORTED` is specification-level support for further
investigation within declared bounds. **Publication complete; stopped awaiting explicit
authorization for the recommended independent specification reduction audit.**
