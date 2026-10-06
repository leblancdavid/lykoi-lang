"""Versioned normal program/profile dispatcher; compatibility 0.3 is unchanged."""
import copy
import json
from pathlib import Path

from .collection_query import QueryError, require, validate as validate_query
from .generator import generate as generate_legacy
from .parser import parse
from .validator import validate as validate_legacy

VERSION = "LykoiProgram-1"


def validate_storage(storage, queries):
    try:
        program = validate_legacy(parse(json.dumps(storage["model"])))
        model = program.document
        state = next(s for s in model["state"] if s["id"] == storage["state"])
        types = {t["id"]: t for t in model["types"]}
        record = types[types[state["type"]]["item_type"]]
        fields = {f["name"]: f for f in record["fields"]}
        for q in queries:
            require(q["source"]["collection"] == state["id"], "Collection/state binding mismatch")
            for name, kind in q["source"]["fields"].items():
                f = fields.get(name)
                require(f is not None and not f.get("nullable", False), "Unsupported nullable/missing query field")
                typ = f["type"]
                mapped = "string" if typ in ("prim:string", "prim:timestamp") or types.get(typ, {}).get("kind") == "enum" else None
                require(mapped == kind, "Unsupported model/query field type")
            key = fields[q["source"]["unique_key"]]["id"]
            require(any(i["id"] in state["invariants"] and i.get("kind") == "unique_field" and i.get("field") == key
                        for i in model["invariants"]), "Query identity lacks model uniqueness authority")
            require(q["id"] not in {c["token"] for c in model["commands"]}, "Query/legacy command collision")
        return program
    except (ValueError, TypeError, KeyError, StopIteration) as exc:
        from lykoi_controller import Failure
        raise Failure("UNSUPPORTED_COLLECTION_STORE", reason=str(exc)) from exc


def author(normal):
    if normal.get("profile") == "typed-mutable-values-1":
        from lykoi_pipeline.mutable_profile import recover
    elif normal.get("profile") == "existing-model-1":
        from lykoi_pipeline.model_profile import recover
    elif normal.get("profile") == "existing-composed-1":
        from lykoi_pipeline.composition_profile import recover
    elif normal.get("profile") == "existing-scalar-1":
        from lykoi_pipeline.scalar_profile import recover
    else:
        from lykoi_pipeline.query_profile import recover
    recover(normal)
    return {"lykoi_version": VERSION, "profile": normal["profile"], "contract": copy.deepcopy(normal)}


def generate(source):
    if source.get("lykoi_version") != VERSION:
        return generate_legacy(validate_legacy(parse(json.dumps(source))))
    require(set(source) == {"lykoi_version", "profile", "contract"}, "Unknown normal program fields")
    if source["profile"] == "typed-mutable-values-1":
        from lykoi_pipeline import mutable_profile
        contract = mutable_profile.recover(source["contract"])
        p = mutable_profile.structural(contract, mutable_profile.scalar.frc.digest(contract))
        require(mutable_profile.adequate(contract, mutable_profile.bdi(contract, p))["outcome"] == "ADEQUATE", "Mutation contract is not adequate")
        return generate_mutable(p["facts"]["ir"], list(p["facts"]["queries"].values()))
    if source["profile"] == "existing-model-1":
        from lykoi_pipeline import model_profile as amendment
        contract = amendment.recover(source["contract"])
        p = amendment.structural(contract, amendment.scalar.frc.digest(contract))
        require(amendment.adequate(contract, amendment.bdi(contract, p))["outcome"] == "ADEQUATE", "Existing-model contract is not adequate")
        return normal_resources(generate_legacy(validate_legacy(parse(json.dumps(p["model"])))))
    if source["profile"] == "existing-composed-1":
        from lykoi_pipeline import composition_profile as composed
        contract = composed.recover(source["contract"])
        p = composed.structural(contract, composed.scalar.frc.digest(contract))
        b = composed.bdi(contract, p)
        require(composed.adequate(contract, b)["outcome"] == "ADEQUATE", "Composed contract is not adequate")
        return generate_bound(list(p["facts"]["queries"].values()), p["facts"]["storage"])
    if source["profile"] == "existing-scalar-1":
        from lykoi_pipeline import scalar_profile
        contract = scalar_profile.recover(source["contract"])
        p = scalar_profile.structural(contract, scalar_profile.frc.digest(contract))
        b = scalar_profile.bdi(contract, p)
        require(scalar_profile.adequate(contract, b)["outcome"] == "ADEQUATE", "Scalar contract is not adequate")
        return normal_resources(generate_legacy(validate_legacy(parse(json.dumps(scalar_profile.lower(p["facts"], contract["context"]["domains"].get("scalar_base_model")))))))
    from lykoi_pipeline.query_profile import recover, PROFILE
    require(source["profile"] == PROFILE, "Unsupported program profile")
    contract = recover(source["contract"])
    from lykoi_query import contracts
    p = contracts.structural(contract, source["contract"]["document"]["source_frc"])
    b = contracts.bdi(contract, p)
    a = contracts.adequate(contract, b)
    require(a["outcome"] == "IMPLEMENTATION_ADEQUATE", "Query contract is not adequate")
    queries = [validate_query({k: v for k, v in q.items() if k != "origins"}, complete=True) for q in p["queries"]]
    require(len({q["id"] for q in queries}) == len(queries), "Duplicate query commands")
    storage = source["contract"]["storage"]
    return generate_bound(queries, storage)


