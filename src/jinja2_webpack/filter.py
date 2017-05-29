from os import path


class WebpackFilter(object):
    def __init__(self, manifest):
        self.manifest = manifest

    def update_manifest(self, manifest):
        self.manifest = manifest

    def __call__(self, value):
        basename = path.basename(value)
        return self.manifest.get(basename, '')
