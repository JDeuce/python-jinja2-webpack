from jinja2_webpack import Asset
from jinja2_webpack.renderer import image, script, stylesheet, url


def test_renderers():
    x = Asset(filename='x', url='x')

    assert 'x' == url(x)
    assert 'script' in script(x)
    assert 'link' in stylesheet(x)
    assert 'img' in image(x)
