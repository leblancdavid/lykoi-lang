# R6.9 reviewer input-package specification 1

The `package/` directory is a reproducible **preparation export**, never dispatched.
`publisher-provenance.json` is outside it. Its overall identity is SHA-256 of
canonical `manifest.json`; each payload has its own raw-byte hash and size.
Canonical JSON is ASCII, sorted keys, compact separators, no NaN, one terminal LF.
Payloads retain selected source bytes, including source newline conventions.

## Contents and provenance

- `candidate.md`: frozen R6.6 sections 2–6, exact value/plan/decode/codec/assembly/
  error/budget definitions. Section 1's retrospective reduction findings are omitted.
- `formats.md`: frozen CFG66, DSV66 and BXC66 specifications, including original
  author derivations as claims to challenge. The sole Markdown link is renamed to
  `candidate.md`. No format is implemented or executed.
- `kernel.json`: K01–K22 definition cells selected from the pinned historical audit,
  without outcome/implementation/benchmark columns; K23–K26 point to supplied
  normative excerpts. Construct count stays 26.
- `compatibility.md`, `values.md`, `inputs.md`, `predicates.md`, `interfaces.md`,
  `references.md`, `atomic.md`, `computation.md`, `primary.md`, `effects.md`,
  `history.md`: selected existing-kernel interface definitions. Earlier profile
  restrictions retain their historical scope; explicit later definitions refine them.
- `questions.md`: neutral questions and proof obligations, with no preferred verdict.

`tools/reviewer_isolation/prepare.py` freezes every source hash and inclusive line
range. `publisher-provenance.json` maps local file IDs to repository paths, hashes,
slices and transformations. It is publisher-only material. Original source files
are preserved. No R6.7/R6.8 document, judgment, recommendation, report or guidance
is exported. No previous-round input manifest is sent to a reviewer.

## Reproduction and verification

From the repository root, choose a **new** output directory and an existing parent:

```powershell
python -m tools.reviewer_isolation.prepare . NEW_PACKAGE NEW_PROVENANCE.json
python -m tools.reviewer_isolation.boundary verify-package NEW_PACKAGE EXPECTED_SHA256
```

The caller must supply the expected identity from a separately retained approved
record, not accept an identity obtained from untrusted package bytes. Output folders
must not already exist. File sets, hashes and canonical manifest bytes are checked;
unexpected files/directories, links/reparse points, hardlinks, traversal, Windows
device aliases, case collisions, duplicate JSON keys and unresolved Markdown links
reject. The runner snapshots verified bytes into its own private staging directory.
It never mounts a source repository. No archive extraction is implemented.

## Dependency and contamination boundary

No retrieval or implicit dependency resolution is allowed. Operational Markdown
links must resolve inside the package. Source profile identifiers and historical
prose references are definitions/annotations, not instructions to fetch documents.
If an omitted definition is necessary, that is a missing normative dependency: halt
and propose an explicitly versioned export amendment before substantive dispatch.

The machine validator detects named forbidden-round/guidance markers and unauthorized
resources. It cannot prove that arbitrary paraphrased or encoded prior findings are
absent. The exposed publisher's passage selection can influence a reviewer. Exact
human package approval and an independent source/closure inspection remain necessary.
Dependency sufficiency is **UNREVIEWED**, not mechanically proved. This preparation
export is therefore not an approved complete independent-review corpus.

The implemented runner refuses every `candidate-preparation` dispatch in R6.9.
Synthetic test packages have separate identities and never contain candidate inputs.
