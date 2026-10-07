"""Normal compositional profile for typed value mutations, R5.104."""
import copy

from . import scalar_profile as scalar, query_profile as query
from air_compiler.mutable_values import VERSION as PROFILE, compose, keys, require
from lykoi_controller import Failure

FACETS = ("collections", "mutations", "creation_pipelines")
INPUT_FACET = "input_contracts"
PREDICATE_FACET = "predicate_semantics"
REFERENCE_FACET = "reference_semantics"
ATOMIC_FACET = "atomic_state_semantics"


def typed(relation):
    return relation.get("parameters", {}).get("profile") == PROFILE


def applies(contract):
    return any(typed(o["relation"]) for o in contract["obligations"])


def split(contract):
    require(contract["context"]["domains"].get("capability_profile") == PROFILE, "Explicit mutable composition selection")
    sc, qc = copy.deepcopy(contract), copy.deepcopy(contract)
    sc["obligations"] = [o for o in sc["obligations"] if scalar.typed(o["relation"])]
    qc["obligations"] = [o for o in qc["obligations"] if query.typed(o["relation"])]
    sc["context"]["domains"]["capability_profile"] = scalar.PROFILE
    qc["context"]["domains"]["capability_profile"] = query.PROFILE
    f = scalar.facts(sc)
    scalar_f = copy.deepcopy(f)
    prior = sc["context"]["domains"].get("scalar_base_model")
    # Collection-only introduction steps are validated by the typed extension;
    # the legacy component must retain its own complete scalar migration chain.
    scalar_f["storage"]["version"] = max([1] + [m["to"] for m in scalar_f["evolution"]])
    base = scalar.integrate_facets(scalar.extend_model(scalar_f, prior, allow_unchanged=True), scalar_f) if prior is not None else scalar.lower(scalar_f)
    values = {}
    for o in contract["obligations"]:
        if not typed(o["relation"]):
            continue
        require(o["relation"]["kind"] == "crud", "Typed mutation relation kind")
        p = o["relation"]["parameters"]
        keys(p, ("profile", "facet", "value"))
        require(p["facet"] in FACETS + (INPUT_FACET, PREDICATE_FACET, REFERENCE_FACET, ATOMIC_FACET) and p["facet"] not in values, "Unknown or repeated mutation facet")
        values[p["facet"]] = copy.deepcopy(p["value"])
    closure = contract["context"]["domains"].get("input_value_profile")
    require(closure in (None, "typed-input-values-1"), "Known input/value profile")
    predicates = contract["context"]["domains"].get("predicate_profile")
    require(predicates in (None, "typed-predicates-1"), "Known predicate profile")
    require(not predicates or closure, "Predicate profile composes explicit input stages")
    def common(value):
        if type(value) is dict:
            return value.get("result_type") == "boolean" or any(common(v) for v in value.values())
        return type(value) is list and any(common(v) for v in value)
    require(predicates is not None or not common(contract["obligations"]), "New predicates require explicit versioned profile selection")
    references = contract["context"]["domains"].get("reference_profile")
    require(references in (None, "persistent-references-1") and (not references or predicates), "Explicit reference composition profile")
    atomic = contract["context"]["domains"].get("atomic_state_profile")
    require(atomic in (None, "atomic-durable-state-1") and (not atomic or references), "Explicit atomic state composition selection")
    require(set(values) == set(FACETS + ((INPUT_FACET,) if closure else ()) + ((PREDICATE_FACET,) if predicates else ()) + ((REFERENCE_FACET,) if references else ()) + ((ATOMIC_FACET,) if atomic else ())), "Every selected profile facet required; empty is explicit")
    ir = compose(base, {k: v for k, v in values.items() if k not in (REFERENCE_FACET, ATOMIC_FACET)})
    reference_ir = None
    if references:
        from air_compiler.references import compose as compose_references
        reference_ir = compose_references(ir, values[REFERENCE_FACET])
    require(ir["model"]["state"][0]["schema_version"] == f["storage"]["version"], "Declared storage version must equal composed migration boundary")
    if prior is not None:
        prior_version = prior["state"][0]["schema_version"]
        require(all(len(c["migration"]) == 1 and c["migration"][0]["from"] >= prior_version for c in values["collections"]), "Existing-model collection introduction needs fresh additive migration authority")
    groups = query.validate_relations(qc)
    interfaces = contract["context"]["domains"].get("predicate_value_interface_profile")
    require(interfaces in (None, "predicate-value-interfaces-1"), "Known interface closure profile")
    from air_compiler.collection_query import INTERFACES
    new_interfaces = any("source" in w for m in values["mutations"] for w in m["changes"]) or any(set(q) & set(INTERFACES) for q in groups.values())
    require(not new_interfaces or (interfaces and predicates), "Interface closure requires explicit versioned composition selection")
    if groups:
        binding = contract["context"]["domains"].get("collection_store")
        require(binding == {"kind": "composed_scalar", "state": base["state"][0]["id"]}, "Query binds the same mutable state")
        qc["context"]["domains"]["collection_store"] = {"kind": "mutable_state", "ir": ir, "state": binding["state"]}
        from air_compiler.profiles import validate_mutable_storage
        validate_mutable_storage(qc["context"]["domains"]["collection_store"], list(groups.values()))
    # Discover scalar decisions on its qualified standalone semantic component;
    # preservation of prior model IDs/commands was already checked above.
    sc["context"]["domains"].pop("scalar_base_model", None)
    for o in sc["obligations"]:
        p = o["relation"]["parameters"]
        if p["facet"] == "storage":
            p["value"] = copy.deepcopy(scalar_f["storage"])
    result = dict(scalar=f, mutable=values, ir=ir, queries=groups)
    if reference_ir is not None:
        result["references"] = reference_ir
    if atomic:
        from air_compiler.atomic_state import compose as compose_atomic
        result["atomic_state"] = compose_atomic(ir, reference_ir, values[ATOMIC_FACET])
        require(not set(groups) & {q["id"] for q in values[ATOMIC_FACET]["queries"]}, "No primary/history query command collision")
    return sc, qc, result


