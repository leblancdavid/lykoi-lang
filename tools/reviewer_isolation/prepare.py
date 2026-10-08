"""Reproducible publisher-only export. No review/model invocation."""
from pathlib import Path
import argparse
from .boundary import canonical, create_package, digest, Halt, verify_package


# Raw-byte pins taken from the preserved R6.8 inventory. Slices use inclusive
# source line numbers, preserving each selected source byte (including CRLF).
SOURCES = [
    ("candidate.md", "benchmark/results/phase6/r6_6/CANDIDATE-SEMANTICS.md", "65befaec8dcf45257c22e7dac38f59c93489330081f3c1818164ae6eeb5392de", [(44, 194)]),
    ("formats.md", "benchmark/results/phase6/r6_6/COMPOSITION-WITNESSES.md", "f272705d93c4c23f77d64517f765b180a400cb67c80523d6f784f00c25ab434d", [(1, 202)]),
    ("compatibility.md", "docs/axiom-v0.3.md", "c95de9a5747ed2f6a839c4ce01e2c3a650a6902c529247d8729e0750e1621740", [(1, 45)]),
    ("values.md", "docs/typed-mutable-values-v1.md", "bb7b1f742f6dd6edd18e3882911d29194374ec7f0e6ffb49973f5123c51c6b1e", [(9, 64), (120, 135), (137, 148)]),
    ("inputs.md", "docs/typed-input-values-v1.md", "080a85372a68b394677a489cf6c9f29f333d64535dc104fcb83d4a7e32f2e372", [(10, 118), (145, 153)]),
    ("predicates.md", "docs/typed-predicates-v1.md", "9e082ae01ec9cbac9c49f0bf9671c1465ff366cf9ff3de1ecfeb285223a934b2", [(9, 99)]),
    ("interfaces.md", "docs/predicate-value-interfaces-v1.md", "59d3338f3667b2eca6659fd2a4ef948761ad85c3f222db2eccef48dbb591e68b", [(9, 86)]),
    ("references.md", "docs/persistent-references-v1.md", "59be9d2f1e78abbfd7a6a574842314b65d4eae3013e3a703bed5ae5a6fcdbd34", [(36, 130), (142, 156), (165, 189)]),
    ("atomic.md", "docs/atomic-durable-history-v1.md", "6d704c7c2a7a18ff41ccc95c3372f8dff790818f621613a12cadd8b3bf9b90c7", [(15, 71), (82, 95)]),
    ("computation.md", "docs/typed-computation-v1.md", "e0fb1d1cf55544cd7e29b6e462045f670a19391518c387c2137dff95cbeb3d8b", [(5, 11), (28, 91), (114, 122)]),
    ("primary.md", "docs/primary-value-interfaces-v1.md", "210911c599e93f925ee494c538ebb57ba052a58553269739c903f0a22d068ab0", [(11, 47), (60, 96)]),
    ("effects.md", "docs/prewrite-conditional-composition-v1.md", "7a2110c3994944936fdd5865578a405214c2241b029514d733c42d35bf9580d9", [(3, 36), (39, 163), (165, 180)]),
    ("history.md", "docs/historical-state-trusted-verification-v1.md", "ccce86fbf69d4b79015e48b8c7296263db683961273a4b755674d42de45c37b8", [(3, 67), (71, 75), (108, 109)]),
]

QUESTIONS = b"""# Review questions and formal obligations

Use only the supplied definitions. No preferred conclusion is supplied.
Assess every interpretation/assembly operation and each atomic codec direction.
For reductions provide a typed composition, equivalence domain, failure and
location equivalence, limit/work accounting, and all imported meanings.
For necessity distinguish a bounded insufficiency argument from failure to find
a reduction. Assess type preservation, progress, termination, determinism,
logical work, paired-layout round trips, source provenance and compositionality.
Reconstruct CFG66, DSV66 and BXC66 from their contracts and identify the first
failure on removing each operation. Identify specification ambiguities without
silently repairing them. Existing-kernel interface excerpts retain their historical
scope; later supplied excerpts refine earlier restrictions only where explicit.
Record any missing normative definition as unresolved; do not retrieve dependencies.
No implementation or format execution. Seal the result before comparison.
"""


