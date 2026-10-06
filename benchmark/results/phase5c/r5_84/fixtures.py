"""Same-context known-answer corpus. Inventory construction uses source, not FRC.

The isolated inventory is a separate immutable artifact; this file does not replace it.
"""
import copy
import hashlib
import json
from pathlib import Path

from benchmark.evaluation import formal_requirements_r5_80 as frc
from benchmark.evaluation import source_coverage_r5_84 as coverage

BASE = Path(__file__).resolve().parent
# Exact public allowlist; no repository walks or protected resource resolution.
SOURCES = json.loads((BASE / "sources.json").read_text(encoding="utf-8"))["sources"]
TARGETS = ("filtering", "ordering", "cardinality", "tie", "defaults", "optional_null",
           "normalization", "persistence", "transition", "retry", "errors", "failure_atomicity",
           "deadline", "identity", "event_order", "event_count")

# label: FRC kind, existing BDI family, structural facts, observation
PROFILES = {
    "filtering": ("filter_order", "selection", {"selection": True}, "return"),
    "ordering": ("filter_order", "ordering", {"collection": True, "max_results": "many", "order_varies": True}, "order"),
    "cardinality": ("filter_order", "cardinality", {"selection": True, "exactly_one": True, "multiple_matches": True}, "return"),
    "tie": ("filter_order", "tie", {"selection": True, "exactly_one": True, "multiple_matches": True}, "return"),
    "defaults": ("default", "optional", {"optional_input": True}, "return"),
    "optional_null": ("optional_dispatch", "optional", {"optional_input": True}, "return"),
    "normalization": ("normalize_ascii", "normalization", {"normalize": True, "unique": False}, "return"),
    "persistence": ("persist", "persistence", {"persist": True, "failure_after_write": False}, "later"),
    "transition": ("transition", "transition", {"transition": True, "repeat": False}, "later"),
    "retry": ("transition", "retry", {"transition": True, "repeat": True, "poststate_admitted": True}, "later"),
    "errors": ("optional_dispatch", "invalid_input", {"invalid_admitted": True}, "error"),
    "failure_atomicity": ("persist", "failure_atomicity", {"persist": True, "failure_after_write": True}, "later"),
    # Detection labels only: no discovery rule or Lykoi semantic additions.
    "deadline": ("invariant", "deadline_boundary", {}, "timing"),
    "identity": ("invariant", "identity_stability", {}, "identity"),
    "event_order": ("effects", "event_ordering", {}, "events"),
    "event_count": ("effects", "event_multiplicity", {}, "events"),
    "freedom": ("filter_order", "ordering", {"collection": True, "max_results": "many", "order_varies": True}, "order"),
    "unspecified": ("sum", "arithmetic", {}, "return"),
    "ambiguity": ("filter_order", "selection", {"selection": True}, "return"),
    "conflict": ("filter_order", "cardinality", {"selection": True, "exactly_one": True, "multiple_matches": False}, "return"),
    "cross_clause": ("filter_order", "cardinality", {"selection": True, "exactly_one": True, "multiple_matches": True}, "return"),
    "nonsemantic": ("sum", "arithmetic", {}, "return"),
    "unreachable": ("filter_order", "ordering", {"collection": True, "max_results": "one", "order_varies": True}, "order"),
}


def inventory(source, label):
    """Known-answer source-only annotations; no candidate argument or completeness flag."""
    text = source["record"]["text"]
    quotes = [text]
    categories = ["BEHAVIOR"]
    if label == "optional_null":
        quotes = ["An omitted value returns zero;", "an explicit null returns null."]
        categories = ["BEHAVIOR", "BEHAVIOR"]
    elif label == "freedom":
        quotes = ["Return all records", "in any order;", "consumers may not depend on returned order."]
        categories = ["BEHAVIOR", "FREEDOM", "CONSUMER_RESTRICTION"]
    elif label == "unspecified":
        quotes = text.split(". ")
        quotes[0] += "."
        categories = ["BEHAVIOR", "UNSPECIFIED"]
    elif label == "nonsemantic":
        quotes = text.split(". ")
        quotes[0] += "."
        categories = ["BEHAVIOR", "NONBEHAVIORAL"]
    elif label in ("cross_clause", "conflict", "unreachable"):
        quotes = text.split(". ")
        quotes[0] += "."
        categories = ["CARDINALITY_BOUND", "FREEDOM"] if label == "unreachable" else ["BEHAVIOR", "BEHAVIOR"]
    elif label == "ambiguity":
        categories = ["AMBIGUITY"]
    items = []
    for n, (quote, category) in enumerate(zip(quotes, categories)):
        a = text.index(quote)
        items.append({"id": "S" + str(n + 1), "spans": [{"start": a, "end": a + len(quote), "quote": quote}],
                      "meaning": quote, "category": category, "material": category != "NONBEHAVIORAL",
                      "dependencies": ["S1"] if n and label in ("freedom", "cross_clause", "unreachable") else []})
    return {"version": coverage.SOI_VERSION, "source_commitment": frc.digest(source),
            "extractor": "coordinating-source-inventory-author", "context_class": "SAME_CONTEXT",
            "items": items, "questions": [],
            "limitations": ["Known-answer abstract profile; no claim of full natural-language completeness"]}


