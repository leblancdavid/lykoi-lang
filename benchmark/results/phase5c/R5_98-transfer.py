"""Post-freeze evidence only. Never repairs generic implementation or old results."""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from air_compiler.collection_query import QueryError, validate
from benchmark.evaluation import formal_requirements_r5_80 as frc
from lykoi_controller import Failure
from lykoi_query import contracts
from lykoi_query.corpus import queries


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_freeze():
    freeze = json.loads((OUT / "R5_98-SYNTHETIC-FREEZE.json").read_text(encoding="utf-8"))
    for path, expected in freeze["files"].items():
        assert sha(ROOT / path) == expected, path
    assert sha(OUT / "R5_98-VERIFICATION.json") == freeze["verification_sha256"]


def main():
    check_freeze()
    public = json.loads((OUT / "r5_82/corpus.json").read_text(encoding="utf-8"))
    source = next(c for c in public["cases"] if c["id"] == "nullable")
    # Probe the exact unsupported operator/type class, without inventing an
    # equality interpretation of a less-than requirement. No historical repair.
    q = queries()[0]
    q["id"] = "public-price-limit"
    q["predicate"] = {"field": "category", "operator": "less_than", "operand": {"parameter": "requested_category"}}
    try:
        validate(q)
        raise AssertionError("Unexpected range support")
    except QueryError as exc:
        public_result = {"classification": "UNSUPPORTED_RANGE_AND_NULLABILITY", "probe_error": str(exc),
                         "source": source, "source_sha256": sha(OUT / "r5_82/corpus.json"),
                         "scope": "Operator-class refusal probe, not a faithful complete authored price application",
                         "unchanged_gaps": ["less_than predicate", "numeric runtime parameter", "nullable field policy"]}
    first_path = OUT / "R5_97-B03_FIRST_RESULT.json"
    before = sha(first_path)
    first = json.loads(first_path.read_text(encoding="utf-8"))
    assert first["B03_FIRST_RESULT"] == "DECISION_DISCOVERY_UNSUPPORTED"
    for evidence in first["evidence"]:
        assert sha(ROOT / evidence["path"]) == evidence["sha256"], evidence["path"]
    c = json.loads((OUT / "R5_97-FRC.json").read_text(encoding="utf-8"))
    # Native preserved candidate is intentionally not rewritten into synthetic
    # provenance or guessed typed facets. This is the declared transfer target.
    p = contracts.structural(c, frc.digest(c))
    try:
        contracts.coverage(c, p)
        raise AssertionError("Unexpected legacy prose mapping")
    except Failure as exc:
        outcome = str(exc)
        assert "STRUCTURAL_COVERAGE_FAILURE" in outcome
    check_freeze()
    assert sha(first_path) == before
    result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "freeze_sha256": sha(OUT / "R5_98-SYNTHETIC-FREEZE.json"),
              "historical_public_transfer": public_result,
              "B03_POST_EXPOSURE_TRANSFER": "STRUCTURAL_COVERAGE_FAILURE",
              "target": "Unmodified R5.97 candidate FRC through prospective query structural adapter",
              "failure": outcome, "projection": p,
              "gap": "Legacy prose relations and CLI/storage context have no faithful typed-facet adapter in this profile",
              "downstream": {name: "NOT_RUN" for name in ("BDI", "adequacy", "V1", "authoring", "compilation", "behavioral_verification")},
              "B03_FIRST_RESULT": first["B03_FIRST_RESULT"], "first_result_sha256": before,
              "immutable_evidence_verified": len(first["evidence"]),
              "generic_implementation_unchanged": True,
              "stop": "No remediation after transfer; no B04 access"}
    with (OUT / "R5_98-TRANSFER.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(result["B03_POST_EXPOSURE_TRANSFER"])
    print(public_result["classification"])


if __name__ == "__main__":
    main()
