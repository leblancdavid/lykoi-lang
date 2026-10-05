"""Resolved implementation provenance, independent of module spelling.

This inspector establishes provenance, not a native loader sandbox or complete
execution capsule. Repository membership is an explicit content-bound input.
Distribution metadata is evidence only when its installed file actually matches.
"""

from importlib import machinery, metadata
from pathlib import Path
import sys
import sysconfig
import struct

from benchmark.evaluation.recorder_r5_43 import ProtocolFailure, canonical, digest

PROTOCOL = 'lykoi-dependency-provenance-r5.49'
CATEGORIES = {
    'REPOSITORY_OWNED': 'Resolved implementation is a content-bound repository member or verified deployment copy.',
    'LANGUAGE_RUNTIME': 'Repository-owned implementation designated as Lykoi validation/lowering/runtime infrastructure.',
    'STANDARD_RUNTIME': 'Implementation belongs to the resolved Python standard runtime, excluding installation sites.',
    'THIRD_PARTY': 'External implementation attributed to a distribution by matching installed-file identity.',
    'NATIVE_EXTERNAL': 'Resolved external executable/library, separately content-bound; descendants require closure.',
    'DECLARED_PROGRAM_DEPENDENCY': 'Explicit program input/capability; role orthogonal to implementation provenance.',
    'DEVELOPMENT_AUTHORING': 'Author/editor/provider state unused by the qualified operation; excluded only by an operation boundary.',
    'OPTIONAL_TOOLING': 'Tool unused by core semantics; may still be material to a qualification operation.',
    'UNKNOWN': 'Resolved implementation or attribution cannot be established; material use fails closed.'}


def members(root, paths):
    root = Path(root).resolve()
    result = {}
    for name in sorted(set(paths)):
        path = root / name
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            raise ProtocolFailure('unqualified repository member')
        result[path.resolve()] = {'path': path.relative_to(root).as_posix(),
                                  'sha256': digest(path.read_bytes())}
    return result


def distributions(candidates):
    """No unrelated package list enters identity. Index implementation locations."""
    result = {}
    for distribution in metadata.distributions():
        for file in distribution.files or ():
            path = Path(distribution.locate_file(file)).resolve()
            if path in candidates and path.is_file():
                result.setdefault(path, []).append({
                    'distribution': distribution.metadata['Name'],
                    'version': distribution.version, 'sha256': digest(path.read_bytes())})
    return result


class Resolver:
    def __init__(self, repository_members, *, installed=None, copies=None,
                 standard_roots=None, site_roots=None):
        self.members = repository_members
        self.installed = installed
        self.copies = copies or {}
        paths = sysconfig.get_paths()
        runtime_roots = {paths['stdlib'], paths['platstdlib']}
        shared = sysconfig.get_config_var('DESTSHARED')
        if shared:
            runtime_roots.add(shared)
        if sys.platform == 'win32':
            runtime_roots.add(str(Path(sys.base_prefix) / 'DLLs'))
        self.standard = tuple(Path(p).resolve() for p in
                              (standard_roots or runtime_roots))
        self.sites = tuple(Path(p).resolve() for p in
                           (site_roots or {paths['purelib'], paths['platlib']}))

    def location(self, path):
        path = Path(path).resolve()
        if not path.is_file():
            return {'category': 'UNKNOWN', 'reason': 'implementation unavailable'}
        actual = digest(path.read_bytes())
        member = self.members.get(path)
        if member is None and path in self.copies:
            member = self.members.get(Path(self.copies[path]).resolve())
        if member is not None:
            if actual != member['sha256']:
                raise ProtocolFailure('repository implementation changed')
            return {'category': 'REPOSITORY_OWNED', 'source': member['path'], 'sha256': actual}
        installed = distributions({path}) if self.installed is None else self.installed
        owners = [r for r in installed.get(path, ()) if r['sha256'] == actual]
        if owners:
            return {'category': 'THIRD_PARTY', 'owners': sorted(owners, key=canonical), 'sha256': actual}
        if (any(path.is_relative_to(p) for p in self.standard) and
                not any(path.is_relative_to(p) for p in self.sites)):
            return {'category': 'STANDARD_RUNTIME', 'sha256': actual,
                    'binding': 'separate implementation bytes; exact executable alone is insufficient'}
        return {'category': 'UNKNOWN', 'reason': 'external implementation unattributed', 'sha256': actual}

    def module(self, module):
        spec = getattr(module, '__spec__', None)
        if spec is None:
            return {'category': 'UNKNOWN', 'reason': 'module has no resolved specification'}
        if spec.origin in {'built-in', 'frozen'}:
            expected = machinery.BuiltinImporter if spec.origin == 'built-in' else machinery.FrozenImporter
            if spec.loader is not expected:
                return {'category': 'UNKNOWN', 'reason': 'unqualified special loader'}
            return {'category': 'STANDARD_RUNTIME', 'binding': 'DERIVED from exact interpreter image',
                    'implementation': spec.origin}
        if spec.origin is None and spec.submodule_search_locations is not None:
            locations = [Path(p).resolve() for p in spec.submodule_search_locations]
            # A namespace has no implementation bytes; bind membership/search
            # locations and require each executed descendant separately.
            owned = all(any(p.is_relative_to(location) for p in self.members) for location in locations)
            return {'category': 'REPOSITORY_OWNED' if locations and owned else 'UNKNOWN',
                    'implementation': 'namespace', 'descendants_required': True,
                    'locations': sorted({r['path'].rsplit('/', 1)[0] for p, r in self.members.items()
                                         if any(p.is_relative_to(loc) for loc in locations)})}
        if not isinstance(spec.loader, (machinery.SourceFileLoader, machinery.SourcelessFileLoader,
                                        machinery.ExtensionFileLoader)):
            return {'category': 'UNKNOWN', 'reason': 'custom loader closure unsupported'}
        row = self.location(spec.origin)
        row['implementation'] = ('native-extension' if isinstance(spec.loader, machinery.ExtensionFileLoader)
                                 else 'bytecode' if isinstance(spec.loader, machinery.SourcelessFileLoader) else 'source')
        if row['implementation'] == 'native-extension':
            row['descendants_required'] = True
        return row


