"""Source-bound diagnostic captures through unchanged Workspace/Pipeline APIs.

No benchmark dispatcher, mapping, semantic or backend extension is installed.
The captures are same-agent analytical evidence, not independent formalization.
Run once; all published evidence is new and historical files remain untouched.
"""
import copy
import datetime
import hashlib
import json
from pathlib import Path
import tempfile

from lykoi_controller import canonical
from lykoi_pipeline import Pipeline, PipelineController
from lykoi_pipeline import plans
from lykoi_pipeline.controller import digest
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.producers import ModelAdapter
from lykoi_workspace.query_corpus import response as query_response

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
MODEL = json.loads((ROOT / "air/task_manager.json").read_text(encoding="utf-8"))
STAGES = ("FORMALIZATION", "STRUCTURAL", "BDI", "ADEQUACY", "REPRESENTATION",
          "AUTHORING", "COMPILATION", "RUNTIME", "BEHAVIORAL_VERIFICATION")

# Compact obligation inventory: input, transformation/selection, order, validation,
# state/result/persistence, and other observations remain separately inspectable.
# Missing precursor features are demands, never constructed by an evaluation adapter.
INVENTORY = {
 "B01": ("enum evolution", {
  "operations": "create, list, list-high, migrate",
  "input": "Accept CRITICAL as well as LOW/NORMAL/HIGH; omitted priority remains NORMAL",
  "selection": "list-high matches exactly HIGH, not CRITICAL; list includes CRITICAL",
  "ordering": "CRITICAL ranks above HIGH; lists retain created_at/id ascending",
  "validation": "Retain accepted-priority and existing state validation",
  "state": "Creation persists selected priority; migration preserves old LOW/NORMAL/HIGH",
  "result": "Return CRITICAL unchanged on create/list; preserve other task fields",
  "persistence": "Explicit atomic/idempotent migration; compatible old tasks"}),
 "B02": ("ordered normalized values", {
  "operations": "create, migrate; all task-returning operations",
  "input": "Zero or more repeated --tag VALUE flags; omission gives []",
  "selection": "Trim each value; exact case-sensitive deduplication retaining first occurrence",
  "ordering": "First occurrence in input determines tags order",
  "validation": "Nonblank after trimming; any bad tag fails invalid_tag with no task",
  "state": "Persist tags array on tasks; old tasks migrate to []",
  "result": "Every task result contains tags array",
  "persistence": "Explicit atomic/idempotent migration; errors preserve bytes"}),
 "B03": ("runtime membership query", {
  "operations": "list-tag --tag VALUE",
  "input": "Runtime string; do not trim query value",
  "selection": "Exact case-sensitive tags membership; include completed tasks",
  "ordering": "created_at ascending, then id ascending",
  "validation": "Blank/whitespace-only input -> invalid_tag",
  "state": "Read-only, including no matches and rejection",
  "result": "Whole matching tasks once each; no matches []",
  "persistence": "Storage bytes and file absence unchanged"}),
 "B04": ("verbatim optional field", {
  "operations": "create --source VALUE, migrate; list and later mutations",
  "input": "Optional string, omitted -> empty string",
  "selection": "Identity transformation; preserve supplied whitespace verbatim",
  "ordering": "Existing normal list ordering",
  "validation": "No additional source validation; retain ordinary create validation",
  "state": "Persist source; later mutations preserve it; migrate missing source to empty string",
  "result": "Every task contains source string",
  "persistence": "Explicit atomic/idempotent field migration"}),
 "B05": ("runtime equality query", {
  "operations": "list-status --status pending|completed",
  "input": "Runtime status in declared pending/completed domain",
  "selection": "Return every exact matching task, including completed for completed query",
  "ordering": "created_at ascending, then id ascending",
  "validation": "No new error code/behavior for out-of-domain status is specified",
  "state": "Read-only; retain existing commands",
  "result": "Whole matching records; empty result []",
  "persistence": "Unchanged storage bytes/file absence"}),
 "B06": ("normalized field and equality query", {
  "operations": "create --category VALUE, list-category --category VALUE, migrate",
  "input": "Omitted/explicitly empty -> empty string; otherwise trim supplied create value",
  "selection": "Exact case-sensitive category query including empty uncategorized value; list retains all",
  "ordering": "Normal created_at/id list ordering",
  "validation": "Whitespace-only nonempty create input -> invalid_category",
  "state": "Persist category; migrated tasks get empty string",
  "result": "Category returned on every task; query returns complete records",
  "persistence": "Explicit atomic migration; failed writes preserve state"}),
 "B07": ("append mutation", {
  "operations": "append-note --id ID --text TEXT; create and migrate defaults",
  "input": "Trim text; notes initially []",
  "selection": "Lookup task by ID; append one normalized string",
  "ordering": "Repeated appends retain insertion order",
  "validation": "Blank text -> invalid_note; missing task -> task_not_found",
  "state": "Update notes only; failed append leaves task unchanged",
  "result": "Return updated task with ordered notes array",
  "persistence": "Persist append; old records migrate to []"}),
 "B08": ("orthogonal lifecycle and query inclusion", {
  "operations": "archive --id ID, list-archived; modify six existing list commands",
  "input": "archived boolean defaults false on create/migrate",
  "selection": "Hide archived from list/high/overdue/tag/status/category; list-archived selects archived",
  "ordering": "Normal ordering on every list",
  "validation": "Repeat archive -> invalid_transition; missing task -> task_not_found",
  "state": "Set archived true independently of pending/completed status; status unchanged",
  "result": "Return archived task; retain other fields",
  "persistence": "Persist boolean and migrate default false; failures unchanged"}),
 "B09": ("nullable temporal range query", {
  "operations": "list-due --start UTC_TIMESTAMP --end UTC_TIMESTAMP",
  "input": "Two UTC timestamp parameters; equal endpoints valid",
  "selection": "nonarchived AND pending AND nonnull due_date in inclusive [start,end]",
  "ordering": "Normal created_at/id ordering",
  "validation": "start>end -> invalid_window; invalid/non-UTC time -> invalid_due_date",
  "state": "Read-only, exclude completed and undated tasks",
  "result": "Whole qualifying tasks; no matches []",
  "persistence": "No write on success or error"}),
 "B10": ("optional identity field and equality query", {
  "operations": "create --owner USER_ID, list-owner --owner USER_ID, migrate",
  "input": "Omitted create owner -> empty string; supplied owner trimmed and nonblank",
  "selection": "Exact case-sensitive query, including empty string for unowned",
  "ordering": "Normal ordering",
  "validation": "Blank supplied create owner -> invalid_owner; no user existence rule yet",
  "state": "Persist owner; migrate to empty string",
  "result": "Every task returns owner string",
  "persistence": "Explicit atomic migration and no state change on rejection"}),
 "B11": ("conditional deletion guard", {
  "operations": "delete --id ID",
  "input": "Existing task identity",
  "selection": "Delete pending regardless of archival, or completed only if archived",
  "ordering": "No new ordering",
  "validation": "completed AND not archived -> delete_requires_archive",
  "state": "Remove on success; preserve storage on failure",
  "result": "Return removed whole task",
  "persistence": "Atomic delete, preserving prior archive behavior"}),
 "B12": ("clock-relative compound query", {
  "operations": "list-urgent; preserve list-overdue",
  "input": "Current UTC clock capability (no runtime query parameter)",
  "selection": "nonarchived AND pending AND due_date nonnull AND due_date<now AND priority in {HIGH,CRITICAL}",
  "ordering": "Normal created_at/id ordering",
  "validation": "Retain stored-state validation; no new input error",
  "state": "Read-only; overdue remains every priority",
  "result": "Whole qualifying tasks; exclude completed/archived/undated/LOW/NORMAL",
  "persistence": "No write effect"}),
 "B13": ("cross-operation terminal guard", {
  "operations": "complete and append-note, retain delete and list-archived",
  "input": "Task identity plus existing mutation inputs",
  "selection": "Archived is terminal for complete/append; no unarchive/reopen",
  "ordering": "No new order; list-archived remains normal",
  "validation": "Archived mutation -> invalid_transition; retain B11 deletion rule",
  "state": "Rejected mutation changes nothing",
  "result": "Archived tasks remain observable until valid deletion",
  "persistence": "Rejection preserves stored bytes"}),
 "B14": ("identity graph invariants", {
  "operations": "add-dependency --id ID --depends-on OTHER_ID, delete, migrate",
  "input": "Ordered dependencies array initially []; two task identities",
  "selection": "Append existing task ID; archived targets valid; reject referenced deletion",
  "ordering": "Dependency insertion order retained",
  "validation": "Self/duplicate/cycle -> invalid_dependency; unknown target -> task_not_found; referenced deletion -> dependency_in_use",
  "state": "Only subject dependencies updated; failed change preserves both tasks",
  "result": "Return updated whole task",
  "persistence": "Persist graph edges, migrate [] atomically; no dangling deletions"}),
 "B15": ("quantified relationship guard", {
  "operations": "complete --id ID",
  "input": "Existing dependency identities",
  "selection": "All referenced tasks completed; archived completed counts; empty dependency set vacuously permits",
  "ordering": "No new ordering",
  "validation": "Any pending dependency -> incomplete_dependencies; retain B13/prior transition rules",
  "state": "Transition only on valid guard; dependencies unchanged",
  "result": "Ordinary completed task result",
  "persistence": "Rejected completion preserves data"}),
 "B16": ("multi-entity referential integrity", {
  "operations": "create-user, list-users, create --owner USER_ID, migrate; retain list-owner",
  "input": "Nonblank case-sensitive user IDs; required existing owner",
  "selection": "Built-in system user always exists; migrate empty owner to system",
  "ordering": "Users by ID ascending; owner-filtered tasks normal order",
  "validation": "Duplicate/blank user -> user_exists/invalid_user; missing/unknown owner -> invalid_owner; migration unknown nonempty owner -> invalid_owner",
  "state": "Persist users and task ownership; create-user then retry failed migration may resolve it",
  "result": "User objects exactly {id: USER_ID}; task owner remains visible",
  "persistence": "Cross-entity migration failure leaves data unchanged; user identity unique"}),
 "B17": ("data-dependent authorization", {
  "operations": "create-user --role ADMIN|USER; all mutating task commands --actor USER_ID",
  "input": "Role defaults USER for create-user; system ADMIN; actor required/existing",
  "selection": "USER creates own tasks/mutates owned tasks; ADMIN any owner; reads unrestricted",
  "ordering": "Existing ordering unchanged; authorization precedes mutation",
  "validation": "Unknown/missing/forbidden actor -> unknown_actor/actor_required/permission_denied",
  "state": "Reject unauthorized changes without state effects",
  "result": "User results now include role, including system",
  "persistence": "Role field needs explicit migration; old ordinary-user role not specified"}),
 "B18": ("atomic ordered event effects", {
  "operations": "Audit create/complete/delete/archive/append-note/add-dependency; list-audit",
  "input": "Actor, task identity, operation and current UTC time",
  "selection": "Exactly one audit entry per successful task mutation; none for rejection or user creation",
  "ordering": "Monotonic sequence numbers; list-audit sequence order",
  "validation": "Mutation and audit entry succeed or fail together",
  "state": "Append durable audit entries carrying sequence/time/actor/operation/task",
  "result": "Return complete audit entry list",
  "persistence": "Migration starts empty history; atomic multi-state commit"}),
 "B19": ("conditional atomic successor creation", {
  "operations": "create --recurrence-days N; complete recurring task; migrate",
  "input": "Positive integer N requires due date; omitted/migrated recurrence null",
  "selection": "On successful completion create exactly one successor; due date original+N UTC calendar days",
  "ordering": "Audit complete before create, both actor-attributed",
  "validation": "Invalid interval/missing due -> invalid_recurrence; no successor on failed completion",
  "state": "Fresh successor ID/time, pending, copy title/description/priority/tags/source/category/owner/notes/project and N; empty dependencies",
  "result": "Preserve ordinary completion response; successor observable in tasks",
  "persistence": "Completion, successor and two audit entries atomic; null migration default"}),
 "B20": ("relationships and composed permission predicates", {
  "operations": "create-project, add-project-member, list-projects, create --project, list-project; task mutations",
  "input": "Unique nonblank case-sensitive project ID; existing owner/member users; actor; optional task project empty means none",
  "selection": "Project task mutation USER=(task owner AND member) OR project owner; ADMIN any; creation ADMIN/owner/member AND B17 ownership",
  "ordering": "Projects and set-valued members by ID; nonarchived project tasks normal order",
  "validation": "Duplicate -> project_exists; bad owner -> invalid_owner; unknown project -> project_not_found; forbidden -> permission_denied; unknown member error unspecified",
  "state": "Owner always member; add-member idempotent; migrated tasks unassigned",
  "result": "Projects {id,owner,members}; updated project on membership addition; whole query tasks",
  "persistence": "Persist projects/membership/task assignment; failed permission checks unchanged"}),
}

