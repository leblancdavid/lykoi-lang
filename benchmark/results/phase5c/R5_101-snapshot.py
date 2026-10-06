"""R5.101 evidence-only snapshot; no false unread declaration or product edits."""
from pathlib import Path
import sys
from lykoi_research import snapshot as baseline

baseline.CHECKS += (
    ("unittest", "discover", "-s", "tests", "-p", "test_collection_query.py", "-v"),
    ("unittest", "discover", "-s", "tests", "-p", "test_collection_query_behavior.py", "-v"),
    ("unittest", "discover", "-s", "tests", "-p", "test_query_normal_path.py", "-v"),
)
text, code = baseline.snapshot("openai/gpt-6.1-sol", "OpenAI")
text = text.replace(
    "- B03 held-out declaration: B03 has not previously been inspected; it remains unread/unexposed.\n"
    "- Declaration basis: explicit operator attestation; this command never opens B03 and cannot prove prior nonexposure.",
    "- Corpus declaration: B01–B20 are exposed development/transfer/regression cases; none is held out.\n"
    "- Snapshot uses R5.96 checks/version recording, without its obsolete B03-unread attestation.")
text = text.replace(
    "Refresh immediately before eventual B03 access. Preserve relevant dirty-tree changes alongside this record.\n"
    "At first access mark B03 exposed; record the first terminal result before any B03-informed Lykoi development.",
    "R5.101 diagnostic baseline. Performance on B01–B20 is development/regression evidence, not held-out generalization evidence.")
text += "\n- FRC: FormalRequirementContract-0.1; typed schema ID: urn:lykoi:frc:collection-query:1 (JSON Schema 2020-12).\n- Structural query: CollectionQuery-0.1; query V1: CollectionQueryDocumentV1.\n- Normal profile: collection-query-1; envelope: LykoiContractV1; author model: LykoiProgram-1.\n- BDI: BehavioralDecisionInventory-0.1; adequacy: ImplementationAdequacy-0.1.\n"
output = Path(__file__).with_name("R5_101-PRE-EVALUATION-SNAPSHOT.md")
with output.open("x", encoding="utf-8", newline="\n") as stream:
    stream.write(text)
print(f"Snapshot: {output}; exit={code}")
sys.exit(code)
