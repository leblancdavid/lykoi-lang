"""Frozen R5.102 exposed transfer. No implementation edits or failure-driven repair.

R5.101 captures are preserved. B04 receives a newly captured typed interpretation
at the formalizer boundary; all deterministic middle stages are ordinary product
APIs. This is local development evidence, never cumulative or held-out success.
"""
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile

from lykoi_pipeline import Pipeline, PipelineController
from lykoi_pipeline.controller import component_paths
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.scalar_corpus import producer, obligations
from lykoi_pipeline.scalar_profile import PROFILE

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("r5_101_preserved", OUT / "R5_101-evaluate.py")
previous = importlib.util.module_from_spec(spec); spec.loader.exec_module(previous)


def pins():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in component_paths()}


def capture_scalar_addition(source, common):
    """Active-agent source capture using baseline context; not a downstream adapter."""
    model = previous.MODEL
    # Full baseline scalar WHAT facts plus source-authorized field introduction.
    return {"id": "source-label", "source": source, "domains": {"scalar_base_model": model, "common_requirement_context": common}, "facts": {
        "storage": {"path": "tasks.json", "version": 4, "missing": "empty_collection", "write": "atomic", "rejection": "unchanged"},
        "fields": [{"name": n, "type": t, "domain": domain, "nullable": nullable, "preservation": "verbatim"} for n, t, domain, nullable in (
            ("id", "identifier", [], False), ("title", "string", [], False), ("description", "string", [], False),
            ("status", "enum", ["pending", "completed"], False), ("priority", "enum", ["LOW", "NORMAL", "HIGH"], False),
            ("created_at", "timestamp", [], False), ("due_date", "timestamp", [], True), ("source", "string", [], False))],
        "creation": {"command": "create", "bindings": [
            {"field": "id", "source": "uuid_v4", "value": None, "default": None},
            {"field": "title", "source": "input", "value": None, "default": None},
            {"field": "description", "source": "input", "value": None, "default": None},
            {"field": "status", "source": "literal", "value": "pending", "default": None},
            {"field": "priority", "source": "input", "value": None, "default": {"value": "NORMAL", "trigger": "omitted", "boundary": "creation"}},
            {"field": "created_at", "source": "utc_clock", "value": None, "default": None},
            {"field": "due_date", "source": "input", "value": None, "default": {"value": None, "trigger": "omitted", "boundary": "creation"}},
            {"field": "source", "source": "input", "value": None, "default": {"value": "", "trigger": "omitted", "boundary": "creation"}}],
            "validation": [{"field": "title", "rule": "nonblank", "error": "invalid_title"}, {"field": "due_date", "rule": "timestamp_utc", "error": "invalid_due_date"}]},
        "listing": {"command": "list", "order": ["created_at", "id"], "result": "whole_records"},
        "lifecycle": [{"field": "status", "initial": "pending", "source": "pending", "target": "completed", "command": "complete", "missing_error": "task_not_found", "transition_error": "invalid_transition", "rejection": "unchanged"}],
        "evolution": [{"from": 1, "to": 2, "defaults": {"priority": "NORMAL"}, "boundary": "explicit_migration", "preservation": "unrelated_fields"},
                      {"from": 2, "to": 3, "defaults": {"due_date": None}, "boundary": "explicit_migration", "preservation": "unrelated_fields"},
                      {"from": 3, "to": 4, "defaults": {"source": ""}, "boundary": "explicit_migration", "preservation": "unrelated_fields"}]}}