QUESTIONS = {
 "B17": "Which role must migration assign to an existing non-system B16 user? The USER creation default does not specify a migration default.",
 "B20": "What application error should add-project-member return for a nonexistent user? The common missing-ID task_not_found rule is task-specific, and B20 only specifies unknown projects and invalid owners.",
}

def query_record(case, source):
    field, param, kind, operator = {
        "B03": ("tags", "tag", "strings", "contains"),
        "B05": ("status", "status", "string", "equals"),
        "B06": ("category", "category", "string", "equals"),
        "B10": ("owner", "owner", "string", "equals"),
    }[case]
    fields = {"id": "string", "created_at": "string", field: kind}
    if field != "status":
        fields["status"] = "string"
    return {"id": case, "source": source, "operation": "list-" + param,
            "domains": {"collection_store": {"kind": "model_state", "model": MODEL, "state": "state_tasks"}},
            "facts": {
                "source": {"collection": "state_tasks", "fields": fields, "unique_key": "id"},
                "parameters": {param: "string"},
                "predicate": {"field": field, "operator": operator, "operand": {"parameter": param}},
                "comparison": {"case": "sensitive", "normalization": "none"},
                "ordering": [{"field": "created_at", "direction": "ASC"}, {"field": "id", "direction": "ASC"}],
                "validation": [{"parameter": "tag", "rule": "nonblank", "error": "invalid_tag"}] if case == "B03" else [],
                "inclusion": [] if field == "status" else [{"field": "status", "mode": "all"}],
                "effect": {"state": "read_only", "persistence": "unchanged"},
                "result": {"shape": "collection", "cardinality": "zero_or_more", "no_match": "empty"}}}

