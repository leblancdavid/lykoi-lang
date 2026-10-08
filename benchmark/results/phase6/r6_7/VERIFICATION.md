# R6.7 publication verification

Publication-only checks; no proposed semantics, Lykoi modules, compiler, lowerer,
runtime, verifier or benchmark acceptance code is executed by these checks.
Baseline: `c1c31072cf38907e81f55a4d9463e03012b872c3`. Initial status clean.

## Recorded checks

1. Before review: six raw-byte SHA-256 identities matched the R6.6 publication
   manifest. Before comparison: protocol and verbatim reviewer hashes recorded.
2. Tracked changes limited to AGENTS.md, README.md, docs/agent-workflow.md,
   docs/project-overview.md, docs/research-log.md and docs/decisions.md, all insertion-only.
   Every other tracked file remains baseline-exact, including implementation,
   kernel accounting and historical R6.3–R6.6 reports/directories. Git path metadata
   was used for preservation, without reading curated-source contents.
3. Exact untracked publication inventory: R6_7-REPORT.md and twelve r6_7 files
   (eleven Markdown documents plus PUBLICATION-IDENTITIES.json). No other new files
   in the workspace. The integrity helper exists only in the approved temporary
   work directory; it does not become project implementation or research semantics.
4. Every local Markdown target in the new report/audit documents and inserted
   guidance resolves; new files end in newline and pass explicit no-index checks.
5. `git diff --check` passes for tracked guidance; explicit `git diff --no-index
   --check -- NUL <new-markdown-file>` checks cover untracked publication files.
   Git may report LF-to-CRLF normalization notices, not whitespace errors.
6. PUBLICATION-IDENTITIES.json covers raw-byte identities of report, ten audit
   documents and six guidance files; it excludes itself and this terminal record
   to avoid self-reference. Input freeze and boundary metadata are also checked.

## Reproduction

The temporary publication checker uses Python stdlib pathlib/hashlib/json/re and
Git subprocesses only, with an explicit publication-file allowlist. It compares
the frozen six identities, protocol/reviewer hashes, current HEAD, insertion-only
tracked differences, exact new-file inventory, local links, whitespace and manifest.
It reads no application/curated source, imports no Lykoi code and executes no semantics.

```
python C:/Users/lblan/AppData/Local/Temp/opencode/verify_r6_7_publication.py --hashes
python C:/Users/lblan/AppData/Local/Temp/opencode/verify_r6_7_publication.py
git diff --check
git status --short
```

SHA-256 values can be rechecked independently using any raw-byte digest tool;
the R6.6 manifest supplies the six input identities and R6.7 manifest the publication
identities. These are local integrity checks, not signatures, semantic proofs or
independent execution evidence. No commit is created.

## Results and terminal boundary

The initial new-file whitespace helper expected exit 0, but Git no-index returns
1 for differences with no whitespace errors; the helper was corrected to accept
0/1 only with empty diagnostic stdout and normalization notices only. No published
semantics or historical file changed in that correction. A terminal exposure
clarification changed the final classification to R6_7_INDEPENDENCE_NOT_ESTABLISHED;
protocol/reviewer original hashes remain exact. Analysis remains qualified.

Final publication checker results:

| Check | Result |
| --- | --- |
| Six frozen R6.6 raw-byte identities | PASS |
| Original protocol and precomparison reviewer hashes | PASS |
| Six insertion-only guidance changes; all other tracked files exact | PASS |
| Exact new publication inventory | PASS |
| 24 new/local publication and guidance links | PASS |
| Tracked git diff --check and explicit new-file whitespace checks | PASS |
| 17 publication SHA-256 identities and terminal metadata | PASS |
| Current HEAD remains baseline; no commit made | PASS |

Semantic executions 0;
benchmark solutions authored/compiled 0; P6-A04 acceptance checks 0; P6-A05 access
none. All previous challenge executions remain NOT_RUN. Kernel 26, implementation,
history and approvals preserved. Provider-neutral semantics unchanged.

Stop after publication; prospective specification repair needs explicit authorization.