def facts(contract):
    return split(contract)[2]


def structural(contract, fid):
    try:
        sc, qc, f = split(contract)
        sp = scalar.structural(sc, fid); scalar.coverage(sc, sp)
        unsupported = [o["id"] for o in contract["obligations"] if not (typed(o["relation"]) or scalar.typed(o["relation"]) or query.typed(o["relation"]))]
        require(contract["context"]["component_authority"] is None, "No arbitrary component authority")
        operations = sp["interface"]["operations"]
        reason = None
    except (Failure, ValueError, KeyError, TypeError, StopIteration) as exc:
        unsupported = [o["id"] for o in contract["obligations"]]
        operations, f, reason = [], None, str(exc)
    rows = [dict(obligation=o["id"], classification="UNSUPPORTED" if o["id"] in unsupported else "REPRESENTED", relation=copy.deepcopy(o["relation"]), operation=None if o["id"] in unsupported else o["id"], justification="Typed compositional mutable-value facets") for o in contract["obligations"]]
    facets = []
    if f:
        for o in contract["obligations"]:
            if typed(o["relation"]):
                facets.append(dict(origin=o["id"], source_quote=o["source_quote"], kind={"collections": "CollectionMutation", "mutations": "ValueMutation", "creation_pipelines": "TransformationPipeline", "input_contracts": "SemanticParameters", "predicate_semantics": "TypedPredicateSemantics", REFERENCE_FACET: "IdentitySelectionGuardComposition", ATOMIC_FACET: "AtomicStateCreationComposition"}[o["relation"]["parameters"]["facet"]], value=copy.deepcopy(o["relation"]["parameters"]["value"])))
                if o["relation"]["parameters"]["facet"] == REFERENCE_FACET:
                    for kind, v in (("TypedFieldIdentity", f["references"]["types"]), ("SelectionCardinalityGuard", f["references"]["checks"]), ("AtomicWriteEffect", f["references"]["facts"]["commit"])):
                        facets.append(dict(origin=o["id"], kind=kind, value=copy.deepcopy(v)))
                if o["relation"]["parameters"]["facet"] == ATOMIC_FACET:
                    for kind, v in (("AtomicWriteEffect", f["atomic_state"]["facts"]["commit"]), ("TypedRecordCreation", f["atomic_state"]["facts"]["operations"]), ("CollectionQuery", f["atomic_state"]["facts"]["queries"]), ("OperationRestriction", f["atomic_state"]["facts"]["append_only"])):
                        facets.append(dict(origin=o["id"], kind=kind, value=copy.deepcopy(v)))
        for o in contract["obligations"]:
            if typed(o["relation"]) and o["relation"]["parameters"]["facet"] == INPUT_FACET:
                for parameter in o["relation"]["parameters"]["value"]:
                    facets += [dict(origin=o["id"], kind="ExternalBinding", value=parameter["binding"]), dict(origin=o["id"], kind="MissingInputBehavior", value=parameter["missing"])]
            if typed(o["relation"]) and o["relation"]["parameters"]["facet"] == "collections":
                for c in o["relation"]["parameters"]["value"]:
                    facets.append(dict(origin=o["id"], kind="CreationValueSource", field=c["name"], value=c["creation"]))
        for m in f["mutable"]["mutations"]:
            origin = next(o["id"] for o in contract["obligations"] if typed(o["relation"]) and o["relation"]["parameters"]["facet"] == "mutations")
            facets += [dict(origin=origin, kind="InputPresence", command=m["command"], value=[dict(input=w["input"], omitted=w["omitted"], missing_error=w["missing_error"]) for w in m["changes"] if "input" in w]), dict(origin=origin, kind="AtomicWriteEffect", command=m["command"], value=m["effect"])]
            for w in m["changes"]:
                if "source" in w:
                    facets.append(dict(origin=origin, kind="CreationValueSource", command=m["command"], field=w["field"], value=w["source"]))
                facets.append(dict(origin=origin, kind="ValidationStage", command=m["command"], field=w["field"], value=w["pipeline"], final_type_error=w["invalid_error"]))
                if INPUT_FACET in f["mutable"]:
                    facets.append(dict(origin=origin, kind="InputValueStages", command=m["command"], field=w["field"], value={"RAW": "supplied_before_pipeline", "TRANSFORMED": "ordered_pipeline_value", "PERSISTED": "complete_candidate_before_atomic_commit"}))
        if INPUT_FACET in f["mutable"]:
            for facet in ("creation_pipelines", "collections"):
                origin = next(o["id"] for o in contract["obligations"] if typed(o["relation"]) and o["relation"]["parameters"]["facet"] == facet)
                for c in f["mutable"][facet]:
                    field, declaration = (c["field"], c) if facet == "creation_pipelines" else (c["name"], c["creation"])
                    if "pipeline" in declaration:
                        facets.append(dict(origin=origin, kind="ValidationStage", command="creation", field=field, value=declaration["pipeline"], final_type_error=declaration["error"]))
    return dict(version=PROFILE, source_frc=fid, rows=rows, facts=f, facets=facets, interface=dict(version=scalar.discovery.VERSION_BDI, operations=operations), unsupported=unsupported, profile_failure=reason, observation_scope="Explicit typed single-record values, ordered pipelines and same-state readonly queries", reachability="Bounded source captures, not general formalization completeness")


