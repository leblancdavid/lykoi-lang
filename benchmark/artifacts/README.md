# Lykoi experiment artifact storage audit — 2026-10-07

## Current automatic storage workflow

The original audit below is preserved. The subsequent R5.109 transfer export grew
to 151,027,731 bytes, demonstrating that per-filename LFS rules were insufficient.
The current `.gitattributes` now automatically routes these families to LFS for
**all rounds and nested result directories**:

```gitattributes
benchmark/results/**/*-EVIDENCE*.json filter=lfs diff=lfs merge=lfs -text
benchmark/results/**/*-B[0-9][0-9]-RESULT.json filter=lfs diff=lfs merge=lfs -text
```

This preserves raw evidence bytes, research hashes and JSON-reading tools. It
handles synthetic/initial/final/transfer evidence and per-case terminal results
without per-round edits. Captures, locks, compact manifests, comparisons, reports,
source and canonical models stay ordinary Git. Small evidence records in these
bulk families use LFS too; attributes select by path, not file size.

One-time checkout setup (Git LFS must be installed):

```powershell
git lfs install
python benchmark/artifacts/git_storage.py install-hook
```

The second command installs a local pre-commit check and the LFS upload hook,
without modifying Git configuration. It refuses to replace a custom pre-commit
hook. If one already exists, invoke `python benchmark/artifacts/git_storage.py check`
from that hook. Re-run setup after cloning or moving to a different Python path.

Then stage intended changes and commit/push normally. Commit the updated
`.gitattributes` with the evidence. Re-add already-staged raw files after the new
attributes are in place. Older matched regular-Git evidence can appear modified
as its representation changes to an LFS pointer; ordinary re-addition migrates
the next revision without altering local evidence or historical commits.

The pre-commit guard checks **actual index blobs**, including files outside the
LFS families. It rejects blobs at least 100 MiB and staged raw content at a path
marked `filter=lfs` in the **staged** attributes. This catches missing filters,
outdated staging and new artifact families locally. Manual/CI command:

```powershell
python benchmark/artifacts/git_storage.py check
```

For a genuinely new bulk naming family, add a family-level LFS rule once. Do not
silently discard observations. Disposable scratch copies still belong in the
narrowly ignored directories below. This workflow prevents ordinary Git size
failures; it does not eliminate LFS storage/bandwidth quotas or remote upload errors.

## Findings

The [compact inventory](storage-audit-2026-10-07.json) records **3,051 files /
1,378,939,606 bytes** in `benchmark/results/`, `experiments/`, `generated/` and
`rehearsal/`, including ignored Python caches. It inventories **38 files at least
1 MiB**, with original byte sizes and SHA-256 hashes, and hashes smaller
R5.106/R5.107 records and reviewed generator dependencies. It excludes Git/LFS
object storage, application/compiler source outside the listed dependencies,
benchmark harness/conventional source, and the audit's own output directory.
This is a working-tree snapshot; Git HEAD alone cannot reproduce it.

Five JSON files exceed GitHub's 100 MiB ordinary Git limit. The six largest files
account for **1,066,214,986 bytes** (77.3% of audited bytes):

| File in `benchmark/results/phase5c/` | Original MB | Compact JSON MB | Gzip level 6 MB | Retention |
| --- | ---: | ---: | ---: | --- |
| `R5_107-SYNTHETIC-FINAL-EVIDENCE-2.json` | 284.65 | 273.43 | 15.94 | Final generic observations; preserve |
| `R5_107-SYNTHETIC-FINAL-EVIDENCE.json` | 242.26 | 231.75 | 14.08 | Earlier pre-transfer observations; preserve |
| `R5_107-SYNTHETIC-EVIDENCE.json` | 195.24 | 185.73 | 11.53 | Initial development observations; preserve |
| `R5_106-SYNTHETIC-EVIDENCE.json` | 125.91 | 117.42 | 2.19 | Includes historical failed oracle case; preserve |
| `R5_106-SYNTHETIC-FINAL-EVIDENCE.json` | 125.91 | 117.42 | 2.19 | Final generic observations; preserve |
| `R5_107-TRANSFER-EVIDENCE.json` | 92.25 | 72.05 | 3.34 | Twenty original exposed-transfer results; preserve |

MB means 1,000,000 bytes. Compression was **measured in memory**; no evidence was
compressed, reformatted, moved or deleted. Together these six originals would
compress to **49,270,716 bytes** with the measured gzip encoding, a 95.4% reduction.
Compacting JSON alone leaves all five oversized files above the limit.

