"""Publish explicit analytical annotations/matrices, never change measured stages."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
EVIDENCE = json.loads((OUT / "R5_101-CURRENT-EVIDENCE.json").read_text(encoding="utf-8"))

# Primary classification describes the first blocker/root explanation. Secondary
# demands are not relabeled as failed downstream pipeline stages.
ANNOTATIONS = {
 "B01": ("STRUCTURAL_INTEGRATION_GAP", "Closed structural bridge cannot carry enum extension, rank/list and migration-preservation relations; legacy enum/default/filter semantics already exist", "SUCCESS"),
 "B02": ("MISSING_GENERAL_SEMANTIC_CAPABILITY", "Persisted ordered string values, repeated input, trim/validate/map and stable deduplication; query read-only strings do not provide mutation semantics", "AXIOM_CAPABILITY_GAP"),
 "B03": ("BACKEND_INTEGRATION_GAP", "Typed membership query is supported; model-state binding refuses missing tags field. Underlying persisted-list prerequisite remains missing", "BLOCKED_BY_GAP -> B02; R5.97 DECISION_DISCOVERY_UNSUPPORTED / STRUCTURAL_COVERAGE_FAILURE; R5.98 transfer STRUCTURAL_COVERAGE_FAILURE"),
 "B04": ("STRUCTURAL_INTEGRATION_GAP", "No normal field-addition/migration/result-preservation bridge despite legacy input_default and literal migration support", "SUCCESS"),
 "B05": (None, "Runtime equality query works against current model; pending/completed domain only, not cumulative B01-B04 achievement", "AXIOM_CAPABILITY_GAP (runtime input-dependent filter)"),
 "B06": ("MISSING_GENERAL_SEMANTIC_CAPABILITY", "Create-time optional/explicit-empty distinction plus trim/validation assignment; exact query exists but category state is missing and mixed mutation/query mappings refuse", "AXIOM_CAPABILITY_GAP"),
 "B07": ("MISSING_GENERAL_SEMANTIC_CAPABILITY", "Ordered persisted value arrays and append transformation; trim-before-write; legacy assignments cannot append", "AXIOM_CAPABILITY_GAP"),
 "B08": ("BACKEND_INTEGRATION_GAP", "Boolean typed query values/inclusion exist, but legacy application fields/store cannot persist booleans; orthogonal archive mutation and coordinated query integration absent", "AXIOM_CAPABILITY_GAP (boolean)"),
 "B09": ("MISSING_GENERAL_SEMANTIC_CAPABILITY", "Two typed temporal operands, inclusive range, cross-input comparison and null exclusion; archive store binding also absent", "BLOCKED_BY_GAP -> B08"),
 "B10": ("MISSING_GENERAL_SEMANTIC_CAPABILITY", "Optional owner create-time trim/validation with omission distinguished; query equality supported but owner state and normal mutation bridge absent", "AXIOM_CAPABILITY_GAP"),
 "B11": ("MISSING_GENERAL_SEMANTIC_CAPABILITY", "Composed conditional rejection/permission predicate: pending OR archived; conjunction-only equality guards are insufficient; boolean prerequisite absent", "BLOCKED_BY_GAP -> B08"),
 "B12": ("MISSING_GENERAL_SEMANTIC_CAPABILITY", "Compose clock/null/pending/archive predicate with scalar priority in a constant set. Legacy before-clock exists; query profile has no clock/nullable predicate or scalar-in-set composition", "BLOCKED_BY_GAP -> B08"),
 "B13": ("STRUCTURAL_INTEGRATION_GAP", "Cross-operation equality/transition guards exist in legacy semantics but normal invariant mapping is absent; boolean/archive and notes prerequisites remain missing", "BLOCKED_BY_GAP -> B08,B07"),
 "B14": ("MISSING_GENERAL_SEMANTIC_CAPABILITY", "Persisted identity edges, append, relation lookup, acyclicity/reachability and inverse-reference deletion guard", "LYKOI_CAPABILITY_GAP"),
 "B15": ("MISSING_GENERAL_SEMANTIC_CAPABILITY", "Quantified related-record state guard (all dependencies complete), with existing transition composition", "BLOCKED_BY_GAP -> B14,B08"),
 "B16": ("MISSING_GENERAL_SEMANTIC_CAPABILITY", "Multiple persistent entity states, dynamic cross-entity existence/uniqueness and relation-aware migration", "AXIOM_CAPABILITY_GAP"),
 "B17": ("AMBIGUOUS_REQUIREMENT", "Existing non-system users need a migration role; creation default USER alone does not authorize that migration. Authorization/state integration is a separate downstream demand", "NOT_EVALUATED (prospective analysis only)"),
 "B18": ("STRUCTURAL_INTEGRATION_GAP", "Effects are accepted as external_effect channels but no supported event decision discovery carries their meaning: rule_for:external_effect. Durable event/transaction semantics also absent downstream", "NOT_EVALUATED"),
 "B19": ("MISSING_GENERAL_SEMANTIC_CAPABILITY", "Nullable positive integer, temporal arithmetic, conditional record copy/create, fresh resources and multi-effect atomicity", "NOT_EVALUATED"),
 "B20": ("AMBIGUOUS_REQUIREMENT", "Unknown member-user rejection error has no explicit authority; persistent project/membership relationships and composed permissions remain downstream demands", "NOT_EVALUATED"),
}

# S=required concept supported in at least one existing profile (not whole-case
# success); I=required concept exists but normal-path/store integration is missing;
# M=required general semantic composition missing; U=authority uncertain; -=not
# required by this local change. Inherited prerequisites are in the report's DAG.
CAPABILITIES = [
 ("Enum evolution / verbatim optional scalar fields", {"B01":"I","B04":"I","B06":"I","B10":"I","B16":"I","B17":"I","B20":"I"}),
 ("Runtime string equality predicate", {"B05":"S","B06":"S","B10":"S","B20":"S"}),
 ("Runtime string-list membership predicate", {"B03":"S"}),
 ("Explicit exact/case-sensitive comparison", {c:"S" for c in ("B02","B03","B05","B06","B10","B14","B16","B17","B20")}),
 ("Create-time trim / optional presence / validation composition", {c:"M" for c in ("B02","B06","B07","B10")}),
 ("Nonblank rejection and declared errors", {c:"S" for c in ("B02","B03","B07","B10","B16","B20")}),
 ("Deterministic key ordering and unique tie break", {c:"S" for c in ("B01","B03","B04","B05","B06","B08","B09","B10","B12","B16","B18","B20")}),
 ("Ordered scalar collections in persisted records", {"B02":"I","B07":"I","B14":"I","B19":"I","B20":"I"}),
 ("Stable first-occurrence dedup / append / set update", {"B02":"M","B07":"M","B14":"M","B20":"M"}),
 ("Input/insertion-occurrence ordering (not key sorting)", {"B02":"M","B07":"M","B14":"M"}),
 ("Boolean task fields / inclusion store integration", {c:"I" for c in ("B08","B09","B11","B12","B13","B20")}),
 ("Positive integer input / nullable integer state", {"B19":"M"}),
 ("Nullable timestamp storage / legacy clock exclusion", {"B09":"S","B12":"S","B19":"S"}),
 ("Temporal range / null-aware runtime predicates / date arithmetic", {"B09":"M","B12":"I","B19":"M"}),
 ("Compound AND/OR/NOT or scalar-in-set predicates", {"B08":"I","B09":"M","B11":"M","B12":"M","B13":"I","B15":"M","B17":"M","B20":"M"}),
 ("Create/update/delete and lifecycle, simple guards", {c:"S" for c in ("B01","B02","B04","B06","B07","B08","B10","B11","B13","B14","B15","B16","B17","B18","B19","B20")}),
 ("Read-only effect and whole-record/empty-list results", {c:"S" for c in ("B01","B03","B04","B05","B06","B08","B09","B10","B12","B13","B16","B18","B20")}),
 ("Normal query/model-state field binding", {"B03":"I","B05":"S","B06":"I","B08":"I","B09":"I","B10":"I","B12":"I","B20":"I"}),
 ("Identity references / dynamic existence / quantified relationships", {c:"M" for c in ("B14","B15","B16","B17","B20")}),
 ("Graph reachability / acyclicity / inverse-use guard", {"B14":"M"}),
 ("Multiple durable entity states", {c:"M" for c in ("B16","B17","B18","B19","B20")}),
 ("Data-dependent actor/owner/role authorization", {c:"M" for c in ("B17","B20")}),
 ("Durable ordered events and transaction composition", {"B18":"M","B19":"M"}),
 ("Conditional copy/map/create with fresh resources", {"B19":"M"}),
 ("Literal field migration / single-store atomic persistence", {**{c:"S" for c in ("B01","B04","B06","B10","B16","B17","B18","B20")}, **{c:"I" for c in ("B02","B07","B08","B14","B19")}}),
 ("Relation-aware conditional migration", {"B16":"M","B17":"U"}),
 ("Unresolved behavioral authority", {"B17":"U","B20":"U"}),
]

def main():
    annotations = []
    lines = ["# R5.101 — twenty-case current capability matrix", "",
             "Requirement-local current pipeline results; **not cumulative Phase 5C achievement**. See the report for evidence limits and dependencies.", "",
             "| Case | Requirement family | First blocker | Native classification | Missing capability/integration (primary class) | Furthest stage | Current result |",
             "| --- | --- | --- | --- | --- | --- | --- |"]
    counts, types = {}, {}
    for c in EVIDENCE["cases"]:
        case = c["case"]
        category, gap, historical = ANNOTATIONS[case]
        annotations.append({"case": case, "primary_gap_class": category, "root_explanation": gap,
                            "historical_result": historical, "current_native": c["native"], "stages": c["stages"],
                            "capabilities": {name: values.get(case, "-") for name, values in CAPABILITIES}})
        counts[c["first_blocker"]] = counts.get(c["first_blocker"], 0) + 1
        if category:
            types[category] = types.get(category, 0) + 1
        lines.append(f"| {case} | {c['family']} | {c['first_blocker']} | `{c['native']}` | {gap} ({category or 'no blocker'}) | {c['furthest']} | {'Behaviorally verified (local)' if c['first_blocker']=='SUCCESS' else 'Blocked; later stages NOT_REACHED'} |")
    lines += ["", "## Explicit stage accounting", "", "P = pass; C = source-bound analytical candidate accepted by native reconciliation; B = blocked; — = NOT_REACHED. No downstream failure is inferred.", "",
              "| Case | Formalization | Structural | BDI | Adequacy | V1/profile | Authoring | Compilation | Runtime | External behavior |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for c in EVIDENCE["cases"]:
        symbols = {"NOT_REACHED":"—", "BLOCKED":"B", "PASS":"P", "PASS_ANALYTICAL_CAPTURE":"C", "PASS_NATIVE_BOUNDED_PROJECTION":"P*"}
        lines.append("| " + c["case"] + " | " + " | ".join(symbols[c["stages"][s]] for s in c["stages"]) + " |")
    lines += ["", "P* for B18 is native bounded structural acceptance of effects channels, not proof that full event semantics were structurally understood.", "",
              "## Historical results (preserved, not current classifications)", "",
              "Conventional historically achieved B01–B16; B17–B20 were not evaluated. Lykoi results below come from the R2/R3/R4/B16 checkpoint reports referenced in the R5.101 report.", "",
              "| Case | Historical Lykoi result | R5.101 current local result |", "| --- | --- | --- |"]
    for c in EVIDENCE["cases"]:
        lines.append(f"| {c['case']} | {ANNOTATIONS[c['case']][2]} | `{c['native']}` |")
    lines += ["", "## Capability-by-case matrix", "",
              "**S** = required/supported concept in an existing profile; **I** = required concept exists but integration is missing; **M** = required semantic composition missing; **U** = uncertain authority; **—** = not required by the local change.", "",
              "S is never shorthand for whole-case success. E.g. query normalization does not implement mutation-time trimming, and a read-only `strings` view does not implement persistent append. I may coexist with a deeper M prerequisite, detailed in the report. Rows describe local demands; cumulative inherited demands are explicit dependency edges instead of twenty repeated supersets.", "",
              "| Capability | " + " | ".join(c["case"] for c in EVIDENCE["cases"]) + " |",
              "| --- | " + " | ".join("---" for _ in EVIDENCE["cases"]) + " |"]
    for name, values in CAPABILITIES:
        lines.append("| " + name + " | " + " | ".join(values.get(c["case"], "—") for c in EVIDENCE["cases"]) + " |")
    lines += ["", "Generic aggregation, pagination, regex/prefix search and stable occurrence sorting of returned *records* are not required by this corpus's local clauses. Tag deduplication and note/dependency insertion order do require occurrence semantics for *values*.", "",
              f"First-result counts: {counts}. Primary root classifications (nineteen blocked cases): {types}.", ""]
    with (OUT / "R5_101-CAPABILITY-MATRICES.md").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(lines))
    with (OUT / "R5_101-CAPABILITY-ANALYSIS.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump({"basis": "Analytical annotations, not extra downstream execution", "first_result_counts": counts,
                   "primary_gap_counts": types, "cases": annotations}, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print("First blockers:", counts)
    print("Primary gap classes:", types)

if __name__ == "__main__":
    main()
