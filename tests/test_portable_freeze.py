"""Adversarial canonical identity and exact binary verification; synthetic only."""
import copy
from pathlib import Path
import tempfile
import unittest

from lykoi_freeze.content import canonical_text, content_identity, sha_bytes, verify_entry, TEXT_CONTRACT
from lykoi_freeze.freeze import semantic_body
from lykoi_freeze.freeze import provenance_body, verify_content
from lykoi_pipeline.controller import digest


class CanonicalTests(unittest.TestCase):
    def pin(self, data, kind="CANONICAL_CONTENT_PIN"):
        entry = {"dependency": "synthetic", "type": "json-text" if kind == "CANONICAL_CONTENT_PIN" else "binary",
                 "freeze_class": kind, "provenance": {"physical_sha256": sha_bytes(data)}}
        if kind == "CANONICAL_CONTENT_PIN":
            entry.update(canonicalization=TEXT_CONTRACT, content_sha256=content_identity(data))
        else:
            entry["exact_sha256"] = sha_bytes(data)
        return entry

    def test_lf_crlf_and_physical_provenance(self):
        lf = b'{"a":1}\n  exact words\n'
        crlf = lf.replace(b"\n", b"\r\n")
        check = verify_entry(self.pin(lf), crlf)
        self.assertTrue(check["passed"])
        self.assertFalse(check["physical_matches_creation"])
        self.assertEqual(canonical_text(crlf), lf)

    def test_meaningful_mutations_invalidate_pins(self):
        cases = {
            "prompt-word": (b"Never infer conventions.\n", b"Always infer conventions.\n"),
            "mapping-value": (b'{"default":"LOW"}\n', b'{"default":"HIGH"}\n'),
            "source-token": (b"return value + 1\n", b"return value - 1\n"),
            "json-value": (b'{"approved":false}\n', b'{"approved":true}\n'),
            "bdi-rule": (b"if collisions > 1: halt()\n", b"if collisions > 2: halt()\n"),
            "verification": (b'{"returncode":0}\n', b'{"returncode":1}\n'),
            "comment": (b"# do not approve\n", b"# approve\n"),
            "indentation": (b"  return 1\n", b" return 1\n"),
            "json-order": (b'{"a":1,"b":2}\n', b'{"b":2,"a":1}\n'),
            "final-newline": (b"word\n", b"word"),
            "extra-newline": (b"word\n", b"word\n\n"),
            "bom": (b"word\n", b"\xef\xbb\xbfword\n"),
            "unicode-nfc-nfd": ("é\n".encode(), "e\u0301\n".encode()),
            "lone-cr": (b"a\rb", b"a\nb"),
        }
        for name, (old, new) in cases.items():
            with self.subTest(name=name):
                self.assertFalse(verify_entry(self.pin(old), new)["passed"])

    def test_invalid_utf8_and_binary_rejected_as_text(self):
        for data in (b"\xff\xfe", b"MZ\x00binary", b"\xc0\xaf"):
            with self.subTest(data=data), self.assertRaises((ValueError, UnicodeError)):
                canonical_text(data)

    def test_exact_binary_never_normalizes(self):
        binary = b"MZ\x00\r\n\xff"
        pin = self.pin(binary, "EXACT_BINARY_PIN")
        self.assertTrue(verify_entry(pin, binary)["passed"])
        self.assertFalse(verify_entry(pin, binary.replace(b"\r\n", b"\n"))["passed"])

    def test_no_implicit_default_or_contract(self):
        pin = self.pin(b"text")
        pin["freeze_class"] = "UNKNOWN"
        with self.assertRaises(ValueError):
            verify_entry(pin, b"text")
        pin = self.pin(b"text")
        pin["canonicalization"] = "STRIP_WHITESPACE"
        with self.assertRaises(ValueError):
            verify_entry(pin, b"text")

    def test_provenance_does_not_change_semantic_identity(self):
        value = {"version": "synthetic", "dependencies": [self.pin(b"text\n")], "provenance": {"path": "machine-a"}}
        changed = copy.deepcopy(value)
        changed["provenance"] = {"path": "different machine"}
        changed["dependencies"][0]["provenance"]["physical_sha256"] = sha_bytes(b"text\r\n")
        self.assertEqual(digest(semantic_body(value)), digest(semantic_body(changed)))
        changed["dependencies"][0]["content_sha256"] = content_identity(b"new meaning\n")
        self.assertNotEqual(digest(semantic_body(value)), digest(semantic_body(changed)))

    def fixture(self, data):
        entry = self.pin(data)
        entry.update(dependency="synthetic.json", reason="Synthetic authoritative data")
        deps = [entry]
        for name, contract in (("python-runtime", "PYTHON_RUNTIME_CONTRACT_V1"),
                               ("opencode-transport", "OPENCODE_ADAPTER_CONTRACT_V1"),
                               ("platform-containment", "PYTHON_RUNTIME_CONTRACT_V1")):
            deps.append({"dependency": name, "type": "execution-infrastructure", "freeze_class": "COMPATIBILITY_CONTRACT",
                         "contract": contract, "reason": "Synthetic explicit contract", "provenance": {}})
        result = {"version": "protected-portable-freeze-r5.94b-1", "dependencies": deps,
                  "provenance": {"path": "historical-location"}, "active": False, "target_authorizations": []}
        result["identity"] = digest(semantic_body(result))
        result["provenance_identity"] = digest(provenance_body(result))
        return result

    def test_machine_relocation_and_crlf_verification(self):
        data = b'{"meaning":"unchanged"}\n'
        candidate = self.fixture(data)
        with tempfile.TemporaryDirectory(prefix="lykoi second machine é ") as directory:
            root = Path(directory)
            (root / "synthetic.json").write_bytes(data.replace(b"\n", b"\r\n"))
            check = verify_content(candidate, candidate["identity"], root)
            self.assertTrue(check["passed"], check)
            self.assertFalse(check["checks"][0]["physical_matches_creation"])

    def test_resealing_changed_semantics_cannot_match_external_pin(self):
        candidate = self.fixture(b"original\n")
        changed = self.fixture(b"replacement\n")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "synthetic.json").write_bytes(b"replacement\n")
            self.assertFalse(verify_content(changed, candidate["identity"], root)["passed"])

    def test_missing_unknown_class_and_escaping_locator_rejected(self):
        for mutation in (lambda c: c["dependencies"][0].pop("freeze_class"),
                         lambda c: c["dependencies"][0].update(freeze_class="UNSPECIFIED"),
                         lambda c: c["dependencies"][0].update(locator="../escape.json")):
            candidate = self.fixture(b"synthetic\n")
            mutation(candidate)
            candidate["identity"] = digest(semantic_body(candidate))
            candidate["provenance_identity"] = digest(provenance_body(candidate))
            self.assertFalse(verify_content(candidate, candidate["identity"])["passed"])
