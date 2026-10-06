"""Prospective R5.88 controller extension; authority-1 history is unchanged.

Native evidence is recomputed, never authorized by producer outcome strings.
The service-owned fixture registry is pinned and immutable across restart.
"""
from __future__ import annotations

import copy
import ast
from functools import lru_cache
import hashlib
from pathlib import Path
import sys

from lykoi_controller import Controller, Failure, canonical
from . import contracts, plans

ROOT = Path(__file__).resolve().parents[2]
STAGES = {"freeze", "structural_receipt", "bdi", "adequacy", "v1", "plan", "bundle", "model", "target", "verification"}
COMPONENTS = (
    "src/lykoi_controller/controller.py", "src/lykoi_workspace/workspace.py",
    "src/lykoi_workspace/producers.py", "src/lykoi_workspace/worker.py",
    "src/lykoi_pipeline/controller.py", "src/lykoi_pipeline/contracts.py",
    "src/lykoi_pipeline/plans.py", "src/lykoi_pipeline/pipeline.py", "src/lykoi_pipeline/author_worker.py",
    "benchmark/evaluation/behavioral_discovery_r5_82.py",
    "benchmark/evaluation/implementation_adequacy_r5_81.py",
    "benchmark/evaluation/formal_requirements_r5_80.py",
    "benchmark/evaluation/benchmark_documents_v1.py",
    "benchmark/semantic/profile_audit_r5_41.py",
    "src/air_compiler/parser.py", "src/air_compiler/model.py", "src/air_compiler/validator.py",
    "src/air_compiler/generator.py", "src/air_compiler/runtime_template.py",
    "schema/axiom-v0.3.schema.json", "schema/formal-requirement-contract-v0.1.schema.json",
    "schema/benchmark-document-contract-v1.schema.json", "schema/sealed-pipeline-v1.schema.json",
)


@lru_cache(maxsize=1)
def component_paths():
    """Explicit import closure of ordinary implementation modules, not discovery.

    Protected inputs, tests, results and requirements are not traversed. Imported
    code can affect V1 validation even where only one function is directly called.
    """
    paths, pending = set(COMPONENTS), list(COMPONENTS)
    prefixes = ("benchmark.semantic", "benchmark.evaluation", "air_compiler", "lykoi_controller", "lykoi_workspace", "lykoi_pipeline")
    def resolve(module):
        if not any(module == p or module.startswith(p + ".") for p in prefixes):
            return None
        base = ("src/" if module.split(".")[0] != "benchmark" else "") + module.replace(".", "/")
        for candidate in (base + ".py", base + "/__init__.py"):
            if (ROOT / candidate).is_file():
                return candidate
        return None
    while pending:
        path = pending.pop()
        if not path.endswith(".py"):
            continue
        module = path.removeprefix("src/").removesuffix(".py").replace("/", ".")
        package = module.rsplit(".", 1)[0]
        for node in ast.walk(ast.parse((ROOT / path).read_text(encoding="utf-8"))):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                base = node.module or ""
                if node.level:
                    parts = package.split(".")
                    base = ".".join(parts[:len(parts) - node.level + 1] + ([base] if base else []))
                names = [base] + [base + "." + a.name for a in node.names if a.name != "*"]
            for name in names:
                candidate = resolve(name)
                if candidate and candidate not in paths:
                    paths.add(candidate)
                    pending.append(candidate)
    return sorted(paths)


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


