"""Input closure authority, faithful representation and observable process tests."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from air_compiler.profiles import author, generate
from lykoi_controller import Failure
from lykoi_pipeline import contracts, mutable_profile, PipelineController
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace
from lykoi_workspace.input_corpus import captures, plan, staged
from lykoi_workspace.query_schema import validate_output

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("input_evaluator", ROOT / "benchmark/results/phase5c/R5_103-evaluate.py")
ev = importlib.util.module_from_spec(spec); spec.loader.exec_module(ev)
CACHE = {}


def prepared(index=0):
    if index not in CACHE:
        r = captures()[index]
        x = ev.evaluate(r["candidate"], plan(r))
        assert x["first_blocker"] == "SUCCESS", x.get("terminal", x)
        CACHE[index] = r, x["formalization"]["contract"], next(a["content"]["target_source"] for a in x["audit"]["artifacts"].values() if a["type"] == "target")
    return copy.deepcopy(CACHE[index])


def value(c, facet):
    return next(o["relation"]["parameters"]["value"] for o in c["obligations"] if o["relation"]["parameters"].get("facet") == facet)


class InputValuesTests(unittest.TestCase):
    def test_four_domains_normal_external_chains(self):
        for index in range(4):
            r, c, source = prepared(index)
            with self.subTest(domain=r["domain"]):
                validate_output(dict(obligations=r["candidate"]["rows"]))
                p = contracts.structural(c, "frc")
                self.assertEqual(contracts.coverage(c, p)["outcome"], "SUPPORTED")
                self.assertEqual(contracts.adequate(c, contracts.bdi(c, p))["outcome"], "ADEQUATE")
                normal = contracts.faithful_v1(c)["normalized"]
                self.assertEqual(mutable_profile.recover(normal), c)
                self.assertEqual(generate(author(normal)), source)

    def test_binding_errors_and_material_omissions_fail_closed(self):
        _, c, _ = prepared(1)
        for case in ("missing", "wrong_parameter", "duplicate", "conflicting_flag", "wrong_type", "constant", "required_optional", "no_missing_behavior", "encoding", "stage", "persisted_order"):
            bad = copy.deepcopy(c); ps = value(bad, "input_contracts")
            if case == "missing": ps.pop()
            elif case == "wrong_parameter": ps[0]["parameter"] = "invented"
            elif case == "duplicate": ps.append(copy.deepcopy(ps[0]))
            elif case == "conflicting_flag": ps[1]["binding"]["flag"] = ps[0]["binding"]["flag"]
            elif case == "wrong_type": ps[0]["type"]["type"] = "boolean"
            elif case == "constant": ps[0]["parameter"] = "category"
            elif case == "required_optional": ps[0]["presence"] = "optional"; ps[0]["missing"] = None
            elif case == "no_missing_behavior": ps[0]["missing"] = None
            elif case == "encoding": ps[0]["binding"]["encoding"] = "json"
            else:
                w = value(bad, "mutations")[-2]["changes"][0]
                if case == "stage": del w["pipeline"][1]["stage"]
                else: w["pipeline"].append(dict(kind="transform", operation="trim"))
            with self.subTest(case=case), self.assertRaises(Failure):
                contracts.coverage(bad, contracts.structural(bad, "frc"))
        bad = copy.deepcopy(c)
        bad["obligations"] = [o for o in bad["obligations"] if o["relation"]["parameters"].get("facet") != "input_contracts"]
        with self.assertRaises(Failure): contracts.coverage(bad, contracts.structural(bad, "frc"))

    def test_literal_typed_order_duplicates_and_default_distinctions(self):
        _, c, _ = prepared(2)
        for wrong in (None, [1], ["A", None], "[]"):
            bad = copy.deepcopy(c); value(bad, "collections")[0]["creation"]["value"] = wrong
            with self.subTest(wrong=wrong), self.assertRaises(Failure): contracts.coverage(bad, contracts.structural(bad, "frc"))
        _, bad, _ = prepared(0); value(bad, "collections")[0]["creation"]["value"] = ["A", "A"]
        with self.assertRaises(Failure): contracts.coverage(bad, contracts.structural(bad, "frc"))
        ir = mutable_profile.facts(c)["ir"]
        create = next(b for b in ir["model"]["behaviors"] if b["kind"] == "create")
        self.assertFalse(any(i["name"] == "keywords" for i in create["inputs"]))
        a = next(a for a in create["assignments"] if a["field"] == "field:mutable:keywords")
        self.assertEqual(a, dict(field="field:mutable:keywords", source="literal", value=["Seed", "A", "Seed"]))
        self.assertEqual(next(a for a in create["assignments"] if a["field"].endswith("description"))["source"], "input_default")

    def test_reconciliation_detects_invented_input_value_authority(self):
        r = captures()[0]["candidate"]
        for case in ("literal", "trim", "required", "missing_error", "raw_stage", "wrong_binding"):
            bad = copy.deepcopy(r)
            def fact(facet): return next(o["relation"]["parameters"]["value"] for o in bad["rows"] if o["relation"]["parameters"].get("facet") == facet)
            if case == "literal": fact("collections")[0]["creation"]["value"] = ["Invented"]
            elif case == "trim": fact("mutations")[3]["changes"][0]["pipeline"] = [dict(kind="transform", operation="trim")]
            elif case == "required": fact("input_contracts")[1]["presence"] = "required"; fact("input_contracts")[1]["missing"] = dict(kind="application_error", error="missing_description")
            elif case == "missing_error": fact("input_contracts")[0]["missing"]["error"] = "invented_error"
            elif case == "wrong_binding": fact("input_contracts")[0]["binding"]["flag"] = "--description"
            else: fact("mutations")[1]["changes"][0]["pipeline"][1]["stage"] = "RAW"
            with tempfile.TemporaryDirectory() as tmp:
                ctrl = PipelineController(Path(tmp) / "case.sqlite", PRINCIPALS)
                try:
                    w = Workspace(ctrl, "public", "input-invention-" + case, CREDENTIALS)
                    w.ingest(CREDENTIALS["owner"], r["source"])
                    w.formalize(ev.producer(bad, "formalizer"))
                    soi = w.commit_inventory(ev.producer(r, "reviewer"))
                    self.assertEqual(ctrl.artifact(w.reconcile(soi))["content"]["outcome"], "DISPUTED")
                finally: ctrl.close()

    def test_v1_roundtrip_and_adequacy_authority(self):
        _, c, _ = prepared()
        normal = contracts.faithful_v1(c)["normalized"]
        for case in ("literal_contents", "literal_default", "stage", "condition", "presence", "binding", "error"):
            bad = copy.deepcopy(normal); f = bad["facts"]["mutable"]
            if case == "literal_contents": f["collections"][0]["creation"]["value"] = ["Changed"]
            elif case == "literal_default": f["collections"][0]["creation"] = dict(input="labels", encoding="json", default=[], pipeline=[], error="invalid_value")
            elif case == "stage": f["mutations"][-2]["changes"][0]["pipeline"][1]["stage"] = "RAW"
            elif case == "condition": f["mutations"][-2]["changes"][0]["pipeline"][1]["when"]["predicate"] = "present"
            elif case == "presence": f["input_contracts"][0]["presence"] = "optional"
            elif case == "binding": f["input_contracts"][0]["binding"]["flag"] = "--wrong"
            else: f["input_contracts"][0]["missing"]["error"] = "wrong"
            with self.subTest(case=case), self.assertRaises(Failure): mutable_profile.recover(bad)
        p = contracts.structural(c, "frc"); p["facets"].pop()
        with self.assertRaises(Failure): contracts.coverage(c, p)
        b = contracts.bdi(c, contracts.structural(c, "frc"))
        for family in ("value_source", "required_input", "missing_input", "external_binding", "pipeline"):
            bad = copy.deepcopy(b)
            next(d for d in bad["result"]["decisions"] if d["family"].endswith("/" + family))["authority"] = None
            self.assertEqual(contracts.adequate(c, bad)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")

    def test_external_correct_binding_empty_array_missing_and_rejection(self):
        r, _, source = prepared(1)
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(source, encoding="utf-8")
            path = Path(tmp) / r["path"]
            def run(*args): return subprocess.run([sys.executable, str(target), *args], cwd=tmp, capture_output=True, text=True)
            p = run("create", "--nickname", "Alias", "--alias-data", "[]")
            self.assertEqual(p.returncode, 0, p.stderr); self.assertEqual(json.loads(p.stdout)["aliases"], [])
            before = path.read_bytes()
            p = run("create", "--nickname", "Missing")
            self.assertEqual(json.loads(p.stderr), {"error": "missing_aliases"}); self.assertEqual(path.read_bytes(), before)
            for wrong in ("null", "[1]", '"constant"'):
                p = run("create", "--nickname", "Wrong", "--alias-data", wrong)
                self.assertEqual(json.loads(p.stderr), {"error": "invalid_value"}); self.assertEqual(path.read_bytes(), before)
            p = run("create", "--nickname", "Wrong", "--aliases", "[]")
            self.assertNotEqual(p.returncode, 0); self.assertEqual(path.read_bytes(), before)

    def test_declared_cli_rejection_not_parser_required_default(self):
        _, c, _ = prepared()
        value(c, "input_contracts")[0]["missing"] = dict(kind="cli_rejection")
        parameter = next(p for p in value(c, "input_contracts") if p["operation"] == "rename" and p["parameter"] == "nickname")
        parameter["missing"] = dict(kind="cli_rejection")
        next(m for m in value(c, "mutations") if m["command"] == "rename")["changes"][0]["missing_error"] = None
        source = generate(author(contracts.faithful_v1(c)["normalized"]))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(source, encoding="utf-8")
            p = subprocess.run([sys.executable, str(target), "create"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(p.returncode, 2); self.assertEqual(p.stderr, "missing required input: --nickname\n")
            self.assertFalse((Path(tmp) / "article.json").exists())
            p = subprocess.run([sys.executable, str(target), "rename", "--id", "unknown"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(p.returncode, 2); self.assertEqual(p.stderr, "missing required input: --nickname\n")
            self.assertFalse((Path(tmp) / "article.json").exists())

    def test_stage_observations_presence_null_whitespace_and_atomic_failure(self):
        _, _, source = prepared()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(source, encoding="utf-8")
            script = '''import importlib.util,json
from unittest.mock import patch
s=importlib.util.spec_from_file_location('target','target.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
t=dict(type='string',domain=[],nullable=False)
v=lambda stage,when=None: dict(kind='validate',rule='nonempty',error='empty',stage=stage,when=when)
trim=dict(kind='transform',operation='trim')
assert m.mutable_pipeline('   ',[trim,v('RAW')],t,'invalid')==''
for stage in ('TRANSFORMED','PERSISTED'):
 try: m.mutable_pipeline('   ',[trim,v(stage)],t,'invalid')
 except m.Failure as e: assert e.code=='empty'
 else: raise AssertionError('stage lost')
for pred,raw,rejected in [('empty','',True),('empty',' ',False),('whitespace','',False),('whitespace',' ',True),('present','',True),('absent','',False)]:
 try: m.mutable_pipeline(raw,[trim,v('TRANSFORMED',dict(stage='RAW',predicate=pred))],t,'invalid')
 except m.Failure: assert rejected,(pred,raw)
 else: assert not rejected,(pred,raw)
nt=dict(type='timestamp',domain=[],nullable=True)
assert m.mutable_pipeline(None,[],nt,'invalid') is None
row=dict(id='known',created_at='2020-01-01T00:00:00Z',nickname='Old',description='Original',state='active',labels=[],category='public')
open('article.json','w').write(json.dumps([row])); before=open('article.json','rb').read()
optional=next(x for x in m.MUTABLE['facts']['mutations'] if x['command']=='optional-nickname')
assert m.execute_mutation(optional,dict(id='known'))==row
assert open('article.json','rb').read()==before
op=next(x for x in m.MUTABLE['facts']['mutations'] if x['command']=='update-profile')
try: m.execute_mutation(op,dict(id='known',nickname=' New ',description=None))
except m.Failure as e: assert e.code=='invalid_value'
else: raise AssertionError('null accepted')
assert open('article.json','rb').read()==before
with patch.object(m.os,'replace',side_effect=OSError('failure')):
 try: m.execute_mutation(op,dict(id='known',nickname=' New ',description='Changed'))
 except m.Failure as e: assert e.code=='persistence_failure'
 else: raise AssertionError('failure missed')
assert open('article.json','rb').read()==before
assert not list(m.Path('.').glob('.lykoi-*.tmp'))
print('stages-presence-atomicity-pass')
'''
            p = subprocess.run([sys.executable, "-c", script], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)


if __name__ == "__main__": unittest.main()
