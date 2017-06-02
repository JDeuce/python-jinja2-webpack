from os import path

from . import renderer
from .utils.load_json import load_json

DEFAULT_SETTINGS = {
    'errorOnInvalidReference': True,
    'publicRoot': '/static/pack',
    'manifest': 'webpack-manifest.json',
    'defaultRenderer': renderer.url,
    'useDefaultRenderByExt': False,
    'renderByExt': {
        '.js': renderer.script,
        '.png': renderer.image,
        '.jpeg': renderer.image,
        '.jpg': renderer.image,
        '.gif': renderer.image,
        '.css': renderer.stylesheet,
    }
}


class Asset(object):
    """ Asset class.
    Might someday expose file access here too so can render assets
    inline """
    def __init__(self, filename, url):
        self.filename = filename
        self.url = url


class AssetNotFoundException(Exception):
    pass


class EnvironmentSettings(object):
    def __init__(self, **kwargs):
        self.__dict__.update(DEFAULT_SETTINGS)

        if not kwargs.get('useDefaultRenderByExt', self.useDefaultRenderByExt):
            self.renderByExt = {}

        self.__dict__.update(kwargs)


class Environment(object):
    def __init__(self, **kwargs):
        self.settings = EnvironmentSettings(**kwargs)
        if self.settings.manifest:
            self.load_manifest(self.settings.manifest)
        else:
            self._manifest = {}

    def _resolve_asset(self, asset):
        return Asset(
            filename=asset,
            url='%s/%s' % (self.settings.publicRoot, asset))

    def _resolve_manifest(self, manifest):
        result = {}
        # Resolve URLs in original manifest items
        for name, asset in manifest.items():
            result[name] = self._resolve_asset(asset)
        # Strip out the extension as well, so if the webpack output
        # file is "commons.js" we can use {{ "commons" | webpack }}
        for name, asset in manifest.items():
            basename, ext = path.splitext(name)
            if basename not in result:
                result[basename] = result[name]

        return result

    def load_manifest(self, filename):
        manifest = load_json(filename)
        self._manifest = self._resolve_manifest(manifest)

    def identify_assetspec(self, spec):
        nodir = path.basename(spec)
        noextension = path.splitext(nodir)[0]
        result = self._manifest.get(spec) \
            or self._manifest.get(nodir) \
            or self._manifest.get(noextension)
        if result:
            return result
        if self.settings.errorOnInvalidReference:
            raise AssetNotFoundException(spec)

    def register_renderer(self, extension, renderer):
        self.settings.renderByExt[extension] = renderer

    def _select_renderer(self, asset):
        name, ext = path.splitext(asset.filename)
        return self.settings.renderByExt.get(
             ext, self.settings.defaultRenderer)

    def render_asset(self, asset):
        renderer = self._select_renderer(asset)
        return renderer(asset)


__version__ = '0.1.3'
