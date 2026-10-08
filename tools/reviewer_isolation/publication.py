"""Check publication scope/identities without touching historical source inputs."""
from pathlib import Path
import subprocess

from . import boundary as b


def publish():
    root = Path.cwd()
    round_dir = root / "benchmark/results/phase6/r6_9"
    expected_package = "b2f178d0db9951e3f2ef781403e1d678921a1f7cd76b7328daf7553dec13e440"
    expected_seal = "c77bd4567e059006da7e429e82bd6a7315553301f428d3bbeaf2e514527b6038"
    b.verify_package(round_dir / "package", expected_package)
    b.verify_seal(round_dir / "evidence-final/host-attempt", expected_seal)
    qualification = b.load(round_dir / "evidence-final/qualification.json")
    if (qualification["tests_run"] != 28 or qualification["failures"]
            or qualification["errors"] or qualification["skips"]):
        raise b.Halt("QUALIFICATION_RESULTS_CHANGED")
    tracked = ["AGENTS.md", "README.md", "docs/agent-workflow.md", "docs/project-overview.md",
               "docs/research-log.md", "docs/decisions.md"]
    paths = [root / p for p in tracked] + [root / "benchmark/results/phase6/R6_9-REPORT.md"]
    paths += [p for p in round_dir.rglob("*") if p.is_file() and p.name != "PUBLICATION.json"]
    paths += list((root / "tools/reviewer_isolation").rglob("*.py"))
    identities = {}
    for p in sorted(paths):
        data = p.read_bytes()
        # Covers untracked publication files too, which git diff --check omits.
        for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
            if line.rstrip(" \t") != line:
                raise b.Halt(f"PUBLICATION_WHITESPACE:{p.relative_to(root)}:{number}")
        identities[p.relative_to(root).as_posix()] = b.digest(data)
    changed = subprocess.run(["git", "diff", "--name-only"], capture_output=True,
                             text=True, check=True).stdout.splitlines()
    untracked = subprocess.run(["git", "ls-files", "--others", "--exclude-standard"],
                               capture_output=True, text=True, check=True).stdout.splitlines()
    if set(changed + untracked) - set(identities) - {"benchmark/results/phase6/r6_9/PUBLICATION.json"}:
        raise b.Halt("UNEXPECTED_CHANGED_FILE")
    subprocess.run(["git", "diff", "--check"], check=True)
    result = {"round": "R6.9", "classification": "R6_9_ISOLATION_CONTROL_GAP",
              "initial_head": "0c35cdf6ee141637dd45b1f8bb50573ce8d839b6",
              "package_sha256": expected_package, "host_attempt_seal_sha256": expected_seal,
              "files": identities, "git_diff_check": "PASS",
              "all_publication_whitespace": "PASS", "scope_check": "PASS",
              "publication_manifest_self_excluded": True}
    target = round_dir / "PUBLICATION.json"
    with target.open("xb") as stream:
        stream.write(b.canonical(result))
    print("PUBLICATION_VERIFIED", b.digest(b.canonical(result)))


if __name__ == "__main__":
    publish()
