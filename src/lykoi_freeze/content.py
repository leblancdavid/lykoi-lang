"""Conservative declared text identity, never an encoding/binary guess."""
import hashlib

TEXT_CONTRACT = "UTF8_CRLF_TO_LF_V1"
CLASSES = {"CANONICAL_CONTENT_PIN", "EXACT_BINARY_PIN", "COMPATIBILITY_CONTRACT", "PROVENANCE_ONLY"}
TEXT_TYPES = {".py": "python-source", ".json": "json-text", ".md": "markdown-text", ".txt": "text"}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def canonical_text(data, contract=TEXT_CONTRACT):
    if contract != TEXT_CONTRACT or type(data) is not bytes:
        raise ValueError("UNDECLARED_CANONICALIZATION")
    text = data.decode("utf-8", errors="strict")
    # NUL is not a supported text representation. BOM, lone CR, final LF and
    # Unicode normalization are deliberately NOT erased or changed.
    if "\x00" in text:
        raise ValueError("BINARY_OR_UNSUPPORTED_TEXT")
    return text.replace("\r\n", "\n").encode("utf-8")


def content_identity(data):
    return sha_bytes(canonical_text(data))


def semantic_entry(entry):
    return {k: v for k, v in entry.items() if k != "provenance"}


def verify_entry(entry, data):
    kind = entry["freeze_class"]
    if kind not in CLASSES:
        raise ValueError("UNKNOWN_DEPENDENCY_CLASS")
    physical = sha_bytes(data)
    if kind == "CANONICAL_CONTENT_PIN":
        if entry["type"] not in TEXT_TYPES.values():
            raise ValueError("TEXT_TYPE_REQUIRED")
        actual = sha_bytes(canonical_text(data, entry["canonicalization"]))
        passed = actual == entry["content_sha256"]
    elif kind == "EXACT_BINARY_PIN":
        if entry["type"] != "binary":
            raise ValueError("BINARY_TYPE_REQUIRED")
        actual, passed = physical, physical == entry["exact_sha256"]
    else:
        raise ValueError("NOT_A_FILE_PIN")
    return {"dependency": entry["dependency"], "freeze_class": kind, "passed": passed,
            "actual_identity": actual, "physical_sha256": physical,
            "physical_matches_creation": physical == entry["provenance"]["physical_sha256"]}
