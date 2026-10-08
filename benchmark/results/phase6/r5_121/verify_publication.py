"""Read-only R5.121 publication checks; --publish pins new evidence once.

Never executes the Redis contract, authors a target or reruns a semantic stage.
"""
import re
import sys

from .record_evaluation import HERE, PHASE, ROOT, EXPECTED, command, git, load, retained_hashes, save, sha
from lykoi_research import local

GUIDANCE = {"AGENTS.md", "README.md", "benchmark/README.md", "docs/project-overview.md",
            "docs/agent-workflow.md", "docs/research-log.md"}
REPORT = "benchmark/results/phase6/R5_121-REPORT.md"
PREFIX = "benchmark/results/phase6/r5_121/"


def main():
    snapshot = load(HERE / "SNAPSHOT.json")
    assert local.implementation_snapshot() == snapshot["implementation_manifest"]
    assert local.digest(local.implementation_snapshot()) == snapshot["implementation_identity"]
    assert retained_hashes() == snapshot["preserved_artifact_file_hashes"]
    assert git("rev-parse", "HEAD") == snapshot["git_commit"]
    receipt = load(HERE / "LOCAL-EXECUTION-RECEIPT.json")
    approval = load(HERE / "APPROVAL-VERIFICATION.json")
    contract = load(PHASE / "r5_119a/FRC-CANDIDATE-R2.json")
    plan = load(PHASE / "r5_119a/ACCEPTANCE-PLAN-R2.json")
    local.verify_receipt(receipt, approval["approved"], contract["source"], contract,
                         plan, approval["approved"]["evaluator"])
    record = load(HERE / "P6_A03_POST_FIRST_RESULT.json")
    evidence = load(HERE / "SEMANTIC-STAGE-EVIDENCE.json")
    assert record["approved_artifacts"] == approval["observed"] == EXPECTED
    assert record["local_receipt"]["identity"] == evidence["receipt_identity"] == local.digest(receipt)
    assert record["semantic_evidence"]["canonical_sha256"] == local.digest(evidence)
    assert record["implementation_snapshot"]["file_sha256"] == sha(HERE / "SNAPSHOT.json")
    assert record["original_first_result"]["file_sha256"] == sha(ROOT / record["original_first_result"]["path"])
    assert record["result"] == evidence["outcome"] == "STRUCTURAL_COVERAGE_FAILURE"
    assert record["stages"] == evidence["stages"] == dict(
        frc="PASS", structural_coverage="HALTED", bdi="NOT_REACHED", adequacy="NOT_REACHED",
        faithful_v1="NOT_REACHED", acceptance_coverage="NOT_REACHED", authoring="NOT_REACHED",
        compilation="NOT_REACHED", external_verification="NOT_REACHED")
    assert evidence["failure"]["details"]["unsupported"] == [
        "A03-E1", "A03-E2", "A03-I1", "A03-I2", "A03-H1", "A03-I3"]
    checks = load(HERE / "BASELINE-CHECKS.json")
    assert all(c["exit_code"] == 0 for c in checks)
    counts = [int(re.search(r"Ran (\d+) tests?", c["stderr"]).group(1))
              for c in checks if "unittest" in c["command"]]
    assert counts == [13, 22, 30, 34, 22, 9, 13, 3] and sum(counts) == 146
    protected = command(["git", "diff", "--exit-code", "HEAD", "--", "src", "schema", "air",
                         "generated", "tests", "benchmark/evaluation", "benchmark/harness",
                         "benchmark/requirements", "benchmark/results/phase5c"])
    assert protected["exit_code"] == 0, protected
    changed = git("diff", "--name-only", "HEAD").splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard").splitlines()
    assert all(p in GUIDANCE or p == REPORT or p.startswith(PREFIX) for p in changed + untracked)
    whitespace = command(["git", "diff", "--check"])
    assert whitespace["exit_code"] == 0, whitespace
    for name in untracked:
        check = command(["git", "diff", "--no-index", "--check", "--", "NUL", name])
        assert check["exit_code"] in (0, 1) and not check["stdout"].strip(), check
    files = [p for p in HERE.iterdir() if p.is_file() and p.name != "PUBLICATION-IDENTITIES.json"]
    files += [ROOT / REPORT]
    identities = {p.relative_to(ROOT).as_posix(): sha(p) for p in sorted(files)}
    if "--publish" in sys.argv:
        save("PUBLICATION-IDENTITIES.json", {"version": "r5_121-publication-identities-1",
                                           "file_sha256": identities,
                                           "terminal_result_canonical_sha256": local.digest(record)})
    else:
        pinned = load(HERE / "PUBLICATION-IDENTITIES.json")
        assert pinned["file_sha256"] == identities
        assert pinned["terminal_result_canonical_sha256"] == local.digest(record)
    print("PASS: 146 baseline tests; approval/artifacts/receipt; snapshot/kernel; immutable linkage;")
    print("native terminal stages; historical preservation; protected implementation; whitespace; scope; publication hashes")
    print("P6_A03_POST_FIRST_RESULT = " + record["result"])


if __name__ == "__main__":
    main()
