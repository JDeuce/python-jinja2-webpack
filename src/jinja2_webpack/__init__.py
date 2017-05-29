import json

DEFAULT_SETTINGS = {
    'publicRoot': '/static/pack',
    'manifest': 'webpack-manifest.json',
}


def get_webpack_resolver(settings):
    root = settings['publicRoot']
    return lambda asset: '%s/%s' % (root, asset)


def resolve_manifest(settings, manifest):
    resolver = get_webpack_resolver(settings)
    result = {}
    for name, asset in manifest.items():
        result[name] = resolver(asset)
    return result


def load_webpack_manifest(settings):
    with open(settings['manifest']) as f:
        manifest = json.loads(f.read())
    return resolve_manifest(settings, manifest)


__version__ = "0.1.2"
