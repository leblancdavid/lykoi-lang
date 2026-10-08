"""Author-owned smoke checks for the cumulative kiln stage-1 contract."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile

source = Path(__file__).with_name("selftest.py")
spec = importlib.util.spec_from_file_location("kiln_s1_generated", source)
app = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app)
providers = {
    "uuid_v4": lambda: "12345678-1234-4234-8234-123456789abc",
    "utc_clock": lambda: "2026-10-08T23:00:00Z",
}
checks = 0


def expect(op, args, expected):
    global checks
    actual = app.handle(op, args, providers)
    assert actual == expected, (op, args, actual, expected)
    checks += 1


def reject(op, args, error):
    store = Path("records.json")
    before = store.read_bytes() if store.exists() else None
    expect(op, args, {"error": error})
    after = store.read_bytes() if store.exists() else None
    assert after == before, (op, "rejection changed storage")


original = Path.cwd()
with tempfile.TemporaryDirectory(dir=r"C:\Users\lblan\AppData\Local\Temp\opencode") as folder:
    try:
        os.chdir(folder)
        expect("list", {}, {"ok": []})
        reject("cool", {"id": "missing"}, "not_found")
        reject("create", {"label": " \t", "vent": "open", "load": "ordinary"}, "invalid_label")
        created = app.handle("create", {"label": "  kiln  ", "vent": "closed", "load": "ordinary"}, providers)
        assert "ok" in created, created
        record = created["ok"]
        assert record == {"id": providers["uuid_v4"](), "created_at": providers["utc_clock"](),
                          "label": "  kiln  ", "phase": "cold", "vent": "closed", "load": "ordinary"}, record
        checks += 1
        identity = {"id": record["id"]}
        reject("cool", identity, "invalid_transition")
        reject("ignite", identity, "gate_required")
        record = dict(record, vent="open")
        expect("set_gate", dict(identity, value="open"), {"ok": record})
        record = dict(record, phase="firing")
        expect("ignite", identity, {"ok": record})
        reject("ignite", identity, "invalid_transition")
        reject("set_gate", dict(identity, value="closed"), "gate_locked")
        reject("set_gate", identity, "invalid_input")
        reject("set_gate", dict(identity, value="bad"), "invalid_input")
        record = dict(record, phase="cold")
        expect("cool", identity, {"ok": record})
        record = dict(record, vent="closed")
        expect("set_gate", dict(identity, value="closed"), {"ok": record})
        reject("ignite", identity, "gate_required")
        expect("list", {}, {"ok": [record]})
        Path("records.json").write_text(json.dumps([dict(record, phase="firing")]), encoding="utf-8")
        reject("list", {}, "invalid_state")
        reject("cool", identity, "invalid_state")
        print(json.dumps({"checks_passed": checks}))
    finally:
        os.chdir(original)
