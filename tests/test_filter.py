from jinja2_webpack.filter import WebpackFilter


def test_filter_defined():
    assert WebpackFilter


def test_simple_lookup():
    manifest = {'a': 'b'}
    f = WebpackFilter(manifest)
    assert f
    assert f('a') == 'b'

def test_basename_lookup():
    manifest = {'a': 'b'}
    f = WebpackFilter(manifest)
    assert f('/path/to/a') == 'b'

