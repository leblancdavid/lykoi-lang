"""Normal source/Workspace/Pipeline integration; no post-formalizer typed injection."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import subprocess
import os
import sys
import unittest

from air_compiler.collection_query import QueryError
from air_compiler.profiles import generate
from lykoi_controller import Failure, canonical
from lykoi_pipeline import Pipeline, PipelineController, contracts, plans
from lykoi_pipeline.controller import ROOT, digest
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_pipeline.pipeline import external_execute
from lykoi_pipeline import query_profile
from lykoi_workspace import Workspace
from lykoi_workspace.query_corpus import captures, producer, PRODUCT_FACTS
from lykoi_workspace.query_schema import validate_output

PRODUCTS = [
    {"sku": "d", "category": "tools", "discontinued": True},
    {"sku": "b", "category": "tools", "discontinued": False},
    {"sku": "a", "category": "TOOLS", "discontinued": False},
    {"sku": "c", "category": " tools ", "discontinued": False},
    {"sku": "e", "category": "other", "discontinued": False},
]
DOCUMENTS = [
    {"id": "z", "labels": ["red", "red"], "created_at": 2, "archived": True},
    {"id": "a", "labels": ["red"], "created_at": 2, "archived": True},
    {"id": "b", "labels": ["blue"], "created_at": 3, "archived": False},
    {"id": "c", "labels": ["red"], "created_at": 1, "archived": False},
]


def task_capture():
    model = json.loads((ROOT / "air/task_manager.json").read_text(encoding="utf-8"))
    return {"id": "model-state", "operation": "find-tasks",
            "source": "Using the supplied task model and its state_tasks collection, return every task whose title exactly equals the runtime title string, case-sensitively preserving spaces. Include pending and completed tasks. Order by created_at ascending then id ascending. Reject empty or whitespace-only title with invalid_title. No matches means an empty collection. Preserve all task fields, state and storage bytes/file absence on success and error. Retain existing commands.",
            "domains": {"collection_store": {"kind": "model_state", "model": model, "state": "state_tasks"}},
            "facts": {
                "source": {"collection": "state_tasks", "fields": {"id": "string", "title": "string", "status": "string", "created_at": "string"}, "unique_key": "id"},
                "parameters": {"title": "string"},
                "predicate": {"field": "title", "operator": "equals", "operand": {"parameter": "title"}},
                "comparison": {"case": "sensitive", "normalization": "none"},
                "ordering": [{"field": "created_at", "direction": "ASC"}, {"field": "id", "direction": "ASC"}],
                "validation": [{"parameter": "title", "rule": "nonblank", "error": "invalid_title"}],
                "inclusion": [{"field": "status", "mode": "all"}],
                "effect": {"state": "read_only", "persistence": "unchanged"},
                "result": {"shape": "collection", "cardinality": "zero_or_more", "no_match": "empty"},
            }}


def independent_plan(record):
    """Literal WHAT-side expectations. Never use projection/runtime to predict output."""
    operation = record["operation"]
    ids = [operation + "/" + f for f in PRODUCT_FACTS]
    name = record["id"]
    store = "tasks.json" if name == "model-state" else "measurements.json"
    if name == "model-state":
        records = [
            {"id": "b", "title": "keep", "description": "second", "status": "completed", "priority": "HIGH", "created_at": "2026-01-01T00:00:00Z", "due_date": None},
            {"id": "a", "title": "keep", "description": "first", "status": "pending", "priority": "LOW", "created_at": "2026-01-01T00:00:00Z", "due_date": None},
            {"id": "c", "title": "other", "description": "excluded", "status": "pending", "priority": "NORMAL", "created_at": "2026-01-02T00:00:00Z", "due_date": None},
        ]
        payload, selected, parameter, value, error = {"schema_version": 3, "records": records}, [records[1], records[0]], "title", "keep", "invalid_title"
    elif name.startswith("documents"):
        selected = [DOCUMENTS[3]] if name == "documents-exclude" else [DOCUMENTS[1], DOCUMENTS[0], DOCUMENTS[3]]
        payload, parameter, value, error = DOCUMENTS, "label", "red", "invalid_label"
    elif name.startswith("users"):
        records = [{"id": 1, "department": "eng", "last_name": "A", "inactive": False},
                   {"id": 3, "department": "eng", "last_name": "A", "inactive": True},
                   {"id": 2, "department": "eng", "last_name": "B", "inactive": False},
                   {"id": 4, "department": "ENG", "last_name": "A", "inactive": False}]
        payload, selected, parameter, value, error = records, [records[1], records[0], records[2]], "department", "eng", "invalid_department"
    else:
        expected_indices = {"casefold": [2, 1, 0], "strip": [1, 3, 0], "descending": [0, 1], "exclude": [1]}
        payload, selected = PRODUCTS, [PRODUCTS[i] for i in expected_indices.get(name, [1, 0])]
        parameter, value, error = "category", "tools", "invalid_category"
    def step(value, result=None, rejection=None):
        argv = [operation, "--" + parameter, value]
        if name != "model-state":
            argv += ["--store", store]
        result_step = {"argv": argv, "returncode": 1 if rejection else 0, "contains": [], "preserved": [store]}
        result_step["stderr_json" if rejection else "stdout_json"] = {"error": rejection} if rejection else result
        result_step["stdout_exact" if rejection else "stderr_exact"] = ""
        return result_step
    def case(identity, fixture, steps):
        c = {"id": identity, "obligations": ids, "initial_state": "fresh_directory", "initial_files": fixture,
             "steps": steps, "invariants": ["Storage bytes/absence unchanged"], "transitions": "Read-only observations", "rejections": "Declared source errors"}
        c["identity"] = digest(c)
        return c
    no_match_error = "no_products" if name == "no-match-error" else None
    blanks = step("   ", [] if name == "nonempty" else None, None if name == "nonempty" else error)
    cases = [case("selection", [{"path": store, "json": payload}], [step(value, selected), step("missing", [], no_match_error), blanks, step("", rejection=error)]),
             case("missing-store", [], [step(value, [], no_match_error), step("", rejection=error)])]
    if name == "model-state":
        cases[0]["steps"].append({"argv": ["list"], "returncode": 0, "contains": ["first", "second", "excluded"], "preserved": [store]})
        cases[0]["identity"] = digest({k: v for k, v in cases[0].items() if k != "identity"})
        cases.append(case("invalid-full-state", [{"path": store, "json": {"schema_version": 3, "records": [{"id": "bad"}]}}],
                          [step(value, rejection="invalid_state"), step("   ", rejection=error)]))
    return {"version": plans.VERSION, "outcome": "READY", "producer": "same-agent-source-side-literal-oracle",
            "source_sha256": hashlib.sha256(record["source"].encode()).hexdigest(), "cases": cases,
            "coverage": [{"obligation": oid, "classification": "EXERCISED", "justification": "Source-derived composition plus near-neighbor witnesses",
                          "cases": [c["identity"] for c in cases]} for oid in ids],
            "limitations": ["Same-agent source/model/oracle; process independence only; finite coverage"]}


def normal_run(record, *, execute=True):
    plan = independent_plan(record)
    with tempfile.TemporaryDirectory() as tmp:
        c = PipelineController(Path(tmp) / "normal.sqlite", PRINCIPALS, verification_fixtures={plan["source_sha256"]: plan})
        try:
            w = Workspace(c, "public", record["id"], CREDENTIALS)
            w.ingest(CREDENTIALS["owner"], record["source"])
            fid = w.formalize(producer(record, "formalizer"))
            inventory = w.commit_inventory(producer(record, "reviewer"))
            reconciliation = w.reconcile(inventory)
            contract = c.artifact(fid)["content"]["contract"]
            if c.artifact(reconciliation)["content"]["outcome"] != "ACCEPTABLE":
                return {"outcome": "NEEDS_CLARIFICATION", "contract": contract, "coverage": c.artifact(reconciliation)["content"]}
            w.approve(CREDENTIALS["owner"], fid)
            seal = w.seal(fid)
            p = Pipeline(c, "public", CREDENTIALS)
            prepared = p.prepare(seal, "normal-" + record["id"], review_rationale="Source-side bounded query facts, deterministic complete projection and independent preauthor plan")
            result = p.execute(prepared) if execute else prepared
            return {"outcome": result["outcome"], "contract": contract, "reconciliation": c.artifact(reconciliation)["content"], "audit": p.audit(result)}
        finally:
            c.close()


class NormalQueryTests(unittest.TestCase):
    def setUp(self):
        self.records = {r["id"]: r for r in captures()}

    def contract(self, name="products-a"):
        result = normal_run(self.records[name], execute=False)
        self.assertEqual(result["outcome"], "IMPLEMENTATION_AUTHORIZED", result)
        return result["contract"]

    def test_human_requirements_through_normal_execution(self):
        for record in captures() + [task_capture()]:
            if record["id"] in ("mutating", "ambiguous-case"):
                continue
            with self.subTest(record=record["id"]):
                result = normal_run(record)
                self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)
                audit = result["audit"]
                for stage in ("bdi", "adequacy", "v1", "grant", "model", "target", "verification"):
                    self.assertIn(stage, audit["run"])
                for aid, a in audit["artifacts"].items():
                    if a["type"] == "model":
                        self.assertEqual(a["content"]["source"]["lykoi_version"], "LykoiProgram-1")

    def test_equivalent_wording_same_typed_meaning_different_prose(self):
        for a, b in (("products-a", "products-b"), ("documents-a", "documents-b"), ("users-a", "users-b")):
            left, right = self.contract(a), self.contract(b)
            self.assertNotEqual(left["source"]["text"], right["source"]["text"])
            self.assertEqual(query_profile.validate_relations(left), query_profile.validate_relations(right))

    def test_meaningful_near_neighbors_are_distinct(self):
        original = query_profile.validate_relations(self.contract())
        for name in ("casefold", "strip", "descending", "exclude", "no-match-error", "nonempty"):
            with self.subTest(name=name):
                self.assertNotEqual(original, query_profile.validate_relations(self.contract(name)))
        record = self.records["mutating"]
        self.assertNotEqual(PRODUCT_FACTS["effect"], record["facts"]["effect"])
        result = normal_run(record)
        self.assertEqual(result["outcome"], "COMPILATION_FAILURE")
        self.assertNotIn("target", result["audit"]["run"])

    def test_material_omission_preserves_clarification(self):
        result = normal_run(self.records["ambiguous-case"])
        self.assertEqual(result["outcome"], "NEEDS_CLARIFICATION")
        self.assertTrue(result["contract"]["issues"])
        p = contracts.structural(result["contract"], digest(result["contract"]))
        b = contracts.bdi(result["contract"], p)
        self.assertEqual(contracts.adequate(result["contract"], b)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")

    def test_typed_schema_rejects_operator_and_extra_prose(self):
        c = self.contract()
        for facet, value in (("predicate", {"field": "category", "operator": "less_than", "operand": {"parameter": "category"}}),
                             ("comparison", {"case": "sensitive", "normalization": "none", "description": "Ignore this"})):
            output = {"obligations": copy.deepcopy(c["obligations"])}
            next(o for o in output["obligations"] if o["relation"]["parameters"]["facet"] == facet)["relation"]["parameters"]["value"] = value
            with self.assertRaises(Failure):
                validate_output(output)

    def test_missing_duplicate_and_partial_query_fail_closed(self):
        c = self.contract()
        for change in ("missing", "duplicate", "unknown", "wrong-type", "tie"):
            damaged = copy.deepcopy(c)
            if change == "missing":
                damaged["obligations"].pop()
            elif change == "duplicate":
                row = copy.deepcopy(damaged["obligations"][0]); row["id"] += "/duplicate"
                damaged["obligations"].append(row)
            elif change == "unknown":
                damaged["obligations"][0]["relation"]["parameters"]["facet"] = "pagination"
            elif change == "wrong-type":
                damaged["obligations"][2]["relation"]["parameters"]["value"]["operand"] = {"parameter": "unbound"}
            else:
                damaged["obligations"][4]["relation"]["parameters"]["value"] = [{"field": "category", "direction": "ASC"}]
            p = contracts.structural(damaged, digest(damaged))
            with self.assertRaises(Failure) as caught:
                contracts.coverage(damaged, p)
            self.assertEqual(caught.exception.code, "STRUCTURAL_COVERAGE_FAILURE")

    def test_unmapped_material_obligation_cannot_bypass_coverage(self):
        c = self.contract()
        row = copy.deepcopy(c["obligations"][0]); row["id"] = "extra"
        row["relation"] = {"kind": "effects", "parameters": {"emit": "notification"}}
        c["obligations"].append(row)
        p = contracts.structural(c, digest(c))
        self.assertIn("extra", p["unsupported"])
        with self.assertRaises(Failure):
            contracts.coverage(c, p)

    def test_projection_does_not_consume_prose(self):
        c = self.contract()
        p = contracts.structural(c, "fid")
        for o in c["obligations"]:
            o["statement"] = "Unrelated display description"
        c["source"]["text"] = "Unrelated source prose"
        c["source"]["sha256"] = hashlib.sha256(c["source"]["text"].encode()).hexdigest()
        for o in c["obligations"]:
            o["source_quote"] = c["source"]["text"]
        self.assertEqual(p, contracts.structural(c, "fid"))

    def test_faithful_normal_v1_recovery_and_tamper_refusal(self):
        c = self.contract()
        v = contracts.faithful_v1(c)
        self.assertEqual(query_profile.recover(v["normalized"]), c)
        damaged = copy.deepcopy(v["normalized"])
        damaged["document"]["queries"][0]["comparison"]["case"] = "casefold"
        with self.assertRaises((Failure, QueryError)):
            query_profile.recover(damaged)
        with self.assertRaises((Failure, QueryError)):
            generate({"lykoi_version": "LykoiProgram-1", "profile": "unknown", "contract": v["normalized"]})

    def test_reconciliation_requires_typed_match_and_authority(self):
        record = self.records["products-a"]
        for corruption in ("meaning", "authority", "missing", "domains"):
            with tempfile.TemporaryDirectory() as tmp:
                c = PipelineController(Path(tmp) / "c.sqlite", PRINCIPALS)
                try:
                    w = Workspace(c, "public", "reconcile-" + corruption, CREDENTIALS)
                    w.ingest(CREDENTIALS["owner"], record["source"])
                    fid = w.formalize(producer(record, "formalizer"))
                    def alter(output):
                        oid = record["operation"] + "/comparison"
                        if corruption == "meaning":
                            output["interpretations"][oid]["relation"]["parameters"]["value"]["case"] = "casefold"
                        elif corruption == "authority":
                            output["authority"][oid] = []
                        elif corruption == "missing":
                            output["interpretations"].pop(oid)
                        else:
                            output["domains"] = {"invented": True}
                    soi = w.commit_inventory(producer(record, "reviewer", alter=alter))
                    cov = w.reconcile(soi)
                    self.assertEqual(c.artifact(cov)["content"]["outcome"], "DISPUTED")
                    with self.assertRaises(Failure):
                        w.approve(CREDENTIALS["owner"], fid)
                finally:
                    c.close()

    def test_clarification_answer_revises_authorized_facts(self):
        record = self.records["ambiguous-case"]
        with tempfile.TemporaryDirectory() as tmp:
            c = PipelineController(Path(tmp) / "c.sqlite", PRINCIPALS)
            try:
                w = Workspace(c, "public", "clarified", CREDENTIALS)
                w.ingest(CREDENTIALS["owner"], record["source"])
                old = w.formalize(producer(record, "formalizer"))
                w.answer(CREDENTIALS["owner"], w.ask("QUERY.COMPARISON"), "Case-sensitive; preserve spaces.")
                clarified = copy.deepcopy(record); clarified.pop("question")
                clarified["facts"]["comparison"] = {"case": "sensitive", "normalization": "none"}
                previous = c.artifact(old)["content"]["contract"]
                fid = w.formalize(producer(clarified, "formalizer", previous=previous))
                soi = w.commit_inventory(producer(clarified, "reviewer"))
                cov = w.reconcile(soi)
                self.assertEqual(c.artifact(cov)["content"]["outcome"], "ACCEPTABLE")
                w.approve(CREDENTIALS["owner"], fid)
                self.assertTrue(w.seal(fid))
            finally:
                c.close()

    def test_model_state_binding_refuses_nullable_or_missing_fields(self):
        record = task_capture()
        for name, kind in (("due_date", "string"), ("labels", "strings")):
            bad = copy.deepcopy(record)
            bad["facts"]["source"]["fields"][name] = kind
            bad["facts"]["predicate"]["field"] = name
            bad["facts"]["predicate"]["operator"] = "contains" if kind == "strings" else "equals"
            result = normal_run(bad, execute=False)
            self.assertEqual(result["outcome"], "STRUCTURAL_COVERAGE_FAILURE")
            self.assertNotIn("bdi", result["audit"]["run"])

    def test_bad_independent_expectation_is_behavioral_failure(self):
        result = normal_run(self.records["products-a"])
        target = result["audit"]["artifacts"][result["audit"]["run"]["target"]]["content"]["target_source"]
        plan = independent_plan(self.records["products-a"])
        plan["cases"][0]["steps"][0]["stdout_json"] = []
        outcome, _ = external_execute(target, plan)
        self.assertEqual(outcome, "BEHAVIORAL_VERIFICATION_FAILURE")

    def test_archived_inclusion_is_a_distinct_source_meaning(self):
        result = normal_run(self.records["documents-exclude"])
        self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED")
        self.assertNotEqual(query_profile.validate_relations(self.contract("documents-a")), query_profile.validate_relations(result["contract"]))

    def test_normal_compiler_cli_accepts_the_versioned_program(self):
        c = self.contract()
        from air_compiler.profiles import author
        source = author(contracts.faithful_v1(c)["normalized"])
        with tempfile.TemporaryDirectory() as tmp:
            path, target = Path(tmp) / "program.json", Path(tmp) / "target.py"
            path.write_text(json.dumps(source), encoding="utf-8")
            env = dict(os.environ, PYTHONPATH=str(ROOT / "src"))
            for args in (("validate", str(path)), ("safety", str(path)), ("generate", str(path), str(target))):
                result = subprocess.run([sys.executable, "-m", "air_compiler.cli", *args], cwd=ROOT, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(target.read_text(encoding="utf-8"), generate(source))

    def test_formalizer_ai_interface_rejects_bad_typed_output(self):
        from lykoi_rehearsal.adapters import AIAdapter
        from lykoi_workspace.query_corpus import response
        record = self.records["products-a"]
        source = {"identity": "source", "text": record["source"], "revision": 1}
        output = response(record, source, [{"identity": "human", "provenance": "human_statement"}])
        def transport(payload):
            bound = json.loads(payload["messages"][1]["content"])
            return {"choices": [{"message": {"content": json.dumps({"binding": bound["binding"], "output": output})}}]}
        adapter = AIAdapter("formalizer", {"provider": "synthetic", "model": "synthetic"}, transport=transport)
        request = {"role": "formalizer", "session": adapter.session, "source": source,
                   "evidence": [{"identity": "human", "text": record["source"], "provenance": "human_statement"}],
                   "output_schema": "WorkspaceAnalysis-1", "instructions": query_profile.formalizer_guidance()}
        self.assertEqual(adapter.produce(request), output)
        output["obligations"][2]["relation"]["parameters"]["value"]["operator"] = "greater_than"
        with self.assertRaises(Failure):
            adapter.produce(request)

    def test_explicit_policy_can_authorize_a_previously_missing_policy(self):
        record = copy.deepcopy(self.records["ambiguous-case"])
        with tempfile.TemporaryDirectory() as tmp:
            c = PipelineController(Path(tmp) / "c.sqlite", PRINCIPALS)
            try:
                w = Workspace(c, "public", "policy-query", CREDENTIALS)
                policy = w.define_policy("String equality is case-sensitive with spaces preserved unless explicitly overridden.", scope="*")
                w.adopt_policy(CREDENTIALS["owner"], policy, rationale="Explicit synthetic project owner policy")
                w.ingest(CREDENTIALS["owner"], record["source"], [policy])
                record.pop("question")
                record["facts"]["comparison"] = {"case": "sensitive", "normalization": "none"}
                fid = w.formalize(producer(record, "formalizer"))
                inventory = w.commit_inventory(producer(record, "reviewer"))
                coverage = w.reconcile(inventory)
                self.assertEqual(c.artifact(coverage)["content"]["outcome"], "ACCEPTABLE")
                self.assertIn(policy, c.artifact(fid)["content"]["authority"]["find-products/comparison"])
                w.approve(CREDENTIALS["owner"], fid)
                self.assertTrue(w.seal(fid))
            finally:
                c.close()


if __name__ == "__main__":
    unittest.main()