def normal_resources(legacy):
    """Normal-path provider binding; default legacy output remains byte-identical."""
    resource_runtime = Path(__file__).with_name("creation_provider_runtime.py").read_text(encoding="utf-8")
    footer = 'if __name__ == "__main__":\n    sys.exit(main())'
    require(legacy.count(footer) == 1, "Legacy backend entrypoint mismatch")
    return legacy.replace(footer, "") + "\n" + resource_runtime + "\n" + footer + "\n"


def validate_mutable_storage(storage, queries):
    from .mutable_values import compose
    ir = storage["ir"]
    require(compose(ir["base"], ir["facts"]) == ir, "Invalid mutable model IR")
    model = ir["model"]
    state = model["state"][0]
    require(storage["state"] == state["id"], "Mutable query state mismatch")
    key = next(t for t in model["types"] if t["kind"] == "record")
    identity = next(f["name"] for f in key["fields"] if f["id"] == state["key_field"])
    for q in queries:
        validate_query(q, complete=True)
        require(q["effect"] == {"state": "read_only", "persistence": "unchanged"}, "Only existing read-only query composition")
        require(q["source"]["collection"] == state["id"] and q["source"]["unique_key"] == identity, "Query collection/unique identity authority")
        require(q["id"] not in {c["token"] for c in model["commands"]} | {m["command"] for m in ir["facts"]["mutations"]}, "Mutation/query command conflict")
        for n, kind in q["source"]["fields"].items():
            t = ir["value_types"].get(n)
            require(t is not None and not t.get("nullable", False), "Missing/nullable query field")
            mapped = "strings" if t["type"] == "collection" and t["element"]["type"] in ("string", "identifier", "enum") else "string" if t["type"] in ("string", "identifier", "enum", "timestamp") else None
            require(mapped == kind, "Unsupported mutable query type")
    return ir


def generate_mutable(ir, queries):
    from .mutable_values import compose
    require(compose(ir["base"], ir["facts"]) == ir, "Invalid mutable IR")
    legacy = normal_resources(generate_legacy(validate_legacy(parse(json.dumps(ir["base"])))))
    footer = 'if __name__ == "__main__":\n    sys.exit(main())'
    runtime = Path(__file__).with_name("mutable_runtime.py").read_text(encoding="utf-8")
    runtime = runtime.replace("MUTABLE = {}  # inserted by normal compiler", "MUTABLE = " + repr(ir) + "\nSPEC = MUTABLE['model']")
    target = legacy.replace(footer, "") + "\n" + runtime + "\n"
    if not queries:
        return target + footer + "\n"
    storage = dict(kind="mutable_state", ir=ir, state=ir["model"]["state"][0]["id"])
    validate_mutable_storage(storage, queries)
    target += "\nlegacy_main = main\n"
    qr = Path(__file__).with_name("collection_query_runtime.py").read_text(encoding="utf-8")
    qr = qr.replace("def execute(", "def execute_query(").replace("execute(model, records, args)", "execute_query(model, records, args)").replace("def main(model):", "def standalone_query_main(model):")
    integration = Path(__file__).with_name("profile_runtime.py").read_text(encoding="utf-8")
    return target + qr + "\n" + integration + "\nif __name__ == '__main__':\n    sys.exit(profile_main(" + repr(queries) + ", " + repr({"kind": "mutable_state", "state": storage["state"]}) + "))\n"


def generate_bound(queries, storage):
    queries = [validate_query(q, complete=True) for q in queries]
    require(len({q["id"] for q in queries}) == len(queries), "Duplicate query commands")
    prefix = "# Generated by LykoiProgram-1 / collection-query-1; do not edit.\n"
    if storage["kind"] == "model_state":
        legacy = normal_resources(generate_legacy(validate_storage(storage, queries)))
        footer = 'if __name__ == "__main__":\n    sys.exit(main())'
        require(legacy.count(footer) == 1, "Legacy backend entrypoint mismatch")
        prefix += legacy.replace(footer, "") + "\nlegacy_main = main\n"
    runtime = Path(__file__).with_name("collection_query_runtime.py").read_text(encoding="utf-8")
    runtime = runtime.replace("def execute(", "def execute_query(").replace("execute(model, records, args)", "execute_query(model, records, args)")
    runtime = runtime.replace("def main(model):", "def standalone_query_main(model):")
    integration = Path(__file__).with_name("profile_runtime.py").read_text(encoding="utf-8")
    return prefix + runtime + "\n" + integration + "\nif __name__ == '__main__':\n    sys.exit(profile_main(" + repr(queries) + ", " + repr({k: v for k, v in storage.items() if k != "model"}) + "))\n"
