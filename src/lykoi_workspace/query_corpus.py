"""R5.99 active-agent formalization captures for human-style synthetic sources.

These are source-bound recorded AI interpretations, replayed for deterministic
regressions, not an English parser or a qualified live formalization service.
Only the producer emits typed FRC obligations; no query documents are injected.
The reviewer record is source-side analytical evidence in the same agent context.
"""
import copy
import hashlib

from lykoi_controller import canonical, Failure
from lykoi_workspace.producers import ModelAdapter

PRODUCT_CONTEXT = ("Products have unique string sku, string category and boolean discontinued fields. ")
PRODUCT_POLICY = ("Match case-sensitively with spaces preserved. Include discontinued products. "
                  "Reject empty or whitespace-only category input with invalid_category. "
                  "Return an empty collection when none match. Do not change memory or storage on success or error.")

# Typed relation values below are formalizer captures authored from the sources,
# rather than outputs manufactured by a prose-to-query mapping algorithm.
PRODUCT_FACTS = {
    "source": {"collection": "products", "fields": {"sku": "string", "category": "string", "discontinued": "boolean"}, "unique_key": "sku"},
    "parameters": {"category": "string"},
    "predicate": {"field": "category", "operator": "equals", "operand": {"parameter": "category"}},
    "comparison": {"case": "sensitive", "normalization": "none"},
    "ordering": [{"field": "sku", "direction": "ASC"}],
    "validation": [{"parameter": "category", "rule": "nonblank", "error": "invalid_category"}],
    "inclusion": [{"field": "discontinued", "mode": "all"}],
    "effect": {"state": "read_only", "persistence": "unchanged"},
    "result": {"shape": "collection", "cardinality": "zero_or_more", "no_match": "empty"},
}