def candidate(label):
    raw = next(s for s in SOURCES if s["id"] == label)
    text = raw["text"]
    source = {"revision": 1, "record": {"id": "R5.84-" + label, "text": text,
              "sha256": hashlib.sha256(text.encode()).hexdigest(), "classification": "SYNTHETIC"}}
    # Inventory published in memory before candidate generation; same-context only.
    soi = inventory(source, label)
    kind, family, fact_values, channel = PROFILES[label]
    contract = {"schema_version": frc.VERSION, "contract_id": source["record"]["id"], "revision": 1,
                "source": copy.deepcopy(source["record"]),
                "context": {"scope": "Sequential abstract public operation; only stated clause distinctions are under calibration",
                            "domains": {}, "assumptions": [], "component_authority": None},
                "obligations": [], "issues": [], "unspecified": [], "implementation_choices": [],
                "lineage": [], "formalizer": "coordinating-candidate-author", "review": None}
    source_map = []
    for item in soi["items"]:
        oid = "O" + item["id"][1:]
        row = {"id": "M" + item["id"][1:], "source_ids": [item["id"]],
               "obligation_ids": [], "disposition": "REPRESENTED"}
        if item["category"] == "NONBEHAVIORAL":
            row.update(disposition="NONBEHAVIORAL", rationale="Planning-note name has no runtime observation requirement")
        elif item["category"] == "UNSPECIFIED":
            row.update(disposition="UNSPECIFIED", preserved_text=item["meaning"])
            contract["unspecified"].append(item["meaning"])
        elif label == "ambiguity":
            row.update(disposition="AMBIGUITY", issue_id="I1")
        else:
            quote = item["spans"][0]["quote"]
            contract["obligations"].append({"id": oid, "basis": "STATED", "source_quote": quote,
                "derived_from": [], "relation": {"kind": kind, "parameters": {"result": item["meaning"]}},
                "statement": item["meaning"]})
            row["obligation_ids"] = [oid]
        source_map.append(row)
    if label in ("ambiguity", "conflict"):
        contract["issues"].append({"id": "I1", "category": "CONFLICT" if label == "conflict" else "AMBIGUITY",
            "description": "Unresolved best criterion" if label == "ambiguity" else "One and two simultaneously required",
            "affects": [o["id"] for o in contract["obligations"]], "alternatives": [], "witness": None, "resolved": False})
    oids = [o["id"] for o in contract["obligations"]]
    facts = {k: {"value": v, "origin": oids or ["source"], "evidence": "Same-context abstract profile annotation"}
             for k, v in fact_values.items()}
    op = {"id": label, "facts": facts, "channels": {channel: "DELEGATED" if label == "freedom" else "MEANINGFUL"}, "authority": {}}
    from benchmark.evaluation.behavioral_discovery_r5_82 import RULES
    for f, (needs, inhibits, ch, options) in RULES.items():
        if all(fact_values.get(k) == v for k, v in needs.items()) and not any(fact_values.get(k) == v for k, v in inhibits.items()):
            if ch not in op["channels"]:
                op["channels"][ch] = "MEANINGFUL"
            if (f == "tie" and label in ("cardinality", "cross_clause")) or (f == "persistence" and label == "failure_atomicity"):
                continue  # Do not turn missing choice authority into a fixture policy.
            chosen = "rollback" if f == "failure_atomicity" else options[0]
            if label == "retry" and f == "transition":
                chosen = "unchanged"
            op["authority"][f] = {"authority": "DELEGATED" if label == "freedom" else "DETERMINED",
                                  "allowed": options if label == "freedom" else [chosen], "source_quote": text}
    entries = [{"path": ["operations", 0, group, k], "value": copy.deepcopy(v),
                "role": "OBSERVATION" if group == "channels" else "FACT" if group == "facts" else "AUTHORITY"}
               for group in ("facts", "channels", "authority") for k, v in op[group].items()]
    structural_map = [{"id": "P" + oid[1:], "obligation_id": oid,
        "status": ("UNSUPPORTED" if label in ("deadline", "identity", "event_order", "event_count")
                   else "REVIEWER_ONLY" if label in ("unspecified", "nonsemantic") else "REPRESENTED"),
        "family": family, "entries": copy.deepcopy(entries),
        "rationale": "Reviewed synthetic projection"} for oid in oids]
    return {"version": coverage.VERSION, "source": source, "soi": soi, "contract": contract,
            "interface": {"operations": [op]}, "source_map": source_map, "structural_map": structural_map,
            "implications": [], "questions": [], "disagreements": []}


