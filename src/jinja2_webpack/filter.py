class WebpackFilter(object):
    """ Jinja2 filter which can be used to reference webpack assets from
    jinja2 templates """
    def __init__(self, environment):
        self.environment = environment

    def __call__(self, assetspec):
        asset = self.environment.identify_assetspec(assetspec)
        if asset:
            return self.environment.render_asset(asset)
