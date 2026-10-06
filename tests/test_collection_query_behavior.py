"""External process oracle: expected IDs are literal, not computed by query code."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from air_compiler.collection_query import generate
from lykoi_query.corpus import queries
from lykoi_query.corpus import contract
from lykoi_query import contracts
from lykoi_query.compiler import compile_document
from benchmark.evaluation import formal_requirements_r5_80 as frc


PRODUCTS = [
    {"sku": "Z", "category": "Book", "discontinued": False},
    {"sku": "B", "category": "BOOK", "discontinued": True},
    {"sku": "A", "category": "BOOK", "discontinued": False},
    {"sku": "W", "category": " BOOK ", "discontinued": True},
    {"sku": "X", "category": "Music", "discontinued": False},
]
USERS = [
    {"id": 1, "department": "Sales", "last_name": "Zed", "inactive": False},
    {"id": 2, "department": "Sales", "last_name": "Able", "inactive": True},
    {"id": 3, "department": "Sales", "last_name": "Able", "inactive": False},
    {"id": 4, "department": "sales", "last_name": "Able", "inactive": False},
]
ARCHIVES = [
    {"id": "z", "owner": "Ada", "created_at": 2, "archived": False},
    {"id": "b", "owner": "Ada", "created_at": 1, "archived": True},
    {"id": "a", "owner": "Ada", "created_at": 1, "archived": False},
    {"id": "x", "owner": "Bea", "created_at": 0, "archived": True},
]
LABELS = [
    {"id": "z", "labels": ["blue", "blue"], "created_at": 2, "archived": True},
    {"id": "b", "labels": ["blue"], "created_at": 1, "archived": True},
    {"id": "a", "labels": ["blue"], "created_at": 1, "archived": False},
    {"id": "x", "labels": ["Blue"], "created_at": 0, "archived": True},
    {"id": "w", "labels": [" blue "], "created_at": 3, "archived": False},
]


class ExternalQueryTests(unittest.TestCase):
    def run_query(self, query, records, value, expected, *, error=None, absent=False):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target, store = root / "query.py", root / "records.json"
            c = contract(query, "Explicit synthetic query policies as recorded; independent external expectations.")
            p = contracts.structural(c, frc.validate(c))
            code = compile_document(contracts.document(c, p))[query["id"]]
            target.write_text(code, encoding="utf-8")
            before = (json.dumps(records, indent=3) + "\n").encode()
            if not absent:
                store.write_bytes(before)
            process = subprocess.run([sys.executable, "-I", str(target), "--store", str(store),
                                      "--" + next(iter(query["parameters"])), value], cwd=root,
                                     capture_output=True, text=True, encoding="utf-8", timeout=20)
            self.assertEqual(process.returncode, 1 if error else 0, process.stderr)
            if error:
                self.assertEqual(process.stdout, "")
                self.assertEqual(json.loads(process.stderr), {"error": error})
            else:
                self.assertEqual(process.stderr, "")
                result = json.loads(process.stdout)
                self.assertEqual(None if result is None else [r[query["source"]["unique_key"]] for r in result], expected)
                if result:
                    originals = {r[query["source"]["unique_key"]]: r for r in records}
                    self.assertTrue(all(r == originals[r[query["source"]["unique_key"]]] for r in result))
            self.assertEqual(store.exists(), not absent)
            if not absent:
                self.assertEqual(store.read_bytes(), before)

    def test_exact_no_normalization_and_alternate_state(self):
        q = queries()[0]
        for value, ids in [("BOOK", ["A", "B"]), ("Book", ["Z"]), ("book", []),
                           (" BOOK ", ["W"]), ("missing", [])]:
            with self.subTest(value=value):
                self.run_query(q, PRODUCTS, value, ids)

    def test_validation_error_not_empty_result(self):
        for q, records in zip(queries(), [PRODUCTS, USERS, ARCHIVES, PRODUCTS, PRODUCTS, LABELS]):
            for value in ("", " \t\n", "\u2003"):
                with self.subTest(query=q["id"], value=value):
                    self.run_query(q, records, value, None, error=q["validation"][0]["error"])

    def test_multi_key_precedence_and_direction(self):
        self.run_query(queries()[1], USERS, "Sales", [3, 2, 1])
        self.run_query(queries()[2], ARCHIVES, "Ada", ["a", "b", "z"])

    def test_deliberate_casefold_and_strip_contrasts(self):
        self.run_query(queries()[3], PRODUCTS, "book", ["A", "B", "Z"])
        self.run_query(queries()[3], PRODUCTS, " book ", ["W"])
        self.run_query(queries()[4], PRODUCTS, " BOOK ", ["A", "B", "W"])
        self.run_query(queries()[4], PRODUCTS, "book", [])

    def test_collection_membership_once_and_archived_inclusion(self):
        q = queries()[5]
        self.run_query(q, LABELS, "blue", ["z", "a", "b"])
        self.run_query(q, LABELS, "Blue", ["x"])
        self.run_query(q, LABELS, " blue ", ["w"])

    def test_absent_storage_success_and_error_preserve_absence(self):
        q = queries()[0]
        self.run_query(q, [], "BOOK", [], absent=True)
        self.run_query(q, [], " ", None, error="invalid_category", absent=True)

    def test_no_match_error_null_distinct_and_state_unchanged(self):
        q = queries()[0]
        q["result"].update(no_match="error", error="not_found")
        self.run_query(q, PRODUCTS, "absent", None, error="not_found")
        q["result"].pop("error"); q["result"]["no_match"] = "null"
        self.run_query(q, PRODUCTS, "absent", None)

    def test_declared_exclusion_and_validation_contrast(self):
        q = queries()[0]
        q["inclusion"] = [{"field": "discontinued", "mode": "equals", "value": False}]
        self.run_query(q, PRODUCTS, "BOOK", ["A"])
        q["validation"] = []
        self.run_query(q, PRODUCTS, " ", [])
        q["validation"] = [{"parameter": "requested_category", "rule": "nonempty", "error": "empty_only"}]
        self.run_query(q, PRODUCTS, " ", [])

    def test_constant_operand_does_not_use_input(self):
        q = queries()[0]; q["predicate"]["operand"] = {"constant": "BOOK"}
        self.run_query(q, PRODUCTS, "Music", ["A", "B"])

    def test_invalid_record_state_is_not_silently_filtered(self):
        q = queries()[0]
        invalid = copy.deepcopy(PRODUCTS); invalid[-1]["category"] = 5
        self.run_query(q, invalid, "BOOK", None, error="invalid_state")
        duplicate = PRODUCTS + [PRODUCTS[0]]
        self.run_query(q, duplicate, "BOOK", None, error="invalid_state")


if __name__ == "__main__":
    unittest.main()
