import copy
import unittest

from benchmark.evaluation.implementation_adequacy_r5_81 import analyze, authorization, commitment
from benchmark.results.phase5c.r5_81.experiment import fixtures, run


class AdequacyTests(unittest.TestCase):
    def setUp(self):
        self.cases = fixtures()

    def test_corpus_classifications(self):
        for key, (c, a, expected) in self.cases.items():
            with self.subTest(case=key):
                self.assertEqual(analyze(c, a)["status"], expected)

    def test_approval_does_not_authorize_incomplete(self):
        c, a, _ = self.cases["A-incomplete"]
        self.assertFalse(authorization(c, {"outcome": "APPROVED", "contract_commitment": commitment(c)}, a))

    def test_adequacy_without_fidelity_does_not_authorize(self):
        c, a, _ = self.cases["A-complete"]
        self.assertFalse(authorization(c, {"outcome": "NEEDS_CLARIFICATION", "contract_commitment": commitment(c)}, a))

    def test_separate_positive_authorization(self):
        c, a, _ = self.cases["A-complete"]
        self.assertTrue(authorization(c, {"outcome": "APPROVED", "contract_commitment": commitment(c)}, a))

    def test_stale_fidelity(self):
        c, a, _ = self.cases["A-complete"]
        self.assertFalse(authorization(c, {"outcome": "APPROVED", "contract_commitment": "stale"}, a))

    def test_stale_analysis(self):
        c, a, _ = self.cases["A-complete"]
        a = copy.deepcopy(a)
        a["contract_commitment"] = "stale"
        self.assertEqual(analyze(c, a)["status"], "OUTSIDE_ANALYSIS_SCOPE")

    def test_unreviewed_inventory(self):
        c, a, _ = self.cases["A-complete"]
        a = copy.deepcopy(a)
        a["coverage_reviewed"] = False
        self.assertEqual(analyze(c, a)["status"], "OUTSIDE_ANALYSIS_SCOPE")

    def test_explicit_freedom_not_silence(self):
        c, a, _ = self.cases["D-unconstrained"]
        self.assertEqual(analyze(c, a)["status"], "IMPLEMENTATION_ADEQUATE")
        a = copy.deepcopy(a)
        a["decisions"][0]["clauses"] = []
        self.assertEqual(analyze(c, a)["status"], "IMPLEMENTATION_UNDERSPECIFIED")

    def test_internal_and_excluded_choices(self):
        c, a, _ = self.cases["E-internal"]
        self.assertEqual(analyze(c, a)["status"], "IMPLEMENTATION_ADEQUATE")
        a = copy.deepcopy(a)
        a["decisions"][0]["relevance"] = "EXCLUDED"
        a["decisions"][0]["reason"] = "Outside declared exact-result observation interface."
        self.assertEqual(analyze(c, a)["status"], "IMPLEMENTATION_ADEQUATE")

    def test_conflict_and_ambiguity_block(self):
        for key in ("F-conflict", "G-ambiguity"):
            c, a, expected = self.cases[key]
            self.assertEqual(analyze(c, a)["status"], expected)
            self.assertFalse(authorization(c, {"outcome": "APPROVED", "contract_commitment": commitment(c)}, a))

    def test_mutations(self):
        evidence = run()
        self.assertEqual(len(evidence["mutations"]), 7)
        for result in evidence["mutations"].values():
            self.assertEqual(result["status"], "IMPLEMENTATION_UNDERSPECIFIED")
            self.assertEqual(len(result["missing_decisions"]), 1)
        self.assertEqual(evidence["internal_clause_removal"]["status"], "IMPLEMENTATION_ADEQUATE")

    def test_multiple_implementations(self):
        d = run()["divergence"]
        self.assertEqual(d["adequate_internal_strategy_agreements"], [True] * 5)
        for key in ("omitted_order_literal_outputs", "omitted_default_literal_outputs_query_zero", "omitted_tie_literal_outputs"):
            self.assertNotEqual(*d[key])
        self.assertTrue(d["freedom_membership_equivalent"])

    def test_stability(self):
        self.assertEqual(run(), run())

    def test_invalid_authority_and_domain(self):
        c, a, _ = self.cases["A-complete"]
        for value in ("invented", ""):
            changed = copy.deepcopy(a)
            changed["decisions"][0]["clauses"][0]["source_quote"] = value
            self.assertEqual(analyze(c, changed)["status"], "OUTSIDE_ANALYSIS_SCOPE")

    def test_malformed_receipt(self):
        c, a, _ = self.cases["A-complete"]
        self.assertFalse(authorization(c, [], a))

    def test_public_b01_and_fidelity_separation(self):
        public = run()["public"]
        self.assertTrue(all(r["fidelity_binding_matches"] for r in public.values()))
        self.assertEqual(public["S01"]["status"], "IMPLEMENTATION_ADEQUATE")
        self.assertEqual(public["B01"]["status"], "NEEDS_CLARIFICATION")
        self.assertFalse(public["B01"]["experimental_authorization"])
        for key in ("S02", "S10", "P01"):
            self.assertEqual(public[key]["fidelity_status"], "APPROVED")
            self.assertEqual(public[key]["status"], "OUTSIDE_ANALYSIS_SCOPE")

    def test_scope_and_empty_inventory_fail_closed(self):
        c, a, _ = self.cases["A-complete"]
        for field, value in (("scope", "narrowed"), ("decisions", [])):
            changed = copy.deepcopy(a)
            changed[field] = value
            self.assertEqual(analyze(c, changed)["status"], "OUTSIDE_ANALYSIS_SCOPE")

    def test_noncanonical_json_fails_closed(self):
        c, a, _ = self.cases["A-complete"]
        a = copy.deepcopy(a)
        a["unexpected"] = float("nan")
        self.assertEqual(analyze(c, a)["status"], "OUTSIDE_ANALYSIS_SCOPE")


if __name__ == "__main__":
    unittest.main(verbosity=2)