### Why they are growing

`src/lykoi_workspace/interface_corpus.py:77–86` builds a long source statement
containing the complete contract, then repeats it in each obligation's
`source_quote`. `R5_103-evaluate.py:48–54` exports candidate, formalization,
inventory and the complete pipeline audit together. `Pipeline.audit()` retains
the full dependency graph and authority journal for reconstruction after restart.
Later stage artifacts repeat the facts and statements.

In the first case of the largest file, one **44,917-byte source string occurs
1,474 times**, accounting for 66,162,741 duplicate UTF-8 bytes before JSON escaping.
The compact audit alone is 54,494,144 bytes, with 22 artifacts. Candidate,
formalization and source inventory each occupy about 4.5 MB. The inventory records
artifact-type sizes: BDI, adequacy and V1 contain large repeated payloads, not just
generated Python target text.

`R5_107-transfer.py:171,178` publishes individual results and embeds the results
again in an aggregate. Future aggregates could reference immutable per-case
records by hash. Historical wrapper timestamps and exact bytes still matter.

## Reproducibility and retention

| Artifact family | Reproducible portion | Source-of-truth portion / disposition |
| --- | --- | --- |
| `generated/task_manager.py` and manifest (28,686 bytes) | Deterministic backend from canonical model and matching compiler | Keep existing committed regression fixtures; future scratch copies may be ignored |
| Python caches (523,930 bytes) | Interpreter caches from source | Already ignored; genuinely disposable |
| Synthetic JSON (1,041,086,689 bytes / 13 files) | Captures/plans and derived payloads with exact historical inputs/code | Original failures, timestamps, envelopes, journals and observations; preserve originals |
| Transfer evidence and case results (240,243,424 bytes / 25 files) | New evaluation from fixed captures, implementation and plans | Original terminal receipts, stdout/stderr/state checks and ordering; preserve |
| Candidate JSON (11,599,049 bytes / 100 files) | Some builders recreate structural inputs | Exact captured interpretation, source linkage and pre-outcome commitment; keep in Git |
| Locks, verification, audits, reports, interruptions and matrices | Some summaries derivable from retained inputs | Hashes, chronology, failures and first classifications; keep compact originals in Git |
| `experiments/` (24,348 bytes) and older inventories/traces | Replay only with historical prerequisites | Hash-pinned models/plans and execution provenance; preserve |
| Other older research records | Not established by this audit | Frozen inputs, evidence and checkpoints; preserve pending individual review |

**No large whole-file artifact was proven safe to discard.** Having a generator
does not establish exact historical replay. R5.106 implementation differs from
current R5.107 code; earlier R5.107 pre-transfer versions cannot be replaced by
the latest corpus builder's output. Evaluated uncommitted implementation bytes
must be retained separately from the lock's `git_head`.

The audit verifies **215 historical file pins** from R5.107 generic lock 3 and
**58 evidence pins** from the original R5.107 final audit: no missing/mismatched
files. The compact inventory extracts original case outcomes, stages, counts and
metadata from the six profiled files; it does not replace their full receipts or
assert that original journals can be regenerated.

## Prospective `.gitignore` policy

Implemented narrow rules reserve these new directories for **recreatable scratch
output**, not published research records:

```gitignore
/benchmark/artifacts/local/
/experiments/local-artifacts/
/rehearsal/local-artifacts/
```

Future disposable generated targets, scratch databases, exploratory replay dumps,
profiling exports and duplicate diagnostic views may go there after their source
inputs, implementation/tool versions and recreation commands are recorded outside
the ignored directory. Claim-supporting original observations must not exist only
there. Existing drivers retain their historical output locations.

Keep manifests, captures, requirements, policies, plans, hashes, instructions,
first-result receipts, failures and reports visible to Git. Do not blanket-ignore
`*.json`, `*-EVIDENCE.json`, `benchmark/results/`, or `generated/`. A hash is an
integrity commitment, not a backup. Ignore rules do not remove tracked history.

The five oversized originals identified in this audit remain in LFS, now covered
by the recurring family patterns above. Future original evidence in these families
is covered automatically; other families need a family-level LFS rule or a durable
archive with a checked-in retrieval record, rather than being ignored.

### Proposed future evidence format (not implemented)

1. Commit a compact per-run manifest: input/implementation hashes, source
   revision and dirty-state snapshot, interpreter/tools, commands, outcomes,
   first terminal classification, raw evidence size/hash and archive locator.
