"""Capture public matching-version implementation evidence, no executable install."""
import urllib.request
from common import HERE, save, sha, now

URLS = {
    'opencode-mcp-index.txt': 'https://raw.githubusercontent.com/anomalyco/opencode/v1.18.32/packages/opencode/src/mcp/index.ts',
    'opencode-mcp-catalog.txt': 'https://raw.githubusercontent.com/anomalyco/opencode/v1.18.32/packages/opencode/src/mcp/catalog.ts',
    'opencode-package.txt': 'https://raw.githubusercontent.com/anomalyco/opencode/v1.18.32/packages/opencode/package.json',
    'mcp-sdk-types.txt': 'https://raw.githubusercontent.com/modelcontextprotocol/typescript-sdk/v1.29.0/src/types.ts',
}

if __name__ == '__main__':
    directory = HERE / 'SOURCE'
    directory.mkdir(exist_ok=True)
    records = {}
    for name, url in URLS.items():
        assert not (directory / name).exists()
        try:
            body = urllib.request.urlopen(url, timeout=30).read()
            (directory / name).write_bytes(body)
            records[name] = dict(url=url, sha256=sha(directory/name), bytes=len(body))
        except Exception as exc:
            records[name] = dict(url=url, error=str(exc))
    save('SOURCE/IDENTITIES.json', dict(timestamp=now(), files=records, note='Public version-tag source; installed binary build equivalence not independently attested. No executable or dependency installed.'))
