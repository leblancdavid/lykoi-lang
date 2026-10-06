"""Meaningful normal-path, authority and external mutation challenges."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from air_compiler.mutable_values import compose, stable_unique
from air_compiler.profiles import author, generate
from lykoi_controller import Failure
from lykoi_pipeline import contracts, mutable_profile
from lykoi_workspace.mutable_corpus import captures, plan
from lykoi_workspace.query_schema import validate_output
from lykoi_pipeline import PipelineController
from lykoi_pipeline.example import PRINCIPALS, CREDENTIALS
from lykoi_workspace import Workspace

ROOT = Path(__file__).resolve().parents[1]
CACHE = {}
spec = importlib.util.spec_from_file_location("mutation_evaluator", ROOT / "benchmark/results/phase5c/R5_103-evaluate.py")
evaluation = importlib.util.module_from_spec(spec); spec.loader.exec_module(evaluation)


def prepared(record=None):
    record = record or captures()[0]
    if record["domain"] in CACHE:
        return copy.deepcopy(CACHE[record["domain"]])
    result = evaluation.evaluate(record["candidate"], plan(record))
    assert result["first_blocker"] == "SUCCESS", result.get("terminal", result)
    value = record, result["formalization"]["contract"], next(a["content"]["target_source"] for a in result["audit"]["artifacts"].values() if a["type"] == "target")
    CACHE[record["domain"]] = value
    return copy.deepcopy(value)


class MutableValuesTests(unittest.TestCase):
    def test_collection_additive_migration_normal_path(self):
        r = captures()[0]
        prior = mutable_profile.scalar.lower(r["scalar"])
        c = r["candidate"]
        c["source"] += " Schema 2 explicitly introduces labels on existing records with historical value ['Legacy']; creation default remains empty. migrate preserves all other fields and is idempotent."
        c["domains"]["scalar_base_model"] = prior
        for o in c["rows"]:
            p = o["relation"]["parameters"]
            if p.get("profile") == "existing-scalar-1" and p["facet"] == "storage": p["value"]["version"] = 2
            if p.get("profile") == mutable_profile.PROFILE and p["facet"] == "collections": p["value"][0]["migration"] = [{"from": 1, "to": 2, "value": ["Legacy"]}]
        old = dict(id="known", created_at="2020-01-01T00:00:00Z", nickname="Old", description="Original", state="active")
        expected = {**old, "labels": ["Legacy"]}
        external = plan(r)
        case = dict(id="migration", obligations=[o["id"] for o in c["rows"]], initial_state="fresh_directory", initial_files=[dict(path="article.json", json=[old])], steps=[
            dict(argv=["list"], returncode=1, contains=[], stdout_exact="", stderr_json={"error": "migration_required"}, preserved=["article.json"]),
            dict(argv=["migrate"], returncode=0, contains=[], stdout_json={"migrated": 1}, stderr_exact=""),
            dict(argv=["list"], returncode=0, contains=[], stdout_json=[expected], stderr_exact="", preserved=["article.json"]),
            dict(argv=["migrate"], returncode=0, contains=[], stdout_json={"migrated": 0}, stderr_exact="", preserved=["article.json"]),
            dict(argv=["find-value", "--value", "Legacy"], returncode=0, contains=[], stdout_json=[expected], stderr_exact="", preserved=["article.json"])], invariants=["Explicit historical authority and unrelated-field preservation"], transitions="Additive migration", rejections="Unmigrated data refused")
        case["identity"] = hashlib.sha256(evaluation.canonical(case)).hexdigest()
        external["cases"] = [case]
        for row in external["coverage"]: row["cases"] = [case["identity"]]
        result = evaluation.evaluate(c, external)
        self.assertEqual(result["first_blocker"], "SUCCESS", result.get("terminal"))
        bad = copy.deepcopy(result["formalization"]["contract"])
        coll = next(o for o in bad["obligations"] if o["relation"]["parameters"].get("facet") == "collections")
        coll["relation"]["parameters"]["value"][0]["migration"] = []
        with self.assertRaises(Failure): contracts.coverage(bad, contracts.structural(bad, "frc"))

    def test_source_reconciliation_rejects_invented_mutation_choices(self):
        for invented in ("transform", "duplicates"):
            r = captures()[0]["candidate"]; bad = copy.deepcopy(r)
            if invented == "duplicates":
                row = next(o for o in bad["rows"] if o["relation"]["parameters"].get("facet") == "collections")
                row["relation"]["parameters"]["value"][0]["duplicates"] = "allow"
            else:
                row = next(o for o in bad["rows"] if o["relation"]["parameters"].get("facet") == "mutations")
                row["relation"]["parameters"]["value"][3]["changes"][0]["pipeline"] = [dict(kind="transform", operation="trim")]
            with tempfile.TemporaryDirectory() as tmp:
                controller = PipelineController(Path(tmp) / "case.sqlite", PRINCIPALS)
                try:
                    w = Workspace(controller, "public", "invention-" + invented, CREDENTIALS)
                    w.ingest(CREDENTIALS["owner"], r["source"])
                    w.formalize(evaluation.producer(bad, "formalizer"))
                    soi = w.commit_inventory(evaluation.producer(r, "reviewer"))
                    reconciliation = controller.artifact(w.reconcile(soi))["content"]
                    self.assertEqual(reconciliation["outcome"], "DISPUTED")
                finally: controller.close()

    def test_repeated_inputs_element_pipeline_and_creation_authority(self):
        r, c, _ = prepared()
        coll = next(o for o in c["obligations"] if o["relation"]["parameters"].get("facet") == "collections")["relation"]["parameters"]["value"][0]
        coll["creation"].update(input="label", encoding="repeated", pipeline=[dict(kind="map_elements", pipeline=[dict(kind="transform", operation="trim"), dict(kind="validate", rule="nonempty", error="empty_value")]), dict(kind="transform", operation="stable_deduplicate")])
        # This is a separately source-authorized synthetic extension, never an
        # inferred default or edit to sealed authority.
        c["source"]["text"] += " Creation accepts repeated --label inputs, trims each, rejects empty with empty_value, then stably deduplicates."
        c["source"]["sha256"] = hashlib.sha256(c["source"]["text"].encode()).hexdigest()
        collrow = next(o for o in c["obligations"] if o["relation"]["parameters"].get("facet") == "collections")
        collrow["source_quote"] = c["source"]["text"]
        source = generate(author(contracts.faithful_v1(c)["normalized"]))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(source, encoding="utf-8")
            p = subprocess.run([sys.executable, str(target), "create", "--nickname", "X", "--label", " B ", "--label", "A", "--label", "B", "--label", "b"], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr); self.assertEqual(json.loads(p.stdout)["labels"], ["B", "A", "b"])
            before = (Path(tmp) / "article.json").read_bytes()
            p = subprocess.run([sys.executable, str(target), "create", "--nickname", "X", "--label", " "], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(json.loads(p.stderr), {"error": "empty_value"}); self.assertEqual((Path(tmp) / "article.json").read_bytes(), before)

    def test_four_domains_normal_chain_and_external_behavior(self):
        for record in captures():
            with self.subTest(domain=record["domain"]):
                validate_output(dict(obligations=record["candidate"]["rows"]))
                _, c, source = prepared(record)
                p = contracts.structural(c, "frc")
                self.assertEqual(contracts.coverage(c, p)["outcome"], "SUPPORTED")
                b = contracts.bdi(c, p)
                self.assertEqual(contracts.adequate(c, b)["outcome"], "ADEQUATE")
                normal = contracts.faithful_v1(c)["normalized"]
                self.assertEqual(mutable_profile.recover(normal), c)
                self.assertEqual(generate(author(normal)), source)

    def test_stable_dedup_cases(self):
        for before, after in [([], []), (["b", "a", "b", "B", "a"], ["b", "a", "B"]), (["b", "a"], ["b", "a"])]:
            self.assertEqual(stable_unique(before), after)

    def test_material_facet_omission_and_tampering_fail_closed(self):
        _, c, _ = prepared()
        for facet in mutable_profile.FACETS:
            bad = copy.deepcopy(c); bad["obligations"] = [o for o in bad["obligations"] if o["relation"]["parameters"].get("facet") != facet]
            with self.subTest(facet=facet), self.assertRaises(Failure):
                contracts.coverage(bad, contracts.structural(bad, "frc"))
        p = contracts.structural(c, "frc"); p["facets"].pop()
        with self.assertRaises(Failure): contracts.coverage(c, p)

    def test_v1_detects_all_material_mutation_changes(self):
        _, c, _ = prepared()
        normal = contracts.faithful_v1(c)["normalized"]
        for change in ("duplicates", "order", "presence", "transform", "validate", "atomic"):
            bad = copy.deepcopy(normal); f = bad["facts"]["mutable"]
            if change == "duplicates": f["collections"][0]["duplicates"] = "allow"
            elif change == "order": f["collections"][0]["ordering"] = "sorted"
            elif change == "presence": f["mutations"][3]["changes"][0]["omitted"] = "reject"
            elif change == "atomic": f["mutations"][0]["effect"]["rejection"] = "partial"
            elif change == "transform": f["mutations"][1]["changes"][0]["pipeline"].reverse()
            else: f["mutations"][1]["changes"][0]["pipeline"][1]["error"] = "another_error"
            with self.subTest(change=change), self.assertRaises(Failure): mutable_profile.recover(bad)

    def test_missing_mutation_authority_is_not_adequate(self):
        _, c, _ = prepared()
        b = contracts.bdi(c, contracts.structural(c, "frc"))
        for family in ("duplicates", "ordering", "presence", "pipeline", "atomicity"):
            bad = copy.deepcopy(b)
            decision = next(d for d in bad["result"]["decisions"] if d["family"].endswith("/" + family))
            decision["authority"] = None
            with self.subTest(family=family):
                self.assertEqual(contracts.adequate(c, bad)["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")

    def test_invalid_policies_and_conflicting_operations_refuse(self):
        _, c, _ = prepared()
        original = mutable_profile.facts(c)["ir"]
        for case in ("append_unique", "ordering", "equality", "presence", "atomic", "pipeline", "lifecycle"):
            f = copy.deepcopy(original["facts"])
            if case == "append_unique": f["mutations"][0]["changes"][0]["operation"] = "append"
            elif case == "ordering": f["collections"][0]["ordering"] = "set"
            elif case == "equality": f["collections"][0]["equality"] = "casefold"
            elif case == "presence": del f["mutations"][0]["changes"][0]["omitted"]
            elif case == "atomic": del f["mutations"][0]["effect"]["atomicity"]
            elif case == "pipeline": f["mutations"][1]["changes"][0]["pipeline"] = [dict(kind="transform", operation="lower")]
            else: f["mutations"][1]["changes"][0]["field"] = "state"
            with self.subTest(case=case), self.assertRaises(Failure): compose(original["base"], f)

    def test_external_dedup_empty_unique_and_invalid_collection(self):
        r, _, source = prepared(captures()[2])
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(source, encoding="utf-8")
            path = Path(tmp) / r["path"]
            row = dict(id="known", created_at="2020-01-01T00:00:00Z", nickname="Old", description="", state="active", keywords=[])
            path.write_text(json.dumps([row]), encoding="utf-8")
            for value, expected in [('[]', []), ('["b","a"]', ["b", "a"]), ('["b","a","b","B"]', ["b", "a", "B"]), ('["a","a"]', ["a"])]:
                p = subprocess.run([sys.executable, str(target), "write-values", "--id", "known", "--keywords", value], cwd=tmp, capture_output=True, text=True)
                self.assertEqual(p.returncode, 0, p.stderr); self.assertEqual(json.loads(p.stdout)["keywords"], expected)
            before = path.read_bytes()
            for invalid in ('null', '[1]', '"x"', 'not json'):
                p = subprocess.run([sys.executable, str(target), "write-values", "--id", "known", "--keywords", invalid], cwd=tmp, capture_output=True, text=True)
                self.assertEqual(json.loads(p.stderr), {"error": "invalid_value"}); self.assertEqual(path.read_bytes(), before)

    def test_persistence_failure_has_no_partially_mutated_record(self):
        r, _, source = prepared()
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(source, encoding="utf-8")
            script = '''import importlib.util,json,os
from unittest.mock import patch
s=importlib.util.spec_from_file_location('target','target.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
row=dict(id='known',created_at='2020-01-01T00:00:00Z',nickname='Old',description='Original',state='active',labels=[])
open('article.json','w').write(json.dumps([row])); before=open('article.json','rb').read()
with patch.object(m.os,'replace',side_effect=OSError('failure')):
 try: m.execute_mutation(m.MUTABLE['facts']['mutations'][4],dict(id='known',nickname=' New ',description='Changed'))
 except m.Failure as e: assert e.code=='persistence_failure'
 else: raise AssertionError('expected failure')
assert open('article.json','rb').read()==before
assert row['nickname']=='Old' and row['description']=='Original'
assert not list(m.Path('.').glob('.lykoi-*.tmp'))
print('atomic-failure-pass')
'''
            p = subprocess.run([sys.executable, "-c", script], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)

    def test_nullable_timestamp_presence_and_typed_enum_updates(self):
        _, c, _ = prepared(captures()[3])
        fields = next(o for o in c["obligations"] if o["id"] == "profile/fields")["relation"]["parameters"]["value"]
        fields += [dict(name="review_at", type="timestamp", domain=[], nullable=True, preservation="verbatim"), dict(name="category", type="enum", domain=["A", "B"], nullable=False, preservation="verbatim")]
        creation = next(o for o in c["obligations"] if o["id"] == "profile/creation")["relation"]["parameters"]["value"]
        creation["bindings"] += [dict(field="review_at", source="input", value=None, default=dict(value=None, trigger="omitted", boundary="creation")), dict(field="category", source="input", value=None, default=dict(value="A", trigger="omitted", boundary="creation"))]
        from lykoi_workspace.mutable_corpus import mutation, change
        mutations = next(o for o in c["obligations"] if o["id"] == "profile/mutations")["relation"]["parameters"]["value"]
        mutations.append(mutation("change-values", [change("review_at", optional=True), change("category", steps=[dict(kind="transform", operation="trim"), dict(kind="validate", rule="typed", error="invalid_category")], optional=True)]))
        text = c["source"]["text"] + " Add existing nullable UTC review_at default null and category enum A/B default A. change-values leaves omitted fields unchanged, accepts explicit null only for review_at, trims category then validates its domain with invalid_category."
        c["source"]["text"] = text; c["source"]["sha256"] = hashlib.sha256(text.encode()).hexdigest()
        source = generate(author(contracts.faithful_v1(c)["normalized"]))
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "target.py"; target.write_text(source, encoding="utf-8")
            script = '''import importlib.util,json
s=importlib.util.spec_from_file_location('target','target.py'); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
row=dict(id='known',created_at='2020-01-01T00:00:00Z',nickname='Old',description='Original',state='active',interests=[],review_at='2020-01-01T00:00:00Z',category='A')
open('profile.json','w').write(json.dumps([row])); operation=m.MUTABLE['facts']['mutations'][-1]
assert m.execute_mutation(operation,dict(id='known'))['review_at']==row['review_at']
r=m.execute_mutation(operation,dict(id='known',review_at=None,category=' B ')); assert r['review_at'] is None and r['category']=='B'
before=open('profile.json','rb').read()
for values,error in [(dict(review_at='bad'), 'invalid_value'),(dict(category=None),'invalid_value'),(dict(review_at='2021-01-01T00:00:00Z',category='C'),'invalid_category')]:
 try: m.execute_mutation(operation,dict(id='known',**values))
 except m.Failure as e: assert e.code==error,(e.code,error)
 else: raise AssertionError('expected rejection')
 assert open('profile.json','rb').read()==before
print('presence-type-atomicity-pass')
'''
            p = subprocess.run([sys.executable, "-c", script], cwd=tmp, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)


if __name__ == "__main__": unittest.main()