def coverage(contract, projection):
    expected = structural(contract, projection["source_frc"])
    if expected != projection or expected["unsupported"]:
        raise Failure("STRUCTURAL_COVERAGE_FAILURE", unsupported=expected["unsupported"], reason=expected["profile_failure"])
    return dict(outcome="SUPPORTED", version=PROFILE, rows=expected["rows"], scope=expected["observation_scope"], limitations=[expected["reachability"]])


def bdi(contract, projection):
    coverage(contract, projection)
    result = scalar.discovery.discover(contract, projection["interface"])
    # Prospective extension: retain historical discovery engine/rules unchanged.
    # Each material choice has finite alternatives and exact source-clause authority.
    def decision(oid, family, allowed, alternatives, channel="later"):
        row = next(o for o in contract["obligations"] if o["id"] == oid)
        result["decisions"].append(dict(id=oid + ":" + family, family=family, operation=oid, origins=[oid], trigger={"typed_mutation": True}, facts=["typed_mutation"], alternatives=alternatives, channel=channel, observation_scope="MEANINGFUL", consequence="Material mutation choice changes " + channel, rule=PROFILE + "/" + family, evidence="BOUNDED_STRUCTURAL", witnesses=[], reachability="DECLARED_POSSIBLE_UNLESS_SUPPORTED_INVARIANT", authority=dict(allowed=[allowed], authority="DETERMINED", source_quote=row["source_quote"]), dependency=[]))
    for o in contract["obligations"]:
        if not typed(o["relation"]):
            continue
        p = o["relation"]["parameters"]
        if p["facet"] == "collections":
            for c in p["value"]:
                decision(o["id"], c["name"] + "/duplicates", c["duplicates"], ["allow", "unique"])
                decision(o["id"], c["name"] + "/ordering", "insertion", ["insertion", "sorted"], "order")
                decision(o["id"], c["name"] + "/equality", "exact", ["exact", "casefold"])
                sequence = scalar.json.dumps(c["creation"].get("pipeline", []), sort_keys=True)
                decision(o["id"], c["name"] + "/creation_pipeline", sequence, [sequence, "unauthorized_reordering"], "error")
                source = c["creation"].get("source", "input_default")
                decision(o["id"], c["name"] + "/value_source", source, ["literal", "input_default", "input", "omission"])
        if p["facet"] == INPUT_FACET:
            for parameter in p["value"]:
                prefix = parameter["operation"] + "/" + parameter["parameter"]
                decision(o["id"], prefix + "/required_input", parameter["presence"], ["required", "optional"], "error")
                missing = scalar.json.dumps(parameter["missing"], sort_keys=True)
                decision(o["id"], prefix + "/missing_input", missing, [missing, "incidental_parser_default"], "error")
                binding = scalar.json.dumps(parameter["binding"], sort_keys=True)
                decision(o["id"], prefix + "/external_binding", binding, [binding, "wrong_parameter"], "error")
        if p["facet"] == PREDICATE_FACET:
            for i, guard in enumerate(p["value"]["guards"]):
                behavior = scalar.json.dumps({k: guard[k] for k in ("command", "error", "rejection")}, sort_keys=True)
                decision(o["id"], "guard/" + str(i) + "/rejection", behavior, [behavior, "unauthorized_error_or_partial_write"], "error")
        if p["facet"] == REFERENCE_FACET:
            # Independently inspectable authority for target, existence, deletion,
            # bindings, finite selection domain and transitive path policy.
            for facet, v in p["value"].items():
                meaning = scalar.json.dumps(v, sort_keys=True)
                decision(o["id"], "reference/" + facet, meaning, [meaning, "omitted_or_altered_reference_authority"], "error" if facet in ("references", "guards") else "later")
        if p["facet"] == ATOMIC_FACET:
            for facet, v in p["value"].items():
                meaning = scalar.json.dumps(v, sort_keys=True)
                decision(o["id"], "atomic_state/" + facet, meaning, [meaning, "omitted_or_altered_state_authority"])
            for op in p["value"]["operations"]:
                for facet in ("on", "sampling", "ordering", "resources", "creations"):
                    meaning = scalar.json.dumps(op[facet], sort_keys=True)
                    decision(o["id"], op["command"] + "/" + facet, meaning, [meaning, "omitted_or_altered_state_authority"])
        entries = p["value"] if p["facet"] in ("mutations", "creation_pipelines") else []
        for m in entries:
            if p["facet"] == "mutations":
                decision(o["id"], m["command"] + "/atomicity", "unchanged", ["unchanged", "partial"])
                writes = m["changes"]
            else:
                writes = [m]
            for w in writes:
                prefix = (m.get("command", "creation") + "/" + w["field"])
                if "source" in w:
                    literal = scalar.json.dumps(w["source"], sort_keys=True)
                    decision(o["id"], prefix + "/literal_assignment", literal, [literal, "altered_literal_or_default_trigger"])
                if "omitted" in w:
                    decision(o["id"], prefix + "/presence", w["omitted"], ["unchanged", "reject"])
                    decision(o["id"], prefix + "/operation", w["operation"], ["replace", "append", "add_unique"])
                sequence = scalar.json.dumps(w["pipeline"], sort_keys=True)
                decision(o["id"], prefix + "/pipeline", sequence, [sequence, "unauthorized_reordering"], "error")
    if projection["facts"]["queries"]:
        from lykoi_query import contracts as queries
        _, qc, _ = split(contract)
        qp = queries.structural(qc, scalar.frc.digest(qc))
        qb = queries.bdi(qc, qp)["result"]
        for k in ("decisions", "exclusions", "unknown"):
            result[k] += qb[k]
    from air_compiler.predicates import decisions
    def trees(v, path):
        if type(v) is dict:
            if v.get("result_type") == "boolean":
                yield path, v
            else:
                for k, child in v.items():
                    yield from trees(child, path + "/" + k)
        elif type(v) is list:
            for i, child in enumerate(v):
                yield from trees(child, path + "/" + str(i))
    for o in contract["obligations"]:
        for path, tree in trees(o["relation"]["parameters"], "condition"):
            for family, meaning in decisions(tree, path):
                decision(o["id"], family, meaning, [meaning, "missing_or_altered_predicate_authority"], "return")
    result["extension"] = PROFILE
    return dict(version=scalar.discovery.VERSION_BDI, outcome="UNSUPPORTED" if result["unknown"] else "SUPPORTED", result=result)


