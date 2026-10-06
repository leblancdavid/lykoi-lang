"""Closed complete pattern registry, not a generic relation fallback."""
import copy

from lykoi_controller import Failure
from lykoi_pipeline import contracts
from lykoi_pipeline.controller import digest

TITLE = {"kind": "crud", "parameters": {"domain": "task creation", "result": "supplied title"}}
REGISTRY = {
    "version": "qualified-task-create-mappings-1",
    "mappings": [
        {"id": "task-title-create-1", "pattern": "exactly one STATED TITLE relation",
         "v1": "exact ID, statement and relation parameters; task-create declarative application",
         "preservation": "All normative relation atoms, statements and IDs retained; unspecified behavior not constrained",
         "evidence": "tests/test_public_rehearsal.py: mapping preservation and external calibration",
         "unsupported": "Any second obligation, context authority, richer title/domain/frame semantics"},
        {"id": "task-title-default-create-1", "pattern": "exactly one TITLE and one STATED omitted-priority relation",
         "v1": "exact ID, statement and relation parameters, including LOW/NORMAL/HIGH value",
         "preservation": "TITLE plus exact default preserved; no implicit priority requirement",
         "evidence": "tests/test_public_rehearsal.py: all enum boundaries and wrong-default rejection",
         "unsupported": "Any additional obligation, ordering, cardinality, filtering, default condition variation"}
    ]
}


def select(contract):
    contracts.frc.validate(contract)
    context = contract["context"]
    rows = contract["obligations"]
    title = [o for o in rows if o["relation"] == TITLE]
    default = [o for o in rows if o["relation"] in [
        {"kind": "priority_create", "parameters": {"condition": "priority omitted", "result": p}}
        for p in ("LOW", "NORMAL", "HIGH")]]
    if (contract["issues"] or context["component_authority"] is not None
            or context["domains"] or context["assumptions"]
            or any(o["basis"] != "STATED" or o["derived_from"] for o in rows)
            or len(title) != 1 or len(default) > 1 or len(rows) != 1 + len(default)):
        raise Failure("UNREPRESENTABLE_SOURCE", gap="NO_QUALIFIED_COMPLETE_MAPPING")
    return "task-title-default-create-1" if default else "task-title-create-1"


def project(contract):
    mapping = select(contract)
    # V1's existing declarative containers require complete envelope fields. These
    # describe this projection's observation scope, not invented baseline behavior.
    config = {"transport": {"operations": [], "failures": {}, "persistence": {"missing": "unspecified", "initial": None}},
              "state": {"version": "1", "versions": {"1": {"record": {}}}, "alternatives": {}, "initial": {}},
              "launch": {"id": "task-create-public", "store": {"base": "cwd", "path": "tasks.json", "parent": "existing"},
                         "trace": {"mode": "none", "directory": {"base": "cwd", "path": ".", "parent": "existing"}},
                         "runtime": "CPython", "provider": {"mode": "production", "types": {}, "values": {}}}}
    document = {"schema_version": contracts.v1.VERSION, "document_id": "rehearsal-" + digest(contract),
                "role": "behavioral", "payload": {
                    "application": {"id": "task-create-observation-scope", "state": {"versions": {"1": {"record": {}}}},
                                    "operations": {o["id"]: copy.deepcopy(o["relation"]) for o in contract["obligations"]}},
                    "configuration": config, "obligations": [
                        {"id": o["id"], "requirement": {"kind": o["relation"]["kind"], "statement": o["statement"], **copy.deepcopy(o["relation"]["parameters"])}}
                        for o in contract["obligations"]]}}
    normalized = contracts.v1.assemble([document])
    recovered = {o["id"]: {"kind": o["requirement"]["kind"], "parameters": {
        k: v for k, v in o["requirement"].items() if k not in {"kind", "statement"}}} for o in normalized["obligations"]}
    if recovered != {o["id"]: o["relation"] for o in contract["obligations"]}:
        raise Failure("UNREPRESENTABLE_SOURCE", gap="PRESERVATION_FAILURE")
    if {o["id"]: o["requirement"]["statement"] for o in normalized["obligations"]} != {o["id"]: o["statement"] for o in contract["obligations"]}:
        raise Failure("UNREPRESENTABLE_SOURCE", gap="PRESERVATION_FAILURE")
    return {"version": contracts.v1.VERSION, "outcome": "FAITHFUL_COMPLETE", "mapping": mapping,
            "document": document, "normalized": normalized,
            "coverage": [{"frc_id": o["id"], "v1_id": o["id"]} for o in contract["obligations"]]}
