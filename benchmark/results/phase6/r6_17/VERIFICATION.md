# R6.17 — Publication verification

Scope: documentation-only charter and experimental design. Initial working tree
clean at HEAD `13c5bde277a107435ab62e30dff6a1a798b94ac6`.

## Checks

Publication checks use Git scope/identity inspection and a read-only Python
standard-library document audit. No publication utility or architecture is
implemented in the repository. The audit checks:

- HEAD unchanged and tracked modifications restricted to `AGENTS.md`, `README.md`,
  `benchmark/README.md`, `docs/agent-workflow.md`, `docs/project-overview.md`,
  `docs/decisions.md`, `docs/research-log.md`.
- New files restricted to `docs/symbolic-research-charter-r6.17.md`,
  `benchmark/results/phase6/R6_17-REPORT.md` and the dedicated `r6_17/` publication.
- Tracked protected production paths `src/`, `schema/`, `air/`, `generated/`,
  unchanged `experiments/semantic_interpreter/`, and dedicated R6.3–R6.16 reports/
  directories match HEAD blob identities using Git hashing. Historical result
  content is not executed. Current entry-point guidance is intentionally revised;
  historical manifests referring to older guidance are not rewritten.
- Every relative Markdown publication link resolves locally; new documents have
  UTF-8 text, terminal newlines and no trailing whitespace.
- `git diff --check` passes for tracked edits; new-file whitespace is explicitly
  checked too, because Git's unstaged diff does not include untracked files.
- `PUBLICATION-IDENTITIES.json` binds raw SHA256 and byte lengths of the new
  charter/report/design documents and revised guidance. The manifest excludes
  itself to avoid self-reference; verification checks its members after creation.

Results: **PASS** for scope, protected identities, publication links/whitespace,
manifest members and `git diff --check`. Exact counts and hashes are retained
in the publication manifest. No compiler/application/VM regression or historical
acceptance suite is rerun for these prose-only changes.

## Readiness review

All ten requested deliverables have linked publications. Design states A/B/C
vocabulary distinction, composition-only discovery, ten lifecycle stages, five
representation alternatives, three main tracks, B-cap and C-expand controls,
development/freeze/unseen phases, local resource-before-model gate, equal budgets,
contamination controls, full metrics/amortization, falsifiable outcomes and stops.
Unknown hardware/model/task identities are future locked inputs under a specified
procedure; they are not measured or chosen in this round. Future mechanics/control
qualification can halt execution despite this design's ready classification.

No production/kernel/VM changes, historical classification amendments, model calls,
training, P6-A04 acceptance or P6-A05 access. Stopped after publication.
