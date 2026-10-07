"""Typed computation semantics, normal path loss detection and external behavior."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from air_compiler.computation import INTEGER, TIME, DURATION, POLICY, validate
from air_compiler.mutable_values import valid_value
from air_compiler.profiles import author, generate
from lykoi_controller import Failure
from lykoi_pipeline import contracts, mutable_profile, PipelineController
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.computation_corpus import captures, plan, node, graph
from lykoi_workspace.predicate_corpus import operand

ROOT = Path(__file__).resolve().parents[1]
s = importlib.util.spec_from_file_location("computation_evaluator", ROOT / "benchmark/results/phase5c/R5_103-evaluate.py")
ev = importlib.util.module_from_spec(s); s.loader.exec_module(ev)
CACHE = {}


def prepared():
    if not CACHE:
        r = captures()[0]; x = ev.evaluate(r["candidate"], plan(r))
        assert x["first_blocker"] == "SUCCESS", x.get("terminal", x)
        CACHE.update(record=r, contract=x["formalization"]["contract"])
    return copy.deepcopy(CACHE["record"]), copy.deepcopy(CACHE["contract"])


class ComputationTests(unittest.TestCase):
    def test_lykoi_integer_domain_not_python(self):
        for v in (-(2**63), -1, 0, 2**63-1): self.assertTrue(valid_value(v, INTEGER))
        for v in (True, False, 1.0, "1", None, -(2**63)-1, 2**63): self.assertFalse(valid_value(v, INTEGER))

    def test_five_domains_external_numeric_temporal_atomic_successor(self):
        for r in captures():
            x = ev.evaluate(r["candidate"], plan(r))
            self.assertEqual(x["first_blocker"], "SUCCESS", x.get("terminal", x))
            self.assertEqual(x["external_invocations"], 15)

    def test_graph_rejects_missing_and_dynamic_semantics(self):
        r, c = prepared(); f = contracts.structural(c, "frc")["facts"]
        ref = f["references"]; op = ref["facts"]["operations"][1]
        for edit in ("arity", "operator", "type", "cycle", "overflow", "domain", "unit", "clock", "snapshot", "unbound"):
            g = copy.deepcopy(op["computations"]); n = g["nodes"][0]
            if edit == "arity": n["operands"].pop()
            if edit == "operator": n["operator"] = "multiply"
            if edit == "type": n["operands"][0]["type"] = TIME
            if edit == "cycle": n["operands"][0] = operand("computed", INTEGER, name="new_quantity"); n["depends_on"] = ["new_quantity"]
            if edit == "overflow": g["policy"]["overflow"] = "wrap"
            if edit == "domain": g["policy"]["integer_domain"] = "python_int"
            if edit == "unit": g["nodes"][1]["operator"] = "shift_months"
            if edit == "clock": n["operands"][0] = operand("resource", INTEGER, name="ambient")
            if edit == "snapshot": g["policy"]["snapshot"] = "ambient_latest"
            if edit == "unbound": n.pop("binding")
            with self.assertRaises(Failure): validate(g, ref["types"], r["metric"], {n: p["type"] for n, p in op["parameters"].items()})

    def test_coverage_adequacy_v1_and_reconciliation_material_mutations(self):
        r, c = prepared(); p = contracts.structural(c, "frc"); normal = contracts.faithful_v1(c)["normalized"]
        self.assertEqual(mutable_profile.recover(normal), c)
        for edit in ("operator", "operand", "constant", "domain", "binding", "failure", "unit"):
            bad = copy.deepcopy(normal)
            op = bad["facts"]["atomic_state"]["facts"]["operations"][0]
            n = op["computations"]["nodes"][1]
            if edit == "operator": n["operator"] = "value"
            if edit == "operand": n["operands"][0]["name"] = "wrong"
            if edit == "constant": n["operands"][1]["value"] = 2
            if edit == "domain": op["computations"]["nodes"][0]["operands"][0]["selection"]["entity"] = r["metric"]
            if edit == "binding": n["binding"] = "wrong"
            if edit == "failure": op["computations"]["policy"]["overflow"] = "wrap"
            if edit == "unit": n["operator"] = "shift_utc_seconds"
            with self.assertRaises(Failure): mutable_profile.recover(bad)
            projection = copy.deepcopy(p); projection["facts"] = bad["facts"]
            with self.assertRaises(Failure): contracts.coverage(c, projection)
        b = contracts.bdi(c, p)
        choices = [d for d in b["result"]["decisions"] if d["family"].startswith("computation/")]
        self.assertEqual(len(choices), 4)
        for d in choices:
            bad = copy.deepcopy(b); next(x for x in bad["result"]["decisions"] if x["id"] == d["id"])["authority"] = None
            self.assertEqual(contracts.adequate(c, bad)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")
        candidate = r["candidate"]
        for edit in ("operator", "operand", "constant", "domain", "binding", "failure", "unit"):
            bad = copy.deepcopy(candidate)
            a = next(x for x in bad["rows"] if x["relation"]["parameters"]["facet"] == "atomic_state_semantics")["relation"]["parameters"]["value"]["operations"][0]["computations"]
            n = a["nodes"][1]
            if edit == "operator": n["operator"] = "value"
            if edit == "operand": n["operands"][0]["name"] = "wrong"
            if edit == "constant": n["operands"][1]["value"] = 2
            if edit == "domain": a["nodes"][0]["operands"][0]["selection"]["entity"] = r["metric"]
            if edit == "binding": n["binding"] = "different"
            if edit == "failure": a["policy"]["overflow"] = "wrap"
            if edit == "unit": n["operator"] = "shift_utc_seconds"
            with tempfile.TemporaryDirectory() as tmp:
                ctrl = PipelineController(Path(tmp) / "case.sqlite", PRINCIPALS)
                try:
                    w = Workspace(ctrl, "public", "computation-authority", CREDENTIALS); w.ingest(CREDENTIALS["owner"], candidate["source"])
                    try: w.formalize(ev.producer(bad, "formalizer"))
                    except Failure: continue
                    soi = w.commit_inventory(ev.producer(candidate, "reviewer"))
                    self.assertEqual(ctrl.artifact(w.reconcile(soi))["content"]["outcome"], "DISPUTED")
                finally: ctrl.close()

    def test_backend_boundary_and_stale_state_and_persistence_failure(self):
        r, c = prepared()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "target.py").write_text(generate(author(contracts.faithful_v1(c)["normalized"])), encoding="utf-8")
            store = root / r["path"]
            payload = dict(schema_version=1, records=[], entities={r["metric"]: [dict(id="a", quantity=5, due_at="2024-02-28T12:00:00Z")], r["history"]: []})
            store.write_text(json.dumps(payload), encoding="utf-8")
            probe = '''import target as t,json,sys
op=next(o for o in t.REFERENCE["facts"]["operations"] if o["command"]=="compute")
mode=sys.argv[1]
if mode=="persist":
 def fail(*args): raise OSError("injected")
 t.os.replace=fail
inputs=dict(id="a",adjustment=1,seconds=86400,record="h",successor="b")
try:
 print(json.dumps(t.reference_operation(op,inputs)))
except t.Failure as e:
 print(json.dumps({"error":e.code}));sys.exit(1)
'''
            (root / "probe.py").write_text(probe, encoding="utf-8")
            before = store.read_bytes()
            x = subprocess.run([sys.executable, "probe.py", "persist"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(json.loads(x.stdout), {"error": "persistence_failure"}); self.assertEqual(store.read_bytes(), before)
            # Observation is current operation snapshot, not a compile-time value.
            payload["entities"][r["metric"]][0]["quantity"] = 10
            store.write_text(json.dumps(payload), encoding="utf-8")
            x = subprocess.run([sys.executable, "probe.py", "normal"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(x.returncode, 0, x.stderr); self.assertEqual(json.loads(x.stdout)["quantity"], 11)
            stored = json.loads(store.read_text())["entities"]
            self.assertEqual(stored[r["history"]][0]["ordinal"], 1)
            self.assertEqual(stored[r["metric"]][1]["quantity"], 11)
            # Python accepts True as int and arbitrary-precision integers; reload
            # rejects both, as well as floating integral values, before any effect.
            for value in (True, 1.0, 2**63):
                corrupt = copy.deepcopy(payload); corrupt["entities"][r["metric"]][0]["quantity"] = value
                store.write_text(json.dumps(corrupt), encoding="utf-8"); before = store.read_bytes()
                x = subprocess.run([sys.executable, "probe.py", "normal"], cwd=tmp, capture_output=True, text=True)
                self.assertEqual(json.loads(x.stdout), {"error": "invalid_state"}); self.assertEqual(store.read_bytes(), before)

    def test_external_backend_independence_integer_and_temporal_vectors(self):
        _, c = prepared()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); (root / "target.py").write_text(generate(author(contracts.faithful_v1(c)["normalized"])), encoding="utf-8")
            vectors = []
            for left, right, expected in ((0, 1, 1), (10, -3, 7), (-5, -1, -6), (2**63-2, 1, 2**63-1), (-(2**63)+1, -1, -(2**63)), (2**63-1, 1, None), (-(2**63), -1, None)):
                vectors.append((graph([node("result", "add", [operand("literal", INTEGER, value=left), operand("literal", INTEGER, value=right)])]), expected))
            for instant, seconds, expected in (("2024-02-28T12:00:00Z", 86400, "2024-02-29T12:00:00Z"), ("2024-02-29T12:00:00Z", 86400, "2024-03-01T12:00:00Z"), ("2023-02-28T12:00:00Z", 86400, "2023-03-01T12:00:00Z"), ("2024-01-01T00:00:00.123456Z", -1, "2023-12-31T23:59:59.123456Z"), ("9999-12-31T23:59:59Z", 1, None), ("0001-01-01T00:00:00Z", -1, None), ("2024-01-01T00:00:60Z", 0, None), ("2024-01-01T00:00:00+00:00", 0, None), ("20240101T000000Z", 0, None)):
                vectors.append((graph([node("result", "shift_utc_seconds", [operand("literal", TIME, value=instant), operand("literal", DURATION, value=seconds)], TIME)]), expected))
            (root / "vectors.json").write_text(json.dumps(vectors), encoding="utf-8")
            probe = '''import target as t,json
out=[]
for g,expected in json.load(open("vectors.json")):
 try: out.append(t.computation_evaluate(g,{}, {},{})["result"])
 except t.Failure: out.append(None)
print(json.dumps(out))
'''
            (root / "vectors.py").write_text(probe, encoding="utf-8")
            x = subprocess.run([sys.executable, "vectors.py"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(x.returncode, 0, x.stderr)
            self.assertEqual(json.loads(x.stdout), [expected for _, expected in vectors])

    def test_selection_domain_dependency_and_consumer_authority(self):
        r, c = prepared(); f = contracts.structural(c, "frc")["facts"]
        from air_compiler.references import compose as compose_references
        from air_compiler.atomic_state import compose as compose_atomic
        for edit in ("missing_domain", "wrong_domain", "missing_dependency", "unbound_consumer", "missing_policy", "integer_as_duration"):
            refs, atom = copy.deepcopy(f["references"]["facts"]), copy.deepcopy(f["atomic_state"]["facts"])
            g = atom["operations"][0]["computations"]
            if edit == "missing_domain": g["nodes"][0]["operands"][0]["selection"].pop("entity")
            if edit == "wrong_domain": g["nodes"][0]["operands"][0]["selection"]["entity"] = "ambient"
            if edit == "missing_dependency": g["nodes"][1]["depends_on"] = []
            if edit == "unbound_consumer": atom["operations"][0]["creations"][0]["bindings"]["ordinal"]["source"]["name"] = "missing"
            if edit == "missing_policy": g.pop("policy")
            if edit == "integer_as_duration": refs["operations"][1]["computations"]["nodes"][1]["operands"][1]["type"] = INTEGER
            with self.assertRaises(Failure):
                ri = compose_references(f["ir"], refs); compose_atomic(f["ir"], ri, atom)


if __name__ == "__main__": unittest.main()
