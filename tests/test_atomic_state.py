"""Atomic coupled records: full pipeline and independent subprocess failure probes."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from air_compiler.profiles import author, generate
from air_compiler.atomic_state import compose
from lykoi_controller import Failure
from lykoi_pipeline import contracts, mutable_profile, PipelineController
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.atomic_state_corpus import captures, plan

ROOT = Path(__file__).resolve().parents[1]
s = importlib.util.spec_from_file_location("atomic_evaluator", ROOT / "benchmark/results/phase5c/R5_103-evaluate.py")
ev = importlib.util.module_from_spec(s); s.loader.exec_module(ev)
CACHE = {}


def prepared():
    if not CACHE:
        r = captures()[0]
        result = ev.evaluate(r["candidate"], plan(r))
        assert result["first_blocker"] == "SUCCESS", result.get("terminal", result)
        CACHE.update(record=r, contract=result["formalization"]["contract"], result=result)
    return copy.deepcopy(CACHE["record"]), copy.deepcopy(CACHE["contract"])


class AtomicStateTests(unittest.TestCase):
    def test_normal_pipeline_multidomain_external_behavior(self):
        for r in captures():
            result = ev.evaluate(r["candidate"], plan(r))
            self.assertEqual(result["first_blocker"], "SUCCESS", result.get("terminal"))
            self.assertEqual(result["external_invocations"], 21)

    def test_coverage_v1_and_adequacy_reject_material_losses(self):
        _, c = prepared()
        p = contracts.structural(c, "frc")
        normal = contracts.faithful_v1(c)["normalized"]
        self.assertEqual(mutable_profile.recover(normal), c)
        for facet in ("operations", "queries", "commit", "append_only"):
            bad = copy.deepcopy(p); bad["facts"]["atomic_state"]["facts"].pop(facet)
            with self.assertRaises(Failure): contracts.coverage(c, bad)
            bad = copy.deepcopy(normal); bad["facts"]["atomic_state"]["facts"].pop(facet)
            with self.assertRaises(Failure): mutable_profile.recover(bad)
        b = contracts.bdi(c, p)
        ds = [d for d in b["result"]["decisions"] if d["family"].startswith("atomic_state/")]
        self.assertEqual(len(ds), 4)
        for d in ds:
            bad = copy.deepcopy(b); next(x for x in bad["result"]["decisions"] if x["id"] == d["id"])["authority"] = None
            self.assertEqual(contracts.adequate(c, bad)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")

    def test_missing_authority_numeric_escape_and_append_only_refused(self):
        _, c = prepared(); f = contracts.structural(c, "frc")["facts"]
        for edit in ("empty", "frame", "clock", "payload", "numeric", "after_delete", "standalone"):
            a, refs = copy.deepcopy(f["atomic_state"]["facts"]), copy.deepcopy(f["references"])
            op = a["operations"][0]
            if edit == "empty": op["creations"] = []
            if edit == "frame": a["commit"]["rejection"] = "partial"
            if edit == "clock": op["resources"][0]["capability"] = "ambient"
            if edit == "payload": op["creations"][0]["bindings"].pop("subject")
            if edit == "numeric": op["creations"][0]["bindings"]["payload"]["source"] = dict(kind="successor", type=dict(type="integer", domain=[]), name="counter")
            if edit == "after_delete": a["operations"][-1]["creations"][0]["bindings"]["subject"]["source"]["kind"] = "after"
            if edit == "standalone": refs["facts"]["operations"].append(dict(command="edit-history", entity=a["append_only"][0], kind="update"))
            with self.assertRaises(Failure): compose(f["ir"], refs, a)

    def test_reconciliation_material_secondary_effect_content_and_order(self):
        r = captures()[0]["candidate"]
        index = next(i for i, row in enumerate(r["rows"]) if row["relation"]["parameters"]["facet"] == "atomic_state_semantics")
        for edit in ("omit", "duplicate", "subject", "action", "clock", "frame", "order", "payload", "failure", "immutable"):
            bad = copy.deepcopy(r); a = bad["rows"][index]["relation"]["parameters"]["value"]
            op = a["operations"][0]; fields = op["creations"][0]["bindings"]
            if edit == "omit": op["creations"] = []
            if edit == "duplicate": op["creations"].append(copy.deepcopy(op["creations"][0]))
            if edit == "subject": fields["subject"]["source"] = dict(kind="literal", type=fields["subject"]["source"]["type"], value="wrong")
            if edit == "action": fields["action"]["source"]["value"] = "delete"
            if edit == "clock": op["resources"][0]["capability"] = "wrong"
            if edit == "frame": a["commit"]["rejection"] = "partial"
            if edit == "order": a["queries"][0]["ordering"] = [dict(field="id", direction="ASC")]
            if edit == "payload": fields["payload"]["source"] = dict(kind="literal", type=fields["payload"]["source"]["type"], value="wrong")
            if edit == "failure": op["on"] = "failure"
            if edit == "immutable": a["append_only"] = []
            with tempfile.TemporaryDirectory() as tmp:
                ctrl = PipelineController(Path(tmp) / "case.sqlite", PRINCIPALS)
                try:
                    w = Workspace(ctrl, "public", "atomic-authority", CREDENTIALS)
                    w.ingest(CREDENTIALS["owner"], r["source"])
                    # Some corruptions are rejected by the closed producer schema;
                    # otherwise independent unchanged source inventory disputes.
                    try: w.formalize(ev.producer(bad, "formalizer"))
                    except Failure: continue
                    soi = w.commit_inventory(ev.producer(r, "reviewer"))
                    self.assertEqual(ctrl.artifact(w.reconcile(soi))["content"]["outcome"], "DISPUTED")
                finally: ctrl.close()

    def test_controlled_clock_order_failures_and_multiple_creations_external(self):
        r, c = prepared()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"
            target.write_text(generate(author(contracts.faithful_v1(c)["normalized"])), encoding="utf-8")
            path = Path(tmp) / r["path"]
            payload = plan(r)["cases"][0]["initial_files"][0]["json"]
            path.write_text(json.dumps(payload), encoding="utf-8")
            # Providers and adapter-failure injection are host test bindings in a
            # separate process; observable store/query results are asserted here.
            probe = '''import target as t,sys,json
op=t.REFERENCE["facts"]["operations"][0]
clock=t.ATOMIC_STATE["facts"]["operations"][0]["resources"][0]["capability"]
mode=sys.argv[1]
if mode=="persist":
 def fail(*a): raise OSError("injected")
 t.os.replace=fail
if mode=="secondary":
 t.ATOMIC_STATE["facts"]["operations"][0]["creations"][0]["bindings"]["payload"]["source"]={"kind":"literal","value":False}
if mode=="primary": inputs={"id":"absent","value":"new","record":"z","actor":"person"}
else: inputs={"id":"a","value":"new","record":sys.argv[2],"actor":"person"}
if mode in ("double","duplicate"):
 import copy
 second=copy.deepcopy(t.ATOMIC_STATE["facts"]["operations"][0]["creations"][0])
 second["bindings"]["id"]["source"]={"kind":"literal","value":"second" if mode=="double" else inputs["record"]}
 t.ATOMIC_STATE["facts"]["operations"][0]["creations"].append(second)
calls=[]
def observe(): calls.append(1); return "2030-01-01T00:00:00Z"
try:
 result=t.reference_operation(op,inputs,providers={clock:observe})
 print(json.dumps({"result":result,"calls":len(calls)}))
except t.Failure as e:
 print(json.dumps({"error":e.code})); sys.exit(1)
'''
            (Path(tmp) / "probe.py").write_text(probe, encoding="utf-8")
            def run(mode, rid="z"):
                return subprocess.run([sys.executable, "probe.py", mode, rid], cwd=tmp, capture_output=True, text=True)
            before = path.read_bytes()
            for mode, error in (("primary", "record_not_found"), ("secondary", "invalid_history"), ("duplicate", "history_exists"), ("persist", "persistence_failure")):
                p = run(mode); self.assertEqual(p.returncode, 1, p.stderr)
                self.assertEqual(json.loads(p.stdout), {"error": error})
                self.assertEqual(path.read_bytes(), before)
            p = run("double")
            self.assertEqual(p.returncode, 0, p.stderr); self.assertEqual(json.loads(p.stdout)["calls"], 1)
            stored = json.loads(path.read_text())["entities"][r["history"]]
            self.assertEqual([x["id"] for x in stored], ["z", "second"])
            self.assertEqual([x["timestamp"] for x in stored], ["2030-01-01T00:00:00Z"] * 2)
            p = subprocess.run([sys.executable, str(target), "history"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(json.loads(p.stdout), stored)
            for cmd in ("edit-history", "delete-history"):
                before = path.read_bytes()
                p = subprocess.run([sys.executable, str(target), cmd, "--id", "z"], cwd=tmp, capture_output=True, text=True)
                self.assertNotEqual(p.returncode, 0); self.assertEqual(path.read_bytes(), before)

    def test_shared_primary_creation_clock_and_sorted_history(self):
        for r in (captures()[0], captures()[1]):
            result = ev.evaluate(r["candidate"], plan(r)); c = result["formalization"]["contract"]
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "target.py"; target.write_text(generate(author(contracts.faithful_v1(c)["normalized"])), encoding="utf-8")
                probe = '''import target as t,json
b=next(b for b in t.SPEC["behaviors"] if b["kind"]=="create")
op=next(o for o in t.ATOMIC_STATE["facts"]["operations"] if o["command"]=="create")
clock=next(r["capability"] for r in op["resources"] if r["name"]=="clock")
uid=next(r["capability"] for r in op["resources"] if r["name"]=="record_id")
calls=[]
def now(): calls.append(1); return "2031-01-01T00:00:00Z"
inputs={i["id"]:"fresh" for i in b["inputs"] if i["name"]=="nickname"}
row=t.execute(b,inputs,providers={clock:now,uid:lambda:"00000000-0000-4000-8000-000000000001"})
print(json.dumps({"row":row,"calls":len(calls)}))
'''
                (Path(tmp) / "probe.py").write_text(probe, encoding="utf-8")
                p = subprocess.run([sys.executable, "probe.py"], cwd=tmp, capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stderr); value = json.loads(p.stdout)
                self.assertEqual(value["calls"], 1)
                path = Path(tmp) / r["path"]; payload = json.loads(path.read_text())
                h = payload["entities"][r["history"]][0]
                self.assertEqual(h["timestamp"], value["row"]["created_at"])
                # Distinct occurrence order vs timestamp/id key order after reload.
                h.update(id="z", timestamp="2031-01-01T00:00:00Z")
                h2 = {**h, "id": "a", "timestamp": "2029-01-01T00:00:00Z"}
                payload["entities"][r["history"]] = [h, h2]; path.write_text(json.dumps(payload), encoding="utf-8")
                before = path.read_bytes()
                p = subprocess.run([sys.executable, str(target), "history"], cwd=tmp, capture_output=True, text=True)
                self.assertEqual([x["id"] for x in json.loads(p.stdout)], ["z", "a"] if r["policy"] == "occurrence" else ["a", "z"])
                self.assertEqual(path.read_bytes(), before)

    def test_multiple_creations_compile_and_migration_is_not_an_operation(self):
        r, c = prepared()
        a = next(o["relation"]["parameters"]["value"] for o in c["obligations"] if o["relation"]["parameters"].get("facet") == "atomic_state_semantics")
        second = copy.deepcopy(a["operations"][0]["creations"][0])
        second["bindings"]["id"]["source"] = dict(kind="literal", type=second["bindings"]["id"]["source"]["type"], value="receipt")
        a["operations"][0]["creations"].append(second)
        normal = contracts.faithful_v1(c)["normalized"]
        # Round-trip rejects a changed secondary payload, clock, cardinality or order.
        for edit in ("remove", "payload", "frame", "clock", "order"):
            bad = copy.deepcopy(normal)
            f = bad["facts"]["atomic_state"]["facts"]
            if edit == "remove": f["operations"][0]["creations"].pop()
            if edit == "payload": f["operations"][0]["creations"][0]["bindings"]["action"]["source"]["value"] = "delete"
            if edit == "frame": f["commit"]["rejection"] = "partial"
            if edit == "clock": f["operations"][0]["resources"][0]["capability"] = "wrong"
            if edit == "order": f["queries"][0]["ordering"] = [dict(field="id", direction="ASC")]
            with self.assertRaises(Failure): mutable_profile.recover(bad)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(generate(author(normal)), encoding="utf-8")
            payload = plan(r)["cases"][0]["initial_files"][0]["json"]
            payload["entities"] = {}
            path = Path(tmp) / r["path"]; path.write_text(json.dumps(payload), encoding="utf-8")
            def run(*args): return subprocess.run([sys.executable, str(target), *args], cwd=tmp, capture_output=True, text=True)
            before = path.read_bytes()
            self.assertEqual(json.loads(run("history").stdout), [])
            self.assertEqual(path.read_bytes(), before)
            self.assertEqual(json.loads(run("migrate").stdout), {"migrated": 1})
            self.assertEqual(json.loads(path.read_text())["entities"], {r["history"]: []})
            self.assertEqual(json.loads(run("migrate").stdout), {"migrated": 0})
            p = run(r["command"], "--id", "a", "--value", "new", "--record", "one", "--actor", "operator")
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertEqual([x["id"] for x in json.loads(run("history").stdout)], ["one", "receipt"])
            # Duplicate in a later secondary effect rolls back the new primary
            # candidate and the first newly constructed secondary record.
            before = path.read_bytes()
            p = run(r["command"], "--id", "a", "--value", "partial", "--record", "two", "--actor", "operator")
            self.assertEqual(json.loads(p.stderr), {"error": "history_exists"})
            self.assertEqual(path.read_bytes(), before)


if __name__ == "__main__": unittest.main()
