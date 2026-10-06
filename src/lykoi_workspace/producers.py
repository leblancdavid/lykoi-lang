"""Unprivileged structured-output adapters. No controller or credentials in inputs."""
from __future__ import annotations

import copy
import subprocess
import sys
from pathlib import Path
from typing import Protocol

from lykoi_controller import Failure, canonical
from lykoi_controller.controller import parse_json


class Producer(Protocol):
    role: str
    session: str
    provenance: dict
    isolation: str

    def produce(self, request: dict) -> dict: ...


class ModelAdapter:
    """Future model invocation callback receives only a copied role-specific request.

    Deployments own callback containment and fresh model contexts. A provider name
    is attribution, not demonstrated provider independence. Output stays untrusted.
    """
    isolation = "CONTEXT_SEPARATED_COOPERATIVE"

    def __init__(self, role, session, invoke, *, provider, model):
        self.role, self.session, self.invoke = role, session, invoke
        self.provenance = {"provider": provider, "model": model}

    def produce(self, request):
        result = self.invoke(copy.deepcopy(request))
        canonical(result)
        if type(result) is not dict:
            raise Failure("INVALID_PRODUCER_OUTPUT")
        return copy.deepcopy(result)


class SubprocessFixture:
    """Separate one-shot local interpreter with stdin allowlist, empty environment.

    Fixture outputs are configured independently, never obtained from the other
    producer. No candidate is passed to the reviewer. This is process/context
    separation, not an OS sandbox against malicious filesystem/network access.
    """
    isolation = "PROCESS_SEPARATED_FIXTURE_NO_OS_SANDBOX"

    def __init__(self, role, session, output):
        self.role, self.session = role, session
        self.output = copy.deepcopy(output)
        self.provenance = {"provider": "local-fixture", "model": "deterministic-1"}

    def produce(self, request):
        worker = Path(__file__).with_name("worker.py")
        process = subprocess.run(
            [sys.executable, "-I", str(worker)],
            input=canonical({"role": self.role, "request": request, "output": self.output}),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env={},
            cwd=worker.parent, timeout=15, check=False,
        )
        if process.returncode:
            raise Failure("PRODUCER_FAILED", role=self.role)
        if len(process.stdout) > 1000000:
            raise Failure("PRODUCER_OUTPUT_TOO_LARGE")
        return parse_json(process.stdout.decode("utf-8"))