def review(bundle):
    """Synthetic bookkeeping review, never an actual independent semantic approval."""
    keys = ["inventory:" + i["id"] for i in bundle["soi"]["items"]]
    for group, prefix in (("source_map", "mapping:"), ("structural_map", "projection:"), ("implications", "implication:")):
        keys += [prefix + r["id"] for r in bundle[group]]
    keys += ["exclusion:" + r["id"] for r in bundle["source_map"] if r["disposition"] == "EXCLUDED"]
    receipt = {"version": coverage.VERSION, "reviewer": "synthetic-bookkeeping-reviewer", "context_class": "SAME_CONTEXT",
               "evidence_commitment": coverage.evidence_hash(bundle), "result": "COVERAGE_APPROVED",
               "judgments": {k: {"result": "PASS", "rationale": "Known-answer fixture judgment; NOT independent authority"} for k in keys}}
    admission = {"mode": "PUBLIC_SYNTHETIC_EXPERIMENT", "reviewer": receipt["reviewer"],
                 "review_commitment": frc.digest(receipt), "inventory_commitment": frc.digest(bundle["soi"])}
    fidelity = {"contract_commitment": frc.digest(bundle["contract"]), "reviewer": "synthetic-fidelity-bookkeeper",
                "outcome": "APPROVED", "checks": {k: True for k in frc.CHECKS}, "findings": []}
    return receipt, admission, fidelity


def run_bundle(bundle):
    return coverage.downstream(bundle, *review(bundle))


def two_clause(label):
    """Generalize the R5.83 store-plus-omitted-behavior negative control."""
    base, target = candidate("persistence"), candidate(label)
    prefix = base["source"]["record"]["text"] + " "
    text = prefix + target["source"]["record"]["text"]
    base["source"]["record"].update(id="R5.84-two-clause-" + label, text=text,
                                  sha256=hashlib.sha256(text.encode()).hexdigest())
    base["contract"]["source"] = copy.deepcopy(base["source"]["record"])
    base["contract"]["contract_id"] = base["source"]["record"]["id"]
    sid = {i["id"]: "T" + i["id"] for i in target["soi"]["items"]}
    oid = {o["id"]: "T" + o["id"] for o in target["contract"]["obligations"]}
    for item in target["soi"]["items"]:
        item["id"] = sid[item["id"]]
        item["dependencies"] = [sid[x] for x in item["dependencies"]]
        for span in item["spans"]:
            span["start"] += len(prefix)
            span["end"] += len(prefix)
    base["soi"]["items"] += target["soi"]["items"]
    base["soi"]["source_commitment"] = frc.digest(base["source"])
    for o in target["contract"]["obligations"]:
        o["id"] = oid[o["id"]]
    base["contract"]["obligations"] += target["contract"]["obligations"]
    for row in target["source_map"]:
        row["id"] = "T" + row["id"]
        row["source_ids"] = [sid[x] for x in row["source_ids"]]
        row["obligation_ids"] = [oid[x] for x in row["obligation_ids"]]
    base["source_map"] += target["source_map"]
    op = target["interface"]["operations"][0]
    for fact in op["facts"].values():
        fact["origin"] = [oid.get(x, x) for x in fact["origin"]]
    base["interface"]["operations"].append(op)
    for row in target["structural_map"]:
        row["id"] = "T" + row["id"]
        row["obligation_id"] = oid[row["obligation_id"]]
        for e in row["entries"]:
            e["path"][1] = 1
            e["value"] = copy.deepcopy(op[e["path"][2]][e["path"][3]])
    base["structural_map"] += target["structural_map"]
    return base


def omission(label, structural=False):
    b = two_clause(label)
    if structural:
        b["interface"]["operations"].pop()
    else:
        b["contract"]["obligations"] = [o for o in b["contract"]["obligations"] if not o["id"].startswith("T")]
        b["interface"]["operations"].pop()
        b["structural_map"] = [r for r in b["structural_map"] if not r["id"].startswith("T")]
    b["coverage_complete"] = True
    return b
