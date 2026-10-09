"""Object-root publication annotation; original schema remains authoritative."""
import copy
import jsonschema

def publish(schema):
    result = copy.deepcopy(schema)
    if result.get('type') == 'object':
        return result
    if set(result) != {'oneOf'} or not result['oneOf']:
        raise ValueError('Unsupported root conversion')
    if not all(type(branch) is dict and branch.get('type') == 'object'
               for branch in result['oneOf']):
        raise ValueError('Every union branch must explicitly require an object')
    # Each original branch already requires an object. This adds no restriction
    # or accepted instance, and leaves all original branch constraints intact.
    result['type'] = 'object'
    return result

def validate(original, arguments):
    jsonschema.Draft202012Validator(original).validate(arguments)
