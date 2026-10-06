"""Record public/synthetic baseline checks and a human held-out declaration."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys

from air_compiler.generator import VERSION as BACKEND_VERSION


ROOT = Path(__file__).resolve().parents[2]
# Explicit selection: never discover the entire historical evaluation/harness tree.
CHECKS = (
    ("air_compiler.cli", "validate", "air/task_manager.json"),
    ("air_compiler.cli", "safety", "air/task_manager.json"),
    ("unittest", "discover", "-s", "tests", "-p", "test_compiler.py", "-v"),
    ("unittest", "discover", "-s", "tests", "-p", "test_application.py", "-v"),
    ("unittest", "discover", "-s", "tests", "-p", "test_authority_controller.py", "-v"),
    ("unittest", "discover", "-s", "tests", "-p", "test_requirements_workspace.py", "-v"),
    ("unittest", "discover", "-s", "tests", "-p", "test_sealed_pipeline.py", "-v"),
    ("unittest", "discover", "-s", "tests", "-p", "test_public_rehearsal.py", "-v"),
    ("unittest", "discover", "-s", "benchmark/evaluation", "-p", "test_benchmark_documents_v1.py", "-v"),
    ("unittest", "discover", "-s", "benchmark/harness", "-p", "test_baseline.py", "-v"),
)


def run(argv, env=None):
    try:
        result = subprocess.run(argv, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, encoding="utf-8",
                                errors="replace", timeout=600)
        return result.returncode, result.stdout
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 1, str(exc)


def block(text):
    # Use a fence longer than any backtick run in captured output.
    width = max((len(part) for part in text.split() if set(part) == {"`"}), default=0)
    fence = "`" * max(3, width + 1)
    return f"{fence}text\n{text.rstrip()}\n{fence}\n"


def snapshot(model, provider):
    started = datetime.now(timezone.utc).isoformat()
    head_code, head = run(["git", "rev-parse", "HEAD"])
    state_code, state = run(["git", "status", "--porcelain=v1", "--untracked-files=all"])
    model_doc = json.loads((ROOT / "air/task_manager.json").read_text(encoding="utf-8"))
    # Read version declarations as data: do not import historical runner machinery.
    import ast
    versions = {}
    module = ast.parse((ROOT / "benchmark/evaluation/benchmark_documents_v1.py").read_text(encoding="utf-8"))
    for node in module.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("VERSION", "CONTRACT"):
                    versions[target.id] = node.value.value
    lines = ["# Lykoi current-environment research snapshot", "",
             f"- Started (UTC): {started}", f"- Git commit: {head.strip()}",
             f"- Core serialization/semantics: {model_doc['axiom_version']} (`docs/axiom-v0.3.md`)",
             f"- Python backend: {BACKEND_VERSION}",
             "- Generic semantic prototype: current repository sources at the recorded commit/tree",
             f"- Representation: {versions['VERSION']} / {versions['CONTRACT']}",
             f"- AI model (declared): {model}", f"- Provider (declared): {provider}",
             f"- Python: {sys.version.replace(chr(10), ' ')}",
             f"- Interpreter (provenance only): {sys.executable}",
             f"- Platform (provenance only): {platform.platform()}",
             "- B03 held-out declaration: B03 has not previously been inspected; it remains unread/unexposed.",
             "- Declaration basis: explicit operator attestation; this command never opens B03 and cannot prove prior nonexposure.",
             "- This records a baseline, not benchmark success or machine/model eligibility.", "",
             "## Working tree before checks", "", block(state or "clean"),
             "## Current relevant checks", ""]
    failed = bool(head_code or state_code)
    env = {**os.environ, "PYTHONPATH": os.pathsep.join((str(ROOT / "src"), str(ROOT))),
           "PYTHONIOENCODING": "utf-8"}
    for args in CHECKS:
        argv = [sys.executable, "-m", *args]
        code, output = run(argv, env)
        failed |= code != 0
        lines.extend([f"### `{shlex.join(['python', '-m', *args])}`", "",
                      f"Exit code: {code}", "", block(output)])
    end_code, end_state = run(["git", "status", "--porcelain=v1", "--untracked-files=all"])
    failed |= end_code != 0
    lines.extend(["## Working tree after checks (before snapshot publication)", "", block(end_state or "clean"),
                  f"- Git metadata exit codes (HEAD / before / after): {head_code} / {state_code} / {end_code}",
                  f"- Check summary: {'FAILURES RECORDED' if failed else 'ALL SELECTED CHECKS PASSED'}",
                  f"- Finished (UTC): {datetime.now(timezone.utc).isoformat()}", "",
                  "Refresh immediately before eventual B03 access. Preserve relevant dirty-tree changes alongside this record.",
                  "At first access mark B03 exposed; record the first terminal result before any B03-informed Lykoi development.", ""])
    return "\n".join(lines), int(failed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-b03-unread", action="store_true",
                        help="attest that B03 has never been inspected; does not access B03")
    parser.add_argument("--model", default="unknown")
    parser.add_argument("--provider", default="unknown")
    parser.add_argument("--output", type=Path, help="new Markdown file in an existing directory (default: stdout)")
    args = parser.parse_args(argv)
    if not args.confirm_b03_unread:
        parser.error("an explicit --confirm-b03-unread declaration is required")
    output = args.output
    if output and (output.exists() or not output.parent.is_dir()):
        parser.error("output must be a new file in an existing directory")
    text, code = snapshot(args.model, args.provider)
    if output:
        with output.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(text)
        print(f"Snapshot recorded: {output}; checks {'failed (see evidence)' if code else 'passed'}")
    else:
        print(text, end="")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
