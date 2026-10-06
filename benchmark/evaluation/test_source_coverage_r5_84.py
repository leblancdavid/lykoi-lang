"""Public tests only; no broad harness discovery or protected fixture imports."""
import copy
import unittest

from benchmark.evaluation import source_coverage_r5_84 as coverage
from benchmark.evaluation import formal_requirements_r5_80 as frc
from benchmark.evaluation.behavioral_discovery_r5_82 import discover, adequacy_sidecar
from benchmark.evaluation.implementation_adequacy_r5_81 import authorization
from benchmark.results.phase5c.r5_84.fixtures import (
    SOURCES, TARGETS, candidate, two_clause, review, run_bundle, omission,
)


class CoverageTests(unittest.TestCase):
    def deny(self, bundle):
        result = run_bundle(bundle)
        self.assertFalse(result["experimental_authorization"])
        self.assertFalse(result["production_authorization"])
        self.assertNotEqual(result["coverage"]["status"], "COVERAGE_APPROVED")
        return result

    def test_positive_control_and_production_separation(self):
        r = run_bundle(candidate("persistence"))
        self.assertEqual(r["coverage"]["status"], "COVERAGE_APPROVED")
        self.assertEqual(r["adequacy"], "IMPLEMENTATION_ADEQUATE")
        self.assertTrue(r["experimental_authorization"])
        self.assertFalse(r["production_authorization"])

    def test_all_public_source_capsules_have_exact_text_accountability(self):
        for source in SOURCES:
            with self.subTest(source=source["id"]):
                b = candidate(source["id"])
                frc.validate(b["contract"])
                r = run_bundle(b)
                self.assertNotIn("UNACCOUNTED_SOURCE_TEXT", r["coverage"]["findings"])
                self.assertFalse(any(f.startswith("INVALID_COVERAGE_EVIDENCE") for f in r["coverage"]["findings"]))

    def test_public_r5_83_negative_control_is_reproduced(self):
        from benchmark.results.phase5c.r5_83.audit import synthetic_probe
        result = synthetic_probe()
        self.assertFalse(result["declared_events"]["authorization_helper"])
        self.assertFalse(result["omitted_events_default_coverage"]["authorization_helper"])
        self.assertTrue(result["omitted_events_false_coverage_attestation"]["authorization_helper"])
        self.assertTrue(result["excluded_events_false_scope_attestation"]["authorization_helper"])

    def test_independent_disagreement_and_public_b01_calibration(self):
        from benchmark.results.phase5c.r5_84.qualify import independent_comparison, b01_calibration
        comparison = independent_comparison()
        self.assertEqual(len(comparison), 6)
        self.assertTrue(all(r["coverage"] == "COVERAGE_DISPUTED" and not r["authorized"] for r in comparison.values()))
        b01 = b01_calibration()
        self.assertEqual(b01["adequacy"], "NEEDS_CLARIFICATION")
        self.assertEqual(b01["discovery"], "NOT_RUN")
        self.assertFalse(b01["authorized"])

    def test_16_source_omissions_and_legacy_false_attestations(self):
        for label in TARGETS:
            with self.subTest(label=label):
                b = omission(label)
                self.deny(b)
                _, _, fidelity = review(b)
                old = adequacy_sidecar(b["contract"], discover(b["contract"], b["interface"]), True)
                self.assertTrue(authorization(b["contract"], fidelity, old))

    def test_16_structural_losses(self):
        for label in TARGETS:
            with self.subTest(label=label):
                self.deny(omission(label, structural=True))

    def test_16_incorrect_exclusions(self):
        for label in TARGETS:
            with self.subTest(label=label):
                b = two_clause(label)
                for r in b["source_map"]:
                    if r["id"].startswith("T"):
                        r.update(disposition="EXCLUDED", exclusion={"class": "EXPLICIT_NON_SEMANTIC",
                                 "premises": r["source_ids"], "rationale": "Formalizer says irrelevant"})
                self.deny(b)

    def test_four_unsupported_families_are_visible(self):
        for label in TARGETS[-4:]:
            with self.subTest(label=label):
                r = self.deny(candidate(label))
                self.assertTrue(r["coverage"]["source_coverage_approved"])
                self.assertEqual(r["coverage"]["status"], "STRUCTURAL_SCOPE_UNSUPPORTED")
                self.assertEqual(r["adequacy"], "OUTSIDE_ANALYSIS_SCOPE")

    def test_six_inventions(self):
        for invented in ("sorting", "default", "invalid_input_rejection", "persistence", "tie_break", "retry"):
            with self.subTest(invented=invented):
                b = candidate("persistence")
                o = copy.deepcopy(b["contract"]["obligations"][0])
                o.update(id="INVENTED", statement="Invented " + invented)
                b["contract"]["obligations"].append(o)
                r = self.deny(b)
                self.assertIn("INVENTED_OR_UNJUSTIFIED_FRC_OBLIGATION:INVENTED", r["coverage"]["findings"])

    def test_six_plausible_but_not_necessary_implications(self):
        for invented in ("sorting", "default", "invalid_input_rejection", "persistence", "tie_break", "retry"):
            with self.subTest(invented=invented):
                b = candidate("cross_clause")
                o = copy.deepcopy(b["contract"]["obligations"][0])
                o.update(id="O3", basis="NECESSARY_IMPLICATION", derived_from=["O1"], statement="Require " + invented)
                b["contract"]["obligations"].append(o)
                b["implications"] = [{"id": "N1", "premises": ["S1"], "result": "O3",
                    "inference_class": "REASONABLE_CONVENTION", "mode": "REVIEWER_DERIVED",
                    "rationale": "Seems like good design", "review_status": "APPROVED"}]
                r = self.deny(b)
                self.assertIn("UNSUPPORTED_INFERENCE_CLASS:N1", r["coverage"]["findings"])

    def test_one_to_many_many_to_one_mapping(self):
        b = candidate("optional_null")
        # One source inventory item, two formal clauses (not a required 1:1 mapping).
        b["soi"]["items"] = [{**b["soi"]["items"][0], "spans": [{"start": 0,
            "end": len(b["source"]["record"]["text"]), "quote": b["source"]["record"]["text"]}]}]
        b["source_map"] = [{"id": "M1", "source_ids": ["S1"], "obligation_ids": ["O1", "O2"], "disposition": "REPRESENTED"}]
        self.assertEqual(run_bundle(b)["coverage"]["status"], "COVERAGE_APPROVED")
        b = candidate("cross_clause")
        b["contract"]["obligations"] = [{**b["contract"]["obligations"][0],
            "statement": b["source"]["record"]["text"], "source_quote": b["source"]["record"]["text"]}]
        b["source_map"] = [{"id": "M1", "source_ids": ["S1", "S2"], "obligation_ids": ["O1"], "disposition": "REPRESENTED"}]
        b["structural_map"] = b["structural_map"][:1]
        self.assertEqual(run_bundle(b)["coverage"]["status"], "COVERAGE_APPROVED")

    def test_implication_provenance_and_plausible_nonnecessity(self):
        b = candidate("cross_clause")
        o = copy.deepcopy(b["contract"]["obligations"][0])
        o.update(id="O3", basis="NECESSARY_IMPLICATION", derived_from=["O1", "O2"],
                 statement="The returned singleton is active.")
        b["contract"]["obligations"].append(o)
        b["structural_map"].append({**copy.deepcopy(b["structural_map"][0]), "id": "P3", "obligation_id": "O3"})
        b["implications"] = [{"id": "N1", "premises": ["S1", "S2"], "result": "O3",
            "inference_class": "REVIEWER_NECESSITY", "mode": "REVIEWER_DERIVED",
            "rationale": "One record plus every returned record active entails active singleton",
            "denial_witness": "An inactive singleton violates S1; an empty result violates S2",
            "review_status": "APPROVED"}]
        self.assertEqual(run_bundle(b)["coverage"]["status"], "COVERAGE_APPROVED")
        b["implications"][0].update(inference_class="CONJUNCTION_ELIMINATION",
            mode="MECHANICAL_CONDITIONAL_ON_REVIEWED_PREMISES", premise_atoms=["active", "singleton"], conclusion="sorted")
        self.deny(b)
        b["implications"][0]["conclusion"] = "active"
        self.assertEqual(run_bundle(b)["coverage"]["status"], "COVERAGE_APPROVED")
        b["implications"][0]["premises"] = []
        self.deny(b)

    def test_ambiguity_conflict_and_disagreement(self):
        self.assertEqual(self.deny(candidate("ambiguity"))["adequacy"], "NEEDS_CLARIFICATION")
        self.assertEqual(self.deny(candidate("conflict"))["adequacy"], "CONFLICTING_REQUIREMENT")
        b = candidate("unreachable")
        b["disagreements"] = [{"source_id": "S1", "reviewers": ["A", "B"],
            "question": "Does admission bound govern exact returned collection?", "resolution": None}]
        self.assertEqual(self.deny(b)["coverage"]["status"], "COVERAGE_DISPUTED")

    def test_nonbehavioral_and_explicit_freedom_accounting(self):
        b = candidate("nonsemantic")
        r = run_bundle(b)
        self.assertTrue(r["coverage"]["source_coverage_approved"])
        b["source_map"][0].update(disposition="NONBEHAVIORAL", rationale="Incorrectly private")
        self.deny(b)
        b = candidate("freedom")
        self.assertEqual(run_bundle(b)["coverage"]["status"], "COVERAGE_APPROVED")
        b["source_map"] = b["source_map"][:1]
        self.deny(b)

    def test_exclusion_authority_classes(self):
        b = candidate("freedom")
        b["source_map"][1].update(disposition="EXCLUDED", exclusion={"class": "EXPLICIT_NON_SEMANTIC",
            "premises": ["S3"], "rationale": "Explicit consumer restriction on order"})
        self.assertEqual(run_bundle(b)["coverage"]["status"], "COVERAGE_APPROVED")
        b["source_map"][1]["exclusion"]["premises"] = ["S1"]
        self.deny(b)
        b = candidate("unreachable")
        b["source_map"][1].update(disposition="EXCLUDED", exclusion={"class": "MECHANICALLY_IRRELEVANT",
            "premises": ["S1"], "rationale": "Finite bound under declared exact-collection reading",
            "domain": {"exhaustive": True, "collections": [[], ["a"]]}})
        self.assertEqual(run_bundle(b)["coverage"]["status"], "COVERAGE_APPROVED")
        b["source_map"][1]["exclusion"]["domain"]["collections"].append(["a", "b"])
        self.deny(b)

    def test_mutations_and_nonsemantic_metadata_stability(self):
        base = candidate("persistence")
        receipt, admission, fidelity = review(base)
        modified = copy.deepcopy(base)
        modified["metadata"] = {"caption": "New display label"}
        modified["coverage_complete"] = True
        self.assertEqual(coverage.assess(base, receipt, admission), coverage.assess(modified, receipt, admission))
        mutations = [
            lambda b: b["contract"]["obligations"].clear(),
            lambda b: b["structural_map"].clear(),
            lambda b: b["interface"]["operations"][0]["facts"].pop("persist"),
            lambda b: b["interface"]["operations"][0]["channels"].clear(),
            lambda b: b["interface"]["operations"][0]["channels"].update(later="EXCLUDED"),
            lambda b: b["interface"]["operations"][0]["facts"]["failure_after_write"].update(value=True),
            lambda b: b["source"]["record"].update(text=b["source"]["record"]["text"] + " Emit a public event."),
            lambda b: b["soi"]["items"][0]["spans"][0].update(end=2),
            lambda b: b["questions"].append("Unresolved admitted domain"),
        ]
        for n, mutate in enumerate(mutations):
            with self.subTest(n=n):
                b = copy.deepcopy(base)
                mutate(b)
                self.assertNotEqual(coverage.assess(b, receipt, admission)["status"], "COVERAGE_APPROVED")
                self.deny(b)

    def test_consistent_source_extension_without_inventory_extension(self):
        b = candidate("persistence")
        text = b["source"]["record"]["text"] + " Emit a public event."
        import hashlib
        b["source"]["record"].update(text=text, sha256=hashlib.sha256(text.encode()).hexdigest())
        b["contract"]["source"] = copy.deepcopy(b["source"]["record"])
        b["soi"]["source_commitment"] = frc.digest(b["source"])
        r = self.deny(b)  # Even newly pinned review cannot hide unaccounted source text.
        self.assertIn("UNACCOUNTED_SOURCE_TEXT", r["coverage"]["findings"])

    def test_unreviewed_rejected_and_production_admission(self):
        b = candidate("persistence")
        receipt, admission, fidelity = review(b)
        for field, value in (("review_commitment", "wrong"), ("inventory_commitment", "wrong"), ("mode", "PRODUCTION")):
            with self.subTest(field=field):
                a = {**admission, field: value}
                self.assertFalse(coverage.downstream(b, receipt, a, fidelity)["experimental_authorization"])
        receipt["result"] = "COVERAGE_REJECTED"
        admission["review_commitment"] = frc.digest(receipt)
        self.assertFalse(coverage.downstream(b, receipt, admission, fidelity)["experimental_authorization"])
        self.assertFalse(coverage.downstream(b, None, admission, fidelity)["experimental_authorization"])
        self.assertFalse(coverage.downstream(b, {}, {}, fidelity)["experimental_authorization"])

    def test_review_dependent_exclusion_requires_inspectable_judgment(self):
        b = candidate("unreachable")
        b["source_map"][1].update(disposition="EXCLUDED", exclusion={"class": "REVIEWER_CLASSIFIED_IRRELEVANT",
            "premises": ["S1"], "rationale": "Conditional exact singleton-collection interpretation"})
        receipt, admission, fidelity = review(b)
        self.assertEqual(coverage.assess(b, receipt, admission)["status"], "COVERAGE_APPROVED")
        receipt["judgments"]["exclusion:M2"] = {"result": "UNDETERMINED", "rationale": "Scope not established"}
        admission["review_commitment"] = frc.digest(receipt)
        self.assertFalse(coverage.downstream(b, receipt, admission, fidelity)["experimental_authorization"])

    def test_invariant_weakening_invalidates_finite_exclusion(self):
        b = candidate("unreachable")
        b["source_map"][1].update(disposition="EXCLUDED", exclusion={"class": "MECHANICALLY_IRRELEVANT",
            "premises": ["S1"], "rationale": "Finite bound",
            "domain": {"exhaustive": True, "collections": [[], ["a"]]}})
        receipt, admission, _ = review(b)
        # A changed source bound requires a new inventory and review; cannot reuse proof.
        b["source"]["record"]["text"] = b["source"]["record"]["text"].replace("At most one", "At most two")
        self.assertNotEqual(coverage.assess(b, receipt, admission)["status"], "COVERAGE_APPROVED")

    def test_residual_dishonest_inventory_is_not_mechanically_solved(self):
        b = omission("event_count")
        # A colluding source extractor absorbs all text into one vague inventory item.
        # A dishonest reviewer then pins fresh bogus semantic evidence. This is not
        # the naked-boolean attack: it demonstrates the remaining authority gap.
        item = b["soi"]["items"][0]
        text = b["source"]["record"]["text"]
        item["spans"] = [{"start": 0, "end": len(text), "quote": text}]
        b["soi"]["items"] = [item]
        b["source_map"] = b["source_map"][:1]
        r = run_bundle(b)
        self.assertTrue(r["experimental_authorization"])
        self.assertFalse(r["production_authorization"])


if __name__ == "__main__":
    unittest.main()
