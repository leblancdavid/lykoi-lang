"""R5.86 authority infrastructure; no language or semantic producer changes."""

from .controller import Controller, Failure, canonical, identity

__all__ = ["Controller", "Failure", "canonical", "identity"]
