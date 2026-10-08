"""Standalone stage-2 evidence-custody registry. Storage is relative to cwd."""

import datetime
import json
import os
import tempfile
import uuid
from pathlib import Path


FIELDS = {"id", "created_at", "label", "phase", "witness", "material"}
STORE = Path("records.json")


def _timestamp(value):
    if not isinstance(value, str) or "T" not in value:
        raise ValueError("invalid timestamp")
    parsed = datetime.datetime.fromisoformat(
        value[:-1] + "+00:00" if value.endswith("Z") else value
    )
    if parsed.tzinfo is None or parsed.utcoffset() != datetime.timedelta(0):
        raise ValueError("timestamp must be UTC")
    return parsed


def _valid_record(record):
    if not isinstance(record, dict) or set(record) != FIELDS:
        return False
    if not isinstance(record["id"], str):
        return False
    identity = uuid.UUID(record["id"])
    if identity.version != 4 or identity.variant != uuid.RFC_4122:
        return False
    if str(identity) != record["id"]:
        return False
    _timestamp(record["created_at"])
    return (
        isinstance(record["label"], str)
        and bool(record["label"].strip())
        and record["phase"] in ("unsealed", "sealed")
        and record["witness"] in ("present", "absent")
        and record["material"] in ("routine", "fragile")
        and (
            record["phase"] != "sealed"
            or record["witness"] == "present"
            or (record["witness"] == "absent" and record["material"] == "fragile")
        )
    )


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def _load():
    try:
        with STORE.open("r", encoding="utf-8") as stream:
            records = json.load(stream, object_pairs_hook=_unique_object)
    except FileNotFoundError:
        return []
    if not isinstance(records, list):
        raise ValueError("store must be a list")
    identities = set()
    for record in records:
        if not _valid_record(record) or record["id"] in identities:
            raise ValueError("invalid persisted state")
        identities.add(record["id"])
    return records


def _save(records):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=STORE.parent,
            prefix=".records-", suffix=".tmp", delete=False
        ) as stream:
            temporary = stream.name
            json.dump(records, stream, ensure_ascii=False, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, STORE)
        temporary = None
    finally:
        if temporary is not None:
            os.unlink(temporary)


def handle(op, args, providers):
    """Return an ok record/list or a domain error; reload before every operation."""
    try:
        records = _load()
    except (ValueError, TypeError, AttributeError, OverflowError, OSError):
        return {"error": "invalid_state"}

    if op == "list":
        return {"ok": sorted(records, key=lambda r: (_timestamp(r["created_at"]), r["id"]))}

    if op == "create":
        label = args.get("label")
        if (
            not isinstance(label, str) or not label.strip()
            or args.get("witness") not in ("present", "absent")
            or args.get("material") not in ("routine", "fragile")
        ):
            return {"error": "invalid_input"}
        identity = providers["uuid_v4"]()
        if any(record["id"] == identity for record in records):
            return {"error": "id_collision"}
        record = {
            "id": identity,
            "created_at": providers["utc_clock"](),
            "label": label,
            "phase": "unsealed",
            "witness": args["witness"],
            "material": args["material"],
        }
        records.append(record)
        _save(records)
        return {"ok": record}

    if op not in ("seal", "unseal", "protect", "set_gate"):
        return {"error": "invalid_input"}
    record = next((r for r in records if r["id"] == args.get("id")), None)
    if record is None:
        return {"error": "not_found"}
    if op == "seal":
        if record["phase"] != "unsealed":
            return {"error": "invalid_transition"}
        if record["witness"] != "present":
            return {"error": "gate_required"}
        record["phase"] = "sealed"
    elif op == "unseal":
        if record["phase"] != "sealed":
            return {"error": "invalid_transition"}
        record["phase"] = "unsealed"
    elif op == "protect":
        if record["phase"] != "unsealed":
            return {"error": "invalid_transition"}
        if record["witness"] != "absent" or record["material"] != "fragile":
            return {"error": "exception_denied"}
        record["phase"] = "sealed"
    else:
        value = args.get("value")
        if record["phase"] == "sealed" and value == "absent":
            return {"error": "gate_locked"}
        if value not in ("present", "absent"):
            return {"error": "invalid_input"}
        record["witness"] = value
    _save(records)
    return {"ok": record}
