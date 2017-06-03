from os import path

from . import renderer
from .utils import load_json

DEFAULT_SETTINGS = {
    'errorOnInvalidReference': True,
    'publicRoot': '/static/pack',
    'manifest': 'webpack-manifest.json',
    'defaultRenderer': renderer.url,
    'useDefaultRenderByExt': False,  # this setting is mostly experimental
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
    inline. For now the url is the interesting attribute  """
    def __init__(self, filename, url):
        self.filename = filename
        self.url = url


class AssetNotFoundException(Exception):
    """ Thrown when an asset cannot be found,
    can be disabled by settings errorOnInvalidReference = False """
    pass


class EnvironmentSettings(object):
    def __init__(self, **kwargs):
        self.__dict__.update(DEFAULT_SETTINGS)

        if not kwargs.get('useDefaultRenderByExt', self.useDefaultRenderByExt):
            self.renderByExt = {}

        self.__dict__.update(kwargs)


class Environment(object):
    """ The webpack environment class. Loads the manifest and allows
    it to be accessed.
    Settings:
        * manifest - default "webpack-manifest.json"
            Path to the WebpackManifest file
        * errorOnInvalidReference - default True
            True if exception should be thrown when you try to resolve an
            invalid asset reference
        * publicRoot - default /static/pack
            The public path to prepend to all asset URLs
    """
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
        """ Lookup an asset from the webpack manifest.
        The asset spec is processed such that you might reference an entry
        with or without the extension.

        Will raise an AssetNotFoundException if the errorOnInvalidReference
        setting is enabled and the asset cannot be found.

        Note that all files must be have globally unique names,
        due to a limitation in the way that WebpackManifestPlugin writes
        the data.
        """
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
        """ Register a new renderer function to the environment """
        self.settings.renderByExt[extension] = renderer

    def _select_renderer(self, asset):
        name, ext = path.splitext(asset.filename)
        return self.settings.renderByExt.get(
             ext, self.settings.defaultRenderer)

    def render_asset(self, asset):
        """ Render an asset to a URL or something more interesting,
        by looking up the extension in the registered renderers """
        renderer = self._select_renderer(asset)
        return renderer(asset)


__version__ = '0.1.4'
