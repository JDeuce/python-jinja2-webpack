def script(asset):
    return '<script src="%s"></script>' % asset.url


def image(asset):
    return '<img src="%s">' % asset.url


def stylesheet(asset):
    return '<link rel="stylesheet" href="%s">' % asset.url


def url(asset):
    return asset.url
