# R6.5 publication and preservation verification

## Evidence boundary

Publication checks inspect documentation, static source identities and preservation
only. They import no Lykoi modules, call no semantic pipeline, author/compile no
candidate, run no runtime/acceptance suite and access no P6-A05 content. No verifier
implementation or publication recorder is added. Read-only Python standard-library
commands in the session compute hashes and assertions; Git commands inspect scope.

[PUBLICATION-IDENTITIES.json](PUBLICATION-IDENTITIES.json) retains baseline digests,
the static sources underlying E1–E9 and the four primary publication hashes.
The evidence manifest and this verification note are not self-hashed, avoiding
recursive identities. SHA-256 entries bind exact working-tree bytes (including
line endings); no signature, independent review or behavioral proof is claimed.

## Checks and outcomes

| Check | Outcome / bounded meaning |
| --- | --- |
| Baseline scope | Initial R6.4 working changes became existing clean commit `402963b` before this round's edits. This round made no commit. |
| Implementation preservation | 129 tracked files under `src/`, `schema/`, `air/`, `generated/` retain the baseline aggregate SHA-256. Includes compiler/lowerer/runtime/verifier and canonical model files. |
| Approved/historical preservation | 34 files: R6.1–R6.4 reports and their round directories (excluding `__pycache__`), plus R5.114 kernel accounting, retain the baseline aggregate SHA-256. Fixture/approval identities remain byte-identical. No historical content is amended. |
| Other tracked changes | Git diff contains exactly seven navigation/log documents. Existing line sequences are preserved with insertions only. All other tracked paths, including historical evidence outside the hashed subset, have no Git change. |
| New-file scope | Only the R6.5 report and `r6_5/` Markdown/JSON publications; no program/plan/test/implementation files. Nothing staged by this round. |
| Static evidence identity | All ten E1–E9 source-file SHA-256 entries match inspected bytes. |
| Publication identities | All four primary report/matrix/candidate/reuse file hashes match the published manifest. |
| Matrix completeness | Exact IDs A1–A5, B1–B5, C1–C5, D1–D5, E1–E5, no duplicates: 25 rows; classes 1/2/3/4 = 7/6/7/5. Not a coverage score. |
| Kernel record | Preserved accounting has `final_count: 26`, `additions: []`. |
| Local links | All relative Markdown links in the six new Markdown/JSON publication documents resolve to existing files; links are checked for existence without opening their targets. |
| Whitespace | `git diff --check` passes; new Markdown has no trailing whitespace or conflict markers. |

The first insertion-preservation assertion used Python's platform-default decoding
for Git stdout and falsely rejected Unicode-bearing `AGENTS.md`. Re-running with
explicit UTF-8 decoding passed; no document or implementation repair was required.
This is a publication-check issue, not a semantic/behavioral result.

## Reproduction of identities

For each individual entry, SHA-256 is over raw file bytes. Aggregate digests use:

1. Implementation paths from `git ls-files -- src schema air generated`.
2. History paths enumerated explicitly above; never recurse over all Phase 6 or
   curated source material.
3. For each path, obtain raw-byte SHA-256; construct a mapping of relative POSIX
   path → hex digest, ordered by path.
4. Serialize with Python standard `json.dumps(mapping, sort_keys=True,
   separators=(",", ":"))`, encode UTF-8 and SHA-256 the result.

Recorded baseline implementation digest:
`ceb4636771eca5081639fbdcf782c7046a3221bd2673fbb9fd638dd5e8e14dd3`.
Recorded history/accounting digest:
`ced8024a5addf609ee021782a1775ef2b7f860f820e4ae9ab674c4b7bb7ac9ae`.

Read-only Git scope commands used:

```powershell
git status --short
git log --oneline -3
git diff --name-only
git diff --cached --name-only
git diff --check
```

Python assertions recompute these digests, the manifest entries, matrix IDs/classes,
insertion-only navigation changes and local-link existence. These commands do not
need compiler credentials, provider credentials or an execution environment.

## Terminal boundary

`R6_5_SEMANTIC_EXTENSION_REQUIRED` is an architectural, normative-vocabulary
classification. All proposed architecture/semantic/evaluation executions **NOT_RUN**;
P6-A04 acceptance executions **0**. No P6-A05 access. No minimality theorem,
benchmark score, behavioral success, native first-blocker or new approved construct.

**Publication complete; stopped pending explicit owner authorization.**