def external(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ProtocolFailure('external implementation unavailable')
    return {'category': 'NATIVE_EXTERNAL', 'sha256': digest(path.read_bytes()),
            'descendants_required': True}


def pe_imports(path):
    """Direct PE imports only. Resolution, forwarders and dynamic loads remain open.

    This is diagnostic evidence, explicitly insufficient for closure. Malformed
    images fail closed; no executable is loaded to inspect its import table.
    """
    data = Path(path).read_bytes()
    try:
        def u16(offset):
            return struct.unpack_from('<H', data, offset)[0]
        def u32(offset):
            return struct.unpack_from('<I', data, offset)[0]
        if data[:2] != b'MZ':
            raise ValueError
        header = u32(0x3c)
        if data[header:header + 4] != b'PE\0\0':
            raise ValueError
        optional = header + 24
        magic = u16(optional)
        directory = optional + {0x10b: 96, 0x20b: 112}[magic]
        section_start = optional + u16(header + 20)
        sections = []
        for i in range(u16(header + 6)):
            offset = section_start + i * 40
            sections.append((u32(offset + 12), u32(offset + 8),
                             u32(offset + 20), u32(offset + 16)))
        def physical(rva):
            for base, virtual, raw, size in sections:
                if base <= rva < base + max(virtual, size) and rva - base < size:
                    offset = raw + rva - base
                    if offset >= len(data):
                        raise ValueError
                    return offset
            raise ValueError
        def text(rva):
            offset = physical(rva)
            end = data.index(b'\0', offset, min(len(data), offset + 256))
            return data[offset:end].decode('ascii')
        imports = []
        rva, size = u32(directory + 8), u32(directory + 12)
        if rva:
            offset = physical(rva)
            terminated = False
            for i in range(min(size // 20, 4096)):
                descriptor = offset + i * 20
                fields = struct.unpack_from('<IIIII', data, descriptor)
                if not any(fields):
                    terminated = True
                    break
                imports.append(text(fields[3]))
            if not terminated:
                raise ValueError
        return {'direct_imports': sorted(set(imports)),
                'delay_import_table_present': bool(u32(directory + 13 * 8)),
                'complete': False,
                'unresolved': ['loader search/API-set resolution', 'forwarded exports',
                               'runtime-loaded libraries and OS services']}
    except (ValueError, KeyError, struct.error, UnicodeError):
        raise ProtocolFailure('native image inspection unavailable') from None


def closure(nodes, edges, roots, *, unresolved=()):
    """Validate an explicitly supplied graph, never infer completeness from imports."""
    reached, pending = set(), list(roots)
    while pending:
        name = pending.pop()
        if name in reached:
            continue
        if name not in nodes or name not in edges:
            raise ProtocolFailure('dependency closure incomplete')
        reached.add(name)
        if nodes[name]['category'] == 'UNKNOWN':
            raise ProtocolFailure('material dependency provenance unknown')
        pending.extend(edges[name])
    if unresolved or any(nodes[n].get('descendants_required') for n in reached):
        raise ProtocolFailure('native or dynamic descendant closure unqualified')
    return {'nodes': {n: nodes[n] for n in sorted(reached)},
            'edges': {n: sorted(set(edges[n])) for n in sorted(reached)}}
