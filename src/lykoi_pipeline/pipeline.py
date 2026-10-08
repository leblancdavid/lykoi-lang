"""Trusted orchestration, deterministic build and external CLI observations."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from air_compiler.generator import generate
from air_compiler.parser import parse, AirError
from air_compiler.validator import validate
from lykoi_controller import Failure, canonical
from . import contracts, plans
from .controller import digest


def classify_observations(plan, observations):
    failure = None
    if len(observations) != len(plan["cases"]):
        raise Failure("VERIFICATION_PLAN_COVERAGE_GAP")
    for case, observed in zip(plan["cases"], observations):
        if observed["identity"] != case["identity"] or len(observed["steps"]) != len(case["steps"]):
            raise Failure("VERIFICATION_PLAN_COVERAGE_GAP")
        for expected, actual in zip(case["steps"], observed["steps"]):
            if "host" in expected and actual.get("execution") != expected["host"]:
                raise Failure("VERIFICATION_BINDING_FAILURE", reason="Host source/context/input mismatch")
            if actual.get("unexecutable"):
                actual["passed"] = False
                failure = "RUNTIME_FAILURE"
            else:
                passed = (actual["returncode"] == expected["returncode"]
                          and all(x in actual["stdout"] for x in expected["contains"])
                          and all(x not in actual["stdout"] for x in expected.get("absent", [])))
                if expected.get("files"):
                    passed = passed and actual.get("files") == expected["files"]
                for channel in ("stdout", "stderr"):
                    if channel + "_exact" in expected:
                        passed = passed and actual[channel] == expected[channel + "_exact"]
                    if channel + "_json" in expected:
                        try:
                            passed = passed and json.loads(actual[channel]) == expected[channel + "_json"]
                        except (ValueError, TypeError):
                            passed = False
                if expected.get("preserved"):
                    passed = passed and actual.get("preserved") == {p: True for p in expected["preserved"]}
                if actual.get("passed", passed) != passed:
                    raise Failure("VERIFICATION_BINDING_FAILURE", reason="Forged pass result")
                actual["passed"] = passed
                if not passed and failure is None:
                    failure = "BEHAVIORAL_VERIFICATION_FAILURE"
    return failure or "BEHAVIORALLY_VERIFIED"


def external_execute(target_source, plan):
    """Fresh application processes, case-local directories, persisted step state.

    CLI or verifier-owned controlled host, no author success claims.
    Standard subprocess environment is intentionally bounded, not OS sandboxed.
    """
    observations = []
    with tempfile.TemporaryDirectory(prefix="lykoi-verifier-") as tmp:
        root = Path(tmp)
        target = root / "target.py"
        target.write_text(target_source, encoding="utf-8", newline="\n")
        for n, case in enumerate(plan["cases"]):
            state = root / str(n)
            state.mkdir()
            for fixture in case.get("initial_files", []):
                (state / fixture["path"]).write_text(json.dumps(fixture["json"], ensure_ascii=False), encoding="utf-8")
            steps = []
            for step in case["steps"]:
                observed_paths = set(step.get("preserved", [])) | {f["path"] for f in step.get("files", [])}
                durable_before = {p: (state / p).read_bytes() if (state / p).exists() else None for p in observed_paths}
                before = {p: (state / p).read_bytes() if (state / p).exists() else None
                          for p in step.get("preserved", [])}
                try:
                    host = step.get("host")
                    runner = Path(__file__).with_name("host_verifier.py")
                    argv = [str(runner), str(target)] if host is not None else [str(target), *step["argv"]]
                    result = subprocess.run([sys.executable, "-I", "-S", *argv], input=canonical(host).decode() if host is not None else None,
                                            cwd=state, env={}, text=True, capture_output=True, timeout=10)
                    files = []
                    for observation in step.get("files", []):
                        path = state / observation["path"]
                        try:
                            observed = json.loads(path.read_text(encoding="utf-8"))
                        except (OSError, ValueError):
                            observed = {"unobservable": True}
                        files.append({"path": observation["path"], "json": observed})
                    steps.append({"returncode": result.returncode, "stdout": result.stdout,
                                  "stderr": result.stderr, "unexecutable": None, "files": files,
                                  "preserved": {p: ((state / p).read_bytes() if (state / p).exists() else None) == b
                                                 for p, b in before.items()}})
                    if host is not None:
                        steps[-1]["execution"] = copy.deepcopy(host)
                        steps[-1]["durable_sha256"] = {p: {"before": hashlib.sha256(b).hexdigest() if b is not None else None,
                            "after": hashlib.sha256((state / p).read_bytes()).hexdigest() if (state / p).exists() else None} for p, b in durable_before.items()}
                except (OSError, subprocess.TimeoutExpired) as exc:
                    steps.append({"returncode": None, "stdout": "", "stderr": "",
                                   "unexecutable": type(exc).__name__})
                    if "host" in step: steps[-1]["execution"] = copy.deepcopy(step["host"])
            observations.append({"identity": case["identity"], "steps": steps})
    outcome = classify_observations(plan, observations)
    return outcome, observations


def trusted_binding(target, plan_seal, plan):
    """Bind the sealed source-side host requests and exact verifier adapter bytes."""
    if not any("host" in s for c in plan["cases"] for s in c["steps"]): return None
    return {"version": "controlled-host-verification-1", "target_sha256": target["target_sha256"],
            "what_seal": target["manifest"]["what_seal"], "plan_seal": plan_seal,
            "adapter_sha256": hashlib.sha256(Path(__file__).with_name("host_verifier.py").read_bytes()).hexdigest(),
            "requests": [s["host"] for c in plan["cases"] for s in c["steps"] if "host" in s],
            "actor_source": "verifier-owned sealed controlled-host fixture; no authentication inference"}


class Pipeline:
    def __init__(self, controller, project, credentials):
        self.c, self.project, self.credentials = controller, project, dict(credentials)

    def call(self, role, command, **args):
        return self.c.execute(self.credentials[role], self.project, command,
                              expected_revision=self.c.revision, **args)

    def reg(self, role, kind, content, **deps):
        return self.call(role, "register", kind=kind, schema=contracts.VERSION, content=content, dependencies=deps)

    def check(self, aid):
        return self.call("mechanical", "validate", subject=aid, check="pipeline-native")

    def review(self, aid, rationale):
        return self.call("reviewer", "review", subject=aid, outcome="ACCEPTED", rationale=rationale,
                         access=list(self.c.artifact(aid)["dependencies"].values()))

    def prepare(self, seal, run, *, review_rationale):
        """Trusted service coordinates separate principals; reviewers own rationale.

        Local fixture reviewers are cooperative known-answer evidence, not AI truth.
        All candidates and denials remain in the controller even when this halts.
        """
        fid, contract = self.c.what(seal)
        result = {"seal": seal, "frc": fid, "run": run}
        try:
            freeze = self.reg("controller", "freeze", self.c.components())
            result["freeze"] = freeze
            self.check(freeze)
            structural = self.reg("formalizer", "structural", contracts.structural(contract, fid), frc=fid)
            result["structural"] = structural
            self.check(structural)
            # No BDI invocation until coverage and review have both succeeded.
            receipt = self.reg("reviewer", "structural_receipt", contracts.coverage(contract, self.c.artifact(structural)["content"]),
                               seal=seal, structural=structural)
            result["structural_receipt"] = receipt
            self.check(receipt)
            self.review(structural, review_rationale)
            self.review(receipt, review_rationale)
            bdi = self.reg("mechanical", "bdi", contracts.bdi(contract, self.c.artifact(structural)["content"]),
                           seal=seal, structural_receipt=receipt, freeze=freeze)
            result["bdi"] = bdi
            self.check(bdi)
            adequate = self.reg("mechanical", "adequacy", contracts.adequate(contract, self.c.artifact(bdi)["content"]),
                                seal=seal, bdi=bdi, structural_receipt=receipt, freeze=freeze)
            result["adequacy"] = adequate
            self.check(adequate)
            self.review(adequate, review_rationale)
            projected = contracts.faithful_v1(contract)
            v1 = self.reg("formalizer", "v1", projected, seal=seal, adequacy=adequate)
            result["v1"] = v1
            self.check(v1)
            self.review(v1, review_rationale)
            plan = self.reg("verifier", "plan", self.c.expected_plan(contract), seal=seal, freeze=freeze,
                            structural_receipt=receipt, bdi=bdi, adequacy=adequate, v1=v1)
            result["plan"] = plan
            self.check(plan)
            self.review(plan, review_rationale)
            plan_seal = self.call("verification_authority", "seal_plan", subject=plan)
            result["plan_seal"] = plan_seal
            manifest = {"version": contracts.VERSION, "frc": fid, "what_seal": seal, "structural": structural,
                        "structural_receipt": receipt, "bdi": bdi, "adequacy": adequate, "v1": v1,
                        "plan_seal": plan_seal, "components": freeze, "run": run, "fixture": digest(self.c.author_fixture)}
            author_input = {"version": contracts.VERSION, "run": run, "v1": projected["normalized"],
                            "toolchain": {"compiler": "0.3.0", "semantics": "axiom-0.3"}, "fixture": copy.deepcopy(self.c.author_fixture)}
            bundle = self.reg("formalizer", "bundle", {"manifest": manifest, "author_input": author_input},
                              v1=v1, adequacy=adequate, plan_seal=plan_seal, freeze=freeze)
            result["bundle"] = bundle
            self.check(bundle)
            result["grant"] = self.call("controller", "grant", subject=bundle)
            result["outcome"] = "IMPLEMENTATION_AUTHORIZED"
        except Failure as exc:
            result.update(outcome=exc.code, failure=exc.as_dict())
            self.record_halt(result)
        return result

    def record_halt(self, result):
        # A context is owner-readable immutable data, not acceptance authority.
        # Record through the existing controller's journal for restart diagnosis.
        aid = self.call("owner", "register", kind="context", content={"pipeline_halt": copy.deepcopy(result)})
        result["halt_record"] = aid

    def author(self, bundle, grant, freeze):
        applicable = self.c.applicable(grant, bundle, freeze)
        if not applicable["applicable"]:
            raise Failure("GRANT_DENIAL", cause=applicable["failure"])
        reservation = self.call("author", "reserve", subject=bundle, grant=grant, freeze=freeze)
        request = self.c.artifact(bundle)["content"]["author_input"]
        worker = Path(__file__).with_name("author_worker.py")
        with tempfile.TemporaryDirectory(prefix="lykoi-author-") as tmp:
            try:
                result = subprocess.run([sys.executable, "-I", "-S", str(worker)], input=canonical(request).decode(),
                                        cwd=tmp, env={}, text=True, capture_output=True, timeout=10)
                if result.returncode:
                    raise Failure("AUTHORING_FAILURE", stderr=result.stderr)
                output = json.loads(result.stdout)
            except (OSError, subprocess.TimeoutExpired, ValueError) as exc:
                raise Failure("AUTHORING_FAILURE", reason=type(exc).__name__) from exc
            if "failure" in output:
                raise Failure(output["failure"], isolation=output.get("isolation"), reason=output.get("reason"))
        self.c.check_freeze(freeze)
        output["source_identity"] = digest(output["source"])
        model = self.reg("author", "model", output, bundle=bundle, grant=grant)
        self.check(model)
        self.call("author", "complete", subject=reservation, output=model)
        return model

    def build(self, model, freeze):
        self.c.check_freeze(freeze)
        a = self.c.artifact(model)
        source = a["content"]["source"]
        try:
            from air_compiler.profiles import generate as generate_program
            generated = generate_program(source)
        except (AirError, ValueError, KeyError, TypeError) as exc:
            raise Failure("COMPILATION_FAILURE", reason=str(exc)) from exc
        grant = a["dependencies"]["grant"]
        target = self.reg("mechanical", "target", {"outcome": "BUILT", "target_source": generated,
                          "target_sha256": hashlib.sha256(generated.encode()).hexdigest(),
                          "source_identity": a["content"]["source_identity"], "compiler": "0.3.0",
                          "author_run": a["content"]["run"], "grant": grant,
                          "manifest": self.c.artifact(a["dependencies"]["bundle"])["content"]["manifest"]}, model=model, freeze=freeze)
        self.check(target)
        return target

    def verify(self, target, plan_seal, freeze):
        self.c.check_freeze(freeze)
        self.c._native(target)
        plan_id = self.c.artifact(plan_seal)["dependencies"]["plan"]
        plan = self.c.artifact(plan_id)["content"]
        # The separate verifier bundle contains no author self-assessment.
        bundle = {"target": target, "plan_seal": plan_seal, "environment": "CPython isolated fresh subprocess",
                   "fixtures": "fresh per-case directory; shared persisted state only within a case"}
        binding = trusted_binding(self.c.artifact(target)["content"], plan_seal, plan)
        if binding is not None: bundle["trusted_context"] = binding
        outcome, observations = external_execute(self.c.artifact(target)["content"]["target_source"], plan)
        self.c.check_freeze(freeze)
        result = self.reg("verifier", "verification", {"outcome": outcome, "target": target, "plan": plan_id,
                          "verifier": plans.VERSION, "bundle": bundle, "cases": observations,
                          "unresolved": [], "isolation": "EXTERNAL_PROCESS_FIXTURE_NO_OS_SANDBOX"},
                          target=target, plan_seal=plan_seal, freeze=freeze)
        self.check(result)
        self.call("verifier", "bind_verification", subject=result)
        return result

    def execute(self, prepared):
        result = dict(prepared)
        if result["outcome"] != "IMPLEMENTATION_AUTHORIZED":
            return result
        try:
            result["model"] = self.author(result["bundle"], result["grant"], result["freeze"])
            result["target"] = self.build(result["model"], result["freeze"])
            result["verification"] = self.verify(result["target"], result["plan_seal"], result["freeze"])
            result["outcome"] = self.c.artifact(result["verification"])["content"]["outcome"]
            result["terminal_record"] = self.call("owner", "register", kind="context", content={"pipeline_result": copy.deepcopy(result)})
        except Failure as exc:
            result.update(outcome=exc.code, failure=exc.as_dict())
            self.record_halt(result)
        return result

    def audit(self, result):
        """Reconstruct exact content as well as the authority journal after restart."""
        ids = {v for v in result.values() if type(v) is str and ":CJ-1:sha256:" in v}
        graph = set()
        for aid in ids:
            graph.update(self.c.closure(aid))
        return {"run": result, "artifacts": {aid: self.c.artifact(aid) for aid in sorted(graph)},
                "events": [e for e in self.c.events() if e["subject"] in graph],
                "current_components": self.c.components(), "isolation": "LOCAL_FIXTURE_NO_OS_SANDBOX"}

    def audit_run(self, run):
        """Find a halted or completed run using durable journal content only."""
        records = []
        for event in self.c.events():
            if event["type"] != "ARTIFACT_REGISTERED":
                continue
            a = self.c.artifact(event["subject"])
            if a["project"] != self.project:
                continue
            content = a["content"]
            terminal = content.get("pipeline_halt", content.get("pipeline_result"))
            if terminal and terminal.get("run") == run:
                records.append(dict(terminal, terminal_record=event["subject"]))
        if records:
            return self.audit(records[-1])
        raise Failure("UNKNOWN_RUN", run=run)
