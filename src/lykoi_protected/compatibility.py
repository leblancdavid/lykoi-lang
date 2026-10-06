"""Private, fail-closed compatibility views of byte-preserved historical modules.

Only the explicitly listed provenance/version substitutions change source code.
Dependency rebinding is private to these module namespaces (never sys.modules or
shared globals). This preserves historical freezes without copying semantic
implementations into a second maintained engine. All input files and this recipe
are pinned by the new freeze. Unexpected recipe anchors fail at import.
"""
from pathlib import Path
from types import ModuleType

from lykoi_controller import Failure
from lykoi_pipeline.controller import ROOT
from lykoi_pipeline import Pipeline, plans
from . import CLASSIFICATION


def view(path, replacements=(), bindings=None, omit=()):
    source = (ROOT / path).read_text(encoding="utf-8")
    for old, new in (*replacements, *((line, "") for line in omit)):
        if source.count(old) != 1:
            raise Failure("PROTECTED_COMPATIBILITY_DRIFT", path=path, anchor=old)
        source = source.replace(old, new)
    module = ModuleType("lykoi_protected.private." + Path(path).stem)
    module.__file__ = str(ROOT / path)
    module.__package__ = ("lykoi_" + path.split("/")[1].removeprefix("lykoi_")) if path.startswith("src/") else "benchmark.evaluation"
    module.__dict__.update(bindings or {})
    exec(compile(source, module.__file__, "exec"), module.__dict__)
    module.__dict__.update(bindings or {})
    return module


frc = view("benchmark/evaluation/formal_requirements_r5_80.py", (
    ("VERSION = 'FormalRequirementContract-0.1'", "VERSION = 'FormalRequirementContract-protected-0.1'"),
    ("source['classification'] in ('SYNTHETIC', 'PUBLIC')",
     "source['classification'] in ('SYNTHETIC', 'PUBLIC', 'PROTECTED_EVALUATION')")))
contracts = view("src/lykoi_pipeline/contracts.py", bindings={"frc": frc})
mappings = view("src/lykoi_rehearsal/mappings.py", bindings={"contracts": contracts})
verification = view("src/lykoi_rehearsal/verification.py", bindings={"select": mappings.select})
controller = view("src/lykoi_pipeline/controller.py", bindings={"contracts": contracts})
# Class bases must be bound before class definitions, not rebound afterward.
service = view("src/lykoi_rehearsal/service.py", bindings={
    "Pipeline": Pipeline, "PipelineController": controller.PipelineController, "plans": plans,
    "contracts": contracts, "mappings": mappings, "verification": verification}, omit=(
    "from lykoi_pipeline import Pipeline, PipelineController, contracts, plans",))
workspace = view("src/lykoi_workspace/workspace.py", (
    ('        contract = {"schema_version": "FormalRequirementContract-0.1"',
     '        contract = {"schema_version": "FormalRequirementContract-protected-0.1"'),
    ('resolution_contract = {"schema_version": "FormalRequirementContract-0.1"',
     'resolution_contract = {"schema_version": "FormalRequirementContract-protected-0.1"'),
    ('"text": source["text"], "classification": "SYNTHETIC"',
     '"text": source["text"], "classification": self.classification'),
    ('"text": text, "classification": "SYNTHETIC"',
     '"text": text, "classification": self.classification'),
    ('"Public synthetic requirements session "', '"Requirements session "')),
    bindings={"validate": frc.validate, "check_revision": frc.check_revision})
