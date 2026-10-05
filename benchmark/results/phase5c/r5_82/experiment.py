"""Explicit allowlisted public files; stdout evidence, no protected discovery."""
import copy
import json
from pathlib import Path
from benchmark.evaluation.behavioral_discovery_r5_82 import discover, adequacy_sidecar
from benchmark.evaluation.implementation_adequacy_r5_81 import analyze

ROOT = Path(__file__).resolve().parent


def load(name):
    return json.loads((ROOT / name).read_text(encoding="utf-8"))


def inputs(case):
    contract = {"id": case["id"], "source": case["source"], "scope": case.get("scope", "sequential abstract interface")}
    interface = {"operations": [{"id": case["id"], "facts": {
        k: {"value": v, "origin": [case["id"] + ".interface." + k], "evidence": case["source"]}
        for k, v in case["facts"].items()}, "channels": case["channels"],
        "authority": case.get("authority", {})}]}
    if "finite_domain" in case:
        interface["operations"][0]["finite_domain"] = case["finite_domain"]
    return contract, interface


def families(bdi):
    return sorted(d["family"] for d in bdi["decisions"])


def run():
    cases = {c["id"]: c for c in load("corpus.json")["cases"]}
    expected = load("expected.json")
    inventories = {k: discover(*inputs(c)) for k, c in cases.items()}
    coverage, tp, fp, fn, rejected = {}, 0, 0, 0, 0
    for key, bdi in inventories.items():
        actual, wanted = set(families(bdi)), set(expected["decisions"][key])
        irrelevant = set(expected["irrelevant"].get(key, []))
        row = {"tp": sorted(actual & wanted), "fp": sorted(actual - wanted),
               "fn": sorted(wanted - actual), "correctly_rejected": sorted(irrelevant - actual)}
        coverage[key] = row
        tp += len(row["tp"]); fp += len(row["fp"]); fn += len(row["fn"])
        rejected += len(row["correctly_rejected"])
    # Expected deltas were chosen before invoking each mutated discovery.
    specs = [
        ("remove-selection-obligation", "hidden-tie", "selection", False, ["selection", "cardinality", "tie"], []),
        ("weaken-invariant", "unique-score", "unique_match", False, [], ["tie"]),
        ("broaden-optional", "scalar", "optional_input", True, [], ["optional"]),
        ("introduce-nullability", "nonnull", "nonnull_precondition", False, [], ["nullable_predicate"]),
        ("permit-duplicates", "filter", "duplicates_admitted", True, [], ["duplicates"]),
        ("change-cardinality", "hidden-tie", "exactly_one", False, ["cardinality", "tie"], []),
    ]
    mutations = []
    for name, key, fact, value, removed, added in specs:
        c = copy.deepcopy(cases[key]); c["facts"][fact] = value
        c["source"] += " Prospective mutation: " + fact + "=" + str(value)
        before, after = set(families(inventories[key])), set(families(discover(*inputs(c))))
        mutations.append({"id": name, "removed": sorted(before-after), "added": sorted(after-before),
                          "expected_removed": sorted(removed), "expected_added": sorted(added),
                          "pass": before-after == set(removed) and after-before == set(added)})
    c = copy.deepcopy(cases["private-order"]); c["channels"]["order"] = "MEANINGFUL"
    mutations.append({"id": "expose-channel", "added": families(discover(*inputs(c))),
                      "pass": families(discover(*inputs(c))) == ["ordering"]})
    c = copy.deepcopy(cases["unordered"]); c.pop("authority"); c["channels"]["order"] = "MEANINGFUL"
    c["source"] = "Return active records."
    mutations.append({"id": "remove-explicit-freedom", "pass": families(discover(*inputs(c))) == families(inventories["unordered"]),
                      "explanation": "Decision persists; authority and consumer scope change, not decision existence."})
    for note in ("loop instead of recursion", "prefer a hash map", "metadata revision 2"):
        c = copy.deepcopy(cases["scalar"])
        if note.startswith("metadata"):
            c["note"] = note
        else:
            c["source"] += " Internal hint: " + note + "."
        mutations.append({"id": note, "pass": families(discover(*inputs(c))) == []})
    finite = []
    for key, domain in (
        ("hidden-tie", {"score_states":[[1],[7,7],[1,2]]}),
        ("unique-score", {"score_states":[[1],[7,8],[1,2]]}),
        ("hidden-collision", {"normalization_values":["A","a"],"transform":"lower"}),
        ("injective", {"normalization_values":["a","b"],"transform":"lower"}),
    ):
        c = copy.deepcopy(cases[key])
        for fact in ("multiple_matches", "unique_match", "collision_possible", "injective_on_domain", "normalization_identity"):
            c["facts"].pop(fact, None)
        domain.update({"exhaustive":True,"origin":[key + ".finite-domain"]})
        c["finite_domain"] = domain
        b = discover(*inputs(c))
        finite.append({"case":key,"domain":domain,"inventory":b,
                       "matches_expected":families(b) == sorted(expected["decisions"][key])})
    # Plans intentionally use different residual policies, not shared algorithms.
    plans = [
        {"case":"hidden-tie", "decision":"tie", "input":[["a",7],["b",7]], "plan_a":"scan and retain first maximum", "plan_b":"sort and select last maximum", "outputs":["a","b"]},
        {"case":"hidden-history", "decision":"default_trigger_domain", "input":{}, "plan_a":"materialize default on load", "plan_b":"reject absent historical unit", "outputs":["C","error"]},
        {"case":"hidden-collision", "decision":"collision", "input":["A","a"], "plan_a":"reject normalized duplicate", "plan_b":"merge normalized duplicate", "outputs":["error",["a"]]},
        {"case":"hidden-retry", "decision":"retry", "input":"closed", "plan_a":"idempotent close", "plan_b":"reject closed record", "outputs":["success","error"]},
        {"case":"hidden-failure", "decision":"failure_atomicity", "input":"notification fails after write", "plan_a":"transactional rollback", "plan_b":"retain committed write", "outputs":[1,2]},
        {"case":"scalar", "decision":None, "input":[2,3], "plan_a":"direct addition", "plan_b":"sum a sequence", "outputs":[5,5]},
    ]
    for p in plans:
        p["covered"] = p["decision"] in families(inventories[p["case"]]) if p["decision"] else True
        p["independence"] = "same coordinating context; separately described strategies, not independent producers"
    # R5.81 integration is deliberately only a reviewed two-option local probe.
    local = {"id":"ordering-probe", "source":"Any permutation is permitted; callers must ignore order.",
             "scope":"Exactly two distinct fixed records; only forward/reverse order decision; sequential calls",
             "facts":{"collection":True,"max_results":"many","order_varies":True}, "channels":{"order":"DELEGATED"},
             "authority":cases["unordered"]["authority"]}
    contract, interface = inputs(local)
    delegated = analyze(contract, adequacy_sidecar(contract, discover(contract, interface), True))
    omitted = copy.deepcopy(local); omitted.pop("authority"); omitted["source"] = "Return a sequence."
    oc, oi = inputs(omitted)
    missing = analyze(oc, adequacy_sidecar(oc, discover(oc, oi), True))
    unreviewed = analyze(contract, adequacy_sidecar(contract, discover(contract, interface)))
    # Exact public candidate only. Conditional legacy branch, NOT established baseline reachability.
    public = json.loads((ROOT.parent / "r5_80" / "candidates.json").read_text(encoding="utf-8"))["B01"]
    bi = {"operations":[{"id":"priority-lifecycle", "facts":{
        "creation_default":{"value":True,"origin":["B01.O08"],"evidence":"Default value stated; creation context conditional"},
        "historical_absence":{"value":True,"origin":["B01.O07","B01.I1"],"evidence":"Unresolved admitted historical-state branch, conditional only"}},
        "channels":{"later":"MEANINGFUL"}}]}
    b01 = discover(public, bi)
    b01["qualification"] = "CONDITIONAL_DISCOVERY_NOT_INDEPENDENT_ELICITATION"
    b01["authority_status"] = "NEEDS_CLARIFICATION"
    b01["authoring_authorized"] = False
    ba = adequacy_sidecar(public, b01)
    ba["issues"] = [{"kind":"AMBIGUITY", "reason":"B01.I1: default trigger domain and historical reachability unresolved"}]
    b01["adequacy"] = analyze(public, ba)
    return {"classification":"R5_82_BEHAVIORAL_DECISION_DISCOVERY_PARTIAL", "inventories":inventories,
            "coverage":{"cases":coverage,"tp":tp,"fp":fp,"fn":fn,"correctly_rejected":rejected,
                        "identity":"operation:family exact; no equivalence remapping", "unresolved_reviewer_disagreements":"No independent reviewer; expected-record questions unresolved"},
            "hidden_challenge":{k: coverage[k] for k in expected["witnesses"]},
            "mutations":mutations, "finite_implications":finite, "plans":plans,
            "adequacy":{"delegated":delegated,"omitted":missing,"unreviewed":unreviewed}, "B01":b01,
            "independence":{"ordinary_coordinator_attempts":1,"context_isolated":0,"provider_model_isolated":0,"strict_isolation_qualified":0},
            "B03":{"status":["B03_PRISTINE","B03_NOT_EVALUATED","B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT"],
                   "source_reads":0,"metadata_inspections":0,"discovery":0,"evaluation":0,"authorization":0,"packaging":0,"opening":0,"consumer_observation":0,"generation":0,"execution":0,"acceptance":0,"repair":0}}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