def rows(case, source):
    inventory = INVENTORY[case][1]
    typed = case in ("B03", "B05", "B06", "B10")
    result = query_response(query_record(case, source), {"text": source}, []) ["obligations"] if typed else []
    # Pure queries are entirely represented by their nine facets. Mixed requests
    # additionally retain creation, normalization, migration and result obligations.
    if case in ("B03", "B05"):
        return result
    kinds = {"B01": "priority_extension", "B09": "filter_order", "B11": "invariant",
             "B12": "filter_order", "B13": "invariant", "B14": "invariant",
             "B15": "invariant", "B17": "invariant", "B18": "effects", "B19": "transition", "B20": "invariant"}
    for facet, meaning in inventory.items():
        result.append({"id": case + "/" + facet, "basis": "STATED", "source_quote": source,
                       "derived_from": [], "statement": meaning,
                       "relation": {"kind": kinds.get(case, "crud"),
                                    "parameters": {"obligation_facet": facet, "meaning": meaning}}})
    return result

def producer(case, source, role, common):
    captured = rows(case, source)
    question = QUESTIONS.get(case)
    domains = {"evaluation_scope": "requirement-local against current model, not cumulative achieved history",
               "common_requirement_context": common,
               "precursor_requirements": [f"B{i:02d}" for i in range(1, int(case[1:]))]}
    if case in ("B03", "B05", "B06", "B10"):
        domains.update({"capability_profile": "collection-query-1", **query_record(case, source)["domains"]})
    def invoke(request):
        assert request["source"]["text"] == source
        references = [e["identity"] for e in request["evidence"] if e["provenance"] == "human_statement"]
        authority = {o["id"]: references for o in captured}
        if role == "formalizer":
            return {"obligations": copy.deepcopy(captured), "authority": authority, "domains": domains,
                    "questions": [{"id": case + ".QUESTION", "text": question, "priority": "BLOCKING", "affects": [captured[0]["id"]]}] if question else [],
                    "issues": [{"id": case + ".AMBIGUITY", "category": "AMBIGUITY", "description": question,
                                "affects": [captured[0]["id"]], "alternatives": [], "witness": None, "resolved": False}] if question else [],
                    "lineage": [], "policy_applications": []}
        source_record = {"id": request["source"]["identity"], "text": source, "classification": "SYNTHETIC",
                         "sha256": hashlib.sha256(source.encode()).hexdigest()}
        inventory = {"version": "SourceObligationInventory-0.1",
                     "source_commitment": hashlib.sha256(canonical({"revision": request["source"]["revision"], "record": source_record})).hexdigest(),
                     "extractor": "R5.101-active-agent-source-inventory", "context_class": "SAME_AGENT_ANALYTICAL_CAPTURE",
                     "items": [{"id": o["id"], "spans": [{"start": 0, "end": len(source), "quote": source}],
                                "meaning": o["statement"], "category": "BEHAVIOR", "material": True, "dependencies": []} for o in captured],
                     "questions": [question] if question else [],
                     "limitations": ["Same-context analytical inventory; umbrella source spans; no independent cognition or owner review claimed"]}
        return {"inventory": inventory, "interpretations": {o["id"]: {k: o[k] for k in ("statement", "relation")} for o in captured},
                "authority": authority, "domains": domains}
    return ModelAdapter(role, case + ":" + role, invoke, provider="OpenAI", model="openai/gpt-6.1-sol/recorded-active-agent-capture")

