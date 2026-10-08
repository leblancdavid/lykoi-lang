import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.reviewer_isolation import boundary as b
from tools.reviewer_isolation.prepare import prepare


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r69-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.files = {"task.md": b"Synthetic task: return the literal SYNTHETIC_OK.\n"}
        self.package = self.root / "package"
        self.identity = b.create_package(self.package, self.files, "synthetic")
        self.adapter = self.root / "adapter"
        self.adapter.write_bytes(b"synthetic-adapter-fixture-not-executable")
        self.config = {"provider": "synthetic-local", "model": "literal-fixture-1",
                       "adapter_sha256": b.digest(self.adapter.read_bytes()), "environment": {},
                       "tools": [], "network": "none", "session": "new",
                       "retrieval": "disabled", "system_message": "Use only the supplied synthetic input."}

    def run_case(self):
        return b.invoke(self.package, self.identity, self.config, self.adapter, self.root / "evidence")

    def test_reproducible_package(self):
        second = b.create_package(self.root / "second", self.files, "synthetic")
        self.assertEqual(second, self.identity)
        self.assertEqual(b.verify_package(self.package, self.identity)[1], self.files)

    def test_modified_package_refuses_and_preserves_failure(self):
        (self.package / "task.md").write_bytes(b"changed")
        record, anchor = self.run_case()
        self.assertEqual(record["status"], "PACKAGE_CONTENT_MISMATCH")
        self.assertEqual(b.verify_seal(self.root / "evidence", anchor), record)

    def test_wrong_package_identity(self):
        self.identity = "0" * 64
        self.assertEqual(self.run_case()[0]["status"], "PACKAGE_IDENTITY_MISMATCH")

    def test_unexpected_repository_file(self):
        (self.package / "extra.md").write_bytes(b"synthetic repository sentinel")
        with self.assertRaises(b.Halt):
            b.verify_package(self.package, self.identity)

    def test_empty_unexpected_directory(self):
        (self.package / "extra").mkdir()
        with self.assertRaisesRegex(b.Halt, "UNEXPECTED_DIRECTORY"):
            b.verify_package(self.package, self.identity)

    def test_path_traversal_and_platform_aliases(self):
        for name in ("../outside", "/absolute", "C:/secret", "a\\b", "a/../b", "a//b", "CON", "LPT1.txt"):
            with self.subTest(name=name), self.assertRaises(b.Halt):
                b.safe_name(name)

    def test_symlink_denied(self):
        target = self.root / "outside"
        target.write_bytes(b"synthetic forbidden content")
        try:
            (self.package / "link").symlink_to(target)
        except OSError:
            self.skipTest("Host does not permit symlink creation; denial not exercised")
        with self.assertRaisesRegex(b.Halt, "LINK_OR_REPARSE_POINT"):
            b.verify_package(self.package, self.identity)

    def test_hardlink_denied(self):
        os.link(self.package / "task.md", self.root / "alias")
        with self.assertRaisesRegex(b.Halt, "NONREGULAR_OR_HARDLINK"):
            b.verify_package(self.package, self.identity)

    def test_undeclared_dependency(self):
        with self.assertRaisesRegex(b.Halt, "UNDECLARED_DEPENDENCY"):
            b.create_package(self.root / "bad", {"task.md": b"[outside](../outside.md)"}, "synthetic")

    def test_prior_findings_and_guidance_markers(self):
        for content in (b"R6.7 synthetic finding", b"R6_8 synthetic finding", b"AGENTS.md"):
            with self.subTest(content=content), self.assertRaisesRegex(b.Halt, "FORBIDDEN_CONTEXT"):
                b.create_package(self.root / "bad", {"task.md": content}, "synthetic")

    def test_forbidden_file_broker_access(self):
        broker = b.Broker(self.files, ["read_package"])
        self.assertEqual(broker.call("read_package", "task.md"), self.files["task.md"])
        with self.assertRaisesRegex(b.Halt, "FORBIDDEN_FILE"):
            broker.call("read_package", "outside.md")

    def test_unauthorized_retrieval_broker(self):
        with self.assertRaisesRegex(b.Halt, "UNAUTHORIZED_TOOL"):
            b.Broker(self.files, []).call("search", "index")
        with self.assertRaisesRegex(b.Halt, "EXCESS_TOOL_PERMISSION"):
            b.Broker(self.files, ["search"])

    def test_excess_environment_and_tool_configuration(self):
        for key, value in (("environment", {"SYNTHETIC_SECRET": "sentinel"}), ("tools", ["search"]),
                           ("network", "any"), ("retrieval", "shared-index")):
            config = dict(self.config, **{key: value})
            with self.subTest(key=key), self.assertRaises(b.Halt):
                b.validate_config(config)

    def test_inherited_guidance_configuration(self):
        self.config["system_message"] += " synthetic inherited guidance"
        self.assertEqual(self.run_case()[0]["status"], "INHERITED_GUIDANCE_OR_SESSION")

    def test_shared_session_configuration(self):
        self.config["session"] = "reuse-prior-session"
        self.assertEqual(self.run_case()[0]["status"], "INHERITED_GUIDANCE_OR_SESSION")

    def test_provider_labels_do_not_change_contract_meaning(self):
        manifest, files = b.verify_package(self.package, self.identity)
        first = b.request_for(manifest, files, self.config)
        second = b.request_for(manifest, files, dict(self.config, provider="another-provider", model="another-model"))
        for key in ("messages", "tools", "session", "retrieval", "package_sha256", "version"):
            self.assertEqual(first[key], second[key])
        self.assertNotEqual(first["invocation"], second["invocation"])

    def test_substantive_dispatch_refused(self):
        manifest = b.package_manifest(self.files, "candidate-preparation")
        with self.assertRaisesRegex(b.Halt, "SUBSTANTIVE_DISPATCH_NOT_AUTHORIZED"):
            b.request_for(manifest, self.files, self.config)

    def test_unavailable_controls_fail_closed(self):
        with patch.object(b, "sandbox_available", return_value=False), patch.object(b.subprocess, "run") as run:
            record, anchor = self.run_case()
            run.assert_not_called()
        self.assertEqual(record["status"], "ISOLATION_CONTROL_GAP")
        b.verify_seal(self.root / "evidence", anchor)

    def test_adapter_identity_failure(self):
        self.adapter.write_bytes(b"different adapter")
        self.assertEqual(self.run_case()[0]["status"], "ADAPTER_IDENTITY_MISMATCH")

    def test_adapter_failure_mock_transport_only(self):
        result = subprocess.CompletedProcess([], 7, b"partial synthetic", b"synthetic adapter failure")
        with patch.object(b, "sandbox_available", return_value=True), patch.object(b.shutil, "which", return_value="bwrap"), patch.object(b.subprocess, "run", return_value=result):
            record, anchor = self.run_case()
        self.assertEqual(record["status"], "PROVIDER_ADAPTER_FAILURE")
        self.assertEqual((self.root / "evidence" / "output.bin").read_bytes(), result.stdout)
        b.verify_seal(self.root / "evidence", anchor)

    def test_adapter_success_is_not_qualification_mock_transport_only(self):
        result = subprocess.CompletedProcess([], 0, b"SYNTHETIC_OK", b"")
        with patch.object(b, "sandbox_available", return_value=True), patch.object(b.shutil, "which", return_value="bwrap"), patch.object(b.subprocess, "run", return_value=result) as run:
            record, anchor = self.run_case()
            args = run.call_args
            self.assertEqual(args.kwargs["env"], {})
            self.assertIn("--unshare-all", args.args[0])
            self.assertNotIn(str(Path.cwd()), args.args[0])
        self.assertEqual(record["status"], "SEALED_SYNTHETIC_UNQUALIFIED")
        b.verify_seal(self.root / "evidence", anchor)

    def test_adapter_timeout_mock_transport_only(self):
        with patch.object(b, "sandbox_available", return_value=True), patch.object(b.shutil, "which", return_value="bwrap"), patch.object(b.subprocess, "run", side_effect=subprocess.TimeoutExpired([], 30, output=b"partial")):
            self.assertEqual(self.run_case()[0]["status"], "PROVIDER_ADAPTER_TIMEOUT")

    def test_output_modified_after_seal(self):
        _, anchor = self.run_case()
        (self.root / "evidence" / "output.bin").write_bytes(b"modified")
        with self.assertRaisesRegex(b.Halt, "OUTPUT_MODIFIED"):
            b.verify_seal(self.root / "evidence", anchor)

    def test_resealed_modification_fails_external_anchor(self):
        _, anchor = self.run_case()
        p = self.root / "evidence"
        (p / "output.bin").write_bytes(b"modified")
        identity = b.load(p / "seal.json")
        identity["files"]["output.bin"] = b.digest(b"modified")
        (p / "seal.json").write_bytes(b.canonical(identity))
        with self.assertRaisesRegex(b.Halt, "SEAL_ANCHOR_MISMATCH"):
            b.verify_seal(p, anchor)

    def test_missing_provenance(self):
        anchor = b.seal(self.root / "evidence", {"version": b.VERSION})
        with self.assertRaisesRegex(b.Halt, "MISSING_PROVENANCE"):
            b.verify_seal(self.root / "evidence", anchor)

    def test_duplicate_json_keys(self):
        p = self.root / "duplicate.json"
        p.write_bytes(b'{"a":1,"a":2}')
        with self.assertRaisesRegex(b.Halt, "DUPLICATE_JSON_KEY"):
            b.load(p)

    def test_actual_fresh_process_environment_and_history(self):
        # Executed subprocess control, not an OS sandbox or a model-memory test.
        os.environ["R69_SYNTHETIC_SECRET"] = "synthetic sentinel"
        self.addCleanup(os.environ.pop, "R69_SYNTHETIC_SECRET", None)
        code = "import os,sys,json; print(json.dumps({'secret':os.getenv('R69_SYNTHETIC_SECRET'),'cwd':os.getcwd(),'history': 'prior_session' in globals(),'input':sys.stdin.read()}))"
        result = subprocess.run([sys.executable, "-I", "-c", code], env={}, cwd=self.root,
                                input="synthetic input only", text=True, capture_output=True, timeout=10, check=True)
        data = json.loads(result.stdout)
        self.assertIsNone(data["secret"])
        self.assertFalse(data["history"])
        self.assertEqual(Path(data["cwd"]), self.root)
        self.assertEqual(data["input"], "synthetic input only")

    def test_candidate_export_reproducibility_and_exclusions(self):
        repo = Path(__file__).resolve().parents[3]
        first = prepare(repo, self.root / "candidate1", self.root / "origins1.json")
        second = prepare(repo, self.root / "candidate2", self.root / "origins2.json")
        self.assertEqual(first, second)
        manifest, files = b.verify_package(self.root / "candidate1", first)
        self.assertEqual(manifest["purpose"], "candidate-preparation")
        self.assertEqual(len(files), 15)
        for name, data in files.items():
            self.assertIsNone(b.FORBIDDEN.search(name + data.decode()))


if __name__ == "__main__":
    unittest.main()
