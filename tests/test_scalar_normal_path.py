"""R5.102 normal typed-FRC closure and external persistence/restart challenges."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from uuid import UUID
from datetime import datetime, timezone

from air_compiler.profiles import author, generate
from lykoi_controller import Failure
from lykoi_pipeline import Pipeline, PipelineController, contracts, plans
from lykoi_pipeline.controller import digest
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_pipeline import scalar_profile as profile
from lykoi_workspace import Workspace
from lykoi_workspace.producers import ModelAdapter
from lykoi_workspace.scalar_corpus import captures, producer, obligations
from lykoi_workspace.query_schema import validate_output


def literal_record(record, identity="known", state=None, reference="  retained  "):
    result = {"id": identity, record["label"]: "  exact !  ", "state": state or record["initial"],
            "class": record["values"][1], "reference": reference, "created_at": "2026-01-01T00:00:00Z", "review_at": None}
    if any(f["name"] == "annotation" for f in record["facts"]["fields"]):
        result["annotation"] = "state"
    return result


def independent_plan(record):
    ids = [o["id"] for o in obligations(record)]
    store = record["id"] + ".json"
    old = literal_record(record)
    for m in record["facts"]["evolution"]:
        for field in m["defaults"]: old.pop(field)
    current = literal_record(record)
    advanced = {**current, "state": record["target"]}
    migrated = copy.deepcopy(old)
    for m in record["facts"]["evolution"]: migrated.update(m["defaults"])
    version = record["facts"]["storage"]["version"]
    def step(argv, expected=None, error=None, preserve=False, contains=None, rc=None):
        s = {"argv": argv, "returncode": (1 if error else 0) if rc is None else rc,
             "contains": contains or [], "preserved": [store] if preserve else []}
        if expected is not None or error:
            s["stderr_json" if error else "stdout_json"] = {"error": error} if error else expected
        if rc is None:
            s["stdout_exact" if error else "stderr_exact"] = ""
        return s
    def case(cid, fixture, steps):
        c = {"id": cid, "obligations": ids, "initial_state": "fresh_directory", "initial_files": fixture,
             "steps": steps, "invariants": ["Identity and unrelated values preserved", "Rejected storage unchanged"], "transitions": "Declared guarded lifecycle", "rejections": "Source error codes"}
        c["identity"] = digest(c)
        return c
    cases = [
        case("creation-reload", [], [step(["register", "--" + record["label"], "  exact !  ", "--reference", " supplied "], contains=["  exact !  ", " supplied ", record["initial"], record["values"][0]]),
                                          step(["list"], preserve=True, contains=["  exact !  ", " supplied ", record["values"][0]]),
                                          step(["register", "--" + record["label"], "   "], error="invalid_label", preserve=True),
                                          step(["register", "--" + record["label"], "valid", "--review-at", "bad"], error="invalid_review", preserve=True),
                                          step(["register", "--" + record["label"], "valid", "--class", "OUTSIDE"], preserve=True, rc=2)]),
        case("lifecycle-restart-rejection", [{"path": store, "json": {"schema_version": version, "records": [current]}}], [
            step(["advance", "--id", "known"], advanced), step(["list"], [advanced], preserve=True),
            step(["advance", "--id", "known"], error="invalid_transition", preserve=True),
            step(["advance", "--id", "absent"], error="record_not_found", preserve=True), step(["list"], [advanced], preserve=True)]),
        case("authorized-migration", [{"path": store, "json": [old]}], [step(["list"], error="migration_required", preserve=True),
            step(["migrate"], {"migrated": 1}), step(["list"], [migrated], preserve=True), step(["migrate"], {"migrated": 0}, preserve=True)]),
        case("invalid-historical-value", [{"path": store, "json": [{**old, "class": "OUTSIDE"}]}], [step(["migrate"], error="invalid_state", preserve=True)]),
        case("missing-read-no-initialization", [], [step(["list"], [], preserve=True), step(["migrate"], {"migrated": 0}, preserve=True)]),
    ]
    return {"version": plans.VERSION, "outcome": "READY", "producer": "R5.102-source-side-literal-external-plan", "source_sha256": hashlib.sha256(record["source"].encode()).hexdigest(),
            "cases": cases, "coverage": [{"obligation": oid, "classification": "EXERCISED", "justification": "Source-derived literal process/restart/migration observations", "cases": [c["identity"] for c in cases]} for oid in ids],
            "limitations": ["Finite same-agent source-side plan; process independence, not independent cognition"]}


def normal_run(record, execute=True):
    plan = independent_plan(record)  # source oracle exists before authorship
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "normal.sqlite"
        c = PipelineController(path, PRINCIPALS, verification_fixtures={plan["source_sha256"]: plan})
        try:
            w = Workspace(c, "public", record["id"], CREDENTIALS)
            w.ingest(CREDENTIALS["owner"], record["source"])
            fid = w.formalize(producer(record, "formalizer"))
            soi = w.commit_inventory(producer(record, "reviewer"))
            rid = w.reconcile(soi)
            reconciliation = c.artifact(rid)["content"]
            if reconciliation["outcome"] != "ACCEPTABLE":
                return {"outcome": reconciliation["outcome"], "reconciliation": reconciliation}
            w.approve(CREDENTIALS["owner"], fid)
            seal = w.seal(fid)
            contract = c.artifact(fid)["content"]["contract"]
            p = Pipeline(c, "public", CREDENTIALS)
            prepared = p.prepare(seal, "r5-102-" + record["id"], review_rationale="Source-authorized existing scalar facts; full deterministic coverage; source-side external plan")
            terminal = p.execute(prepared) if execute else prepared
            audit = p.audit(terminal)
            c.close()
            c = PipelineController(path, PRINCIPALS, verification_fixtures={plan["source_sha256"]: plan})
            restarted = Pipeline(c, "public", CREDENTIALS).audit(terminal)
            assert restarted == audit
            return {"outcome": terminal["outcome"], "contract": contract, "audit": audit, "reconciliation": reconciliation, "restart_audit": "IDENTICAL"}
        finally:
            c.close()


class ScalarNormalPathTests(unittest.TestCase):
    def contract(self):
        result = normal_run(captures()[0], execute=False)
        self.assertEqual(result["outcome"], "IMPLEMENTATION_AUTHORIZED", result)
        return result["contract"]

    def test_multi_domain_normal_path_and_restart(self):
        for record in captures():
            with self.subTest(domain=record["id"]):
                result = normal_run(record)
                self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)
                self.assertEqual(result["restart_audit"], "IDENTICAL")
                self.assertTrue(all(s in result["audit"]["run"] for s in ("bdi", "adequacy", "v1", "grant", "model", "target", "verification")))

    def test_external_resources_defaults_null_and_verbatim(self):
        result = normal_run(captures()[0])
        self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)
        source = next(a["content"]["target_source"] for a in result["audit"]["artifacts"].values() if a["type"] == "target")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "program.py"; target.write_text(source, encoding="utf-8")
            def call(*args):
                p = subprocess.run([sys.executable, str(target), *args], cwd=tmp, capture_output=True, text=True, encoding="utf-8", timeout=15)
                self.assertEqual(p.returncode, 0, p.stderr)
                return json.loads(p.stdout)
            before = datetime.now(timezone.utc)
            one = call("register", "--caption", " exact ")
            two = call("register", "--caption", "Second", "--class", "LOAN", "--reference", "", "--review-at", "2026-01-02T03:04:05.000Z")
            self.assertEqual(UUID(one["id"]).version, 4)
            self.assertNotEqual(one["id"], two["id"])
            self.assertGreaterEqual(datetime.fromisoformat(one["created_at"].replace("Z", "+00:00")), before)
            self.assertEqual(one["caption"], " exact "); self.assertEqual(one["class"], "REFERENCE")
            self.assertEqual(one["reference"], ""); self.assertIsNone(one["review_at"])
            self.assertEqual(two["review_at"], "2026-01-02T03:04:05.000Z")
            self.assertEqual(call("list"), [one, two])

    def test_existing_model_additive_evolution_normal_path(self):
        original = captures()[0]
        initial = normal_run(original)
        self.assertEqual(initial["outcome"], "BEHAVIORALLY_VERIFIED")
        # Existing model is prior authorized program context, never a middle-stage
        # author fixture in the new requirement's path.
        base = profile.lower(profile.facts(initial["contract"]))
        record = copy.deepcopy(original)
        record["source"] += " Using this existing version-2 model, introduce annotation at schema version 3 as a verbatim optional string. Omission on register gives the literal string state. Explicit version-2-to-3 migration adds annotation with the literal state; retain every existing command, guard, type, resource and prior migration unchanged."
        record["domains"] = {"scalar_base_model": base}
        record["facts"]["storage"]["version"] = 3
        record["facts"]["fields"].append({"name": "annotation", "type": "string", "domain": [], "nullable": False, "preservation": "verbatim"})
        record["facts"]["creation"]["bindings"].append({"field": "annotation", "source": "input", "value": None, "default": {"value": "state", "trigger": "omitted", "boundary": "creation"}})
        record["facts"]["evolution"].append({"from": 2, "to": 3, "defaults": {"annotation": "state"}, "boundary": "explicit_migration", "preservation": "unrelated_fields"})
        result = normal_run(record)
        self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)
        evolved = profile.lower(profile.facts(result["contract"]), base)
        self.assertEqual(evolved["transitions"], base["transitions"])
        self.assertEqual(evolved["migrations"][0], base["migrations"][0])

    def test_existing_enum_domain_expansion_normal_path(self):
        record = captures()[1]
        original = normal_run(record)
        self.assertEqual(original["outcome"], "BEHAVIORALLY_VERIFIED")
        base = profile.lower(profile.facts(original["contract"]))
        record["domains"] = {"scalar_base_model": base}
        record["source"] += " Expand the class domain of this supplied model with CALIBRATION, preserving every earlier value exactly, current creation default CONTROL and existing explicit migration. No rank semantics or historical repairs are authorized."
        next(f for f in record["facts"]["fields"] if f["name"] == "class")["domain"].append("CALIBRATION")
        result = normal_run(record)
        self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)
        source = next(a["content"]["target_source"] for a in result["audit"]["artifacts"].values() if a["type"] == "target")
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "program.py"; target.write_text(source, encoding="utf-8")
            p = subprocess.run([sys.executable, str(target), "register", "--specimen", " exact ", "--class", "CALIBRATION"], cwd=tmp, capture_output=True, text=True, timeout=15)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout)["class"], "CALIBRATION")

    def test_verbatim_scalar_store_with_existing_query_comparison(self):
        from lykoi_workspace.query_corpus import producer as query_producer
        record = captures()[2]
        prior = normal_run(record)
        self.assertEqual(prior["outcome"], "BEHAVIORALLY_VERIFIED")
        base = profile.lower(profile.facts(prior["contract"]))
        source = "Using the supplied gallery registry model, find every record with inscription exactly equal to the runtime text, case-sensitively and without trimming. Include draft and published. Return whole records, ascending created_at then id, empty list when no match. No additional query input validation. Preserve state and storage bytes and existing commands."
        query = {"id": "gallery-equality", "source": source, "operation": "find",
                 "domains": {"collection_store": {"kind": "model_state", "model": base, "state": "state"}}, "facts": {
                     "source": {"collection": "state", "fields": {"id": "string", "inscription": "string", "state": "string", "created_at": "string"}, "unique_key": "id"},
                     "parameters": {"text": "string"}, "predicate": {"field": "inscription", "operator": "equals", "operand": {"parameter": "text"}},
                     "comparison": {"case": "sensitive", "normalization": "none"}, "ordering": [{"field": "created_at", "direction": "ASC"}, {"field": "id", "direction": "ASC"}],
                     "validation": [], "inclusion": [{"field": "state", "mode": "all"}], "effect": {"state": "read_only", "persistence": "unchanged"},
                     "result": {"shape": "collection", "cardinality": "zero_or_more", "no_match": "empty"}}}
        ids = ["find/" + f for f in query["facts"]]
        stored = literal_record(record)
        steps = [{"argv": ["find", "--text", value], "returncode": 0, "contains": [], "preserved": ["gallery.json"], "stdout_json": expected, "stderr_exact": ""}
                 for value, expected in (("  exact !  ", [stored]), ("exact !", []), ("  EXACT !  ", []))]
        case = {"id": "verbatim-comparison", "obligations": ids, "initial_state": "fresh_directory", "initial_files": [{"path": "gallery.json", "json": {"schema_version": 2, "records": [stored]}}], "steps": steps,
                "invariants": ["Stored verbatim values and bytes unchanged"], "transitions": "None", "rejections": "None"}
        case["identity"] = digest(case)
        plan = {"version": plans.VERSION, "outcome": "READY", "source_sha256": hashlib.sha256(source.encode()).hexdigest(), "producer": "literal-source-side", "cases": [case],
                "coverage": [{"obligation": oid, "classification": "EXERCISED", "justification": "Exact/case/whitespace near neighbors", "cases": [case["identity"]]} for oid in ids], "limitations": ["Same-agent finite oracle"]}
        with tempfile.TemporaryDirectory() as tmp:
            c = PipelineController(Path(tmp) / "query.sqlite", PRINCIPALS, verification_fixtures={plan["source_sha256"]: plan})
            try:
                w = Workspace(c, "public", "gallery-query", CREDENTIALS); w.ingest(CREDENTIALS["owner"], source)
                fid = w.formalize(query_producer(query, "formalizer")); soi = w.commit_inventory(query_producer(query, "reviewer"))
                rid = w.reconcile(soi); self.assertEqual(c.artifact(rid)["content"]["outcome"], "ACCEPTABLE")
                w.approve(CREDENTIALS["owner"], fid); seal = w.seal(fid)
                p = Pipeline(c, "public", CREDENTIALS); prepared = p.prepare(seal, "gallery-equality", review_rationale="Typed existing query comparison against prior normal-path scalar model")
                result = p.execute(prepared)
                self.assertEqual(result["outcome"], "BEHAVIORALLY_VERIFIED", result)
            finally:
                c.close()

    def test_v1_and_model_tamper_rejected(self):
        c = self.contract(); v = contracts.faithful_v1(c)["normalized"]
        self.assertEqual(profile.recover(v), c)
        bad = copy.deepcopy(v); bad["facts"]["creation"]["bindings"][3]["default"]["value"] = "LOAN"
        with self.assertRaises(Failure):
            generate({"lykoi_version": "LykoiProgram-1", "profile": profile.PROFILE, "contract": bad})
        self.assertIn("DO NOT EDIT", generate(author(v)))

    def test_type_support_is_not_query_type_storage_support(self):
        for kind in ("boolean", "integer", "date", "strings"):
            record = copy.deepcopy(captures()[0]); record["facts"]["fields"][1]["type"] = kind
            with self.assertRaises(Failure):
                profile.validate_facts(record["facts"])

    def test_no_general_null_transform_or_default_scope(self):
        for mutation in ("null", "strip", "scope", "trigger", "missing"):
            record = copy.deepcopy(captures()[0]); f = record["facts"]
            if mutation == "null": f["fields"][1]["nullable"] = True
            elif mutation == "strip": f["fields"][1]["preservation"] = "trimmed"
            elif mutation == "scope": f["creation"]["bindings"][3]["default"]["boundary"] = "historical"
            elif mutation == "trigger": f["creation"]["bindings"][3]["default"]["trigger"] = "null_or_omitted"
            else: del f["creation"]["bindings"][3]["default"]
            with self.assertRaises(Failure): profile.validate_facts(f)

    def test_coverage_missing_extra_and_stale_fail_closed(self):
        c = self.contract()
        for change in ("missing", "extra", "stale"):
            bad = copy.deepcopy(c)
            if change == "missing": bad["obligations"].pop()
            elif change == "extra":
                row = copy.deepcopy(bad["obligations"][0]); row["id"] = "unsupported"
                row["relation"] = {"kind": "effects", "parameters": {"durable_ordered_events": True}}
                bad["obligations"].append(row)
            p = contracts.structural(bad, "frc")
            if change == "stale": p["facts"]["listing"]["order"].reverse()
            with self.assertRaises(Failure) as caught: contracts.coverage(bad, p)
            self.assertEqual(caught.exception.code, "STRUCTURAL_COVERAGE_FAILURE")

    def test_projection_uses_typed_facts_not_display_wording(self):
        c = self.contract(); p = contracts.structural(c, "frc")
        for o in c["obligations"]: o["statement"] = "Different human description"
        self.assertEqual(p, contracts.structural(c, "frc"))

    def test_bdi_existing_rules_and_unchanged_adequacy_omission(self):
        c = self.contract(); p = contracts.structural(c, "frc"); b = contracts.bdi(c, p)
        self.assertEqual(b["outcome"], "SUPPORTED")
        families = {d["family"] for d in b["result"]["decisions"]}
        self.assertTrue({"optional", "persistence", "failure_atomicity", "transition", "retry", "invalid_input"} <= families)
        self.assertEqual(contracts.adequate(c, b)["outcome"], "ADEQUATE")
        damaged = copy.deepcopy(b)
        next(d for d in damaged["result"]["decisions"] if d["family"] == "optional")["authority"] = None
        self.assertEqual(contracts.adequate(c, damaged)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")

    def test_closed_producer_schema(self):
        record = captures()[0]; output = {"obligations": obligations(record)}
        validate_output(output)
        output["obligations"][1]["relation"]["parameters"]["value"][0]["prose"] = "ignore"
        with self.assertRaises(Failure): validate_output(output)

    def test_typed_authority_reconciliation_and_owner_approval(self):
        record = captures()[0]
        for mutation in ("no_authority", "review_disagrees", "context_disagrees", "no_owner"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as tmp:
                c = PipelineController(Path(tmp) / "authority.sqlite", PRINCIPALS)
                try:
                    w = Workspace(c, "public", "authority-" + mutation, CREDENTIALS)
                    w.ingest(CREDENTIALS["owner"], record["source"])
                    formalizer = producer(record, "formalizer")
                    if mutation == "no_authority":
                        original = formalizer.invoke
                        def missing(request):
                            value = original(request); value["authority"] = {}; return value
                        formalizer.invoke = missing
                    try:
                        fid = w.formalize(formalizer)
                    except Failure:
                        self.assertEqual(mutation, "no_authority")
                        continue
                    reviewer = producer(record, "reviewer")
                    if mutation in ("review_disagrees", "context_disagrees"):
                        original = reviewer.invoke
                        def disagree(request):
                            value = original(request)
                            if mutation == "context_disagrees": value["domains"] = {}
                            else: value["interpretations"][record["id"] + "/storage"]["relation"]["parameters"]["value"]["version"] = 1
                            return value
                        reviewer.invoke = disagree
                    soi = w.commit_inventory(reviewer); rid = w.reconcile(soi)
                    if mutation == "no_owner":
                        self.assertEqual(c.artifact(rid)["content"]["outcome"], "ACCEPTABLE")
                        with self.assertRaises(Failure): w.seal(fid)
                    else:
                        self.assertNotEqual(c.artifact(rid)["content"]["outcome"], "ACCEPTABLE")
                finally:
                    c.close()


if __name__ == "__main__":
    unittest.main()
