import json


def load_json(f):
    # passthru dict
    if isinstance(f, dict):
        return f
    try:
        # load from file like object
        string = f.read()
    except AttributeError:
        # load from filename
        with open(f) as fp:
            string = fp.read()
    return json.loads(string)
