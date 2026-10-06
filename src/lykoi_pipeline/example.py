"""Public R5.87 wizard → sealed back-half attempt. Stops at existing V1 gap."""
import argparse
import json
from pathlib import Path
import tempfile

from lykoi_workspace.workspace import Workspace
from lykoi_workspace.example import SOURCE, PRINCIPALS as FRONT_PRINCIPALS, formalize, review
from .controller import PipelineController
from .pipeline import Pipeline

PRINCIPALS = {**FRONT_PRINCIPALS,
    "author": {"credential": "public-author", "roles": ["author"], "projects": ["public"]},
    "verifier": {"credential": "public-verifier", "roles": ["verifier"], "projects": ["public"]},
    "verification_authority": {"credential": "public-plan-owner", "roles": ["verification_authority"], "projects": ["public"]}}
CREDENTIALS = {k: p["credential"] for k, p in PRINCIPALS.items()}
CREDENTIALS["owner"] = CREDENTIALS["human"]


def wizard(c):
    w = Workspace(c, "public", "public-task-wizard", CREDENTIALS)
    policy = w.define_policy("Collection ordering is explicitly unconstrained unless feature requirements specify otherwise.", scope="*")
    w.adopt_policy(CREDENTIALS["owner"], policy, rationale="Public synthetic owner's explicit policy")
    w.ingest(CREDENTIALS["owner"], SOURCE, [policy])
    formalize(w)
    w.answer(CREDENTIALS["owner"], w.ask("PRIORITY.DEFAULT"), "NORMAL")
    formalize(w)
    w.answer(CREDENTIALS["owner"], w.ask("IMPORTANT.MEANING"), "HIGH")
    exact = formalize(w)
    inventory = review(w)
    w.reconcile(inventory)
    w.approve(CREDENTIALS["owner"], exact)
    return w.seal(exact)


def demonstrate(path):
    c = PipelineController(path, PRINCIPALS)
    try:
        seal = wizard(c)
        p = Pipeline(c, "public", CREDENTIALS)
        result = p.execute(p.prepare(seal, "R5.88.PUBLIC.WIZARD.1",
                           review_rationale="Public synthetic bounded relation review, exact item coverage and authority"))
        return p.audit(result)
    finally:
        c.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        evidence = demonstrate(Path(tmp) / "public.sqlite")
    text = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8", newline="\n")
    else:
        print(text)