def b05_plan(source):
    ids = ["list-status/" + f for f in query_record("B05", source)["facts"]]
    def task(identity, status, date, due=None):
        return {"id": identity, "title": identity, "description": "kept verbatim", "status": status,
                "priority": "NORMAL", "created_at": date, "due_date": due}
    records = [task("z", "pending", "2026-01-02T00:00:00Z"),
               task("b", "pending", "2026-01-01T00:00:00Z"),
               task("a", "pending", "2026-01-01T00:00:00Z"),
               task("c", "completed", "2026-01-01T00:00:00Z", "2025-01-01T00:00:00Z")]
    def step(argv, expected, error=False):
        return {"argv": argv, "returncode": 1 if error else 0, "contains": [], "preserved": ["tasks.json"],
                "stderr_json" if error else "stdout_json": expected,
                "stdout_exact" if error else "stderr_exact": ""}
    def case(name, payload, steps):
        c = {"id": name, "obligations": ids, "initial_state": "fresh_directory",
             "initial_files": [] if payload is None else [{"path": "tasks.json", "json": payload}],
             "steps": steps, "invariants": ["Read-only bytes/absence", "Full task results"],
             "transitions": "None", "rejections": "Existing store validation"}
        c["identity"] = digest(c)
        return c
    cases = [
        case("status-partition-and-tie", {"schema_version": 3, "records": records}, [
            step(["list-status", "--status", "pending"], [records[2], records[1], records[0]]),
            step(["list-status", "--status", "completed"], [records[3]]),
            step(["list"], [records[2], records[1], records[3], records[0]])]),
        case("missing-store", None, [step(["list-status", "--status", s], []) for s in ("pending", "completed")]),
        case("empty-store", {"schema_version": 3, "records": []}, [step(["list-status", "--status", s], []) for s in ("pending", "completed")]),
        case("no-completed", {"schema_version": 3, "records": [records[0]]}, [step(["list-status", "--status", "completed"], [])]),
        case("bad-state", {"schema_version": 3, "records": [{"id": "bad"}]}, [step(["list-status", "--status", "pending"], {"error": "invalid_state"}, True)]),
        case("legacy-store", [], [step(["list-status", "--status", "pending"], {"error": "migration_required"}, True)]),
    ]
    return {"version": plans.VERSION, "outcome": "READY", "producer": "same-agent-source-side-literal-external-plan",
            "source_sha256": hashlib.sha256(source.encode()).hexdigest(), "cases": cases,
            "coverage": [{"obligation": oid, "classification": "EXERCISED", "justification": "Exact status partition, ties, empty/missing/legacy/invalid store observations",
                          "cases": [c["identity"] for c in cases]} for oid in ids],
            "limitations": ["Finite same-agent oracle; status outside pending/completed source domain unscored; no cumulative B01-B04 coverage claim"]}

