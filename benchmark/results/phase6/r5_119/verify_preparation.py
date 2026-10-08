"""Read-only P6-A03 preparation integrity; no semantic stages or behavioral tests."""
import hashlib
import json
from pathlib import Path

from benchmark.evaluation.formal_requirements_r5_80 import digest, validate


HERE = Path(__file__).resolve().parent
CURATION = HERE.parent / "r5_116a"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    provenance = load(CURATION / "P6-A03-provenance.json")
    assert provenance["repository"] == "redis/redis"
    assert provenance["issue_number"] == 13736
    assert provenance["selection_order"] == 3
    for key in ("source", "issue_api", "search", "repository_capture",
                "repository_ref_capture", "acceptance"):
        row = provenance[key]
        assert row["path"].startswith(("captures/redis__redis/", "acceptance/P6-A03"))
        assert sha(CURATION / row["path"]) == row["sha256"], key
    source = load(CURATION / provenance["source"]["path"])
    issue = load(CURATION / provenance["issue_api"]["path"])
    repo = load(CURATION / provenance["repository_capture"]["path"])
    for field in ("title", "body"):
        assert source[field] == issue[field]
        assert hashlib.sha256(source[field].encode("utf-8")).hexdigest() == provenance[field + "_utf8_sha256"]
    assert source["title"] == provenance["original_title"]
    for field, saved in (("number", "issue_number"), ("id", "issue_numeric_id"),
                         ("node_id", "issue_node_id"), ("html_url", "issue_url"),
                         ("created_at", "issue_created_at"), ("updated_at", "issue_updated_at")):
        assert issue[field] == provenance[saved], field
    assert issue["user"]["login"] == provenance["author_login"]
    assert issue["user"]["id"] == provenance["author_numeric_id"]
    assert repo["full_name"] == provenance["repository"]
    assert repo["id"] == provenance["repository_numeric_id"]

    frc = load(HERE / "FRC-CANDIDATE.json")
    commitment = validate(frc)  # Existing envelope only: no projection/review gate.
    assert frc["source"]["text"] == source["body"]
    assert frc["context"]["domains"]["source_capture_sha256"] == provenance["source"]["sha256"]
    assert frc["context"]["domains"]["source_provenance_sha256"] == sha(CURATION / "P6-A03-provenance.json")
    assert frc["review"] is None
    assert [q["id"] for q in frc["issues"]] == ["A03-Q1"]
    assert all(q["resolved"] is False for q in frc["issues"])

    plan = load(HERE / "ACCEPTANCE-PLAN-CANDIDATE.json")
    assert plan["frc"]["canonical_sha256"] == commitment
    assert plan["source"]["capture_sha256"] == provenance["source"]["sha256"]
    assert plan["source"]["body_sha256"] == provenance["body_utf8_sha256"]
    assert plan["fixed_before_authoring"] is True
    assert plan["expectation_basis"] == "preserved-source"
    assert plan["approved"] is False and plan["sealed"] is False
    assert plan["native_plan"] is None
    ids = {o["id"] for o in frc["obligations"]}
    checks = plan["checks"]
    assert len({c["id"] for c in checks}) == len(checks) == 6
    assert {oid for c in checks for oid in c["obligations"]} == ids
    for check in checks:
        assert check["source_quote"] in source["body"], check["id"]
        assert check["inputs"] and check["observable"] and check["expected"]
        assert check["state_effects"] and check["error_behavior"]
        assert check["status"].endswith("NOT_RUN")
    assert checks[4]["expected"]["selected_expectation"] is None
    assert checks[5]["expected"]["selected_expectation"] is None

    result = {
        "source_capture_sha256": provenance["source"]["sha256"],
        "source_body_sha256": provenance["body_utf8_sha256"],
        "frc_canonical_sha256": commitment,
        "frc_file_sha256": sha(HERE / "FRC-CANDIDATE.json"),
        "acceptance_plan_canonical_sha256": digest(plan),
        "acceptance_plan_file_sha256": sha(HERE / "ACCEPTANCE-PLAN-CANDIDATE.json"),
        "frc_envelope": "VALID_NOT_APPROVED",
        "source_and_binding_checks": "PASS",
        "external_checks_executed": 0,
    }
    identity_path = HERE / "IDENTITIES.json"
    if identity_path.exists():
        recorded = load(identity_path)
        for key, value in result.items():
            assert recorded[key] == value, key
        for name, expected in recorded["review_files_sha256"].items():
            assert sha(HERE / name) == expected, name
        print("Recorded identities and human review files: PASS")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
