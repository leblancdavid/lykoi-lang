"""Closed role disclosure policy. Source identities are opaque, never paths."""
from . import PURPOSE, CLASSIFICATION, VERSION

POLICY = {
    "version": VERSION, "purpose": PURPOSE, "classification": CLASSIFICATION,
    "raw": ["admission", "formalizer", "reviewer"],
    "formal": ["controller", "reviewer", "formalizer", "mechanical", "owner", "verifier", "verification_authority"],
    "author": "grant-bound-author-input-only",
    "verifier": "formal-WHAT-or-exact-target-and-sealed-plan-only",
    "reviewer_barrier": "SOI_COMMITTED-before-candidate-disclosure",
    "development": "no-separate-development-disclosure",
    "scope": "one-source-one-run-first-terminal-result",
    "containment": "trusted-local-service; mediated-worker-inputs; not-hostile-OS-isolation",
}

COUNTERS = ("authorizations", "open_attempts", "source_opens", "source_reads", "source_admissions",
            "formalizer_exposures", "reviewer_exposures", "author_exposures",
            "verifier_exposures", "development_exposures", "denials")
