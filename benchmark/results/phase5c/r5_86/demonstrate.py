"""Public synthetic controller evidence and exact public checkout diagnostics.

Prints a prospective report; never rewrites historical results or opens protected
inputs. Test fixtures contain synthetic service credentials, not deployment keys.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT / "src"), str(ROOT / "tests")]

from lykoi_controller import Controller
from test_authority_controller import Case, PRINCIPALS


def demonstrate():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "synthetic.sqlite"
        c = Controller(path, PRINCIPALS)
        try:
            case = Case(c)
            b = case.full()
            positive = c.applicable(b["grant"], b["bundle"], b["freeze"])
            assert positive["applicable"]
            before = c.audit(b["bundle"])
            c.close()
            c = Controller(path, PRINCIPALS)
            assert c.audit(b["bundle"]) == before
            case = Case(c)
            new = case.source(b"Tasks have optional priority; default HIGH.", b["policy"])
            case.call("human", "supersede", subject=b["source"], replacement=new)
            stale = c.applicable(b["grant"], b["bundle"], b["freeze"])
            assert not stale["applicable"]
            c.check_integrity()
            return {"case": "public-synthetic-optional-priority", "semantic_producers": "SYNTHETIC_PLACEHOLDERS",
                    "identities": b, "replacement_source": new, "valid_chain": positive,
                    "restart_preserves_authority": True, "stale_chain": stale,
                    "journal_events": c.revision, "historical_grant_retained": c.artifact(b["grant"])["type"] == "grant"}
        finally:
            c.close()


def checkout_diagnostics():
    # These two files are already public inputs of the explicitly selected tests.
    records = {}
    for relative, expected in (
        ("benchmark/requirements/B01.md", "b7b2d714db5cee566e9e55982dd4c4d95d3d57f0c341e04ba1e15c24e9a8e94d"),
        ("benchmark/results/phase5c/r5_84/independent-soi.json", "ff124b66301901a9e945338ccad1a354f8e393d8fe9175f06d1fbf3068d29d44"),
    ):
        raw = (ROOT / relative).read_bytes()
        lf = raw.replace(b"\r\n", b"\n")
        records[relative] = {"historical_physical_pin": expected,
                             "checkout_sha256": hashlib.sha256(raw).hexdigest(),
                             "lf_sha256": hashlib.sha256(lf).hexdigest(),
                             "lf_matches_historical_pin": hashlib.sha256(lf).hexdigest() == expected,
                             "crlf_sequences": raw.count(b"\r\n")}
    return records


if __name__ == "__main__":
    print(json.dumps({"controller": demonstrate(), "checkout_diagnostics": checkout_diagnostics()},
                     sort_keys=True, indent=2))
