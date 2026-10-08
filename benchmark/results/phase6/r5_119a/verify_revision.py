"""Read-only revision/provenance bookkeeping; no ACL engine or pipeline execution."""
import hashlib
import json
from pathlib import Path

from benchmark.evaluation.formal_requirements_r5_80 import check_revision, digest, validate


HERE = Path(__file__).resolve().parent
PREVIOUS = HERE.parent / "r5_119"
CURATION = HERE.parent / "r5_116a"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    old_ids = load(PREVIOUS / "IDENTITIES.json")
    old = load(PREVIOUS / "FRC-CANDIDATE.json")
    old_plan = load(PREVIOUS / "ACCEPTANCE-PLAN-CANDIDATE.json")
    assert validate(old) == old_ids["frc_canonical_sha256"]
    assert digest(old_plan) == old_ids["acceptance_plan_canonical_sha256"]
    assert sha(PREVIOUS / "FRC-CANDIDATE.json") == old_ids["frc_file_sha256"]
    assert sha(PREVIOUS / "ACCEPTANCE-PLAN-CANDIDATE.json") == old_ids["acceptance_plan_file_sha256"]
    for name, expected in old_ids["review_files_sha256"].items():
        assert sha(PREVIOUS / name) == expected, name
    p = load(CURATION / "P6-A03-provenance.json")
    assert p["repository"] == "redis/redis" and p["issue_number"] == 13736
    for key in ("source", "issue_api", "search", "repository_capture",
                "repository_ref_capture", "acceptance"):
        assert sha(CURATION / p[key]["path"]) == p[key]["sha256"], key
    original = load(CURATION / p["source"]["path"])
    assert original["body"] == old["source"]["text"]
    assert p["source"]["sha256"] == old_ids["source_capture_sha256"]

    e = load(HERE / "INHERITED-EVIDENCE.json")
    assert e["revision_committer_utc"] < p["issue_created_at"]
    assert e["baseline_probes_executed"] == e["acceptance_tests_executed"] == 0
    quotes = {q["id"]: q["text"] for d in e["documents"] for q in d["quotes"]}
    assert len(quotes) == 15
    assert all(d["url"].startswith("https://raw.githubusercontent.com/redis/redis-doc/" + e["revision"] + "/") for d in e["documents"])
    new = load(HERE / "FRC-CANDIDATE-R2.json")
    frc_digest = validate(new)
    edge = check_revision(old, new)
    composite = original["body"] + "\n\n[Inherited documentation, not issue-author text: redis/redis-doc@" + e["revision"] + "]\n"
    sections = (("D1 topics/acl.md:", ["D1-Q1", "D1-Q2", "D1-Q3", "D1-Q4", "D1-Q5"]),
                ("D2 commands/acl-setuser.md:", ["D2-Q2", "D2-Q3"]),
                ("D3 commands/select.md:", ["D3-Q1", "D3-Q2", "D3-Q3"]))
    composite += "\n".join(title + "\n" + "\n".join(quotes[q] for q in ids) for title, ids in sections)
    assert new["source"]["text"] == composite
    domains = new["context"]["domains"]
    assert domains["inherited_evidence_canonical_sha256"] == digest(e)
    assert domains["original_source_capture_sha256"] == p["source"]["sha256"]
    assert domains["original_body_sha256"] == old["source"]["sha256"]
    assert domains["original_provenance_sha256"] == sha(CURATION / "P6-A03-provenance.json")
    assert domains["prior_frc_canonical_sha256"] == old_ids["frc_canonical_sha256"]
    assert not new["issues"] and new["review"] is None

    plan = load(HERE / "ACCEPTANCE-PLAN-R2.json")
    assert plan["frc"]["canonical_sha256"] == frc_digest
    assert plan["frc"]["revision"] == 2
    assert plan["composite_source_sha256"] == new["source"]["sha256"]
    assert plan["inherited_evidence_canonical_sha256"] == digest(e)
    assert plan["original_source_capture_sha256"] == p["source"]["sha256"]
    assert plan["original_body_sha256"] == old["source"]["sha256"]
    assert plan["previous_plan_canonical_sha256"] == old_ids["acceptance_plan_canonical_sha256"]
    assert plan["approved"] is False and plan["sealed"] is False
    assert plan["native_plan"] is None and plan["acceptance_tests_executed"] == 0
    assert not plan["material_questions"] and plan["fixed_before_authoring"] is True
    checks = plan["checks"]
    assert len(checks) == len({c["id"] for c in checks}) == 7
    obligations = {o["id"] for o in new["obligations"]}
    assert set(domains["source_traceability"]) == obligations
    assert {oid for c in checks for oid in c["obligations"]} == obligations
    for check in checks:
        assert check["executed"] is False
        assert all(check[k] for k in ("inputs", "expected", "state_effects", "error_behavior", "source_basis"))
    mixed = checks[4]["cases"]
    controls = checks[5]["cases"]
    assert len(mixed) == 12 and len(controls) == 4
    assert [row["expected_select"] for row in mixed] == [
        "DENY", "ALLOW", "ALLOW", "DENY", "DENY", "ALLOW",
        "DENY", "ALLOW", "ALLOW", "DENY", "DENY", "ALLOW"]
    assert all(row["expected_marker"] == ("d-marker" if row["expected_select"] == "ALLOW" else "zero-marker") for row in mixed)
    assert [row["expected_permission"] for row in controls] == ["DENY", "ALLOW", "DENY", "ALLOW"]

    result = {
        "original_source_capture_sha256": p["source"]["sha256"],
        "composite_source_sha256": new["source"]["sha256"],
        "evidence_canonical_sha256": digest(e),
        "frc_canonical_sha256": frc_digest,
        "frc_file_sha256": sha(HERE / "FRC-CANDIDATE-R2.json"),
        "acceptance_plan_canonical_sha256": digest(plan),
        "acceptance_plan_file_sha256": sha(HERE / "ACCEPTANCE-PLAN-R2.json"),
        "revision_edge": edge,
        "bookkeeping": "PASS_NOT_APPROVAL_OR_BEHAVIORAL_VERIFICATION",
        "baseline_probes_executed": 0,
        "acceptance_tests_executed": 0,
    }
    manifest_path = HERE / "IDENTITIES.json"
    if manifest_path.exists():
        recorded = load(manifest_path)
        for key, value in result.items():
            assert recorded[key] == value, key
        for name, expected in recorded["publication_files_sha256"].items():
            assert sha(HERE / name) == expected, name
        print("Publication identities: PASS")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
