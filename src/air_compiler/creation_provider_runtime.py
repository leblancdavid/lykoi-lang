"""Normal API binding for the existing UUID/UTC creation capabilities.

Included by normal compiler dispatch only. Providers are test/host dependencies,
not persisted semantic values or new CLI inputs. Default providers stay unchanged.
"""
from contextvars import ContextVar
from uuid import UUID

_creation_providers = ContextVar("lykoi_creation_providers", default={})
_resource_value_of = value_of
_resource_execute = execute


def value_of(assignment, inputs):
    if assignment["source"] != "capability" or assignment["id"] not in _creation_providers.get():
        return _resource_value_of(assignment, inputs)
    value = _creation_providers.get()[assignment["id"]]()
    kind = by_id("capabilities", assignment["id"])["kind"]
    if kind == "utc_clock":
        valid = isinstance(value, str) and utc_timestamp(value)
    elif kind == "uuid_v4":
        try:
            valid = isinstance(value, str) and UUID(value).version == 4
        except (ValueError, AttributeError):
            valid = False
    else:
        valid = False
    if not valid:
        raise Failure("invalid_state")
    return value


def execute(behavior, inputs, clock=None, *, providers=None):
    providers = {} if providers is None else providers
    allowed = {a["id"] for a in behavior["assignments"] if a["source"] == "capability"} if behavior["kind"] == "create" else set()
    if (type(providers) is not dict or not set(providers) <= allowed
            or not set(providers) <= set(behavior["requires"])
            or not all(callable(p) for p in providers.values())):
        raise ValueError("Providers must bind declared creation capabilities only")
    token = _creation_providers.set(providers)
    try:
        return _resource_execute(behavior, inputs, clock)
    finally:
        _creation_providers.reset(token)
