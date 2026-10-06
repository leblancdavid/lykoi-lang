"""Fixed deterministic author worker. Stdin allowlist; stdout is the sole output.

Python audit hooks deny normal file/process/network APIs during fixture execution.
This is not OS containment of arbitrary malicious Python/native code.
"""
import copy
import json
import sys


def deny(event, args):
    if event == "open" or event.startswith(("socket.", "subprocess.", "os.system", "os.exec", "os.spawn", "ctypes.")):
        raise PermissionError("AUTHOR_RESOURCE_DENIED")


def main():
    request = json.load(sys.stdin)
    if set(request) != {"version", "run", "v1", "toolchain", "fixture"}:
        raise ValueError("AUTHOR_INPUT_ALLOWLIST_VIOLATION")
    sys.addaudithook(deny)
    fixture = request["fixture"]
    normal = request["v1"]
    if normal.get("schema_version") == "LykoiContractV1" and normal.get("profile") in ("collection-query-1", "existing-scalar-1", "existing-composed-1", "existing-model-1"):
        # Fixed semantic author: no test material, source interpretation or adapter
        # injection. Trusted build will recover/validate the authorized profile.
        source = {"lykoi_version": "LykoiProgram-1", "profile": normal["profile"], "contract": copy.deepcopy(normal)}
        print(json.dumps({"source": source, "run": request["run"], "author_adapter": "restricted-fixture-1",
                          "isolation": "PYTHON_AUDIT_HOOK_PROCESS_FIXTURE_NO_OS_SANDBOX"}))
        return
    if fixture is None:
        print(json.dumps({"failure": "LYKOI_CAPABILITY_GAP", "reason": "No qualified author adapter for this V1 context"}))
        return
    if set(fixture) != {"identity", "source", "mode"}:
        raise ValueError("INVALID_FIXTURE")
    source = copy.deepcopy(fixture["source"])
    mode = fixture["mode"]
    if mode == "hidden_read_probe":
        try:
            open("verification-plan.json", "rb")
        except PermissionError:
            print(json.dumps({"failure": "AUTHOR_RESOURCE_DENIED", "isolation": "PYTHON_AUDIT_HOOK_NO_OS_SANDBOX"}))
            return
        raise RuntimeError("Unexpected read access")
    if mode == "alternate":
        # Declaration order is an internal author choice; same public behavior.
        source["commands"].reverse()
    elif mode == "incorrect":
        def change(node):
            if isinstance(node, dict):
                if node.get("field") == "field_priority" and node.get("source") == "input_default":
                    node["value"] = "LOW"
                for child in node.values():
                    change(child)
            elif isinstance(node, list):
                for child in node:
                    change(child)
        change(source)
    elif mode == "malformed":
        source.pop("types")
    elif mode != "identity":
        raise ValueError("INVALID_FIXTURE_MODE")
    print(json.dumps({"source": source, "run": request["run"], "author_adapter": "restricted-fixture-1",
                      "isolation": "PYTHON_AUDIT_HOOK_PROCESS_FIXTURE_NO_OS_SANDBOX"}))


if __name__ == "__main__":
    main()
