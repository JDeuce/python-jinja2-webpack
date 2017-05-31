class WebpackFilter(object):
    def __init__(self, environment):
        self.environment = environment

    def __call__(self, assetspec):
        asset = self.environment.identify_assetspec(assetspec)
        if asset:
            return self.environment.render_asset(asset)