def evaluate(case, common):
    path = ROOT / "benchmark/requirements" / (case + ".md")
    source = path.read_text(encoding="utf-8")
    plan = b05_plan(source) if case == "B05" else None  # Before authorship.
    with tempfile.TemporaryDirectory(prefix="r5-101-") as tmp:
        c = PipelineController(Path(tmp) / "case.sqlite", PRINCIPALS,
                               verification_fixtures={plan["source_sha256"]: plan} if plan else {})
        try:
            w = Workspace(c, "public", case, CREDENTIALS)
            w.ingest(CREDENTIALS["owner"], source)
            fid = w.formalize(producer(case, source, "formalizer", common))
            soi = w.commit_inventory(producer(case, source, "reviewer", common))
            reconciliation = w.reconcile(soi)
            rec = c.artifact(reconciliation)["content"]
            statuses = {s: "NOT_REACHED" for s in STAGES}
            result = {"case": case, "family": INVENTORY[case][0], "obligation_inventory": INVENTORY[case][1],
                      "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "source_text_sha256": hashlib.sha256(source.encode()).hexdigest(),
                      "stages": statuses, "formalization": c.artifact(fid)["content"],
                      "source_inventory": c.artifact(soi)["content"], "reconciliation": rec,
                      "ambiguity": QUESTIONS.get(case), "external_plan": plan}
            if rec["outcome"] != "ACCEPTABLE":
                statuses["FORMALIZATION"] = "BLOCKED"
                result.update(first_blocker="FORMALIZATION", native="NEEDS_CLARIFICATION", furthest="FORMALIZATION",
                              gap_class="AMBIGUOUS_REQUIREMENT", current_result="NEEDS_CLARIFICATION")
                return result
            statuses["FORMALIZATION"] = "PASS_ANALYTICAL_CAPTURE"
            w.approve(CREDENTIALS["owner"], fid)
            seal = w.seal(fid)
            p = Pipeline(c, "public", CREDENTIALS)
            prepared = p.prepare(seal, "r5-101-" + case, review_rationale="R5.101 same-agent diagnostic review; synthetic owner credentials; no generalization claim")
            terminal = p.execute(prepared)
            audit = p.audit(terminal)
            result["audit"] = audit
            result["current_result"] = terminal["outcome"]
            outcome = terminal["outcome"]
            if outcome == "STRUCTURAL_COVERAGE_FAILURE":
                statuses["STRUCTURAL"] = "BLOCKED"
                result.update(first_blocker="STRUCTURAL", native=outcome, furthest="STRUCTURAL")
            elif outcome == "UNSUPPORTED_BDI_SCOPE":
                statuses["STRUCTURAL"] = "PASS_NATIVE_BOUNDED_PROJECTION"
                statuses["BDI"] = "BLOCKED"
                result.update(first_blocker="BDI", native=outcome, furthest="BDI")
            elif outcome == "BEHAVIORALLY_VERIFIED":
                for s in STAGES[1:]:
                    statuses[s] = "PASS"
                verification = audit["artifacts"][terminal["verification"]]["content"]
                result.update(first_blocker="SUCCESS", native=outcome, furthest="BEHAVIORAL_VERIFICATION",
                              external_invocations=sum(len(x["steps"]) for x in verification["cases"]))
            else:
                raise AssertionError(f"Unanticipated first result, preserve before diagnosis: {case} {terminal}")
            return result
        finally:
            c.close()

def main():
    common = {p: (ROOT / p).read_text(encoding="utf-8") for p in ("benchmark/baseline.md", "benchmark/requirements/README.md")}
    result = {"utc_started": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "scope": "Twenty requirement-local current capability attempts, not replay of frozen cumulative histories",
              "model": "openai/gpt-6.1-sol", "provider": "OpenAI",
              "limitations": ["Same-agent captures, source inventories, oracle and synthetic owner actions; no independent semantic approval", "Normal product code unchanged; no benchmark-specific adapter"],
              "cases": []}
    for case in INVENTORY:
        evidence = evaluate(case, common)
        result["cases"].append(evidence)
        print(case, evidence["first_blocker"], evidence["native"])
    result["utc_finished"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    with (OUT / "R5_101-CURRENT-EVIDENCE.json").open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")

if __name__ == "__main__":
    main()
