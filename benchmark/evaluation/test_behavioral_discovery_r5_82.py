import copy
import unittest
from benchmark.evaluation.behavioral_discovery_r5_82 import discover, adequacy_sidecar
from benchmark.results.phase5c.r5_82.experiment import run, inputs, load


class DiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result = run()

    def test_supported_coverage_and_disclosed_gaps(self):
        coverage = self.result["coverage"]
        self.assertEqual(coverage["fp"], 0)
        self.assertEqual(coverage["fn"], 4)
        recorded = load("results.json")["coverage"]
        for actual, saved in (("tp", "true_positives"), ("fp", "false_positives"),
                              ("fn", "false_negatives"), ("correctly_rejected", "correctly_rejected_irrelevant_choices")):
            self.assertEqual(coverage[actual], recorded[saved])

    def test_hidden_interactions(self):
        for row in self.result["hidden_challenge"].values():
            self.assertEqual(row["fn"], [])

    def test_all_mutations(self):
        for row in self.result["mutations"]:
            with self.subTest(row=row["id"]):
                self.assertTrue(row["pass"])

    def test_plan_divergences_in_inventory(self):
        self.assertTrue(all(p["covered"] for p in self.result["plans"]))

    def test_adequacy_separate_from_discovery(self):
        a = self.result["adequacy"]
        self.assertEqual(a["delegated"]["status"], "IMPLEMENTATION_ADEQUATE")
        self.assertEqual(a["omitted"]["status"], "IMPLEMENTATION_UNDERSPECIFIED")
        self.assertEqual(a["unreviewed"]["status"], "OUTSIDE_ANALYSIS_SCOPE")

    def test_b01_conditional_not_resolved(self):
        b = self.result["B01"]
        self.assertEqual(b["decisions"][0]["family"], "default_trigger_domain")
        self.assertFalse(b["authoring_authorized"])
        self.assertIsNone(b["decisions"][0]["authority"])
        self.assertEqual(b["adequacy"]["status"], "NEEDS_CLARIFICATION")

    def test_fact_provenance_and_inhibitors(self):
        for bdi in self.result["inventories"].values():
            for d in bdi["decisions"]:
                self.assertTrue(d["origins"])
                self.assertTrue(d["facts"])
        self.assertIn("tie", self.result["coverage"]["cases"]["unique-score"]["correctly_rejected"])

    def test_missing_scope_is_unknown(self):
        c = {"id":"x","source":"Return many items","facts":{"collection":True,"max_results":"many","order_varies":True},"channels":{}}
        bdi = discover(*inputs(c))
        self.assertEqual(bdi["decisions"], [])
        self.assertTrue(bdi["unknown"])

    def test_no_undeclared_unique_invariant(self):
        c = next(c for c in load("corpus.json")["cases"] if c["id"] == "unique-score")
        c = copy.deepcopy(c); del c["facts"]["unique_match"]
        self.assertIn("tie", [d["family"] for d in discover(*inputs(c))["decisions"]])

    def test_identity_stable_under_metadata(self):
        c = load("corpus.json")["cases"][1]
        before = discover(*inputs(c)); c = copy.deepcopy(c); c["metadata"] = "unrelated"
        self.assertEqual(before, discover(*inputs(c)))
        before["decisions"][0]["alternatives"].append("mutated")
        self.assertNotEqual(before, discover(*inputs(c)))

    def test_stale_adapter_rejects(self):
        c, i = inputs(load("corpus.json")["cases"][1]); b = discover(c, i)
        c["source"] += " changed"
        with self.assertRaises(ValueError):
            adequacy_sidecar(c, b)

    def test_invalid_trace_and_operation_reject(self):
        c, i = inputs(load("corpus.json")["cases"][1])
        i["operations"].append(copy.deepcopy(i["operations"][0]))
        with self.assertRaises(ValueError):
            discover(c, i)
        i["operations"].pop(); i["operations"][0]["facts"]["selection"]["origin"] = []
        with self.assertRaises(ValueError):
            discover(c, i)

    def test_finite_implication_domains(self):
        self.assertTrue(all(r["matches_expected"] for r in self.result["finite_implications"]))
        tie = self.result["finite_implications"][0]["inventory"]
        d = next(d for d in tie["decisions"] if d["family"] == "tie")
        self.assertEqual(d["evidence"], "MECHANICALLY_DERIVED_FINITE")
        self.assertIn([7, 7], d["witnesses"])

    def test_finite_contradiction_and_nonexhaustive_reject(self):
        c, i = inputs(load("corpus.json")["cases"][4])
        i["operations"][0]["finite_domain"] = {"exhaustive":True,"origin":["domain"],"score_states":[[1,2]]}
        with self.assertRaises(ValueError):
            discover(c, i)
        i["operations"][0]["finite_domain"]["exhaustive"] = False
        with self.assertRaises(ValueError):
            discover(c, i)
        i["operations"][0]["finite_domain"] = {"exhaustive":True,"origin":["domain"],"score_states":[[float("nan")]]}
        with self.assertRaises(ValueError):
            discover(c, i)

    def test_identical_elements_have_no_order_distinction(self):
        c = {"id":"identical","source":"Return two equal scalar values", "facts":{
            "collection":True,"max_results":"many","order_varies":False},"channels":{"order":"MEANINGFUL"}}
        self.assertEqual(discover(*inputs(c))["decisions"], [])

    def test_unsupported_observation_cannot_pass_coverage(self):
        for key in ("timing-gap", "identity-gap", "event-gap"):
            self.assertTrue(self.result["inventories"][key]["unknown"])


if __name__ == "__main__":
    unittest.main()
