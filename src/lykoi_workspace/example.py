"""Public synthetic wizard fixture and executable WHAT-only demonstration.

Formalizer and reviewer are independently configured known-answer fixtures. They
are not qualified semantic extractors, and do not share candidate output.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import tempfile

from lykoi_controller import Controller, canonical
from .workspace import Workspace
from .producers import SubprocessFixture


SOURCE = "Create tasks with titles. Allow optional priority. List important tasks."
PRINCIPALS = {
    "human": {"credential": "public-human", "roles": ["owner"], "projects": ["public"]},
    "formalizer": {"credential": "public-formalizer", "roles": ["formalizer"], "projects": ["public"]},
    "reviewer": {"credential": "public-reviewer", "roles": ["reviewer"], "projects": ["public"]},
    "mechanical": {"credential": "public-mechanical", "roles": ["mechanical"], "projects": ["public"]},
    "controller": {"credential": "public-controller", "roles": ["controller"], "projects": ["public"]},
}
CREDENTIALS = {role: p["credential"] for role, p in PRINCIPALS.items() if role != "human"}


def obligation(oid, quote, statement, kind, parameters):
    return {"id": oid, "basis": "STATED", "source_quote": quote, "derived_from": [],
            "statement": statement, "relation": {"kind": kind, "parameters": parameters}}


def formalizer_fixture(source, evidence, *, previous=None):
    """Formalizer configuration only. No reviewer output is used."""
    human = next(e["identity"] for e in evidence if e["provenance"] == "human_statement")
    answers = {e["question"]: e for e in evidence if e["provenance"] == "clarification_answer"}
    default = answers.get("PRIORITY.DEFAULT")
    important = answers.get("IMPORTANT.MEANING")
    rows = [obligation("TASK.CREATE.TITLE", "Create tasks with titles.", "Create tasks with the supplied title.",
                       "crud", {"domain": "task creation", "result": "supplied title"}),
            obligation("TASK.CREATE.PRIORITY", "Allow optional priority.",
                       "Omitted priority uses " + default["text"] + "." if default else "Priority may be omitted; result unresolved.",
                       "priority_create", {"condition": "priority omitted", "result": default["text"] if default else "UNRESOLVED"}),
            obligation("TASK.LIST.IMPORTANT", "List important tasks.",
                       "List all tasks whose priority is " + important["text"] + "." if important else "List important tasks; selection unresolved.",
                       "priority_filter", {"domain": "tasks", "multiplicity": "all", "predicate": important["text"] if important else "UNRESOLVED"})]
    authority = {o["id"]: [human] for o in rows}
    questions, issues = [], []
    for key, answer, text, oid in (
        ("PRIORITY.DEFAULT", default, "What should happen when priority is omitted?", "TASK.CREATE.PRIORITY"),
        ("IMPORTANT.MEANING", important, "Which priority makes a task important?", "TASK.LIST.IMPORTANT"),
    ):
        if answer:
            authority[oid].append(answer["identity"])
        else:
            questions.append({"id": key, "text": text, "priority": "BLOCKING", "affects": [oid]})
            issues.append({"id": "ISSUE." + key, "category": "AMBIGUITY", "description": text,
                           "affects": [oid], "alternatives": [], "witness": None, "resolved": False})
    applications = []
    for e in evidence:
        if e["provenance"] == "approved_policy":
            applications.append({"policy": e["identity"], "mode": "DEFAULT"})
            rows.append(obligation("TASK.LIST.ORDER", "List important tasks.", "Collection ordering is explicitly unconstrained.",
                                   "filter_order", {"domain": "task lists", "ordering": "unconstrained"}))
            authority["TASK.LIST.ORDER"] = [e["identity"]]
    lineage = []
    if previous:
        old = {o["id"]: o for o in previous["obligations"]}
        new = {o["id"]: o for o in rows}
        for oid in old.keys() - new.keys():
            lineage.append({"change": "retire", "previous": [oid], "current": [], "reason": "Explicit revision"})
        for oid in old.keys() & new.keys():
            if old[oid] != new[oid]:
                lineage.append({"change": "meaning_change", "previous": [oid], "current": [oid],
                                "reason": "Human clarification or explicit candidate correction; exact evidence retained"})
    return {"obligations": rows, "authority": authority, "questions": questions, "issues": issues,
            "lineage": lineage, "policy_applications": applications}


def reviewer_fixture(source, evidence, revision):
    """Independent source-only configuration. Never accepts or reads candidate data."""
    human = next(e["identity"] for e in evidence if e["provenance"] == "human_statement")
    answers = {e["question"]: e for e in evidence if e["provenance"] == "clarification_answer"}
    d = answers.get("PRIORITY.DEFAULT")
    i = answers.get("IMPORTANT.MEANING")
    clauses = [
        ("TASK.CREATE.TITLE", "Create tasks with titles.", "Create tasks with the supplied title.",
         "crud", {"domain": "task creation", "result": "supplied title"}, [human]),
        ("TASK.CREATE.PRIORITY", "Allow optional priority.",
         "Omitted priority uses " + d["text"] + "." if d else "Priority may be omitted; result unresolved.",
         "priority_create", {"condition": "priority omitted", "result": d["text"] if d else "UNRESOLVED"},
         [human, d["identity"]] if d else [human]),
        ("TASK.LIST.IMPORTANT", "List important tasks.",
         "List all tasks whose priority is " + i["text"] + "." if i else "List important tasks; selection unresolved.",
         "priority_filter", {"domain": "tasks", "multiplicity": "all", "predicate": i["text"] if i else "UNRESOLVED"},
         [human, i["identity"]] if i else [human]),
    ]
    for e in evidence:
        if e["provenance"] == "approved_policy":
            clauses.append(("TASK.LIST.ORDER", "List important tasks.", "Collection ordering is explicitly unconstrained.",
                            "filter_order", {"domain": "task lists", "ordering": "unconstrained"}, [e["identity"]]))
    items, interpretations, authority = [], {}, {}
    for oid, quote, statement, kind, parameters, refs in clauses:
        start = source["text"].index(quote)
        items.append({"id": oid, "spans": [{"start": start, "end": start + len(quote), "quote": quote}],
                      "meaning": statement, "category": "BEHAVIOR", "material": True, "dependencies": []})
        interpretations[oid] = {"statement": statement, "relation": {"kind": kind, "parameters": parameters}}
        authority[oid] = refs
    record = {"id": source["identity"], "text": source["text"], "classification": "SYNTHETIC",
              "sha256": hashlib.sha256(source["text"].encode()).hexdigest()}
    inventory = {"version": "SourceObligationInventory-0.1",
                 "source_commitment": hashlib.sha256(canonical({"revision": revision, "record": record})).hexdigest(),
                 "extractor": "review-context", "context_class": SubprocessFixture.isolation,
                 "items": items, "questions": [] if d and i else ["Unresolved priority interpretation"],
                 "limitations": ["Synthetic known-answer extraction; no semantic completeness qualification"]}
    return {"inventory": inventory, "interpretations": interpretations, "authority": authority}


def formalize(workspace):
    previous = workspace._records("frc")
    prior = previous[-1][1]["content"]["contract"] if previous else None
    source, evidence = workspace.inputs()
    return workspace.formalize(SubprocessFixture("formalizer", "formal-context",
                              formalizer_fixture(source, evidence, previous=prior)))


def review(workspace):
    source, evidence = workspace.inputs()
    return workspace.commit_inventory(SubprocessFixture("reviewer", "review-context",
                                      reviewer_fixture(source, evidence, len(workspace.sources))))


def demonstrate(path):
    c = Controller(path, PRINCIPALS)
    try:
        w = Workspace(c, "public", "public-task-wizard", CREDENTIALS)
        policy = w.define_policy("Collection ordering is explicitly unconstrained unless feature requirements specify otherwise.", scope="*")
        w.adopt_policy("public-human", policy, rationale="Public synthetic project owner elects this policy; not a Lykoi default")
        w.ingest("public-human", SOURCE, [policy])
        initial = formalize(w)
        question = w.ask("PRIORITY.DEFAULT")
        w.answer("public-human", question, "NORMAL")
        formalize(w)
        question = w.ask("IMPORTANT.MEANING")
        w.answer("public-human", question, "HIGH")
        exact = formalize(w)
        inventory = review(w)
        reconciliation = w.reconcile(inventory)
        summary = w.approval_summary(exact)
        approval = w.approve("public-human", exact)
        seal = w.seal(exact)
        assert c.state(exact)["sealed"]
        assert not c.state(exact)["implementation_authorized"]
        return {"classification": "R5_87_REQUIREMENTS_WORKSPACE_IMPLEMENTED", "initial": initial,
                "candidate": exact, "inventory": inventory, "reconciliation": reconciliation,
                "approval": approval, "seal": seal, "summary": summary, "status": w.status(),
                "isolation": SubprocessFixture.isolation, "production_ai_qualified": False}
    finally:
        c.close()


def render_transcript(result):
    """Normal-user view; exact identities remain in the separate audit result."""
    commitments = "\n".join("- " + text for text in result["summary"]["commitments"])
    return ("Wizard: Describe what you want.\n"
            "Human: " + SOURCE + "\n\n"
            "Wizard: What should happen when priority is omitted?\n"
            "Human: Use NORMAL.\n\n"
            "Wizard: Which priority makes a task important?\n"
            "Human: HIGH.\n\n"
            "Wizard: A separate source review agrees with this interpretation. Review what the application will do:\n"
            + commitments + "\n"
            "Wizard: Your adopted project policy leaves list ordering unconstrained. Approve these behaviors?\n"
            "Human: Approve.\n"
            "Wizard: This exact requirements version is approved and sealed. Requirements preparation is complete.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Public synthetic requirements wizard; stops at WHAT seal")
    parser.add_argument("--audit", action="store_true", help="Show exact controller bindings instead of the normal-user transcript")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as tmp:
        result = demonstrate(Path(tmp) / "public.sqlite")
        print(json.dumps(result, indent=2, sort_keys=True) if args.audit else render_transcript(result))