def literal_plan(record):
    from lykoi_pipeline import plans
    from lykoi_pipeline.controller import digest
    ids = [o["id"] for o in obligations(record)]
    def task(identity, priority="NORMAL", status="pending", source="  exact source  "):
        return {"id": identity, "title": identity, "description": "untouched", "priority": priority, "status": status, "source": source, "created_at": "2026-01-01T00:00:00Z", "due_date": None}
    a, b = task("a"), task("b", "HIGH")
    def step(argv, expected=None, error=None, preserve=False, contains=None):
        s = {"argv": argv, "returncode": 1 if error else 0, "contains": contains or [], "preserved": ["tasks.json"] if preserve else [], "stdout_exact" if error else "stderr_exact": ""}
        if expected is not None or error: s["stderr_json" if error else "stdout_json"] = {"error": error} if error else expected
        return s
    def case(cid, fixture, steps):
        c = {"id": cid, "obligations": ids, "initial_state": "fresh_directory", "initial_files": fixture, "steps": steps, "invariants": ["All unrelated fields/source preserved"], "transitions": "Baseline completion and removal", "rejections": "Baseline declared errors"}
        c["identity"] = digest(c); return c
    fixture = [{"path": "tasks.json", "json": {"schema_version": 4, "records": [b, a]}}]
    complete = {**a, "status": "completed"}
    old = {k: v for k, v in a.items() if k != "source"}
    migrated = {**old, "source": ""}
    cases = [case("create-verbatim-and-default", [], [
        step(["create", "--title", "supplied", "--description", "kept", "--source", "  exact source  "], contains=["  exact source  "]),
        step(["create", "--title", "omitted", "--description", "kept"], contains=['"source": ""']),
        step(["list"], preserve=True, contains=["supplied", "omitted", "  exact source  "]),
        step(["create", "--title", "  ", "--description", "bad", "--source", "x"], error="invalid_title", preserve=True)]),
        case("all-reads-and-mutations", fixture, [step(["list"], [a, b], preserve=True), step(["list-high"], [b], preserve=True), step(["list-overdue"], [], preserve=True),
            step(["complete", "--id", "a"], complete), step(["complete", "--id", "a"], error="invalid_transition", preserve=True), step(["delete", "--id", "a"], complete), step(["list"], [b], preserve=True)]),
        case("field-migration", [{"path": "tasks.json", "json": {"schema_version": 3, "records": [old]}}], [
            step(["list"], error="migration_required", preserve=True), step(["migrate"], {"migrated": 1}), step(["list"], [migrated], preserve=True), step(["migrate"], {"migrated": 0}, preserve=True)]),
        case("missing-store", [], [step(["list"], [], preserve=True), step(["migrate"], {"migrated": 0}, preserve=True)])]
    return {"version": plans.VERSION, "outcome": "READY", "producer": "R5.102-source-side-literal-transfer-plan", "source_sha256": hashlib.sha256(record["source"].encode()).hexdigest(), "cases": cases,
            "coverage": [{"obligation": oid, "classification": "EXERCISED", "justification": "Verbatim/default/migrate/read/complete/delete/rejection observations", "cases": [c["identity"] for c in cases]} for oid in ids],
            "limitations": ["Local baseline context, not cumulative B01-B03 achievement; same-agent finite oracle"]}


def evaluate_scalar(source, common):
    record = capture_scalar_addition(source, common)
    plan = literal_plan(record)
    with tempfile.TemporaryDirectory(prefix="r5-102-transfer-") as tmp:
        c = PipelineController(Path(tmp) / "transfer.sqlite", PRINCIPALS, verification_fixtures={plan["source_sha256"]: plan})
        try:
            w = Workspace(c, "public", "source-label-transfer", CREDENTIALS); w.ingest(CREDENTIALS["owner"], source)
            fid = w.formalize(producer(record, "formalizer")); soi = w.commit_inventory(producer(record, "reviewer")); rid = w.reconcile(soi)
            rec = c.artifact(rid)["content"]
            stages = {s: "NOT_REACHED" for s in previous.STAGES}
            r = {"case": "B04", "capture": record, "formalization": c.artifact(fid)["content"], "source_inventory": c.artifact(soi)["content"], "reconciliation": rec, "external_plan": plan, "stages": stages}
            if rec["outcome"] != "ACCEPTABLE":
                stages["FORMALIZATION"] = "BLOCKED"; r.update(first_blocker="FORMALIZATION", native=rec["outcome"], current_result=rec["outcome"]); return r
            stages["FORMALIZATION"] = "PASS_ANALYTICAL_CAPTURE"; w.approve(CREDENTIALS["owner"], fid); seal = w.seal(fid)
            p = Pipeline(c, "public", CREDENTIALS); prepared = p.prepare(seal, "r5-102-scalar-transfer", review_rationale="Generic scalar profile applied to source-authorized existing-model addition; no transfer repairs")
            terminal = p.execute(prepared); audit = p.audit(terminal); r["audit"] = audit
            outcome = terminal["outcome"]
            r.update(native=outcome, current_result=outcome)
            if outcome == "BEHAVIORALLY_VERIFIED":
                for stage in previous.STAGES[1:]: stages[stage] = "PASS"
                r.update(first_blocker="SUCCESS", external_invocations=sum(len(x["steps"]) for x in plan["cases"]))
            else:
                blocker = {"STRUCTURAL_COVERAGE_FAILURE": "STRUCTURAL", "UNSUPPORTED_BDI_SCOPE": "BDI", "UNREPRESENTABLE_SOURCE": "REPRESENTATION", "AUTHORING_FAILURE": "AUTHORING", "COMPILATION_FAILURE": "COMPILATION", "BEHAVIORAL_VERIFICATION_FAILURE": "BEHAVIORAL_VERIFICATION"}.get(outcome, "ADEQUACY")
                for stage in previous.STAGES[1:]:
                    stages[stage] = "BLOCKED" if stage == blocker else "PASS"
                    if stage == blocker: break
                r["first_blocker"] = blocker
            return r
        finally:
            c.close()


