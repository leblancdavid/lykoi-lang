"""Explicit integration adapter; production decoder and semantics stay unchanged."""


def install_list_storage_profile(namespace, declaration):
    if declaration is None:
        return
    required = {'state', 'format', 'schema_version', 'migrations', 'invalid_state_error'}
    if (set(declaration) != required or declaration['format'] != 'json_list'
            or type(declaration['schema_version']) is not int
            or declaration['schema_version'] != 1
            or declaration['migrations'] != 'forbidden'
            or declaration['invalid_state_error'] != 'invalid_state'):
        raise ValueError('unsupported persistence profile')
    spec = namespace['SPEC']
    selected = [s for s in spec['state'] if s['id'] == declaration['state']]
    if (len(selected) != 1 or type(selected[0].get('schema_version')) is not int
            or selected[0]['schema_version'] != 1 or spec.get('migrations')):
        raise ValueError('profile requires an explicit nonmigrating version-1 state')
    selected_state = selected[0]
    original_decode = namespace['decode_state']
    failure = namespace['Failure']

    def decode_list_storage(payload, state):
        # Identity scopes the override to this actual lowered state, not a name match.
        if state is not selected_state:
            return original_decode(payload, state)
        try:
            records = original_decode(payload, state)
        except failure as exc:
            if exc.code == 'migration_required':
                raise failure('invalid_state') from exc
            raise
        if not isinstance(payload, list):
            raise failure('invalid_state')
        return records

    namespace['decode_state'] = decode_list_storage
