"""TypedPredicate-1: closed, pure boolean trees; no source prose or code."""
import copy
import json

from lykoi_controller import Failure

VERSION = "typed-predicates-1"


def require(ok, reason):
    if not ok:
        raise Failure("INVALID_TYPED_PREDICATE", reason=reason)


def keys(v, names):
    require(type(v) is dict and set(v) == set(names), "Closed predicate object: " + str(names))


def scalar_type(t):
    require(type(t) is dict, "Typed operand required")
    if t.get("type") == "duration":
        require(t == dict(type="duration", domain=[], unit="seconds"), "Fixed elapsed-second duration only")
        return t
    if t.get("type") == "collection":
        keys(t, ("type", "element", "ordering", "duplicates", "equality"))
        scalar_type(t["element"])
        require(t["element"]["type"] != "collection" and not t["element"].get("nullable", False), "Nonnullable scalar elements")
        require(t["ordering"] == "insertion" and t["duplicates"] in ("allow", "unique") and t["equality"] == "exact", "Existing collection policies")
    else:
        require(set(t) in ({"type", "domain"}, {"type", "domain", "nullable"}), "Explicit scalar type/domain")
        require(t["type"] in ("string", "identifier", "enum", "boolean", "timestamp", "integer"), "Closed scalar value types")
        require(type(t.get("nullable", False)) is bool and (not t.get("nullable", False) or t["type"] in ("timestamp", "integer")), "Bounded timestamp/integer nullability")
        require((t["type"] == "enum" and type(t["domain"]) is list and bool(t["domain"]) and all(type(x) is str for x in t["domain"]) and len(set(t["domain"])) == len(t["domain"])) or (t["type"] != "enum" and t["domain"] == []), "Exact scalar domain")
    return t


def same_type(a, b):
    a, b = copy.deepcopy(a), copy.deepcopy(b)
    a.setdefault("nullable", False); b.setdefault("nullable", False)
    return a == b


def validate(tree, *, fields=None, parameters=None, value_type=None, resources=None, depth=0):
    fields, parameters, resources = fields or {}, parameters or {}, resources or {}
    require(depth < 32, "Bounded tree depth")
    require(type(tree) is dict and tree.get("result_type") == "boolean", "Declared boolean result; no truthiness")
    kind = tree.get("kind")

    def operand(o, presence=False):
        require(type(o) is dict, "Structured operand")
        k = o.get("kind")
        if k == "literal":
            keys(o, ("kind", "type", "value"))
            from .mutable_values import valid_value
            require(valid_value(o["value"], scalar_type(o["type"])), "Typed literal")
            require(not presence, "Literal cannot be omitted")
        else:
            keys(o, ("kind", "type", "stage") if k == "value" else ("kind", "type", "name"))
            t = scalar_type(o["type"])
            if k == "value":
                require(value_type is not None and same_type(t, value_type) and o["stage"] in ("RAW", "TRANSFORMED", "PERSISTED"), "Declared local staged pipeline value")
            else:
                env = fields if k == "field" else parameters if k == "parameter" else resources if k == "resource" else {}
                require(o["name"] in env and same_type(t, env[o["name"]]), "Bound typed reference")
                require(not presence or k == "parameter", "Presence belongs to supplied inputs")
        return o["type"]

    if kind in ("and", "or"):
        keys(tree, ("kind", "result_type", "children"))
        require(type(tree["children"]) is list and 2 <= len(tree["children"]) <= 64, "At least two explicit grouped operands")
        for child in tree["children"]:
            validate(child, fields=fields, parameters=parameters, value_type=value_type, resources=resources, depth=depth + 1)
    elif kind == "not":
        keys(tree, ("kind", "result_type", "child"))
        validate(tree["child"], fields=fields, parameters=parameters, value_type=value_type, resources=resources, depth=depth + 1)
    elif kind in ("is_null", "present"):
        keys(tree, ("kind", "result_type", "operand"))
        t = operand(tree["operand"], presence=kind == "present")
        require(kind != "is_null" or t.get("nullable", False), "Null tests only on supported nullable values")
    elif kind in ("compare", "member"):
        keys(tree, ("kind", "result_type", "operator", "left", "right", "policy", "nulls"))
        left, right = operand(tree["left"]), operand(tree["right"])
        require(tree["nulls"] == "false", "Atomic comparisons involving null return false; NOT complements")
        keys(tree["policy"], ("case", "normalization"))
        require(tree["policy"]["case"] in ("sensitive", "casefold") and tree["policy"]["normalization"] in ("none", "strip"), "Explicit comparison policy")
        if kind == "member":
            require(tree["operator"] == "in" and right["type"] == "collection" and same_type(left, right["element"]), "One canonical scalar-IN-collection direction")
            t = left
        else:
            compatible = same_type(left, right) or (left["type"] == right["type"] == "timestamp" and {k: v for k, v in left.items() if k != "nullable"} == {k: v for k, v in right.items() if k != "nullable"})
            require(tree["operator"] in ("eq", "lt", "le", "gt", "ge") and compatible and left["type"] != "collection", "Compatible scalar comparison; inequality is NOT eq")
            t = left
            require(tree["operator"] == "eq" or t["type"] in ("timestamp", "integer"), "Typed timestamp/integer ordering")
        require(t["type"] in ("string", "identifier", "enum") or tree["policy"] == {"case": "sensitive", "normalization": "none"}, "No normalization/coercion for booleans or timestamps")
    else:
        require(False, "Unknown predicate kind")
    return copy.deepcopy(tree)


def canonical_meaning(tree):
    """Bounded equivalence: associative/commutative/idempotent AND/OR, double NOT.

    No distributive expansion or host-language simplification. Serialization still
    retains the exact tree for faithful V1; this key is for reconciliation only.
    """
    if tree.get("kind") == "not":
        child = tree["child"]
        if child.get("kind") == "not":
            return canonical_meaning(child["child"])
        return ("not", canonical_meaning(child))
    if tree.get("kind") in ("and", "or"):
        k = tree["kind"]
        def flatten(t):
            return [v for c in t["children"] for v in flatten(c)] if t.get("kind") == k else [canonical_meaning(t)]
        return (k, tuple(sorted(set(flatten(tree)), key=repr)))
    return json.dumps(tree, sort_keys=True, separators=(",", ":"))


def decisions(tree, path="predicate"):
    """Every material node is a decision, including full operand/type authority."""
    yield path, json.dumps(tree, sort_keys=True)
    if tree["kind"] in ("and", "or"):
        for i, c in enumerate(tree["children"]):
            yield from decisions(c, path + "/" + str(i))
    elif tree["kind"] == "not":
        yield from decisions(tree["child"], path + "/not")


def observes_persisted(tree):
    if type(tree) is dict:
        return (tree.get("kind") == "value" and tree.get("stage") == "PERSISTED") or any(observes_persisted(v) for v in tree.values())
    return type(tree) is list and any(observes_persisted(v) for v in tree)
