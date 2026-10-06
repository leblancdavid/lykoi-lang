"""Reproducible one-shot invocation: public allowlisted JSON on stdin only."""
import argparse
import json
import sys

from lykoi_controller import Failure
from lykoi_controller.controller import parse_json
from .adapters import AIAdapter
from .freeze import configurations


def main():
    parser = argparse.ArgumentParser(description="Public AI candidate invocation; no authority issued")
    parser.add_argument("role", choices=["formalizer", "reviewer", "author", "verifier"])
    args = parser.parse_args()
    adapter = AIAdapter(args.role, configurations()["roles"][args.role])
    try:
        raw = sys.stdin.buffer.read(1000001)
        if len(raw) > 1000000:
            raise Failure("PRODUCER_INPUT_TOO_LARGE")
        request = parse_json(raw.decode())
        if args.role in ("formalizer", "reviewer"):
            request["session"] = adapter.session
        output = adapter.produce(request)
        print(json.dumps({"candidate": output, "receipt": adapter.receipts[-1]}, indent=2, sort_keys=True))
    except Failure as exc:
        print(json.dumps(exc.as_dict(), sort_keys=True))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
