import copy
import unittest

from air_compiler import collection_query as language
from benchmark.evaluation import formal_requirements_r5_80 as frc
from lykoi_controller import Failure
from lykoi_pipeline import contracts as historical
from lykoi_query import contracts
from lykoi_query.corpus import contract, queries
from lykoi_query.compiler import compile_document


class CollectionQueryTests(unittest.TestCase):
    def chain(self, q, source=None):
        c = contract(q, source)
        p = contracts.structural(c, frc.validate(c))
        contracts.coverage(c, p)
        b = contracts.bdi(c, p)
        a = contracts.adequate(c, b)
        return c, p, b, a

    def test_composed_corpus_complete_through_all_layers(self):
        for q in queries():
            with self.subTest(query=q["id"]):
                c, p, b, a = self.chain(q)
                self.assertEqual(len(p["rows"]), 9)
                self.assertEqual(b["outcome"], "SUPPORTED")
                self.assertEqual(a["outcome"], "IMPLEMENTATION_ADEQUATE")
                self.assertEqual(len(b["result"]["decisions"]), 8)
                self.assertEqual(contracts.recover(contracts.document(c, p)), c)
                self.assertEqual(compile_document(contracts.document(c, p))[q["id"]], language.generate(q))
                self.assertEqual(language.generate(q), language.generate(copy.deepcopy(q)))

    def test_policy_omission_is_not_freedom(self):
        for facet in language.POLICIES:
            with self.subTest(facet=facet):
                q = queries()[0]
                options = contracts.alternatives(q, facet)
                q[facet] = None
                c, p, b, a = self.chain(q, "The observable " + facet + " policy is omitted; other policies are stated.")
                self.assertEqual(a["outcome"], "IMPLEMENTATION_UNDERSPECIFIED")
                self.assertIn(q["id"] + ":query_" + facet, a["result"]["missing_decisions"])
                with self.assertRaises(language.QueryError):
                    language.generate(q)
                # Alternatives admitted by the bounded language (the implicit
                # exclusion sentinel is analysis-only and not an authored policy).
                if facet == "inclusion":
                    options = contracts.alternatives(queries()[0], facet)
                q[facet] = {"freedom": options}
                c, p, b, a = self.chain(q, "Explicit freedom among the stated " + facet + " alternatives; other policies stated.")
                self.assertEqual(a["outcome"], "IMPLEMENTATION_ADEQUATE")
                decision = next(d for d in b["result"]["decisions"] if d["family"] == "query_" + facet)
                self.assertEqual(decision["authority"]["authority"], "UNCONSTRAINED")
                with self.assertRaises(language.QueryError):
                    language.generate(q)

    def test_near_misses_have_distinct_structural_and_decision_meaning(self):
        original = queries()[1]
        variants = []
        q = copy.deepcopy(original); q["predicate"]["operand"] = {"constant": "Sales"}; variants.append(q)
        q = copy.deepcopy(original); q["comparison"]["case"] = "casefold"; variants.append(q)
        q = copy.deepcopy(original); q["comparison"]["normalization"] = "strip"; variants.append(q)
        q = copy.deepcopy(original); q["ordering"] = [{"field": "id", "direction": "DESC"}]; variants.append(q)
        q = copy.deepcopy(original); q["ordering"][1]["direction"] = "ASC"; variants.append(q)
        q = copy.deepcopy(original); q["ordering"].reverse(); variants.append(q)
        q = copy.deepcopy(original); q["effect"] = {"state": "mutating", "persistence": "write"}; variants.append(q)
        q = copy.deepcopy(original); q["result"].update(no_match="error", error="not_found"); variants.append(q)
        q = copy.deepcopy(original); q["result"]["no_match"] = "null"; variants.append(q)
        q = copy.deepcopy(original); q["validation"] = []; variants.append(q)
        q = copy.deepcopy(original); q["validation"][0]["rule"] = "nonempty"; variants.append(q)
        q = copy.deepcopy(original); q["inclusion"] = [{"field": "inactive", "mode": "equals", "value": False}]; variants.append(q)
        c, p, b, a = self.chain(original)
        for q in variants:
            with self.subTest(query=q):
                c2, p2, b2, a2 = self.chain(q, "Explicit alternative query semantics as recorded in this synthetic fixture.")
                self.assertNotEqual(p["queries"], p2["queries"])
                self.assertNotEqual([d["authority"]["allowed"] for d in b["result"]["decisions"]],
                                    [d["authority"]["allowed"] for d in b2["result"]["decisions"]])
                self.assertEqual(a2["outcome"], "IMPLEMENTATION_ADEQUATE")
                if q["effect"]["state"] == "mutating":
                    with self.assertRaises(language.QueryError):
                        language.generate(q)

    def test_coverage_fail_closed_for_every_lost_facet_and_stale_value(self):
        q = queries()[0]
        c, p, b, a = self.chain(q)
        for i in range(9):
            with self.subTest(facet=i):
                lost = copy.deepcopy(c); lost["obligations"].pop(i)
                projection = contracts.structural(lost, frc.validate(lost))
                with self.assertRaises(Failure):
                    contracts.coverage(lost, projection)
                corrupt = copy.deepcopy(p); corrupt["rows"].pop(i)
                with self.assertRaises(Failure):
                    contracts.coverage(c, corrupt)
        corrupt = copy.deepcopy(p); corrupt["queries"][0]["comparison"]["case"] = "casefold"
        with self.assertRaises(Failure):
            contracts.coverage(c, corrupt)

    def test_unsupported_features_and_inconsistent_types_refuse(self):
        mutations = [lambda q: q["predicate"].update(operator="regex"),
                     lambda q: q["predicate"]["operand"].update(parameter="unknown"),
                     lambda q: q["comparison"].update(normalization="NFC"),
                     lambda q: q["ordering"].append({"field": "missing", "direction": "ASC"}),
                     lambda q: q["ordering"][0].update(direction="SIDEWAYS"),
                     lambda q: q["result"].update(cardinality="exactly_one"),
                     lambda q: q["effect"].update(persistence="write"),
                     lambda q: q["validation"][0].update(rule="regex"),
                     lambda q: q.update(limit=5),
                     lambda q: q["source"]["fields"].update(category="integer")]
        for change in mutations:
            q = queries()[0]; change(q)
            with self.subTest(query=q), self.assertRaises(language.QueryError):
                language.validate(q)
        c = contract(queries()[0]); c["obligations"][0]["relation"]["parameters"]["pagination"] = 10
        p = contracts.structural(c, frc.validate(c))
        with self.assertRaises(Failure):
            contracts.coverage(c, p)

    def test_duplicate_facet_and_extra_obligation_never_complete(self):
        c = contract(queries()[0])
        extra = copy.deepcopy(c["obligations"][0]); extra["id"] = "extra"
        c["obligations"].append(extra)
        p = contracts.structural(c, frc.validate(c))
        with self.assertRaises(Failure):
            contracts.coverage(c, p)
        extra["relation"]["parameters"] = {"predicate": "human prose only"}
        p = contracts.structural(c, frc.validate(c))
        with self.assertRaises(Failure):
            contracts.coverage(c, p)

    def test_v1_gap_is_not_opaque_serialization_success(self):
        c, p, b, a = self.chain(queries()[0])
        with self.assertRaises(Failure):
            historical.faithful_v1(c)
        doc = contracts.document(c, p)
        for facet in language.FACETS:
            corrupt = copy.deepcopy(doc); corrupt["queries"][0][facet] = None
            with self.subTest(facet=facet), self.assertRaises(language.QueryError):
                contracts.recover(corrupt)

    def test_identifier_renaming_does_not_change_applicability(self):
        q = queries()[0]; q["id"] = "unrelated_new_public_query"
        c, p, b, a = self.chain(q, "Public independent query with all declared policies.")
        self.assertEqual(a["outcome"], "IMPLEMENTATION_ADEQUATE")

    def test_readonly_authority_remains_material_in_adequacy(self):
        from benchmark.evaluation import implementation_adequacy_r5_81 as adequacy
        c, p, b, a = self.chain(queries()[0])
        sidecar = copy.deepcopy(a["sidecar"])
        decision = next(d for d in sidecar["decisions"] if d["id"].endswith("query_effect"))
        decision["clauses"] = []
        self.assertEqual(adequacy.analyze(c, sidecar)["status"], "IMPLEMENTATION_UNDERSPECIFIED")
        sidecar = copy.deepcopy(a["sidecar"])
        decision = next(d for d in sidecar["decisions"] if d["id"].endswith("query_effect"))
        clause = copy.deepcopy(decision["clauses"][0]); clause["allowed"] = [decision["options"][1]]
        decision["clauses"].append(clause)
        self.assertEqual(adequacy.analyze(c, sidecar)["status"], "CONFLICTING_REQUIREMENT")

    def test_memory_frame_and_detached_results(self):
        from air_compiler.collection_query_runtime import execute, ApplicationError
        from test_collection_query_behavior import PRODUCTS
        q = queries()[0]
        records = copy.deepcopy(PRODUCTS); before = copy.deepcopy(records)
        result = execute(q, records, {"requested_category": "BOOK"})
        result[0]["category"] = "changed by consumer"
        self.assertEqual(records, before)
        with self.assertRaises(ApplicationError):
            execute(q, records, {"requested_category": " "})
        self.assertEqual(records, before)

    def test_multiple_query_composition_in_one_contract(self):
        import hashlib
        parts = [contract(q) for q in queries()]
        c = copy.deepcopy(parts[0])
        c["contract_id"] = "query-corpus"
        c["source"]["text"] = "\n".join(p["source"]["text"] for p in parts)
        c["source"]["sha256"] = hashlib.sha256(c["source"]["text"].encode()).hexdigest()
        c["obligations"] = [o for p in parts for o in p["obligations"]]
        p = contracts.structural(c, frc.validate(c))
        self.assertEqual(contracts.coverage(c, p)["obligations"], 54)
        self.assertEqual(len(compile_document(contracts.document(c, p))), 6)


if __name__ == "__main__":
    unittest.main()
