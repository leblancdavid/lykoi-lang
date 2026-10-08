"""Author-owned finite-state checks derived from kiln requirements."""
import importlib.util
import itertools
import json
import os
from pathlib import Path
import tempfile

here = Path(__file__).resolve().parent
intent = json.loads((here / "intent.json").read_text())
previous = json.loads((here.parent / "s1" / "intent.json").read_text())
for key in ("version", "storage", "fields", "create"):
    assert intent[key] == previous[key], key
for command, operation in previous["operations"].items():
    assert intent["operations"][command] == operation, command
spec = importlib.util.spec_from_file_location("kiln_s2_generated", here / "selftest.py")
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
    assert before == after, (op, "changed rejected store")


original = Path.cwd()
with tempfile.TemporaryDirectory(dir=r"C:\Users\lblan\AppData\Local\Temp\opencode") as folder:
    try:
        os.chdir(folder)
        expect("list", {}, {"ok": []})
        reject("rescue", {"id": "missing"}, "not_found")
        reject("create", {"label": " \t", "vent": "closed", "load": "emergency"}, "invalid_label")
        record = {"id": providers["uuid_v4"](), "created_at": providers["utc_clock"](),
                  "label": "  kiln  ", "phase": "cold", "vent": "closed", "load": "emergency"}
        expect("create", {"label": record["label"], "vent": "closed", "load": "emergency"}, {"ok": record})
        reject("create", {"label": "duplicate", "vent": "open", "load": "ordinary"}, "id_collision")
        identity = {"id": record["id"]}
        operations = [("list", {}), ("cool", identity), ("ignite", identity), ("rescue", identity)]
        operations += [("set_gate", dict(identity, value=value)) for value in ("open", "closed", "bad")]
        operations += [("set_gate", identity)]
        for phase, vent, load in itertools.product(("cold", "firing"), ("open", "closed"), ("ordinary", "emergency")):
            current = dict(record, phase=phase, vent=vent, load=load)
            valid = phase == "cold" or vent == "open" or load == "emergency"
            for op, args in operations:
                Path("records.json").write_text(json.dumps([current], indent=2) + "\n", encoding="utf-8")
                error = None
                expected_record = dict(current)
                if not valid:
                    error = "invalid_state"
                elif op == "cool":
                    if phase != "firing":
                        error = "invalid_transition"
                    else:
                        expected_record["phase"] = "cold"
                elif op == "ignite":
                    if phase != "cold":
                        error = "invalid_transition"
                    elif vent != "open":
                        error = "gate_required"
                    else:
                        expected_record["phase"] = "firing"
                elif op == "rescue":
                    if phase != "cold":
                        error = "invalid_transition"
                    elif vent != "closed" or load != "emergency":
                        error = "exception_denied"
                    else:
                        expected_record["phase"] = "firing"
                elif op == "set_gate":
                    value = args.get("value")
                    if phase == "firing" and value == "closed":
                        error = "gate_locked"
                    elif value not in ("open", "closed"):
                        error = "invalid_input"
                    else:
                        expected_record["vent"] = value
                if error:
                    reject(op, args, error)
                else:
                    expect(op, args, {"ok": [current] if op == "list" else expected_record})
                    if op != "list":
                        assert json.loads(Path("records.json").read_text()) == [expected_record]
            if valid:
                Path("records.json").write_text(json.dumps([current]), encoding="utf-8")
                reject("rescue", {"id": "missing"}, "not_found")
        print(json.dumps({"checks_passed": checks, "state_combinations": 8,
                          "prior_intent_fields_create_operations_preserved": True}))
    finally:
        os.chdir(original)
