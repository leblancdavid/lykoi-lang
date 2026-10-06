"""Trusted compiler-target worker. Python API guard, explicitly not an OS sandbox."""
import argparse
import datetime
import json
import os
from pathlib import Path
import sys
import tempfile
import uuid

source = sys.stdin.read()
code = compile(source, "<frozen-compiler-target>", "exec")
root = Path.cwd().resolve()
runtime = Path(sys.base_prefix).resolve()

if os.name == "posix":
    import resource
    resource.setrlimit(resource.RLIMIT_CPU, (8, 8))
    resource.setrlimit(resource.RLIMIT_FSIZE, (2000000, 2000000))
    resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))


def guard(event, args):
    if event.startswith(("socket.", "subprocess.", "ctypes.")) or event in {"os.system", "os.exec", "os.posix_spawn"}:
        raise PermissionError("CONTAINMENT_FAILURE: forbidden process/network/native API")
    if event == "open":
        path, mode, flags = args
        if isinstance(path, int):
            return
        resolved = Path(path).resolve()
        writing = (isinstance(mode, str) and any(x in mode for x in "wax+")) or (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT))
        if not resolved.is_relative_to(root) and (writing or not resolved.is_relative_to(runtime)):
            raise PermissionError("CONTAINMENT_FAILURE: filesystem scope")
    if event in {"os.remove", "os.rename", "os.mkdir", "os.rmdir", "os.listdir", "os.scandir"}:
        paths = args[:2] if event == "os.rename" else args[:1]
        for path in paths:
            if isinstance(path, (str, bytes)) and not Path(os.fsdecode(path)).resolve().is_relative_to(root):
                raise PermissionError("CONTAINMENT_FAILURE: filesystem mutation/scope")


sys.addaudithook(guard)
exec(code, {"__name__": "__main__", "__file__": "<frozen-compiler-target>"})
