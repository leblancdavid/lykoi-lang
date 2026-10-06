"""Public R5.84 evidence reproduction. Prints JSON; never writes results or grants."""
import copy
import hashlib
import json
import sys
from pathlib import Path

from benchmark.evaluation import formal_requirements_r5_80 as frc
from benchmark.evaluation import source_coverage_r5_84 as coverage
from benchmark.evaluation.behavioral_discovery_r5_82 import discover, adequacy_sidecar
from benchmark.evaluation.implementation_adequacy_r5_81 import authorization
from benchmark.results.phase5c.r5_84.fixtures import BASE, SOURCES, TARGETS, omission, candidate, review, run_bundle

ROOT = BASE.parents[3]
INDEPENDENT_PIN = "ff124b66301901a9e945338ccad1a354f8e393d8fe9175f06d1fbf3068d29d44"


def independent_comparison():
    raw = (BASE / "independent-soi.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == INDEPENDENT_PIN
    independent = json.loads(raw)
    records = {}
    for inventory in independent["sources"]:
        label = inventory["source_id"]
        b = candidate(label)
        assert inventory["source_text"] == b["source"]["record"]["text"]
        # Process C source-span overlap is a navigation aid, NOT semantic entailment.
        navigation = {}
        for item in inventory["items"]:
            assert item["quote"] in inventory["source_text"]
            navigation[item["id"]] = [o["id"] for o in b["contract"]["obligations"]
                if item["quote"] in o["source_quote"] or o["source_quote"] in item["quote"]]
        uncertainties = [i for i in inventory["items"] if i["category"] == "ambiguity"]
        assert uncertainties
        b["disagreements"] = [{"inventory_commitment": INDEPENDENT_PIN,
            "source_id": label, "question": i["meaning"], "resolution": None} for i in uncertainties]
        r = run_bundle(b)
        assert r["coverage"]["status"] == "COVERAGE_DISPUTED"
        assert not r["experimental_authorization"]
        records[label] = {"candidate_source_inventory_items": len(b["soi"]["items"]),
                          "independent_items": len(inventory["items"]),
                          "span_navigation_not_entailment": navigation,
                          "unresolved_material_questions": len(uncertainties),
                          "coverage": r["coverage"]["status"], "authorized": False}
    return records


def b01_calibration():
    # Exact already-public source plus prior public candidate; no implementation/oracle.
    text = (ROOT / "benchmark/requirements/B01.md").read_text(encoding="utf-8")
    # Source-only pass (same coordinating context already knows historical B01 issue).
    quotes = ["# B01 — Critical priority (local)",
              "Add `CRITICAL` above `HIGH` to accepted task priorities.",
              "`create --priority\nCRITICAL` persists and returns that value;",
              "`list` includes it.", "`list-high`\ncontinues to mean exactly `HIGH`.",
              "Existing LOW, NORMAL and HIGH tasks retain\ntheir values through migration.",
              "A missing priority still defaults to NORMAL."]
    items = []
    for n, quote in enumerate(quotes):
        a = text.index(quote)
        items.append({"id": "S" + str(n), "spans": [{"start": a, "end": a + len(quote), "quote": quote}],
            "meaning": quote, "category": "NONBEHAVIORAL" if n == 0 else "BEHAVIOR", "material": n != 0,
            "dependencies": []})
    a = text.index(quotes[-1])
    items.append({"id": "SQ", "spans": [{"start": a, "end": a + len(quotes[-1]), "quote": quotes[-1]}],
        "meaning": "Missing priority trigger could cover omitted creation argument or historical absent field",
        "category": "AMBIGUITY", "material": True, "dependencies": ["S5", "S6"]})
    contract = json.loads((ROOT / "benchmark/results/phase5c/r5_80/candidates.json").read_text(encoding="utf-8"))["B01"]
    assert contract["source"]["text"] == text
    source = {"revision": 1, "record": copy.deepcopy(contract["source"])}
    soi = {"version": coverage.SOI_VERSION, "source_commitment": frc.digest(source),
           "extractor": "same-context-public-B01-calibrator", "context_class": "SAME_CONTEXT",
           "items": items, "questions": [], "limitations": ["Known public issue, no blind rediscovery"]}
    target_ids = [[], ["B01.O01", "B01.O02"], ["B01.O03"], ["B01.O04"],
                  ["B01.O05"], ["B01.O07"], ["B01.O08"]]
    maps = [{"id": "M" + str(n), "source_ids": [item["id"]], "obligation_ids": target_ids[n],
             "disposition": "NONBEHAVIORAL" if n == 0 else "REPRESENTED",
             "rationale": "Heading only" if n == 0 else "Public clause mapped without resolving trigger uncertainty"}
            for n, item in enumerate(items[:-1])]
    maps.append({"id": "MQ", "source_ids": ["SQ"], "obligation_ids": [],
                 "disposition": "AMBIGUITY", "issue_id": "B01.I1"})
    bundle = {"version": coverage.VERSION, "source": source, "soi": soi, "contract": contract,
              "interface": {"operations": []}, "source_map": maps, "structural_map": [],
              "implications": [{"id": "N1", "premises": ["S4"], "result": "B01.O06",
                  "inference_class": "REVIEWER_NECESSITY", "mode": "REVIEWER_DERIVED",
                  "rationale": "Exactly HIGH excludes other distinct named priorities",
                  "denial_witness": "Including CRITICAL contradicts exactly HIGH", "review_status": "APPROVED"}],
              "questions": [], "disagreements": [], "coverage_complete": True}
    result = run_bundle(bundle)
    assert result["coverage"]["status"] == "SOURCE_AMBIGUOUS"
    assert result["adequacy"] == "NEEDS_CLARIFICATION" and not result["experimental_authorization"]
    # Erasing the issue and falsely claiming completion cannot discard SOI ambiguity.
    corrupted = copy.deepcopy(bundle)
    corrupted["contract"]["issues"] = []
    corrupted["source_map"][-1].update(disposition="REPRESENTED", obligation_ids=["B01.O08"])
    assert not run_bundle(corrupted)["experimental_authorization"]
    return {"source_text_sha256": source["record"]["sha256"], "inventory": soi,
            "source_map": maps, "coverage": result["coverage"]["status"],
            "adequacy": result["adequacy"], "discovery": result["discovery"],
            "authorized": False, "false_resolution_authorized": False,
            "qualification": "PUBLIC_KNOWN_ISSUE_SAME_CONTEXT_CALIBRATION_NOT_REDISCOVERY"}


def run():
    challenges = {}
    for label in TARGETS:
        source_loss, structural_loss = omission(label), omission(label, structural=True)
        new = run_bundle(source_loss)
        structural = run_bundle(structural_loss)
        _, _, fidelity = review(source_loss)
        old = adequacy_sidecar(source_loss["contract"], discover(source_loss["contract"], source_loss["interface"]), True)
        legacy_authorized = authorization(source_loss["contract"], fidelity, old)
        assert legacy_authorized and not new["experimental_authorization"] and not structural["experimental_authorization"]
        challenges[label] = {"omission": new["coverage"]["status"],
                             "structural_loss": structural["coverage"]["status"],
                             "legacy_false_attestation_authorized": legacy_authorized,
                             "r5_84_authorized": False}
    unsupported = {label: run_bundle(candidate(label))["coverage"]["status"] for label in TARGETS[-4:]}
    assert set(unsupported.values()) == {"STRUCTURAL_SCOPE_UNSUPPORTED"}
    b01 = b01_calibration()
    return {"classification": "R5_84_INDEPENDENT_COVERAGE_AUTHORITY_PARTIAL",
            "primary_sources": len(SOURCES),
            "primary_accounting_results": {s["id"]: run_bundle(candidate(s["id"]))["coverage"]["status"] for s in SOURCES},
            "challenges": challenges, "unsupported": unsupported,
            "independent_inventory_physical_sha256": INDEPENDENT_PIN,
            "independence_comparison": independent_comparison(), "B01": b01,
            "production_authority": False, "candidate_activation": "NOT_ACTIVATED",
            "B03": {"status": ["B03_PRISTINE", "B03_NOT_EVALUATED", "B03_NOT_EXPOSED_TO_LYKOI_DEVELOPMENT"],
                    "accounting_basis": "Scoped session activity and inherited status; no protected ledger inspection",
                    "source_access_attempts": 0, "source_reads": 0, "content_revealing_metadata": 0,
                    "formalization": 0, "discovery": 0, "adequacy": 0, "authorization": 0,
                    "reservations": 0, "packaging": 0, "opening": 0, "consumer_observation": 0,
                    "generation": 0, "execution": 0, "acceptance": 0, "repair": 0}}


if __name__ == "__main__":
    if sys.argv[1:] == ["--corpus"]:
        print(json.dumps({s["id"]: candidate(s["id"]) for s in SOURCES}, indent=2))
    else:
        print(json.dumps(run(), indent=2))