def main():
    verification = json.loads((OUT / "R5_102-VERIFICATION.json").read_text(encoding="utf-8"))
    assert verification["all_pass"], "No transfer before passing generic verification"
    before = pins()
    baseline_files = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob("R5_101-*") if p.is_file()}
    assert baseline_files == verification["r5_101_baseline_files"]
    freeze = {"utc": datetime.datetime.now(datetime.timezone.utc).isoformat(), "classification": "GENERIC_IMPLEMENTATION_FIXED_FOR_EXPOSED_TRANSFER", "implementation": before,
              "r5_101_baseline": baseline_files, "verification_sha256": hashlib.sha256((OUT / "R5_102-VERIFICATION.json").read_bytes()).hexdigest()}
    with (OUT / "R5_102-PRE-TRANSFER.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(freeze, stream, indent=2); stream.write("\n")
    prior = {r["case"]: r for r in json.loads((OUT / "R5_101-CURRENT-EVIDENCE.json").read_text(encoding="utf-8"))["cases"]}
    common = {p: (ROOT / p).read_text(encoding="utf-8") for p in ("benchmark/baseline.md", "benchmark/requirements/README.md")}
    rows = []
    for case in previous.INVENTORY:
        assert pins() == before, "Implementation drift before transfer"
        current = evaluate_scalar((ROOT / "benchmark/requirements/B04.md").read_text(encoding="utf-8"), common) if case == "B04" else previous.evaluate(case, common)
        current["previous_first_blocker"] = prior[case]["first_blocker"]
        current["newly_reached"] = [s for s in previous.STAGES if prior[case]["stages"][s] == "NOT_REACHED" and current["stages"][s] != "NOT_REACHED"]
        rows.append(current); print(case, current["previous_first_blocker"], "->", current["first_blocker"], current["native"], flush=True)
    assert pins() == before, "No failure-driven transfer repair allowed"
    assert baseline_files == {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in OUT.glob("R5_101-*") if p.is_file()}
    distribution = {k: sum(r["first_blocker"] == k for r in rows) for k in sorted({r["first_blocker"] for r in rows})}
    result = {"utc_finished": datetime.datetime.now(datetime.timezone.utc).isoformat(), "scope": "Frozen exposed requirement-local regression transfer, not cumulative or held-out", "implementation_unchanged": True,
              "capture_policy": "R5.101 captures replayed for nineteen cases; B04 freshly interpreted at formalizer input into the tested generic existing-scalar profile; no manually injected middle artifacts",
              "limitations": ["Same-agent source inventory/oracle and synthetic owner approval", "Unchanged prose captures are capture-compatibility evidence, not proof that current typed re-formalization would fail"], "distribution": distribution, "cases": rows}
    with (OUT / "R5_102-TRANSFER-EVIDENCE.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2); stream.write("\n")
    markdown = ["# R5.102 — frozen exposed B01–B20 transfer", "", "Requirement-local development/regression evidence; **not held-out generalization or cumulative achievement**.", "", "| Case | R5.101 first blocker | R5.102 first blocker | Native result | Newly reached stages |", "| --- | --- | --- | --- | --- |"]
    markdown += ["| " + " | ".join((r["case"], r["previous_first_blocker"], r["first_blocker"], "`" + r["native"] + "`", ", ".join(r["newly_reached"]) or "None")) + " |" for r in rows]
    markdown += ["", "First-blocker distribution: `" + json.dumps(distribution, sort_keys=True) + "`.", "", "B04 uses new typed formalizer output; nineteen rows retain R5.101 captures. Prose-shaped legacy facts are not reparsed downstream. This comparison consequently measures both legacy-capture compatibility and one fresh typed transfer; unchanged halts are not exhaustive current typed-formalization results.", "", "Implementation pins matched before each case and after the whole transfer. B17/B20 questions remain unanswered. R5.101 files match the pre-transfer baseline."]
    with (OUT / "R5_102-CAPABILITY-MATRIX.md").open("x", encoding="utf-8", newline="\n") as stream:
        stream.write("\n".join(markdown) + "\n")


if __name__ == "__main__":
    main()
