"""Standalone stage-2 kiln firing permits; records.json is relative to the cwd."""

import datetime
import json
import os
import tempfile
import uuid


FIELDS = {"id", "created_at", "label", "phase", "vent", "load"}


def _utc(value):
    if not isinstance(value, str):
        raise ValueError("timestamp must be a string")
    parsed = datetime.datetime.fromisoformat(
        value[:-1] + "+00:00" if value.endswith("Z") else value
    )
    if parsed.tzinfo is None or parsed.utcoffset() != datetime.timedelta(0):
        raise ValueError("timestamp must be UTC")
    return parsed


def _valid_id(value):
    if not isinstance(value, str):
        return False
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError):
        return False
    return parsed.version == 4 and parsed.variant == uuid.RFC_4122


def _valid_record(record):
    if not isinstance(record, dict) or set(record) != FIELDS:
        return False
    if not _valid_id(record["id"]):
        return False
    try:
        _utc(record["created_at"])
    except (ValueError, TypeError, OverflowError):
        return False
    return (
        isinstance(record["label"], str)
        and bool(record["label"].strip())
        and isinstance(record["phase"], str)
        and record["phase"] in ("cold", "firing")
        and isinstance(record["vent"], str)
        and record["vent"] in ("open", "closed")
        and isinstance(record["load"], str)
        and record["load"] in ("ordinary", "emergency")
        and (record["phase"] != "firing" or record["vent"] == "open"
             or (record["vent"] == "closed" and record["load"] == "emergency"))
    )


def _reload():
    try:
        with open("records.json", "r", encoding="utf-8") as stream:
            # Duplicate JSON keys are not silently repaired into valid records.
            def unique_object(pairs):
                result = {}
                for key, value in pairs:
                    if key in result:
                        raise ValueError("duplicate field")
                    result[key] = value
                return result

            records = json.load(stream, object_pairs_hook=unique_object)
    except FileNotFoundError:
        return []
    if not isinstance(records, list) or not all(_valid_record(r) for r in records):
        raise ValueError("invalid records")
    identities = [uuid.UUID(r["id"]) for r in records]
    if len(set(identities)) != len(identities):
        raise ValueError("duplicate identity")
    return records


def _commit(records):
    # The temporary file is on the same filesystem as the destination.
    path = os.path.abspath("records.json")
    descriptor, temporary = tempfile.mkstemp(prefix=".kiln-", suffix=".json", dir=os.path.dirname(path))
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(records, stream, ensure_ascii=True, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def handle(op, args, providers):
    """Return an ok record/list or an error code, reloading for every call."""
    try:
        records = _reload()
    except (OSError, ValueError, TypeError, UnicodeError, OverflowError):
        return {"error": "invalid_state"}

    if op == "list":
        return {"ok": sorted(records, key=lambda r: (_utc(r["created_at"]), r["id"]))}
    if not isinstance(args, dict):
        return {"error": "invalid_input"}
    if op == "create":
        label = args.get("label")
        vent = args.get("vent")
        load = args.get("load")
        if (not isinstance(label, str) or not label.strip()
                or not isinstance(vent, str) or vent not in ("open", "closed")
                or not isinstance(load, str) or load not in ("ordinary", "emergency")):
            return {"error": "invalid_input"}
        identity = providers["uuid_v4"]()
        if not _valid_id(identity):
            return {"error": "invalid_input"}
        if any(uuid.UUID(r["id"]) == uuid.UUID(identity) for r in records):
            return {"error": "id_collision"}
        created_at = providers["utc_clock"]()
        record = {"id": identity, "created_at": created_at, "label": label,
                  "phase": "cold", "vent": vent, "load": load}
        if not _valid_record(record):
            return {"error": "invalid_input"}
        updated = records + [record]
    elif op in ("ignite", "set_gate", "cool", "rescue"):
        index = next((i for i, r in enumerate(records) if r["id"] == args.get("id")), None)
        if index is None:
            return {"error": "not_found"}
        original = records[index]
        record = dict(original)
        if op == "ignite":
            if original["phase"] != "cold":
                return {"error": "invalid_transition"}
            if original["vent"] != "open":
                return {"error": "gate_required"}
            record["phase"] = "firing"
        elif op == "cool":
            if original["phase"] != "firing":
                return {"error": "invalid_transition"}
            record["phase"] = "cold"
        elif op == "rescue":
            if original["phase"] != "cold":
                return {"error": "invalid_transition"}
            if original["vent"] != "closed" or original["load"] != "emergency":
                return {"error": "exception_denied"}
            record["phase"] = "firing"
        else:
            value = args.get("value")
            if original["phase"] == "firing" and value == "closed":
                return {"error": "gate_locked"}
            if not isinstance(value, str) or value not in ("open", "closed"):
                return {"error": "invalid_input"}
            record["vent"] = value
        updated = list(records)
        updated[index] = record
    else:
        return {"error": "invalid_input"}
    try:
        _commit(updated)
    except OSError:
        return {"error": "invalid_state"}
    return {"ok": record}
