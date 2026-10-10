"""Bounded local contract tests; all temporary stores stay in this directory."""
import copy
import importlib.util
import itertools
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parent
ID = "00000000-0000-4000-8000-000000000001"
OTHER = "00000000-0000-4000-8000-000000000002"
MISSING = "00000000-0000-4000-8000-000000000003"
STAMP = "2026-10-10T00:00:00Z"
PROVIDERS = {"uuid_v4": lambda: MISSING, "utc_clock": lambda: STAMP}


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def record(phase="cold", vent="open", load="ordinary", identity=ID):
    return dict(id=identity, created_at=STAMP, label="  Kiln\u2603  ",
                phase=phase, vent=vent, load=load)


def encoded(records):
    return (json.dumps(records, ensure_ascii=False, indent=3) + " \n\n").encode()


def expected(original, op, args, legacy=False):
    if args.get("id") != original["id"]:
        return {"error": "not_found"}
    changed = dict(original)
    phase, vent, load = (original[k] for k in ("phase", "vent", "load"))
    if op == "ignite":
        if phase != "cold":
            return {"error": "invalid_transition"}
        if vent != "open" and (legacy or load != "emergency"):
            return {"error": "gate_required"}
        changed["phase"] = "firing"
    elif op == "cool":
        if phase != "firing":
            return {"error": "invalid_transition"}
        changed["phase"] = "cold"
    elif op == "rescue":
        if phase != "cold":
            return {"error": "invalid_transition"}
        if vent != "closed" or load != "emergency":
            return {"error": "exception_denied"}
        changed["phase"] = "firing"
    else:
        value = args.get("value")
        if phase == "firing" and value == "closed" and (legacy or load == "ordinary"):
            return {"error": "gate_locked"}
        if not isinstance(value, str) or value not in ("open", "closed"):
            return {"error": "invalid_input"}
        changed["vent"] = value
    return {"ok": changed}


