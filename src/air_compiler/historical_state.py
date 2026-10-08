"""Explicit additive related-state evolution; creation authority is never consulted."""
import copy

from .references import keys, require, erase
from .mutable_values import valid_value
from .predicates import same_type

VERSION = "historical-related-state-1"


def validate(facts, references, model):
    keys(facts, ("steps", "invalid", "rejection", "preservation"))
    require(facts["invalid"] == "invalid_state" and facts["rejection"] == "unchanged" and facts["preservation"] == "unrelated_fields", "Explicit historical rejection/preservation")
    types = references["types"]
    primary = references["facts"]["primary"]
    require(all(r["migration"] is None for r in references["facts"]["references"]), "Additive historical authority cannot silently mix legacy missing-or-empty repair")
    steps = facts["steps"]
    require(type(steps) is list and bool(steps), "Explicit historical introduction authority")
    introduced, boundaries = set(), set()
    for step in steps:
        keys(step, ("from", "to", "entities"))
        require(type(step["from"]) is int and 1 <= step["from"] and type(step["to"]) is int and step["to"] == step["from"] + 1 and step["to"] <= model["state"][0]["schema_version"] and step["from"] not in boundaries, "Unique additive version transition")
        boundaries.add(step["from"])
        require(type(step["entities"]) is list and bool(step["entities"]), "Nonempty related introductions")
        seen = set()
        for entity in step["entities"]:
            keys(entity, ("entity", "add_fields", "computations"))
            e = entity["entity"]
            require(e in types and e != primary and e not in seen, "Unique supported related entity")
            seen.add(e)
            require(type(entity["add_fields"]) is list and bool(entity["add_fields"]), "Explicit additive fields")
            for field in entity["add_fields"]:
                keys(field, ("field", "source"))
                n = field["field"]
                require(n in types[e] and n != references["identities"][e] and (e, n) not in introduced, "One introduction, immutable nominal identity")
                introduced.add((e, n))
    for step in steps:
        historical = copy.deepcopy(types)
        record = next(t for t in model["types"] if t["kind"] == "record")
        names = {f["id"]: f["name"] for f in record["fields"]}
        for migration in model["migrations"]:
            if migration["from_version"] >= step["from"]:
                for field in migration["add_fields"]: historical[primary].pop(names[field["field"]])
        for later in steps:
            if later["from"] >= step["from"]:
                for entity in later["entities"]:
                    for field in entity["add_fields"]: historical[entity["entity"]].pop(field["field"])
        for entity in step["entities"]:
            e, computed = entity["entity"], {}
            if entity["computations"] is not None:
                from .computation import validate as graph
                computed = graph(entity["computations"], historical, e, {})
            for field in entity["add_fields"]:
                s, target = field["source"], types[e][field["field"]]
                if s.get("kind") == "computed":
                    from .computation import bound
                    bound(s, computed, target)
                else:
                    keys(s, ("kind", "type", "value") if s.get("kind") == "literal" else ("kind", "type", "name"))
                    require(s.get("kind") in ("literal", "before") and same_type(s["type"], target), "Exact nominal migration source; no creation default")
                    require(valid_value(s["value"], erase(target)) if s["kind"] == "literal" else s["name"] in historical[e] and same_type(historical[e][s["name"]], target), "Authorized literal or existing historical field")
    return copy.deepcopy(facts)
