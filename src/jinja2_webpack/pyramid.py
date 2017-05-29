from . import DEFAULT_SETTINGS
from . import load_webpack_manifest
from .filter import WebpackFilter


def webpack_settings_from_settings(registry_settings):
    prefixes = ['webpack.']
    settings = DEFAULT_SETTINGS.copy()
    for k, v in registry_settings.items():
        for prefix in prefixes:
            if k.startswith(prefix):
                setting_name = k[len(prefix):]
                settings[setting_name] = v

    return settings


def includeme(config):
    registry_settings = config.registry.settings
    settings = webpack_settings_from_settings(registry_settings)
    registry_settings['webpack'] = settings

    # load the webpack manifest
    manifest = load_webpack_manifest(settings)
    if not manifest:
        raise Exception('Failed to load manifest')

    # expose a webpack filter
    wpf = WebpackFilter(manifest)
    jinja2_env = config.get_jinja2_environment()
    if jinja2_env is None:
        raise Exception('Unable to find jinja2 environment. '
                        'Try config.commit()')
    jinja2_env.filters['webpack'] = wpf
