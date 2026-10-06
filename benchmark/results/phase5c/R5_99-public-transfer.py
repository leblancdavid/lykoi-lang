"""Already-public negative transfers after generic freeze. No benchmark access.

This driver reads only the named R5.80 and R5.82 public synthetic records.
It never reads requirement directories, B03 or later benchmark logs/oracles.
"""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from lykoi_controller import Failure, canonical
from lykoi_pipeline import PipelineController, contracts
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.producers import ModelAdapter


def verify_freeze():
    freeze = json.loads((OUT / "R5_99-GENERIC-FREEZE.json").read_text(encoding="utf-8"))
    changed = [p for p, h in freeze["files"].items() if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h]
    if changed:
        raise RuntimeError("Generic freeze changed: " + str(changed))
    return hashlib.sha256((OUT / "R5_99-GENERIC-FREEZE.json").read_bytes()).hexdigest()


def attempt(identity, source_text, obligations, issues, gaps):
    """Unrepresentable semantics are retained as ordinary unsupported FRC facts."""
    with tempfile.TemporaryDirectory() as tmp:
        c = PipelineController(Path(tmp) / "public.sqlite", PRINCIPALS)
        try:
            w = Workspace(c, "public", "public-transfer-" + identity, CREDENTIALS)
            w.ingest(CREDENTIALS["owner"], source_text)
            def formal(request):
                authority = {o["id"]: [e["identity"] for e in request["evidence"] if e["provenance"] == "human_statement"] for o in obligations}
                return {"obligations": copy.deepcopy(obligations), "issues": copy.deepcopy(issues), "authority": authority,
                        "questions": [], "unsupported": gaps}
            formalizer = ModelAdapter("formalizer", identity + ":formalizer", formal, provider="OpenAI", model="openai/gpt-6.1-sol/recorded-active-agent-capture")
            fid = w.formalize(formalizer)
            contract = c.artifact(fid)["content"]["contract"]
            def review(request):
                # Source-side analytical record, no candidate passed in the request.
                record = {"id": request["source"]["identity"], "text": source_text, "classification": "SYNTHETIC", "sha256": hashlib.sha256(source_text.encode()).hexdigest()}
                refs = [e["identity"] for e in request["evidence"] if e["provenance"] == "human_statement"]
                inventory = {"version": "SourceObligationInventory-0.1", "source_commitment": hashlib.sha256(canonical({"revision": request["source"]["revision"], "record": record})).hexdigest(),
                             "extractor": "same-agent-public-source-review", "context_class": "SAME_AGENT_ANALYTICAL_CAPTURE",
                             "items": [{"id": o["id"], "spans": [{"start": 0, "end": len(source_text), "quote": source_text}], "meaning": o["statement"],
                                        "category": "BEHAVIOR", "material": True, "dependencies": []} for o in obligations],
                             "questions": [i["description"] for i in issues], "limitations": ["Same-agent source-side analytical review"]}
                return {"inventory": inventory, "interpretations": {o["id"]: {k: o[k] for k in ("statement", "relation")} for o in obligations},
                        "authority": {o["id"]: refs for o in obligations}}
            soi = w.commit_inventory(ModelAdapter("reviewer", identity + ":reviewer", review, provider="OpenAI", model="openai/gpt-6.1-sol/recorded-active-agent-capture"))
            coverage = w.reconcile(soi)
            projection = contracts.structural(contract, fid)
            try:
                structural_result = contracts.coverage(contract, projection)
            except Failure as exc:
                structural_result = exc.as_dict()
            return {"id": identity, "source": source_text, "formalization": "VALID_FRC_UNSUPPORTED_MEANING_RETAINED", "typed_query_formalization": "UNSUPPORTED",
                    "contract": contract, "reconciliation": c.artifact(coverage)["content"],
                    "structural_diagnostic": projection, "structural_coverage": structural_result,
                    "normal_terminal": "NEEDS_CLARIFICATION" if issues else "UNSUPPORTED_SCOPE",
                    "gaps": gaps, "bdi": "NOT_RUN", "adequacy": "NOT_RUN", "v1": "NOT_RUN", "authoring": "NOT_RUN", "compilation": "NOT_RUN", "external_behavior": "NOT_RUN"}
        finally:
            c.close()


def main():
    before = verify_freeze()
    old = json.loads((OUT / "r5_80/candidates.json").read_text(encoding="utf-8"))
    public = json.loads((OUT / "r5_82/corpus.json").read_text(encoding="utf-8"))
    records = []
    for key, gaps in [("S03", ["Stable input-occurrence ties without unique identity", "Activation predicate/type needs clarification"]),
                      ("S11", ["Numeric greater-than predicate", "Numeric runtime limit", "Prefix/cardinality limit and input-occurrence order"])]:
        candidate = old[key]
        records.append(attempt("R5.80." + key, candidate["source"]["text"], candidate["obligations"], candidate["issues"], gaps))
    for key in ("nullable", "nonnull"):
        source = next(c["source"] for c in public["cases"] if c["id"] == key)
        row = {"id": "PRICE.SELECT", "basis": "STATED", "source_quote": source, "derived_from": [],
               "statement": "Return records whose numeric price is less than supplied limit; " + ("null price is admitted, behavior unresolved." if key == "nullable" else "admitted calls have non-null prices."),
               "relation": {"kind": "filter_order", "parameters": {"predicate": {"field": "price", "operator": "less_than", "operand": {"parameter": "limit"}},
                            "price_domain": "nullable" if key == "nullable" else "admitted non-null"}}}
        gaps = ["Numeric less-than predicate", "Numeric runtime binding"] + (["Nullable predicate/meaning"] if key == "nullable" else [])
        records.append(attempt("R5.82." + key, source, [row], [], gaps))
    after = verify_freeze()
    result = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "freeze_before": before, "freeze_after": after,
              "outcome": "PUBLIC_FILTERING_GAPS_REMAIN", "cases": records,
              "B03_POST_EXPOSURE_TRANSFER_2": "NOT_RUN_FIREWALL_INCIDENT", "historical_results_changed": False,
              "later_requirement_files_opened": False, "limitation": "Generic engineering only; benchmark log disclosure invalidates nonexposure claim"}
    with (OUT / "R5_99-PUBLIC-TRANSFER.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False); stream.write("\n")
    print(result["outcome"])
    for row in records:
        print(row["id"], row["normal_terminal"], "; ".join(row["gaps"]))


if __name__ == "__main__":
    main()