2. Preserve original observation bytes in lossless gzip or LFS. Record raw and
   archive SHA-256/size, codec/version and retrieval instructions. Verify
   decompression against the original raw hash before migration. Preserve current
   canonicalization and historical pins.
3. Store source text, models, plans and artifact payloads once by hash; future
   manifests reference them. Preserve exact authority envelopes and journal
   ordering. Deduplication needs an explicit export/reader format.
4. Publish compact per-case results once; aggregates reference their hashes.
   Expanded transient views belong in the ignored scratch directories.

No archive migration, generator change or historical rewrite is part of this audit.

## Verification and reproduction

From the repository root, with Python 3.10+ and Git, recheck the saved sizes/hashes:

```powershell
python benchmark/artifacts/audit.py --verify benchmark/artifacts/storage-audit-2026-10-07.json
```

To create a new audit, select a fresh filename; publication refuses overwrites:

```powershell
python benchmark/artifacts/audit.py --output benchmark/artifacts/storage-audit-NEXT.json
```

The audit scans ignored files too, profiles JSON of at least 50 MiB, measures gzip
level 6 and hashes large files in chunks. It loads each profiled JSON individually;
profiling requires more memory than a size scan. For hashes without JSON profiling,
set `--profile-mib` above the largest artifact, e.g. `--profile-mib 1000000`.

### Recreate a disposable canonical backend copy

```powershell
$env:PYTHONPATH='src'
New-Item -ItemType Directory -Force benchmark/artifacts/local
python -m air_compiler.cli validate air/task_manager.json
python -m air_compiler.cli generate air/task_manager.json benchmark/artifacts/local/task_manager.py
```

Matching model/compiler bytes are prerequisites for byte equivalence. Compiler
regression tests compare committed generated output and manifest with the model.
Keep `generated/` intact; the ignored copy is only a scratch output.

### Replay cases (new observations)

Use a separate scratch checkout containing exact pinned implementation/input
bytes, not merely the recorded Git HEAD. Verify each `implementation` hash in the
applicable lock and retain historical dependencies in the driver's import chain.
Match the recorded runtime/tools for historical behavior. Fresh timestamps, IDs,
subprocess paths, random IDs and clock observations can differ on replay.

| Original family | Inputs | Evaluator / original publisher |
| --- | --- | --- |
| R5.106 final synthetic | `predicate_corpus.py` (`captures`, `plan`), exact R5.106 code and final verification 2 | `R5_103-evaluate.py` (`evaluate`); `R5_106-generic.py` |
| R5.107 final synthetic 2 | `interface_corpus.py` (`captures`, `plan`), lock 3 code and final verification 2 | `R5_103-evaluate.py` (`evaluate`); `R5_107-generic.py` |
| R5.107 transfer | Exact `R5_107-Bxx-CANDIDATE.json` `producer_capture`/`external_plan`, corpus lock and generic lock 3 | `R5_103-evaluate.py` (`evaluate`); `R5_107-transfer.py` |
| Initial/earlier synthetic | Corresponding earlier captures/code from before later changes | Latest builders are not exact reproduction recipes |

Replay harnesses can import `evaluate`, pass a selected captured candidate/plan,
and publish a new result under an ignored scratch path. Transfer should read the
fixed candidate instead of rebuilding its interpretation. Do not invoke original
publishers in the evidence directory: they use exclusive writes and also publish
implementation/corpus locks. A new replay lock cannot replace an original lock.

Historical replay was **not run**. This driver mapping is a recipe with explicit
prerequisites, not a successful replay claim.

### Checks completed for this audit

- All **132** listed file sizes/hashes verified after documentation and ignore edits.
- Original historical/evidence pin checks: **215 + 58** matches, no missing files.
- Three representative scratch paths are ignored; nine representative evidence,
  source and audit paths remain visible to Git, including tracked paths checked
  with `git check-ignore --no-index`.
- Canonical backend regenerated into the approved external temporary directory;
  its raw Git blob hash matches `generated/task_manager.py` byte-for-byte.
- Scoped whitespace checks passed for the edited storage documentation and ignore
  rules. R5.107's previously recorded frozen product-code whitespace defect remains
  outside these storage edits.

New audit Python/JSON/Markdown use explicit LF attributes so the audit tool's
recorded hash survives normal checkout on Windows. Historical artifact attributes
and evidence bytes were not rewritten by this audit.
