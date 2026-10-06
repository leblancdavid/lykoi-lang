"""One-shot deterministic worker. Imports no service or controller module."""
import json
import sys

payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
request = payload["request"]
assert set(request) == {"role", "instructions", "session", "source", "evidence", "output_schema"}
assert request["role"] == payload["role"]
assert payload["role"] in {"formalizer", "reviewer"}
json.dump(payload["output"], sys.stdout, ensure_ascii=True, allow_nan=False)
