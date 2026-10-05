"""Explicit public-only corpus loader and reproducible experiment (stdout only)."""
import copy
import json
from pathlib import Path

from benchmark.evaluation.implementation_adequacy_r5_81 import VERSION, analyze, authorization, commitment

ROOT = Path(__file__).resolve().parent


def fixtures():
    corpus = json.loads((ROOT / "corpus.json").read_text(encoding="utf-8"))
    result = {}
    for case in corpus["cases"]:
        contract = {"id": case["id"], "source": case["source"], "scope": corpus["scope"]}
        decision = {"id": case["decision"], "relevance": case.get("relevance", "REQUIRED"),
                    "reason": "Declared interface admits distinguishable choices for " + case["decision"],
                    "options": case["options"], "clauses": case["clauses"]}
        if decision["relevance"] == "INTERNAL":
            decision["reason"] = "Algorithm choice cannot alter exact mathematical sum or effect prohibition."
        analysis = {"version": VERSION, "contract_commitment": commitment(contract),
                    "scope": corpus["scope"], "coverage_reviewed": True,
                    "supported": case.get("supported", True), "decisions": [decision],
                    "issues": [{"kind": "AMBIGUITY", "reason": case["issue"]}] if "issue" in case else []}
        result[case["id"]] = (contract, analysis, case["expected"])
    return result


def mutate(contract, analysis):
    """Remove the behavioral source clause and authority, never merely its schema field."""
    c, a = copy.deepcopy(contract), copy.deepcopy(analysis)
    quote = a["decisions"][0]["clauses"][0]["source_quote"]
    c["source"] = c["source"].replace(quote, "")
    a["decisions"][0]["clauses"] = []
    a["contract_commitment"] = commitment(c)
    return c, a


def divergence():
    tasks = [{"id": "z", "creation": 0, "priority": 1},
             {"id": "a", "creation": 1, "priority": 1}]
    # Two internal strategies implement creation ordering identically.
    sorted_plan = lambda rows: sorted(rows, key=lambda t: t["creation"])
    def insertion_plan(rows):
        output = []
        for task in rows:
            at = 0
            while at < len(output) and output[at]["creation"] < task["creation"]:
                at += 1
            output.insert(at, task)
        return output
    adequate = []
    for rows in (tasks, tasks[::-1], [], tasks[:1], [{"id": "gap", "creation": 7, "priority": 1}]):
        adequate.append(sorted_plan(rows) == insertion_plan(rows))
    missing = [{"id": "missing", "creation": 2}]
    default_zero = lambda rows: [t["id"] for t in rows if t.get("priority", 0) == 0]
    exclude_missing = lambda rows: [t["id"] for t in rows if "priority" in t and t["priority"] == 0]
    ids = lambda rows: [t["id"] for t in rows]
    return {"witness": tasks, "adequate_internal_strategy_agreements": adequate,
            "omitted_order_literal_outputs": [ids(sorted_plan(tasks)), ids(sorted_plan(tasks)[::-1])],
            "omitted_default_literal_outputs_query_zero": [default_zero(missing), exclude_missing(missing)],
            "omitted_tie_literal_outputs": [[sorted_plan(tasks)[0]["id"]], [sorted_plan(tasks)[-1]["id"]]],
            "explicit_order_freedom_outputs": [ids(sorted_plan(tasks)), ids(sorted_plan(tasks)[::-1])],
            "freedom_membership_equivalent": sorted(["z", "a"]) == sorted(["a", "z"]),
            "claim": "Finite witnesses and plans, not universal equivalence proof."}


def public_analysis():
    # Exact already-public R5.80 records only; no requirement-directory access.
    public = ROOT.parent / "r5_80"
    candidates = json.loads((public / "candidates.json").read_text(encoding="utf-8"))
    receipts = json.loads((public / "reviews.json").read_text(encoding="utf-8"))["receipts"]
    results = {}
    for key in ("S01", "S02", "S10", "B01", "P01"):
        c = candidates[key]
        a = {"version": VERSION, "contract_commitment": commitment(c),
             "scope": c["context"]["scope"], "coverage_reviewed": True,
             "supported": key == "S01", "issues": [], "decisions": []}
        if key == "S01":
            for id_, quote, options, selected in (
                    ("arithmetic", "return their sum", ["exact-sum", "offset"], "exact-sum"),
                    ("effects", "No state or external effects are permitted.", ["none", "effect"], "none")):
                a["decisions"].append({"id": id_, "relevance": "REQUIRED",
                                      "reason": "Source determines " + id_, "options": options,
                                      "clauses": [{"authority": "DETERMINED", "allowed": [selected],
                                                   "source_quote": quote}]})
        elif key == "B01":
            a["issues"] = [{"kind": "AMBIGUITY", "reason":
                "B01.O08/B01.I1: NORMAL default is stated but its trigger domain is unresolved: omitted creation argument only versus creation omission plus missing legacy stored field. Implementing migration/creation would choose observable persisted/returned priority or failure behavior without authority."}]
        result = analyze(c, a)
        result["fidelity_status"] = receipts[key]["outcome"]
        result["fidelity_binding_matches"] = receipts[key]["contract_commitment"] == commitment(c)
        result["experimental_authorization"] = authorization(c, receipts[key], a)
        result["scope_limit"] = ("Abstract typed mathematical integers only; no production transport authority." if key == "S01" else
                                 "No complete bounded decision inventory; no software authoring authority.")
        results[key] = result
    return results


def run():
    cases = fixtures()
    outcomes = {key: analyze(c, a) for key, (c, a, _) in cases.items()}
    mutations = {}
    for key in ("A-complete", "B-complete", "C-complete", "M-rejection", "M-transition", "M-cardinality", "M-normalization"):
        c, a, _ = cases[key]
        mc, ma = mutate(c, a)
        mutations[key] = analyze(mc, ma)
    c, a, _ = cases["E-internal"]
    c = copy.deepcopy(c)
    c["source"] = c["source"].replace(" An internal loop or direct addition may be used.", "")
    a = copy.deepcopy(a)
    a["contract_commitment"] = commitment(c)
    return {"cases": outcomes, "mutations": mutations, "public": public_analysis(),
            "internal_clause_removal": analyze(c, a), "divergence": divergence()}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
