"""Check actual staged Git blobs and install a local, non-destructive size hook."""

import argparse
from pathlib import Path
import re
import shlex
import subprocess
import sys


LIMIT = 100 * 1024 * 1024
MARKER = "# Lykoi staged artifact storage check"
POINTER = re.compile(
    rb"version https://git-lfs.github.com/spec/v1\n"
    rb"oid sha256:[0-9a-f]{64}\nsize [0-9]+\n"
)


def git(root, *args, input=None):
    return subprocess.check_output(["git", *args], cwd=root, input=input)


def repository():
    return Path(subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], text=True
    ).strip())


def check(root):
    entries = []
    conflicts = []
    for record in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not record:
            continue
        meta, name = record.split(b"\t", 1)
        mode, oid, stage = meta.split()
        if stage != b"0":
            conflicts.append(name.decode("utf-8", errors="replace"))
        elif mode != b"160000":  # A gitlink is a commit, not a file blob.
            entries.append((oid, name))
    oids = sorted({oid for oid, name in entries})
    sizes = {}
    if oids:
        response = git(root, "cat-file", "--batch-check=%(objectname) %(objecttype) %(objectsize)",
                       input=b"\n".join(oids) + b"\n")
        for line in response.splitlines():
            oid, kind, size = line.split()
            if kind != b"blob":
                raise ValueError("Index contains a non-blob file object")
            sizes[oid] = int(size)
    errors = [f"Unresolved merge entry: {name}" for name in sorted(set(conflicts))]
    for oid, name in entries:
        if sizes[oid] >= LIMIT:
            errors.append(f"{name.decode('utf-8', errors='replace')}: staged blob is {sizes[oid]:,} bytes (limit {LIMIT:,})")
    changed = set(git(root, "diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").split(b"\0")) - {b""}
    filters = {}
    if changed:
        response = git(root, "check-attr", "--cached", "-z", "--stdin", "filter",
                       input=b"\0".join(sorted(changed)) + b"\0")
        parts = response.split(b"\0")
        for offset in range(0, len(parts) - 1, 3):
            name, attribute, value = parts[offset:offset + 3]
            filters[name] = value
    lfs_count = 0
    for oid, name in entries:
        if name in changed and filters.get(name) == b"lfs":
            if sizes[oid] > 1024 or not POINTER.fullmatch(git(root, "cat-file", "blob", oid.decode())):
                errors.append(f"{name.decode('utf-8', errors='replace')}: LFS-tracked path contains raw data in the index; re-add it with Git LFS installed")
            else:
                lfs_count += 1
    if errors:
        print("Lykoi commit storage check failed:", file=sys.stderr)
        for error in errors:
            print("  " + error, file=sys.stderr)
        print("Install Git LFS, stage .gitattributes, and re-add affected evidence files.\n"
              "For a new bulk family, add an LFS attribute before staging it.\n"
              "Keep genuinely disposable output in benchmark/artifacts/local/.\n"
              "Preserve original evidence; do not delete it just to pass this check.", file=sys.stderr)
        return 1
    print(f"Lykoi storage check: {len(entries)} index blobs below 100 MiB; {lfs_count} changed LFS pointers verified.")
    return 0


def install(root):
    git(root, "lfs", "version")
    configured = subprocess.run(["git", "config", "--get", "core.hooksPath"], cwd=root,
                                capture_output=True, text=True)
    if configured.returncode not in (0, 1):
        raise RuntimeError("Cannot resolve Git hooks configuration")
    if configured.returncode == 0:
        directory = Path(configured.stdout.strip())
        if not directory.is_absolute():
            directory = root / directory
    else:
        directory = Path(git(root, "rev-parse", "--git-path", "hooks").decode().strip())
        if not directory.is_absolute():
            directory = root / directory
    hook = directory / "pre-commit"
    if not directory.is_dir():
        raise RuntimeError(f"Hooks directory does not exist: {directory}")
    if hook.exists() and MARKER not in hook.read_text(encoding="utf-8").splitlines()[:3]:
        raise RuntimeError(f"Existing custom hook preserved: {hook}. Add the check command to that hook manually.")
    # Installs LFS upload hooks without changing Git configuration or forcing replacements.
    git(root, "lfs", "update")
    content = ("#!/bin/sh\n" + MARKER + "\n" +
               "exec " + shlex.quote(Path(sys.executable).as_posix()) +
               " benchmark/artifacts/git_storage.py check\n")
    with hook.open("w" if hook.exists() else "x", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
    hook.chmod(hook.stat().st_mode | 0o111)
    print(f"Installed local size check: {hook}")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("check", "install-hook"), nargs="?", default="check")
    args = parser.parse_args()
    try:
        root = repository()
        return install(root) if args.operation == "install-hook" else check(root)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Lykoi storage check: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
