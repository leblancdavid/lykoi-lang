"""Fresh R5.49 provenance evidence; disposable layouts, no benchmark requests."""

import importlib.util
from importlib import machinery
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch
from importlib import metadata

from benchmark.evaluation import dependency_provenance_r5_49 as provenance
from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, loads


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.paths = ['src/package/__init__.py', 'src/package/nested/helper.py',
                      'deployment/utility.py', 'generated/output.py', 'namespace/helper.py']
        for name in self.paths:
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('VALUE = 42\n', encoding='utf-8')
        self.members = provenance.members(self.root, self.paths)
        self.resolver = provenance.Resolver(self.members, installed={})

    def module(self, name, path):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_multiple_repository_layouts(self):
        for name in self.paths:
            with self.subTest(layout=name):
                row = self.resolver.module(self.module('arbitrary_name', self.root / name))
                self.assertEqual(row['category'], 'REPOSITORY_OWNED')
                self.assertEqual(row['source'], name)

    def test_nested_repository_helper(self):
        row = self.resolver.module(self.module('unexpected.helper', self.root / self.paths[1]))
        self.assertEqual(row['category'], 'REPOSITORY_OWNED')

    def test_generated_repository_module(self):
        self.assertEqual(self.resolver.module(self.module('output', self.root / self.paths[3]))['category'],
                         'REPOSITORY_OWNED')

    def test_verified_deployment_alias(self):
        target = self.root / 'renamed.py'
        source = self.root / self.paths[2]
        target.write_bytes(source.read_bytes())
        resolver = provenance.Resolver(self.members, installed={}, copies={target.resolve(): source})
        self.assertEqual(resolver.module(self.module('not_an_exception', target))['source'], self.paths[2])
        target.write_text('VALUE = 43\n')
        with self.assertRaises(ProtocolFailure):
            resolver.module(self.module('not_an_exception', target))

    def test_namespace_descendants(self):
        module = types.ModuleType('space')
        module.__spec__ = machinery.ModuleSpec('space', None, is_package=True)
        module.__spec__.submodule_search_locations = [str(self.root / 'namespace')]
        row = self.resolver.module(module)
        self.assertEqual(row['category'], 'REPOSITORY_OWNED')
        self.assertTrue(row['descendants_required'])

    def test_standard_library(self):
        import json
        self.assertEqual(self.resolver.module(json)['category'], 'STANDARD_RUNTIME')

    def test_builtin_is_derived(self):
        self.assertIn('DERIVED', self.resolver.module(sys)['binding'])

    def test_frozen_actual_loader(self):
        import os
        if os.__spec__.origin == 'frozen':
            self.assertEqual(self.resolver.module(os)['implementation'], 'frozen')
        else:
            self.assertEqual(self.resolver.module(os)['category'], 'STANDARD_RUNTIME')

    def test_third_party_installed_file_identity(self):
        site = self.root / 'site-packages'
        package = site / 'installed.py'
        site.mkdir()
        package.write_text('VALUE = 99\n')
        row = {'distribution': 'independent-fixture', 'version': '1',
               'sha256': provenance.digest(package.read_bytes())}
        resolver = provenance.Resolver(self.members, installed={package.resolve(): [row]},
                                       standard_roots=[self.root], site_roots=[site])
        self.assertEqual(resolver.module(self.module('utility', package))['category'], 'THIRD_PARTY')
        package.write_text('VALUE = 100\n')
        self.assertEqual(resolver.location(package)['category'], 'UNKNOWN')

    def test_real_distribution_metadata_resolution(self):
        site = self.root / 'installed-site'
        info = site / 'independent_fixture-1.0.dist-info'
        info.mkdir(parents=True)
        package = site / 'independent_fixture.py'
        package.write_text('VALUE = 99\n')
        (info / 'METADATA').write_text('Metadata-Version: 2.1\nName: independent-fixture\nVersion: 1.0\n')
        (info / 'RECORD').write_text('independent_fixture.py,,\n')
        installed = list(metadata.distributions(path=[str(site)]))
        self.assertEqual(len(installed), 1)
        with patch.object(provenance.metadata, 'distributions', return_value=installed):
            resolver = provenance.Resolver(self.members)
            self.assertEqual(resolver.module(self.module('installed', package))['category'], 'THIRD_PARTY')

    def test_native_import_diagnostic_not_closure(self):
        if sys.platform == 'win32':
            row = provenance.pe_imports(sys.executable)
            self.assertTrue(row['direct_imports'])
            self.assertFalse(row['complete'])

    def test_malformed_native_image_rejected(self):
        with self.assertRaises(ProtocolFailure):
            provenance.pe_imports(self.root / self.paths[0])

    def test_editable_external_source_not_repository(self):
        external = self.root / 'external_checkout/source.py'
        external.parent.mkdir()
        external.write_text('VALUE = 88\n')
        self.assertEqual(self.resolver.module(self.module('package', external))['category'], 'UNKNOWN')
        row = {'distribution': 'editable-fixture', 'version': '1',
               'sha256': provenance.digest(external.read_bytes())}
        resolver = provenance.Resolver(self.members, installed={external.resolve(): [row]})
        self.assertEqual(resolver.location(external)['category'], 'THIRD_PARTY')

    def test_unbound_file_inside_repository_not_owned(self):
        path = self.root / 'unbound.py'
        path.write_text('VALUE = 88\n')
        self.assertEqual(self.resolver.location(path)['category'], 'UNKNOWN')

    def test_external_executable(self):
        self.assertEqual(provenance.external(sys.executable)['category'], 'NATIVE_EXTERNAL')

    def test_native_external_mutation_changes_identity(self):
        path = self.root / 'native-fixture.bin'
        path.write_bytes(b'first native implementation')
        before = provenance.external(path)
        path.write_bytes(b'second native implementation')
        self.assertNotEqual(before['sha256'], provenance.external(path)['sha256'])

    def test_material_repository_mutation(self):
        path = self.root / self.paths[0]
        path.write_text('VALUE = 43\n')
        with self.assertRaises(ProtocolFailure):
            self.resolver.location(path)

    def test_transitive_graph_and_cycle(self):
        nodes = {n: {'category': 'REPOSITORY_OWNED'} for n in ('operation', 'helper', 'nested')}
        edges = {'operation': ['helper'], 'helper': ['nested'], 'nested': ['helper']}
        self.assertEqual(set(provenance.closure(nodes, edges, ['operation'])['nodes']), set(nodes))

    def test_missing_descendant_rejected(self):
        with self.assertRaises(ProtocolFailure):
            provenance.closure({'operation': {'category': 'REPOSITORY_OWNED'}},
                               {'operation': ['missing']}, ['operation'])

    def test_unknown_dependency_rejected(self):
        with self.assertRaises(ProtocolFailure):
            provenance.closure({'operation': {'category': 'UNKNOWN'}}, {'operation': []}, ['operation'])

    def test_native_closure_not_assumed_from_file_hash(self):
        with self.assertRaises(ProtocolFailure):
            provenance.closure({'python': provenance.external(sys.executable)}, {'python': []}, ['python'])

    def test_dynamic_closure_gap_rejected(self):
        with self.assertRaises(ProtocolFailure):
            provenance.closure({'op': {'category': 'REPOSITORY_OWNED'}}, {'op': []}, ['op'],
                               unresolved=['late import'])

    def test_custom_loader_rejected(self):
        module = types.ModuleType('claimed_builtin')
        module.__spec__ = machinery.ModuleSpec('claimed_builtin', object(), origin='built-in')
        self.assertEqual(self.resolver.module(module)['category'], 'UNKNOWN')

    def test_canonical_round_trip_and_determinism(self):
        module = self.module('fixture', self.root / self.paths[2])
        row = self.resolver.module(module)
        self.assertEqual(row, loads(canonical(row)))
        self.assertEqual(row, self.resolver.module(module))


if __name__ == '__main__':
    unittest.main()