def main():
    started = time.perf_counter()
    candidate, baseline = load("first"), load("baseline")
    count = 0
    original_cwd = Path.cwd()
    with tempfile.TemporaryDirectory(prefix="self-test-", dir=ROOT) as directory:
        os.chdir(directory)
        store = Path("records.json")

        def check(module, payload, op, args, want, providers=PROVIDERS):
            nonlocal count
            if payload is None:
                store.unlink(missing_ok=True)
            else:
                store.write_bytes(payload)
            actual = module.handle(op, args, providers)
            assert actual == want, (op, args, actual, want)
            if "error" in want or op == "list":
                assert (store.read_bytes() if store.exists() else None) == payload
            else:
                persisted = json.loads(store.read_bytes())
                assert all(module._valid_record(r) for r in persisted)
                before = json.loads(payload) if payload is not None else []
                if op == "create":
                    assert persisted == before + [want["ok"]]
                else:
                    assert persisted == [want["ok"] if r["id"] == args["id"] else r
                                         for r in before]
            count += 1

        values = ["open", "closed", None, 0, False, [], {}, "CLOSED", "", ["closed"]]
        mutations = [(op, {}) for op in ("ignite", "cool", "rescue")]
        mutations += [("set_gate", {})] + [("set_gate", {"value": v}) for v in values]
        for phase, vent, load_type in itertools.product(
                ("cold", "firing"), ("open", "closed"), ("ordinary", "emergency")):
            if phase == "firing" and vent == "closed" and load_type == "ordinary":
                continue
            selected = record(phase, vent, load_type)
            unselected = record("firing", "closed", "emergency", OTHER)
            payload = encoded([unselected, selected])
            for op, extra in mutations:
                for identity in (ID, MISSING, None):
                    args = dict(id=identity, **extra)
                    check(candidate, payload, op, args, expected(selected, op, args))
                    check(baseline, payload, op, args, expected(selected, op, args, True))
            check(candidate, payload, "list", None, {"ok": [selected, unselected]})

        invalid = [b"not json", b"{}", b"[null]", b"\xff", b'[{"id":1,"id":2}]',
                   encoded([record("firing", "closed", "ordinary")]),
                   encoded([record(), record(identity=ID)])]
        for key, value in [("phase", "bad"), ("vent", "bad"), ("load", "bad"),
                           ("label", " "), ("created_at", "2026-10-10"), ("id", "bad")]:
            bad = record(identity=OTHER)
            bad[key] = value
            invalid.append(encoded([record(), bad]))
        bad = record(identity=OTHER)
        bad["extra"] = 1
        invalid.append(encoded([record(), bad]))
        for payload in invalid:
            for op in ("create", "list", "ignite", "set_gate", "cool", "rescue", "unknown"):
                for args in ({"id": ID, "value": "closed", "label": " "},
                             {"id": MISSING, "value": None}, None):
                    check(candidate, payload, op, args, {"error": "invalid_state"})

        for payload in (None, encoded([])):
            check(candidate, payload, "list", {}, {"ok": []})
            for op, extra in mutations:
                check(candidate, payload, op, dict(id=ID, **extra), {"error": "not_found"})
            check(candidate, payload, "create", {"label": " "}, {"error": "invalid_label"})
        for vent, load_type in itertools.product(("open", "closed"), ("ordinary", "emergency")):
            args = {"label": "  Exact\u2603  ", "vent": vent, "load": load_type}
            want = {"ok": dict(record(vent=vent, load=load_type, identity=MISSING), label=args["label"])}
            check(candidate, encoded([record()]), "create", args, want)
            check(baseline, encoded([record()]), "create", args, want)
        check(candidate, encoded([record()]), "create",
              {"label": "x", "vent": "open", "load": "emergency"},
              {"error": "id_collision"}, {"uuid_v4": lambda: ID, "utc_clock": lambda: STAMP})

        # Each step starts a fresh Python client, sharing one persistent store.
        store.unlink(missing_ok=True)
        worker = (
            "import importlib.util,json,sys;"
            "s=importlib.util.spec_from_file_location('app',sys.argv[1]);"
            "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
            "p={'uuid_v4':lambda:sys.argv[4],'utc_clock':lambda:sys.argv[5]};"
            "print(json.dumps(m.handle(sys.argv[2],json.loads(sys.argv[3]),p)))"
        )
        sequence = [
            ("create", {"label": "  retained  ", "vent": "closed", "load": "emergency"}, "ok"),
            ("ignite", {"id": ID}, "ok"),
            ("set_gate", {"id": ID, "value": "closed"}, "ok"),
            ("list", {}, "ok"),
            ("cool", {"id": ID}, "ok"),
            ("rescue", {"id": ID}, "ok"),
            ("ignite", {"id": ID}, "invalid_transition"),
            ("set_gate", {"id": ID}, "invalid_input"),
            ("set_gate", {"id": ID, "value": "open"}, "ok"),
            ("set_gate", {"id": ID, "value": "closed"}, "ok"),
            ("cool", {"id": ID}, "ok"),
            ("list", {}, "ok"),
        ]
        for op, args, status in sequence:
            before = store.read_bytes() if store.exists() else None
            process = subprocess.run(
                [sys.executable, "-B", "-c", worker, str(ROOT / "first.py"),
                 op, json.dumps(args), ID, STAMP],
                capture_output=True, text=True, check=True, timeout=5)
            result = json.loads(process.stdout)
            assert ("ok" in result) if status == "ok" else result == {"error": status}
            if status != "ok" or op == "list":
                assert store.read_bytes() == before
            persisted = json.loads(store.read_bytes())
            assert len(persisted) == 1 and persisted[0]["id"] == ID
            assert persisted[0]["label"] == "  retained  "
            assert persisted[0]["created_at"] == STAMP and persisted[0]["load"] == "emergency"
            assert candidate._valid_record(persisted[0])
            count += 1
        assert json.loads(store.read_bytes())[0] == dict(record(vent="closed", load="emergency"), label="  retained  ")
        os.chdir(original_cwd)
    print(json.dumps({"result": "passed", "cases": count,
                      "fresh_process_operations": len(sequence),
                      "duration_seconds": round(time.perf_counter() - started, 3)}))


if __name__ == "__main__":
    main()
