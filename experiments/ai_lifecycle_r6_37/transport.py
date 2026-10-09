"""Unique module loading avoids collisions with historical helper modules."""
import importlib.util
from pathlib import Path
from runner import ROOT, HERE, OUT, TEMP, EXE, environment, sanitize, save, raw, sha, load, config, ask, AGENT_PROMPT

_spec = importlib.util.spec_from_file_location('r637_tools', Path(__file__).with_name('tools.py'))
tools = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(tools)
TOOLS, c, Registry, Journal, package, normalize = (tools.TOOLS, tools.c, tools.Registry,
    tools.Journal, tools.package, tools.normalize)
