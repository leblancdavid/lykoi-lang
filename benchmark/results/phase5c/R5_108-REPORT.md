# R5.108 — Semantic kernel audit and consolidation analysis

**Final classification: `R5_108_SEMANTIC_KERNEL_CONVERGING`.**

Analysis/documentation only. The full architectural reference is
[the semantic-kernel audit](../../../docs/semantic-kernel-audit-r5.108.md).
R5.107 remains `R5_107_PREDICATE_VALUE_INTERFACE_CLOSED`, with **13/20 exposed
requirement-local behavioral successes, B01–B13**. No new transfer results or
held-out generalization claims are introduced.

## Deliverables

| Deliverable | Audit location |
| --- | --- |
| Exact original core recovery, count/versioning/identity | Section 2 |
| Every original concept's purpose, evidence, current location and lineage | Section 3 |
| Post-core additions and material refinements with first/normal introduction | Section 5 |
| Four levels / core accounting unit / complete original and added kernel tables | Sections 3–5 |
| Cross-layer semantic mapping | Section 10 |
| Predicate/value/transformation/mutation/lifecycle/resource/persistence/query audits | Sections 6–9 |
| Semantic duplication | Section 11 |
| Backend-leak classification | Section 12 |
| Core/composition reuse and leverage / kernel stability / R5.107 evaluation | Sections 3–4 and 13 |
| Exact growth accounting | Section 4 |
| B14–B20 demand analysis and relationship/event/arithmetic hypotheses | Section 14 |
| Hierarchical map and AI-native implications/recommendations | Sections 15–16 |
| Project overview, decisions and research-log updates | `docs/project-overview.md`, `decisions.md`, `research-log.md` |
| Current regression, validation/safety, scope and whitespace evidence | `R5_108-VERIFICATION.json` |

## Method / evidence boundary

Started with `git status --short`: substantial pre-existing R5.106/R5.107 changes
and untracked evidence were present. Before any workspace edit, a byte-hash
snapshot covered 3,503 tracked/untracked nonignored files. Change scope is measured
against that starting workspace, not against HEAD (which already differs).
The temporary read-only audit runner is outside the workspace; no production or
infrastructure module was introduced. Concurrent artifact-retention documentation
and configuration updates were observed and preserved, separately attributed in
the scope evidence.

Read the governing overview/workflow, benchmark policy, exact historical ledger
and R5.40/R5.41 reports, current versioned specifications, existing inventory,
R5.107 report and frozen remaining requirements. Traced definitions through the
historical `benchmark/semantic/` prototypes and current compiler/runtime/profile
modules. No memory reconstruction substitutes for an available original list.

This is a same-agent static architectural analysis. Mathematical reductions such
as OR from AND/NOT are stated under the existing pure two-valued model. Proposed
decompositions do not certify arbitrary executable composition or minimality.
Reuse cites selected exposed case realizations and published synthetic domains;
no invented uniform clause-use count, summed unique-domain denominator or numeric
leverage score. Synthetic captures/oracles/approvals retain their same-agent limits.

## Exact accounting and assessment

| Quantity | Count |
| --- | ---: |
| Original R5.40/R5.41 candidate core | **30** |
| Original raw categorized entries | **46** |
| Still core unchanged | 7 |
| Refined core | 11 |
| Absorbed | 2 |
| Reclassified composition | 4 |
| Deprecated | 0 |
| Experimental/unresolved | 6 |
| Original concepts retained as proposed core | **18** |
| Previously uncounted core foundations with pre-R5.41 antecedents | 4 |
| Genuinely new irreducible categories first established after R5.41 | **0 established** |
| **Current proposed architectural kernel** | **22** |

The four additions to accounting are presence, resource/capability authority,
durable state and atomic commit. New **executable support** after R5.41 is extensive;
zero new categories is not zero behavioral development. General cardinality remains
historical executable support with specialized migration counting normally;
the proposed core count is not a normal-language capability tally.

Converging means the **recent bounded capabilities increasingly derive from
composition**, not that Lykoi has found a final universal kernel. Low-leverage
prototype concepts, separate IRs and backend boundary leakage remain important
counterevidence. B14/B15/B19 can still require new or newly qualified foundations.

## Verification

