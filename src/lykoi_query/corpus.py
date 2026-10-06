"""New synthetic/public query requirements. No benchmark-source dispatch."""
import copy
import hashlib

from air_compiler.collection_query import FACETS
from benchmark.evaluation import formal_requirements_r5_80 as frc


REQUIREMENTS = {
    "products": "Return all products whose category equals the runtime requested_category, case-sensitively with no normalization (spaces significant). Order by sku ascending. Include discontinued products. Reject empty or whitespace-only requested_category with invalid_category. No matches returns an empty collection. This query leaves memory and persisted bytes/file absence unchanged on success and error.",
    "users": "Return all users whose department equals runtime requested_department, case-sensitive without normalization. Order by last_name ascending then id descending. Include inactive users. Reject empty or whitespace-only requested_department with invalid_department. No matches returns an empty collection. State and persistence remain unchanged on success and rejection.",
    "archives": "Return all documents whose owner equals runtime requested_owner, case-sensitive without normalization. Order by created_at ascending then id ascending. Include archived documents. Reject empty or whitespace-only requested_owner with invalid_owner. No matches returns an empty collection. State and persistence remain unchanged on success and rejection.",
    "folded_products": "Return products by runtime requested_category using Unicode casefold equality, with no whitespace normalization. Order by sku ascending and include discontinued products. Reject empty or whitespace-only input with invalid_category. No matches returns an empty collection. State and persistence remain unchanged on success and rejection.",
    "trimmed_products": "Return products by runtime requested_category using case-sensitive equality after stripping leading/trailing Unicode whitespace from both operands. Order by sku ascending and include discontinued products. Reject empty or whitespace-only input with invalid_category. No matches returns an empty collection. State and persistence remain unchanged on success and rejection.",
    "document_labels": "Return all documents with a labels member exactly equal to runtime requested_label, case-sensitive and without normalization. Each document appears once even with repeated labels. Order by created_at descending then id ascending. Include archived documents. Reject empty or whitespace-only requested_label with invalid_label. No matches returns an empty collection. State and persistence remain unchanged on success and rejection.",
}


def base(identity, fields, key, parameter, field, ordering, inclusion, error, operator="equals"):
    return {"id": identity,
            "source": {"collection": identity, "fields": fields, "unique_key": key},
            "parameters": {parameter: "string"},
            "predicate": {"field": field, "operator": operator, "operand": {"parameter": parameter}},
            "comparison": {"case": "sensitive", "normalization": "none"},
            "ordering": [{"field": f, "direction": d} for f, d in ordering],
            "validation": [{"parameter": parameter, "rule": "nonblank", "error": error}],
            "inclusion": [{"field": inclusion, "mode": "all"}],
            "effect": {"state": "read_only", "persistence": "unchanged"},
            "result": {"shape": "collection", "cardinality": "zero_or_more", "no_match": "empty"}}


def queries():
    products = base("products", {"sku": "string", "category": "string", "discontinued": "boolean"}, "sku",
                    "requested_category", "category", [("sku", "ASC")], "discontinued", "invalid_category")
    users = base("users", {"id": "integer", "department": "string", "last_name": "string", "inactive": "boolean"},
                 "id", "requested_department", "department", [("last_name", "ASC"), ("id", "DESC")], "inactive", "invalid_department")
    archives = base("archives", {"id": "string", "owner": "string", "created_at": "integer", "archived": "boolean"},
                    "id", "requested_owner", "owner", [("created_at", "ASC"), ("id", "ASC")], "archived", "invalid_owner")
    labels = base("document_labels", {"id": "string", "labels": "strings", "created_at": "integer", "archived": "boolean"},
                  "id", "requested_label", "labels", [("created_at", "DESC"), ("id", "ASC")], "archived", "invalid_label", "contains")
    folded, trimmed = copy.deepcopy(products), copy.deepcopy(products)
    folded["id"] = folded["source"]["collection"] = "folded_products"
    folded["comparison"]["case"] = "casefold"
    trimmed["id"] = trimmed["source"]["collection"] = "trimmed_products"
    trimmed["comparison"]["normalization"] = "strip"
    return [products, users, archives, folded, trimmed, labels]


def contract(query, source=None):
    source = source or REQUIREMENTS[query["id"]]
    obligations = [{"id": query["id"] + "/" + facet, "basis": "STATED", "source_quote": source,
                    "derived_from": [], "relation": {"kind": "filter_order", "parameters": {
                        "query": query["id"], "facet": facet, "value": copy.deepcopy(query[facet])}},
                    "statement": "Declared query " + facet} for facet in FACETS]
    result = {"schema_version": frc.VERSION, "contract_id": query["id"], "revision": 1,
              "source": {"id": query["id"], "text": source, "sha256": hashlib.sha256(source.encode()).hexdigest(),
                         "classification": "SYNTHETIC"},
              "context": {"scope": "Read-only parameterized collection query", "domains": {
                  "text": "Unicode strings; exact codepoint equality or explicit casefold; strip uses Python Unicode whitespace",
                  "state": "JSON array of exactly declared typed records, unique identity; missing file is empty collection"},
                  "assumptions": [], "component_authority": None},
              "obligations": obligations, "issues": [], "unspecified": [], "implementation_choices": [],
              "lineage": [], "formalizer": "R5.98 synthetic semantic corpus", "review": None}
    frc.validate(result)
    return result
