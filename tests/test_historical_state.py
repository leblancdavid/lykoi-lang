"""R5.114 normal authority path, cross-version persistence and external host evidence."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

from air_compiler.profiles import author, generate
from lykoi_pipeline import contracts, mutable_profile, PipelineController
from lykoi_pipeline.pipeline import classify_observations, external_execute
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.historical_corpus import captures, plan
from lykoi_controller import Failure

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("historical_evaluator", ROOT / "benchmark/results/phase5c/R5_103-evaluate.py")
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
CACHE = {}


def evaluate(r):
    name = r["candidate"]["id"]
    if name not in CACHE: CACHE[name] = ev.evaluate(r["candidate"], plan(r))
    return copy.deepcopy(CACHE[name])


class HistoricalStateTests(unittest.TestCase):
    def test_normal_multidomain_migration_and_host_path(self):
        for r in captures():
            x = evaluate(r)
            if r["candidate"]["question"]:
                self.assertEqual(x["first_blocker"], "FORMALIZATION")
                self.assertEqual(x["native"], "DISPUTED")
                self.assertTrue(all(x["stages"][s] == "NOT_REACHED" for s in ev.STAGES[1:]))
                continue
            self.assertEqual(x["first_blocker"], "SUCCESS", x.get("terminal", x))
            verification = next(a["content"] for a in x["audit"]["artifacts"].values() if a["type"] == "verification")
            binding = verification["bundle"]["trusted_context"]
            self.assertEqual(binding["target_sha256"], next(a["content"]["target_sha256"] for a in x["audit"]["artifacts"].values() if a["type"] == "target"))
            self.assertTrue(binding["what_seal"] and binding["adapter_sha256"])
            observed = [s for c in verification["cases"] for s in c["steps"] if "execution" in s]
            self.assertTrue(any(s["returncode"] == 0 for s in observed))
            for s in observed:
                self.assertTrue(s["passed"])
                if s["returncode"] == 1:
                    self.assertTrue(all(v["before"] == v["after"] for v in s["durable_sha256"].values()))

    def test_authority_reconciliation_coverage_bdi_v1(self):
        r = captures()[1]; x = evaluate(r)
        self.assertEqual(x["first_blocker"], "SUCCESS", x.get("terminal"))
        contract = x["formalization"]["contract"]
        v1 = contracts.faithful_v1(contract)["normalized"]
        self.assertEqual(mutable_profile.recover(v1), contract)
        projection = contracts.structural(contract, "frc")
        bad = copy.deepcopy(projection); bad["facts"]["references"]["historical"]["steps"] = []
        with self.assertRaises(Failure): contracts.coverage(contract, bad)
        decisions = contracts.bdi(contract, projection)
        historical = [d for d in decisions["result"]["decisions"] if d["family"].startswith("historical/")]
        self.assertEqual(len(historical), 4)
        for decision in historical:
            bad = copy.deepcopy(decisions)
            next(d for d in bad["result"]["decisions"] if d["id"] == decision["id"])["authority"] = None
            self.assertEqual(contracts.adequate(contract, bad)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")
        for mode in ("default", "omit", "nominal", "future"):
            candidate = copy.deepcopy(r["candidate"])
            facet = next(o for o in candidate["rows"] if o["id"].endswith("/historical_state_semantics"))["relation"]["parameters"]["value"]
            field = facet["steps"][0]["entities"][0]["add_fields"][0]
            if mode == "default": field["source"] = dict(kind="literal", type=field["source"]["type"], value="viewer")
            if mode == "omit": facet["steps"][0]["entities"].pop(0)
            if mode == "nominal": facet["steps"][0]["entities"][1]["add_fields"][0]["source"]["type"]["entity"] = "WrongEntity"
            if mode == "future": field["source"]["name"] = "role"
            with tempfile.TemporaryDirectory() as tmp:
                c = PipelineController(Path(tmp) / "case.sqlite", PRINCIPALS)
                try:
                    w = Workspace(c, "public", "history-authority", CREDENTIALS)
                    w.ingest(CREDENTIALS["owner"], candidate["source"])
                    w.formalize(ev.producer(candidate, "formalizer"))
                    soi = w.commit_inventory(ev.producer(r["candidate"], "reviewer"))
                    self.assertEqual(c.artifact(w.reconcile(soi))["content"]["outcome"], "DISPUTED")
                finally: c.close()
        bad = copy.deepcopy(v1); bad["facts"]["references"]["historical"]["steps"] = []
        with self.assertRaises(Failure): mutable_profile.recover(bad)

    def test_migration_rollback_and_overflow(self):
        r = captures()[0]; x = evaluate(r)
        self.assertEqual(x["first_blocker"], "SUCCESS", x.get("terminal"))
        source = generate(author(contracts.faithful_v1(x["formalization"]["contract"])["normalized"]))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); target = root / "target.py"
            target.write_text(source, encoding="utf-8")
            spec = importlib.util.spec_from_file_location("migration_failure", target)
            mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            path = root / r["path"]
            store = next(c for c in mod.SPEC["capabilities"] if c["kind"] == "json_file")
            store["path"] = str(path)
            initial = copy.deepcopy(plan(r)["cases"][1]["initial_files"][0]["json"])
            for mode in ("overflow", "replace_failure", "second_record_invalid"):
                old = copy.deepcopy(initial)
                if mode == "overflow": old["entities"][r["entity"]][0]["amount"] = 2**63 - 1
                if mode == "second_record_invalid": old["entities"][r["entity"]].append({**old["entities"][r["entity"]][0], "id": "second", "amount": "bad"})
                path.write_text(json.dumps(old), encoding="utf-8"); before = path.read_bytes()
                original = mod.os.replace
                if mode == "replace_failure":
                    def fail(*args): raise OSError("injected replacement failure")
                    mod.os.replace = fail
                try:
                    with self.assertRaises(mod.Failure) as failure: mod.migrate()
                    self.assertEqual(failure.exception.code, "persistence_failure" if mode == "replace_failure" else "computation_failed" if mode == "overflow" else "invalid_state")
                    self.assertEqual(path.read_bytes(), before)
                    self.assertEqual(sorted(p.name for p in root.iterdir() if p.is_file()), sorted(["target.py", r["path"]]))
                finally: mod.os.replace = original

    def test_external_failure_is_not_target_self_certification(self):
        r = captures()[1]; p = plan(r); x = evaluate(r)
        self.assertEqual(x["first_blocker"], "SUCCESS", x.get("terminal"))
        verification = next(a["content"] for a in x["audit"]["artifacts"].values() if a["type"] == "verification")
        observed = copy.deepcopy(verification["cases"])
        forged = next(s for c in observed for s in c["steps"] if "execution" in s)
        forged["execution"]["execution_context"]["actor"] = "operator"
        with self.assertRaises(Failure): classify_observations(p, observed)
        wrong = 'print("BEHAVIORALLY_VERIFIED")\n'
        outcome, observations = external_execute(wrong, p)
        self.assertNotEqual(outcome, "BEHAVIORALLY_VERIFIED")
        observed = copy.deepcopy(verification["cases"])
        forged = observed[0]["steps"][0]; forged["stdout"] = '{"success": true}'; forged["passed"] = True
        with self.assertRaises(Failure): classify_observations(p, observed)


if __name__ == "__main__": unittest.main()
