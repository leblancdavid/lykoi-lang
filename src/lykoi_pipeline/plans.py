"""Independent deterministic verification fixtures, reviewed before authorship.

This producer runs in the verifier role; it receives WHAT, never implementation.
Component-context observation is explicitly unqualified in this bounded producer.
"""
import copy

from lykoi_controller import Failure, canonical
import hashlib

VERSION = "external-cli-plan-1"
ISOLATION = "SEPARATE_ROLE_DETERMINISTIC_FIXTURE_NO_MODEL_PROVIDER_INDEPENDENCE"


def produce(contract):
    cases, rows = [], []
    for o in contract["obligations"]:
        oid, r = o["id"], o["relation"]
        kind, p = r["kind"], r["parameters"]
        steps = None
        if kind == "crud" and p == {"domain": "task creation", "result": "supplied title"}:
            steps = [{"argv": ["create", "--title", "public title", "--description", "public description"],
                      "returncode": 0, "contains": ["public title"]}]
        elif kind == "priority_create" and p.get("result") in ("LOW", "NORMAL", "HIGH"):
            steps = [{"argv": ["create", "--title", "default probe", "--description", "public"],
                      "returncode": 0, "contains": [p["result"]]}]
        elif kind == "priority_filter" and p.get("predicate") == "HIGH":
            steps = [{"argv": ["create", "--title", "included", "--description", "public", "--priority", "HIGH"], "returncode": 0, "contains": []},
                     {"argv": ["create", "--title", "excluded", "--description", "public", "--priority", "LOW"], "returncode": 0, "contains": []},
                     {"argv": ["list-high"], "returncode": 0, "contains": ["included"], "absent": ["excluded"]}]
        elif kind == "filter_order" and p.get("ordering") == "unconstrained":
            rows.append({"obligation": oid, "classification": "AUTHORIZED_FREEDOM",
                         "justification": "No order expectation; membership remains tested independently", "cases": []})
            continue
        if steps is None:
            rows.append({"obligation": oid, "classification": "UNVERIFIED",
                         "justification": "No independent external CLI fixture for this relation", "cases": []})
            continue
        case = {"id": oid + ":external", "obligations": [oid], "initial_state": "fresh_directory",
                "steps": steps, "invariants": [], "transitions": "Ordered commands share case-local persisted state",
                "rejections": "Only contract-authorized expectations; unspecified errors are not invented"}
        case["identity"] = hashlib.sha256(canonical(case)).hexdigest()
        cases.append(case)
        rows.append({"obligation": oid, "classification": "EXERCISED", "justification": "WHAT-derived public CLI fixture", "cases": [case["identity"]]})
    if contract["context"]["component_authority"] is not None:
        rows.append({"obligation": "@component-context", "classification": "UNVERIFIED",
                     "justification": "Complete component behavior lacks a qualified external execution fixture", "cases": []})
    return {"version": VERSION, "outcome": "READY" if all(r["classification"] != "UNVERIFIED" for r in rows) and cases else "UNVERIFIED",
            "producer": ISOLATION, "cases": cases, "coverage": rows,
            "limitations": ["Bounded synthetic fixtures; no general semantic extraction qualification"]}


def review_coverage(contract, plan):
    expected = {o["id"] for o in contract["obligations"]}
    if contract["context"]["component_authority"] is not None:
        expected.add("@component-context")
    rows = plan["coverage"]
    if len(rows) != len(expected) or {r["obligation"] for r in rows} != expected:
        raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Missing, duplicate or extra obligation")
    identities = {c["identity"] for c in plan["cases"]}
    if not identities or len(identities) != len(plan["cases"]):
        raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Empty or duplicate cases")
    for case in plan["cases"]:
        body = {k: v for k, v in case.items() if k != "identity"}
        if case["identity"] != hashlib.sha256(canonical(body)).hexdigest() or not case["steps"]:
            raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Case identity mismatch")
        if not set(case["obligations"]) <= expected:
            raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Unbound case")
        for fixture in case.get("initial_files", []):
            if set(fixture) != {"path", "json"} or fixture["path"] not in ("measurements.json", "tasks.json"):
                raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Fixture state allowlist violation")
        if len({f["path"] for f in case.get("initial_files", [])}) != len(case.get("initial_files", [])):
            raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Duplicate fixture state")
        for step in case["steps"]:
            if (not isinstance(step["argv"], list) or not all(type(x) is str for x in step["argv"])
                    or type(step["returncode"]) is not int or not all(type(x) is str for x in step["contains"])):
                raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Invalid executable case")
            if any(p not in ("measurements.json", "tasks.json") for p in step.get("preserved", [])):
                raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Preservation state allowlist violation")
            for observation in step.get("files", []):
                if set(observation) != {"path", "json"} or observation["path"] not in ("measurements.json", "tasks.json"):
                    raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Fixture state allowlist violation")
    for r in rows:
        if not r["justification"] or r["classification"] not in ("EXERCISED", "AUTHORIZED_FREEDOM"):
            raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", obligation=r["obligation"])
        if r["classification"] == "EXERCISED" and (not r["cases"] or not set(r["cases"]) <= identities):
            raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", obligation=r["obligation"])
        if r["classification"] == "EXERCISED" and any(r["obligation"] not in next(c for c in plan["cases"] if c["identity"] == cid)["obligations"] for cid in r["cases"]):
            raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="False traceability")
        if r["classification"] == "AUTHORIZED_FREEDOM":
            obligation = next((o for o in contract["obligations"] if o["id"] == r["obligation"]), None)
            if obligation is None or obligation["relation"] != {"kind": "filter_order", "parameters": {"domain": "task lists", "ordering": "unconstrained"}}:
                raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Unjustified test exclusion")
    return copy.deepcopy(rows)
