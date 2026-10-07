"""Generated normal query dispatcher and read-only collection-view adapter."""


def profile_main(queries, storage):
    models = {q["id"]: q for q in queries}
    if storage["kind"] in ("model_state", "mutable_state") and len(sys.argv) > 1 and sys.argv[1] not in models:
        return legacy_main()
    parser = argparse.ArgumentParser(prog="lykoi")
    commands = parser.add_subparsers(dest="command", required=True)
    for q in queries:
        sub = commands.add_parser(q["id"])
        if storage["kind"] == "json_array":
            sub.add_argument("--store", required=True)
        for name in q["parameters"]:
            sub.add_argument("--" + name.replace("_", "-"), dest=name, required=name not in q.get("parameter_errors", {}) or q["parameter_errors"][name]["missing"] == {"kind": "cli_rejection"}, default=argparse.SUPPRESS)
    args = vars(parser.parse_args())
    model = models[args.pop("command")]
    try:
        query_path = Path(args.pop("store")) if storage["kind"] == "json_array" else None
        if model["predicate"].get("result_type") == "boolean":
            for n, typ in model["parameters"].items():
                if n in args and typ["type"] in ("collection", "boolean"):
                    try:
                        args[n] = json.loads(args[n])
                    except ValueError:
                        raise ApplicationError(model.get("parameter_errors", {}).get(n, {}).get("invalid", "invalid_input"))
        resources = prepare_query(model, args) if model["predicate"].get("result_type") == "boolean" else None
        # Declared runtime validation is independent of persisted record validity.
        for rule in model["validation"]:
            value = args[rule["parameter"]]
            if ((rule["rule"] == "nonempty" and value == "") or
                    (rule["rule"] == "nonblank" and not value.strip())):
                raise ApplicationError(rule["error"])
        if storage["kind"] == "json_array":
            path = query_path
            records = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
            result = execute_predicate_query(model, records, args, resources=resources) if resources is not None else execute_query(model, records, args)
        else:
            state = by_id("state", storage["state"])
            record_type, path = state_layout(state)
            records = read_state(state, record_type, path)
            # Validate the full legacy store before projecting the supported view.
            # Nonquery nullable fields survive unchanged; no nullable predicate.
            view = [{k: r[k] for k in model["source"]["fields"]} for r in records]
            selected = execute_predicate_query(model, view, args, resources=resources) if resources is not None else execute_query(model, view, args)
            key = model["source"]["unique_key"]
            originals = {r[key]: r for r in records}
            result = None if selected is None else [copy.deepcopy(originals[r[key]]) for r in selected]
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except ApplicationError as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    except (OSError, ValueError):
        print(json.dumps({"error": "invalid_state"}), file=sys.stderr)
        return 1
    except globals().get("Failure", ApplicationError) as exc:
        print(json.dumps({"error": exc.code}), file=sys.stderr)
        return 1