def captures():
    """Records retain different prose, identical/distinct formalizer meaning."""
    a = PRODUCT_CONTEXT + "Show every product whose category exactly equals the supplied category, ordered by SKU ascending. " + PRODUCT_POLICY
    b = PRODUCT_CONTEXT + "Given a category, list products in ascending SKU order where the product category matches that input exactly. " + PRODUCT_POLICY
    records = [{"id": "products-a", "operation": "find-products", "source": a, "facts": copy.deepcopy(PRODUCT_FACTS)},
               {"id": "products-b", "operation": "find-products", "source": b, "facts": copy.deepcopy(PRODUCT_FACTS)}]
    neighbors = [
        ("casefold", "Match case-sensitively with spaces preserved.", "Match using Unicode casefold on both operands, with spaces preserved.", "comparison", {"case": "casefold", "normalization": "none"}),
        ("strip", "Match case-sensitively with spaces preserved.", "Match case-sensitively after trimming leading/trailing Unicode whitespace from both operands.", "comparison", {"case": "sensitive", "normalization": "strip"}),
        ("descending", "ordered by SKU ascending", "ordered by SKU descending", "ordering", [{"field": "sku", "direction": "DESC"}]),
        ("exclude", "Include discontinued products.", "Exclude discontinued products.", "inclusion", [{"field": "discontinued", "mode": "equals", "value": False}]),
        ("no-match-error", "Return an empty collection when none match.", "Report no_products error when none match.", "result", {"shape": "collection", "cardinality": "zero_or_more", "no_match": "error", "error": "no_products"}),
        ("mutating", "Do not change memory or storage on success or error.", "Mutate matching records and write storage.", "effect", {"state": "mutating", "persistence": "write"}),
        ("nonempty", "Reject empty or whitespace-only category input with invalid_category.", "Reject only the empty string category with invalid_category; whitespace-only values are valid.", "validation", [{"parameter": "category", "rule": "nonempty", "error": "invalid_category"}]),
    ]
    for identity, before, after, facet, value in neighbors:
        facts = copy.deepcopy(PRODUCT_FACTS)
        facts[facet] = value
        records.append({"id": identity, "operation": "find-products", "source": a.replace(before, after), "facts": facts})
    unresolved = copy.deepcopy(PRODUCT_FACTS)
    unresolved["comparison"] = None
    records.append({"id": "ambiguous-case", "operation": "find-products",
                    "source": a.replace("exactly equals", "matches").replace("Match case-sensitively with spaces preserved. ", ""),
                    "facts": unresolved, "question": "Should matching be case-sensitive, and should surrounding whitespace be preserved?"})
    docs = {
        "source": {"collection": "documents", "fields": {"id": "string", "labels": "strings", "created_at": "integer", "archived": "boolean"}, "unique_key": "id"},
        "parameters": {"label": "string"},
        "predicate": {"field": "labels", "operator": "contains", "operand": {"parameter": "label"}},
        "comparison": {"case": "sensitive", "normalization": "none"},
        "ordering": [{"field": "created_at", "direction": "DESC"}, {"field": "id", "direction": "ASC"}],
        "validation": [{"parameter": "label", "rule": "nonblank", "error": "invalid_label"}],
        "inclusion": [{"field": "archived", "mode": "all"}],
        "effect": {"state": "read_only", "persistence": "unchanged"},
        "result": {"shape": "collection", "cardinality": "zero_or_more", "no_match": "empty"},
    }
    records.extend([
        {"id": "documents-a", "operation": "find-documents", "facts": copy.deepcopy(docs),
         "source": "Documents have unique string id, string-list labels, integer created_at and boolean archived fields. Show all documents containing the supplied label, once per document. Compare case-sensitively, keeping spaces significant. Sort newest created_at first, then id ascending. Include archived documents. Reject blank or empty label with invalid_label. Return an empty list if nothing matches. Leave state and persisted bytes/file absence unchanged on success and error."},
        {"id": "documents-b", "operation": "find-documents", "facts": copy.deepcopy(docs),
         "source": "Documents have unique string id, string-list labels, integer created_at and boolean archived fields. Given a label string, return each document with an exactly equal labels member once. Use case-sensitive equality without whitespace normalization. Include archived records and order by created_at descending followed by id ascending. Empty or whitespace-only input is invalid_label. No matching document means an empty collection. This is read-only in memory and on disk, including failures and missing files."},
    ])
    archived_exclusion = copy.deepcopy(records[-2])
    archived_exclusion["id"] = "documents-exclude"
    archived_exclusion["source"] = archived_exclusion["source"].replace("Include archived documents.", "Exclude archived documents.")
    archived_exclusion["facts"]["inclusion"] = [{"field": "archived", "mode": "equals", "value": False}]
    records.append(archived_exclusion)
    users = {
        "source": {"collection": "users", "fields": {"id": "integer", "department": "string", "last_name": "string", "inactive": "boolean"}, "unique_key": "id"},
        "parameters": {"department": "string"},
        "predicate": {"field": "department", "operator": "equals", "operand": {"parameter": "department"}},
        "comparison": {"case": "sensitive", "normalization": "none"},
        "ordering": [{"field": "last_name", "direction": "ASC"}, {"field": "id", "direction": "DESC"}],
        "validation": [{"parameter": "department", "rule": "nonblank", "error": "invalid_department"}],
        "inclusion": [{"field": "inactive", "mode": "all"}],
        "effect": {"state": "read_only", "persistence": "unchanged"},
        "result": {"shape": "collection", "cardinality": "zero_or_more", "no_match": "empty"},
    }
    records.extend([
        {"id": "users-a", "operation": "find-users", "facts": copy.deepcopy(users),
         "source": "Users have unique integer id, string department, string last_name and boolean inactive fields. Show every user whose department equals the supplied department string exactly, case-sensitively and without trimming. Sort by last_name ascending then id descending. Include inactive users. Reject blank or empty department with invalid_department. No matches means an empty collection. Do not change memory or persisted bytes/file absence on success or error."},
        {"id": "users-b", "operation": "find-users", "facts": copy.deepcopy(users),
         "source": "Users have unique integer id, string department, string last_name and boolean inactive fields. Given a department, list all users in ascending last_name order with larger id first for equal surnames. Select users with a case-sensitive exact department match, preserving whitespace. Inactive users are included. Empty and whitespace-only input fails with invalid_department. Return an empty list when nothing matches. All state and persistence remain unchanged even on rejection or absent storage."},
    ])
    return records


