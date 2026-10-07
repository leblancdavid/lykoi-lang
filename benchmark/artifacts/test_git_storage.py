"""Exercise the size guard against actual disposable Git indexes, without commits."""

import contextlib
import io
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import git_storage


class StorageCheckTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix="lykoi-storage-")
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        subprocess.run(["git", "init", "--quiet", str(self.root)], check=True)

    def put(self, name, content):
        oid = git_storage.git(self.root, "hash-object", "-w", "--stdin", input=content).decode().strip()
        git_storage.git(self.root, "update-index", "--add", "--cacheinfo", "100644", oid, name)

    def check(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            result = git_storage.check(self.root)
        return result, output.getvalue()

    def test_checks_staged_bytes_not_working_copy(self):
        self.put("output.json", b"x" * 100)
        (self.root / "output.json").write_bytes(b"small")
        with patch.object(git_storage, "LIMIT", 100):
            result, text = self.check()
        self.assertEqual(result, 1)
        self.assertIn("staged blob is 100 bytes", text)

    def test_below_limit_passes(self):
        self.put("manifest.json", b"{}\n")
        with patch.object(git_storage, "LIMIT", 4):
            result, _ = self.check()
        self.assertEqual(result, 0)

    def test_lfs_raw_blob_refused_even_below_size_limit(self):
        self.put(".gitattributes", b"*-EVIDENCE.json filter=lfs -text\n")
        self.put("ROUND-EVIDENCE.json", b"{}\n")
        result, text = self.check()
        self.assertEqual(result, 1)
        self.assertIn("raw data in the index", text)

    def test_valid_pointer_passes_even_for_huge_lfs_payload(self):
        self.put(".gitattributes", b"*-EVIDENCE.json filter=lfs -text\n")
        self.put("ROUND-EVIDENCE.json", b"version https://git-lfs.github.com/spec/v1\n"
                 b"oid sha256:" + b"a" * 64 + b"\nsize 500000000\n")
        result, text = self.check()
        self.assertEqual(result, 0)
        self.assertIn("1 changed LFS pointers verified", text)

    def test_attributes_must_be_staged(self):
        self.put(".gitattributes", b"*-EVIDENCE.json filter=lfs -text\n")
        (self.root / ".gitattributes").write_text("", encoding="utf-8")
        self.put("ROUND-EVIDENCE.json", b"raw\n")
        result, _ = self.check()
        self.assertEqual(result, 1)

    def test_custom_hook_is_preserved(self):
        hook = self.root / ".git" / "hooks" / "pre-commit"
        original = "#!/bin/sh\n# Existing user hook\nexit 0\n"
        hook.write_text(original, encoding="utf-8")
        real_git = git_storage.git

        def call(root, *args, **kwargs):
            if args == ("lfs", "version"):
                return b"git-lfs test\n"
            return real_git(root, *args, **kwargs)

        with patch.object(git_storage, "git", side_effect=call):
            with self.assertRaisesRegex(RuntimeError, "custom hook preserved"):
                git_storage.install(self.root)
        self.assertEqual(hook.read_text(encoding="utf-8"), original)


if __name__ == "__main__":
    unittest.main()
