"""Normal-path primary numeric, context actor and atomic composition evidence."""
import copy
import importlib.util
from pathlib import Path
import json
import subprocess
import sys
import tempfile
import unittest

from air_compiler.profiles import author, generate
from lykoi_pipeline import contracts, mutable_profile, PipelineController
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_controller import Failure
from lykoi_workspace.primary_corpus import captures, plan

ROOT = Path(__file__).resolve().parents[1]
s = importlib.util.spec_from_file_location("primary_evaluator", ROOT / "benchmark/results/phase5c/R5_103-evaluate.py")
ev = importlib.util.module_from_spec(s); s.loader.exec_module(ev)
CACHE = {}


def evaluate(r):
    name = r["candidate"]["id"]
    if name not in CACHE:
        CACHE[name] = ev.evaluate(r["candidate"], plan(r))
    return copy.deepcopy(CACHE[name])


class PrimaryInterfaceTests(unittest.TestCase):
    def test_normal_path_five_domains(self):
        for r in captures():
            x = evaluate(r)
            self.assertEqual(x["first_blocker"], "SUCCESS", x.get("terminal", x))

    def test_authority_loss_and_faithful_projection(self):
        r = captures()[0]; x = evaluate(r)
        self.assertEqual(x["first_blocker"], "SUCCESS", x.get("terminal", x))
        c = x["formalization"]["contract"]
        p = contracts.structural(c, "frc")
        v = contracts.faithful_v1(c)["normalized"]
        self.assertEqual(mutable_profile.recover(v), c)
        for change in ("null", "migration", "actor", "successor", "ordinal", "membership"):
            bad = copy.deepcopy(v); f = bad["facts"]
            if change == "null": f["ir"]["facts"]["primary_interfaces"]["integers"][1]["type"]["nullable"] = False
            if change == "migration": f["ir"]["facts"]["primary_interfaces"]["integers"][1]["migration"][0]["value"] = 7
            if change == "actor": f["ir"]["facts"]["primary_interfaces"]["context_inputs"][0]["authority"] = "owner"
            if change == "successor": f["atomic_state"]["facts"]["operations"][0]["creations"][1]["bindings"]["nickname"]["source"]["name"] = "description"
            if change == "ordinal": f["atomic_state"]["facts"]["operations"][0]["computations"]["nodes"][0]["operands"][0]["selection"]["entity"] = r["primary"]
            if change == "membership": f["atomic_state"]["facts"]["operations"][0]["creations"].pop()
            with self.assertRaises(Failure): mutable_profile.recover(bad)
            projection = copy.deepcopy(p); projection["facts"] = f
            with self.assertRaises(Failure): contracts.coverage(c, projection)
        b = contracts.bdi(c, p)
        decisions = [d for d in b["result"]["decisions"] if d["family"].startswith("primary/")]
        self.assertEqual(len(decisions), 2)
        for d in decisions:
            bad = copy.deepcopy(b); next(a for a in bad["result"]["decisions"] if a["id"] == d["id"])["authority"] = None
            self.assertEqual(contracts.adequate(c, bad)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")
        candidate = copy.deepcopy(r["candidate"])
        facet = next(o for o in candidate["rows"] if o["relation"]["parameters"].get("facet") == "primary_interfaces")
        facet["relation"]["parameters"]["value"]["integers"][1]["migration"][0]["value"] = 7
        with tempfile.TemporaryDirectory() as tmp:
            ctrl = PipelineController(Path(tmp) / "case.sqlite", PRINCIPALS)
            try:
                w = Workspace(ctrl, "public", "primary-authority", CREDENTIALS)
                w.ingest(CREDENTIALS["owner"], candidate["source"])
                w.formalize(ev.producer(candidate, "formalizer"))
                soi = w.commit_inventory(ev.producer(r["candidate"], "reviewer"))
                self.assertEqual(ctrl.artifact(w.reconcile(soi))["content"]["outcome"], "DISPUTED")
            finally:
                ctrl.close()

    def test_persistence_failure_and_host_missing_actor_preserve_state(self):
        r = captures()[0]; x = evaluate(r)
        self.assertEqual(x["first_blocker"], "SUCCESS", x.get("terminal", x))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "target.py").write_text(generate(author(contracts.faithful_v1(x["formalization"]["contract"])["normalized"])), encoding="utf-8")
            path = root / r["path"]
            path.write_text(json.dumps(dict(schema_version=2, records=[r["record"]], entities={e["name"]: e["initial"] for e in r["references"]["entities"]})), encoding="utf-8")
            probe = '''import target as t,sys,json
if sys.argv[1]=="persist":
 def fail(*a): raise OSError("injected")
 t.os.replace=fail
 op=t.REFERENCE["facts"]["operations"][0]
 call=lambda:t.reference_operation(op,dict(id="a",adjustment=1,actor="operator",record="h",successor="b"))
else:
 b=next(b for b in t.SPEC["behaviors"] if b["kind"]=="update")
 call=lambda:t.execute(b,{b["lookup"]["input"]:"a"})
try: call()
except t.Failure as e: print(json.dumps({"error":e.code}))
'''
            (root / "probe.py").write_text(probe, encoding="utf-8")
            before = path.read_bytes()
            for mode, error in (("persist", "persistence_failure"), ("actor", "actor_required")):
                run = subprocess.run([sys.executable, "probe.py", mode], cwd=tmp, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(json.loads(run.stdout), {"error": error})
                self.assertEqual(path.read_bytes(), before)
            original = json.loads(before)
            for value in (True, 1.0, 2**63, -(2**63)-1):
                bad = copy.deepcopy(original); bad["records"][0]["quantity"] = value
                path.write_text(json.dumps(bad), encoding="utf-8"); corrupt = path.read_bytes()
                run = subprocess.run([sys.executable, "probe.py", "persist"], cwd=tmp, capture_output=True, text=True)
                self.assertEqual(json.loads(run.stdout), {"error": "invalid_state"})
                self.assertEqual(path.read_bytes(), corrupt)


if __name__ == "__main__": unittest.main()
