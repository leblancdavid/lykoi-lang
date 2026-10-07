"""Nominal bindings, integrity composition, semantic preservation and external CLI."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from air_compiler.profiles import author, generate
from air_compiler.references import compose, identity, validate_condition
from lykoi_controller import Failure
from lykoi_pipeline import contracts, mutable_profile, PipelineController
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.reference_corpus import captures, plan, extent, reach, sequence
from lykoi_workspace.predicate_corpus import operand, compare, group

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("reference_evaluator", ROOT / "benchmark/results/phase5c/R5_103-evaluate.py")
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
CACHE = {}


def prepared():
    if not CACHE:
        r = captures()[0]
        result = ev.evaluate(r["candidate"], plan(r))
        assert result["first_blocker"] == "SUCCESS", result.get("terminal", result)
        CACHE.update(record=r, result=result, contract=result["formalization"]["contract"])
    return copy.deepcopy(CACHE["record"]), copy.deepcopy(CACHE["contract"])


class ReferenceTests(unittest.TestCase):
    def test_normal_reference_pipeline_external_write_reload_integrity(self):
        r, c = prepared()
        p = contracts.structural(c, "frc"); contracts.coverage(c, p)
        self.assertIn("references", p["facts"])
        self.assertEqual(contracts.adequate(c, contracts.bdi(c, p))["outcome"], "ADEQUATE")
        normal = contracts.faithful_v1(c)["normalized"]
        self.assertEqual(mutable_profile.recover(normal), c)
        self.assertEqual(generate(author(normal)), generate(author(normal)))
        self.assertGreaterEqual(CACHE["result"]["external_invocations"], 30)

    def test_nominal_identity_substitution_and_implicit_bindings_rejected(self):
        _, c = prepared()
        p = contracts.structural(c, "frc")
        f, ir = p["facts"]["mutable"]["reference_semantics"], p["facts"]["ir"]
        bad = copy.deepcopy(f)
        op = next(o for o in bad["operations"] if o["command"] == "replace-owner")
        op["parameters"]["value"]["type"] = identity("Order")
        with self.assertRaises(Failure): compose(ir, bad)
        bad = copy.deepcopy(f); bad["references"][0]["target"] = "Unknown"
        with self.assertRaises(Failure): compose(ir, bad)
        tree = copy.deepcopy(f["guards"][0]["predicate"])
        tree["selection"]["binding"] = "primary"
        with self.assertRaises(Failure): validate_condition(tree, p["facts"]["references"]["types"], {"primary": "Order"}, {"id": identity("Order")})
        tree = compare(operand("field", identity("Customer"), name="implicit.id"), operand("parameter", identity("Customer"), name="owner"))
        with self.assertRaises(Failure): validate_condition(tree, p["facts"]["references"]["types"], {}, {"owner": identity("Customer")})

    def test_coverage_v1_and_bdi_adequacy_preserve_integrity(self):
        _, c = prepared()
        p = contracts.structural(c, "frc")
        for name in ("types", "checks", "facts"):
            bad = copy.deepcopy(p); bad["facts"]["references"].pop(name)
            with self.assertRaises(Failure): contracts.coverage(c, bad)
            normal = contracts.faithful_v1(c)["normalized"]; normal["facts"]["references"].pop(name)
            with self.assertRaises(Failure): mutable_profile.recover(normal)
        b = contracts.bdi(c, p)
        selected = [d for d in b["result"]["decisions"] if d["family"].startswith("reference/")]
        self.assertEqual(len(selected), 6)
        for d in selected:
            bad = copy.deepcopy(b)
            next(x for x in bad["result"]["decisions"] if x["id"] == d["id"])["authority"] = None
            self.assertEqual(contracts.adequate(c, bad)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")

    def test_reconciliation_material_target_policy_domain_quantifier_and_cycle_loss(self):
        r = captures()[0]["candidate"]
        index = next(i for i, o in enumerate(r["rows"]) if o["relation"]["parameters"]["facet"] == "reference_semantics")
        for edit in ("target", "existence", "deletion", "quantifier", "predicate", "domain", "cycle"):
            bad = copy.deepcopy(r)
            f = bad["rows"][index]["relation"]["parameters"]["value"]
            if edit == "target": f["references"][0]["target"] = "Order"
            if edit == "existence": f["references"][0]["existence"] = dict(policy="unchecked", error=None)
            if edit == "deletion": f["references"][0]["deletion"] = dict(policy="permit", error=None)
            if edit == "quantifier": f["guards"][0]["predicate"]["relation"] = "ge"; f["guards"][0]["predicate"]["value"] = 1
            if edit == "predicate": f["guards"][0]["predicate"]["selection"]["predicate"]["children"][1] = f["guards"][0]["predicate"]["selection"]["predicate"]["children"][1]["child"]
            if edit == "domain": f["guards"][0]["predicate"]["selection"]["entity"] = "Order"
            if edit == "cycle": next(o for o in f["operations"] if o["command"] == "add-parent")["guards"] = []
            with tempfile.TemporaryDirectory() as tmp:
                ctrl = PipelineController(Path(tmp) / "case.sqlite", PRINCIPALS)
                try:
                    w = Workspace(ctrl, "public", "reference-authority", CREDENTIALS)
                    w.ingest(CREDENTIALS["owner"], r["source"])
                    w.formalize(ev.producer(bad, "formalizer"))
                    soi = w.commit_inventory(ev.producer(r, "reviewer"))
                    self.assertEqual(ctrl.artifact(w.reconcile(soi))["content"]["outcome"], "DISPUTED")
                finally: ctrl.close()

    def test_absent_observable_authority_is_not_invented(self):
        _, c = prepared()
        f = contracts.structural(c, "frc")["facts"]
        for policy in ("existence", "deletion"):
            bad = copy.deepcopy(f["mutable"]["reference_semantics"])
            bad["references"][0][policy]["error"] = None
            with self.assertRaises(Failure): compose(f["ir"], bad)
        bad = copy.deepcopy(f["mutable"]["reference_semantics"])
        bad["references"][0]["deletion"]["policy"] = "cascade"
        with self.assertRaises(Failure): compose(f["ir"], bad)
        bad = copy.deepcopy(f["mutable"]["reference_semantics"])
        for ref in bad["references"]:
            if ref["target"] == "Customer": ref["deletion"] = dict(policy="unavailable", error=None)
        with self.assertRaises(Failure): compose(f["ir"], bad)
        bad["operations"] = [op for op in bad["operations"] if op["command"] != "delete-target"]
        self.assertEqual(compose(f["ir"], bad)["version"], "persistent-references-1")

    def test_exists_none_all_exact_cardinality_and_finite_scope(self):
        _, c = prepared()
        code = generate(author(contracts.faithful_v1(c)["normalized"]))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(code, encoding="utf-8")
            s = importlib.util.spec_from_file_location("reference_target", target)
            m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
            ti = identity("Customer")
            active_type = dict(type="boolean", domain=[], nullable=False)
            active = compare(operand("field", active_type, name="related.active"), operand("literal", active_type, value=True))
            domain = compare(operand("field", ti, name="related.id"), operand("field", sequence(ti), name="primary.member_ids"), member=True)
            exists = extent("Customer", group("and", domain, active), "ge", 1)
            none = extent("Customer", group("and", domain, active))
            all_ = extent("Customer", group("and", domain, group("not", active)))
            rows = {"Customer": [dict(id="a", active=True), dict(id="b", active=False), dict(id="unrelated", active=False)]}
            for members, truth in (([], (False, True, True)), (["a"], (True, False, True)), (["a", "b"], (True, False, False)), (["b"], (False, True, False))):
                bindings = {"primary": {"member_ids": members}}
                self.assertEqual(tuple(m.reference_condition(t, rows, bindings, {}) for t in (exists, none, all_)), truth)
            exact = extent("Customer", domain, "eq", 2)
            self.assertTrue(m.reference_condition(exact, rows, {"primary": {"member_ids": ["a", "b"]}}, {}))

    def test_reachability_long_path_nonreflexive_and_multi_domain(self):
        # Local-predicate unrolls with fixed depth k cannot distinguish chains
        # longer than k. Explicit reachability observes any finite nonempty path.
        for r in (captures()[1], captures()[5]):
            # Reuse the qualified compiler backend; domain-specific schemas do not
            # dispatch by project/category names.
            result = ev.evaluate(r["candidate"], plan(r))
            self.assertEqual(result["first_blocker"], "SUCCESS", result.get("terminal"))
            c = result["formalization"]["contract"]
            with tempfile.TemporaryDirectory() as tmp:
                target = Path(tmp) / "target.py"; target.write_text(generate(author(contracts.faithful_v1(c)["normalized"])), encoding="utf-8")
                s = importlib.util.spec_from_file_location("reach_target", target); m = importlib.util.module_from_spec(s); s.loader.exec_module(m)
                e = r["primary"]; t = identity(e)
                rows = {e: [dict(id=str(i), parent_ids=[str(i + 1)] if i < 80 else []) for i in range(81)]}
                tree = reach(e, "parent_ids", operand("literal", t, value="0"), operand("literal", t, value="80"))
                self.assertTrue(m.reference_condition(tree, rows, {}, {}))
                tree["target"]["value"] = "0"
                self.assertFalse(m.reference_condition(tree, rows, {}, {}))
                rows[e][-1]["parent_ids"] = ["0"]
                self.assertTrue(m.reference_condition(tree, rows, {}, {}))

    def test_store_reservation_rejection_and_failed_commit_preserve_bytes(self):
        r, c = prepared()
        code = generate(author(contracts.faithful_v1(c)["normalized"]))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(code, encoding="utf-8")
            payload = plan(r)["cases"][0]["initial_files"][0]["json"]
            path = Path(tmp) / r["path"]; path.write_text(json.dumps(payload), encoding="utf-8")
            before = path.read_bytes()
            lock = Path(str(path) + ".operation-lock"); lock.write_text("", encoding="utf-8")
            p = subprocess.run([sys.executable, str(target), "replace-owner", "--id", "a", "--value", "owner"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(json.loads(p.stderr), {"error": "store_busy"})
            self.assertEqual(path.read_bytes(), before); lock.unlink()
            probe = "import target,os\ndef fail(*a): raise OSError('injected')\ntarget.os.replace=fail\nraise SystemExit(target.reference_main(target.main))\n"
            (Path(tmp) / "probe.py").write_text(probe, encoding="utf-8")
            p = subprocess.run([sys.executable, "probe.py", "replace-owner", "--id", "a", "--value", "m1"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(json.loads(p.stderr), {"error": "persistence_failure"})
            self.assertEqual(path.read_bytes(), before)
            self.assertFalse(lock.exists())

    def test_migration_reference_authority_rejection_retry_and_reload(self):
        r, c = prepared()
        # Only an explicitly declared empty-value migration may repair the owner.
        for o in c["obligations"]:
            if o["relation"]["parameters"].get("facet") == "reference_semantics":
                o["relation"]["parameters"]["value"]["references"][0]["migration"] = dict(when="missing_or_empty", value="owner")
        code = generate(author(contracts.faithful_v1(c)["normalized"]))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(code, encoding="utf-8")
            payload = plan(r)["cases"][0]["initial_files"][0]["json"]
            payload["records"][0]["owner_id"] = ""
            payload["records"][1]["owner_id"] = "unknown"
            path = Path(tmp) / r["path"]; path.write_text(json.dumps(payload), encoding="utf-8")
            before = path.read_bytes()
            def run(*argv):
                return subprocess.run([sys.executable, str(target), *argv], cwd=tmp, capture_output=True, text=True)
            p = run("migrate")
            self.assertEqual(json.loads(p.stderr), {"error": "missing_target"}); self.assertEqual(path.read_bytes(), before)
            p = run("create-target", "--id", "unknown", "--active", "true")
            self.assertEqual(p.returncode, 0, p.stderr)
            p = run("migrate"); self.assertEqual(json.loads(p.stdout), {"migrated": 3})
            rows = json.loads(run("list").stdout)
            self.assertEqual([x["owner_id"] for x in rows], ["owner", "unknown", "owner"])
            self.assertEqual(json.loads(run("migrate").stdout), {"migrated": 0})

    def test_explicit_permit_and_stale_same_value_write_rejection(self):
        r, c = prepared()
        for o in c["obligations"]:
            if o["relation"]["parameters"].get("facet") == "reference_semantics":
                for ref in o["relation"]["parameters"]["value"]["references"]:
                    if ref["target"] == "Customer": ref["deletion"] = dict(policy="permit", error=None)
        code = generate(author(contracts.faithful_v1(c)["normalized"]))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(code, encoding="utf-8")
            payload = plan(r)["cases"][0]["initial_files"][0]["json"]
            path = Path(tmp) / r["path"]; path.write_text(json.dumps(payload), encoding="utf-8")
            def run(*argv): return subprocess.run([sys.executable, str(target), *argv], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(run("delete-target", "--id", "owner").returncode, 0)
            before = path.read_bytes()
            for argv in (("replace-owner", "--id", "a", "--value", "owner"), ("advance", "--id", "a")):
                p = run(*argv)
                self.assertEqual(json.loads(p.stderr), {"error": "missing_target"}); self.assertEqual(path.read_bytes(), before)

    def test_reference_collections_allow_duplicates_preserve_order_and_remove_stably(self):
        r, c = prepared()
        for o in c["obligations"]:
            p = o["relation"]["parameters"]
            if p.get("facet") == "collections":
                next(x for x in p["value"] if x["name"] == "member_ids")["duplicates"] = "allow"
            if p.get("facet") == "reference_semantics":
                f = p["value"]
                next(x for x in f["operations"] if x["command"] == "add-member")["changes"][0]["operation"] = "append"
                # Domain operand retains the exact collection duplicate policy.
                f["guards"][0]["predicate"]["selection"]["predicate"]["children"][0]["right"]["type"]["duplicates"] = "allow"
        code = generate(author(contracts.faithful_v1(c)["normalized"]))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(code, encoding="utf-8")
            path = Path(tmp) / r["path"]; path.write_text(json.dumps(plan(r)["cases"][0]["initial_files"][0]["json"]), encoding="utf-8")
            def run(command, value):
                p = subprocess.run([sys.executable, str(target), command, "--id", "a", "--value", value], cwd=tmp, capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stderr)
                return json.loads(p.stdout)["member_ids"]
            self.assertEqual(run("add-member", "m1"), ["m1"])
            self.assertEqual(run("add-member", "m2"), ["m1", "m2"])
            self.assertEqual(run("add-member", "m1"), ["m1", "m2", "m1"])
            self.assertEqual(run("remove-member", "m1"), ["m2"])


if __name__ == "__main__": unittest.main()
