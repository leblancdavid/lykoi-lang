"""Fixed independent installed-state observations. NOT EXECUTED in R6.3.

Use only under later explicit approval/execution authorization. No installer,
authoring callback or expected-result derivation from generated software.
"""
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit


def observe(manifest, report, stage):
    fixture = json.loads(Path(manifest).read_text(encoding='utf-8'))
    root = Path(fixture['absolute_workdir'])
    package = fixture['containing_package']
    for filename, key in [('setup.py', 'setup_py_sha256'), ('my_module.py', 'my_module_py_sha256')]:
        assert hashlib.sha256((root / filename).read_bytes()).hexdigest() == package[key], filename
    wheel = fixture['artifacts'][0]
    assert hashlib.sha256(Path(fixture['local_wheel_path']).read_bytes()).hexdigest() == wheel['sha256']
    if stage == 'before':
        for name in ('pipefunc', 'my-local-package'):
            try:
                metadata.distribution(name)
            except metadata.PackageNotFoundError:
                continue
            raise AssertionError('Preinstalled target masks installation: ' + name)
        print(json.dumps({'A04-N0': 'PASS_ABSENT', 'behavioral_success': False}))
        return
    assert stage == 'after'
    data = json.loads(Path(report).read_text(encoding='utf-8'))
    local, = [r for r in data['install'] if r['metadata']['name'].lower().replace('_', '-') == 'pipefunc']
    containing, = [r for r in data['install'] if r['metadata']['name'].lower().replace('_', '-') == 'my-local-package']
    assert local['metadata']['version'] == '0.46.0'
    info = local['download_info']
    url = urlsplit(info['url'])
    assert url.scheme == 'file' and url.netloc in ('', 'localhost')
    assert unquote(url.path) == fixture['local_wheel_path']
    assert info['archive_info']['hashes']['sha256'] == wheel['sha256']
    # Input remains exact; output metadata may use internal canonical representations.
    requires = containing['metadata'].get('requires_dist', [])
    assert any('file:' in r and wheel['filename'] in r for r in requires), requires
    installed = metadata.distribution('my-local-package')
    assert installed.version == '0.1.0'
    assert Path(installed.locate_file('my_module.py')).read_bytes() == b''
    dependency = metadata.distribution('pipefunc')
    assert dependency.version == '0.46.0'
    direct = json.loads(dependency.read_text('direct_url.json'))
    assert unquote(urlsplit(direct['url']).path) == fixture['local_wheel_path']
    assert direct['archive_info']['hashes']['sha256'] == wheel['sha256']
    for filename, expected in wheel['installed_payload_sha256'].items():
        assert hashlib.sha256(Path(dependency.locate_file(filename)).read_bytes()).hexdigest() == expected, filename
    print(json.dumps({k: 'PASS' for k in ('A04-PARSE', 'A04-RESOLVE', 'A04-CONTAINING-INSTALL', 'A04-DEPENDENCY-INSTALL')}))


if __name__ == '__main__':
    observe(*sys.argv[1:])