def prepare(repo, destination, provenance):
    repo = Path(repo).absolute()
    files, origins = {}, []
    for name, source, expected, ranges in SOURCES:
        # Validate each ancestor for links; no recursive repository enumeration.
        p = repo / source
        for ancestor in (p, *p.parents):
            if ancestor.is_symlink() or getattr(ancestor.lstat(), "st_file_attributes", 0) & 0x400:
                raise Halt("SOURCE_LINK")
        if p.stat().st_nlink != 1:
            raise Halt("SOURCE_HARDLINK")
        data = p.read_bytes()
        if digest(data) != expected:
            raise Halt("FROZEN_SOURCE_IDENTITY_MISMATCH")
        lines = data.splitlines(keepends=True)
        exported = b"\n\n".join(b"".join(lines[a-1:b]) for a, b in ranges)
        files[name] = exported
        origins.append({"file": name, "source": source, "source_sha256": expected,
                        "inclusive_line_ranges": ranges, "export_sha256": digest(exported)})
    files["questions.md"] = QUESTIONS
    audit_source = "docs/semantic-kernel-audit-r5.108.md"
    audit_expected = "8558f4600eb43c85e99a58b89b567011a3c31955a2f98c4187c18aafbc1f7d39"
    from .boundary import no_links
    no_links(repo / audit_source)
    audit = (repo / audit_source).read_bytes()
    if digest(audit) != audit_expected:
        raise Halt("FROZEN_SOURCE_IDENTITY_MISMATCH")
    # Export only definition cells, omitting outcomes, implementation locations,
    # benchmarks and irreducibility/accounting claims from this historical audit.
    definitions = {}
    for line in audit.decode("utf-8").splitlines()[81:128]:
        cells = line.split("|")
        if len(cells) < 7:
            continue
        import re
        match = re.fullmatch(r"CORE (K\d\d)", cells[3].strip())
        if match:
            definitions[match[1]] = cells[1].strip().split(" ", 1)[1]
        elif re.match(r"K(?:19|20|21|22) ", cells[1].strip()):
            key, text = cells[1].strip().split(" ", 1)
            definitions[key] = text + ": " + cells[-2].strip().split(";")[0]
    if set(definitions) != {f"K{i:02}" for i in range(1, 23)}:
        raise Halt("KERNEL_DEFINITION_EXTRACTION")
    definitions.update({"K23": "Finite nonempty-path reachability; see references.md.",
                        "K24": "Checked signed-64 integer addition; see computation.md.",
                        "K25": "Fixed-duration UTC instant displacement; see computation.md.",
                        "K26": "Checked elapsed-day to duration conversion; see effects.md."})
    files["kernel.json"] = canonical({"construct_count": 26, "definitions": definitions})
    origins.append({"file": "kernel.json", "source": audit_source, "source_sha256": audit_expected,
                    "inclusive_line_ranges": [[82, 128]],
                    "transformation": "K01-K18 purpose cells; K19-K22 names/definition notes before semicolon; K23-K26 local normative pointers"})
    # This link resolves wholly inside the export, with an explicit transformation.
    files["formats.md"] = files["formats.md"].replace(b"(CANDIDATE-SEMANTICS.md)", b"(candidate.md)")
    for origin in origins:
        origin["export_sha256"] = digest(files[origin["file"]])
    identity = create_package(destination, files, "candidate-preparation")
    verify_package(destination, identity)
    publisher = {"package_sha256": identity, "sources": origins,
                 "transformation": "inclusive raw-line slices joined with two LF bytes; formats link renamed",
                 "dependencies": "Only the local formats-to-candidate link; no automatic dependency retrieval",
                 "status": "PREPARED_NOT_DISPATCHED_DEPENDENCY_SUFFICIENCY_UNREVIEWED"}
    Path(provenance).write_bytes(canonical(publisher))
    return identity


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("repo"); parser.add_argument("destination"); parser.add_argument("provenance")
    args = parser.parse_args()
    print(prepare(args.repo, args.destination, args.provenance))
