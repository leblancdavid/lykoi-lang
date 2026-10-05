"""Synthetic standalone application; no task-manager or protected inputs."""

import sys
from pathlib import Path

if __name__ == '__main__':
    if sys.argv[1:2] == ['read']:
        Path(sys.argv[2]).read_text()
    raise SystemExit(1 if sys.argv[1:] == ['fail'] else 0)
