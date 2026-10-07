"""Typed trees, source authority and normal external predicate composition."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

from air_compiler.predicates import validate, canonical_meaning
from air_compiler.predicate_runtime import predicate_eval
from air_compiler.profiles import author, generate
from lykoi_controller import Failure
from lykoi_pipeline import contracts, mutable_profile, PipelineController
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.predicate_corpus import captures, plan, operand, compare, group, unary
from lykoi_workspace.query_schema import validate_output

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("predicate_evaluator", ROOT / "benchmark/results/phase5c/R5_103-evaluate.py")
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
CACHE = {}


def prepared():
    if not CACHE:
        r = captures()[0]
        x = ev.evaluate(r["candidate"], plan(r))
        assert x["first_blocker"] == "SUCCESS", x.get("terminal", x)
        CACHE.update(record=r, contract=x["formalization"]["contract"], result=x)
    return copy.deepcopy(CACHE["record"]), copy.deepcopy(CACHE["contract"])


def query(c, command):
    return next(o["relation"]["parameters"]["value"] for o in c["obligations"] if o["relation"]["parameters"].get("query") == command and o["relation"]["parameters"]["facet"] == "predicate")


def mutations():
    r = captures()[0]["candidate"]
    index = next(i for i, o in enumerate(r["rows"]) if o["relation"]["parameters"].get("query") == "select-products" and o["relation"]["parameters"]["facet"] == "predicate")
    original = r["rows"][index]["relation"]["parameters"]["value"]
    cases = {}
    t = copy.deepcopy(original); t["kind"] = "or"; cases["and_or"] = (index, t)
    cases["removed"] = (index, original["children"][0])
    cases["extra"] = (index, group("and", original, group("not", original["children"][0])))
    cases["negated"] = (index, group("not", original))
    t = copy.deepcopy(original); t["children"][0]["policy"]["case"] = "casefold"; cases["case_policy"] = (index, t)
    for command, label, edit in [
        ("select-range", "inclusive", lambda t: t["children"][0].update(operator="gt")),
        ("select-sessions", "null_inversion", lambda t: t["children"].__setitem__(0, t["children"][0]["child"])),
        ("select-documents", "membership_direction", lambda t: t.update(left=t["right"], right=t["left"])),
        ("group-inner", "grouping", lambda t: t.update(kind="or", children=[group("and", t["children"][0], t["children"][1]["children"][0]), t["children"][1]["children"][1]]))]:
        i = next(i for i, o in enumerate(r["rows"]) if o["relation"]["parameters"].get("query") == command and o["relation"]["parameters"]["facet"] == "predicate")
        t = copy.deepcopy(r["rows"][i]["relation"]["parameters"]["value"]); edit(t); cases[label] = (i, t)
    return r, cases


class PredicateTests(unittest.TestCase):
    def test_atomic_types_presence_null_and_timestamp_boundaries(self):
        t = dict(type="timestamp", domain=[], nullable=True)
        f = operand("field", t, name="time"); p = operand("parameter", t, name="bound")
        for op, expected in (("lt", False), ("le", True), ("gt", False), ("ge", True), ("eq", True)):
            tree = compare(f, p, op); validate(tree, fields={"time": t}, parameters={"bound": t})
            self.assertEqual(predicate_eval(tree, {"time": "2024-01-01T00:00:00.000Z"}, {"bound": "2024-01-01T00:00:00Z"}), expected)
            self.assertFalse(predicate_eval(tree, {"time": None}, {"bound": "2024-01-01T00:00:00Z"}))
        self.assertTrue(predicate_eval(unary("is_null", f), {"time": None}))
        self.assertTrue(predicate_eval(group("not", compare(f, p)), {"time": None}, {"bound": "2024-01-01T00:00:00Z"}))
        s = dict(type="string", domain=[])
        present = unary("present", operand("parameter", s, name="optional"))
        validate(present, parameters={"optional": s})
        self.assertFalse(predicate_eval(present)); self.assertTrue(predicate_eval(present, inputs={"optional": ""}))
        # R5.111 admits explicitly bounded integer equality/order; the old
        # pre-computation rejection is superseded, not a historical result edit.
        integer = dict(type="integer", domain=[])
        validate(compare(operand("literal", integer, value=1), operand("literal", integer, value=1)))
        for typ in (dict(type="boolean", domain=[], nullable=True),):
            with self.assertRaises(Failure): validate(compare(operand("literal", typ, value=1), operand("literal", typ, value=1)))
        with self.assertRaises(Failure): validate(compare(operand("literal", dict(type="boolean", domain=[]), value=1), operand("literal", dict(type="boolean", domain=[]), value=True)))
        with self.assertRaises(Failure): validate(unary("is_null", operand("literal", s, value="")))
        with self.assertRaises(Failure): validate(compare(operand("literal", s, value="a"), operand("literal", s, value="b"), "lt"))

    def test_tree_grouping_and_bounded_equivalence(self):
        s = dict(type="string", domain=[])
        atoms = [compare(operand("field", s, name=n), operand("literal", s, value="yes")) for n in ("a", "b", "c")]
        a, b, c = atoms
        left, right = group("and", a, group("or", b, c)), group("or", group("and", a, b), c)
        self.assertNotEqual(canonical_meaning(left), canonical_meaning(right))
        row = dict(a="no", b="no", c="yes")
        self.assertFalse(predicate_eval(left, row)); self.assertTrue(predicate_eval(right, row))
        self.assertEqual(canonical_meaning(group("and", a, b)), canonical_meaning(group("and", b, a)))
        self.assertEqual(canonical_meaning(group("not", group("not", a))), canonical_meaning(a))
        self.assertEqual(json.loads(json.dumps(left)), left)

    def test_normal_requirements_to_external_behavior(self):
        r, c = prepared()
        validate_output(dict(obligations=r["candidate"]["rows"]))
        p = contracts.structural(c, "frc"); contracts.coverage(c, p)
        b = contracts.bdi(c, p)
        self.assertEqual(contracts.adequate(c, b)["outcome"], "ADEQUATE")
        normal = contracts.faithful_v1(c)["normalized"]
        self.assertEqual(mutable_profile.recover(normal), c)
        self.assertEqual(generate(author(normal)), generate(author(normal)))
        self.assertEqual(CACHE["result"]["external_invocations"], 31)

    def test_source_reconciliation_adversarial_meaning_changes(self):
        original, changes = mutations()
        for label, (index, tree) in changes.items():
            bad = copy.deepcopy(original); bad["rows"][index]["relation"]["parameters"]["value"] = tree
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmp:
                ctrl = PipelineController(Path(tmp) / "case.sqlite", PRINCIPALS)
                try:
                    w = Workspace(ctrl, "public", "predicate-" + label, CREDENTIALS)
                    w.ingest(CREDENTIALS["owner"], original["source"])
                    try:
                        w.formalize(ev.producer(bad, "formalizer"))
                    except Failure:
                        # Ill-typed membership direction is refused even earlier.
                        self.assertEqual(label, "membership_direction")
                        continue
                    soi = w.commit_inventory(ev.producer(original, "reviewer"))
                    self.assertEqual(ctrl.artifact(w.reconcile(soi))["content"]["outcome"], "DISPUTED")
                finally: ctrl.close()

    def test_coverage_and_v1_detect_all_material_mutations(self):
        _, c = prepared()
        normal = contracts.faithful_v1(c)["normalized"]
        r, changes = mutations()
        for label, (i, tree) in changes.items():
            bad = copy.deepcopy(normal)
            row = r["rows"][i]["relation"]["parameters"]
            bad["facts"]["queries"][row["query"]]["predicate"] = tree
            with self.subTest(label=label), self.assertRaises(Failure): mutable_profile.recover(bad)
        p = contracts.structural(c, "frc")
        p["facts"]["queries"]["select-products"]["predicate"]["children"].pop()
        with self.assertRaises(Failure): contracts.coverage(c, p)
        bad = copy.deepcopy(c)
        query(bad, "select-products")["children"][1]["left"]["type"]["type"] = "string"
        with self.assertRaises(Failure): contracts.coverage(bad, contracts.structural(bad, "frc"))

    def test_bdi_adequacy_missing_predicate_authority(self):
        _, c = prepared()
        b = contracts.bdi(c, contracts.structural(c, "frc"))
        material = [d for d in b["result"]["decisions"] if d["family"].startswith("condition/")]
        self.assertGreater(len(material), 20)
        for decision in material[:8]:
            bad = copy.deepcopy(b)
            next(d for d in bad["result"]["decisions"] if d["id"] == decision["id"])["authority"] = None
            self.assertEqual(contracts.adequate(c, bad)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")

    def test_boolean_migration_and_record_local_invariant(self):
        r, c = prepared()
        def facet(name):
            return next(o["relation"]["parameters"]["value"] for o in c["obligations"] if o["relation"]["parameters"].get("facet") == name)
        facet("storage")["version"] = 2
        facet("collections")[0]["migration"] = [dict(**{"from": 1}, to=2, value=[])]
        semantics = facet("predicate_semantics")
        semantics["booleans"][0]["migration"] = [dict(**{"from": 1}, to=2, value=False)]
        boolean = dict(type="boolean", domain=[], nullable=False)
        enabled = operand("field", boolean, name="enabled")
        # A bounded invariant can use the same tree at storage boundaries.
        semantics["invariants"] = [dict(predicate=group("or", compare(enabled, operand("literal", boolean, value=False)), compare(enabled, operand("literal", boolean, value=True))), error="invalid_state")]
        source = generate(author(contracts.faithful_v1(c)["normalized"]))
        row = dict(id="known", nickname="Name", description="Text", state="active", category="public", created_at="2020-01-01T00:00:00Z", expires_at=None)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(source, encoding="utf-8")
            path = Path(tmp) / r["path"]; path.write_text(json.dumps([row]), encoding="utf-8")
            def run(*args):
                return subprocess.run([sys.executable, str(target), *args], cwd=tmp, capture_output=True, text=True)
            result = run("migrate"); self.assertEqual(result.returncode, 0, result.stderr)
            expected = {**row, r["collection"]: [], "enabled": False}
            self.assertEqual(json.loads(run("list").stdout), [expected])
            payload = json.loads(path.read_text()); payload["records"][0]["enabled"] = 0
            path.write_text(json.dumps(payload), encoding="utf-8"); before = path.read_bytes()
            result = run("list"); self.assertEqual(json.loads(result.stderr), {"error": "invalid_state"})
            self.assertEqual(path.read_bytes(), before)
        semantics["booleans"][0]["migration"][0]["value"] = 0
        with self.assertRaises(Failure): contracts.coverage(c, contracts.structural(c, "frc"))


if __name__ == "__main__": unittest.main()
