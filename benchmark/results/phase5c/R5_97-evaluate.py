"""Single R5.97 research evaluation; calls unchanged pure product functions.

This is experiment evidence, not a formalizer/mapping/verification capability.
No approval identity, independent reviewer, or implementation grant is fabricated.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

from lykoi_controller import Failure
from lykoi_protected.compatibility import frc, contracts

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
PREFIX = "R5_97-"
assert not (OUT / (PREFIX + "B03_FIRST_RESULT.json")).exists(), "No rerun allowed"


def save(name, value):
    path = OUT / (PREFIX + name + ".json")
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")
    return path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


access = json.loads((OUT / (PREFIX + "B03-ACCESS.json")).read_text(encoding="utf-8"))
text = access["source_text"]
assert hashlib.sha256(text.encode("utf-8")).hexdigest() == access["source_sha256"]
# No rereading B03, oracle, other-track implementation, or later requirements.
context = []
for relative in ("benchmark/baseline.md", "benchmark/requirements/README.md"):
    path = ROOT / relative
    context.append({"path": relative, "sha256": sha(path), "text": path.read_bytes().decode("utf-8")})
save("CONTEXT", {"authority": "Frozen shared benchmark contract, not implementation behavior", "sources": context})

# Source-first accounting: exact spans; no new relation vocabulary or inferred policy.
specs = [
    ("B03-REQ-001", "Add `list-tag --tag VALUE`.", "crud",
     {"domain": "Existing task CLI", "operation": "list-tag --tag VALUE", "condition": "Invocation of the new command", "result": "Read/list task query under the shared JSON subprocess contract", "frame": "B03-REQ-009"},
     "The task CLI shall expose list-tag --tag VALUE using the existing JSON subprocess interface."),
    ("B03-REQ-002", "Return tasks whose `tags` contains exactly VALUE", "filter_order",
     {"domain": "Valid stored tasks and nonblank query VALUE", "predicate": "tags contains a string exactly equal to VALUE", "multiplicity": "All and only qualifying tasks, each once", "frame": "B03-REQ-009"},
     "For a valid nonblank query, return all and only tasks with a tag exactly equal to the supplied VALUE."),
    ("B03-REQ-003", "case-sensitive", "filter_order",
     {"domain": "B03-REQ-002", "comparison": "Case-sensitive exact equality", "result": "work does not match Work", "frame": "B03-REQ-009"},
     "Tag matching shall be case-sensitive; work shall not select a task tagged only Work."),
    ("B03-REQ-004", "query input is not trimmed", "filter_order",
     {"domain": "Nonblank query VALUE", "comparison": "Use VALUE verbatim without trimming", "result": "Whitespace around nonblank input remains part of the match value", "frame": "B03-REQ-009"},
     "Matching shall use the supplied query verbatim without trimming it."),
    ("B03-REQ-005", "including completed tasks", "filter_order",
     {"domain": "Existing valid task statuses", "predicate": "B03-REQ-002 without excluding completed tasks", "result": "Qualifying completed and pending tasks included", "frame": "B03-REQ-009"},
     "Qualifying completed tasks shall be included along with qualifying pending tasks."),
    ("B03-REQ-006", "normal order", "filter_order",
     {"domain": "Returned matching task list", "ordering": "(created_at, id) ascending", "authority": "benchmark/baseline.md and benchmark/requirements/README.md", "multiplicity": "B03-REQ-002", "frame": "B03-REQ-009"},
     "The returned matching tasks shall be ordered by (created_at, id) ascending, as defined by the shared benchmark contract."),
    ("B03-REQ-007", "Reject blank or whitespace-only query input with `invalid_tag`.", "transition",
     {"domain": "Blank or whitespace-only query VALUE", "condition": "Query input is blank or whitespace-only", "result": "Reject with invalid_tag in the shared JSON error envelope on stderr and exit 1", "successor_state": "Unchanged storage", "frame": "B03-REQ-009"},
     "Blank or whitespace-only query input shall fail with invalid_tag, using the existing JSON error envelope and exit status, without changing storage."),
    ("B03-REQ-008", "A tag not present returns `[]`", "filter_order",
     {"domain": "Valid nonblank query VALUE", "condition": "No stored task has an exactly matching tag", "result": [], "frame": "B03-REQ-009"},
     "A valid query with no matching tag shall return an empty JSON list."),
    ("B03-REQ-009", "the query never changes storage", "transition",
     {"domain": "Every list-tag invocation", "condition": "Success or rejection", "successor_state": "Storage unchanged, including observable persisted bytes and file absence", "result": "No storage mutation", "frame": "All existing stored tasks and unrelated fields preserved"},
     "The query shall never change storage, on either success or rejection; persisted bytes and file absence shall remain unchanged."),
]

items, rows, coverage = [], [], []
for n, (oid, quote, kind, parameters, statement) in enumerate(specs, 1):
    start = text.index(quote)
    span = {"start": start, "end": start + len(quote), "quote": quote}
    item = {"id": f"B03-SOI-{n:03}", "spans": [span], "category": "OBLIGATION",
            "meaning": statement, "material": True, "dependencies": []}
    items.append(item)
    rows.append({"id": oid, "basis": "STATED", "source_quote": quote, "derived_from": [],
                 "relation": {"kind": kind, "parameters": parameters}, "statement": statement})
    coverage.append({"source_id": item["id"], "obligation_ids": [oid], "span": span,
                     "disposition": "REPRESENTED_IN_FRC", "rationale": "Exact normative source fragment"})

# Account for every full line too, retaining punctuation, wrapping and the example.
line_ledger = []
offset = 0
for line in text.splitlines(keepends=True):
    ids = [r["id"] for r in rows if any(
        s["start"] < offset + len(line) and s["end"] > offset
        for i in items if i["meaning"] == r["statement"] for s in i["spans"])]
    if "`work` does not select" in line or "task tagged `Work`" in line:
        ids = sorted(set(ids + ["B03-REQ-002", "B03-REQ-003"]))
    line_ledger.append({"start": offset, "end": offset + len(line), "quote": line,
                        "obligation_ids": ids,
                        "disposition": "SOURCE_CONTEXT_TITLE" if line.startswith("#") else
                        "LAYOUT" if not line.strip() else "NORMATIVE_OR_EXAMPLE",
                        "rationale": "Title identifies benchmark and local scope" if line.startswith("#") else
                        "Blank formatting line" if not line.strip() else "Normative clauses and exact illustrative case remain accounted for"})
    offset += len(line)
assert offset == len(text)
inventory = {"version": "SourceObligationInventory-0.1", "source_sha256": access["source_sha256"],
             "producer": "openai/gpt-6.1-sol / active research agent", "items": items, "questions": [],
             "source_lines": line_ledger,
             "isolation": "Same active agent context; NOT independent/blind source-only review. Inventory saved before FRC artifact; no qualified reviewer or authority receipt asserted."}
inventory_path = save("SOI", inventory)
contract = {"schema_version": frc.VERSION, "contract_id": "R5.97-B03", "revision": 1,
            "source": {"id": "B03", "text": text, "sha256": access["source_sha256"],
                       "classification": "PROTECTED_EVALUATION"},
            "context": {"scope": "B03 local list-by-tag change to the existing task CLI under the frozen shared benchmark contract; requirements/README.md retains cumulative compatibility. No other-track implementation or hidden oracle is authority.",
                        "domains": {"query": "CLI string VALUE; blank/whitespace-only rejected; other VALUE compared verbatim", "tasks": "Valid task records with tags, pending or completed", "order": "(created_at, id) ascending per frozen shared contract"},
                        "assumptions": [], "component_authority": None},
            "obligations": rows, "issues": [],
            "unspecified": ["No new concurrency, performance or internal-algorithm policy is supplied by B03; existing shared contract remains applicable."],
            "implementation_choices": ["Any internal strategy that preserves the complete required observable behavior."],
            "lineage": [], "formalizer": "openai/gpt-6.1-sol / active research agent", "review": None}
contract_path = save("FRC", contract)
contract_id = frc.validate(contract)
save("FORMALIZATION", {"outcome": "FRC_CANDIDATE_STRUCTURALLY_VALID", "contract_commitment": contract_id,
                       "source_sha256": access["source_sha256"], "obligation_count": len(rows),
                       "active_issues": [], "material_ambiguities_detected": [], "conflicts_detected": [],
                       "normal_order_authority": context[0]["path"] + " and " + context[1]["path"],
                       "coverage": coverage, "full_source_accounting": line_ledger,
                       "reconciliation": "Same-context source inventory/FRC accounting: nine material entries mapped to nine stable obligations; no omissions or invented assumptions detected by this agent.",
                       "independent_review": "NOT_PERFORMED; no false reviewer identity, approval, owner seal or qualified completeness claim",
                       "scope": "Simplified R5.96 research uses this source-anchored candidate for negative structural analysis; not a sealed production WHAT or an implementation authorization."})

projection = contracts.structural(contract, contract_id)
projection_path = save("STRUCTURAL", projection)
try:
    contracts.coverage(contract, projection)
except Failure as failure:
    terminal = failure.as_dict()
else:
    raise RuntimeError("Expected no result; stop rather than improvise a downstream workflow")

# The first native terminal failure is durably recorded before reporting/analysis.
stage_evidence = save("STAGES", {
    "formalization": "Source-anchored FRC candidate validated; independent approval not asserted",
    "structural_projection": "Completed; every obligation reported UNSUPPORTED by existing adapter",
    "structural_coverage": terminal,
    "bdi": "NOT_RUN: structural coverage failed",
    "adequacy": "NOT_RUN: structural coverage failed; neither adequate nor underspecified established",
    "representation": "NOT_RUN: earlier structural halt; complete V1 representability undetermined by this evaluation",
    "authoring": "NOT_RUN", "compilation": "NOT_RUN", "runtime": "NOT_RUN", "behavioral_verification": "NOT_RUN"})
machinery_paths = ["src", "schema", "air", "generated", "rehearsal", "benchmark/evaluation",
                   "benchmark/requirements", "benchmark/harness", "benchmark/conventional"]
drift = subprocess.check_output(["git", "diff", "HEAD", "--", *machinery_paths], cwd=ROOT, text=True)
assert not drift, "Machinery/source drift invalidates evaluation"
evidence_paths = [OUT / (PREFIX + "PRE-B03-SNAPSHOT.md"), OUT / (PREFIX + "B03-ACCESS.json"),
                  OUT / (PREFIX + "CONTEXT.json"), inventory_path, contract_path,
                  OUT / (PREFIX + "FORMALIZATION.json"), projection_path, stage_evidence,
                  Path(__file__).resolve(), OUT / (PREFIX + "access.py")]
result = {"record": "B03_FIRST_RESULT", "round": "R5.97",
          "recorded_utc": datetime.now(timezone.utc).isoformat(),
          "round_classification": "R5_97_B03_HELD_OUT_EVALUATION_COMPLETE",
          "B03_FIRST_RESULT": "DECISION_DISCOVERY_UNSUPPORTED",
          "native_result": terminal, "stage": "STRUCTURAL_PROJECTION_COVERAGE",
          "classification_basis": "Existing R5.83 taxonomy: materially unsupported structural annotation/discovery scope; retain exact native STRUCTURAL_COVERAGE_FAILURE. This is not V1 or Lykoi semantic impossibility.",
          "git_commit": "8c4240ae85336bc8700b788e44cc7f5b88f3c2d7",
          "snapshot_sha256": access["snapshot_sha256"], "source_sha256": access["source_sha256"],
          "first_access_utc": access["first_access_started_utc"], "exposure_state": "EXPOSED_TO_FORMALIZATION_AND_STRUCTURAL_ANALYSIS",
          "frc_commitment": contract_id, "affected_obligations": projection["unsupported"],
          "model": access["model"], "provider": access["provider"],
          "formalization_limitations": "Same-context candidate and inventory, not independent source review or owner-approved sealed WHAT; negative pure-function research analysis only.",
          "machinery_changed_after_access_before_result": False, "machinery_diff": drift,
          "evidence": [{"path": p.relative_to(ROOT).as_posix(), "sha256": sha(p)} for p in evidence_paths],
          "downstream": {k: "NOT_RUN" for k in ("BDI", "adequacy", "representation", "authoring", "compilation", "runtime", "behavioral_verification")},
          "stop": "First terminal result preserved. No repair, downstream diagnostic call, improved attempt, rerun or B04 access is authorized in R5.97."}
result_path = save("B03_FIRST_RESULT", result)
with (OUT / (PREFIX + "B03_FIRST_RESULT.sha256")).open("x", encoding="ascii", newline="\n") as stream:
    stream.write(sha(result_path) + "  " + result_path.name + "\n")
print(json.dumps(result, indent=2, ensure_ascii=False))
