"""Trusted host binding is an embedding boundary, not a CLI authentication source."""
AUTHORIZATION = {}  # inserted by normal compiler
_permission_execute = execute
_permission_mutation = execute_mutation
_permission_related = reference_operation
_permission_commit = reference_commit
_permission_context = ContextVar("lykoi_permission", default=None)


def permission_predicate(tree, rows, bindings, inputs):
    def typed(node):
        if type(node) is dict:
            if node.get("kind") == "parameter" and node["name"] in inputs and not mutable_value_valid(inputs[node["name"]], node["type"]): return False
            return all(typed(v) for v in node.values())
        return all(typed(v) for v in node) if type(node) is list else True
    return typed(tree) and reference_condition(tree, rows, bindings, inputs)


def permission_check(op, rows, inputs):
    target = None
    if op["lookup"]:
        key = REFERENCE["identities"][op["entity"]]
        target = next((r for r in rows[op["entity"]] if r[key] == inputs.get(op["lookup"])), None)
        if target is None:
            return  # The existing target lookup error retains precedence.
    bindings = {"primary": target} if target else {}
    for check in op.get("checks", []):
        if not permission_predicate(check["predicate"], rows, bindings, inputs): raise Failure(check["error"])
    if not permission_predicate(op["predicate"], rows, bindings, inputs):
        raise Failure(op["error"])


def permission_call(command, inputs, call, execution_context):
    op = next((o for o in AUTHORIZATION["facts"]["operations"] if o["command"] == command), None)
    if op is None:
        if execution_context is not None: raise ValueError("No authorized context binding")
        return call(inputs)
    actor = op["actor"]
    named = copy.deepcopy(inputs)
    if actor["source"] == "trusted_context":
        # Only an explicitly authorized embedding may supply this host argument.
        # It is deliberately absent from CLI flags, environment and durable state.
        if execution_context is None: raise Failure(actor["missing_error"])
        if type(execution_context) is not dict or set(execution_context) != {"source", "actor"} or execution_context["source"] != actor["context"]:
            raise Failure(actor["invalid_error"])
        value = execution_context["actor"]
        if actor["name"] in named and named[actor["name"]] != value: raise Failure(actor["invalid_error"])
        named[actor["name"]] = value
        if hasattr(named, "supplied"): named.supplied.add(actor["name"])
    elif execution_context is not None:
        raise Failure(actor["invalid_error"])
    if actor["name"] not in named: raise Failure(actor["missing_error"])
    if not mutable_value_valid(named[actor["name"]], actor["type"]): raise Failure(actor["invalid_error"])
    related = next((r for r in REFERENCE["facts"]["operations"] if r["command"] == command), None)
    if related: named = reference_defaults(related, named)
    before = reference_rows()
    permission_check(op, before, named)
    token = _permission_context.set((op, named, before))
    try:
        return call(named)
    finally:
        _permission_context.reset(token)


def reference_commit(before, after, *, migration=False):
    context = _permission_context.get()
    if context and not migration:
        op, inputs, observed = context
        current = reference_rows()
        # Reject a stale host observation; cooperating CLI already holds reservation.
        if current != observed or before != observed: raise Failure(op["error"])
        permission_check(op, current, inputs)
    return _permission_commit(before, after, migration=migration)


def execute(behavior, inputs, clock=None, *, providers=None, execution_context=None):
    command = next(c["token"] for c in SPEC["commands"] if c.get("behavior") == behavior["id"])
    named = {i["name"]: inputs[i["id"]] for i in behavior["inputs"] if i["id"] in inputs}
    def call(values):
        bound = {i["id"]: values[i["name"]] for i in behavior["inputs"] if i["name"] in values}
        return _permission_execute(behavior, bound, clock, providers=providers)
    return permission_call(command, named, call, execution_context)


def execute_mutation(mutation, inputs, *, providers=None, execution_context=None):
    return permission_call(mutation["command"], inputs, lambda values: _permission_mutation(mutation, values, providers=providers), execution_context)


def reference_operation(op, inputs, *, providers=None, execution_context=None):
    return permission_call(op["command"], inputs, lambda values: _permission_related(op, values, providers=providers), execution_context)
