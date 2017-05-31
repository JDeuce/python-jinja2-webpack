import pytest

from jinja2_webpack import AssetNotFoundException, Environment


@pytest.fixture(scope="module")
def env():
    e = Environment(
        publicRoot='/pack',
        manifest={
            'a': 'b',
            'foo.js': 'foo.123.js',
            'bar.test': 'bar.123.test'
        })
    return e


def test_identify_basic(env):
    assert env.identify_assetspec('a')


def test_identify_no_extension(env):
    assert env.identify_assetspec('foo')
    assert env.identify_assetspec('foo').filename == 'foo.123.js'


def test_identify_no_directory(env):
    assert env.identify_assetspec('../foo')
    assert env.identify_assetspec('../foo').filename == 'foo.123.js'


def test_identify_invalid_asset():
    env = Environment(errorOnInvalidReference=False, manifest=None)
    assert env.identify_assetspec('baz') is None


def test_identify_error_on_invalid_reference():
    env = Environment(errorOnInvalidReference=True, manifest=None)
    with pytest.raises(AssetNotFoundException):
        env.identify_assetspec('test')


def test_renderer(env):
    a = env.identify_assetspec('a')
    assert env.render_asset(a) == '/pack/b'


@pytest.fixture(scope="module")
def rendering_env():
    e = Environment(
        publicRoot='/pack',
        useDefaultRenderByExt=True,
        manifest={
            'a': 'b',
            'foo.js': 'foo.123.js',
            'bar.test': 'bar.123.test'
        })
    return e


def test_js_renderer(rendering_env):
    foo = rendering_env.identify_assetspec('foo.js')
    assert foo
    assert "script" in rendering_env.render_asset(foo)


def test_add_renderer(rendering_env):
    def test_renderer(asset):
        return 'TEST'

    rendering_env.register_renderer('.test', test_renderer)

    bar = rendering_env.identify_assetspec('bar')
    assert bar
    assert rendering_env.render_asset(bar) == 'TEST'
