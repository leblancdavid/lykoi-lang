"""Independent WHAT-side plan production and deterministic external observations."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from lykoi_controller import Failure
from lykoi_pipeline import plans
from lykoi_pipeline.controller import digest
from lykoi_pipeline.pipeline import classify_observations
from .mappings import select

CONTAINMENT = {"version": "public-trusted-target-containment-1", "program_class": "trusted deterministic compiler output only",
               "process": "isolated CPython -I -S; fresh process per command", "cwd": "fresh case-local temporary directory",
               "environment": "empty", "filesystem": "Python audit guard: case directory read/write, runtime directory read-only",
               "network": "Python socket API denied; no OS firewall", "timeout_seconds": 10,
               "output_bytes": 1000000, "resource_limits": "POSIX CPU=8s, file=2MB, address space=512MB; unavailable on Windows",
               "hostile_code_safety": False, "author_plan_separation": "role/bundle allowlists; no shared model history"}


def produce(contract):
    select(contract)
    plan = plans.produce(contract)
    plan["producer"] = "WHAT_SIDE_DETERMINISTIC_RULE_PRODUCER_1_NOT_FIXTURE_LOOKUP"
    plan["limitations"] = ["Finite title/default observations; no exhaustive string-domain proof"]
    plans.review_coverage(contract, plan)
    return plan


def candidate_plan(adapter, contract, seal, profile_identity):
    result = adapter.produce({"what": copy.deepcopy(contract), "what_seal": seal, "profile_identity": profile_identity})
    plan = result["plan"]
    for case in plan["cases"]:
        case.pop("identity", None)
        case["identity"] = digest(case)
    review(contract, plan)
    return plan


def review(contract, plan):
    select(contract)
    plans.review_coverage(contract, plan)
    # Concrete observations must cover the supported claims. A coverage label
    # alone cannot substitute for an independently executable expectation.
    for row in plan["coverage"]:
        o = next(o for o in contract["obligations"] if o["id"] == row["obligation"])
        linked = [c for c in plan["cases"] if c["identity"] in row["cases"]]
        expected = o["relation"]["parameters"].get("result")
        valid = False
        for case in linked:
            for step in case["steps"]:
                if step.get("files") or set(step) - {"argv", "returncode", "contains", "absent"}:
                    raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", reason="Outside observation envelope")
                argv = step["argv"]
                if not argv or argv[0] != "create" or step["returncode"] != 0:
                    continue
                if o["relation"]["kind"] == "crud" and "--title" in argv:
                    index = argv.index("--title") + 1
                    valid |= index < len(argv) and bool(argv[index].strip()) and argv[index] in step["contains"]
                elif o["relation"]["kind"] == "priority_create":
                    valid |= "--priority" not in argv and expected in step["contains"]
        if not valid:
            raise Failure("VERIFICATION_PLAN_COVERAGE_GAP", obligation=o["id"], reason="Missing executable claim observation")
    return copy.deepcopy(plan)


def execute(target_source, plan):
    observations = []
    worker = Path(__file__).with_name("containment_worker.py")
    with tempfile.TemporaryDirectory(prefix="lykoi-public-verifier-") as tmp:
        for n, case in enumerate(plan["cases"]):
            state = Path(tmp) / str(n)
            state.mkdir()
            steps = []
            for step in case["steps"]:
                try:
                    # File-backed capture avoids unbounded parent memory. Disk quota
                    # is POSIX-only; Windows class explicitly remains trusted-code.
                    with tempfile.TemporaryFile() as out, tempfile.TemporaryFile() as err:
                        result = subprocess.run([sys.executable, "-I", "-S", str(worker), *step["argv"]],
                                                input=target_source.encode(), stdout=out, stderr=err, cwd=state, env={}, timeout=10)
                        out.seek(0)
                        err.seek(0)
                        stdout, stderr = out.read(1000001), err.read(1000001)
                    if max(len(stdout), len(stderr)) > 1000000:
                        raise Failure("CONTAINMENT_FAILURE", reason="output limit")
                    if b"CONTAINMENT_FAILURE" in stderr:
                        raise Failure("CONTAINMENT_FAILURE", reason="Python API denial")
                    steps.append({"returncode": result.returncode, "stdout": stdout.decode("utf-8", errors="replace"),
                                  "stderr": stderr.decode("utf-8", errors="replace"), "unexecutable": None, "files": []})
                except subprocess.TimeoutExpired:
                    raise Failure("CONTAINMENT_FAILURE", reason="execution deadline") from None
                except OSError as exc:
                    steps.append({"returncode": None, "stdout": "", "stderr": "", "unexecutable": type(exc).__name__})
            observations.append({"identity": case["identity"], "steps": steps})
    return classify_observations(plan, observations), observations
