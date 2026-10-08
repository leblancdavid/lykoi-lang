"""R5.113 normal path, permission authority, image graphs and failure frames."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from air_compiler.profiles import author, generate
from lykoi_pipeline import contracts, mutable_profile, PipelineController
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.authorization_corpus import captures, plan
from lykoi_controller import Failure
from air_compiler.computation import validate as validate_graph, INTEGER, DURATION
from lykoi_workspace.authorization_corpus import CONVERSION
from lykoi_workspace.computation_corpus import graph, node
from lykoi_workspace.predicate_corpus import operand

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("authorization_evaluator", ROOT / "benchmark/results/phase5c/R5_103-evaluate.py")
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
CACHE = {}


def evaluate(r):
    name = r["candidate"]["id"]
    if name not in CACHE: CACHE[name] = ev.evaluate(r["candidate"], plan(r))
    return copy.deepcopy(CACHE[name])


class AuthorizationCompositionTests(unittest.TestCase):
    def test_conversion_refinement_boundaries_and_explicit_alternative(self):
        from air_compiler.mutable_values import compose
        from air_compiler.references import compose as references
        from air_compiler.atomic_state import compose as atomic
        from air_compiler.authorization import compose as authorization
        from air_compiler.profiles import generate_mutable
        r = captures()[0]
        base = mutable_profile.scalar.lower({**r["scalar"], "storage": {**r["scalar"]["storage"], "version": 1}})
        ir = compose(base, {k: v for k, v in r["mutable"].items() if k not in ("atomic_state_semantics", "authorization_semantics")})
        ri = references(ir, r["references"])
        facts = copy.deepcopy(r["mutable"]["atomic_state_semantics"])
        effect = facts["operations"][0]["creations"][0]
        effect["when"] = None
        for field, value in (("subject", "a"), ("quantity", 10)):
            source = effect["bindings"][field]["source"]
            source["alternative"] = dict(kind="literal", type=source["type"], value=value)
        ai = atomic(ir, ri, facts); au = authorization(ir, ri, r["mutable"]["authorization_semantics"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target = root / "target.py"
            target.write_text(generate_mutable(ir, [], ri, ai, au), encoding="utf-8")
            spec = importlib.util.spec_from_file_location("duration_probe", target)
            mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            scale = node("seconds", "days_to_seconds", [operand("parameter", INTEGER, name="days")], DURATION)
            scale["conversion"] = copy.deepcopy(CONVERSION)
            g = graph([scale]); validate_graph(g, ri["types"], r["primary"], dict(days=INTEGER))
            limit = (2**63 - 1) // 86400
            for value in (0, 1, -1, limit, -limit):
                self.assertEqual(mod.computation_evaluate(g, {}, {}, dict(days=value))["seconds"], value * 86400)
            for value in (limit + 1, -limit - 1, True, 1.0, "1", None):
                with self.assertRaises(mod.Failure): mod.computation_evaluate(g, {}, {}, dict(days=value))
            nullable = dict(type="integer", domain=[], nullable=True)
            refine = node("integer", "refine_integer", [operand("parameter", nullable, name="value")]); refine["null"] = dict(policy="literal", value=7)
            fallback = graph([refine]); validate_graph(fallback, ri["types"], r["primary"], dict(value=nullable))
            self.assertEqual(mod.computation_evaluate(fallback, {}, {}, dict(value=None))["integer"], 7)
            with self.assertRaises(mod.Failure): mod.computation_evaluate(fallback, {}, {}, {})
            refine["null"] = dict(policy="reject")
            with self.assertRaises(mod.Failure): mod.computation_evaluate(fallback, {}, {}, dict(value=None))
            related = ri["facts"]["operations"][0]
            defaulted = mod.reference_inputs(related, dict(id="a", adjustment=0, actor="operator", record="h", successor="b", successor_history="sh"))
            present = dict(kind="present", result_type="boolean", operand=operand("parameter", {"type": "timestamp", "domain": [], "nullable": True}, name="start"))
            self.assertFalse(mod.predicate_eval(present, inputs=defaulted))
            self.assertEqual(defaulted["start"], "2020-01-01T00:00:00Z")
            from air_compiler.computation import bound, TIME
            bound(operand("computed", TIME, name="instant"), dict(instant=TIME), {**TIME, "nullable": True})
            with self.assertRaises(Failure): bound(operand("computed", {**TIME, "nullable": True}, name="instant"), dict(instant={**TIME, "nullable": True}), TIME)
            (root / r["path"]).write_text(json.dumps(dict(schema_version=2, records=[r["record"]], entities=r["entities"])), encoding="utf-8")
            from lykoi_workspace.authorization_corpus import args
            run = subprocess.run([sys.executable, "target.py", *args(0)], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(run.returncode, 0, run.stderr)
            stored = json.loads((root / r["path"]).read_text(encoding="utf-8"))
            self.assertEqual(len(stored["records"]), 1)
            self.assertEqual(stored["entities"][r["history"]], [dict(id="sh", subject="a", actor="operator", ordinal=2, quantity=10)])

    def test_normal_path_five_domains(self):
        for r in captures():
            x = evaluate(r)
            self.assertEqual(x["first_blocker"], "SUCCESS", x.get("terminal", x))

    def test_reconciliation_projection_and_decision_authority(self):
        r = captures()[1]; x = evaluate(r)
        self.assertEqual(x["first_blocker"], "SUCCESS", x.get("terminal", x))
        contract = x["formalization"]["contract"]
        projection = contracts.structural(contract, "frc")
        normal = contracts.faithful_v1(contract)["normalized"]
        self.assertEqual(mutable_profile.recover(normal), contract)
        decisions = contracts.bdi(contract, projection)
        permission = [d for d in decisions["result"]["decisions"] if d["family"].startswith("authorization/")]
        self.assertEqual(len(permission), 28)
        for d in permission:
            bad = copy.deepcopy(decisions)
            next(v for v in bad["result"]["decisions"] if v["id"] == d["id"])["authority"] = None
            self.assertEqual(contracts.adequate(contract, bad)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")
        for change in ("actor", "owner", "guard", "error", "condition", "image", "scale", "fallback"):
            candidate = copy.deepcopy(r["candidate"])
            facets = {o["relation"]["parameters"].get("facet"): o["relation"]["parameters"].get("value") for o in candidate["rows"]}
            auth = facets["authorization_semantics"]["operations"][0]
            effects = facets["atomic_state_semantics"]["operations"][0]["creations"]
            if change == "actor": auth["actor"]["source"] = "trusted_context"; auth["actor"]["context"] = "forged"
            if change == "owner": auth["predicate"] = auth["predicate"]["children"][0]
            if change == "guard": facets["authorization_semantics"]["operations"].pop(0)
            if change == "error": auth["error"] = "wrong_error"
            if change == "condition": effects[0]["when"] = None
            if change == "image": effects[0]["bindings"]["subject"]["source"]["field"] = "owner_id"
            if change == "scale": effects[2]["computations"]["nodes"][1]["conversion"]["seconds_per_day"] = 3600
            if change == "fallback": effects[2]["computations"]["nodes"][0]["null"] = dict(policy="literal", value=0)
            with tempfile.TemporaryDirectory() as tmp:
                ctrl = PipelineController(Path(tmp) / "case.sqlite", PRINCIPALS)
                try:
                    w = Workspace(ctrl, "public", "permission-authority", CREDENTIALS)
                    w.ingest(CREDENTIALS["owner"], candidate["source"])
                    try: w.formalize(ev.producer(candidate, "formalizer"))
                    except Failure: continue
                    soi = w.commit_inventory(ev.producer(r["candidate"], "reviewer"))
                    self.assertEqual(ctrl.artifact(w.reconcile(soi))["content"]["outcome"], "DISPUTED", change)
                finally: ctrl.close()
        for change in ("missing", "cycle", "entity", "conditional"):
            bad = copy.deepcopy(contract)
            facet = next(o for o in bad["obligations"] if o["relation"]["parameters"].get("facet") == "atomic_state_semantics")
            effects = facet["relation"]["parameters"]["value"]["operations"][0]["creations"]
            if change == "missing": effects[0]["depends_on"] = []
            if change == "cycle":
                effects[2]["bindings"]["id"]["source"] = dict(kind="created", type=effects[2]["bindings"]["id"]["source"]["type"], effect="successor_history", entity=r["history"], field="subject", alternative=None)
                effects[2]["depends_on"] = ["successor_history"]
            if change == "entity": effects[0]["bindings"]["subject"]["source"]["entity"] = r["history"]
            if change == "conditional": effects[0]["when"] = None
            self.assertTrue(contracts.structural(bad, "frc")["unsupported"], change)
        bad = copy.deepcopy(normal); bad["facts"]["authorization"]["facts"]["operations"] = []
        with self.assertRaises(Failure): mutable_profile.recover(bad)
        altered = copy.deepcopy(projection); altered["facts"]["authorization"]["facts"]["operations"] = []
        with self.assertRaises(Failure): contracts.coverage(contract, altered)

    def test_trusted_host_stale_state_and_atomic_failure(self):
        r = captures()[1]; x = evaluate(r)
        self.assertEqual(x["first_blocker"], "SUCCESS", x.get("terminal", x))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "target.py").write_text(generate(author(contracts.faithful_v1(x["formalization"]["contract"])["normalized"])), encoding="utf-8")
            path = root / r["path"]
            initial = dict(schema_version=2, records=[r["record"]], entities=r["entities"])
            probe = '''import target as t,sys,json,copy
op=next(o for o in t.REFERENCE["facts"]["operations"] if o["command"]=="trusted-adjust")
inputs=dict(id="a",adjustment=1,record="h",successor="b",successor_history="sh")
ctx=dict(source="controlled_host",actor="operator")
mode=sys.argv[1]
if mode=="forge": inputs["actor"]="other"
if mode=="source": ctx["source"]="cli"
if mode=="wrong_role": ctx["actor"]="viewer"
if mode=="owner": ctx["actor"]="other"
if mode=="persist":
 def fail(*a): raise OSError("injected")
 t.os.replace=fail
if mode=="stale":
 original=t.reference_rows; calls=[0]
 def stale():
  rows=original(); calls[0]+=1
  if calls[0]>1: rows[op["entity"]][0]["owner_id"]="other"
  return rows
 t.reference_rows=stale
try: print(json.dumps(t.reference_operation(op,inputs,execution_context=ctx)))
except t.Failure as e: print(json.dumps({"error":e.code}))
'''
            (root / "probe.py").write_text(probe, encoding="utf-8")
            for mode, error in (("forge", "invalid_actor"), ("source", "invalid_actor"), ("wrong_role", "permission_denied"), ("owner", "permission_denied"), ("stale", "permission_denied"), ("persist", "persistence_failure"), ("success", None)):
                path.write_text(json.dumps(initial), encoding="utf-8"); before = path.read_bytes()
                run = subprocess.run([sys.executable, "probe.py", mode], cwd=tmp, capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                response = json.loads(run.stdout)
                if error:
                    self.assertEqual(response, {"error": error}, mode)
                    self.assertEqual(path.read_bytes(), before, mode)
                else:
                    self.assertEqual(response["quantity"], 11)
                    persisted = json.loads(path.read_text(encoding="utf-8"))
                    self.assertEqual(len(persisted["records"]), 2)
                    self.assertEqual(len(persisted["entities"][r["history"]]), 2)


if __name__ == "__main__": unittest.main()
