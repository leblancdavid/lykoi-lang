"""Verifier-owned controlled embedding. Outputs are observations, never authority.

Only deterministic compiler-built targets are admitted by the parent pipeline.
This adapter is not authentication infrastructure or hostile-code OS containment.
"""
import importlib.util
import json
import sys
import os
from pathlib import Path
from contextlib import contextmanager


@contextmanager
def reservation(target, path):
    lock = Path(str(path) + ".operation-lock")
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise target.Failure("store_busy")
    os.close(fd)
    try: yield
    finally: lock.unlink()


def main():
    request = json.load(sys.stdin)
    spec = importlib.util.spec_from_file_location("lykoi_verified_target", sys.argv[1])
    target = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(target)
    command, inputs = request["command"], request["inputs"]
    context = request["execution_context"]
    try:
        # Reuse the same cooperative one-store reservation as ordinary CLI calls.
        state = target.SPEC["state"][0]
        _, path = target.state_layout(state)
        with reservation(target, path):
            related = next((o for o in target.REFERENCE["facts"]["operations"] if o["command"] == command), None)
            mutation = next((m for m in target.MUTABLE["facts"]["mutations"] if m["command"] == command), None)
            if related:
                value = target.reference_operation(related, inputs, execution_context=context)
            elif mutation:
                value = target.execute_mutation(mutation, inputs, execution_context=context)
            else:
                entry = next(c for c in target.SPEC["commands"] if c["token"] == command)
                behavior = next(b for b in target.SPEC["behaviors"] if b["id"] == entry["behavior"])
                bound = {i["id"]: inputs[i["name"]] for i in behavior["inputs"] if i["name"] in inputs}
                value = target.execute(behavior, bound, execution_context=context)
        print(json.dumps(value, ensure_ascii=False))
        return 0
    except target.Failure as exc:
        print(json.dumps({"error": exc.code}), file=sys.stderr)
        return 1


if __name__ == "__main__": sys.exit(main())