**93/93 focused existing tests pass**, plus canonical model validation and safety:
compiler 22, application 9, typed predicates 7, FRC 18, BDI 16, adequacy 18 and
external baseline 3. `R5_108-VERIFICATION.json` contains exact commands, exit codes,
counts and stdout/stderr. This covers the current core rather than qualifying
infrastructure or rerunning exposed transfer.

An initial broader unchanged R5.107 regression invocation exceeded the tool's
600-second timeout before publishing its aggregate record. Twelve completed suite
results reported exit 0 / **148 tests** in session stdout, including mutable/input/
predicate/interface/query/scalar/composition and compiler/application regressions.
These overlap the focused run and are **not added** to its denominator. The
interrupted attempt is recorded separately; no complete new 361-test pass is claimed.

Documentation whitespace checks pass, including new untracked audit/report text.
Full `git diff --check` **exits 2** on the one inherited R5.107 trailing space at
`src/lykoi_pipeline/mutable_profile.py:259`; its complete file hash is unchanged.
No formatting repair occurred. All starting production, schema, model, generated,
test and historical-evidence file hashes remain unchanged. The only starting-file
changes are the three audit-updated project documents and separately observed
concurrent `.gitattributes`, `.gitignore` and README artifact-retention changes.
The concurrent new `benchmark/artifacts/` files are also identified separately.
Unexpected scope changes are **zero**. Post-report scope/whitespace confirmation is
in `R5_108-FINAL-AUDIT.json`; the initial verification evidence remains preserved.

## Completion answers

1. **Original list/count:** exactly the 30 names in audit section 2, recovered
   from R5.4 ledger membership selected by R5.5 plus R5.10 cardinality. Raw #30
   `invoke` is not core #30 `cardinality`. Earlier counts differ by membership.
2. **Original concepts still core:** 18 (seven active, eleven refined), with
   bounded normal-support qualifications in the lineage table.
3. **Absorbed/reclassified:** exactness and source-relative order become policies;
   nonblank, precondition, lexicographic ordering and default_missing become
   compositions. Six graph/quantifier/scope/offset concepts remain unresolved.
4. **Genuinely new core:** none first established after R5.41 under this proposed
   decomposition. Four previously uncounted foundations are now explicit; they
   have older behavioral evidence.
5. **Proposed count:** 22; not forced to equal 30, not a minimality proof.
6. **Major compositions:** CollectionQuery, predicate trees/OR/ranges, pipelines,
   typed mutation operations, staged validation, defaults, lifecycle, migration.
7. **Duplication:** significant across condition representations, type checks,
   parameters/bindings, validation and ordering; common predicate evaluation is
   already a positive consolidation. Similar names sometimes mean different things.
8. **Backend leaks:** yes—Unicode repertoire, timestamp grammar/precision, string
   collation, parser/exception/JSON boundaries and stdout; atomicity is bounded by
   backend/OS guarantees. Explicit occurrence/presence/null semantics are preserved.
9. **Stability:** converging within bounded evidence, not semantic explosion or
   demonstrated universal generality.
10. **8→13:** five local successes through faithful existing-family interface
    composition; usable expressiveness depends on the whole path. Not held-out.
11. **B14–B16:** direct relationships/existence plausibly compose; cycle reachability
    likely needs a new/admitted core relation; related-state quantification needs
    implementation research. Not necessarily a new Relationship atom.
12. **B18:** a new event primitive is not established as necessary. Source requires
    internal durable audit; discovery calls it external_effect. Ordered coupled
    effects/counter computation remain unqualified.
13. **B19:** typed arithmetic/calendar displacement likely adds/adopts core
    computation; successor construction/commit plausibly compose existing effects
    with broader scope. Resources alone do not compute the due date.
14. **Next recommendation:** persistent relationships/cross-entity integrity still
    R5.109's recommended family, only upon separate instruction.
15. **Protect:** explicit independent operator meanings, typed operands/stable IDs,
    pure shared conditions, faithful cross-layer mapping, source authority, scoped
    capabilities, occurrence/stage distinctions and atomic failure frames. Minimize
    repeated behavioral facts without hidden Python behavior or human-only aliases.

**Stop after R5.108.** No relationship, arithmetic, event, production refactor or
infrastructure implementation follows from this report.
