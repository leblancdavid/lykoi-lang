# R5.120 final preservation audit

Baseline HEAD: `493a376d001d8cd2928f7078f9e935db29c576f5`.
Initial working tree was clean. No staging or commit performed.

## Checks

- `git diff --exit-code HEAD -- src schema air generated tests benchmark experiments`
  exited **0**: all previously tracked implementation, semantic tooling, compiler,
  schema, canonical/generated models, tests, prompts, experiments and Phase 5/6
  benchmark evidence unchanged. Additive untracked R5.120 publications are reviewed
  separately; this command does not validate untracked additions.
- `git diff --check` exited **0**. Git reported normal LF/CRLF conversion notices,
  no whitespace errors. The final audit file uses ordinary LF text.
- Final R5.119A read-only revision verifier exited **0**, again confirming exact
  canonical/physical source, FRC, plan, evidence and publication identities. No
  prior acceptance outcomes or expectations changed.
- Reviewed `git diff`: five tracked documentation files have **50 additive lines**
  only: `AGENTS.md`, `README.md`, `docs/agent-workflow.md`,
  `docs/project-overview.md`, `docs/research-log.md`. Historical entries preserved.
- `git status --short` shows those five documentation updates plus only the new
  `benchmark/results/phase6/R5_120-REPORT.md` and `r5_120/` evidence directory.
- First-result Git blob identity observed immediately after persistence and again
  after checks/publication: **`ccf8cbeb3f4c9dae72a6d602d00324e3725d6831`**.
  The first result was never patched or rerun. This is a Git blob SHA-1 commitment,
  not an authority-1 identity or a claim of controller-enforced storage immutability.

## Publication blob commitments

Obtained using `git hash-object` (no `-w`, staging or commit). These bind the exact
published file bytes as Git blobs; approved candidate identities remain the
separate canonical SHA-256 commitments in ARTIFACT-INTEGRITY.json.

| File | Git blob SHA-1 |
| --- | --- |
| APPROVAL-RECEIPT.json | 33f6519a2a0ecc521eb888cb478196c8fa63fa4b |
| ARTIFACT-INTEGRITY.json | bf3a47967d2d7c5c639f36214475f1ddb99441e8 |
| SNAPSHOT.json | 56cd599ff4a3b9296cd02439524126a3f0c00a73 |
| RESEARCH-AUTHORIZATION.json | 85c11c07cd49b2dd4d0a37bf37b6a422bd3279d2 |
| PIPELINE-STAGES.json | 8565a5a0a76bf38c83d7490ad175289fa9f578a3 |
| P6_A03_FIRST_RESULT.json | ccf8cbeb3f4c9dae72a6d602d00324e3725d6831 |
| BASELINE-CHECKS.md | d721cc534fba580b27ed4bd63cf1aa6fab9d25b7 |
| ../R5_120-REPORT.md | 337d2ce958651097cde796e2ceb63baf332047cb |

No secrets, credentials, signatures or claimed authority events published. Source
content access limited to preserved P6-A03 preparation/revision artifacts; no other
curated requirement evaluated. Prior first results preserved. Kernel 26 unchanged;
no Redis-specific primitive, FRC/V1/prompt/verification change, generated patch,
simulation, Redis acceptance execution, remediation or linked retry.

**Stop:** R5.120 ends with its immutable authority-boundary result. Only legitimate
external authority provisioning and separate authorization can support a later
linked post-exposure attempt.