class PipelineController(Controller):
    def __init__(self, path, principals, *, verification_fixtures=None, author_fixture=None):
        self.verification_fixtures = copy.deepcopy(verification_fixtures or {})
        self.author_fixture = copy.deepcopy(author_fixture)
        super().__init__(path, principals)
        registry = canonical({"plans": self.verification_fixtures, "author": self.author_fixture}).decode()
        self.db.execute("INSERT OR IGNORE INTO config VALUES ('pipeline-fixtures', ?)", (registry,))
        if self.db.execute("SELECT value FROM config WHERE key='pipeline-fixtures'").fetchone()[0] != registry:
            self.close()
            raise Failure("FREEZE_FAILURE", reason="Fixture registry substitution")

    def components(self):
        return {"version": contracts.VERSION, "controller": "authority-1+sealed-pipeline-1",
                "compiler": "0.3.0", "semantics": "axiom-0.3", "author_adapter": "restricted-fixture-1",
                "verifier_adapter": plans.VERSION, "bdi": contracts.discovery.VERSION_BDI,
                "adequacy": contracts.adequacy.VERSION, "v1": contracts.v1.VERSION,
                "schemas": ["authority-1", contracts.VERSION, "FormalRequirementContract-0.1", contracts.v1.VERSION, "axiom-0.3"],
                "tools": {"python": sys.version, "executable_sha256": hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
                          "runtime_libraries": {name: hashlib.sha256((Path(sys.executable).parent / name).read_bytes()).hexdigest()
                              for name in (f"python{sys.version_info.major}{sys.version_info.minor}.zip", f"python{sys.version_info.major}{sys.version_info.minor}.dll")
                              if (Path(sys.executable).parent / name).is_file()}},
                "files": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in component_paths()},
                "fixture_registry": digest({"plans": self.verification_fixtures, "author": self.author_fixture})}

    def what(self, seal):
        a = self.artifact(seal)
        if a["type"] != "frc_seal":
            raise Failure("MISSING_WHAT_SEAL")
        self._fresh(seal)
        approval = self.artifact(a["dependencies"]["approval"])
        fid = approval["dependencies"]["frc"]
        self._need(fid, "ARTIFACT_SEALED")
        content = self.artifact(fid)["content"]
        contracts.frc.validate(content["contract"])
        return fid, content["contract"]

    def expected_plan(self, contract):
        return copy.deepcopy(self.verification_fixtures.get(digest(contract), plans.produce(contract)))

    def check_freeze(self, freeze):
        a = self.artifact(freeze)
        self._fresh(freeze)
        if a["type"] != "freeze" or a["schema"] != contracts.VERSION or a["content"] != self.components():
            raise Failure("FREEZE_FAILURE", reason="Component identity substitution")

    def _register(self, actor, project, kind, content, dependencies=None, schema="authority-1"):
        if kind == "plan" and "author" in self.principals[actor]["roles"]:
            raise Failure("AUTHOR_VERIFICATION_ROLE_CONFLICT")
        if kind in STAGES and schema != contracts.VERSION:
            raise Failure("NATIVE_PIPELINE_EVIDENCE_REQUIRED", stage=kind)
        if kind == "plan" and schema == contracts.VERSION:
            self._role(actor, {"verifier"})
            deps = dependencies or {}
            types = {"seal": "frc_seal", "freeze": "freeze", "structural_receipt": "structural_receipt",
                     "bdi": "bdi", "adequacy": "adequacy", "v1": "v1"}
            if set(deps) != set(types):
                raise Failure("REQUIRED_DEPENDENCY", stage="plan")
            for edge, kind_ in types.items():
                self._subject(deps[edge], project, kind_)
            aid = self._put(kind, project, content, deps, actor, schema)
            self._coherent(aid)
            return aid
        return super()._register(actor, project, kind, content, dependencies, schema)

    def _native(self, aid):
        a = self.artifact(aid)
        kind, value, d = a["type"], a["content"], a["dependencies"]
        if a["schema"] != contracts.VERSION:
            raise Failure("NATIVE_PIPELINE_EVIDENCE_REQUIRED", stage=kind)
        if kind == "freeze":
            self.check_freeze(aid)
            return
        seal = d.get("seal")
        if kind == "structural":
            fid = d["frc"]
            contract = self.artifact(fid)["content"]["contract"]
            expected = contracts.structural(contract, fid)
        elif kind in {"structural_receipt", "bdi", "adequacy", "v1", "plan"}:
            fid, contract = self.what(seal)
            if kind == "structural_receipt":
                projection = self.artifact(d["structural"])
                if projection["dependencies"]["frc"] != fid:
                    raise Failure("DEPENDENCY_MISMATCH")
                self._native(d["structural"])
                expected = contracts.coverage(contract, projection["content"])
            elif kind == "bdi":
                self.check_freeze(d["freeze"])
                self._native(d["structural_receipt"])
                self._need(d["structural_receipt"], "REVIEW_COMMITTED", "ACCEPTED")
                projection = self.artifact(self.artifact(d["structural_receipt"])["dependencies"]["structural"])["content"]
                expected = contracts.bdi(contract, projection)
                if expected["outcome"] != "SUPPORTED":
                    raise Failure("UNSUPPORTED_BDI_SCOPE", unknown=expected["result"]["unknown"])
            elif kind == "adequacy":
                self._native(d["bdi"])
                bd = self.artifact(d["bdi"])["dependencies"]
                if bd != {"seal": seal, "structural_receipt": d["structural_receipt"], "freeze": d["freeze"]}:
                    raise Failure("DEPENDENCY_MISMATCH")
                expected = contracts.adequate(contract, self.artifact(d["bdi"])["content"])
                if expected["outcome"] != "ADEQUATE":
                    raise Failure(expected["result"]["status"], findings=expected["result"]["findings"])
            elif kind == "v1":
                self._native(d["adequacy"])
                if self.artifact(d["adequacy"])["dependencies"]["seal"] != seal:
                    raise Failure("DEPENDENCY_MISMATCH")
                expected = contracts.faithful_v1(contract)
            else:
                self.check_freeze(d["freeze"])
                ad = self.artifact(d["adequacy"])
                if ad["dependencies"] != {"seal": seal, "bdi": d["bdi"], "structural_receipt": d["structural_receipt"], "freeze": d["freeze"]}:
                    raise Failure("DEPENDENCY_MISMATCH")
                if self.artifact(d["v1"])["dependencies"] != {"seal": seal, "adequacy": d["adequacy"]}:
                    raise Failure("DEPENDENCY_MISMATCH")
                for dep in (d["structural_receipt"], d["bdi"], d["adequacy"], d["v1"]):
                    self._native(dep)
                plans.review_coverage(contract, value)
                expected = self.expected_plan(contract)
                plans.review_coverage(contract, expected)
        elif kind == "bundle":
            self.check_bundle(aid)
            return
        elif kind == "model":
            grant = d["grant"]
            self.check_bundle(d["bundle"])
            freeze = self.artifact(grant)["dependencies"]["freeze"]
            if not self.applicable(grant, d["bundle"], freeze)["applicable"]:
                raise Failure("GRANT_DENIAL")
            if (set(value) != {"source", "source_identity", "run", "author_adapter", "isolation"}
                    or value.get("source_identity") != digest(value["source"])
                    or value.get("author_adapter") != "restricted-fixture-1"
                    or value.get("run") != self.artifact(d["bundle"])["content"]["manifest"]["run"]):
                raise Failure("AUTHORING_FAILURE")
            return
        elif kind == "target":
            from air_compiler.generator import generate
            from air_compiler.parser import parse
            self._native(d["model"])
            self.check_freeze(d["freeze"])
            model = self.artifact(d["model"])
            grant = model["dependencies"]["grant"]
            if self.artifact(grant)["dependencies"]["freeze"] != d["freeze"]:
                raise Failure("DEPENDENCY_MISMATCH")
            source = generate(parse(canonical(model["content"]["source"]).decode()))
            expected = {"outcome": "BUILT", "target_source": source, "target_sha256": hashlib.sha256(source.encode()).hexdigest(),
                        "source_identity": model["content"]["source_identity"], "compiler": "0.3.0",
                        "author_run": model["content"]["run"], "grant": grant,
                        "manifest": self.artifact(model["dependencies"]["bundle"])["content"]["manifest"]}
        elif kind == "verification":
            self._native(d["target"])
            self.check_freeze(d["freeze"])
            if self.artifact(d["target"])["dependencies"]["freeze"] != d["freeze"]:
                raise Failure("DEPENDENCY_MISMATCH")
            plan_id = self.artifact(d["plan_seal"])["dependencies"]["plan"]
            plan = self.artifact(plan_id)["content"]
            self._native(plan_id)
            model = self.artifact(d["target"])["dependencies"]["model"]
            bundle = self.artifact(self.artifact(model)["dependencies"]["bundle"])
            if bundle["dependencies"]["plan_seal"] != d["plan_seal"]:
                raise Failure("DEPENDENCY_MISMATCH")
            if value["target"] != d["target"] or value["plan"] != plan_id or value["verifier"] != plans.VERSION:
                raise Failure("VERIFICATION_BINDING_FAILURE")
            if [c["identity"] for c in value["cases"]] != [c["identity"] for c in plan["cases"]]:
                raise Failure("VERIFICATION_PLAN_COVERAGE_GAP")
            from .pipeline import classify_observations
            expected = classify_observations(plan, value["cases"])
            if value["outcome"] != expected:
                raise Failure("VERIFICATION_BINDING_FAILURE")
            return
        else:
            raise Failure("UNKNOWN_NATIVE_STAGE", stage=kind)
        if value != expected:
            raise Failure("NATIVE_EVIDENCE_MISMATCH", stage=kind)

    def _validate(self, actor, project, subject, check, outcome="PASS", access=None):
        a = self._subject(subject, project)
        if a["schema"] != contracts.VERSION:
            return super()._validate(actor, project, subject, check, outcome, access)
        self._role(actor, {"mechanical", "controller"})
        if check != "pipeline-native" or outcome != "PASS":
            raise Failure("NATIVE_PIPELINE_EVIDENCE_REQUIRED")
        self._native(subject)
        self._event("MECHANICALLY_VALIDATED", subject, actor, "mechanical", "MECHANICALLY_VALIDATED",
                    evidence={"check": check, "version": contracts.VERSION})
        return subject

    def _seal_plan(self, actor, project, subject):
        self._native(subject)
        if "author" in self.principals[actor]["roles"]:
            raise Failure("AUTHOR_VERIFICATION_ROLE_CONFLICT")
        return super()._seal_plan(actor, project, subject)

    def _review(self, actor, project, subject, outcome, rationale, access):
        if self.artifact(subject)["type"] == "plan" and "author" in self.principals[actor]["roles"]:
            raise Failure("AUTHOR_VERIFICATION_ROLE_CONFLICT")
        return super()._review(actor, project, subject, outcome, rationale, access)

    def check_bundle(self, aid):
        a = self.artifact(aid)
        d, value = a["dependencies"], a["content"]
        self.check_freeze(d["freeze"])
        v = self.artifact(d["v1"])
        ad = self.artifact(d["adequacy"])
        seal = ad["dependencies"]["seal"]
        fid, _ = self.what(seal)
        plan = self.artifact(d["plan_seal"])["dependencies"]["plan"]
        pd = self.artifact(plan)["dependencies"]
        if pd != {"seal": seal, "freeze": d["freeze"], "structural_receipt": ad["dependencies"]["structural_receipt"],
                  "bdi": ad["dependencies"]["bdi"], "adequacy": d["adequacy"], "v1": d["v1"]} or v["dependencies"] != {"seal": seal, "adequacy": d["adequacy"]}:
            raise Failure("DEPENDENCY_MISMATCH")
        receipt = ad["dependencies"]["structural_receipt"]
        structural = self.artifact(receipt)["dependencies"]["structural"]
        manifest = {"version": contracts.VERSION, "frc": fid, "what_seal": seal, "structural": structural,
                    "structural_receipt": receipt, "bdi": ad["dependencies"]["bdi"], "adequacy": d["adequacy"],
                    "v1": d["v1"], "plan_seal": d["plan_seal"], "components": d["freeze"],
                    "run": value["manifest"]["run"], "fixture": digest(self.author_fixture)}
        if value["manifest"] != manifest or type(manifest["run"]) is not str or not manifest["run"]:
            raise Failure("FREEZE_FAILURE", reason="Run manifest substitution")
        expected_author = {"version": contracts.VERSION, "run": manifest["run"],
                           "v1": v["content"]["normalized"], "toolchain": {"compiler": "0.3.0", "semantics": "axiom-0.3"},
                           "fixture": copy.deepcopy(self.author_fixture)}
        if value["author_input"] != expected_author:
            raise Failure("AUTHOR_INPUT_ALLOWLIST_VIOLATION")
        for x in (structural, receipt, ad["dependencies"]["bdi"], d["adequacy"], d["v1"], plan):
            self._native(x)
            self._need(x, "MECHANICALLY_VALIDATED")
        for x in (structural, receipt, d["adequacy"], d["v1"], plan):
            self._need(x, "REVIEW_COMMITTED", "ACCEPTED")
            if self._blocked(x):
                raise Failure("UNSUPPORTED_OR_DISPUTED")
        self._need(plan, "PLAN_SEALED")
        return manifest

    def _grant(self, actor, project, subject):
        self._role(actor, {"controller"})
        a = self._subject(subject, project, "bundle")
        if a["schema"] != contracts.VERSION:
            raise Failure("NATIVE_PIPELINE_EVIDENCE_REQUIRED")
        self.check_bundle(subject)
        if self._has(subject, "GRANT_ISSUED"):
            raise Failure("GRANT_ALREADY_ISSUED")
        run = a["content"]["manifest"]["run"]
        for event in self.events():
            if event["type"] == "GRANT_ISSUED" and event["subject"] != subject:
                previous = self.artifact(event["subject"])
                if previous["project"] == project and previous["content"].get("manifest", {}).get("run") == run:
                    raise Failure("RUN_IDENTITY_REUSE", run=run)
        self._check_policies(self.what(self.artifact(a["dependencies"]["adequacy"])["dependencies"]["seal"])[0])
        graph = self.closure(subject, authoritative=True)
        grant = self._put("grant", project, {"purpose": "implementation", "action": "author",
                                           "prerequisite_closure": sorted(graph), "authority_events": self._evidence_ids(subject)},
                          {"bundle": subject, "freeze": a["dependencies"]["freeze"]}, actor)
        self._event("GRANT_ISSUED", subject, actor, "controller", "IMPLEMENTATION_AUTHORIZED", evidence=grant)
        return grant

    def applicable(self, grant, subject, freeze, action="author"):
        try:
            g = self.artifact(grant)
            if g["type"] != "grant" or g["content"]["action"] != action or g["dependencies"] != {"bundle": subject, "freeze": freeze}:
                raise Failure("GRANT_IDENTITY_MISMATCH")
            self._fresh(grant)
            self._coherent(grant)
            self._need(subject, "GRANT_ISSUED")
            manifest = self.check_bundle(subject)
            approval = self.artifact(self.artifact(manifest["what_seal"])["dependencies"]["approval"])
            what_only = approval["dependencies"]["structural"]
            for aid in self.closure(grant, authoritative=True):
                if aid == what_only and self.artifact(aid)["content"].get("scope") == "requirements-only; no V1/BDI support asserted":
                    if any(self._has(aid, "REVIEW_COMMITTED", x) for x in ("DISPUTED", "REJECTED", "REVISION_REQUIRED")):
                        raise Failure("AUTHORITY_DISPUTED", artifact=aid)
                    continue
                if self._blocked(aid):
                    raise Failure("AUTHORITY_DISPUTED", artifact=aid)
            return {"applicable": True, "grant": grant}
        except Failure as exc:
            return {"applicable": False, "failure": exc.as_dict()}

    def _bind_verification(self, actor, project, subject):
        self._native(subject)
        if "author" in self.principals[actor]["roles"]:
            raise Failure("SELF_VERIFICATION")
        return super()._bind_verification(actor, project, subject)
