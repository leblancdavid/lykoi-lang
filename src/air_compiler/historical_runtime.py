"""Private whole-store additive candidates, validated before one replacement."""


def historical_types(version):
    types = copy.deepcopy(REFERENCE["types"])
    primary = REFERENCE["facts"]["primary"]
    state = SPEC["state"][0]
    rt, _ = state_layout(state)
    for step in SPEC["migrations"]:
        if step["from_version"] >= version:
            for field in step["add_fields"]: types[primary].pop(field_name(rt, field["field"]))
    for step in REFERENCE["historical"]["steps"]:
        if step["from"] >= version:
            for entity in step["entities"]:
                for field in entity["add_fields"]: types[entity["entity"]].pop(field["field"])
    return types


def historical_validate(rows, version):
    types = historical_types(version)
    if type(rows) is not dict or set(rows) != set(types): raise Failure("invalid_state")
    for e, fields in types.items():
        records, key = rows[e], REFERENCE["identities"][e]
        if type(records) is not list or any(type(r) is not dict or set(r) != set(fields) or any(not mutable_value_valid(r[n], t) for n, t in fields.items()) for r in records): raise Failure("invalid_state")
        ids = [r[key] for r in records]
        if any(type(i) is not str or not i.strip() for i in ids) or len(set(ids)) != len(ids): raise Failure("invalid_state")
    # Existing reference fields obey their declared existence policy even when a
    # later introduction would otherwise overwrite evidence of invalid old data.
    for r in REFERENCE["facts"]["references"]:
        if r["field"] not in types[r["entity"]] or r["existence"]["policy"] != "required": continue
        target = {x[REFERENCE["identities"][r["target"]]] for x in rows[r["target"]]}
        for row in rows[r["entity"]]:
            value = row[r["field"]]
            values = value if type(value) is list else [value]
            if any(v not in target for v in values): raise Failure(r["existence"]["error"])


def historical_migrate():
    state = SPEC["state"][0]
    rt, path = state_layout(state)
    payload = reference_payload()
    if not payload: return {"migrated": 0}
    if type(payload) is not dict or set(payload) != {"schema_version", "records", "entities"}: raise Failure("invalid_state")
    version = payload["schema_version"]
    if type(version) is not int or not 1 <= version <= state["schema_version"]: raise Failure("invalid_state")
    primary = REFERENCE["facts"]["primary"]
    if type(payload["entities"]) is not dict or primary in payload["entities"]: raise Failure("invalid_state")
    rows = copy.deepcopy({primary: payload["records"], **payload["entities"]})
    original = copy.deepcopy(rows)
    historical_validate(rows, version)
    while version < state["schema_version"]:
        step = next((m for m in SPEC["migrations"] if m["from_version"] == version), None)
        if step is None: raise Failure("invalid_state")
        before = copy.deepcopy(rows)
        added = {field_name(rt, a["field"]): a["value"] for a in step["add_fields"]}
        rows[primary] = [{**r, **copy.deepcopy(added)} for r in rows[primary]]
        related = next((s for s in REFERENCE["historical"]["steps"] if s["from"] == version), None)
        for entity in related["entities"] if related else []:
            e = entity["entity"]
            for index, row in enumerate(before[e]):
                values = computation_evaluate(entity["computations"], before, {"before": row}, {}) if entity["computations"] else {}
                for field in entity["add_fields"]:
                    s = field["source"]
                    rows[e][index][field["field"]] = computation_value(s, before, {"before": row}, {}, {}, values)
        version = step["to_version"]
        historical_validate(rows, version)
    # Current initial constants, invariants and all references are checked by the
    # same commit implementation used for ordinary operations.
    reference_entities({"entities": {e: r for e, r in rows.items() if e != primary}})
    if not valid_state(rows[primary], state, rt): raise Failure("invalid_state")
    reference_integrity(rows, rows, migration=True)
    changed = payload["schema_version"] != version or rows != original
    if changed: reference_commit(rows, rows, migration=True)
    count = sum(len(records) for records in original.values()) if changed else 0
    return {"migrated": count}
