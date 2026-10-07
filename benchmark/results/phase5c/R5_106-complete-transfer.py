"""Complete the exact locked corpus, recording producer validation failures.

This evidence wrapper preserves the native producer-stage exception instead of
changing source captures or extending the frozen normal predicate profile.
"""
import copy
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path

from lykoi_controller import Failure

OUT = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("resume106preserved", OUT / "R5_106-resume-transfer.py")
r = importlib.util.module_from_spec(s); s.loader.exec_module(r)
generic, ev = r.generic, r.ev
native_evaluate = ev.evaluate


def captured_evaluate(record, plan):
    try:
        return native_evaluate(record, plan)
    except Failure as exc:
        # The current evaluator's only uncaught Failure boundary is pre-prepare
        # workspace producer/reconciliation. Preserve the native failure stage.
        stages = {s: "NOT_REACHED" for s in ev.STAGES}; stages["FORMALIZATION"] = "BLOCKED"
        return dict(case=record["id"], stages=stages, candidate=copy.deepcopy(record), external_plan=copy.deepcopy(plan),
            first_blocker="FORMALIZATION", native=exc.code, terminal=dict(outcome=exc.code, failure=exc.as_dict()),
            observation="Native typed producer validation refused a bound-reference mismatch before sealing; no source ambiguity inferred", external_invocations=0)


def main():
    # Reuse the preserved driver's exact corpus/hash checks and exclusive
    # publication. Its resume-lock publication gets a fresh prospective name.
    original_publish = generic.publish
    def publish(name, value):
        if name == "R5_106-TRANSFER-RESUME-LOCK.json":
            name = "R5_106-TRANSFER-COMPLETION-LOCK.json"
            value["completion_script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
            value["utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if name == "R5_106-TRANSFER-EVIDENCE.json":
            value["additional_interruption"] = "R5_106-TRANSFER-INTERRUPTION-2.json"
        original_publish(name, value)
    generic.publish = publish
    ev.evaluate = captured_evaluate
    r.main()


if __name__ == "__main__": main()
