"""Public multi-domain source interpretations captured by the active AI in R5.102.

These are producer outputs, not an English parser or injected middle artifacts.
Source-only review/oracles share an agent: process separation is not cognition.
"""
import copy
import hashlib

from lykoi_controller import canonical
from lykoi_pipeline.scalar_profile import PROFILE
from .producers import ModelAdapter


def captures():
    result = []
    for domain, label, values, initial, target in (
        ("library", "caption", ["REFERENCE", "LOAN"], "available", "checked_out"),
        ("laboratory", "specimen", ["CONTROL", "SAMPLE"], "received", "processed"),
        ("gallery", "inscription", ["PUBLIC", "PRIVATE"], "draft", "published"),
    ):
        fields = [{"name": n, "type": t, "domain": enum, "nullable": nullable, "preservation": "verbatim"} for n, t, enum, nullable in (
            ("id", "identifier", [], False), (label, "string", [], False), ("state", "enum", [initial, target], False),
            ("class", "enum", values, False), ("reference", "string", [], False), ("created_at", "timestamp", [], False), ("review_at", "timestamp", [], True))]
        bindings = []
        for n, source, value, default in (("id", "uuid_v4", None, None), (label, "input", None, None),
            ("state", "literal", initial, None), ("class", "input", None, values[0]), ("reference", "input", None, ""),
            ("created_at", "utc_clock", None, None), ("review_at", "input", None, "NULL")):
            bindings.append({"field": n, "source": source, "value": value, "default": None if default is None else {"value": None if default == "NULL" else default, "trigger": "omitted", "boundary": "creation"}})
        source = (f"For the {domain} registry, register a record with a required nonblank {label}; retain all supplied characters exactly, including spaces. "
                  f"Each record has a new UUID id and current UTC created_at from declared ID and clock resources. State starts {initial}. "
                  f"Class is exactly one of {values}; omitted class on registration defaults to {values[0]}. Optional reference defaults to an empty string only when omitted on registration, otherwise retain it verbatim. "
                  "Optional review_at is a valid UTC timestamp string retained verbatim, with null on omission; no other nullable fields. Blank label fails invalid_label; invalid review_at fails invalid_review. "
                  f"List returns whole records by created_at then id ascending. Advance by id permits only {initial} to {target}; missing identity fails record_not_found, repeat or illegal state fails invalid_transition. "
                  f"Persist in {domain}.json with atomic writes; missing file is empty. Rejections preserve stored bytes and unrelated fields. Schema version 2 introduces reference; explicit migrate assigns empty reference to version-1 records and preserves all other values. Migration is atomic, repeat migration changes nothing. "
                  "Creation defaults do not authorize any other historical repair. Other fields already exist in version 1. Enum input membership is enforced by the existing CLI choices policy.")
        facts = {"storage": {"path": domain + ".json", "version": 2, "missing": "empty_collection", "write": "atomic", "rejection": "unchanged"},
                 "fields": fields, "creation": {"command": "register", "bindings": bindings, "validation": [{"field": label, "rule": "nonblank", "error": "invalid_label"}, {"field": "review_at", "rule": "timestamp_utc", "error": "invalid_review"}]},
                 "listing": {"command": "list", "order": ["created_at", "id"], "result": "whole_records"},
                 "lifecycle": [{"field": "state", "initial": initial, "source": initial, "target": target, "command": "advance", "missing_error": "record_not_found", "transition_error": "invalid_transition", "rejection": "unchanged"}],
                 "evolution": [{"from": 1, "to": 2, "defaults": {"reference": ""}, "boundary": "explicit_migration", "preservation": "unrelated_fields"}]}
        result.append({"id": domain, "label": label, "source": source, "facts": facts, "initial": initial, "target": target, "values": values})
    return result


def obligations(record):
    return [{"id": record["id"] + "/" + facet, "basis": "STATED", "source_quote": record["source"], "derived_from": [],
             "statement": "Source-authorized " + facet + " for " + record["id"],
             "relation": {"kind": "crud", "parameters": {"profile": PROFILE, "facet": facet, "value": copy.deepcopy(value)}}} for facet, value in record["facts"].items()]


def producer(record, role):
    def invoke(request):
        assert request["source"]["text"] == record["source"]
        rows = obligations(record)
        refs = [e["identity"] for e in request["evidence"] if e["provenance"] == "human_statement"]
        authority = {o["id"]: refs for o in rows}
        domains = {"capability_profile": PROFILE, **copy.deepcopy(record.get("domains", {}))}
        if role == "formalizer":
            return {"obligations": rows, "authority": authority, "domains": domains, "questions": [], "issues": [], "lineage": [], "policy_applications": []}
        source = request["source"]
        source_record = {"id": source["identity"], "text": source["text"], "classification": "SYNTHETIC", "sha256": hashlib.sha256(source["text"].encode()).hexdigest()}
        inventory = {"version": "SourceObligationInventory-0.1", "source_commitment": hashlib.sha256(canonical({"revision": source["revision"], "record": source_record})).hexdigest(),
                     "extractor": "R5.102-source-only-active-agent-capture", "context_class": "SAME_AGENT_ANALYTICAL_CAPTURE",
                     "items": [{"id": o["id"], "spans": [{"start": 0, "end": len(record["source"]), "quote": record["source"]}], "meaning": o["statement"], "category": "BEHAVIOR", "material": True, "dependencies": []} for o in rows],
                     "questions": [], "limitations": ["Same-agent captured interpretation; no independent cognition; synthetic owner actions"]}
        return {"inventory": inventory, "interpretations": {o["id"]: {"statement": "Independent display " + o["id"], "relation": o["relation"]} for o in rows}, "authority": authority, "domains": domains}
    return ModelAdapter(role, record["id"] + ":" + role, invoke, provider="OpenAI", model="openai/gpt-6.1-sol/active-agent-capture")
