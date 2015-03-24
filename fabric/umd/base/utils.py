
from umd import exception


def to_list(obj):
    if not isinstance(obj, (str, list)):
        raise exception.ConfigException("obj variable type '%s' not supported."
                                        % type(obj))
    elif isinstance(obj, str):
        return [obj]
    return obj