adequate = scalar.adequate


def faithful_v1(contract):
    p = structural(contract, scalar.frc.digest(contract)); coverage(contract, p)
    normal = dict(schema_version=scalar.V1, profile=PROFILE, contract=copy.deepcopy(contract), facts=p["facts"])
    return dict(version=scalar.V1, profile=PROFILE, outcome="FAITHFUL_COMPLETE", document=normal, normalized=copy.deepcopy(normal), coverage=[dict(frc_id=o["id"], v1_id=o["id"]) for o in contract["obligations"]])


def recover(normal):
    keys(normal, ("schema_version", "profile", "contract", "facts"))
    require(normal["schema_version"] == scalar.V1 and normal["profile"] == PROFILE, "Versioned mutable V1")
    require(faithful_v1(normal["contract"])["normalized"] == normal, "Faithful mutable V1 recovery")
    return copy.deepcopy(normal["contract"])


def formalizer_guidance():
    return ("Typed mutable values compose complete existing-scalar-1 facets with crud relations "
            "{profile:typed-mutable-values-1,facet,value}: collections, mutations, creation_pipelines. "
            "Select capability_profile typed-mutable-values-1. Declare nonnullable scalar element type/domain, "
            "insertion ordering, independent allow/unique duplicate policy and exact equality. Declare creation "
            "default separately from migration authority. Mutations declare command, identity lookup, missing_error, "
            "changes, guards and effect {atomicity:single_record,persistence:atomic,rejection:unchanged}. Each change "
            "declares field,input,operation replace/append/add_unique,omitted unchanged/reject,missing_error, "
            "pipeline,invalid_error. Ordered pipeline steps are transform operation verbatim/trim/stable_deduplicate "
            "or validate rule nonempty/nonblank/typed with error. Never infer transforms or duplicate behavior. "
             "Missing material authority requires clarification; typed facts are candidates, not authority."
               " Select input_value_profile typed-input-values-1 for the bounded input closure. Add input_contracts: "
               "operation,parameter,type,presence required/optional,binding {source:cli_flag,flag,encoding:text/json/repeated}, "
               "missing null for optional or {kind:application_error,error} / {kind:cli_rejection} for required. "
               "Every creation/mutation parameter needs exactly one binding with exact type and presence. "
               "Collections may instead have creation {source:literal,value:[typed elements]}, without a creation input or default. "
               "Closure validate steps require stage RAW/TRANSFORMED/PERSISTED and when null or {stage,predicate:present/absent/empty/nonempty/whitespace}. "
               "RAW is preserved before transformations, not trimmed. PERSISTED observes the final candidate before atomic commit. "
                "For predicate_profile typed-predicates-1 also declare predicate_semantics {booleans,guards,invariants}. "
                "Conditions use closed boolean result trees compare(eq/lt/le/gt/ge), and/or(children), not(child), is_null, present, member(in). "
                "Operands are typed field/parameter/literal or staged local value; comparison nodes declare case/normalization and nulls:false. "
                "No != alias: use NOT eq; collection CONTAINS lowers scalar IN collection. Query comparison is {scope:predicate_nodes}, inclusion []. "
                "Booleans have literal creation and authorized migration; mutable replace inputs use JSON boolean encoding. "
                "Guard rejection is explicit unchanged with declared error, evaluated before mutation. "
                "Only nullable timestamps; ordered comparisons only timestamps. No arithmetic. "
                 "Never guess recent boundaries, inclusivity, null participation or ambiguous AND/OR grouping: request clarification. "
                 "For predicate_value_interface_profile predicate-value-interfaces-1, literal mutation changes declare "
                 "field,source {kind:literal,type,value},operation:replace,pipeline:[],invalid_error; no parameter or default trigger. "
                 "Query amendment declares complete base query,composition and/or/replace,predicate; resulting selection must match "
                 "and unrelated facets remain exact. Existing listing base must normalize its actual declared behavior. "
                 "Query preconditions are separate {predicate,error,stage:before_selection,rejection:unchanged}; "
                 "parameter_errors map names to {missing,invalid}. Resource bindings declare name,type,capability," 
                  "sampling:once_per_query, with an existing UTC clock capability. Never infer composition, errors or clock authority. "
                  "For reference_profile persistent-references-1 declare reference_semantics with primary, entities, references, operations, guards, commit. "
                  "Identity operands retain type identifier, domain [], entity nominal target. Related fields use explicit alias.field namespaces. "
                  "Reference fields declare target, existence required/unchecked and deletion restrict/permit with authorized errors and explicit migration or null. "
                  "Related guards compose extent(select(entity,binding,predicate)) eq/ge N. EXISTS is ge 1; NONE is eq 0; ALL is eq 0 over related AND NOT P. "
                  "Declare the exact domain, missing behavior and exclusive one-store one-record commit; never infer cascade. "
                   "Cycle guards may explicitly use reachable with same-entity typed source/target, declared field and nonempty paths; this is a new core candidate, not hidden traversal. "
                   "Select atomic_state_profile atomic-durable-state-1 for atomic_state_semantics operations,queries,append_only,commit. "
                   "Bind existing primary writes to 1..8 ordinary related creations with complete typed payload sources literal/parameter/before/after/resource. "
                   "Declare success-only creation, once_per_operation resource sampling, declared_creation_occurrence order and one_store bounded_records unchanged rejection. "
                   "Queries are existing complete CollectionQuery; empty ordering explicitly preserves occurrence order in this profile. "
                   "No implicit history fields, ambient clock, numeric successor, JSON blob or external-effect authority. Missing record/sequence authority requires clarification.")
