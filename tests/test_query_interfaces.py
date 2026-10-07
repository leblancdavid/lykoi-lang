"""Normal-path interface composition, authority losses and external determinism."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from air_compiler.profiles import author, generate
from air_compiler.collection_query import validate
from air_compiler.collection_query_runtime import execute, ApplicationError
from lykoi_controller import Failure
from lykoi_pipeline import contracts, mutable_profile, PipelineController
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.interface_corpus import captures, plan, amend

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("interface_evaluator", ROOT / "benchmark/results/phase5c/R5_103-evaluate.py")
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
CACHE = {}


def prepared():
    if not CACHE:
        r = captures()[0]
        result = ev.evaluate(r["candidate"], plan(r))
        assert result["first_blocker"] == "SUCCESS", result.get("terminal", result)
        CACHE.update(record=r, result=result, contract=result["formalization"]["contract"])
    return copy.deepcopy(CACHE["record"]), copy.deepcopy(CACHE["contract"])


class InterfaceTests(unittest.TestCase):
    def test_full_normal_path_literal_persistence_amendment_errors(self):
        r, c = prepared()
        p = contracts.structural(c, "frc"); contracts.coverage(c, p)
        self.assertEqual(contracts.adequate(c, contracts.bdi(c, p))["outcome"], "ADEQUATE")
        normal = contracts.faithful_v1(c)["normalized"]
        self.assertEqual(mutable_profile.recover(normal), c)
        self.assertEqual(generate(author(normal)), generate(author(normal)))
        self.assertEqual(CACHE["result"]["external_invocations"], 21)

    def test_declared_clock_injected_external_process_sample_once_and_order(self):
        r, c = prepared()
        source = generate(author(contracts.faithful_v1(c)["normalized"]))
        query = r["queries"]["expired"]
        query["resources"].append({**query["resources"][0], "name": "same_clock_alias"})
        rows = plan(r)["cases"][0]["initial_files"][0]["json"]
        # External process imports only generated target, controls the declared
        # provider and observes query output; no in-process runtime substitution.
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(source, encoding="utf-8")
            (Path(tmp) / r["path"]).write_text(json.dumps(rows), encoding="utf-8")
            probe = ("import target, json\ncount=[]\ndef now():\n count.append(1)\n return '2999-01-01T00:00:00Z'\n" +
                "q=" + repr(query) + "\nstate=target.SPEC['state'][0]\nrt,path=target.state_layout(state)\nrows=target.read_state(state,rt,path)\nbefore=path.read_bytes()\n" +
                "result=target.execute_query(q, rows, {}, providers={q['resources'][0]['capability']:now})\n" +
                "print(json.dumps({'ids':[r['id'] for r in result],'samples':len(count),'preserved':path.read_bytes()==before}))\n")
            (Path(tmp) / "probe.py").write_text(probe, encoding="utf-8")
            p = subprocess.run([sys.executable, "probe.py"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual(json.loads(p.stdout), dict(ids=["b"], samples=1, preserved=True))
        q = copy.deepcopy(r["queries"]["owner-expired"])
        rows[2]["expires_at"] = "2001-01-01T00:00:00Z"
        cid = q["resources"][0]["capability"]
        self.assertEqual([x["id"] for x in execute(q, rows, {"owner": "Beta"}, providers={cid: lambda: "2024-01-01T00:00:00Z"})], ["c", "b"])
        with self.assertRaises(ApplicationError): execute(q, rows, {"owner": "Beta"}, providers={cid: lambda: "bad"})
        with self.assertRaises(ValueError): execute(q, rows, {"owner": "Beta"}, providers={"ambient": lambda: "2024-01-01T00:00:00Z"})

    def test_precondition_before_selection_distinct_parameter_validation(self):
        r = captures()[0]
        q = r["queries"]["owner-required"]
        for inputs, error in (({}, "missing_owner"), ({"owner": True}, "invalid_owner_type"), ({"owner": ""}, "invalid_owner")):
            with self.assertRaises(ApplicationError) as ctx:
                execute(q, object(), inputs, providers={q["resources"][0]["capability"]: lambda: "2024-01-01T00:00:00Z"})
            self.assertEqual(str(ctx.exception), error)
        self.assertEqual(execute(q, [], {"owner": "absent"}, providers={q["resources"][0]["capability"]: lambda: "2024-01-01T00:00:00Z"}), [])

    def test_source_reconciliation_literal_composition_error_and_clock_identity(self):
        r = captures()[0]["candidate"]
        edits = []
        i = next(i for i, o in enumerate(r["rows"]) if o["relation"]["parameters"].get("facet") == "mutations")
        v = copy.deepcopy(r["rows"][i]["relation"]["parameters"]["value"])
        next(m for m in v if m["command"] == "deactivate")["changes"][0]["source"]["value"] = True
        edits.append((i, v))
        for facet, command in (("preconditions", "owner-required"), ("resources", "expired"), ("amendment", "list")):
            i = next(i for i, o in enumerate(r["rows"]) if o["relation"]["parameters"].get("facet") == facet and o["relation"]["parameters"].get("query") == command)
            v = copy.deepcopy(r["rows"][i]["relation"]["parameters"]["value"])
            if facet == "preconditions": v[0]["error"] = "wrong_error"
            if facet == "resources": v[0]["capability"] = "wrong_clock"
            if facet == "amendment": v["composition"] = "replace"
            edits.append((i, v))
        for i, value in edits:
            bad = copy.deepcopy(r); bad["rows"][i]["relation"]["parameters"]["value"] = value
            if bad["rows"][i]["relation"]["parameters"]["facet"] == "amendment":
                next(o for o in bad["rows"] if o["relation"]["parameters"].get("query") == "list" and o["relation"]["parameters"].get("facet") == "predicate")["relation"]["parameters"]["value"] = copy.deepcopy(value["predicate"])
            with tempfile.TemporaryDirectory() as tmp:
                ctrl = PipelineController(Path(tmp) / "case.sqlite", PRINCIPALS)
                try:
                    w = Workspace(ctrl, "public", "interfaces-authority", CREDENTIALS)
                    w.ingest(CREDENTIALS["owner"], r["source"])
                    w.formalize(ev.producer(bad, "formalizer"))
                    soi = w.commit_inventory(ev.producer(r, "reviewer"))
                    self.assertEqual(ctrl.artifact(w.reconcile(soi))["content"]["outcome"], "DISPUTED")
                finally: ctrl.close()

    def test_coverage_v1_and_adequacy_detect_material_interface_loss(self):
        _, c = prepared()
        p = contracts.structural(c, "frc")
        for facet in ("amendment", "preconditions", "resources", "parameter_errors"):
            bad = copy.deepcopy(p)
            query = next(q for q in bad["facts"]["queries"].values() if facet in q)
            query.pop(facet)
            with self.assertRaises(Failure): contracts.coverage(c, bad)
            normal = contracts.faithful_v1(c)["normalized"]
            next(q for q in normal["facts"]["queries"].values() if facet in q).pop(facet)
            with self.assertRaises(Failure): mutable_profile.recover(normal)
        b = contracts.bdi(c, p)
        normal = contracts.faithful_v1(c)["normalized"]
        next(m for m in normal["facts"]["mutable"]["mutations"] if m["command"] == "deactivate")["changes"][0]["source"]["value"] = True
        with self.assertRaises(Failure): mutable_profile.recover(normal)
        decisions = [d for d in b["result"]["decisions"] if "literal_assignment" in d["family"] or d["family"] in ("query_amendment", "query_preconditions", "query_resources", "query_parameter_errors")]
        self.assertGreaterEqual(len(decisions), 10)
        for d in decisions:
            bad = copy.deepcopy(b)
            next(x for x in bad["result"]["decisions"] if x["id"] == d["id"])["authority"] = None
            self.assertEqual(contracts.adequate(c, bad)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")

    def test_amendment_modes_preserve_order_and_refuse_unknown_authority(self):
        r = captures()[0]
        a = r["queries"]["list"]["amendment"]
        for mode in ("and", "or", "replace"):
            q = amend(a["base"], a["predicate"], mode)
            validate(q, complete=True)
            self.assertEqual(q["ordering"], a["base"]["ordering"])
        q = amend(a["base"], a["predicate"], "unknown")
        with self.assertRaises(Failure): validate(q)
        q = copy.deepcopy(r["queries"]["list"]); q["ordering"].reverse()
        with self.assertRaises(Failure): validate(q)
        q = copy.deepcopy(r["queries"]["expired"]); q.pop("resources")
        with self.assertRaises(Failure): validate(q)


if __name__ == "__main__": unittest.main()