def response(record, source, evidence, *, reviewer=False, previous=None):
    """Serialize a captured formalizer/SOI response, bound to its exact input.

    This replay interface is intentionally unable to interpret a new source.
    ModelAdapter callers can replace the capture with any actual AI invocation.
    """
    if source["text"] != record["source"]:
        raise Failure("CAPTURE_SOURCE_MISMATCH")
    refs = [e["identity"] for e in evidence if e["provenance"] in ("human_statement", "clarification_answer", "approved_policy")]
    rows = []
    for facet, value in record["facts"].items():
        rows.append({"id": record["operation"] + "/" + facet, "basis": "STATED", "source_quote": source["text"],
                     "derived_from": [], "statement": ("Source inventory: " if reviewer else "Query contract: ") + facet,
                     "relation": {"kind": "filter_order", "parameters": {"query": record["operation"], "facet": facet, "value": copy.deepcopy(value)}}})
    authority = {o["id"]: refs for o in rows}
    questions, issues = [], []
    if record.get("question"):
        affects = [record["operation"] + "/comparison"]
        questions = [{"id": "QUERY.COMPARISON", "text": record["question"], "priority": "BLOCKING", "affects": affects}]
        issues = [{"id": "ISSUE.COMPARISON", "category": "AMBIGUITY", "description": record["question"], "affects": affects,
                   "alternatives": [], "witness": None, "resolved": False}]
    domains = {"capability_profile": "collection-query-1", **copy.deepcopy(record.get("domains", {}))}
    if not reviewer:
        lineage = []
        if previous:
            old = {o["id"]: o for o in previous["obligations"]}
            lineage = [{"change": "meaning_change", "previous": [o["id"]], "current": [o["id"]], "reason": "Source-authorized clarification"}
                       for o in rows if o["id"] in old and o != old[o["id"]]]
        return {"obligations": rows, "authority": authority, "questions": questions, "issues": issues, "domains": domains,
                "lineage": lineage, "policy_applications": [{"policy": e["identity"], "mode": "DEFAULT"}
                    for e in evidence if e["provenance"] == "approved_policy"]}
    source_record = {"id": source["identity"], "text": source["text"], "classification": "SYNTHETIC",
                     "sha256": hashlib.sha256(source["text"].encode()).hexdigest()}
    inventory = {"version": "SourceObligationInventory-0.1", "source_commitment": hashlib.sha256(canonical({"revision": source["revision"], "record": source_record})).hexdigest(),
                 "extractor": "active-agent-source-side-capture", "context_class": "SAME_AGENT_ANALYTICAL_CAPTURE",
                 "items": [{"id": o["id"], "spans": [{"start": 0, "end": len(source["text"]), "quote": source["text"]}],
                            "meaning": o["statement"], "category": "BEHAVIOR", "material": True, "dependencies": []} for o in rows],
                 "questions": [q["text"] for q in questions], "limitations": ["Same-agent capture; no independent cognition/completeness proof"]}
    return {"inventory": inventory, "interpretations": {o["id"]: {k: o[k] for k in ("statement", "relation")} for o in rows},
            "authority": authority, "domains": domains}


def producer(record, role, *, previous=None, alter=None):
    def invoke(request):
        output = response(record, request["source"], request["evidence"], reviewer=role == "reviewer", previous=previous)
        if alter:
            alter(output)
        return output
    return ModelAdapter(role, record["id"] + ":" + role, invoke, provider="OpenAI",
                        model="openai/gpt-6.1-sol/recorded-active-agent-capture")
